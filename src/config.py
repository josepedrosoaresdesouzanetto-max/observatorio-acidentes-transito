from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DADOS_DIR = PROJECT_ROOT / "dados"
BRUTOS_DIR = DADOS_DIR / "01_brutos"
OCORRENCIA_BRUTOS_DIR = BRUTOS_DIR / "ocorrencia"
PESSOA_BRUTOS_DIR = BRUTOS_DIR / "pessoa"
TRATADOS_DIR = DADOS_DIR / "02_tratados"
MODELADOS_DIR = DADOS_DIR / "03_modelados"
DICIONARIO_DIR = DADOS_DIR / "04_dicionario"
RELATORIOS_DIR = PROJECT_ROOT / "relatorios"
GRAFICOS_DIR = RELATORIOS_DIR / "graficos"
TABELAS_DIR = RELATORIOS_DIR / "tabelas"

ENCODINGS = ("utf-8-sig", "latin1", "cp1252")
SEPARADOR_PADRAO = ";"
ANOS_ANALISE = (2024, 2025, 2026)

for directory in (TRATADOS_DIR, MODELADOS_DIR, DICIONARIO_DIR, GRAFICOS_DIR, TABELAS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
