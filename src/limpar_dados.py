from __future__ import annotations

import pandas as pd

from src.carregar_dados import carregar_dados, resolver_anos_analise
from src.config import TRATADOS_DIR
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


def gerar_tratados(anos: tuple[int, ...] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    anos_resolvidos = anos or resolver_anos_analise()
    print(f"Anos processados: {anos_resolvidos}")
    ocorrencias = limpar_dataframe(carregar_dados("ocorrencia", anos=anos_resolvidos))
    pessoas = limpar_dataframe(carregar_dados("pessoa", anos=anos_resolvidos))
    salvar_csv(ocorrencias, TRATADOS_DIR / "ocorrencias_tratadas.csv")
    salvar_csv(pessoas, TRATADOS_DIR / "pessoas_tratadas.csv")
    return ocorrencias, pessoas


if __name__ == "__main__":
    ocorrencias, pessoas = gerar_tratados()
    print("ocorrencias", ocorrencias.shape)
    print("pessoas", pessoas.shape)
