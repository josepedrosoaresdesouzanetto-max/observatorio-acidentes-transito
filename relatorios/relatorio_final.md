# Relatório final - Observatório de Acidentes de Trânsito no Brasil

## 1. Resumo executivo

O projeto organiza e analisa dados públicos da Polícia Rodoviária Federal sobre acidentes em rodovias federais brasileiras. A análise principal usa os anos de 2024, 2025, 2026, com 2026 tratado como recorte parcial.

Foram processadas **175,459 ocorrências** na base tratada principal.

## 2. Objetivo

Identificar padrões de acidentes por tempo, local, rodovia, causa, tipo de acidente, clima, condições da via e gravidade, usando um fluxo reproduzível com Python, SQL, documentação e gráficos.

## 3. Fonte dos dados

Os dados são públicos e vieram da PRF. O projeto usa arquivos de ocorrência (`datatran`) e arquivos de pessoa/envolvido (`acidentes`).

## 4. Anos analisados

| ano | acidentes |
| --- | --- |
| 2024 | 73156 |
| 2025 | 72529 |
| 2026 | 29774 |

O ano de 2026 é parcial, pois ainda está em andamento. Por isso, não deve ser comparado diretamente com anos fechados sem essa ressalva.

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
