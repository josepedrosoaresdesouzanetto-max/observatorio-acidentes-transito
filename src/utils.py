from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Iterable

import pandas as pd


def normalizar_nome_coluna(coluna: str) -> str:
    texto = unicodedata.normalize("NFKD", str(coluna)).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^0-9a-zA-Z]+", "_", texto.strip().lower())
    return re.sub(r"_+", "_", texto).strip("_")


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalizar_nome_coluna(coluna) for coluna in df.columns]
    aliases = {
        "condicao_meteorologica": "condicao_metereologica",
        "condicoes_metereologicas": "condicao_metereologica",
        "feridos": "total_feridos_origem",
    }
    return df.rename(columns={origem: destino for origem, destino in aliases.items() if origem in df.columns})


def ler_csv_prf(path: Path, nrows: int | None = None) -> pd.DataFrame:
    erros: list[str] = []
    for encoding in ("utf-8-sig", "latin1", "cp1252"):
        try:
            return pd.read_csv(path, sep=";", encoding=encoding, dtype=str, low_memory=False, nrows=nrows)
        except UnicodeDecodeError as exc:
            erros.append(f"{encoding}: {exc}")
    raise UnicodeDecodeError("csv", b"", 0, 1, f"Nenhum encoding funcionou para {path}: {erros}")


def salvar_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")


def primeira_coluna_existente(df: pd.DataFrame, candidatas: Iterable[str]) -> str | None:
    for coluna in candidatas:
        if coluna in df.columns:
            return coluna
    return None
