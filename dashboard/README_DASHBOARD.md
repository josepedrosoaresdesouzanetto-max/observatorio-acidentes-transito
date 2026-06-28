# Dashboard interativo

Este dashboard foi criado em Streamlit para explorar os dados tratados e modelados do projeto **Observatório de Acidentes de Trânsito no Brasil** com uma interface corporativa, estável e apresentável em sala de aula.

## Objetivo

Permitir uma análise interativa dos acidentes em rodovias federais brasileiras, com filtros, cards executivos, gráficos profissionais, rankings de risco e leitura da variável-alvo `acidente_fatal`.

## Fontes de dados usadas

Fonte principal:

- `dados/02_tratados/ocorrencias_tratadas.csv`
- `dados/02_tratados/pessoas_tratadas.csv`

Arquivos modelados usados quando disponíveis:

- `dados/03_modelados/indice_risco_uf.csv`
- `dados/03_modelados/indice_risco_br.csv`
- `dados/03_modelados/indice_risco_municipio.csv`
- `dados/03_modelados/indice_risco_causa_acidente.csv`
- `dados/03_modelados/indice_risco_faixa_horario.csv`

## Como executar

Na raiz do projeto:

```powershell
pip install -r requirements.txt
streamlit run dashboard/app.py
```

No Windows, também é possível abrir o dashboard dando dois cliques no arquivo `ABRIR_DASHBOARD.bat` na raiz do projeto.

Os ícones dos cards ficam armazenados em `dashboard/assets/icons/` e são carregados pelo próprio app.

Se os CSVs tratados ou modelados não existirem, rode antes:

```powershell
python -m src.limpar_dados
python -m src.modelar_dados
python -m src.calcular_indice_risco
```

## Filtros disponíveis

Todos os filtros começam vazios. Filtro vazio significa que todos os valores são considerados.

- Ano
- UF
- BR
- Causa do acidente
- Tipo de acidente
- Fase do dia
- Condição meteorológica
- Faixa de horário

## Abas do dashboard

1. **Visão Geral:** cards executivos, acidentes por ano, UF, mês, dia da semana e resumo anual.
2. **Perfil dos Acidentes:** causas, tipos de acidente, fase do dia e condição meteorológica.
3. **Gravidade:** percentual de acidentes fatais por UF, mortos por UF, acidentes graves por causa e comparação entre volume e gravidade.
4. **Rodovias e Locais Críticos:** rankings de BRs, municípios, BRs por índice de risco, UFs por índice de risco e municípios críticos.
5. **Índice de Risco:** fórmula, rankings por UF, BR e causa, e classificação em baixo, médio, alto e crítico.

## Tratamento visual de categorias

O dashboard não altera os CSVs. Apenas na camada visual, a categoria `Ignorado` aparece como `Não informado`.

Categorias raras, como `Neve` e `Granizo`, continuam disponíveis nos filtros e gráficos. Elas são mantidas porque fazem parte do registro público, mas devem ser interpretadas como condições raras no contexto brasileiro.

## Limitações

- 2026 é parcial e não deve ser comparado diretamente com anos fechados.
- O índice de risco é uma métrica educacional e analítica, não uma previsão oficial.
- O dashboard depende dos CSVs tratados e modelados gerados pelos scripts do projeto.
- Os dados são públicos e não incluem dados pessoais sensíveis no repositório.
