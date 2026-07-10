import pandas as pd
import pytest

from src.analisar_fatores_associados import analisar_fator


@pytest.fixture
def ocorrencias():
    return pd.DataFrame(
        {
            "fator": ["A", "A", "B", "B", "C", None, "   "],
            "acidente_fatal": [1, 0, 0, 0, 1, 1, 0],
            "mortos": [2, 0, 0, 0, 1, 3, 0],
            "feridos_graves": [1, 2, 3, 4, 5, 6, 7],
        }
    )


def test_calcula_agregacoes_e_percentuais(ocorrencias):
    resultado = analisar_fator(ocorrencias, "fator", minimo_ocorrencias=0)
    a = resultado.set_index("categoria").loc["A"]
    b = resultado.set_index("categoria").loc["B"]
    assert a["total_acidentes"] == 2
    assert a["acidentes_fatais"] == 1
    assert a["acidentes_nao_fatais"] == 1
    assert a["percentual_fatalidade"] == 50
    assert a["mortos"] == 2
    assert b["percentual_fatalidade"] == 0


def test_grupo_com_cem_por_cento_e_categoria_ausente(ocorrencias):
    resultado = analisar_fator(ocorrencias, "fator", minimo_ocorrencias=0).set_index("categoria")
    assert resultado.loc["C", "percentual_fatalidade"] == 100
    assert resultado.loc["Não informado", "total_acidentes"] == 2
    assert resultado.loc["Não informado", "acidentes_fatais"] == 1


def test_aplica_minimo_apos_agregacao_e_ordena(ocorrencias):
    resultado = analisar_fator(ocorrencias, "fator", minimo_ocorrencias=2)
    assert resultado["categoria"].tolist() == ["A", "Não informado", "B"]
    assert "C" not in resultado["categoria"].tolist()


def test_nao_altera_dataframe_original(ocorrencias):
    original = ocorrencias.copy(deep=True)
    analisar_fator(ocorrencias, "fator", minimo_ocorrencias=0)
    pd.testing.assert_frame_equal(ocorrencias, original)


def test_coluna_ausente_gera_erro_claro(ocorrencias):
    with pytest.raises(ValueError, match="Coluna analisada não encontrada"):
        analisar_fator(ocorrencias, "inexistente")


def test_sem_divisao_por_zero_em_dataframe_vazio():
    vazio = pd.DataFrame(columns=["fator", "acidente_fatal", "mortos", "feridos_graves"])
    resultado = analisar_fator(vazio, "fator")
    assert resultado.empty
