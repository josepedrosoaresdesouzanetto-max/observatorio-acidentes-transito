# Observatório de Acidentes de Trânsito no Brasil

Projeto de análise de dados sobre acidentes em rodovias federais brasileiras, usando dados públicos da Polícia Rodoviária Federal (PRF).

## Objetivo

Organizar, tratar, modelar e analisar dados de acidentes para identificar padrões por ano, UF, município, rodovia, causa, horário, clima, tipo de pista e gravidade.

## Fonte dos dados

Os dados vêm de arquivos públicos da PRF. O projeto usa dois tipos de base:

- **Ocorrências:** arquivos `datatran`, com uma linha por acidente.
- **Pessoas/envolvidos:** arquivos `acidentes`, com registros dos envolvidos nas ocorrências.

## Anos analisados

A análise principal usa os anos: **2024, 2025, 2026**.

O ano de **2026 é parcial**, pois ainda está em andamento. Por isso, comparações entre 2026 e anos fechados devem ser feitas com cuidado.

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

## Como executar

```powershell
python -m src.limpar_dados
python -m src.modelar_dados
python -m src.calcular_indice_risco
python -m src.gerar_graficos
python -m src.gerar_relatorio
```

## Dashboard interativo

O projeto inclui um dashboard executável em Streamlit, com visual corporativo, filtros laterais, cards executivos, gráficos interativos, tratamento visual de categorias e rankings de risco.

Para abrir o dashboard, rode na raiz do projeto:

```powershell
pip install -r requirements.txt
streamlit run dashboard/app.py
```

No Windows, também é possível abrir o dashboard dando dois cliques no arquivo `ABRIR_DASHBOARD.bat` na raiz do projeto.

Os ícones dos cards do dashboard ficam armazenados localmente em `dashboard/assets/icons/`.

Se os dados tratados/modelados ainda não existirem, rode antes:

```powershell
python -m src.limpar_dados
python -m src.modelar_dados
python -m src.calcular_indice_risco
```

No dashboard, todos os filtros começam vazios. Filtro vazio significa todos os valores. A categoria `Ignorado` é exibida como `Não informado` apenas na camada visual; categorias raras como `Neve` e `Granizo` são preservadas.

## Como rodar testes

```powershell
python -m pytest
```

## Dados

A fonte principal dos scripts é `dados/01_brutos/`. CSVs antigos encontrados na raiz foram preservados em `dados/00_arquivos_originais_encontrados/`, sem apagar os originais.

Arquivos grandes de dados não devem ser enviados ao GitHub sem necessidade. Para reproduzir o projeto, coloque os CSVs da PRF nas pastas indicadas em `dados/01_brutos/`.

## Principais perguntas respondidas

- Quantos acidentes ocorreram por ano?
- Quais UFs concentram mais acidentes?
- Quais causas aparecem com mais frequência?
- Quais BRs aparecem no ranking de acidentes?
- Onde há mais mortes e feridos graves?
- Como interpretar 2026 como recorte parcial?
- Quais grupos aparecem com maior índice de risco?

## Índice de risco

O índice de risco é uma métrica simples, explicável e educacional:

```text
indice_risco = total_acidentes + mortos * 5 + feridos_graves * 3 + feridos_leves
```

Ele é calculado por UF, BR, município, causa e faixa de horário. A classificação em baixo, médio, alto e crítico usa a distribuição dos próprios resultados.

## Resultados gerados

Os gráficos ficam em `relatorios/graficos/` e o relatório consolidado em `relatorios/relatorio_final.md`.

## Proteção de dados e LGPD

Este projeto utiliza dados públicos disponibilizados para fins de análise educacional. Nenhum dado pessoal, sensível ou identificável foi incluído no repositório. A análise foi organizada respeitando boas práticas de privacidade, minimização de dados e uso responsável das informações.

## Limitações

- 2026 é parcial.
- Os resultados dependem da qualidade dos registros da fonte.
- A análise cobre o escopo de rodovias federais registrado pela PRF.
- Padrões encontrados não provam causalidade absoluta.

## Próximos passos

- Atualizar 2026 quando o ano fechar.
- Cruzar com frota, população ou fluxo de veículos.
- Refinar o índice de risco.

## Autor

Pedro Netto.
