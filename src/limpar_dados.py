from __future__ import annotations

import pandas as pd

from src.carregar_dados import carregar_dados
from src.config import ANOS_ANALISE, TRATADOS_DIR
from src.criar_colunas_derivadas import criar_derivadas
from src.utils import salvar_csv


CATEGORICAS = [
    "uf", "municipio", "causa_acidente", "tipo_acidente", "classificacao_acidente",
    "fase_dia", "condicao_metereologica", "tipo_pista", "tracado_via", "tipo_envolvido",
    "estado_fisico", "sexo",
]


def limpar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    for coluna in CATEGORICAS:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("Nao informado").astype(str).str.strip()
            df[coluna] = df[coluna].replace({"": "Nao informado", "nan": "Nao informado"})
    if "km" in df.columns:
        df["km"] = df["km"].astype(str).str.replace(",", ".", regex=False)
        df["km"] = pd.to_numeric(df["km"], errors="coerce")
    if "br" in df.columns:
        df["br"] = pd.to_numeric(df["br"], errors="coerce").astype("Int64")
    return criar_derivadas(df)


def gerar_tratados(anos: tuple[int, ...] = ANOS_ANALISE) -> tuple[pd.DataFrame, pd.DataFrame]:
    ocorrencias = limpar_dataframe(carregar_dados("ocorrencia", anos=anos))
    pessoas = limpar_dataframe(carregar_dados("pessoa", anos=anos))
    salvar_csv(ocorrencias, TRATADOS_DIR / "ocorrencias_tratadas.csv")
    salvar_csv(pessoas, TRATADOS_DIR / "pessoas_tratadas.csv")
    return ocorrencias, pessoas


if __name__ == "__main__":
    ocorrencias, pessoas = gerar_tratados()
    print("ocorrencias", ocorrencias.shape)
    print("pessoas", pessoas.shape)
