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

O eixo analítico central do projeto é a variável-alvo `acidente_fatal`. Ela é criada a partir do campo original `mortos`: `acidente_fatal = 1` quando `mortos >= 1` e `acidente_fatal = 0` quando `mortos = 0`. Assim, o projeto diferencia o campo original, a regra de transformação e a variável usada para comparar acidentes fatais e não fatais. Quando `acidente_fatal = 1`, isso significa que houve pelo menos uma morte registrada na ocorrência, não que morreu exatamente uma pessoa.

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

O insight central do projeto é que **o volume de acidentes não responde sozinho ao problema analítico do curso**. Para investigar acidentes com vítimas fatais, a leitura mais adequada é comparar a **proporção de acidentes fatais** entre grupos, usando a variável-alvo `acidente_fatal`.

A pergunta "o que causa acidente fatal?" é tratada com cuidado metodológico: este projeto identifica fatores **associados** à fatalidade, mas não prova causalidade direta. Para afirmar causa, seria necessário complementar a análise com dados de exposição ao risco, fluxo de veículos, infraestrutura, velocidade, fiscalização e outros fatores externos.

Na base analisada, UFs e rodovias com muitos registros podem não ser exatamente as mesmas com maior fatalidade relativa. Por isso, o dashboard separa contagens absolutas, como total de acidentes e mortos, de métricas proporcionais, como o **percentual de fatalidade**.

Um exemplo importante da análise é a diferença entre volume absoluto e proporção. Uma UF pode concentrar mais acidentes fatais em quantidade total por ter maior volume de registros, enquanto outra pode apresentar maior percentual de fatalidade por ter uma proporção maior de acidentes com pelo menos uma morte. Por isso, o projeto analisa tanto acidentes fatais quanto percentual de fatalidade.

A resposta analítica do projeto é: acidentes fatais devem ser observados pela comparação entre ocorrências fatais e não fatais, cruzando `acidente_fatal` com UF, BR, causa, tipo de acidente, fase do dia, clima e tipo de pista. Esses cruzamentos indicam fatores **associados** à fatalidade, mas não provam causalidade.

O índice de risco permanece como métrica educacional complementar, útil para combinar frequência e severidade. Ele não substitui a variável-alvo `acidente_fatal` nem deve ser apresentado como resposta principal do problema.

Outro ponto importante é que **o ano corrente deve ser tratado como parcial quando estiver no recorte**. Em 2026, isso significa interpretar 2026 com cuidado; quando o projeto avançar para 2027, a mesma regra passa a valer para 2027.

## Fonte dos dados

Os dados vêm de arquivos públicos da PRF. O projeto usa dois tipos principais de base:

- **Ocorrências:** arquivos `datatran`, com uma linha por acidente.
- **Pessoas/envolvidos:** arquivos `acidentes`, com registros dos envolvidos nas ocorrências.

A análise principal usa automaticamente os anos disponíveis em `dados/01_brutos/ocorrencia/` a partir de **2024**. No recorte local atual, isso cobre **2024, 2025 e 2026**. Os arquivos de 2022 e 2023 foram preservados como histórico bruto, mas não são o foco principal do relatório.

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

Para atualizar tudo a partir dos CSVs brutos locais, use o orquestrador:

```powershell
python -m src.atualizar_projeto
```

## Automação segura dos dados

O projeto foi preparado para ser reciclável sem baixar nem sobrescrever dados brutos automaticamente. A rotina abaixo consulta a fonte pública da PRF, compara com os arquivos locais e grava um relatório de status:

```powershell
python -m src.verificar_dados_publicos --salvar-relatorio
```

Para rodar a checagem semanalmente no Windows, use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\instalar_agendamento_verificacao.ps1
```

Por padrão, o agendamento fica semanal, segunda-feira às 09:00. Os relatórios e logs ficam em `logs/`, pasta ignorada pelo Git.

## Auditoria e qualidade dos dados

Para fortalecer a rastreabilidade, o projeto também gera um manifesto técnico dos CSVs brutos com tipo, ano, tamanho, data de modificação e hash SHA-256:

```powershell
python -m src.auditar_dados
```

Esse comando também gera um relatório de qualidade da base tratada, com checagens de duplicidade de ID, nulos em colunas importantes, valores negativos e categorias raras.

Arquivos gerados:

```text
relatorios/tabelas/manifesto_dados_brutos.csv
relatorios/tabelas/qualidade_ocorrencias.csv
relatorios/qualidade_dados.md
```

Esses artefatos ajudam a demonstrar controle de dados, reprodutibilidade e maturidade do pipeline.

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

- O ano corrente é parcial quando estiver presente no recorte.
- Os resultados dependem da qualidade dos registros da fonte.
- A análise cobre o escopo de rodovias federais registrado pela PRF.
- Padrões encontrados não provam causalidade absoluta.
- O índice de risco é uma métrica educacional, não uma previsão oficial.

## Próximos passos

- Adicionar prints reais do dashboard em `docs/imagens/`.
- Adicionar novos CSVs públicos da PRF na camada bruta e rodar `python -m src.atualizar_projeto` quando houver publicação nova.
- Cruzar os resultados com frota, população ou fluxo de veículos.
- Evoluir o dashboard com novos comparativos.
- Refinar o índice de risco.

## Autor

Pedro Netto.
