"""Leitura validada e comparação imutável de arquivos CSV da PRF."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.utils import normalizar_nome_coluna


ENCODINGS_SUPORTADOS = ("utf-8", "utf-8-sig", "latin-1", "cp1252")
SEPARADORES_SUPORTADOS = (";", ",")
VALOR_NULO = "<NULO>"
COLUNAS_SENSIVEIS = {"cpf", "cnpj", "nome", "email", "telefone", "celular", "endereco", "placa", "renavam", "chassi"}
CHAVES_ESTAVEIS = (
    ("id", "pesid"),
    ("id", "id_veiculo", "tipo_envolvido", "idade", "sexo"),
    ("data_inversa", "horario", "uf", "br", "km", "municipio", "latitude", "longitude"),
)


class ErroValidacaoCSV(ValueError):
    """Erro esperado ao validar um arquivo remoto ou local."""


@dataclass(frozen=True)
class DiagnosticoCSV:
    path: Path
    encoding: str
    separador: str
    linhas: int
    colunas: tuple[str, ...]
    sha256: str
    tamanho_bytes: int


@dataclass
class ResultadoComparacao:
    chave_utilizada: tuple[str, ...] | None
    estrategia_chave: str
    novos: pd.DataFrame = field(default_factory=pd.DataFrame)
    alterados: pd.DataFrame = field(default_factory=pd.DataFrame)
    removidos: pd.DataFrame = field(default_factory=pd.DataFrame)
    inalterados: int = 0
    duplicados_remoto: int = 0
    duplicados_local: int = 0
    sem_chave_remoto: int = 0
    sem_chave_local: int = 0
    mensagem: str = ""

    @property
    def comparacao_segura(self) -> bool:
        return self.chave_utilizada is not None


def sha256_arquivo(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        while bloco := arquivo.read(chunk_size):
            digest.update(bloco)
    return digest.hexdigest()


def _parece_html(conteudo: bytes) -> bool:
    inicio = conteudo[:2048].lstrip().lower()
    return inicio.startswith((b"<!doctype html", b"<html", b"<head", b"<body"))


def detectar_formato_csv(path: Path) -> tuple[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        raise ErroValidacaoCSV("Arquivo vazio ou inexistente.")
    amostra_bytes = path.read_bytes()[:128 * 1024]
    if _parece_html(amostra_bytes):
        raise ErroValidacaoCSV("O conteúdo recebido é HTML, não CSV.")

    erros: list[str] = []
    for encoding in ENCODINGS_SUPORTADOS:
        try:
            texto = amostra_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            erros.append(f"{encoding}: {exc}")
            continue
        primeira_linha = next((linha for linha in texto.splitlines() if linha.strip()), "")
        if not primeira_linha:
            continue
        contagens = {separador: primeira_linha.count(separador) for separador in SEPARADORES_SUPORTADOS}
        separador = max(contagens, key=contagens.get)
        if contagens[separador] > 0:
            return encoding, separador
    raise ErroValidacaoCSV("Não foi possível detectar encoding e separador do CSV. " + " | ".join(erros))


def carregar_csv_validado(path: Path) -> tuple[pd.DataFrame, DiagnosticoCSV]:
    encoding, separador = detectar_formato_csv(path)
    try:
        dataframe = pd.read_csv(path, sep=separador, encoding=encoding, dtype=str, low_memory=False)
    except Exception as exc:
        raise ErroValidacaoCSV(f"Falha ao interpretar CSV: {exc}") from exc
    if dataframe.empty:
        raise ErroValidacaoCSV("CSV sem registros de dados.")
    if len(dataframe.columns) < 2:
        raise ErroValidacaoCSV("Schema inesperado: o CSV possui menos de duas colunas.")
    colunas = tuple(normalizar_nome_coluna(coluna) for coluna in dataframe.columns)
    if len(set(colunas)) != len(colunas):
        raise ErroValidacaoCSV("Schema inesperado: colunas duplicadas após normalização.")
    diagnostico = DiagnosticoCSV(
        path=path,
        encoding=encoding,
        separador=separador,
        linhas=len(dataframe),
        colunas=colunas,
        sha256=sha256_arquivo(path),
        tamanho_bytes=path.stat().st_size,
    )
    return dataframe, diagnostico


def normalizar_para_comparacao(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalizado = dataframe.copy(deep=True)
    normalizado.columns = [normalizar_nome_coluna(coluna) for coluna in normalizado.columns]
    for coluna in normalizado.columns:
        serie = normalizado[coluna].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        normalizado[coluna] = serie.fillna(VALOR_NULO).replace("", VALOR_NULO)
    return normalizado


def _chave_valida(df: pd.DataFrame, colunas: tuple[str, ...]) -> bool:
    if not set(colunas).issubset(df.columns):
        return False
    chave = df[list(colunas)]
    if chave.eq(VALOR_NULO).any(axis=1).any():
        return False
    return not chave.duplicated().any()


def escolher_chave(local: pd.DataFrame, remoto: pd.DataFrame) -> tuple[tuple[str, ...] | None, str]:
    if "id" in local.columns and "id" in remoto.columns and _chave_valida(local, ("id",)) and _chave_valida(remoto, ("id",)):
        return ("id",), "id"
    for candidata in CHAVES_ESTAVEIS:
        if _chave_valida(local, candidata) and _chave_valida(remoto, candidata):
            return candidata, "campos_estaveis"

    colunas_comuns = sorted(set(local.columns) & set(remoto.columns))
    if not colunas_comuns:
        return None, "sem_chave"
    hash_local = local[colunas_comuns].agg("|".join, axis=1).map(lambda valor: hashlib.sha256(valor.encode("utf-8")).hexdigest())
    hash_remoto = remoto[colunas_comuns].agg("|".join, axis=1).map(lambda valor: hashlib.sha256(valor.encode("utf-8")).hexdigest())
    if not hash_local.duplicated().any() and not hash_remoto.duplicated().any():
        local["__hash_linha"] = hash_local
        remoto["__hash_linha"] = hash_remoto
        return ("__hash_linha",), "hash_linha"
    return None, "sem_chave"


def _duplicados_e_nulos(df: pd.DataFrame, colunas: Iterable[str]) -> tuple[int, int]:
    nomes = list(colunas)
    chave = df[nomes]
    sem_chave = int(chave.eq(VALOR_NULO).any(axis=1).sum())
    duplicados = int(chave.duplicated(keep=False).sum())
    return duplicados, sem_chave


def _valor_publicavel(coluna: str, valor: str) -> str:
    return "<REDACTED>" if coluna in COLUNAS_SENSIVEIS else valor


def comparar_dataframes(local_original: pd.DataFrame, remoto_original: pd.DataFrame) -> ResultadoComparacao:
    local = normalizar_para_comparacao(local_original)
    remoto = normalizar_para_comparacao(remoto_original)
    duplicados_id_local, sem_id_local = _duplicados_e_nulos(local, ("id",)) if "id" in local.columns else (0, 0)
    duplicados_id_remoto, sem_id_remoto = _duplicados_e_nulos(remoto, ("id",)) if "id" in remoto.columns else (0, 0)
    chave, estrategia = escolher_chave(local, remoto)
    if chave is None:
        return ResultadoComparacao(
            chave_utilizada=None,
            estrategia_chave=estrategia,
            duplicados_local=duplicados_id_local,
            duplicados_remoto=duplicados_id_remoto,
            sem_chave_local=sem_id_local,
            sem_chave_remoto=sem_id_remoto,
            mensagem="Não foi possível identificar registros de forma segura.",
        )

    duplicados_chave_local, sem_chave_local = _duplicados_e_nulos(local, chave)
    duplicados_chave_remoto, sem_chave_remoto = _duplicados_e_nulos(remoto, chave)
    duplicados_local = duplicados_id_local if estrategia != "id" and "id" in local.columns else duplicados_chave_local
    duplicados_remoto = duplicados_id_remoto if estrategia != "id" and "id" in remoto.columns else duplicados_chave_remoto
    sem_chave_local = sem_id_local if estrategia != "id" and "id" in local.columns else sem_chave_local
    sem_chave_remoto = sem_id_remoto if estrategia != "id" and "id" in remoto.columns else sem_chave_remoto
    local_valido = local[~local[list(chave)].eq(VALOR_NULO).any(axis=1) & ~local[list(chave)].duplicated(keep=False)].copy()
    remoto_valido = remoto[~remoto[list(chave)].eq(VALOR_NULO).any(axis=1) & ~remoto[list(chave)].duplicated(keep=False)].copy()
    local_idx = local_valido.set_index(list(chave), drop=False)
    remoto_idx = remoto_valido.set_index(list(chave), drop=False)
    chaves_local = set(local_idx.index.tolist())
    chaves_remoto = set(remoto_idx.index.tolist())
    somente_remoto = chaves_remoto - chaves_local
    somente_local = chaves_local - chaves_remoto
    comuns = chaves_local & chaves_remoto

    novos = remoto_idx.loc[list(somente_remoto)].reset_index(drop=True) if somente_remoto else remoto.iloc[0:0].copy()
    removidos = local_idx.loc[list(somente_local)].reset_index(drop=True) if somente_local else local.iloc[0:0].copy()
    colunas_comparadas = sorted((set(local.columns) & set(remoto.columns)) - set(chave) - {"__hash_linha"})
    alteracoes: list[dict[str, str]] = []
    inalterados = 0
    for valor_chave in comuns:
        linha_local = local_idx.loc[valor_chave]
        linha_remota = remoto_idx.loc[valor_chave]
        colunas_alteradas = [coluna for coluna in colunas_comparadas if linha_local[coluna] != linha_remota[coluna]]
        if not colunas_alteradas:
            inalterados += 1
            continue
        chave_texto = valor_chave if isinstance(valor_chave, tuple) else (valor_chave,)
        for coluna in colunas_alteradas:
            alteracoes.append(
                {
                    "chave": json.dumps(dict(zip(chave, chave_texto)), ensure_ascii=False),
                    "coluna": coluna,
                    "valor_local": _valor_publicavel(coluna, linha_local[coluna]),
                    "valor_remoto": _valor_publicavel(coluna, linha_remota[coluna]),
                }
            )

    return ResultadoComparacao(
        chave_utilizada=chave,
        estrategia_chave=estrategia,
        novos=novos.reset_index(drop=True),
        alterados=pd.DataFrame(alteracoes, columns=["chave", "coluna", "valor_local", "valor_remoto"]),
        removidos=removidos.reset_index(drop=True),
        inalterados=inalterados,
        duplicados_remoto=duplicados_remoto,
        duplicados_local=duplicados_local,
        sem_chave_remoto=sem_chave_remoto,
        sem_chave_local=sem_chave_local,
        mensagem="Comparação concluída.",
    )


def comparar_arquivos(local_path: Path, remoto_path: Path) -> tuple[ResultadoComparacao, DiagnosticoCSV, DiagnosticoCSV]:
    local, diagnostico_local = carregar_csv_validado(local_path)
    remoto, diagnostico_remoto = carregar_csv_validado(remoto_path)
    resultado = comparar_dataframes(local, remoto)
    return resultado, diagnostico_local, diagnostico_remoto
