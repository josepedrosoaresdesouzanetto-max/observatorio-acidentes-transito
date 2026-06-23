import pandas as pd

from src.config import TRATADOS_DIR
from src.limpar_dados import limpar_dataframe
from src.utils import ler_csv_prf


def test_colunas_essenciais_tratadas():
    path = TRATADOS_DIR / "ocorrencias_tratadas.csv"
    assert path.exists(), "Rode python -m src.limpar_dados antes dos testes."
    df = ler_csv_prf(path, nrows=20)
    essenciais = {
        "id", "data_inversa", "ano", "mes", "hora", "uf", "municipio",
        "br", "causa_acidente", "tipo_acidente", "mortos",
        "feridos_leves", "feridos_graves", "total_feridos",
        "total_vitimas", "acidente_grave", "nivel_gravidade",
    }
    assert essenciais.issubset(df.columns)


def test_total_feridos_e_acidente_grave():
    df = pd.DataFrame({
        "id": [1, 2],
        "data_inversa": ["2024-01-06", "2024-01-07"],
        "dia_semana": ["sábado", "domingo"],
        "horario": ["13:45:00", "01:10:00"],
        "mortos": [0, 1],
        "feridos_leves": [2, 0],
        "feridos_graves": [1, 0],
    })
    tratado = limpar_dataframe(df)
    assert tratado.loc[0, "total_feridos"] == 3
    assert tratado.loc[0, "acidente_grave"] == "Sim"
    assert tratado.loc[1, "acidente_grave"] == "Sim"
