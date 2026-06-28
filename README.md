# Observatório de Acidentes de Trânsito no Brasil

Análise de dados públicos da PRF sobre acidentes em rodovias federais brasileiras, com pipeline em Python, consultas SQL, relatório técnico e dashboard interativo em Streamlit.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/status-projeto%20acad%C3%AAmico-blue?style=flat)

## Sobre o projeto

Este projeto organiza, trata e analisa dados públicos da **Polícia Rodoviária Federal (PRF)** para observar padrões de acidentes em rodovias federais brasileiras.

A proposta é transformar bases grandes em uma análise reproduzível, com foco em perguntas como:

- quais fatores estão associados a acidentes fatais;
- quais UFs concentram mais acidentes;
- quais causas aparecem com mais frequência;
- quais BRs se destacam nos rankings;
- em quais períodos os acidentes ocorrem mais;
- onde há maior combinação entre volume e gravidade.

O eixo analítico central do projeto é a variável-alvo `acidente_fatal`. Ela é criada a partir do campo original `mortos`: `acidente_fatal = 1` quando `mortos >= 1` e `acidente_fatal = 0` quando `mortos = 0`. Assim, o projeto diferencia o campo original, a regra de transformação e a variável usada para comparar acidentes fatais e não fatais.

O projeto foi desenvolvido como entrega acadêmica e também como material de portfólio júnior em análise de dados.

## Tecnologias usadas

- **Python** para tratamento, modelagem e geração de artefatos.
- **Pandas** para leitura, limpeza e agregações.
- **Matplotlib** para gráficos estáticos do relatório.
- **Streamlit** para o dashboard interativo.
- **Plotly** para gráficos interativos no dashboard.
- **SQL** para consultas, modelagem e testes de qualidade.
- **Pytest** para testes básicos do pipeline.
- **Jupyter Notebook** para roteiros de exploração e documentação analítica.

## O que este projeto entrega

- Limpeza e padronização dos dados da PRF.
- Separação dos dados em camadas bruta, tratada e modelada.
- Criação de colunas derivadas para análise temporal, geográfica e de gravidade.
- Criação da variável-alvo `acidente_fatal` a partir de `mortos`.
- Modelagem analítica com dimensões, fatos e índices de risco.
- Consultas SQL organizadas por carga, tratamento, modelagem, views e testes.
- Dashboard interativo com filtros, cards, rankings e gráficos.
- Relatório final em Markdown com gráficos e tabelas.
- Testes básicos com `pytest`.
- Documentação técnica sobre fonte, metodologia, LGPD e limitações.

## Demonstração do dashboard

O dashboard fica em `dashboard/app.py` e foi construído com Streamlit e Plotly.

As imagens abaixo estão reservadas para prints do dashboard. Elas ainda não foram adicionadas ao repositório para evitar referências quebradas no README.

<!--
Adicionar prints futuramente:

![Dashboard - visão geral](docs/imagens/dashboard_home.png)
![Ranking de UFs](docs/imagens/ranking_ufs.png)
![Índice de risco](docs/imagens/indice_risco.png)
-->

Para abrir o dashboard:

```powershell
pip install -r requirements.txt
streamlit run dashboard/app.py
```

No Windows, também é possível abrir o dashboard com dois cliques no arquivo:

```text
ABRIR_DASHBOARD.bat
```

## Principais insights

Sem tratar o volume e a gravidade em conjunto, a análise pode ficar incompleta. Uma UF ou rodovia pode ter muitos acidentes, enquanto outra pode se destacar por mortes ou feridos graves.

Por isso, o projeto inclui um **índice de risco educacional**, criado para combinar frequência e severidade. Ele não é uma previsão oficial nem um indicador validado por órgão público, mas ajuda a comparar grupos de forma transparente.

Além do índice, o projeto analisa a **proporção de acidentes fatais**. Essa leitura é importante porque volume absoluto e fatalidade relativa podem apontar prioridades diferentes.

Outro ponto importante é que **2026 é um ano parcial**. Os resultados desse ano devem ser interpretados com cuidado e não comparados diretamente com anos fechados.

## Fonte dos dados

Os dados vêm de arquivos públicos da PRF. O projeto usa dois tipos principais de base:

- **Ocorrências:** arquivos `datatran`, com uma linha por acidente.
- **Pessoas/envolvidos:** arquivos `acidentes`, com registros dos envolvidos nas ocorrências.

A análise principal usa os anos **2024, 2025 e 2026**. Os arquivos de 2022 e 2023 foram preservados como histórico bruto, mas não são o foco principal do relatório.

## Estrutura do projeto

```text
dados/01_brutos/      CSVs originais padronizados
dados/02_tratados/    CSVs limpos
dados/03_modelados/   dimensões, fatos e índices de risco
src/                  scripts Python
sql/                  scripts SQL para PostgreSQL
notebooks/            roteiros de análise em Jupyter
relatorios/           relatório, gráficos e tabelas
docs/                 documentação técnica
docs/imagens/         espaço reservado para prints do dashboard
dashboard/            dashboard interativo em Streamlit
apresentacao/         roteiro para sala de aula
testes/               testes com pytest
```

## Como instalar dependências

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Como executar o pipeline

Execute os comandos abaixo na raiz do projeto:

```powershell
python -m src.limpar_dados
python -m src.modelar_dados
python -m src.calcular_indice_risco
python -m src.gerar_graficos
python -m src.gerar_relatorio
```

Se os arquivos tratados e modelados ainda não existirem, rode primeiro:

```powershell
python -m src.limpar_dados
python -m src.modelar_dados
python -m src.calcular_indice_risco
```

## Como rodar os testes

```powershell
python -m pytest
```

## Índice de risco

O índice de risco é uma métrica simples, explicável e educacional:

```text
indice_risco = total_acidentes + mortos * 5 + feridos_graves * 3 + feridos_leves
```

Ele é calculado por UF, BR, município, causa e faixa de horário. A classificação em baixo, médio, alto e crítico usa a distribuição dos próprios resultados.

## Resultados gerados

- Gráficos: `relatorios/graficos/`
- Tabelas: `relatorios/tabelas/`
- Relatório final: `relatorios/relatorio_final.md`
- Dashboard: `dashboard/app.py`
- Roteiro de apresentação: `apresentacao/roteiro_apresentacao.md`

## Dados e GitHub

Os CSVs grandes de dados brutos, tratados e modelados não são enviados ao GitHub. Eles ficam ignorados pelo `.gitignore`.

Para reproduzir o projeto, coloque os CSVs públicos da PRF nas pastas indicadas em `dados/01_brutos/` e execute o pipeline.

## Proteção de dados e LGPD

Este projeto utiliza dados públicos disponibilizados para fins de análise educacional. Nenhum dado pessoal sensível ou identificável foi incluído no repositório.

## Limitações

- 2026 é parcial.
- Os resultados dependem da qualidade dos registros da fonte.
- A análise cobre o escopo de rodovias federais registrado pela PRF.
- Padrões encontrados não provam causalidade absoluta.
- O índice de risco é uma métrica educacional, não uma previsão oficial.

## Próximos passos

- Adicionar prints reais do dashboard em `docs/imagens/`.
- Atualizar 2026 quando o ano fechar.
- Cruzar os resultados com frota, população ou fluxo de veículos.
- Evoluir o dashboard com novos comparativos.
- Refinar o índice de risco.

## Autor

Pedro Netto.
