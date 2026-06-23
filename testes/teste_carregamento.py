from pathlib import Path

import pytest

from src.carregar_dados import carregar_dados, localizar_arquivos
from src.config import OCORRENCIA_BRUTOS_DIR, PESSOA_BRUTOS_DIR, TRATADOS_DIR


def test_existem_arquivos_brutos():
    ocorrencias = localizar_arquivos("ocorrencia")
    pessoas = localizar_arquivos("pessoa")
    assert OCORRENCIA_BRUTOS_DIR.exists()
    assert PESSOA_BRUTOS_DIR.exists()
    assert ocorrencias, "Nenhum CSV de ocorrência encontrado em dados/01_brutos/ocorrencia."
    assert pessoas, "Nenhum CSV de pessoa encontrado em dados/01_brutos/pessoa."


def test_carrega_ocorrencias_2024():
    df = carregar_dados("ocorrencia", anos=(2024,))
    assert not df.empty
    assert {"id", "data_inversa", "uf", "municipio", "causa_acidente"}.issubset(df.columns)


def test_arquivos_tratados_existem_ou_orientam_execucao():
    esperados = [TRATADOS_DIR / "ocorrencias_tratadas.csv", TRATADOS_DIR / "pessoas_tratadas.csv"]
    faltantes = [str(path) for path in esperados if not path.exists()]
    if faltantes:
        pytest.fail("Arquivos tratados ausentes. Rode: python -m src.limpar_dados. Faltantes: " + ", ".join(faltantes))
