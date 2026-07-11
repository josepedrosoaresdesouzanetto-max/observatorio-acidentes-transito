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
LOGS_DIR = PROJECT_ROOT / "logs"
TEMPORARIOS_PRF_DIR = DADOS_DIR / "temporarios" / "prf"
BACKUPS_PRF_DIR = DADOS_DIR / "backups"
MANIFESTO_REMOTO_PRF_PATH = LOGS_DIR / "manifesto_dados_remotos.json"
RELATORIO_SINCRONIZACAO_PRF_PATH = LOGS_DIR / "relatorio_sincronizacao_prf.md"

ENCODINGS = ("utf-8-sig", "latin1", "cp1252")
SEPARADOR_PADRAO = ";"
ANO_INICIAL_ANALISE = 2024
ANOS_ANALISE = (2024, 2025, 2026)
URL_DADOS_ABERTOS_PRF = "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf"

for directory in (TRATADOS_DIR, MODELADOS_DIR, DICIONARIO_DIR, GRAFICOS_DIR, TABELAS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
