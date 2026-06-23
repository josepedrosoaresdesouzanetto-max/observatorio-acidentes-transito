from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.config import OCORRENCIA_BRUTOS_DIR, PESSOA_BRUTOS_DIR
from src.utils import ler_csv_prf, normalizar_colunas


def localizar_arquivos(tipo: str = "ocorrencia") -> list[Path]:
    pasta = OCORRENCIA_BRUTOS_DIR if tipo == "ocorrencia" else PESSOA_BRUTOS_DIR
    return sorted(pasta.glob("acidentes_*_*.csv"))


def extrair_ano(path: Path) -> int | None:
    match = re.search(r"(20\d{2})", path.name)
    return int(match.group(1)) if match else None


def carregar_arquivo(path: Path) -> pd.DataFrame:
    df = normalizar_colunas(ler_csv_prf(path))
    ano = extrair_ano(path)
    if ano is not None and "ano" not in df.columns:
        df["ano"] = ano
    df["arquivo_origem"] = path.name
    return df


def carregar_dados(tipo: str = "ocorrencia", anos: tuple[int, ...] | None = None) -> pd.DataFrame:
    partes = []
    for path in localizar_arquivos(tipo):
        ano = extrair_ano(path)
        if anos and ano not in anos:
            continue
        partes.append(carregar_arquivo(path))
    if not partes:
        raise FileNotFoundError(f"Nenhum arquivo bruto encontrado para tipo={tipo!r}.")
    return pd.concat(partes, ignore_index=True)


if __name__ == "__main__":
    for tipo in ("ocorrencia", "pessoa"):
        df = carregar_dados(tipo)
        print(tipo, df.shape)
