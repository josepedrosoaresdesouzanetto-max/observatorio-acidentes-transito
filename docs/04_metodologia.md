# Metodologia

O projeto foi organizado em camadas para separar dados originais, dados tratados e dados modelados.

## 1. Coleta dos dados

Os arquivos CSV públicos da PRF foram localizados no projeto. Os arquivos de ocorrência e pessoa/envolvido foram identificados por nome, tamanho e colunas.

## 2. Organização dos arquivos

Os CSVs originais foram preservados. Cópias padronizadas foram colocadas em `dados/01_brutos/ocorrencia/` e `dados/01_brutos/pessoa/`. Arquivos antigos encontrados na raiz também foram preservados em `dados/00_arquivos_originais_encontrados/`.

## 3. Tratamento

A leitura usa separador `;` e tratamento de encoding. Depois, são padronizados nomes de colunas, datas, horários, categorias vazias, duplicados e tipos numéricos.

## 4. Padronização

Os nomes das colunas são convertidos para um formato mais estável, em letras minúsculas e com `_`. Isso reduz problemas entre anos diferentes.

## 5. Criação de colunas derivadas

Foram criadas colunas como `ano`, `mes`, `hora`, `faixa_horario`, `final_de_semana`, `total_feridos`, `total_vitimas`, `teve_morte`, `acidente_grave` e `nivel_gravidade`.

## 6. Modelagem

A camada modelada separa dimensões e fatos para facilitar consultas e análises. Também são gerados arquivos de índice de risco por diferentes dimensões.

## 7. Análise exploratória

A análise considera volume de acidentes, localidade, rodovia, período, causa, tipo de acidente, clima, fase do dia e gravidade.

## 8. Geração de gráficos

Os gráficos são gerados em PNG na pasta `relatorios/graficos/`, permitindo uso em relatório, apresentação ou dashboard.

## 9. Índice de risco

O índice de risco é uma métrica educacional simples, criada para comparar grupos considerando volume e gravidade.

## 10. Conclusões

As conclusões são baseadas nos dados processados e deixam claro que 2026 é parcial e que a análise mostra padrões, não causalidade absoluta.
