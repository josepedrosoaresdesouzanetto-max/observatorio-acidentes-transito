from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import threading
import time
from types import SimpleNamespace
from urllib.error import HTTPError

import pandas as pd
import pytest

from src.comparar_arquivos_prf import ErroValidacaoCSV, carregar_csv_validado, comparar_arquivos, comparar_dataframes
from src.criar_colunas_derivadas import criar_derivadas
from src.sincronizar_dados_prf import (
    ErroSincronizacao,
    MetadadosRemotos,
    aplicar_atualizacao_controlada,
    baixar_arquivo_temporario,
    detectar_status_remoto,
    destino_seguro,
    gerar_relatorios_comparacao,
    gerar_relatorio_verificacao,
    main,
    obter_metadados_remotos,
    url_download_direto,
    verificar_publicacoes,
)


class RespostaFalsa:
    def __init__(self, conteudo: bytes = b"", headers: dict | None = None, status: int = 200):
        self._stream = BytesIO(conteudo)
        self.headers = headers or {}
        self.status = status

    def read(self, tamanho: int = -1) -> bytes:
        return self._stream.read(tamanho)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def publicacao(url: str = "https://exemplo.gov.br/acidentes_2025.csv"):
    return SimpleNamespace(url=url, ano=2025, tipo="ocorrencia", titulo="Ocorrências 2025")


def dataframe_base() -> pd.DataFrame:
    return pd.DataFrame({"id": ["1", "2"], "uf": ["SP", "RJ"], "mortos": ["0", "1"]})


def escrever_csv(path: Path, linhas: str, encoding: str = "utf-8") -> Path:
    path.write_bytes(linhas.encode(encoding))
    return path


def test_remoto_igual_ao_local():
    resultado = comparar_dataframes(dataframe_base(), dataframe_base().copy())
    assert resultado.inalterados == 2
    assert resultado.novos.empty and resultado.alterados.empty and resultado.removidos.empty
    assert resultado.chave_utilizada == ("id",)


def test_identifica_novas_linhas():
    remoto = pd.concat([dataframe_base(), pd.DataFrame({"id": ["3"], "uf": ["MG"], "mortos": ["0"]})], ignore_index=True)
    resultado = comparar_dataframes(dataframe_base(), remoto)
    assert resultado.novos["id"].tolist() == ["3"]


def test_identifica_linhas_alteradas_e_valores():
    remoto = dataframe_base().copy()
    remoto.loc[1, "uf"] = "MG"
    resultado = comparar_dataframes(dataframe_base(), remoto)
    assert resultado.alterados.iloc[0].to_dict() | {} == {
        "chave": '{"id": "2"}', "coluna": "uf", "valor_local": "RJ", "valor_remoto": "MG"
    }


def test_identifica_linhas_removidas():
    resultado = comparar_dataframes(dataframe_base(), dataframe_base().iloc[[0]].copy())
    assert resultado.removidos["id"].tolist() == ["2"]


def test_identifica_id_duplicado_e_faz_fallback():
    remoto = pd.DataFrame({"id": ["1", "1"], "uf": ["SP", "RJ"], "mortos": ["0", "1"]})
    resultado = comparar_dataframes(dataframe_base(), remoto)
    assert resultado.duplicados_remoto == 2
    assert resultado.estrategia_chave == "hash_linha"


def test_id_ausente_faz_fallback_para_hash_de_linha():
    local = pd.DataFrame({"uf": ["SP", "RJ"], "valor": ["a", "b"]})
    resultado = comparar_dataframes(local, local.copy())
    assert resultado.estrategia_chave == "hash_linha"
    assert resultado.inalterados == 2


def test_sem_chave_segura_quando_hash_tambem_duplica():
    local = pd.DataFrame({"uf": ["SP", "SP"], "valor": ["a", "a"]})
    resultado = comparar_dataframes(local, local.copy())
    assert not resultado.comparacao_segura
    assert resultado.mensagem == "Não foi possível identificar registros de forma segura."


def test_comparacao_nao_altera_dataframes():
    local = dataframe_base()
    remoto = dataframe_base()
    copia_local, copia_remoto = local.copy(deep=True), remoto.copy(deep=True)
    comparar_dataframes(local, remoto)
    pd.testing.assert_frame_equal(local, copia_local)
    pd.testing.assert_frame_equal(remoto, copia_remoto)


@pytest.mark.parametrize(
    ("encoding", "separador"),
    [("utf-8", ";"), ("utf-8", ","), ("latin-1", ";"), ("latin-1", ",")],
)
def test_detecta_encoding_e_separador(tmp_path, encoding, separador):
    path = escrever_csv(tmp_path / "dados.csv", f"id{separador}município\n1{separador}São Paulo\n", encoding)
    _, diagnostico = carregar_csv_validado(path)
    assert diagnostico.separador == separador
    assert diagnostico.encoding in {encoding, "utf-8-sig"}
    assert diagnostico.linhas == 1


def test_recusa_arquivo_vazio(tmp_path):
    path = tmp_path / "vazio.csv"
    path.write_bytes(b"")
    with pytest.raises(ErroValidacaoCSV, match="vazio"):
        carregar_csv_validado(path)


def test_recusa_html_com_extensao_csv(tmp_path):
    path = escrever_csv(tmp_path / "falso.csv", "<html><body>erro</body></html>")
    with pytest.raises(ErroValidacaoCSV, match="HTML"):
        carregar_csv_validado(path)


def test_metadados_funcionam_sem_headers_opcionais():
    metadados = obter_metadados_remotos(publicacao(), opener=lambda *_args, **_kwargs: RespostaFalsa())
    assert metadados.etag is None
    assert metadados.last_modified is None
    assert metadados.content_length is None


def test_metadados_registram_headers_disponiveis():
    headers = {"ETag": '"abc"', "Last-Modified": "Mon, 01 Jun 2026 10:00:00 GMT", "Content-Length": "123"}
    metadados = obter_metadados_remotos(publicacao(), opener=lambda *_args, **_kwargs: RespostaFalsa(headers=headers))
    assert (metadados.etag, metadados.last_modified, metadados.content_length) == ('"abc"', headers["Last-Modified"], 123)


def test_timeout_tem_mensagem_controlada():
    def timeout(*_args, **_kwargs):
        raise TimeoutError("tempo esgotado")

    with pytest.raises(ErroSincronizacao, match="Falha de rede"):
        obter_metadados_remotos(publicacao(), opener=timeout)


def test_http_404_tem_mensagem_controlada():
    def nao_encontrado(request, **_kwargs):
        raise HTTPError(request.full_url, 404, "Not Found", {}, None)

    with pytest.raises(ErroSincronizacao, match="HTTP 404"):
        obter_metadados_remotos(publicacao(), opener=nao_encontrado)


def test_download_temporario_valida_e_renomeia(tmp_path):
    conteudo = b"id;uf\n1;SP\n"
    headers = {"Content-Type": "text/csv", "Content-Length": str(len(conteudo))}
    resultado = baixar_arquivo_temporario(
        publicacao(), diretorio=tmp_path, opener=lambda *_args, **_kwargs: RespostaFalsa(conteudo, headers)
    )
    assert resultado.path.name == "prf_2025_ocorrencia.csv"
    assert resultado.path.exists()
    assert not (tmp_path / "prf_2025_ocorrencia.csv.part").exists()


def test_download_interrompido_e_recusado(tmp_path):
    conteudo = b"id;uf\n1;SP\n"
    headers = {"Content-Type": "text/csv", "Content-Length": str(len(conteudo) + 10)}
    with pytest.raises(ErroSincronizacao, match="incompleto"):
        baixar_arquivo_temporario(publicacao(), diretorio=tmp_path, opener=lambda *_a, **_k: RespostaFalsa(conteudo, headers))


def test_download_recusa_html(tmp_path):
    conteudo = b"<html><body>erro</body></html>"
    with pytest.raises(ErroSincronizacao, match="HTML"):
        baixar_arquivo_temporario(
            publicacao(), diretorio=tmp_path, opener=lambda *_a, **_k: RespostaFalsa(conteudo, {"Content-Type": "text/html"})
        )


def test_path_traversal_fica_contido_no_diretorio(tmp_path):
    destino = destino_seguro(tmp_path, "../../fora.csv")
    assert destino.parent == tmp_path.resolve()
    assert destino.name == "fora.csv"


def test_converte_link_google_drive_para_download_direto():
    url = "https://drive.google.com/file/d/abc-123/view?usp=sharing/download"
    assert url_download_direto(url) == "https://drive.usercontent.google.com/download?id=abc-123&export=download&confirm=t"


def test_prioridade_da_deteccao_de_mudanca():
    anterior = {"sha256": "a", "etag": "igual", "last_modified": "x", "content_length": 10}
    assert detectar_status_remoto({"sha256": "b", "etag": "igual"}, anterior) == "possível atualização detectada"
    assert detectar_status_remoto({"sha256": "a", "etag": "diferente"}, anterior) == "sem mudança detectada"
    assert detectar_status_remoto({"sha256": None, "etag": None}, anterior) == "comparação pendente"
    assert detectar_status_remoto({"sha256": None}, None) == "novo arquivo publicado"


def test_verificacao_offline_grava_manifesto(tmp_path):
    manifesto = tmp_path / "manifesto.json"
    metadados = MetadadosRemotos(
        publicacao().url, "acidentes_2025.csv", 2025, "ocorrencia", None, None, None, None, "2026-01-01T00:00:00"
    )
    resultados = verificar_publicacoes([publicacao()], manifesto, consultar=lambda _arquivo: metadados)
    assert resultados[0].status in {"novo arquivo publicado", "comparação pendente"}
    assert manifesto.exists()
    assert publicacao().url in manifesto.read_text(encoding="utf-8")


def _metadados_para(arquivo):
    return MetadadosRemotos(
        arquivo.url,
        Path(arquivo.url).name,
        arquivo.ano,
        arquivo.tipo,
        100,
        "Mon, 01 Jun 2026 10:00:00 GMT",
        '"etag"',
        None,
        "2026-01-01T00:00:00",
    )


def test_consulta_paralela_isola_timeout_http_e_preserva_ordem(tmp_path):
    urls = ["https://oficial/slow.csv", "https://oficial/ok.csv", "https://oficial/timeout.csv", "https://oficial/404.csv"]
    arquivos = [SimpleNamespace(url=url, ano=2020 + indice, tipo="ocorrencia", titulo=url) for indice, url in enumerate(urls)]
    lento_iniciado = threading.Event()
    liberar_lento = threading.Event()

    def consultar(arquivo):
        if "slow" in arquivo.url:
            lento_iniciado.set()
            liberar_lento.wait(timeout=1)
            return _metadados_para(arquivo)
        assert lento_iniciado.wait(timeout=0.5)
        liberar_lento.set()
        if "timeout" in arquivo.url:
            raise TimeoutError("fonte lenta")
        if "404" in arquivo.url:
            raise HTTPError(arquivo.url, 404, "Not Found", {}, None)
        return _metadados_para(arquivo)

    inicio = time.monotonic()
    resultados = verificar_publicacoes(arquivos, tmp_path / "manifesto.json", consultar=consultar, max_workers=4)
    duracao = time.monotonic() - inicio

    assert duracao < 0.8
    assert [item.url for item in resultados] == urls
    assert resultados[0].erro is None and resultados[1].erro is None
    assert resultados[2].status == "comparação pendente" and "fonte lenta" in resultados[2].erro
    assert resultados[3].status == "comparação pendente" and "404" in resultados[3].erro
    manifesto = json.loads((tmp_path / "manifesto.json").read_text(encoding="utf-8"))
    assert [item["url"] for item in manifesto["arquivos"]] == urls


def test_todos_links_indisponiveis_concluem_e_manifesto_e_valido(tmp_path):
    arquivos = [SimpleNamespace(url=f"https://oficial/{indice}.csv", ano=2020 + indice, tipo="pessoa") for indice in range(6)]

    def indisponivel(_arquivo):
        raise TimeoutError("timeout externo")

    manifesto_path = tmp_path / "manifesto.json"
    resultados = verificar_publicacoes(arquivos, manifesto_path, consultar=indisponivel, max_workers=3)
    assert len(resultados) == 6
    assert all(item.status == "comparação pendente" and item.erro for item in resultados)
    assert len(json.loads(manifesto_path.read_text(encoding="utf-8"))["arquivos"]) == 6
    relatorio = gerar_relatorio_verificacao(resultados, tmp_path / "relatorio.md")
    texto = relatorio.read_text(encoding="utf-8")
    assert "limitação da fonte externa" in texto
    assert "Nenhum CSV completo foi baixado" in texto


def test_limite_absoluto_de_oito_trabalhadores(tmp_path):
    lock = threading.Lock()
    ativos = 0
    maximo_ativo = 0
    arquivos = [SimpleNamespace(url=f"https://oficial/{indice}.csv", ano=2000 + indice, tipo="ocorrencia") for indice in range(16)]

    def consultar(arquivo):
        nonlocal ativos, maximo_ativo
        with lock:
            ativos += 1
            maximo_ativo = max(maximo_ativo, ativos)
        time.sleep(0.03)
        with lock:
            ativos -= 1
        return _metadados_para(arquivo)

    verificar_publicacoes(arquivos, tmp_path / "manifesto.json", consultar=consultar, max_workers=99)
    assert maximo_ativo <= 8


def test_timeout_individual_padrao_e_limitado(monkeypatch, tmp_path):
    timeouts = []
    arquivos = [SimpleNamespace(url=f"https://oficial/{indice}.csv", ano=2020 + indice, tipo="ocorrencia") for indice in range(3)]

    def consultar_fake(arquivo, opener=None, timeout=0):
        timeouts.append(timeout)
        return _metadados_para(arquivo)

    monkeypatch.setattr("src.sincronizar_dados_prf.obter_metadados_remotos", consultar_fake)
    verificar_publicacoes(arquivos, tmp_path / "manifesto.json")
    assert timeouts == [8, 8, 8]


def test_gera_relatorios_e_tabelas_de_diferencas(tmp_path):
    local_path = escrever_csv(tmp_path / "local.csv", "id;uf\n1;SP\n2;RJ\n")
    remoto_path = escrever_csv(tmp_path / "remoto.csv", "id;uf\n1;MG\n3;BA\n")
    resultado, local, remoto = comparar_arquivos(local_path, remoto_path)
    metadados = MetadadosRemotos(
        publicacao().url, remoto_path.name, 2025, "ocorrencia", remoto.tamanho_bytes, None, None, remoto.sha256, "agora"
    )
    relatorio = gerar_relatorios_comparacao(
        resultado, local, remoto, metadados, tmp_path / "relatorio.md", tmp_path / "tabelas"
    )
    assert relatorio.exists()
    assert (tmp_path / "tabelas" / "resumo_sincronizacao.csv").exists()
    assert (tmp_path / "tabelas" / "novas_ocorrencias.csv").exists()
    assert "Registros novos: 1" in relatorio.read_text(encoding="utf-8")


def test_aplicacao_sem_confirmar_e_bloqueada(tmp_path):
    local = escrever_csv(tmp_path / "local.csv", "id;uf\n1;SP\n")
    remoto = escrever_csv(tmp_path / "remoto.csv", "id;uf\n1;RJ\n")
    with pytest.raises(ErroSincronizacao, match="--confirmar"):
        aplicar_atualizacao_controlada(local, remoto, confirmar=False, backups_dir=tmp_path / "backups")


def test_cli_recusa_aplicacao_sem_confirmar(capsys):
    codigo = main(["--aplicar-atualizacao", "--ano", "2025", "--tipo", "ocorrencias"])
    assert codigo == 2
    assert "--confirmar" in capsys.readouterr().out


def test_aplicacao_cria_backup(tmp_path):
    local = escrever_csv(tmp_path / "local.csv", "id;uf\n1;SP\n")
    remoto = escrever_csv(tmp_path / "remoto.csv", "id;uf\n1;RJ\n")
    resultado = aplicar_atualizacao_controlada(local, remoto, True, tmp_path / "backups")
    assert resultado.backup.exists()
    assert "RJ" in local.read_text(encoding="utf-8")
    assert "SP" in resultado.backup.read_text(encoding="utf-8")


def test_falha_de_validacao_executa_rollback(tmp_path):
    local = escrever_csv(tmp_path / "local.csv", "id;uf\n1;SP\n")
    remoto = escrever_csv(tmp_path / "remoto.csv", "id;uf\n1;RJ\n")
    with pytest.raises(ErroSincronizacao, match="rollback executado"):
        aplicar_atualizacao_controlada(local, remoto, True, tmp_path / "backups", validador=lambda _path: False)
    assert "SP" in local.read_text(encoding="utf-8")


def test_datas_bissextas_validas_sao_preservadas_e_invalidas_rejeitadas():
    original = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "data_inversa": ["2024-02-29", "2025-02-29", "2024-03-01"],
            "horario": ["10:00:00"] * 3,
        }
    )
    resultado = criar_derivadas(original)
    assert len(resultado) == 3
    assert resultado.loc[0, "data_inversa"] == pd.Timestamp("2024-02-29")
    assert pd.isna(resultado.loc[1, "data_inversa"])
    assert resultado.loc[2, "data_inversa"] == pd.Timestamp("2024-03-01")


def test_recorte_de_datas_nao_pressupoe_ano_fixo_de_365_dias():
    original = pd.DataFrame(
        {"id": [1, 2], "data_inversa": ["2023-02-28", "2024-02-29"], "horario": ["00:00:00", "00:00:00"]}
    )
    resultado = criar_derivadas(original)
    assert resultado["data_inversa"].notna().all()
    assert (resultado.loc[1, "data_inversa"] - resultado.loc[0, "data_inversa"]).days == 366
