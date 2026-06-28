# Dashboard interativo - Observatório de Acidentes de Trânsito no Brasil

O dashboard real do projeto está implementado em Streamlit no arquivo `dashboard/app.py`.

Ele usa os dados tratados e modelados do projeto para permitir análise interativa dos acidentes em rodovias federais brasileiras registrados pela PRF.

## Como abrir

Na raiz do projeto:

```powershell
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Identidade visual

O dashboard usa tema escuro corporativo, cards executivos, abas organizadas, gráficos Plotly padronizados, sidebar em português e avisos sobre interpretação dos dados.

## Fontes usadas

- `dados/02_tratados/ocorrencias_tratadas.csv`
- `dados/02_tratados/pessoas_tratadas.csv`
- `dados/03_modelados/indice_risco_uf.csv`
- `dados/03_modelados/indice_risco_br.csv`
- `dados/03_modelados/indice_risco_municipio.csv`
- `dados/03_modelados/indice_risco_causa_acidente.csv`
- `dados/03_modelados/indice_risco_faixa_horario.csv`

## Filtros laterais

Os filtros começam vazios e, nesse estado, mostram todos os registros.

- Ano
- UF
- BR
- Causa do acidente
- Tipo de acidente
- Fase do dia
- Condição meteorológica
- Faixa de horário

## Indicadores

- Total de acidentes
- Acidentes fatais
- Mortos
- Percentual de fatalidade
- Feridos graves
- Feridos leves
- Vítimas
- Acidentes graves
- Percentual de graves

## Abas

1. **Visão Geral:** cards, acidentes por ano, UF, mês, dia da semana e tabela resumo por ano.
2. **Perfil dos Acidentes:** principais causas, tipos, fase do dia e clima.
3. **Gravidade:** percentual de acidentes fatais por UF, mortos por UF, acidentes graves por causa e comparação entre volume e gravidade.
4. **Rodovias e Locais Críticos:** ranking de BRs, municípios e risco por BR/UF/município.
5. **Índice de Risco:** fórmula, rankings por UF, BR e causa, e classificação por risco.

## Observações

2026 é um ano parcial. O índice de risco é uma métrica educacional e analítica, não uma previsão oficial. A categoria `Ignorado` é exibida como `Não informado` apenas no dashboard. Categorias raras como `Neve` e `Granizo` são preservadas.
