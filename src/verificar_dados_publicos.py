from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import re
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd

from src.auditar_dados import gerar_manifesto_dados, gerar_relatorio_qualidade, validar_layout_brutos
from src.carregar_dados import anos_disponiveis, localizar_arquivos, resolver_anos_analise
from src.config import (
    ANO_INICIAL_ANALISE,
    DADOS_DIR,
    LOGS_DIR,
    MODELADOS_DIR,
    OCORRENCIA_BRUTOS_DIR,
    PESSOA_BRUTOS_DIR,
    PROJECT_ROOT,
    TRATADOS_DIR,
    URL_DADOS_ABERTOS_PRF,
)
from src.recorte_temporal import anos_parciais
from src.utils import ler_csv_prf, normalizar_nome_coluna


COLUNAS_OCORRENCIAS_OBRIGATORIAS = {
    "id",
    "data_inversa",
    "uf",
    "br",
    "municipio",
    "causa_acidente",
    "tipo_acidente",
    "ano",
    "mortos",
    "acidente_fatal",
    "feridos_graves",
    "feridos_leves",
}

COLUNAS_PESSOAS_RELEVANTES = {
    "id",
    "uf",
    "ano",
    "tipo_envolvido",
    "estado_fisico",
    "idade",
    "sexo",
}

COLUNAS_SENSIVEIS = {
    "cpf",
    "cnpj",
    "nome",
    "email",
    "telefone",
    "celular",
    "endereco",
    "placa",
    "renavam",
    "chassi",
}

ARQUIVOS_PROIBIDOS = {".env", ".env.local", ".env.production"}
PASTAS_CACHE = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PADROES_CSV_FORA_DADOS = ("acidentes*.csv", "datatran*.csv")


@dataclass
class ResultadoVerificacao:
    status: str
    item: str
    detalhe: str


@dataclass(frozen=True)
class ArquivoPublicoPRF:
    ano: int
    tipo: str
    titulo: str
    url: str


class ParserDadosAbertosPRF(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.tokens: list[tuple[str, str, str | None]] = []
        self._href_atual: str | None = None
        self._texto_link: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        atributos = dict(attrs)
        href = atributos.get("href")
        if href:
            self._href_atual = urljoin(self.base_url, href)
            self._texto_link = []

    def handle_data(self, data: str) -> None:
        texto = " ".join(data.split())
        if not texto:
            return
        if self._href_atual:
            self._texto_link.append(texto)
        else:
            self.tokens.append(("texto", texto, None))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href_atual:
            texto = " ".join(self._texto_link).strip()
            self.tokens.append(("link", texto, self._href_atual))
            self._href_atual = None
            self._texto_link = []


def ok(item: str, detalhe: str) -> ResultadoVerificacao:
    return ResultadoVerificacao("OK", item, detalhe)


def aviso(item: str, detalhe: str) -> ResultadoVerificacao:
    return ResultadoVerificacao("AVISO", item, detalhe)


def erro(item: str, detalhe: str) -> ResultadoVerificacao:
    return ResultadoVerificacao("ERRO", item, detalhe)


def ler_cabecalho(path: Path) -> set[str]:
    df = ler_csv_prf(path, nrows=0)
    return {normalizar_nome_coluna(coluna) for coluna in df.columns}


def ler_csv_tratado(path: Path, colunas: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", usecols=colunas, low_memory=False)


def normalizar_texto(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def extrair_arquivos_publicos_prf(html: str, base_url: str = URL_DADOS_ABERTOS_PRF) -> list[ArquivoPublicoPRF]:
    parser = ParserDadosAbertosPRF(base_url)
    parser.feed(html)

    arquivos: list[ArquivoPublicoPRF] = []
    referencia_atual: tuple[int, str, str] | None = None
    padrao = re.compile(r"documento csv de acidentes\s+(20\d{2}).*agrupados por\s+(ocorrencia|pessoa)")

    for tipo_token, texto, href in parser.tokens:
        texto_normalizado = normalizar_texto(texto)
        if tipo_token == "texto":
            match = padrao.search(texto_normalizado)
            if match and "todas as causas" not in texto_normalizado:
                ano = int(match.group(1))
                tipo_arquivo = match.group(2)
                referencia_atual = (ano, tipo_arquivo, texto)
            continue

        if tipo_token == "link" and referencia_atual and href:
            ano, tipo_arquivo, titulo = referencia_atual
            arquivos.append(ArquivoPublicoPRF(ano=ano, tipo=tipo_arquivo, titulo=titulo, url=href))
            referencia_atual = None

    deduplicados: dict[tuple[int, str], ArquivoPublicoPRF] = {}
    for arquivo in arquivos:
        deduplicados[(arquivo.ano, arquivo.tipo)] = arquivo
    ordem_tipo = {"ocorrencia": 0, "pessoa": 1}
    return sorted(deduplicados.values(), key=lambda item: (-item.ano, ordem_tipo.get(item.tipo, 99)))


def consultar_arquivos_publicos_prf(
    url: str = URL_DADOS_ABERTOS_PRF,
    timeout: int = 30,
) -> list[ArquivoPublicoPRF]:
    request = Request(url, headers={"User-Agent": "observatorio-acidentes-transito/1.0"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")
    return extrair_arquivos_publicos_prf(html, base_url=url)


def verificar_fonte_publica_online() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    try:
        arquivos_publicos = consultar_arquivos_publicos_prf()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return [
            aviso(
                "Consulta online da PRF",
                f"Nao foi possivel consultar a pagina oficial agora: {exc}. A verificacao local foi mantida.",
            )
        ]

    if not arquivos_publicos:
        return [aviso("Consulta online da PRF", "Pagina consultada, mas nenhum CSV de acidentes foi identificado.")]

    anos_publicos = sorted({arquivo.ano for arquivo in arquivos_publicos})
    ocorrencias_publicas = {arquivo.ano for arquivo in arquivos_publicos if arquivo.tipo == "ocorrencia"}
    pessoas_publicas = {arquivo.ano for arquivo in arquivos_publicos if arquivo.tipo == "pessoa"}
    anos_locais_ocorrencia = set(anos_disponiveis("ocorrencia"))
    anos_locais_pessoa = set(anos_disponiveis("pessoa"))
    anos_publicos_recorte = {ano for ano in ocorrencias_publicas if ano >= ANO_INICIAL_ANALISE}

    resultados.append(
        ok(
            "Consulta online da PRF",
            f"Pagina oficial consultada. Anos publicados para acidentes: {anos_publicos}.",
        )
    )

    faltantes_ocorrencia = sorted(anos_publicos_recorte - anos_locais_ocorrencia)
    if faltantes_ocorrencia:
        resultados.append(
            aviso(
                "Ocorrencias publicas novas",
                f"Ha ano(s) publicados na PRF sem CSV local de ocorrencia: {faltantes_ocorrencia}. Nao foi feito download automatico.",
            )
        )
    else:
        resultados.append(ok("Ocorrencias publicas novas", "Arquivos locais cobrem os anos publicados da PRF dentro do recorte."))

    anos_pessoa_recorte = {ano for ano in pessoas_publicas if ano >= ANO_INICIAL_ANALISE}
    faltantes_pessoa = sorted(anos_pessoa_recorte - anos_locais_pessoa)
    if faltantes_pessoa:
        resultados.append(
            aviso(
                "Pessoas publicas novas",
                f"Ha ano(s) publicados na PRF sem CSV local de pessoa: {faltantes_pessoa}. Nao foi feito download automatico.",
            )
        )
    else:
        resultados.append(ok("Pessoas publicas novas", "Arquivos locais de pessoa cobrem os anos publicados dentro do recorte."))

    return resultados


def verificar_documentacao_fonte() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    fonte_path = PROJECT_ROOT / "docs" / "02_fonte_dos_dados.md"
    manifesto_path = DADOS_DIR / "00_arquivos_originais_encontrados" / "MANIFESTO_ARQUIVOS_ORIGINAIS.md"

    if not fonte_path.exists():
        resultados.append(erro("Documentacao da fonte", "Arquivo docs/02_fonte_dos_dados.md nao encontrado."))
    else:
        texto = fonte_path.read_text(encoding="utf-8", errors="ignore").lower()
        menciona_prf = "prf" in texto or "policia rodoviaria federal" in texto or "polícia rodoviária federal" in texto
        menciona_publico = "public" in texto or "públic" in texto
        if menciona_prf and menciona_publico:
            resultados.append(ok("Documentacao da fonte", "Fonte publica da PRF documentada."))
        else:
            resultados.append(aviso("Documentacao da fonte", "Documentacao existe, mas nao deixa claramente PRF/publico."))

    if manifesto_path.exists():
        resultados.append(ok("Manifesto de originais", "Manifesto dos arquivos originais encontrado."))
    else:
        resultados.append(aviso("Manifesto de originais", "Manifesto de arquivos originais nao encontrado."))
    return resultados


def verificar_arquivos_brutos() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    ocorrencias = localizar_arquivos("ocorrencia")
    pessoas = localizar_arquivos("pessoa")
    anos_ocorrencia = anos_disponiveis("ocorrencia")
    anos_pessoa = anos_disponiveis("pessoa")
    anos_pipeline = resolver_anos_analise()

    for pasta, nome in ((OCORRENCIA_BRUTOS_DIR, "ocorrencia"), (PESSOA_BRUTOS_DIR, "pessoa")):
        if pasta.exists():
            resultados.append(ok(f"Pasta bruta {nome}", str(pasta.relative_to(PROJECT_ROOT))))
        else:
            resultados.append(erro(f"Pasta bruta {nome}", f"Pasta ausente: {pasta}"))

    if ocorrencias:
        resultados.append(ok("CSVs brutos de ocorrencia", f"{len(ocorrencias)} arquivo(s). Anos encontrados: {list(anos_ocorrencia)}."))
    else:
        resultados.append(erro("CSVs brutos de ocorrencia", "Nenhum arquivo acidentes_*_*.csv encontrado."))

    if pessoas:
        resultados.append(ok("CSVs brutos de pessoa", f"{len(pessoas)} arquivo(s). Anos encontrados: {list(anos_pessoa)}."))
    else:
        resultados.append(erro("CSVs brutos de pessoa", "Nenhum arquivo acidentes_*_*.csv encontrado para pessoas."))

    resultados.append(
        ok(
            "Recorte automatico do pipeline",
            f"Anos de ocorrencia a partir de {ANO_INICIAL_ANALISE}: {list(anos_pipeline)}.",
        )
    )
    anos_pessoa_faltantes = sorted(set(anos_pipeline) - set(anos_pessoa))
    if anos_pessoa_faltantes:
        resultados.append(
            aviso(
                "Cobertura da base de pessoas",
                f"Sem arquivo de pessoa para ano(s) {anos_pessoa_faltantes}; a analise principal por ocorrencia continua disponivel.",
            )
        )

    return resultados


def verificar_layout_brutos() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    for resultado in validar_layout_brutos():
        if resultado.status == "ERRO":
            resultados.append(erro(resultado.item, resultado.detalhe))
        elif resultado.status == "AVISO":
            resultados.append(aviso(resultado.item, resultado.detalhe))
        else:
            resultados.append(ok(resultado.item, resultado.detalhe))
    return resultados


def verificar_manifesto_e_qualidade() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    try:
        manifesto = gerar_manifesto_dados()
        resultados.append(ok("Manifesto de dados brutos", f"{len(manifesto)} arquivo(s) auditado(s) com hash SHA-256."))
    except Exception as exc:
        resultados.append(erro("Manifesto de dados brutos", f"Falha ao gerar manifesto: {exc}"))

    try:
        qualidade = gerar_relatorio_qualidade()
        problemas = qualidade[
            qualidade["metrica"].astype(str).str.startswith(("ids_duplicados", "negativos_"))
            & (pd.to_numeric(qualidade["valor"], errors="coerce").fillna(0) > 0)
        ]
        if problemas.empty:
            resultados.append(ok("Qualidade dos dados tratados", f"{len(qualidade)} metrica(s) gerada(s), sem duplicidade de ID ou negativos."))
        else:
            detalhes = "; ".join(f"{row.metrica}={row.valor}" for row in problemas.itertuples())
            resultados.append(aviso("Qualidade dos dados tratados", f"Metricas geradas com pontos de atencao: {detalhes}."))
    except Exception as exc:
        resultados.append(aviso("Qualidade dos dados tratados", f"Nao foi possivel gerar relatorio de qualidade: {exc}"))

    return resultados


def extrair_ano_arquivo(path: Path) -> int | None:
    for parte in path.stem.replace("-", "_").split("_"):
        if parte.isdigit() and len(parte) == 4 and parte.startswith("20"):
            return int(parte)
    return None


def verificar_colunas_sensiveis_em_csvs(paths: list[Path]) -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    achados: list[str] = []
    for path in paths:
        try:
            colunas = ler_cabecalho(path)
        except Exception as exc:  # pragma: no cover - mensagem operacional
            resultados.append(aviso("Leitura de cabecalho", f"Nao foi possivel ler {path.name}: {exc}"))
            continue
        sensiveis = sorted(colunas & COLUNAS_SENSIVEIS)
        if sensiveis:
            achados.append(f"{path.relative_to(PROJECT_ROOT)}: {sensiveis}")

    if achados:
        resultados.append(erro("Colunas sensiveis", "Possiveis colunas sensiveis encontradas: " + " | ".join(achados)))
    else:
        resultados.append(ok("Colunas sensiveis", "Nenhuma coluna sensivel obvia encontrada nos CSVs verificados."))
    return resultados


def verificar_tratados() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    ocorrencias_path = TRATADOS_DIR / "ocorrencias_tratadas.csv"
    pessoas_path = TRATADOS_DIR / "pessoas_tratadas.csv"

    if not ocorrencias_path.exists():
        resultados.append(erro("Ocorrencias tratadas", "Arquivo dados/02_tratados/ocorrencias_tratadas.csv ausente."))
        return resultados

    cabecalho_ocorrencias = ler_cabecalho(ocorrencias_path)
    faltantes = sorted(COLUNAS_OCORRENCIAS_OBRIGATORIAS - cabecalho_ocorrencias)
    if faltantes:
        resultados.append(erro("Colunas de ocorrencias tratadas", f"Colunas obrigatorias ausentes: {faltantes}."))
    else:
        resultados.append(ok("Colunas de ocorrencias tratadas", "Colunas essenciais presentes."))

    try:
        colunas_validacao = ["mortos", "acidente_fatal", "ano", "uf"]
        ocorrencias = ler_csv_tratado(ocorrencias_path, colunas_validacao)
        resultados.extend(verificar_variavel_alvo(ocorrencias))
        resultados.extend(verificar_recorte_temporal(ocorrencias))
    except Exception as exc:
        resultados.append(erro("Leitura de ocorrencias tratadas", f"Falha ao validar dados tratados: {exc}"))

    if not pessoas_path.exists():
        resultados.append(aviso("Pessoas tratadas", "Arquivo dados/02_tratados/pessoas_tratadas.csv ausente."))
    else:
        cabecalho_pessoas = ler_cabecalho(pessoas_path)
        relevantes = sorted(COLUNAS_PESSOAS_RELEVANTES & cabecalho_pessoas)
        resultados.append(ok("Pessoas tratadas", f"Arquivo encontrado. Colunas relevantes presentes: {relevantes}."))

    return resultados


def verificar_variavel_alvo(df: pd.DataFrame) -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    mortos = pd.to_numeric(df["mortos"], errors="coerce").fillna(0)
    acidente_fatal = pd.to_numeric(df["acidente_fatal"], errors="coerce").fillna(-1).astype(int)
    esperado = (mortos >= 1).astype(int)
    divergencias = int((acidente_fatal != esperado).sum())

    valores_invalidos = sorted(set(acidente_fatal.unique()) - {0, 1})
    if valores_invalidos:
        resultados.append(erro("Valores de acidente_fatal", f"Valores invalidos encontrados: {valores_invalidos}."))
    else:
        resultados.append(ok("Valores de acidente_fatal", "Variavel binaria com valores 0/1."))

    if divergencias:
        resultados.append(erro("Regra acidente_fatal", f"{divergencias} linha(s) divergem da regra mortos >= 1."))
    else:
        resultados.append(ok("Regra acidente_fatal", "mortos >= 1 -> 1; mortos = 0 -> 0."))
    return resultados


def verificar_recorte_temporal(df: pd.DataFrame) -> list[ResultadoVerificacao]:
    ano = pd.to_numeric(df["ano"], errors="coerce").dropna().astype(int)
    anos_encontrados = tuple(sorted(ano.unique().tolist()))
    anos_esperados = resolver_anos_analise()
    resultados: list[ResultadoVerificacao] = []

    faltantes = sorted(set(anos_esperados) - set(anos_encontrados))
    if faltantes:
        resultados.append(aviso("Recorte temporal", f"Anos detectados nos brutos ainda ausentes nos tratados: {faltantes}. Rode python -m src.limpar_dados."))
    else:
        resultados.append(ok("Recorte temporal", f"Tratados sincronizados com o recorte automatico: {anos_encontrados}."))

    legados = sorted((set(anos_encontrados) - set(anos_esperados)) & set(range(2000, ANO_INICIAL_ANALISE)))
    if legados:
        resultados.append(aviso("Anos fora do recorte principal", f"Tratados contem ano(s) anteriores a {ANO_INICIAL_ANALISE}: {legados}."))

    for ano_parcial in anos_parciais(anos_encontrados):
        resultados.append(
            aviso(
                f"{ano_parcial} parcial",
                f"Ano {ano_parcial} presente e ainda em andamento; interpretar como recorte parcial.",
            )
        )
    return resultados


def verificar_modelados() -> list[ResultadoVerificacao]:
    esperados = [
        "indice_risco_uf.csv",
        "indice_risco_br.csv",
        "indice_risco_municipio.csv",
        "indice_risco_causa_acidente.csv",
        "indice_risco_faixa_horario.csv",
    ]
    faltantes = [nome for nome in esperados if not (MODELADOS_DIR / nome).exists()]
    if faltantes:
        return [aviso("Arquivos modelados", f"Arquivos ausentes: {faltantes}. Rode python -m src.modelar_dados e python -m src.calcular_indice_risco.")]
    return [ok("Arquivos modelados", "Arquivos modelados esperados encontrados.")]


def verificar_arquivos_indesejados() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    achados_criticos: list[str] = []
    achados_cache: list[str] = []

    for path in PROJECT_ROOT.rglob("*"):
        if any(part in PASTAS_CACHE for part in path.parts):
            achados_cache.append(str(path.relative_to(PROJECT_ROOT)))
            continue
        if path.is_file() and path.name in ARQUIVOS_PROIBIDOS:
            achados_criticos.append(str(path.relative_to(PROJECT_ROOT)))

    csvs_fora_dados: list[str] = []
    for padrao in PADROES_CSV_FORA_DADOS:
        for path in PROJECT_ROOT.glob(padrao):
            if path.is_file():
                csvs_fora_dados.append(str(path.relative_to(PROJECT_ROOT)))

    if achados_criticos:
        resultados.append(erro("Arquivos proibidos", "Arquivos sensiveis encontrados: " + ", ".join(sorted(achados_criticos))))
    else:
        resultados.append(ok("Arquivos proibidos", "Nenhum .env encontrado no projeto."))

    if csvs_fora_dados:
        resultados.append(aviso("CSVs fora da camada dados", "CSVs soltos encontrados: " + ", ".join(sorted(csvs_fora_dados))))
    else:
        resultados.append(ok("CSVs fora da camada dados", "Nenhum acidentes*.csv/datatran*.csv solto na raiz."))

    if achados_cache:
        resultados.append(aviso("Caches locais", f"{len(set(achados_cache))} item(ns) de cache encontrados; nao versionar."))
    else:
        resultados.append(ok("Caches locais", "Nenhum cache comum encontrado."))
    return resultados


def verificar_dados_publicos() -> list[ResultadoVerificacao]:
    resultados: list[ResultadoVerificacao] = []
    resultados.extend(verificar_documentacao_fonte())
    resultados.extend(verificar_fonte_publica_online())
    resultados.extend(verificar_arquivos_brutos())
    resultados.extend(verificar_layout_brutos())
    resultados.extend(verificar_manifesto_e_qualidade())

    csvs_para_checar = localizar_arquivos("ocorrencia") + localizar_arquivos("pessoa")
    for tratado in (TRATADOS_DIR / "ocorrencias_tratadas.csv", TRATADOS_DIR / "pessoas_tratadas.csv"):
        if tratado.exists():
            csvs_para_checar.append(tratado)
    resultados.extend(verificar_colunas_sensiveis_em_csvs(csvs_para_checar))

    resultados.extend(verificar_tratados())
    resultados.extend(verificar_modelados())
    resultados.extend(verificar_arquivos_indesejados())
    return resultados


def gerar_texto_relatorio(resultados: list[ResultadoVerificacao], gerado_em: datetime | None = None) -> str:
    gerado_em = gerado_em or datetime.now()
    linhas = [
        "# Verificacao de dados publicos",
        "",
        f"Gerado em: {gerado_em:%Y-%m-%d %H:%M:%S}",
        "",
        "Objetivo: confirmar que o projeto usa dados publicos da PRF e que a base tratada esta coerente.",
        "",
    ]
    for resultado in resultados:
        linhas.append(f"[{resultado.status}] {resultado.item}: {resultado.detalhe}")
    linhas.append("")
    erros = sum(resultado.status == "ERRO" for resultado in resultados)
    avisos = sum(resultado.status == "AVISO" for resultado in resultados)
    linhas.append(f"Resumo: {erros} erro(s), {avisos} aviso(s), {len(resultados) - erros - avisos} ok.")
    if erros:
        linhas.append("Resultado final: REPROVADO para entrega ate corrigir os erros.")
    else:
        linhas.append("Resultado final: APROVADO com observacao dos avisos.")
    return "\n".join(linhas) + "\n"


def imprimir_relatorio(resultados: list[ResultadoVerificacao]) -> None:
    print(gerar_texto_relatorio(resultados), end="")


def salvar_relatorio(
    resultados: list[ResultadoVerificacao],
    path: Path | str | None = None,
) -> Path:
    destino = Path(path) if path else LOGS_DIR / "status_dados_publicos.md"
    if not destino.is_absolute():
        destino = PROJECT_ROOT / destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_texto_relatorio(resultados), encoding="utf-8", newline="\n")
    return destino


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verifica fonte publica da PRF e consistencia local sem baixar ou sobrescrever dados.",
    )
    parser.add_argument(
        "--salvar-relatorio",
        nargs="?",
        const=str(LOGS_DIR / "status_dados_publicos.md"),
        help="Salva o relatorio Markdown no caminho informado, ou em logs/status_dados_publicos.md se nenhum caminho for passado.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    resultados = verificar_dados_publicos()
    imprimir_relatorio(resultados)
    if args.salvar_relatorio:
        destino = salvar_relatorio(resultados, args.salvar_relatorio)
        print(f"Relatorio salvo em: {destino}")
    return 1 if any(resultado.status == "ERRO" for resultado in resultados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
