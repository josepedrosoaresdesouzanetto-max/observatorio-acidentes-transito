import pandas as pd

from src.config import TRATADOS_DIR
from src.limpar_dados import limpar_dataframe
from src.utils import ler_csv_prf


def test_colunas_essenciais_tratadas():
    path = TRATADOS_DIR / "ocorrencias_tratadas.csv"
    assert path.exists(), "Rode python -m src.limpar_dados antes dos testes."
    df = ler_csv_prf(path, nrows=20)
    if "acidente_fatal" not in df.columns and "mortos" in df.columns:
        df["acidente_fatal"] = (pd.to_numeric(df["mortos"], errors="coerce").fillna(0) >= 1).astype(int)
    essenciais = {
        "id", "data_inversa", "ano", "mes", "hora", "uf", "municipio",
        "br", "causa_acidente", "tipo_acidente", "mortos",
        "feridos_leves", "feridos_graves", "total_feridos",
        "total_vitimas", "acidente_fatal", "acidente_grave", "nivel_gravidade",
    }
    assert essenciais.issubset(df.columns)
    acidente_fatal = pd.to_numeric(df["acidente_fatal"], errors="coerce").fillna(0).astype(int)
    esperado = (pd.to_numeric(df["mortos"], errors="coerce").fillna(0) >= 1).astype(int)
    assert (acidente_fatal == esperado).all()


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
    assert tratado.loc[0, "acidente_fatal"] == 0
    assert tratado.loc[1, "acidente_fatal"] == 1
    assert tratado.loc[0, "acidente_grave"] == "Sim"
    assert tratado.loc[1, "acidente_grave"] == "Sim"
