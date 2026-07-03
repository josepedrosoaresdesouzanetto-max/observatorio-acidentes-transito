from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.carregar_dados import extrair_ano, localizar_arquivos
from src.config import PROJECT_ROOT, RELATORIOS_DIR, TABELAS_DIR, TRATADOS_DIR
from src.utils import ler_csv_prf, normalizar_nome_coluna


COLUNAS_BRUTAS_OCORRENCIA = {
    "id",
    "data_inversa",
    "dia_semana",
    "horario",
    "uf",
    "br",
    "municipio",
    "causa_acidente",
    "tipo_acidente",
    "classificacao_acidente",
    "fase_dia",
    "condicao_metereologica",
    "mortos",
    "feridos_graves",
    "feridos_leves",
}

COLUNAS_BRUTAS_PESSOA = {
    "id",
    "uf",
    "tipo_envolvido",
    "estado_fisico",
    "idade",
    "sexo",
}

COLUNAS_QUALIDADE_OCORRENCIAS = [
    "id",
    "ano",
    "data_inversa",
    "uf",
    "br",
    "municipio",
    "causa_acidente",
    "tipo_acidente",
    "fase_dia",
    "condicao_metereologica",
    "mortos",
    "feridos_graves",
    "feridos_leves",
    "total_vitimas",
    "acidente_fatal",
]


@dataclass(frozen=True)
class ResultadoAuditoria:
    status: str
    item: str
    detalhe: str


def sha256_arquivo(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        while chunk := arquivo.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def csvs_auditoria() -> list[Path]:
    paths = localizar_arquivos("ocorrencia") + localizar_arquivos("pessoa")
    return sorted(paths, key=lambda path: str(path.relative_to(PROJECT_ROOT)))


def classificar_tipo(path: Path) -> str:
    partes = {parte.lower() for parte in path.parts}
    nome = path.name.lower()
    if "ocorrencia" in partes or "datatran" in nome or nome.endswith("_ocorrencia.csv"):
        return "ocorrencia"
    if "pessoa" in partes or nome.endswith("_pessoa.csv"):
        return "pessoa"
    return "desconhecido"


def gerar_manifesto_dados(path_saida: Path | None = None) -> pd.DataFrame:
    linhas = []
    for path in csvs_auditoria():
        stat = path.stat()
        linhas.append(
            {
                "arquivo": str(path.relative_to(PROJECT_ROOT)),
                "tipo": classificar_tipo(path),
                "ano": extrair_ano(path),
                "tamanho_bytes": stat.st_size,
                "modificado_em": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "sha256": sha256_arquivo(path),
            }
        )

    manifesto = pd.DataFrame(linhas)
    destino = path_saida or (TABELAS_DIR / "manifesto_dados_brutos.csv")
    destino.parent.mkdir(parents=True, exist_ok=True)
    manifesto.to_csv(destino, index=False, sep=";", encoding="utf-8-sig")
    return manifesto


def cabecalho_normalizado(path: Path) -> set[str]:
    df = ler_csv_prf(path, nrows=0)
    return {normalizar_nome_coluna(coluna) for coluna in df.columns}


def validar_layout_brutos() -> list[ResultadoAuditoria]:
    resultados: list[ResultadoAuditoria] = []
    for tipo, obrigatorias in (
        ("ocorrencia", COLUNAS_BRUTAS_OCORRENCIA),
        ("pessoa", COLUNAS_BRUTAS_PESSOA),
    ):
        paths = localizar_arquivos(tipo)
        if not paths:
            resultados.append(ResultadoAuditoria("ERRO", f"Layout bruto {tipo}", "Nenhum CSV bruto encontrado."))
            continue

        for path in paths:
            try:
                colunas = cabecalho_normalizado(path)
            except Exception as exc:  # pragma: no cover - operacional
                resultados.append(ResultadoAuditoria("AVISO", f"Layout bruto {tipo}", f"{path.name}: falha ao ler cabecalho: {exc}"))
                continue

            faltantes = sorted(obrigatorias - colunas)
            if faltantes:
                resultados.append(ResultadoAuditoria("ERRO", f"Layout bruto {tipo}", f"{path.name}: colunas ausentes {faltantes}."))
            else:
                resultados.append(ResultadoAuditoria("OK", f"Layout bruto {tipo}", f"{path.name}: colunas essenciais presentes."))
    return resultados


def carregar_ocorrencias_qualidade() -> pd.DataFrame:
    path = TRATADOS_DIR / "ocorrencias_tratadas.csv"
    if not path.exists():
        raise FileNotFoundError("Arquivo dados/02_tratados/ocorrencias_tratadas.csv ausente.")
    colunas_disponiveis = pd.read_csv(path, sep=";", encoding="utf-8-sig", nrows=0).columns
    colunas = [coluna for coluna in COLUNAS_QUALIDADE_OCORRENCIAS if coluna in colunas_disponiveis]
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", usecols=colunas, low_memory=False)


def gerar_relatorio_qualidade(path_saida: Path | None = None) -> pd.DataFrame:
    df = carregar_ocorrencias_qualidade()
    linhas: list[dict[str, object]] = []
    total_linhas = len(df)

    linhas.append({"metrica": "linhas_ocorrencias", "valor": total_linhas, "detalhe": "Total de linhas em ocorrencias_tratadas.csv"})
    if "id" in df.columns:
        duplicados = int(df["id"].duplicated().sum())
        linhas.append({"metrica": "ids_duplicados", "valor": duplicados, "detalhe": "IDs duplicados apos tratamento"})

    for coluna in ["ano", "uf", "br", "municipio", "causa_acidente", "tipo_acidente", "acidente_fatal"]:
        if coluna in df.columns:
            nulos = int(df[coluna].isna().sum())
            percentual = (nulos / total_linhas * 100) if total_linhas else 0
            linhas.append(
                {
                    "metrica": f"nulos_{coluna}",
                    "valor": nulos,
                    "detalhe": f"{percentual:.2f}% de nulos em {coluna}",
                }
            )

    for coluna in ["mortos", "feridos_graves", "feridos_leves", "total_vitimas"]:
        if coluna in df.columns:
            numerica = pd.to_numeric(df[coluna], errors="coerce")
            negativos = int((numerica < 0).sum())
            linhas.append({"metrica": f"negativos_{coluna}", "valor": negativos, "detalhe": f"Valores negativos em {coluna}"})

    for coluna in ["uf", "causa_acidente", "tipo_acidente", "condicao_metereologica"]:
        if coluna in df.columns:
            contagem = df[coluna].fillna("Nao informado").astype(str).value_counts()
            raras = int((contagem <= 5).sum())
            linhas.append({"metrica": f"categorias_raras_{coluna}", "valor": raras, "detalhe": "Categorias com ate 5 registros"})

    qualidade = pd.DataFrame(linhas)
    destino = path_saida or (TABELAS_DIR / "qualidade_ocorrencias.csv")
    destino.parent.mkdir(parents=True, exist_ok=True)
    qualidade.to_csv(destino, index=False, sep=";", encoding="utf-8-sig")
    salvar_qualidade_markdown(qualidade)
    return qualidade


def salvar_qualidade_markdown(qualidade: pd.DataFrame, path_saida: Path | None = None) -> Path:
    destino = path_saida or (RELATORIOS_DIR / "qualidade_dados.md")
    destino.parent.mkdir(parents=True, exist_ok=True)

    linhas = [
        "# Relatorio de qualidade dos dados",
        "",
        "Este relatorio resume controles basicos aplicados sobre a base tratada de ocorrencias.",
        "",
        "| Metrica | Valor | Detalhe |",
        "| --- | ---: | --- |",
    ]
    for _, row in qualidade.iterrows():
        linhas.append(f"| {row['metrica']} | {row['valor']} | {row['detalhe']} |")
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    return destino


def auditar_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    manifesto = gerar_manifesto_dados()
    qualidade = gerar_relatorio_qualidade()
    return manifesto, qualidade


def main() -> int:
    manifesto, qualidade = auditar_dados()
    print(f"Manifesto gerado: {TABELAS_DIR / 'manifesto_dados_brutos.csv'} ({len(manifesto)} arquivo(s))")
    print(f"Qualidade gerada: {TABELAS_DIR / 'qualidade_ocorrencias.csv'} ({len(qualidade)} metrica(s))")
    print(f"Relatorio Markdown: {RELATORIOS_DIR / 'qualidade_dados.md'}")
    erros_layout = [resultado for resultado in validar_layout_brutos() if resultado.status == "ERRO"]
    if erros_layout:
        for resultado in erros_layout:
            print(f"[ERRO] {resultado.item}: {resultado.detalhe}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
