# Tratamento dos dados

## Nulos

Campos categóricos vazios são preenchidos como `Não informado` ou equivalente normalizado. Campos numéricos de vítimas e veículos são convertidos para número e recebem zero quando o valor está ausente.

## Duplicados

Registros duplicados são removidos na etapa de limpeza. Os arquivos brutos não são alterados.

## Datas

A coluna `data_inversa` é convertida para data. A partir dela são extraídos `ano` e `mes`.

## Horários

A coluna `horario` é usada para extrair `hora`. Depois, a hora é classificada em `Madrugada`, `Manhã`, `Tarde` e `Noite`.

## Tipos numéricos

Colunas como `mortos`, `feridos_leves`, `feridos_graves`, `ilesos`, `veiculos` e `pessoas` são convertidas para números. Valores inválidos são tratados com cautela e substituídos por zero apenas nas métricas em que isso é necessário para cálculo.

## Nomes de colunas

Os nomes são normalizados para evitar diferenças entre arquivos e anos. A normalização reduz acentos, espaços e variações de escrita.

## Anos diferentes

Os scripts carregam os anos definidos para a análise principal. Atualmente, 2024, 2025 e 2026 são usados no pipeline principal. Os anos 2022 e 2023 permanecem preservados como histórico bruto.

## 2026 parcial

Como 2026 ainda não é um ano fechado, seus resultados não devem ser comparados diretamente com anos completos sem deixar claro que o período é parcial.
