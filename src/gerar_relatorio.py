from __future__ import annotations

import pandas as pd

from src.config import MODELADOS_DIR, RELATORIOS_DIR, TABELAS_DIR, TRATADOS_DIR
from src.utils import ler_csv_prf


def dataframe_markdown(tabela: pd.DataFrame) -> str:
    if tabela.empty:
        return "_Sem dados disponíveis._"
    linhas = ["| " + " | ".join(map(str, tabela.columns)) + " |"]
    linhas.append("| " + " | ".join(["---"] * len(tabela.columns)) + " |")
    for _, row in tabela.iterrows():
        linhas.append("| " + " | ".join(str(row[col]) for col in tabela.columns) + " |")
    return "\n".join(linhas)


def carregar_ocorrencias_tratadas() -> pd.DataFrame:
    path = TRATADOS_DIR / "ocorrencias_tratadas.csv"
    if not path.exists():
        raise FileNotFoundError("Arquivo ocorrencias_tratadas.csv não encontrado. Rode: python -m src.limpar_dados")
    df = ler_csv_prf(path)
    for coluna in ["ano", "mortos", "feridos_graves", "feridos_leves", "total_vitimas"]:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0)
    return df


def gerar_relatorio() -> str:
    df = carregar_ocorrencias_tratadas()
    risco_path = MODELADOS_DIR / "indice_risco_uf.csv"
    if not risco_path.exists():
        raise FileNotFoundError("Arquivo indice_risco_uf.csv não encontrado. Rode: python -m src.modelar_dados")

    acidentes_ano = df.groupby("ano").size().reset_index(name="acidentes").sort_values("ano")
    top_uf = df["uf"].value_counts().head(10).reset_index()
    top_uf.columns = ["uf", "acidentes"]
    top_causas = df["causa_acidente"].value_counts().head(10).reset_index()
    top_causas.columns = ["causa", "acidentes"]
    mortos_uf = df.groupby("uf")["mortos"].sum().sort_values(ascending=False).head(10).reset_index()
    graves_uf = df[df["acidente_grave"] == "Sim"].groupby("uf").size().sort_values(ascending=False).head(10).reset_index(name="acidentes_graves")
    risco_uf = ler_csv_prf(risco_path).head(10)
    risco_uf.to_csv(TABELAS_DIR / "ranking_indice_risco_uf.csv", index=False, encoding="utf-8-sig")

    anos = ", ".join(str(int(a)) for a in sorted(df["ano"].dropna().unique()))
    total = len(df)

    conteudo = f"""
# Relatório final - Observatório de Acidentes de Trânsito no Brasil

## 1. Resumo executivo

O projeto organiza e analisa dados públicos da Polícia Rodoviária Federal sobre acidentes em rodovias federais brasileiras. A análise principal usa os anos de {anos}, com 2026 tratado como recorte parcial.

Foram processadas **{total:,} ocorrências** na base tratada principal.

## 2. Objetivo

Identificar padrões de acidentes por tempo, local, rodovia, causa, tipo de acidente, clima, condições da via e gravidade, usando um fluxo reproduzível com Python, SQL, documentação e gráficos.

## 3. Fonte dos dados

Os dados são públicos e vieram da PRF. O projeto usa arquivos de ocorrência (`datatran`) e arquivos de pessoa/envolvido (`acidentes`).

## 4. Anos analisados

{dataframe_markdown(acidentes_ano)}

O ano de 2026 é parcial, pois ainda está em andamento. Por isso, não deve ser comparado diretamente com anos fechados sem essa ressalva.

## 5. Dados utilizados

A fonte principal dos scripts está em `dados/01_brutos/`. Os dados tratados ficam em `dados/02_tratados/` e os modelados ficam em `dados/03_modelados/`.

## 6. Tratamento realizado

Foram aplicadas etapas de leitura com separador `;`, tratamento de encoding, padronização de nomes de colunas, conversão de datas e horários, tratamento de nulos, remoção de duplicados, conversão de campos numéricos e criação de colunas derivadas.

## 7. Principais análises

### UFs com mais acidentes

{dataframe_markdown(top_uf)}

### Principais causas

{dataframe_markdown(top_causas)}

### UFs com mais mortos

{dataframe_markdown(mortos_uf)}

### UFs com mais acidentes graves

{dataframe_markdown(graves_uf)}

## 8. Gráficos gerados

Os gráficos estão em `relatorios/graficos/`:

- `acidentes_por_ano.png`
- `acidentes_por_uf.png`
- `acidentes_por_horario.png`
- `acidentes_por_dia_semana.png`
- `causas_mais_comuns.png`
- `tipos_acidente.png`
- `acidentes_por_clima.png`
- `acidentes_graves_por_uf.png`
- `ranking_rodovias.png`
- `indice_risco.png`

## 9. Índice de risco

Fórmula usada:

`indice_risco = total_acidentes + mortos * 5 + feridos_graves * 3 + feridos_leves`

O índice é educacional, simples e transparente. Ele não representa previsão oficial nem indicador validado por órgão público.

### Top 10 UFs por índice de risco

{dataframe_markdown(risco_uf)}

## 10. Principais insights encontrados

- A análise mostra que volume de acidentes e gravidade precisam ser observados juntos.
- Rankings por UF, BR e causa ajudam a localizar concentrações de ocorrências.
- O índice de risco facilita a leitura combinada entre frequência e severidade.
- 2026 já possui registros úteis, mas ainda não pode ser comparado como ano fechado.

## 11. Limitações

- 2026 é parcial.
- A qualidade da análise depende da qualidade dos registros disponíveis.
- A base cobre o escopo de rodovias federais registrado pela PRF.
- A análise mostra padrões, não causalidade absoluta.
- Comparações entre anos precisam considerar possíveis diferenças de preenchimento.

## 12. Conclusão

O projeto está organizado como uma base educacional e técnica para demonstrar um fluxo completo de análise de dados: dados brutos, tratamento, modelagem, visualização, SQL, relatório e documentação.

## 13. Próximos passos

- Refinar os notebooks com saídas executadas.
- Manter e evoluir o dashboard interativo com novos filtros e comparativos.
- Atualizar 2026 quando o ano for fechado.
- Incluir indicadores externos, como frota, população ou fluxo de veículos.
"""

    path = RELATORIOS_DIR / "relatorio_final.md"
    path.write_text(conteudo.strip() + "\n", encoding="utf-8", newline="\n")
    return str(path)


if __name__ == "__main__":
    print(gerar_relatorio())
