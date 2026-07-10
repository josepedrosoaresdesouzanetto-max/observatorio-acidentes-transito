"""Agrega fatores descritivos associados à fatalidade dos acidentes."""

from __future__ import annotations

import pandas as pd


COLUNAS_OBRIGATORIAS = {"acidente_fatal", "mortos", "feridos_graves"}


def analisar_fator(
    dataframe: pd.DataFrame,
    coluna: str,
    minimo_ocorrencias: int = 50,
) -> pd.DataFrame:
    """Compara a fatalidade entre categorias de uma coluna.

    A saída é descritiva: percentuais maiores indicam associação no recorte,
    não uma relação causal. O dataframe recebido não é alterado.
    """
    if coluna not in dataframe.columns:
        raise ValueError(f"Coluna analisada não encontrada: '{coluna}'.")

    faltantes = COLUNAS_OBRIGATORIAS.difference(dataframe.columns)
    if faltantes:
        nomes = ", ".join(sorted(faltantes))
        raise ValueError(f"Colunas obrigatórias ausentes para a análise: {nomes}.")
    if minimo_ocorrencias < 0:
        raise ValueError("minimo_ocorrencias deve ser maior ou igual a zero.")

    categorias = dataframe[coluna].astype("string").str.strip()
    categorias = categorias.mask(categorias.isna() | categorias.eq(""), "Não informado")
    trabalho = pd.DataFrame(
        {
            "categoria": categorias,
            "acidente_fatal": pd.to_numeric(dataframe["acidente_fatal"], errors="coerce").fillna(0),
            "mortos": pd.to_numeric(dataframe["mortos"], errors="coerce").fillna(0),
            "feridos_graves": pd.to_numeric(dataframe["feridos_graves"], errors="coerce").fillna(0),
        }
    )
    trabalho["acidente_fatal"] = trabalho["acidente_fatal"].clip(lower=0, upper=1)

    resultado = (
        trabalho.groupby("categoria", dropna=False)
        .agg(
            total_acidentes=("acidente_fatal", "size"),
            acidentes_fatais=("acidente_fatal", "sum"),
            mortos=("mortos", "sum"),
            feridos_graves=("feridos_graves", "sum"),
        )
        .reset_index()
    )
    resultado["acidentes_fatais"] = resultado["acidentes_fatais"].astype(int)
    resultado["acidentes_nao_fatais"] = resultado["total_acidentes"] - resultado["acidentes_fatais"]
    resultado["percentual_fatalidade"] = (
        resultado["acidentes_fatais"].div(resultado["total_acidentes"]).mul(100).fillna(0)
    )
    resultado = resultado[resultado["total_acidentes"] >= minimo_ocorrencias]
    return resultado[
        [
            "categoria",
            "total_acidentes",
            "acidentes_fatais",
            "acidentes_nao_fatais",
            "percentual_fatalidade",
            "mortos",
            "feridos_graves",
        ]
    ].sort_values(["percentual_fatalidade", "total_acidentes", "categoria"], ascending=[False, False, True]).reset_index(drop=True)
