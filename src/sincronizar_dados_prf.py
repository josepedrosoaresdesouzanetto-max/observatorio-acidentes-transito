"""Sincronização controlada dos CSVs públicos da PRF.

O modo padrão apenas verifica. Nenhuma base local é substituída sem a combinação
explícita de ``--aplicar-atualizacao`` e ``--confirmar``.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

import pandas as pd

from src.comparar_arquivos_prf import (
    COLUNAS_SENSIVEIS,
    DiagnosticoCSV,
    ErroValidacaoCSV,
    ResultadoComparacao,
    carregar_csv_validado,
    comparar_arquivos,
    sha256_arquivo,
)
from src.config import (
    BACKUPS_PRF_DIR,
    MANIFESTO_REMOTO_PRF_PATH,
    OCORRENCIA_BRUTOS_DIR,
    PESSOA_BRUTOS_DIR,
    RELATORIO_SINCRONIZACAO_PRF_PATH,
    TABELAS_DIR,
    TEMPORARIOS_PRF_DIR,
)

MAX_WORKERS_METADADOS = 8
TIMEOUT_METADADOS_SEGUNDOS = 8


@dataclass(frozen=True)
class MetadadosRemotos:
    url: str
    nome_arquivo: str
    ano: int
    tipo: str
    content_length: int | None
    last_modified: str | None
    etag: str | None
    sha256: str | None
    verificado_em: str
    status: str = "comparação pendente"
    erro: str | None = None


@dataclass(frozen=True)
class DownloadValidado:
    path: Path
    metadados: MetadadosRemotos
    diagnostico: DiagnosticoCSV


@dataclass(frozen=True)
class ResultadoAplicacao:
    arquivo_local: Path
    backup: Path
    hash_anterior: str
    hash_novo: str
    rollback_executado: bool


class ErroSincronizacao(RuntimeError):
    """Falha operacional esperada, apresentada sem traceback ao usuário."""


def agora_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def normalizar_tipo(tipo: str) -> str:
    aliases = {"ocorrencia": "ocorrencia", "ocorrencias": "ocorrencia", "pessoa": "pessoa", "pessoas": "pessoa"}
    try:
        return aliases[tipo.lower().strip()]
    except KeyError as exc:
        raise ErroSincronizacao("Tipo inválido. Use 'ocorrencias' ou 'pessoas'.") from exc


def nome_temporario(ano: int, tipo: str) -> str:
    return f"prf_{int(ano)}_{normalizar_tipo(tipo)}.csv"


def url_download_direto(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.lower() in {"drive.google.com", "www.drive.google.com"}:
        partes = [parte for parte in parsed.path.split("/") if parte]
        if len(partes) >= 3 and partes[0] == "file" and partes[1] == "d":
            identificador = quote(partes[2], safe="")
            return f"https://drive.usercontent.google.com/download?id={identificador}&export=download&confirm=t"
    return url


def destino_seguro(diretorio: Path, nome: str) -> Path:
    nome_limpo = Path(unquote(nome)).name
    if not nome_limpo or nome_limpo in {".", ".."}:
        raise ErroSincronizacao("Nome de arquivo remoto inválido.")
    base = diretorio.resolve()
    destino = (base / nome_limpo).resolve()
    if base != destino.parent:
        raise ErroSincronizacao("Caminho remoto recusado por proteção contra path traversal.")
    return destino


def _valor_header(headers, nome: str) -> str | None:
    valor = headers.get(nome) if headers is not None else None
    return str(valor).strip() if valor else None


def _content_length(headers) -> int | None:
    valor = _valor_header(headers, "Content-Length")
    try:
        return int(valor) if valor is not None else None
    except ValueError:
        return None


def _mensagem_http(exc: HTTPError) -> str:
    mensagens = {
        403: "acesso negado pela fonte (HTTP 403)",
        404: "arquivo não encontrado (HTTP 404)",
        429: "limite de requisições atingido (HTTP 429)",
        500: "falha interna da fonte (HTTP 500)",
    }
    return mensagens.get(exc.code, f"falha HTTP {exc.code}")


def obter_metadados_remotos(arquivo, opener: Callable = urlopen, timeout: int = 30) -> MetadadosRemotos:
    request = Request(url_download_direto(arquivo.url), method="HEAD", headers={"User-Agent": "observatorio-acidentes-transito/2.0"})
    try:
        with opener(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if status >= 400:
                raise ErroSincronizacao(f"Falha ao consultar cabeçalhos: HTTP {status}.")
            headers = response.headers
    except HTTPError as exc:
        raise ErroSincronizacao(f"Falha ao consultar {arquivo.url}: {_mensagem_http(exc)}.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ErroSincronizacao(f"Falha de rede ao consultar {arquivo.url}: {exc}.") from exc

    nome = Path(unquote(urlparse(arquivo.url).path)).name or nome_temporario(arquivo.ano, arquivo.tipo)
    return MetadadosRemotos(
        url=arquivo.url,
        nome_arquivo=nome,
        ano=int(arquivo.ano),
        tipo=normalizar_tipo(arquivo.tipo),
        content_length=_content_length(headers),
        last_modified=_valor_header(headers, "Last-Modified"),
        etag=_valor_header(headers, "ETag"),
        sha256=None,
        verificado_em=agora_iso(),
    )


def carregar_manifesto(path: Path = MANIFESTO_REMOTO_PRF_PATH) -> dict:
    if not path.exists():
        return {"gerado_em": None, "arquivos": []}
    try:
        dados = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ErroSincronizacao(f"Manifesto remoto inválido: {exc}.") from exc
    return dados if isinstance(dados, dict) else {"gerado_em": None, "arquivos": []}


def salvar_manifesto(registros: Iterable[MetadadosRemotos | dict], path: Path = MANIFESTO_REMOTO_PRF_PATH) -> Path:
    serializados = [asdict(item) if isinstance(item, MetadadosRemotos) else dict(item) for item in registros]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporario = path.with_suffix(path.suffix + ".tmp")
    temporario.write_text(
        json.dumps({"gerado_em": agora_iso(), "arquivos": serializados}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporario.replace(path)
    return path


def detectar_status_remoto(atual: dict, anterior: dict | None) -> str:
    if anterior is None:
        return "novo arquivo publicado"
    prioridades = ("sha256", "etag", "last_modified", "content_length")
    for campo in prioridades:
        valor_atual = atual.get(campo)
        valor_anterior = anterior.get(campo)
        if valor_atual is not None and valor_anterior is not None:
            return "sem mudança detectada" if valor_atual == valor_anterior else "possível atualização detectada"
    return "comparação pendente"


def verificar_publicacoes(
    arquivos: Iterable,
    manifesto_path: Path = MANIFESTO_REMOTO_PRF_PATH,
    consultar: Callable | None = None,
    max_workers: int = 8,
) -> list[MetadadosRemotos]:
    consultar = consultar or (
        lambda arquivo: obter_metadados_remotos(arquivo, timeout=TIMEOUT_METADADOS_SEGUNDOS)
    )
    arquivos = list(arquivos)
    anterior = carregar_manifesto(manifesto_path)
    por_url = {item.get("url"): item for item in anterior.get("arquivos", []) if isinstance(item, dict)}
    consultados: dict[int, MetadadosRemotos] = {}

    def consultar_com_falha_controlada(indice: int, arquivo) -> tuple[int, MetadadosRemotos]:
        try:
            return indice, consultar(arquivo)
        except (ErroSincronizacao, HTTPError, URLError, TimeoutError, OSError) as exc:
            nome = Path(unquote(urlparse(arquivo.url).path)).name or nome_temporario(arquivo.ano, arquivo.tipo)
            return indice, MetadadosRemotos(
                url=arquivo.url,
                nome_arquivo=nome,
                ano=int(arquivo.ano),
                tipo=normalizar_tipo(arquivo.tipo),
                content_length=None,
                last_modified=None,
                etag=None,
                sha256=None,
                verificado_em=agora_iso(),
                status="comparação pendente",
                erro=str(exc),
            )

    trabalhadores = max(1, min(max_workers, MAX_WORKERS_METADADOS, len(arquivos) or 1))
    with ThreadPoolExecutor(max_workers=trabalhadores) as executor:
        futuros = {executor.submit(consultar_com_falha_controlada, indice, arquivo): indice for indice, arquivo in enumerate(arquivos)}
        for futuro in as_completed(futuros):
            indice, metadados = futuro.result()
            consultados[indice] = metadados

    resultados: list[MetadadosRemotos] = []
    for indice, arquivo in enumerate(arquivos):
        metadados = consultados[indice]
        atual = asdict(metadados)
        registro_anterior = por_url.get(metadados.url)
        status = "comparação pendente" if metadados.erro else detectar_status_remoto(atual, registro_anterior)
        if registro_anterior is None and localizar_arquivo_local(metadados.ano, metadados.tipo).exists():
            status = "comparação pendente"
        if atual.get("sha256") is None and registro_anterior:
            atual["sha256"] = registro_anterior.get("sha256")
        resultados.append(MetadadosRemotos(**{**atual, "status": status}))
    salvar_manifesto(resultados, manifesto_path)
    return resultados


def atualizar_registro_manifesto(
    metadados: MetadadosRemotos,
    path: Path = MANIFESTO_REMOTO_PRF_PATH,
) -> Path:
    manifesto = carregar_manifesto(path)
    registros = [item for item in manifesto.get("arquivos", []) if isinstance(item, dict)]
    novo = asdict(metadados)
    filtrados = [
        item
        for item in registros
        if item.get("url") != metadados.url
        and not (item.get("ano") == metadados.ano and item.get("tipo") == metadados.tipo)
    ]
    filtrados.append(novo)
    return salvar_manifesto(filtrados, path)


def atualizar_status_manifesto(
    ano: int,
    tipo: str,
    status: str,
    sha256: str | None = None,
    path: Path = MANIFESTO_REMOTO_PRF_PATH,
) -> Path:
    manifesto = carregar_manifesto(path)
    tipo_normalizado = normalizar_tipo(tipo)
    alterou = False
    registros = []
    for item in manifesto.get("arquivos", []):
        registro = dict(item)
        if registro.get("ano") == int(ano) and registro.get("tipo") == tipo_normalizado:
            registro["status"] = status
            registro["verificado_em"] = agora_iso()
            if sha256:
                registro["sha256"] = sha256
            alterou = True
        registros.append(registro)
    if not alterou:
        registros.append(
            asdict(
                MetadadosRemotos(
                    url="não registrada",
                    nome_arquivo=nome_temporario(ano, tipo_normalizado),
                    ano=int(ano),
                    tipo=tipo_normalizado,
                    content_length=None,
                    last_modified=None,
                    etag=None,
                    sha256=sha256,
                    verificado_em=agora_iso(),
                    status=status,
                    erro=None,
                )
            )
        )
    return salvar_manifesto(registros, path)


def _validar_content_type(headers) -> None:
    content_type = (_valor_header(headers, "Content-Type") or "").lower()
    if "html" in content_type:
        raise ErroSincronizacao("A fonte retornou HTML no lugar de CSV.")


def baixar_arquivo_temporario(
    arquivo,
    diretorio: Path = TEMPORARIOS_PRF_DIR,
    opener: Callable = urlopen,
    timeout: int = 60,
    chunk_size: int = 1024 * 1024,
) -> DownloadValidado:
    diretorio.mkdir(parents=True, exist_ok=True)
    destino = destino_seguro(diretorio, nome_temporario(arquivo.ano, arquivo.tipo))
    parcial = destino_seguro(diretorio, destino.name + ".part")
    request = Request(url_download_direto(arquivo.url), headers={"User-Agent": "observatorio-acidentes-transito/2.0"})
    recebidos = 0
    digest = hashlib.sha256()
    etag: str | None = None
    last_modified: str | None = None
    try:
        with opener(request, timeout=timeout) as response:
            status_http = getattr(response, "status", 200)
            if status_http >= 400:
                raise ErroSincronizacao(f"Download recusado: HTTP {status_http}.")
            _validar_content_type(response.headers)
            esperado = _content_length(response.headers)
            etag = _valor_header(response.headers, "ETag")
            last_modified = _valor_header(response.headers, "Last-Modified")
            with parcial.open("wb") as saida:
                while True:
                    bloco = response.read(chunk_size)
                    if not bloco:
                        break
                    saida.write(bloco)
                    digest.update(bloco)
                    recebidos += len(bloco)
        if recebidos == 0:
            raise ErroSincronizacao("Download concluído sem conteúdo; arquivo vazio.")
        if esperado is not None and recebidos != esperado:
            raise ErroSincronizacao(f"Download incompleto: esperado {esperado} bytes, recebidos {recebidos}.")
        _, diagnostico = carregar_csv_validado(parcial)
        parcial.replace(destino)
    except HTTPError as exc:
        raise ErroSincronizacao(f"Falha no download: {_mensagem_http(exc)}.") from exc
    except (URLError, TimeoutError, PermissionError, OSError, ErroValidacaoCSV) as exc:
        if isinstance(exc, ErroSincronizacao):
            raise
        raise ErroSincronizacao(f"Falha ao baixar ou validar arquivo: {exc}.") from exc
    finally:
        if parcial.exists():
            parcial.unlink()

    _, diagnostico_final = carregar_csv_validado(destino)
    metadados = MetadadosRemotos(
        url=arquivo.url,
        nome_arquivo=Path(unquote(urlparse(arquivo.url).path)).name or destino.name,
        ano=int(arquivo.ano),
        tipo=normalizar_tipo(arquivo.tipo),
        content_length=recebidos,
        last_modified=last_modified,
        etag=etag,
        sha256=digest.hexdigest(),
        verificado_em=agora_iso(),
        status="comparação pendente",
    )
    return DownloadValidado(destino, metadados, diagnostico_final)


def localizar_arquivo_local(ano: int, tipo: str) -> Path:
    tipo_normalizado = normalizar_tipo(tipo)
    pasta = OCORRENCIA_BRUTOS_DIR if tipo_normalizado == "ocorrencia" else PESSOA_BRUTOS_DIR
    return pasta / f"acidentes_{int(ano)}_{tipo_normalizado}.csv"


def localizar_temporario(ano: int, tipo: str, diretorio: Path = TEMPORARIOS_PRF_DIR) -> Path:
    return destino_seguro(diretorio, nome_temporario(ano, tipo))


def _sem_colunas_sensiveis(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe[[coluna for coluna in dataframe.columns if coluna not in COLUNAS_SENSIVEIS]].copy()


def gerar_relatorios_comparacao(
    resultado: ResultadoComparacao,
    local: DiagnosticoCSV,
    remoto: DiagnosticoCSV,
    metadados: MetadadosRemotos,
    relatorio_path: Path = RELATORIO_SINCRONIZACAO_PRF_PATH,
    tabelas_dir: Path = TABELAS_DIR,
) -> Path:
    chave = ", ".join(resultado.chave_utilizada or ()) or "não identificada"
    recomendacao = (
        "Revisar diferenças e aplicar somente com confirmação explícita."
        if resultado.comparacao_segura
        else "Não aplicar: não foi possível identificar registros de forma segura."
    )
    linhas = [
        "# Relatório de sincronização controlada da PRF",
        "",
        f"Gerado em: {agora_iso()}",
        f"Arquivo analisado: {local.path.name}",
        f"URL: {metadados.url}",
        f"Ano: {metadados.ano}",
        f"Tipo: {metadados.tipo}",
        f"Hash local: {local.sha256}",
        f"Hash remoto: {remoto.sha256}",
        f"Tamanho local: {local.tamanho_bytes}",
        f"Tamanho remoto: {remoto.tamanho_bytes}",
        f"Linhas locais: {local.linhas}",
        f"Linhas remotas: {remoto.linhas}",
        f"Registros novos: {len(resultado.novos)}",
        f"Registros alterados: {resultado.alterados['chave'].nunique() if not resultado.alterados.empty else 0}",
        f"Registros removidos: {len(resultado.removidos)}",
        f"Registros inalterados: {resultado.inalterados}",
        f"Duplicados locais: {resultado.duplicados_local}",
        f"Duplicados remotos: {resultado.duplicados_remoto}",
        f"Registros sem chave válida: local={resultado.sem_chave_local}; remoto={resultado.sem_chave_remoto}",
        f"Chave utilizada: {chave} ({resultado.estrategia_chave})",
        f"Encoding remoto: {remoto.encoding}",
        f"Separador remoto: {remoto.separador}",
        f"Colunas remotas: {', '.join(remoto.colunas)}",
        f"Resultado da validação: {resultado.mensagem}",
        f"Recomendação: {recomendacao}",
        "",
        "Nenhuma base local foi substituída por esta comparação.",
    ]
    relatorio_path.parent.mkdir(parents=True, exist_ok=True)
    relatorio_path.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")

    if not resultado.novos.empty or not resultado.alterados.empty or not resultado.removidos.empty:
        tabelas_dir.mkdir(parents=True, exist_ok=True)
        resumo = pd.DataFrame(
            [{
                "arquivo": local.path.name,
                "ano": metadados.ano,
                "tipo": metadados.tipo,
                "novos": len(resultado.novos),
                "alterados": resultado.alterados["chave"].nunique() if not resultado.alterados.empty else 0,
                "removidos": len(resultado.removidos),
                "duplicados_remoto": resultado.duplicados_remoto,
                "duplicados_local": resultado.duplicados_local,
            }]
        )
        resumo.to_csv(tabelas_dir / "resumo_sincronizacao.csv", index=False, encoding="utf-8-sig")
        _sem_colunas_sensiveis(resultado.novos).to_csv(tabelas_dir / "novas_ocorrencias.csv", index=False, encoding="utf-8-sig")
        resultado.alterados.to_csv(tabelas_dir / "ocorrencias_alteradas.csv", index=False, encoding="utf-8-sig")
        _sem_colunas_sensiveis(resultado.removidos).to_csv(tabelas_dir / "ocorrencias_removidas.csv", index=False, encoding="utf-8-sig")
    return relatorio_path


def aplicar_atualizacao_controlada(
    arquivo_local: Path,
    arquivo_temporario: Path,
    confirmar: bool,
    backups_dir: Path = BACKUPS_PRF_DIR,
    validador: Callable[[Path], object] | None = None,
) -> ResultadoAplicacao:
    if not confirmar:
        raise ErroSincronizacao("Atualização recusada: use --confirmar para autorizar explicitamente.")
    if not arquivo_local.exists():
        raise ErroSincronizacao("Arquivo local inexistente; não há base conhecida para criar backup.")
    carregar_csv_validado(arquivo_temporario)
    hash_anterior = sha256_arquivo(arquivo_local)
    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = destino_seguro(backups_dir, f"{arquivo_local.stem}_{timestamp}{arquivo_local.suffix}.bak")
    try:
        shutil.copy2(arquivo_local, backup)
    except (OSError, PermissionError) as exc:
        raise ErroSincronizacao(f"Falha ao criar backup: {exc}.") from exc

    candidato = arquivo_local.with_suffix(arquivo_local.suffix + ".atualizacao.tmp")
    rollback = False
    try:
        shutil.copy2(arquivo_temporario, candidato)
        os.replace(candidato, arquivo_local)
        carregar_csv_validado(arquivo_local)
        if validador is not None:
            retorno = validador(arquivo_local)
            if retorno is False:
                raise ErroSincronizacao("Validação de qualidade reprovou o arquivo atualizado.")
        hash_novo = sha256_arquivo(arquivo_local)
    except Exception as exc:
        rollback = True
        try:
            shutil.copy2(backup, arquivo_local)
        except (OSError, PermissionError) as rollback_exc:
            raise ErroSincronizacao(f"Falha na atualização e no rollback: {rollback_exc}.") from exc
        raise ErroSincronizacao(f"Falha na atualização; rollback executado: {exc}.") from exc
    finally:
        if candidato.exists():
            candidato.unlink()
    return ResultadoAplicacao(arquivo_local, backup, hash_anterior, hash_novo, rollback)


def resumir_status_manifesto(path: Path = MANIFESTO_REMOTO_PRF_PATH) -> str:
    if not path.exists():
        return "comparação pendente"
    dados = carregar_manifesto(path)
    status = [item.get("status", "comparação pendente") for item in dados.get("arquivos", []) if isinstance(item, dict)]
    prioridade = (
        "possível atualização detectada",
        "novo arquivo publicado",
        "atualização aguardando confirmação",
        "comparação pendente",
        "comparação concluída",
        "sem mudança detectada",
    )
    return next((item for item in prioridade if item in status), "comparação pendente")


def gerar_relatorio_verificacao(
    resultados: Iterable[MetadadosRemotos],
    path: Path = RELATORIO_SINCRONIZACAO_PRF_PATH,
) -> Path:
    resultados = list(resultados)
    linhas = [
        "# Relatório de verificação remota da PRF",
        "",
        f"Gerado em: {agora_iso()}",
        "",
        "Este modo consulta somente metadados dos links publicados pela fonte oficial. Nenhum CSV completo foi baixado e nenhuma base local foi substituída.",
        "",
    ]
    for item in resultados:
        detalhe = f"[{item.status.upper()}] {item.ano} {item.tipo}: {item.url}"
        if item.erro:
            detalhe += f" — limitação da fonte externa: {item.erro}"
        linhas.append(detalhe)
    linhas.extend(
        [
            "",
            f"Resumo: {len(resultados)} link(s), {sum(item.erro is not None for item in resultados)} limitação(ões) externa(s).",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporario = path.with_suffix(path.suffix + ".tmp")
    temporario.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    temporario.replace(path)
    return path


def metadados_do_manifesto(
    ano: int,
    tipo: str,
    path: Path = MANIFESTO_REMOTO_PRF_PATH,
) -> MetadadosRemotos | None:
    tipo_normalizado = normalizar_tipo(tipo)
    for item in carregar_manifesto(path).get("arquivos", []):
        if item.get("ano") == int(ano) and item.get("tipo") == tipo_normalizado:
            campos = {campo: item.get(campo) for campo in MetadadosRemotos.__dataclass_fields__}
            return MetadadosRemotos(**campos)
    return None


def _selecionar_publicacao(ano: int, tipo: str):
    from src.verificar_dados_publicos import consultar_arquivos_publicos_prf

    tipo_normalizado = normalizar_tipo(tipo)
    arquivos = consultar_arquivos_publicos_prf()
    for arquivo in arquivos:
        if arquivo.ano == int(ano) and normalizar_tipo(arquivo.tipo) == tipo_normalizado:
            return arquivo
    raise ErroSincronizacao(f"Publicação não encontrada para ano={ano}, tipo={tipo_normalizado}.")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sincronização controlada dos dados públicos da PRF.")
    modos = parser.add_mutually_exclusive_group(required=True)
    modos.add_argument("--verificar", action="store_true", help="Consulta metadados remotos e registra possíveis mudanças.")
    modos.add_argument("--baixar-temporario", action="store_true", help="Baixa e valida um CSV na área temporária.")
    modos.add_argument("--comparar", action="store_true", help="Compara o CSV temporário com o bruto local.")
    modos.add_argument("--aplicar-atualizacao", action="store_true", help="Aplica uma atualização validada com backup e rollback.")
    parser.add_argument("--ano", type=int)
    parser.add_argument("--tipo", choices=["ocorrencia", "ocorrencias", "pessoa", "pessoas"])
    parser.add_argument("--confirmar", action="store_true", help="Confirma explicitamente a substituição controlada.")
    return parser


def _exigir_recorte(args: argparse.Namespace) -> None:
    if args.ano is None or args.tipo is None:
        raise ErroSincronizacao("Informe --ano e --tipo para este modo.")


def executar_cli(args: argparse.Namespace) -> int:
    if args.verificar:
        from src.verificar_dados_publicos import consultar_arquivos_publicos_prf

        resultados = verificar_publicacoes(consultar_arquivos_publicos_prf())
        for item in resultados:
            sufixo = f" | limitação da fonte externa: {item.erro}" if item.erro else ""
            print(f"[{item.status.upper()}] {item.ano} {item.tipo}: {item.url}{sufixo}")
        relatorio = gerar_relatorio_verificacao(resultados)
        print(f"Manifesto remoto: {MANIFESTO_REMOTO_PRF_PATH}")
        print(f"Relatório: {relatorio}")
        return 0

    _exigir_recorte(args)
    tipo = normalizar_tipo(args.tipo)
    local = localizar_arquivo_local(args.ano, tipo)
    temporario = localizar_temporario(args.ano, tipo)
    if args.baixar_temporario:
        download = baixar_arquivo_temporario(_selecionar_publicacao(args.ano, tipo))
        atualizar_registro_manifesto(download.metadados)
        print(f"Arquivo temporário validado: {download.path}")
        print(f"SHA-256: {download.diagnostico.sha256}")
        print(f"Encoding: {download.diagnostico.encoding}; separador: {download.diagnostico.separador}")
        return 0
    if args.comparar:
        resultado, diagnostico_local, diagnostico_remoto = comparar_arquivos(local, temporario)
        registrado = metadados_do_manifesto(args.ano, tipo)
        metadados = MetadadosRemotos(
            registrado.url if registrado else "URL não registrada",
            registrado.nome_arquivo if registrado else temporario.name,
            args.ano,
            tipo,
            diagnostico_remoto.tamanho_bytes,
            registrado.last_modified if registrado else None,
            registrado.etag if registrado else None,
            diagnostico_remoto.sha256,
            agora_iso(),
            "comparação concluída",
            None,
        )
        path = gerar_relatorios_comparacao(resultado, diagnostico_local, diagnostico_remoto, metadados)
        tem_diferencas = not resultado.novos.empty or not resultado.alterados.empty or not resultado.removidos.empty
        status = "atualização aguardando confirmação" if tem_diferencas else "comparação concluída"
        atualizar_status_manifesto(args.ano, tipo, status, diagnostico_remoto.sha256)
        print(resultado.mensagem)
        print(f"Relatório: {path}")
        return 0 if resultado.comparacao_segura else 2
    if args.aplicar_atualizacao:
        resultado = aplicar_atualizacao_controlada(local, temporario, args.confirmar)
        print(f"Atualização aplicada com backup: {resultado.backup}")
        return 0
    return 2


def main(argv: list[str] | None = None) -> int:
    try:
        return executar_cli(construir_parser().parse_args(argv))
    except (ErroSincronizacao, ErroValidacaoCSV, HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"[ERRO] {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
