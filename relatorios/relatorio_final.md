# Relatório final - Observatório de Acidentes de Trânsito no Brasil

## 1. Resumo executivo

O projeto organiza e analisa dados públicos da Polícia Rodoviária Federal sobre acidentes em rodovias federais brasileiras. A análise principal usa os anos disponíveis a partir de 2024. No recorte local atual, isso inclui 2024, 2025 e 2026; o ano corrente é tratado como recorte parcial quando estiver presente.

Foram processadas **175,459 ocorrências** na base tratada principal.

## 2. Objetivo

Identificar padrões associados a acidentes fatais por tempo, local, rodovia, causa, tipo de acidente, clima, condições da via e gravidade, usando um fluxo reproduzível com Python, SQL, documentação e gráficos.

A variável-alvo do projeto é `acidente_fatal`, criada a partir do campo original `mortos`: quando `mortos >= 1`, `acidente_fatal = 1`; quando `mortos = 0`, `acidente_fatal = 0`. Quando `acidente_fatal = 1`, isso significa que houve pelo menos uma morte registrada na ocorrência, não que morreu exatamente uma pessoa.

### Metodologia CRISP-DM

A metodologia principal do projeto é o **CRISP-DM, adaptado para um projeto de Data Analytics**: compreensão do negócio pela pergunta sobre acidentes fatais; compreensão dos dados pelas bases públicas da PRF; preparação com limpeza, padronização e `acidente_fatal`; modelagem analítica com agregações, indicadores e comparações proporcionais; avaliação com testes, auditoria, validação e limitações; e comunicação pelo dashboard, relatório, README e apresentação.

Não há Machine Learning nesta etapa. Em modelo futuro, `mortos`, `feridos_graves`, `feridos_leves`, `total_vitimas`, `acidente_grave`, `indice_risco` e `acidente_fatal` não devem ser preditores diretos. `mortos` cria a variável-alvo; causa e tipo de acidente podem ser registrados apenas após a ocorrência.

## 3. Fonte dos dados

Os dados são públicos e vieram da PRF. O projeto usa arquivos de ocorrência (`datatran`) e arquivos de pessoa/envolvido (`acidentes`).

## 4. Anos analisados

| ano | acidentes |
| --- | --- |
| 2024 | 73156 |
| 2025 | 72529 |
| 2026 | 29774 |

O ano corrente é parcial quando estiver presente no recorte. Por isso, anos em andamento não devem ser comparados diretamente com anos fechados sem essa ressalva.

## 5. Dados utilizados

A fonte principal dos scripts está em `dados/01_brutos/`. Os dados tratados ficam em `dados/02_tratados/` e os modelados ficam em `dados/03_modelados/`.

## 6. Tratamento realizado

Foram aplicadas etapas de leitura com separador `;`, tratamento de encoding, padronização de nomes de colunas, conversão de datas e horários, tratamento de nulos, remoção de duplicados, conversão de campos numéricos e criação de colunas derivadas.

## 7. Principais análises

### UFs com mais acidentes

| uf | acidentes |
| --- | --- |
| MG | 22622 |
| SC | 20105 |
| PR | 18460 |
| RJ | 15461 |
| RS | 12016 |
| SP | 11398 |
| BA | 9971 |
| GO | 7896 |
| PE | 7604 |
| MT | 6256 |

### Principais causas

| causa | acidentes |
| --- | --- |
| Ausência de reação do condutor | 26854 |
| Reação tardia ou ineficiente do condutor | 26182 |
| Acessar a via sem observar a presença dos outros veículos | 16961 |
| Condutor deixou de manter distância do veículo da frente | 10652 |
| Velocidade Incompatível | 10067 |
| Manobra de mudança de faixa | 9808 |
| Ingestão de álcool pelo condutor | 8979 |
| Demais falhas mecânicas ou elétricas | 8137 |
| Transitar na contramão | 5948 |
| Condutor Dormindo | 5029 |

### UFs com mais mortos

| uf | mortos |
| --- | --- |
| MG | 1888 |
| BA | 1452 |
| PR | 1426 |
| SC | 1015 |
| RS | 812 |
| RJ | 808 |
| PE | 789 |
| GO | 749 |
| MA | 651 |
| MT | 575 |

### UFs com maior percentual de acidentes fatais

| uf | total_acidentes | acidentes_fatais | percentual_fatalidade |
| --- | --- | --- | --- |
| MA | 2937 | 562 | 19.14 |
| PA | 2540 | 441 | 17.36 |
| RR | 323 | 56 | 17.34 |
| AM | 369 | 55 | 14.91 |
| AL | 1599 | 209 | 13.07 |
| TO | 1737 | 219 | 12.61 |
| CE | 3258 | 376 | 11.54 |
| BA | 9971 | 1138 | 11.41 |
| PI | 3583 | 360 | 10.05 |
| PE | 7604 | 721 | 9.48 |

### UFs com mais acidentes graves

| uf | acidentes_graves |
| --- | --- |
| MG | 6607 |
| SC | 5050 |
| PR | 4708 |
| BA | 3521 |
| RJ | 3188 |
| PE | 2760 |
| RS | 2685 |
| GO | 2281 |
| SP | 2073 |
| ES | 1928 |

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

| uf | total_acidentes | mortos | feridos_graves | feridos_leves | indice_risco | classe_risco |
| --- | --- | --- | --- | --- | --- | --- |
| MG | 22622 | 1888 | 6797 | 21679 | 74132 | Crítico |
| SC | 20105 | 1015 | 5218 | 17853 | 58687 | Crítico |
| PR | 18460 | 1426 | 4618 | 15977 | 55421 | Crítico |
| RJ | 15461 | 808 | 3027 | 15344 | 43926 | Crítico |
| BA | 9971 | 1452 | 3434 | 9185 | 36718 | Crítico |
| RS | 12016 | 812 | 2670 | 10777 | 34863 | Crítico |
| SP | 11398 | 523 | 1902 | 10426 | 30145 | Crítico |
| PE | 7604 | 789 | 2707 | 5734 | 25404 | Alto |
| GO | 7896 | 749 | 2258 | 6436 | 24851 | Alto |
| ES | 6015 | 403 | 1975 | 5580 | 19535 | Alto |

## 10. Principais insights encontrados

- A pergunta "o que causa acidente fatal?" é tratada neste projeto como análise de fatores associados, não como prova de causalidade direta. A base da PRF permite observar padrões registrados, mas não isolar causa definitiva sem dados externos de exposição ao risco.
- O principal insight é que **volume de acidentes não é a mesma coisa que fatalidade relativa**. Estados ou rodovias com muitos acidentes podem aparecer no topo por quantidade de registros, mas a pergunta do projeto exige observar também o percentual de acidentes fatais.
- Um exemplo importante da análise é a diferença entre volume absoluto e proporção. Uma UF pode concentrar mais acidentes fatais em quantidade total por ter maior volume de registros, enquanto outra pode apresentar maior percentual de fatalidade por ter uma proporção maior de acidentes com pelo menos uma morte.
- A variável-alvo `acidente_fatal` permite responder melhor ao problema do curso porque separa ocorrências com morte registrada das ocorrências sem morte. Com isso, a análise deixa de olhar apenas para `mortos` como contagem e passa a comparar grupos fatais e não fatais.
- Na análise por UF, a comparação proporcional mostra um padrão importante: UFs como MA, PA e RR aparecem com altos percentuais de acidentes fatais no recorte analisado, mesmo quando não são necessariamente as maiores em volume absoluto de acidentes.
- Os fatores que devem orientar a leitura analítica são UF, BR, causa registrada, tipo de acidente, fase do dia, condição meteorológica e tipo de pista. Esses campos ajudam a identificar associações com fatalidade, mas não permitem afirmar causa direta.
- O índice de risco é útil como apoio visual e educacional, porque combina frequência e severidade, mas a resposta central do projeto deve continuar sendo a análise da variável `acidente_fatal` e do percentual de fatalidade.
- 2026 possui registros úteis, mas ainda é parcial. Por isso, comparações anuais precisam ser apresentadas com cautela.

## 11. Limitações

- O ano corrente é parcial quando estiver presente no recorte.
- A qualidade da análise depende da qualidade dos registros disponíveis.
- A base cobre o escopo de rodovias federais registrado pela PRF.
- A análise mostra padrões, não causalidade absoluta.
- Comparações entre anos precisam considerar possíveis diferenças de preenchimento.

## 12. Conclusão

O projeto responde ao problema analítico central ao transformar o campo `mortos` na variável-alvo binária `acidente_fatal` e usar essa variável para comparar acidentes fatais e não fatais. A principal conclusão é que a análise de fatalidade precisa considerar proporções e cruzamentos por contexto, não apenas rankings de volume.

Assim, o dashboard, o relatório e a documentação permitem investigar fatores associados a acidentes com vítimas fatais nas rodovias federais brasileiras, mantendo o cuidado metodológico de falar em associação, e não em causalidade. O projeto também deixa claro que o ano corrente deve ser tratado como parcial e que o índice de risco é uma métrica complementar, não a resposta principal.

## 13. Próximos passos

- Refinar os notebooks com saídas executadas.
- Manter e evoluir o dashboard interativo com novos filtros e comparativos.
- Adicionar novos CSVs públicos da PRF na camada bruta e rodar `python -m src.atualizar_projeto` quando houver publicação nova.
- Incluir indicadores externos, como frota, população ou fluxo de veículos.
