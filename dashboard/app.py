from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analisar_fatores_associados import analisar_fator
from src.recorte_temporal import ano_atual, texto_anos_parciais


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRATADOS_DIR = PROJECT_ROOT / "dados" / "02_tratados"
MODELADOS_DIR = PROJECT_ROOT / "dados" / "03_modelados"
ICONS_DIR = PROJECT_ROOT / "dashboard" / "assets" / "icons"
MAPS_DIR = PROJECT_ROOT / "dashboard" / "assets" / "maps"

OCORRENCIAS_PATH = TRATADOS_DIR / "ocorrencias_tratadas.csv"
PESSOAS_PATH = TRATADOS_DIR / "pessoas_tratadas.csv"
BRASIL_UFS_GEOJSON_PATH = MAPS_DIR / "brasil_ufs.geojson"

INDICE_PATHS = {
    "uf": MODELADOS_DIR / "indice_risco_uf.csv",
    "br": MODELADOS_DIR / "indice_risco_br.csv",
    "municipio": MODELADOS_DIR / "indice_risco_municipio.csv",
    "causa_acidente": MODELADOS_DIR / "indice_risco_causa_acidente.csv",
    "faixa_horario": MODELADOS_DIR / "indice_risco_faixa_horario.csv",
}

OCORRENCIAS_COLUNAS = [
    "id",
    "data_inversa",
    "dia_semana",
    "uf",
    "br",
    "municipio",
    "causa_acidente",
    "tipo_acidente",
    "tipo_pista",
    "tracado_via",
    "uso_solo",
    "classificacao_acidente",
    "fase_dia",
    "condicao_metereologica",
    "ano",
    "mes",
    "faixa_horario",
    "mortos",
    "acidente_fatal",
    "feridos_graves",
    "feridos_leves",
    "total_vitimas",
    "acidente_grave",
]

CORES = {
    "azul": "#38bdf8",
    "azul_claro": "#7dd3fc",
    "amarelo": "#facc15",
    "vermelho": "#ef4444",
    "verde": "#22c55e",
    "roxo": "#a78bfa",
    "texto": "#e5eefb",
    "muted": "#9fb1c8",
    "card": "rgba(15, 23, 42, 0.82)",
    "borda": "rgba(148, 163, 184, 0.24)",
}

ROTULOS = {
    "uf": "UF",
    "br": "BR",
    "municipio": "Município",
    "causa_acidente": "Causa do acidente",
    "tipo_acidente": "Tipo de acidente",
    "condicao_metereologica": "Condição meteorológica",
    "fase_dia": "Fase do dia",
    "faixa_horario": "Faixa de horário",
    "dia_semana": "Dia da semana",
    "classe_risco": "Classe de risco",
    "total_acidentes": "Total de acidentes",
    "acidentes": "Acidentes",
    "mortos": "Mortos",
    "acidente_fatal": "Acidente fatal",
    "acidentes_fatais": "Acidentes fatais",
    "percentual_fatalidade": "% fatalidade",
    "feridos_graves": "Feridos graves",
    "feridos_leves": "Feridos leves",
    "total_vitimas": "Total de vítimas",
    "vitimas": "Vítimas",
    "indice_risco": "Índice de risco",
    "acidentes_graves": "Acidentes graves",
    "percentual_graves": "% graves",
    "ano": "Ano",
    "mes": "Mês",
    "quantidade": "Quantidade",
}

CLIMA_ORDEM = [
    "Céu Claro",
    "Sol",
    "Nublado",
    "Garoa/Chuvisco",
    "Chuva",
    "Nevoeiro/Neblina",
    "Vento",
    "Granizo",
    "Neve",
    "Não informado",
]

DIA_SEMANA_ORDEM = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

RISCO_ORDEM = ["Baixo", "Médio", "Alto", "Crítico"]

METRICAS_MAPA_UF = {
    "Total de acidentes": "total_acidentes",
    "Acidentes fatais": "acidentes_fatais",
    "Percentual de fatalidade": "percentual_fatalidade",
    "Mortos": "mortos",
    "Feridos graves": "feridos_graves",
}

TITULOS_LEGENDA_MAPA = {
    "total_acidentes": "Acidentes",
    "acidentes_fatais": "Acidentes fatais",
    "percentual_fatalidade": "% fatalidade",
    "mortos": "Mortos",
    "feridos_graves": "Feridos graves",
}

ROTULOS_FILTROS_MAPA = {
    "ano": "Ano",
    "uf": "UF",
    "br": "BR",
    "causa_acidente": "Causa",
    "tipo_acidente": "Tipo de acidente",
    "tipo_pista": "Tipo de pista",
    "tracado_via": "Traçado da via",
    "uso_solo": "Uso do solo",
    "fase_dia": "Fase do dia",
    "condicao_metereologica": "Condição meteorológica",
    "faixa_horario": "Faixa horária",
}

FATORES_ASSOCIADOS = {
    "Causa do acidente": "causa_acidente",
    "Tipo de acidente": "tipo_acidente",
    "Tipo de pista": "tipo_pista",
    "Traçado da via": "tracado_via",
    "Uso do solo": "uso_solo",
    "Fase do dia": "fase_dia",
    "Condição meteorológica": "condicao_metereologica",
    "Dia da semana": "dia_semana",
    "Faixa horária": "faixa_horario",
    "BR": "br",
    "UF": "uf",
    "Município": "municipio",
}


st.set_page_config(
    page_title="Observatório de Acidentes de Trânsito no Brasil",
    page_icon="OT",
    layout="wide",
)


def aplicar_estilo_global() -> None:
    """Aplica CSS customizado para uma aparência corporativa."""
    st.markdown(
        f"""
        <style>
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        :root {{
            --card-bg: {CORES["card"]};
            --card-border: {CORES["borda"]};
            --text-main: {CORES["texto"]};
            --text-muted: {CORES["muted"]};
            --accent-blue: {CORES["azul"]};
            --accent-yellow: {CORES["amarelo"]};
            --accent-red: {CORES["vermelho"]};
            --accent-green: {CORES["verde"]};
        }}

        .stApp {{
            background: linear-gradient(135deg, #07111f 0%, #0f172a 54%, #111827 100%);
            color: var(--text-main);
        }}

        .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1480px;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.99), rgba(17, 24, 39, 0.98));
            border-right: 1px solid var(--card-border);
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label {{
            color: var(--text-main) !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: var(--text-muted);
        }}

        .hero {{
            animation: fadeInUp .35s ease-out both;
            padding: 1.35rem 1.45rem;
            border: 1px solid var(--card-border);
            border-radius: 16px;
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.72)),
                linear-gradient(90deg, rgba(56, 189, 248, 0.08), rgba(34, 197, 94, 0.05));
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
            margin-bottom: 1rem;
        }}

        .hero h1 {{
            color: #f8fafc;
            font-size: 2.15rem;
            line-height: 1.12;
            margin: 0 0 .45rem;
            letter-spacing: 0;
        }}

        .hero p {{
            color: var(--text-muted);
            font-size: 1.02rem;
            margin: 0 0 .9rem;
        }}

        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
        }}

        .badge {{
            padding: .35rem .65rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, .30);
            background: rgba(15, 23, 42, .68);
            color: #dbeafe;
            font-size: .82rem;
            font-weight: 700;
        }}

        .badge.yellow {{ color: #fef3c7; border-color: rgba(250, 204, 21, .38); }}
        .badge.red {{ color: #fecaca; border-color: rgba(239, 68, 68, .38); }}

        .info-strip {{
            animation: fadeInUp .45s ease-out both;
            border: 1px solid rgba(56, 189, 248, .22);
            border-radius: 14px;
            background: rgba(8, 47, 73, .34);
            padding: .9rem 1rem;
            margin: .8rem 0 1.1rem;
            color: #dbeafe;
            line-height: 1.45;
        }}

        .metric-card {{
            animation: fadeInUp .42s ease-out both;
            box-sizing: border-box;
            height: 214px;
            padding: .95rem;
            border: 1px solid var(--card-border);
            border-radius: 14px;
            background: var(--card-bg);
            box-shadow: 0 14px 32px rgba(0, 0, 0, .20);
            transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, .52);
            box-shadow: 0 18px 38px rgba(8, 47, 73, .26);
        }}

        .metric-top {{
            display: flex;
            justify-content: space-between;
            gap: .5rem;
            color: var(--text-muted);
            font-size: .74rem;
            font-weight: 800;
            text-transform: uppercase;
        }}

        .metric-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 4px;
            border-radius: 10px;
            background: rgba(15, 23, 42, .58);
            border: 1px solid rgba(148, 163, 184, .18);
            flex: 0 0 auto;
        }}

        .metric-icon img {{
            display: block;
            width: 36px;
            height: 36px;
            object-fit: contain;
            opacity: .92;
            filter: drop-shadow(0 3px 8px rgba(0, 0, 0, .30));
        }}

        .metric-value {{
            color: #ffffff;
            font-size: clamp(1.35rem, 2vw, 1.8rem);
            font-weight: 850;
            margin: .48rem 0 .18rem;
        }}

        .metric-description {{
            color: var(--text-muted);
            font-size: .80rem;
            line-height: 1.30;
        }}

        .metric-card.red .metric-icon {{ border-color: rgba(239, 68, 68, .28); }}
        .metric-card.yellow .metric-icon {{ border-color: rgba(250, 204, 21, .30); }}
        .metric-card.green .metric-icon {{ border-color: rgba(34, 197, 94, .28); }}

        .section-head {{
            margin: .55rem 0 1rem;
            padding: .9rem 1rem;
            border-left: 4px solid var(--accent-blue);
            border-radius: 12px;
            background: rgba(15, 23, 42, .64);
            border-top: 1px solid var(--card-border);
            border-right: 1px solid var(--card-border);
            border-bottom: 1px solid var(--card-border);
        }}

        .section-head h3 {{
            margin: 0 0 .2rem;
            color: #f8fafc;
        }}

        .section-head p {{
            margin: 0;
            color: var(--text-muted);
        }}

        div[data-testid="stTabs"] button {{
            color: #cbd5e1;
            background: rgba(15, 23, 42, .48);
            border-radius: 10px 10px 0 0;
            transition: all .16s ease;
        }}

        div[data-testid="stTabs"] button:hover {{
            color: #ffffff;
            background: rgba(30, 41, 59, .82);
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
        }}

        .ranking-caption {{
            color: var(--text-muted);
            font-size: .88rem;
            margin: -.25rem 0 .55rem;
        }}

        .formula-panel {{
            border: 1px solid rgba(56, 189, 248, .24);
            background:
                linear-gradient(135deg, rgba(15, 23, 42, .90), rgba(30, 41, 59, .66)),
                linear-gradient(90deg, rgba(56, 189, 248, .08), rgba(250, 204, 21, .05));
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: .9rem;
            box-shadow: 0 16px 36px rgba(0, 0, 0, .18);
        }}

        .formula-panel h4 {{
            margin: 0 0 .45rem;
            color: #f8fafc;
            font-size: 1.08rem;
        }}

        .formula-readable {{
            color: #ffffff;
            font-size: clamp(1.05rem, 2vw, 1.35rem);
            font-weight: 800;
            line-height: 1.35;
            margin: .25rem 0 .8rem;
        }}

        .formula-note {{
            color: var(--text-muted);
            margin: .75rem 0 0;
            font-size: .92rem;
            line-height: 1.42;
        }}

        .weight-badges {{
            display: grid;
            grid-template-columns: repeat(4, minmax(130px, 1fr));
            gap: .6rem;
        }}

        .weight-badge {{
            border: 1px solid rgba(148, 163, 184, .24);
            border-radius: 12px;
            padding: .65rem .75rem;
            background: rgba(15, 23, 42, .62);
        }}

        .weight-badge span {{
            display: block;
            color: var(--text-muted);
            font-size: .76rem;
            font-weight: 800;
            text-transform: uppercase;
        }}

        .weight-badge strong {{
            color: #f8fafc;
            font-size: 1.05rem;
        }}

        @media (max-width: 900px) {{
            .weight-badges {{ grid-template-columns: repeat(2, minmax(130px, 1fr)); }}
        }}

        .footer {{
            margin-top: 2rem;
            padding: 1rem;
            border-top: 1px solid var(--card-border);
            color: var(--text-muted);
            text-align: center;
            font-size: .9rem;
        }}

        @media (max-width: 1200px) {{
            .hero h1 {{ font-size: 1.75rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def ler_csv(path: Path, colunas: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", usecols=colunas, low_memory=False)


def normalizar_categorias_dashboard(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza categorias apenas para exibição no dashboard."""
    if df.empty:
        return df
    normalizado = df.copy()
    for coluna in normalizado.select_dtypes(include=["object"]).columns:
        normalizado[coluna] = normalizado[coluna].replace({"Ignorado": "Não informado"})
        normalizado[coluna] = normalizado[coluna].fillna("Não informado")
    return normalizado


@st.cache_data(show_spinner="Carregando dados tratados...")
def carregar_dados() -> dict[str, pd.DataFrame]:
    """Carrega somente os arquivos usados pelo dashboard."""
    if not OCORRENCIAS_PATH.exists():
        return {"erro": pd.DataFrame({"mensagem": [str(OCORRENCIAS_PATH)]})}

    colunas_disponiveis = pd.read_csv(OCORRENCIAS_PATH, sep=";", encoding="utf-8-sig", nrows=0).columns
    colunas_para_ler = [coluna for coluna in OCORRENCIAS_COLUNAS if coluna in colunas_disponiveis]
    ocorrencias = ler_csv(OCORRENCIAS_PATH, colunas_para_ler)
    for coluna in ["ano", "mes", "br", "mortos", "acidente_fatal", "feridos_graves", "feridos_leves", "total_vitimas"]:
        if coluna in ocorrencias.columns:
            ocorrencias[coluna] = pd.to_numeric(ocorrencias[coluna], errors="coerce")
    if "acidente_fatal" not in ocorrencias.columns and "mortos" in ocorrencias.columns:
        ocorrencias["acidente_fatal"] = (ocorrencias["mortos"].fillna(0) >= 1).astype(int)

    ocorrencias = normalizar_categorias_dashboard(ocorrencias)

    indices: dict[str, pd.DataFrame] = {}
    for nome, path in INDICE_PATHS.items():
        if path.exists():
            indice = ler_csv(path)
            for coluna in ["br", "total_acidentes", "mortos", "feridos_graves", "feridos_leves", "indice_risco"]:
                if coluna in indice.columns:
                    indice[coluna] = pd.to_numeric(indice[coluna], errors="coerce").fillna(0)
            indices[nome] = normalizar_categorias_dashboard(indice)

    return {
        "ocorrencias": ocorrencias,
        "pessoas_existe": pd.DataFrame({"existe": [PESSOAS_PATH.exists()]}),
        **{f"indice_{nome}": df for nome, df in indices.items()},
    }


@st.cache_data(show_spinner=False)
def carregar_geojson_brasil_ufs() -> dict:
    """Carrega o GeoJSON local das UFs brasileiras para o mapa coroplético."""
    if not BRASIL_UFS_GEOJSON_PATH.exists():
        return {"type": "FeatureCollection", "features": []}
    return json.loads(BRASIL_UFS_GEOJSON_PATH.read_text(encoding="utf-8"))


def ordenar_opcoes(coluna: str, valores: Iterable) -> list:
    opcoes = [valor for valor in pd.Series(list(valores)).dropna().unique().tolist()]

    if coluna == "ano":
        return sorted(opcoes)
    if coluna == "br":
        return sorted(opcoes)
    if coluna == "condicao_metereologica":
        return sorted(opcoes, key=lambda x: (CLIMA_ORDEM.index(x) if x in CLIMA_ORDEM else 98, str(x)))
    if coluna == "dia_semana":
        return sorted(opcoes, key=lambda x: (DIA_SEMANA_ORDEM.index(x) if x in DIA_SEMANA_ORDEM else 98, str(x)))
    if "Não informado" in opcoes:
        sem_na = sorted([v for v in opcoes if v != "Não informado"], key=lambda x: str(x))
        return sem_na + ["Não informado"]
    return sorted(opcoes, key=lambda x: str(x))


def opcoes_ordenadas(df: pd.DataFrame, coluna: str) -> list:
    if coluna not in df.columns:
        return []
    return ordenar_opcoes(coluna, df[coluna])


def multiselect_filtro(label: str, opcoes: Iterable, key: str, help_text: str) -> list:
    opcoes = list(opcoes)
    if not opcoes:
        return []
    return st.sidebar.multiselect(
        label,
        opcoes,
        default=[],
        key=key,
        help=help_text,
        placeholder="Todos os valores",
    )


def criar_sidebar_filtros(df: pd.DataFrame) -> dict[str, list]:
    st.sidebar.title("Filtros")
    st.sidebar.caption(
        "Comece sem seleção para visualizar todos os registros. Escolha valores apenas quando quiser recortar a análise."
    )
    return {
        "ano": multiselect_filtro("Ano", opcoes_ordenadas(df, "ano"), "filtro_ano", "Filtra pelo ano da ocorrência."),
        "uf": multiselect_filtro("UF", opcoes_ordenadas(df, "uf"), "filtro_uf", "Filtra por unidade federativa."),
        "br": multiselect_filtro("BR", opcoes_ordenadas(df, "br"), "filtro_br", "Filtra por rodovia federal."),
        "causa_acidente": multiselect_filtro(
            "Causa do acidente",
            opcoes_ordenadas(df, "causa_acidente"),
            "filtro_causa",
            "Filtra pela causa registrada pela PRF.",
        ),
        "tipo_acidente": multiselect_filtro(
            "Tipo de acidente",
            opcoes_ordenadas(df, "tipo_acidente"),
            "filtro_tipo",
            "Filtra pelo tipo de acidente.",
        ),
        "fase_dia": multiselect_filtro(
            "Fase do dia",
            opcoes_ordenadas(df, "fase_dia"),
            "filtro_fase",
            "Filtra por período de luminosidade.",
        ),
        "condicao_metereologica": multiselect_filtro(
            "Condição meteorológica",
            opcoes_ordenadas(df, "condicao_metereologica"),
            "filtro_clima",
            "Filtra por condição registrada. Neve e granizo são mantidos como categorias raras.",
        ),
        "faixa_horario": multiselect_filtro(
            "Faixa de horário",
            opcoes_ordenadas(df, "faixa_horario"),
            "filtro_faixa",
            "Filtra por faixa horária do acidente.",
        ),
    }


def aplicar_filtros(df: pd.DataFrame, filtros: dict[str, list]) -> pd.DataFrame:
    """Filtro vazio significa todos os valores."""
    filtrado = df.copy()
    for coluna, valores in filtros.items():
        if valores and coluna in filtrado.columns:
            filtrado = filtrado[filtrado[coluna].isin(valores)]
    return filtrado


def formatar_numero(valor: float | int) -> str:
    return f"{int(valor):,}".replace(",", ".")


def formatar_percentual(valor: float | int, casas: int = 1) -> str:
    return f"{float(valor):.{casas}f}%".replace(".", ",")


def resumo_valores_filtro(coluna: str, valores: list) -> str:
    if not valores:
        return "Todos os valores"
    if coluna == "br":
        valores_formatados = [formatar_br(valor) for valor in valores]
    else:
        valores_formatados = [str(valor) for valor in valores]
    if len(valores_formatados) <= 4:
        return ", ".join(valores_formatados)
    return f"{', '.join(valores_formatados[:4])} +{len(valores_formatados) - 4}"


def resumo_filtros_mapa(filtros: dict[str, list] | None) -> str:
    filtros = filtros or {}
    linhas = [
        "Para alterar os filtros, use a barra lateral esquerda. Este quadro apenas resume o recorte aplicado ao mapa."
    ]
    for coluna, rotulo in ROTULOS_FILTROS_MAPA.items():
        linhas.append(f"- **{rotulo}:** {resumo_valores_filtro(coluna, filtros.get(coluna, []))}")
    return "\n".join(linhas)


def texto_curto_filtros_mapa(filtros: dict[str, list] | None) -> str:
    filtros = filtros or {}
    partes = []
    for coluna in ["ano", "uf", "br", "tipo_acidente", "condicao_metereologica"]:
        partes.append(f"{ROTULOS_FILTROS_MAPA[coluna]}: {resumo_valores_filtro(coluna, filtros.get(coluna, []))}")
    return " | ".join(partes)


@st.cache_data(show_spinner=False)
def carregar_icone_base64(caminho_icone: str) -> str:
    """Carrega um ícone local e devolve um data URI para uso nos cards."""
    caminho = ICONS_DIR / caminho_icone
    if not caminho.exists():
        return ""

    mime_por_extensao = {
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    mime = mime_por_extensao.get(caminho.suffix.lower(), "image/png")
    encoded = base64.b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_metric_card(label: str, value: str, description: str) -> None:
    """Renderiza um card individual como HTML seguro no Streamlit."""
    estilos_por_card = {
        "total de acidentes": ("", "atencao.png"),
        "mortos": ("red", "cranio.png"),
        "acidentes fatais": ("red", "cranio.png"),
        "feridos graves": ("red", "paciente.png"),
        "feridos leves": ("yellow", "placa-de-hospital.png"),
        "vítimas": ("green", "vitima.png"),
        "vitimas": ("green", "vitima.png"),
        "acidentes graves": ("red", "carros-batendo.png"),
        "percentual de fatalidade": ("yellow", "acidente-de-carro.png"),
        "percentual de graves": ("yellow", "percentagem.png"),
    }
    accent_class, icon_file = estilos_por_card.get(label.lower(), ("", "colisao-de-carro.png"))
    icon_src = carregar_icone_base64(icon_file)
    icon_html = f'<img src="{icon_src}" alt="" aria-hidden="true">' if icon_src else ""

    html = f"""
    <div class="metric-card {accent_class}">
        <div class="metric-top">
            <span>{label}</span>
            <span class="metric-icon">{icon_html}</span>
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-description">{description}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def criar_cards(df: pd.DataFrame) -> None:
    total_acidentes = len(df)
    mortos = df.get("mortos", pd.Series(dtype=float)).sum()
    acidentes_fatais = df.get("acidente_fatal", pd.Series(dtype=float)).sum()
    feridos_graves = df.get("feridos_graves", pd.Series(dtype=float)).sum()
    feridos_leves = df.get("feridos_leves", pd.Series(dtype=float)).sum()
    total_vitimas = df.get("total_vitimas", pd.Series(dtype=float)).sum()
    acidentes_graves = (df.get("acidente_grave", pd.Series(dtype=str)) == "Sim").sum()
    percentual_graves = (acidentes_graves / total_acidentes * 100) if total_acidentes else 0
    percentual_fatalidade = (acidentes_fatais / total_acidentes * 100) if total_acidentes else 0

    cards = [
        ("Total de acidentes", formatar_numero(total_acidentes), "Registros no recorte atual"),
        ("Acidentes fatais", formatar_numero(acidentes_fatais), "Com morte registrada"),
        ("Mortos", formatar_numero(mortos), "Óbitos registrados"),
        ("Percentual de fatalidade", f"{percentual_fatalidade:.1f}%", "Acidentes fatais / total"),
        ("Feridos graves", formatar_numero(feridos_graves), "Casos com ferimento grave"),
        ("Feridos leves", formatar_numero(feridos_leves), "Casos com ferimento leve"),
        ("Vítimas", formatar_numero(total_vitimas), "Mortos + feridos"),
        ("Acidentes graves", formatar_numero(acidentes_graves), "Com morte ou ferido grave"),
        ("Percentual de graves", f"{percentual_graves:.1f}%", "Sobre o total filtrado"),
    ]

    for inicio in range(0, len(cards), 3):
        colunas = st.columns(3)
        for coluna, (label, value, description) in zip(colunas, cards[inicio : inicio + 3]):
            with coluna:
                render_metric_card(label, value, description)


def render_header() -> None:
    badge_ano_corrente = f"{ano_atual()} parcial se presente"
    st.markdown(
        f"""
        <div class="hero">
            <h1>Observatório de Acidentes de Trânsito no Brasil</h1>
            <p>Análise interativa de acidentes em rodovias federais brasileiras com dados públicos da PRF.</p>
            <div class="badges">
                <span class="badge">Dados públicos da PRF</span>
                <span class="badge yellow">{badge_ano_corrente}</span>
                <span class="badge red">Índice educacional</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def anos_disponiveis_dashboard(df: pd.DataFrame) -> tuple[int, ...]:
    if "ano" not in df.columns:
        return ()
    anos = pd.to_numeric(df["ano"], errors="coerce").dropna().astype(int)
    return tuple(sorted(anos.unique().tolist()))


def render_avisos(df: pd.DataFrame) -> None:
    aviso_parcial = texto_anos_parciais(anos_disponiveis_dashboard(df))
    st.markdown(
        f"""
        <div class="info-strip">
            <strong>Leitura responsável:</strong> {aviso_parcial}
            Comparações com anos fechados devem ser interpretadas com cuidado. O índice de risco é uma métrica
            educacional criada para apoiar a análise. Ele não representa previsão oficial nem classificação institucional da PRF.
        </div>
        """,
        unsafe_allow_html=True,
    )


def aplicar_layout_grafico(fig, titulo: str):
    fig.update_layout(
        title=dict(text=titulo, x=0.02, xanchor="left", font=dict(size=17, color="#f8fafc")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.18)",
        font=dict(family="Segoe UI, Arial, sans-serif", size=12, color="#dbeafe"),
        margin=dict(l=18, r=18, t=58, b=18),
        height=420,
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#f8fafc", bordercolor="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(148,163,184,0.28)",
        tickfont=dict(color="#cbd5e1"),
        title_font=dict(color="#cbd5e1"),
    )
    fig.update_yaxes(
        gridcolor="rgba(148,163,184,0.13)",
        zeroline=False,
        linecolor="rgba(148,163,184,0.28)",
        tickfont=dict(color="#cbd5e1"),
        title_font=dict(color="#cbd5e1"),
    )
    return fig


def nomes_amigaveis(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={col: ROTULOS.get(col, col) for col in df.columns})


def formatar_br(valor) -> str:
    if pd.isna(valor):
        return "BR não informada"
    texto = str(valor).strip()
    if texto.upper().startswith("BR-"):
        return texto.upper()
    numero = pd.to_numeric(texto, errors="coerce")
    if pd.notna(numero):
        return f"BR-{int(numero)}"
    return f"BR-{texto.replace('BR', '').replace('-', '').strip()}"


def preparar_eixo_categoria(dados: pd.DataFrame, coluna: str) -> pd.DataFrame:
    dados = dados.copy()
    if coluna in dados.columns and coluna == "ano":
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce").astype("Int64").astype(str)
    if coluna in dados.columns and coluna == "br":
        dados[coluna] = dados[coluna].apply(formatar_br)
    return dados


def grafico_barras(
    df: pd.DataFrame,
    x: str,
    y: str,
    titulo: str,
    key: str,
    orientation: str = "v",
    color: str | None = None,
):
    if df.empty or x not in df.columns or y not in df.columns:
        st.info(f"Sem dados suficientes para: {titulo}")
        return

    dados = preparar_eixo_categoria(df, x)
    dados = preparar_eixo_categoria(dados, y)
    color_sequence = [CORES["azul"], CORES["amarelo"], CORES["vermelho"], CORES["verde"], CORES["roxo"]]
    fig = px.bar(
        dados,
        x=x,
        y=y,
        orientation=orientation,
        color=color,
        color_discrete_sequence=color_sequence,
        labels=ROTULOS,
        text_auto=True,
    )
    fig.update_traces(marker_line_width=0, textfont_color="#e5eefb", hovertemplate="%{x}<br>%{y}<extra></extra>")

    if x == "ano":
        anos = sorted(dados[x].dropna().unique().tolist())
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=anos)
    if x == "condicao_metereologica" or y == "condicao_metereologica":
        eixo = "xaxis" if x == "condicao_metereologica" else "yaxis"
        fig.update_layout(**{eixo: dict(categoryorder="array", categoryarray=CLIMA_ORDEM)})
    if x == "dia_semana":
        fig.update_xaxes(categoryorder="array", categoryarray=DIA_SEMANA_ORDEM)
    if x == "classe_risco":
        fig.update_xaxes(categoryorder="array", categoryarray=RISCO_ORDEM)
    if orientation == "h":
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))

    aplicar_layout_grafico(fig, titulo)
    st.plotly_chart(fig, width="stretch", key=key)


def contagem(df: pd.DataFrame, coluna: str, nome_valor: str = "acidentes", top: int | None = None) -> pd.DataFrame:
    if coluna not in df.columns:
        return pd.DataFrame(columns=[coluna, nome_valor])
    resultado = df[coluna].value_counts(dropna=False).reset_index()
    resultado.columns = [coluna, nome_valor]
    if coluna == "condicao_metereologica":
        resultado[coluna] = pd.Categorical(resultado[coluna], categories=CLIMA_ORDEM, ordered=True)
        resultado = resultado.sort_values(coluna)
        resultado[coluna] = resultado[coluna].astype(str)
    elif coluna == "dia_semana":
        resultado[coluna] = pd.Categorical(resultado[coluna], categories=DIA_SEMANA_ORDEM, ordered=True)
        resultado = resultado.sort_values(coluna)
        resultado[coluna] = resultado[coluna].astype(str)
    else:
        resultado = resultado.sort_values(nome_valor, ascending=False)
    if top:
        resultado = resultado.head(top)
    return resultado


def soma_por(df: pd.DataFrame, grupo: str, valor: str, top: int = 15) -> pd.DataFrame:
    if grupo not in df.columns or valor not in df.columns:
        return pd.DataFrame(columns=[grupo, valor])
    return (
        df.groupby(grupo, dropna=False)[valor]
        .sum()
        .sort_values(ascending=False)
        .head(top)
        .reset_index()
    )


def indice_top(dados: dict[str, pd.DataFrame], nome: str, top: int = 15) -> pd.DataFrame:
    df = dados.get(f"indice_{nome}", pd.DataFrame())
    if df.empty or "indice_risco" not in df.columns:
        return pd.DataFrame()
    return df.sort_values("indice_risco", ascending=False).head(top).reset_index(drop=True)


def secao(titulo: str, descricao: str) -> None:
    st.markdown(
        f"""
        <div class="section-head">
            <h3>{titulo}</h3>
            <p>{descricao}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tabela_ranking(df: pd.DataFrame, legenda: str, top: int | None = None) -> None:
    st.markdown(f'<div class="ranking-caption">{legenda}</div>', unsafe_allow_html=True)
    if df.empty:
        st.info("Tabela indisponível para o recorte atual.")
        return
    tabela = df.head(top) if top else df
    st.dataframe(nomes_amigaveis(tabela), width="stretch", hide_index=True)


def aviso_base_modelada(dados: dict[str, pd.DataFrame]) -> None:
    faltantes = [nome for nome in INDICE_PATHS if f"indice_{nome}" not in dados]
    if faltantes:
        st.warning(
            "Arquivo não encontrado. Rode os scripts de preparação antes de abrir o dashboard: "
            "`python -m src.limpar_dados`, `python -m src.modelar_dados` e `python -m src.calcular_indice_risco`."
        )


def render_visao_geral(df: pd.DataFrame) -> None:
    secao("Visão Geral", "Panorama executivo do volume de acidentes por ano, UF, mês e dia da semana.")
    col1, col2 = st.columns([1, 1])
    with col1:
        por_ano = df.groupby("ano", dropna=False).size().reset_index(name="acidentes").sort_values("ano")
        grafico_barras(por_ano, "ano", "acidentes", "Acidentes por ano", key="grafico_acidentes_por_ano")
    with col2:
        grafico_barras(contagem(df, "uf", top=15), "uf", "acidentes", "Acidentes por UF - Top 15", key="grafico_acidentes_por_uf")

    col3, col4 = st.columns([1, 1])
    with col3:
        por_mes = df.groupby("mes", dropna=False).size().reset_index(name="acidentes").sort_values("mes")
        grafico_barras(por_mes, "mes", "acidentes", "Acidentes por mês", key="grafico_acidentes_por_mes")
    with col4:
        grafico_barras(contagem(df, "dia_semana"), "dia_semana", "acidentes", "Acidentes por dia da semana", key="grafico_acidentes_por_dia_semana")

    resumo = (
        df.groupby("ano", dropna=False)
        .agg(
            acidentes=("id", "count"),
            mortos=("mortos", "sum"),
            acidentes_fatais=("acidente_fatal", "sum"),
            feridos_graves=("feridos_graves", "sum"),
            feridos_leves=("feridos_leves", "sum"),
            vitimas=("total_vitimas", "sum"),
        )
        .reset_index()
        .sort_values("ano")
    )
    tabela_ranking(resumo, "Resumo anual dos registros filtrados.")


def preparar_mapa_uf(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "uf" not in df.columns:
        return pd.DataFrame()

    agregacoes = {
        "total_acidentes": ("id", "count"),
        "acidentes_fatais": ("acidente_fatal", "sum"),
        "mortos": ("mortos", "sum"),
        "feridos_graves": ("feridos_graves", "sum"),
    }
    if "feridos_leves" in df.columns:
        agregacoes["feridos_leves"] = ("feridos_leves", "sum")

    mapa = (
        df.assign(uf=df["uf"].astype(str).str.upper().str.strip())
        .groupby("uf", dropna=False)
        .agg(**agregacoes)
        .reset_index()
    )
    if "feridos_leves" not in mapa.columns:
        mapa["feridos_leves"] = 0

    mapa["percentual_fatalidade"] = (
        mapa["acidentes_fatais"] / mapa["total_acidentes"] * 100
    ).replace([float("inf"), -float("inf")], 0).fillna(0)
    return mapa[mapa["uf"].str.match(r"^[A-Z]{2}$", na=False)]


def render_visao_geografica(df: pd.DataFrame, filtros: dict[str, list] | None = None) -> None:
    secao(
        "Visão Geográfica",
        "Mapa interativo por UF para comparar volume absoluto e fatalidade proporcional.",
    )
    st.markdown(
        """
        <div class="info-strip">
            <strong>Pergunta orientadora:</strong> Quais fatores estão associados a acidentes fatais?<br>
            <strong>Leitura esperada:</strong> Neste projeto, a pergunta "o que causa acidente fatal?" é tratada
            como análise de associação, não como prova de causalidade direta. Na visão geográfica, o recorte mostra
            quais estados concentram mais acidentes e acidentes fatais, e quais apresentam maior percentual de
            fatalidade. Volume absoluto e proporção contam histórias diferentes.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Use a barra lateral esquerda para alterar o recorte. O resumo abaixo serve apenas para consulta.")

    mapa = preparar_mapa_uf(df)
    geojson_ufs = carregar_geojson_brasil_ufs()
    if mapa.empty or not geojson_ufs.get("features"):
        st.info("Sem dados geográficos suficientes para o recorte atual.")
        return

    metrica_label = st.selectbox(
        "Métrica do mapa",
        list(METRICAS_MAPA_UF.keys()),
        index=2,
        help="Escolha se o mapa deve destacar volume absoluto ou fatalidade proporcional.",
    )
    with st.expander("Resumo dos filtros ativos", expanded=False):
        st.markdown(resumo_filtros_mapa(filtros))

    metrica = METRICAS_MAPA_UF[metrica_label]
    mapa = mapa.sort_values(metrica, ascending=False)
    for coluna in ["total_acidentes", "acidentes_fatais", "mortos", "feridos_graves", "feridos_leves"]:
        mapa[f"{coluna}_fmt"] = mapa[coluna].apply(formatar_numero)
    mapa["percentual_fatalidade_fmt"] = mapa["percentual_fatalidade"].apply(formatar_percentual)

    titulo_legenda = TITULOS_LEGENDA_MAPA.get(metrica, ROTULOS.get(metrica, metrica))
    colorbar_config = dict(
        title=dict(text=titulo_legenda, font=dict(color="#0f172a", size=12)),
        thickness=14,
        len=0.82,
        tickfont=dict(color="#0f172a", size=11),
    )
    if metrica == "percentual_fatalidade":
        colorbar_config.update(tickformat=".1f", ticksuffix="%")
    else:
        colorbar_config.update(tickformat=",.0f")

    col1, col2 = st.columns([1.45, 1])
    with col1:
        fig = px.choropleth(
            mapa,
            geojson=geojson_ufs,
            locations="uf",
            featureidkey="properties.sigla",
            color=metrica,
            hover_name="uf",
            custom_data=[
                "total_acidentes_fmt",
                "acidentes_fatais_fmt",
                "percentual_fatalidade_fmt",
                "mortos_fmt",
                "feridos_graves_fmt",
                "feridos_leves_fmt",
            ],
            color_continuous_scale=["#0f172a", CORES["azul"], CORES["amarelo"], CORES["vermelho"]],
            labels=ROTULOS,
        )
        aplicar_layout_grafico(
            fig,
            f"Mapa por UF - {metrica_label}<br><sup>Filtros: {texto_curto_filtros_mapa(filtros)}</sup>",
        )
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="#ffffff",
        )
        fig.update_traces(
            marker_line_width=0.95,
            marker_line_color="#111827",
            hovertemplate=(
                "<b>UF: %{location}</b><br><br>"
                "Total de acidentes: %{customdata[0]}<br>"
                "Acidentes fatais: %{customdata[1]}<br>"
                "% fatalidade: %{customdata[2]}<br>"
                "Mortos: %{customdata[3]}<br>"
                "Feridos graves: %{customdata[4]}<br>"
                "Feridos leves: %{customdata[5]}<extra></extra>"
            ),
        )
        fig.update_layout(
            coloraxis_colorbar=colorbar_config,
            height=560,
            margin=dict(l=0, r=0, t=76, b=0),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#0f172a"),
            title=dict(font=dict(color="#0f172a", size=17)),
            hoverlabel=dict(
                bgcolor="rgba(15, 23, 42, .96)",
                font_size=13,
                font_color="#f8fafc",
                bordercolor="#f8fafc",
            ),
        )
        st.plotly_chart(fig, width="stretch", key=f"mapa_uf_{metrica}")

    with col2:
        ranking = mapa[
            ["uf", "total_acidentes", "acidentes_fatais", "percentual_fatalidade", "mortos", "feridos_graves", "feridos_leves"]
        ]
        st.markdown(
            f'<div class="ranking-caption">Todas as UFs por {metrica_label.lower()}.</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            nomes_amigaveis(ranking),
            width="stretch",
            hide_index=True,
            column_config={
                "Total de acidentes": st.column_config.NumberColumn("Total de acidentes", format="%d"),
                "Acidentes fatais": st.column_config.NumberColumn("Acidentes fatais", format="%d"),
                "% fatalidade": st.column_config.NumberColumn("% fatalidade", format="%.1f%%"),
                "Mortos": st.column_config.NumberColumn("Mortos", format="%d"),
                "Feridos graves": st.column_config.NumberColumn("Feridos graves", format="%d"),
                "Feridos leves": st.column_config.NumberColumn("Feridos leves", format="%d"),
            },
        )


def render_fatores_associados(df: pd.DataFrame, filtros: dict[str, list]) -> None:
    st.subheader("Fatores Associados")
    st.write("**Pergunta central:** Quais fatores estão associados aos acidentes fatais?")
    st.caption(
        "A análise compara acidentes fatais e não fatais para identificar categorias com maior percentual de "
        "fatalidade. Os resultados representam associações no recorte analisado e não comprovam causalidade."
    )

    fatores_disponiveis = {rotulo: coluna for rotulo, coluna in FATORES_ASSOCIADOS.items() if coluna in df.columns}
    if not fatores_disponiveis:
        st.info("Nenhuma coluna de fator está disponível no recorte carregado.")
        return

    col_fator, col_minimo = st.columns([1.5, 1])
    with col_fator:
        rotulo_fator = st.selectbox("Fator analisado", list(fatores_disponiveis), key="fator_associado")
    with col_minimo:
        minimo = st.selectbox(
            "Mínimo de acidentes por categoria",
            [10, 25, 50, 100, 250, 500],
            index=2,
            key="minimo_fatores_associados",
        )
    st.warning(
        "Categorias com poucas ocorrências podem apresentar percentuais elevados e instáveis. "
        "O limite mínimo ajuda a tornar a comparação mais confiável."
    )
    with st.expander("Filtros aplicados à análise", expanded=False):
        for coluna, rotulo in ROTULOS_FILTROS_MAPA.items():
            st.write(f"**{rotulo}:** {resumo_valores_filtro(coluna, filtros.get(coluna, []))}")

    coluna = fatores_disponiveis[rotulo_fator]
    analise = analisar_fator(df, coluna, minimo_ocorrencias=minimo)
    if analise.empty:
        st.info("Não há categorias com ocorrências suficientes para o mínimo selecionado.")
        return

    lider_percentual = analise.iloc[0]
    lider_volume = analise.sort_values(["acidentes_fatais", "categoria"], ascending=[False, True]).iloc[0]
    if lider_percentual["categoria"] == lider_volume["categoria"]:
        st.info(
            f"No recorte filtrado, **{lider_percentual['categoria']}** apresenta o maior percentual de fatalidade "
            f"({formatar_percentual(lider_percentual['percentual_fatalidade'])}) e também concentra o maior número "
            f"absoluto de acidentes fatais entre as categorias com pelo menos {formatar_numero(minimo)} acidentes. "
            "Esse resultado representa uma associação nos registros analisados e não comprova causalidade."
        )
    else:
        st.info(
            f"No recorte filtrado, **{lider_percentual['categoria']}** apresenta o maior percentual de fatalidade "
            f"({formatar_percentual(lider_percentual['percentual_fatalidade'])}) entre as categorias com pelo menos "
            f"{formatar_numero(minimo)} acidentes, enquanto **{lider_volume['categoria']}** concentra o maior número "
            "absoluto de acidentes fatais. Esse resultado representa uma associação nos registros analisados e não "
            "comprova causalidade."
        )

    top = analise.head(15).sort_values("percentual_fatalidade", ascending=True)
    fig_percentual = px.bar(
        top,
        x="percentual_fatalidade",
        y="categoria",
        orientation="h",
        text="percentual_fatalidade",
        custom_data=["total_acidentes", "acidentes_fatais", "acidentes_nao_fatais", "mortos", "feridos_graves"],
        labels={"percentual_fatalidade": "% de fatalidade", "categoria": rotulo_fator},
        color_discrete_sequence=[CORES["vermelho"]],
    )
    fig_percentual.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>Total de acidentes: %{customdata[0]:,.0f}<br>Acidentes fatais: %{customdata[1]:,.0f}"
            "<br>Acidentes não fatais: %{customdata[2]:,.0f}<br>Percentual de fatalidade: %{x:.1f}%"
            "<br>Mortos: %{customdata[3]:,.0f}<br>Feridos graves: %{customdata[4]:,.0f}<extra></extra>"
        ),
    )
    aplicar_layout_grafico(fig_percentual, "Percentual de fatalidade por categoria")
    fig_percentual.update_layout(height=max(420, len(top) * 38), margin=dict(l=18, r=95, t=58, b=18))
    fig_percentual.update_xaxes(ticksuffix="%")
    st.plotly_chart(fig_percentual, width="stretch", key="fatores_percentual_fatalidade")
    st.caption("Leitura: 19,1% dos acidentes desta categoria tiveram pelo menos uma morte.")

    st.markdown("#### Volume absoluto versus proporção")
    st.caption(
        "Os rankings permitem comparar volume absoluto e proporção. A categoria com mais acidentes fatais não "
        "necessariamente apresenta o maior percentual de fatalidade."
    )
    ranking_fatais = analise.nlargest(10, ["acidentes_fatais", "total_acidentes"]).sort_values(
        "acidentes_fatais", ascending=True
    )
    ranking_percentual = analise.nlargest(10, ["percentual_fatalidade", "total_acidentes"]).sort_values(
        "percentual_fatalidade", ascending=True
    )
    col_ranking_fatais, col_ranking_percentual = st.columns(2)
    with col_ranking_fatais:
        fig_ranking_fatais = px.bar(
            ranking_fatais,
            x="acidentes_fatais",
            y="categoria",
            orientation="h",
            text="acidentes_fatais",
            custom_data=["total_acidentes", "percentual_fatalidade", "mortos", "feridos_graves"],
            labels={"acidentes_fatais": "Acidentes fatais", "categoria": rotulo_fator},
            color_discrete_sequence=[CORES["amarelo"]],
        )
        fig_ranking_fatais.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>Acidentes fatais: %{x:,.0f}<br>Total de acidentes: %{customdata[0]:,.0f}"
                "<br>Percentual de fatalidade: %{customdata[1]:.1f}%<br>Mortos: %{customdata[2]:,.0f}"
                "<br>Feridos graves: %{customdata[3]:,.0f}<extra></extra>"
            ),
        )
        aplicar_layout_grafico(fig_ranking_fatais, "Top 10 categorias por acidentes fatais")
        fig_ranking_fatais.update_layout(height=500, margin=dict(l=190, r=80, t=58, b=18))
        st.plotly_chart(fig_ranking_fatais, width="stretch", key="fatores_ranking_acidentes_fatais")

    with col_ranking_percentual:
        fig_ranking_percentual = px.bar(
            ranking_percentual,
            x="percentual_fatalidade",
            y="categoria",
            orientation="h",
            text="percentual_fatalidade",
            custom_data=["total_acidentes", "acidentes_fatais", "mortos", "feridos_graves"],
            labels={"percentual_fatalidade": "% de fatalidade", "categoria": rotulo_fator},
            color_discrete_sequence=[CORES["vermelho"]],
        )
        fig_ranking_percentual.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>Percentual de fatalidade: %{x:.1f}%<br>Total de acidentes: %{customdata[0]:,.0f}"
                "<br>Acidentes fatais: %{customdata[1]:,.0f}<br>Mortos: %{customdata[2]:,.0f}"
                "<br>Feridos graves: %{customdata[3]:,.0f}<extra></extra>"
            ),
        )
        aplicar_layout_grafico(fig_ranking_percentual, "Top 10 categorias por percentual de fatalidade")
        fig_ranking_percentual.update_layout(height=500, margin=dict(l=190, r=80, t=58, b=18))
        fig_ranking_percentual.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig_ranking_percentual, width="stretch", key="fatores_ranking_percentual_fatalidade")

    with st.expander("Análise avançada: volume versus proporção", expanded=False):
        st.caption(
            "As colunas representam o número absoluto de acidentes fatais, enquanto a linha mostra o percentual "
            "de fatalidade. Uma categoria pode liderar em volume sem apresentar a maior proporção."
        )
        criterio_rotulo = st.selectbox(
            "Ordenar comparação por",
            ["Acidentes fatais", "Percentual de fatalidade", "Total de acidentes"],
            key="ordenacao_comparacao_fatores",
        )
        criterio_coluna = {
            "Acidentes fatais": "acidentes_fatais",
            "Percentual de fatalidade": "percentual_fatalidade",
            "Total de acidentes": "total_acidentes",
        }[criterio_rotulo]
        comparacao = (
            analise.sort_values([criterio_coluna, "categoria"], ascending=[False, True])
            .head(10)
            .reset_index(drop=True)
        )

        def rotulo_categoria_eixo(valor: object, limite_linha: int = 26) -> str:
            texto = str(valor)
            if len(texto) <= limite_linha:
                return texto
            palavras = texto.split()
            primeira_linha: list[str] = []
            while palavras and len(" ".join(primeira_linha + [palavras[0]])) <= limite_linha:
                primeira_linha.append(palavras.pop(0))
            if not primeira_linha:
                return f"{texto[: limite_linha - 1]}…"
            segunda_linha = " ".join(palavras)
            if len(segunda_linha) > limite_linha:
                segunda_linha = f"{segunda_linha[: limite_linha - 1]}…"
            return f"{' '.join(primeira_linha)}<br>{segunda_linha}"

        comparacao["categoria_eixo"] = comparacao["categoria"].map(rotulo_categoria_eixo)
        dados_tooltip = comparacao[
            [
                "categoria",
                "total_acidentes",
                "acidentes_fatais",
                "acidentes_nao_fatais",
                "percentual_fatalidade",
                "mortos",
                "feridos_graves",
            ]
        ].to_numpy()
        tooltip_completo = (
            "<b>%{customdata[0]}</b><br>Total de acidentes: %{customdata[1]:,.0f}"
            "<br>Acidentes fatais: %{customdata[2]:,.0f}<br>Acidentes não fatais: %{customdata[3]:,.0f}"
            "<br>Percentual de fatalidade: %{customdata[4]:.1f}%<br>Mortos: %{customdata[5]:,.0f}"
            "<br>Feridos graves: %{customdata[6]:,.0f}<extra></extra>"
        )

        fig_comparacao = go.Figure()
        fig_comparacao.add_trace(
            go.Bar(
                name="Acidentes fatais",
                x=comparacao["categoria_eixo"],
                y=comparacao["acidentes_fatais"],
                customdata=dados_tooltip,
                marker_color=CORES["amarelo"],
                text=comparacao["acidentes_fatais"],
                texttemplate="%{text:,.0f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate=tooltip_completo,
            )
        )
        fig_comparacao.add_trace(
            go.Scatter(
                name="% de fatalidade",
                x=comparacao["categoria_eixo"],
                y=comparacao["percentual_fatalidade"],
                customdata=dados_tooltip,
                mode="lines+markers",
                yaxis="y2",
                line=dict(color=CORES["vermelho"], width=3),
                marker=dict(color=CORES["vermelho"], size=9, line=dict(color="#f8fafc", width=1)),
                hovertemplate=tooltip_completo,
            )
        )
        aplicar_layout_grafico(fig_comparacao, "Comparação entre volume e percentual de fatalidade")
        limite_percentual = max(1.0, float(comparacao["percentual_fatalidade"].max()) * 1.18)
        fig_comparacao.update_layout(
            height=590,
            margin=dict(l=55, r=75, t=75, b=175),
            bargap=0.28,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Acidentes fatais", tickformat=",d", rangemode="tozero"),
            yaxis2=dict(
                title="% de fatalidade",
                overlaying="y",
                side="right",
                tickformat=".1f",
                ticksuffix="%",
                range=[0, limite_percentual],
                showgrid=False,
                tickfont=dict(color="#cbd5e1"),
                title_font=dict(color="#cbd5e1"),
            ),
        )
        fig_comparacao.update_xaxes(tickangle=-35, automargin=True)
        st.plotly_chart(fig_comparacao, width="stretch", key="fatores_comparacao_volume_percentual")

    st.markdown("#### Tabela detalhada")
    st.dataframe(
        analise,
        width="stretch",
        hide_index=True,
        column_config={
            "categoria": st.column_config.TextColumn(rotulo_fator),
            "total_acidentes": st.column_config.NumberColumn("Total de acidentes", format="%,d"),
            "acidentes_fatais": st.column_config.NumberColumn("Acidentes fatais", format="%,d"),
            "acidentes_nao_fatais": st.column_config.NumberColumn("Acidentes não fatais", format="%,d"),
            "percentual_fatalidade": st.column_config.NumberColumn("% de fatalidade", format="%.1f%%"),
            "mortos": st.column_config.NumberColumn("Mortos", format="%,d"),
            "feridos_graves": st.column_config.NumberColumn("Feridos graves", format="%,d"),
        },
    )


def render_perfil_acidentes(df: pd.DataFrame) -> None:
    secao("Perfil dos Acidentes", "Principais características dos acidentes registrados pela PRF.")
    col1, col2 = st.columns([1, 1])
    with col1:
        grafico_barras(contagem(df, "causa_acidente", top=12), "acidentes", "causa_acidente", "Principais causas", key="grafico_causas_mais_comuns", orientation="h")
    with col2:
        grafico_barras(contagem(df, "tipo_acidente", top=12), "acidentes", "tipo_acidente", "Tipos de acidente", key="grafico_tipos_acidente", orientation="h")

    col3, col4 = st.columns([1, 1])
    with col3:
        grafico_barras(contagem(df, "fase_dia"), "fase_dia", "acidentes", "Acidentes por fase do dia", key="grafico_acidentes_por_fase_dia")
    with col4:
        grafico_barras(
            contagem(df, "condicao_metereologica"),
            "acidentes",
            "condicao_metereologica",
            "Condição meteorológica",
            key="grafico_condicao_meteorologica",
            orientation="h",
        )


def render_gravidade(df: pd.DataFrame) -> None:
    secao("Gravidade", "Leitura de severidade com foco na variável-alvo acidente_fatal.")
    col1, col2 = st.columns([1, 1])
    with col1:
        fatalidade_uf = (
            df.groupby("uf", dropna=False)
            .agg(total_acidentes=("id", "count"), acidentes_fatais=("acidente_fatal", "sum"))
            .reset_index()
        )
        fatalidade_uf["percentual_fatalidade"] = (
            fatalidade_uf["acidentes_fatais"] / fatalidade_uf["total_acidentes"] * 100
        ).fillna(0)
        fatalidade_uf = fatalidade_uf.sort_values("percentual_fatalidade", ascending=False).head(15)
        grafico_barras(
            fatalidade_uf,
            "uf",
            "percentual_fatalidade",
            "% de acidentes fatais por UF - Top 15",
            key="grafico_percentual_fatalidade_uf",
        )
    with col2:
        grafico_barras(soma_por(df, "uf", "mortos"), "uf", "mortos", "Mortos por UF - Top 15", key="grafico_mortos_por_uf")

    col3, col4 = st.columns([1, 1])
    with col3:
        graves = df[df.get("acidente_grave") == "Sim"]
        grafico_barras(contagem(graves, "causa_acidente", top=12), "acidentes", "causa_acidente", "Acidentes graves por causa", key="grafico_acidentes_graves_por_causa", orientation="h")
    with col4:
        comparacao = (
            df.groupby("uf", dropna=False)
            .agg(total_acidentes=("id", "count"), acidentes_graves=("acidente_grave", lambda s: (s == "Sim").sum()))
            .sort_values("total_acidentes", ascending=False)
            .head(15)
            .reset_index()
        )
        if comparacao.empty:
            st.info("Sem dados para comparar volume e gravidade.")
        else:
            fig = px.bar(
                comparacao,
                x="uf",
                y=["total_acidentes", "acidentes_graves"],
                barmode="group",
                labels=ROTULOS,
                color_discrete_sequence=[CORES["azul"], CORES["vermelho"]],
            )
            aplicar_layout_grafico(fig, "Volume total x acidentes graves por UF")
            st.plotly_chart(fig, width="stretch", key="grafico_volume_total_x_graves_uf")


def render_rodovias_locais(df: pd.DataFrame, dados: dict[str, pd.DataFrame]) -> None:
    secao("Rodovias e Locais Críticos", "Rankings de concentração por rodovia, município e índice de risco.")
    col1, col2 = st.columns([1, 1])
    with col1:
        grafico_barras(contagem(df, "br", top=15), "acidentes", "br", "Ranking de BRs com mais acidentes", key="grafico_ranking_brs", orientation="h")
    with col2:
        grafico_barras(contagem(df, "municipio", top=15), "acidentes", "municipio", "Ranking de municípios com mais acidentes", key="grafico_ranking_municipios", orientation="h")

    col3, col4 = st.columns([1, 1])
    with col3:
        grafico_barras(indice_top(dados, "br"), "indice_risco", "br", "Índice de risco por BR", key="locais_indice_risco_br", orientation="h")
    with col4:
        grafico_barras(indice_top(dados, "uf"), "uf", "indice_risco", "Índice de risco por UF", key="locais_indice_risco_uf")

    tabela_ranking(indice_top(dados, "municipio", top=10), "Top 10 municípios por índice de risco.")


def render_indice_risco(dados: dict[str, pd.DataFrame]) -> None:
    secao("Índice de Risco", "Métrica analítica simples para combinar volume e gravidade.")
    st.markdown(
        """
        <div class="formula-panel">
            <h4>Como o índice é calculado?</h4>
            <div class="formula-readable">
                Índice de risco = acidentes + mortes × 5 + feridos graves × 3 + feridos leves
            </div>
            <div class="weight-badges">
                <div class="weight-badge"><span>Acidentes</span><strong>Peso 1</strong></div>
                <div class="weight-badge"><span>Mortes</span><strong>Peso 5</strong></div>
                <div class="weight-badge"><span>Feridos graves</span><strong>Peso 3</strong></div>
                <div class="weight-badge"><span>Feridos leves</span><strong>Peso 1</strong></div>
            </div>
            <p class="formula-note">
                Quanto maior o índice, maior a combinação entre volume de acidentes e gravidade dos casos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Ver fórmula técnica"):
        st.code("indice_risco = total_acidentes + mortos * 5 + feridos_graves * 3 + feridos_leves")
    st.markdown(
        """
        <div class="info-strip">
            O índice de risco é uma métrica educacional criada para apoiar a análise. Ele não representa previsão oficial
            nem classificação institucional da PRF. A classificação baixo, médio, alto e crítico é calculada a partir da
            distribuição dos próprios resultados do projeto.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        grafico_barras(indice_top(dados, "uf"), "uf", "indice_risco", "Índice de risco por UF", key="risco_indice_risco_uf")
    with col2:
        grafico_barras(indice_top(dados, "br"), "indice_risco", "br", "Índice de risco por BR", key="risco_indice_risco_br", orientation="h")

    col3, col4 = st.columns([1, 1])
    with col3:
        grafico_barras(indice_top(dados, "causa_acidente"), "indice_risco", "causa_acidente", "Índice de risco por causa", key="grafico_indice_risco_causa", orientation="h")
    with col4:
        indice_uf = dados.get("indice_uf", pd.DataFrame())
        if "classe_risco" in indice_uf.columns:
            classes = indice_uf["classe_risco"].value_counts().reset_index()
            classes.columns = ["classe_risco", "quantidade"]
            classes["classe_risco"] = pd.Categorical(classes["classe_risco"], categories=RISCO_ORDEM, ordered=True)
            classes = classes.sort_values("classe_risco")
            classes["classe_risco"] = classes["classe_risco"].astype(str)
            grafico_barras(classes, "classe_risco", "quantidade", "Classificação de risco por UF", key="grafico_classificacao_risco_uf")
        else:
            st.info("Classificação de risco indisponível.")

    col5, col6 = st.columns([1, 1])
    with col5:
        tabela_ranking(indice_top(dados, "uf"), "Top 15 UFs por índice de risco.")
    with col6:
        tabela_ranking(indice_top(dados, "causa_acidente"), "Top 15 causas por índice de risco.")


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
            Projeto educacional de análise de dados. Fonte: dados públicos da Polícia Rodoviária Federal. Autor: Pedro Netto.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    aplicar_estilo_global()
    render_header()

    dados = carregar_dados()
    if "erro" in dados:
        st.error("Arquivo de ocorrências tratadas não encontrado.")
        st.info(
            "Arquivo não encontrado. Rode os scripts de preparação antes de abrir o dashboard:\n\n"
            "`python -m src.limpar_dados`\n\n"
            "`python -m src.modelar_dados`\n\n"
            "`python -m src.calcular_indice_risco`"
        )
        return

    ocorrencias = dados["ocorrencias"]
    render_avisos(ocorrencias)

    if not bool(dados["pessoas_existe"].loc[0, "existe"]):
        st.warning("Arquivo `pessoas_tratadas.csv` não encontrado. O dashboard seguirá com ocorrências.")

    aviso_base_modelada(dados)

    filtros = criar_sidebar_filtros(ocorrencias)
    filtrado = aplicar_filtros(ocorrencias, filtros)
    if filtrado.empty:
        st.warning("Nenhum registro encontrado com os filtros selecionados. Limpe os filtros para voltar à visão geral.")
        return

    criar_cards(filtrado)

    aba_geral, aba_geo, aba_fatores, aba_perfil, aba_gravidade, aba_locais, aba_indice = st.tabs(
        [
            "Visão Geral",
            "Visão Geográfica",
            "Fatores Associados",
            "Perfil dos Acidentes",
            "Gravidade",
            "Rodovias e Locais Críticos",
            "Índice de Risco",
        ]
    )

    with aba_geral:
        render_visao_geral(filtrado)
    with aba_geo:
        render_visao_geografica(filtrado, filtros)
    with aba_fatores:
        render_fatores_associados(filtrado, filtros)
    with aba_perfil:
        render_perfil_acidentes(filtrado)
    with aba_gravidade:
        render_gravidade(filtrado)
    with aba_locais:
        render_rodovias_locais(filtrado, dados)
    with aba_indice:
        render_indice_risco(dados)

    render_footer()


if __name__ == "__main__":
    main()
