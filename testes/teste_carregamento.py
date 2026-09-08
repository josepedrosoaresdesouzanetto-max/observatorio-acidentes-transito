from pathlib import Path

import pytest

from src.carregar_dados import anos_disponiveis, carregar_dados, localizar_arquivos, resolver_anos_analise
from src.config import OCORRENCIA_BRUTOS_DIR, PESSOA_BRUTOS_DIR, TRATADOS_DIR


DADOS_BRUTOS_DISPONIVEIS = (
    OCORRENCIA_BRUTOS_DIR.exists()
    and PESSOA_BRUTOS_DIR.exists()
    and any(OCORRENCIA_BRUTOS_DIR.glob("*.csv"))
    and any(PESSOA_BRUTOS_DIR.glob("*.csv"))
)
ARQUIVOS_TRATADOS = (
    TRATADOS_DIR / "ocorrencias_tratadas.csv",
    TRATADOS_DIR / "pessoas_tratadas.csv",
)
TRATADOS_DISPONIVEIS = all(path.exists() for path in ARQUIVOS_TRATADOS)


@pytest.mark.dados_locais
@pytest.mark.skipif(
    not DADOS_BRUTOS_DISPONIVEIS,
    reason="CSVs da PRF não estão versionados; consulte docs/02_fonte_dos_dados.md.",
)
def test_existem_arquivos_brutos():
    ocorrencias = localizar_arquivos("ocorrencia")
    pessoas = localizar_arquivos("pessoa")
    assert OCORRENCIA_BRUTOS_DIR.exists()
    assert PESSOA_BRUTOS_DIR.exists()
    assert ocorrencias, "Nenhum CSV de ocorrência encontrado em dados/01_brutos/ocorrencia."
    assert pessoas, "Nenhum CSV de pessoa encontrado em dados/01_brutos/pessoa."


@pytest.mark.dados_locais
@pytest.mark.skipif(
    not DADOS_BRUTOS_DISPONIVEIS,
    reason="CSVs da PRF não estão versionados; consulte docs/02_fonte_dos_dados.md.",
)
def test_carrega_ocorrencias_2024():
    df = carregar_dados("ocorrencia", anos=(2024,))
    assert not df.empty
    assert {"id", "data_inversa", "uf", "municipio", "causa_acidente"}.issubset(df.columns)


def test_resolve_anos_analise_a_partir_dos_brutos(monkeypatch):
    arquivos = [
        Path("acidentes_2022_ocorrencia.csv"),
        Path("acidentes_2024_ocorrencia.csv"),
        Path("acidentes_2026_ocorrencia.csv"),
        Path("acidentes_2027_ocorrencia.csv"),
    ]
    monkeypatch.setattr("src.carregar_dados.localizar_arquivos", lambda tipo="ocorrencia": arquivos)

    assert anos_disponiveis("ocorrencia") == (2022, 2024, 2026, 2027)
    assert resolver_anos_analise() == (2024, 2026, 2027)


@pytest.mark.dados_locais
@pytest.mark.skipif(
    not TRATADOS_DISPONIVEIS,
    reason="Arquivos tratados ausentes; execute python -m src.limpar_dados.",
)
def test_arquivos_tratados_existem_ou_orientam_execucao():
    assert all(path.is_file() for path in ARQUIVOS_TRATADOS)
