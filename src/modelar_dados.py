from __future__ import annotations

import pandas as pd

from src.calcular_indice_risco import calcular_indice_risco
from src.config import MODELADOS_DIR, TRATADOS_DIR
from src.utils import ler_csv_prf, salvar_csv


def chave_dim(df: pd.DataFrame, colunas: list[str], nome: str) -> pd.DataFrame:
    dim = df[colunas].drop_duplicates().reset_index(drop=True)
    dim.insert(0, nome, range(1, len(dim) + 1))
    return dim


def gerar_modelados() -> dict[str, pd.DataFrame]:
    ocorrencias = ler_csv_prf(TRATADOS_DIR / "ocorrencias_tratadas.csv")
    ocorrencias["data_inversa"] = pd.to_datetime(ocorrencias["data_inversa"], errors="coerce")

    dim_tempo = ocorrencias[["data_inversa", "ano", "mes", "dia_semana", "hora", "faixa_horario", "final_de_semana"]].drop_duplicates()
    dim_local = chave_dim(ocorrencias, ["uf", "municipio"], "id_local")
    dim_rodovia = chave_dim(ocorrencias, ["br", "km", "tipo_pista", "tracado_via"], "id_rodovia")
    dim_causa = chave_dim(ocorrencias, ["causa_acidente", "tipo_acidente", "classificacao_acidente"], "id_causa")
    dim_clima = chave_dim(ocorrencias, ["condicao_metereologica", "fase_dia"], "id_clima")

    fato_acidentes = ocorrencias[
        [
            "id", "data_inversa", "ano", "uf", "municipio", "br", "km", "causa_acidente",
            "tipo_acidente", "classificacao_acidente", "fase_dia", "condicao_metereologica",
            "mortos", "feridos_leves", "feridos_graves", "ilesos", "veiculos", "total_feridos",
            "total_vitimas", "teve_morte", "acidente_grave", "nivel_gravidade", "faixa_horario",
        ]
    ].copy()

    outputs = {
        "dim_tempo": dim_tempo,
        "dim_local": dim_local,
        "dim_rodovia": dim_rodovia,
        "dim_causa": dim_causa,
        "dim_clima": dim_clima,
        "fato_acidentes": fato_acidentes,
    }
    pessoas_path = TRATADOS_DIR / "pessoas_tratadas.csv"
    if pessoas_path.exists():
        outputs["fato_vitimas"] = ler_csv_prf(pessoas_path)
    for dimensao in ("uf", "br", "municipio", "causa_acidente", "faixa_horario"):
        outputs[f"indice_risco_{dimensao}"] = calcular_indice_risco(ocorrencias, dimensao)
    for nome, df in outputs.items():
        salvar_csv(df, MODELADOS_DIR / f"{nome}.csv")
    return outputs


if __name__ == "__main__":
    for nome, df in gerar_modelados().items():
        print(nome, df.shape)
