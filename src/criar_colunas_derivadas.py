from __future__ import annotations

import pandas as pd


def classificar_faixa_horario(hora: int | float | None) -> str:
    if pd.isna(hora):
        return "Ignorado"
    hora_int = int(hora)
    if 0 <= hora_int <= 5:
        return "Madrugada"
    if 6 <= hora_int <= 11:
        return "Manha"
    if 12 <= hora_int <= 17:
        return "Tarde"
    return "Noite"


def classificar_gravidade(row: pd.Series) -> str:
    if row.get("mortos", 0) > 0:
        return "Fatal"
    if row.get("feridos_graves", 0) > 0:
        return "Grave"
    if row.get("feridos_leves", 0) > 0:
        return "Leve"
    return "Sem vitimas"


def criar_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["data_inversa"] = pd.to_datetime(df.get("data_inversa"), errors="coerce")
    if "ano" not in df.columns:
        df["ano"] = df["data_inversa"].dt.year
    else:
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").fillna(df["data_inversa"].dt.year).astype("Int64")
    df["mes"] = df["data_inversa"].dt.month.astype("Int64")

    horario = df.get("horario", pd.Series(index=df.index, dtype="object")).astype(str)
    df["hora"] = pd.to_numeric(horario.str.extract(r"^(\d{1,2})", expand=False), errors="coerce").astype("Int64")
    df["faixa_horario"] = df["hora"].map(classificar_faixa_horario)

    dia = df.get("dia_semana", pd.Series(index=df.index, dtype="object")).astype(str).str.lower()
    fim_de_semana = dia.str.contains("sab|sábado|domingo|dom", regex=True, na=False)
    df["final_de_semana"] = fim_de_semana.map({True: "Sim", False: "Nao"})

    for coluna in ("mortos", "feridos_leves", "feridos_graves", "ilesos", "veiculos", "pessoas"):
        if coluna not in df.columns:
            df[coluna] = 0
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0).astype(int)

    df["total_feridos"] = df["feridos_leves"] + df["feridos_graves"]
    df["total_vitimas"] = df["mortos"] + df["feridos_leves"] + df["feridos_graves"]
    df["teve_morte"] = (df["mortos"] > 0).map({True: "Sim", False: "Nao"})
    df["acidente_grave"] = ((df["mortos"] > 0) | (df["feridos_graves"] > 0)).map({True: "Sim", False: "Nao"})
    df["nivel_gravidade"] = df.apply(classificar_gravidade, axis=1)
    return df
