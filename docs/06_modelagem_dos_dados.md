# Modelagem dos dados

A camada modelada fica em `dados/03_modelados/` e organiza os dados para análise.

## dim_tempo

Contém combinações de data, ano, mês, dia da semana, hora, faixa de horário e indicação de final de semana.

## dim_local

Reúne UF e município, permitindo análises por região administrativa.

## dim_rodovia

Contém BR, km, tipo de pista e traçado da via. Ajuda a observar trechos e características de rodovia.

## dim_causa

Reúne causa, tipo de acidente e classificação. É útil para comparar frequência e gravidade por causa.

## dim_clima

Agrupa condição meteorológica e fase do dia.

## fato_acidentes

Tabela principal da análise de ocorrências. Contém medidas como mortos, feridos leves, feridos graves, ilesos, veículos, total de feridos, total de vítimas e classificação de gravidade.

## fato_vitimas

Tabela derivada dos arquivos de pessoa/envolvido. Ela preserva informações dos envolvidos para análises específicas de vítimas e perfis.

## Índices de risco

Foram criados arquivos de índice de risco por UF, BR, município, causa e faixa de horário. O índice considera volume de acidentes e severidade.
