from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.config import GRAFICOS_DIR, MODELADOS_DIR, TRATADOS_DIR
from src.utils import ler_csv_prf


plt.style.use("seaborn-v0_8-whitegrid")


def salvar_barra(serie: pd.Series, titulo: str, arquivo: str, xlabel: str = "", ylabel: str = "Total") -> None:
    serie = serie.dropna()
    fig, ax = plt.subplots(figsize=(11, 6))
    serie.plot(kind="bar", ax=ax, color="#2f6f73")
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(GRAFICOS_DIR / arquivo, dpi=150)
    plt.close(fig)


def gerar_graficos() -> list[str]:
    df = ler_csv_prf(TRATADOS_DIR / "ocorrencias_tratadas.csv")
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    for coluna in ("mortos", "feridos_graves", "feridos_leves"):
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0)

    graficos = []
    specs = [
        (df.groupby("ano").size().sort_index(), "Acidentes por ano", "acidentes_por_ano.png", "Ano"),
        (df["uf"].value_counts().head(15), "Acidentes por UF - Top 15", "acidentes_por_uf.png", "UF"),
        (df["faixa_horario"].value_counts(), "Acidentes por faixa de horario", "acidentes_por_horario.png", "Faixa"),
        (df["dia_semana"].value_counts(), "Acidentes por dia da semana", "acidentes_por_dia_semana.png", "Dia"),
        (df["causa_acidente"].value_counts().head(12), "Causas mais comuns", "causas_mais_comuns.png", "Causa"),
        (df["tipo_acidente"].value_counts().head(12), "Tipos de acidente", "tipos_acidente.png", "Tipo"),
        (df["condicao_metereologica"].value_counts().head(12), "Acidentes por condicao meteorologica", "acidentes_por_clima.png", "Condicao"),
        (df[df["acidente_grave"] == "Sim"].groupby("uf").size().sort_values(ascending=False).head(15), "Acidentes graves por UF", "acidentes_graves_por_uf.png", "UF"),
        (df.groupby("br").size().sort_values(ascending=False).head(15), "Ranking de rodovias por acidentes", "ranking_rodovias.png", "BR"),
    ]
    for serie, titulo, arquivo, xlabel in specs:
        salvar_barra(serie, titulo, arquivo, xlabel)
        graficos.append(arquivo)

    risco = ler_csv_prf(MODELADOS_DIR / "indice_risco_uf.csv")
    risco["indice_risco"] = pd.to_numeric(risco["indice_risco"], errors="coerce").fillna(0)
    salvar_barra(risco.set_index("uf")["indice_risco"].head(15), "Indice de risco por UF - Top 15", "indice_risco.png", "UF", "Indice")
    graficos.append("indice_risco.png")
    return graficos


if __name__ == "__main__":
    print("\n".join(gerar_graficos()))
