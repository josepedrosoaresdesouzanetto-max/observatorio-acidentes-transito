from __future__ import annotations

import pandas as pd

from src.config import MODELADOS_DIR, TRATADOS_DIR
from src.utils import ler_csv_prf, salvar_csv


PESO_MORTE = 5
PESO_FERIDO_GRAVE = 3
PESO_FERIDO_LEVE = 1


def classificar_indice(valor: float, cortes: tuple[float, float, float]) -> str:
    baixo, medio, alto = cortes
    if valor <= baixo:
        return "Baixo"
    if valor <= medio:
        return "Médio"
    if valor <= alto:
        return "Alto"
    return "Crítico"


def calcular_indice_risco(df: pd.DataFrame, dimensao: str) -> pd.DataFrame:
    if dimensao not in df.columns:
        raise KeyError(f"Coluna {dimensao!r} ausente para cálculo do índice.")

    dados = df.copy()
    for coluna in ("mortos", "feridos_graves", "feridos_leves"):
        dados[coluna] = pd.to_numeric(dados.get(coluna, 0), errors="coerce").fillna(0)

    agrupado = (
        dados.groupby(dimensao, dropna=False)
        .agg(
            total_acidentes=("id", "count"),
            mortos=("mortos", "sum"),
            feridos_graves=("feridos_graves", "sum"),
            feridos_leves=("feridos_leves", "sum"),
        )
        .reset_index()
    )
    agrupado["indice_risco"] = (
        agrupado["total_acidentes"]
        + agrupado["mortos"] * PESO_MORTE
        + agrupado["feridos_graves"] * PESO_FERIDO_GRAVE
        + agrupado["feridos_leves"] * PESO_FERIDO_LEVE
    )
    cortes = tuple(agrupado["indice_risco"].quantile([0.25, 0.50, 0.75]).fillna(0).tolist())
    agrupado["classe_risco"] = agrupado["indice_risco"].map(lambda valor: classificar_indice(valor, cortes))
    return agrupado.sort_values("indice_risco", ascending=False)


def gerar_indices() -> dict[str, pd.DataFrame]:
    path = TRATADOS_DIR / "ocorrencias_tratadas.csv"
    if not path.exists():
        raise FileNotFoundError("Arquivo de ocorrências tratadas não encontrado. Rode: python -m src.limpar_dados")

    ocorrencias = ler_csv_prf(path)
    outputs: dict[str, pd.DataFrame] = {}
    for dimensao in ("uf", "br", "municipio", "causa_acidente", "faixa_horario"):
        resultado = calcular_indice_risco(ocorrencias, dimensao)
        outputs[dimensao] = resultado
        salvar_csv(resultado, MODELADOS_DIR / f"indice_risco_{dimensao}.csv")
    return outputs


if __name__ == "__main__":
    for nome, df in gerar_indices().items():
        print(nome, df.shape)
