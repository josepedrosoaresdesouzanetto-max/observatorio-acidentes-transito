# Metodologia

O projeto foi organizado em camadas para separar dados originais, dados tratados e dados modelados.

## CRISP-DM adaptado para Data Analytics

A metodologia principal do projeto é o **CRISP-DM, adaptado para um projeto de Data Analytics**. A compreensão do negócio define a pergunta sobre acidentes fatais; a compreensão dos dados examina as bases públicas da PRF; a preparação realiza limpeza, padronização e criação de `acidente_fatal`; a modelagem analítica produz agregações, indicadores e comparações proporcionais; a avaliação combina testes, auditoria, validação da variável-alvo e limitações; e a comunicação ocorre por dashboard, relatório, README e apresentação.

## 1. Coleta dos dados

Os arquivos CSV públicos da PRF foram localizados no projeto. Os arquivos de ocorrência e pessoa/envolvido foram identificados por nome, tamanho e colunas.

## 2. Organização dos arquivos

Os CSVs originais foram preservados. Cópias padronizadas foram colocadas em `dados/01_brutos/ocorrencia/` e `dados/01_brutos/pessoa/`. Arquivos antigos encontrados na raiz também foram preservados em `dados/00_arquivos_originais_encontrados/`.

## 3. Tratamento

A leitura usa separador `;` e tratamento de encoding. Depois, são padronizados nomes de colunas, datas, horários, categorias vazias, duplicados e tipos numéricos.

## 4. Padronização

Os nomes das colunas são convertidos para um formato mais estável, em letras minúsculas e com `_`. Isso reduz problemas entre anos diferentes.

## 5. Criação de colunas derivadas

Foram criadas colunas como `ano`, `mes`, `hora`, `faixa_horario`, `final_de_semana`, `total_feridos`, `total_vitimas`, `acidente_fatal`, `teve_morte`, `acidente_grave` e `nivel_gravidade`.

A variável-alvo do projeto é `acidente_fatal`. Ela é derivada do campo original `mortos`: se `mortos >= 1`, então `acidente_fatal = 1`; se `mortos = 0`, então `acidente_fatal = 0`. Essa separação evita confundir campo original, regra de transformação e variável analítica.

## 6. Modelagem

A camada modelada separa dimensões e fatos para facilitar consultas e análises. Também são gerados arquivos de índice de risco por diferentes dimensões.

## 7. Análise exploratória

A análise considera volume de acidentes, localidade, rodovia, período, causa, tipo de acidente, clima, fase do dia, gravidade e proporção de acidentes fatais.

## 8. Geração de gráficos

Os gráficos são gerados em PNG na pasta `relatorios/graficos/`, permitindo uso em relatório, apresentação ou dashboard.

## 9. Índice de risco

O índice de risco é uma métrica educacional simples, criada para comparar grupos considerando volume e gravidade.

## 10. Conclusões

As conclusões são baseadas nos dados processados e deixam claro que o ano corrente é parcial quando estiver presente no recorte e que a análise mostra padrões, não causalidade absoluta.

## Nota para modelagem preditiva futura

Não há Machine Learning nesta etapa. A coluna `mortos` é utilizada para criar `acidente_fatal` e, por isso, não pode ser usada como variável de entrada em um modelo que tente classificar `acidente_fatal`. Também não devem ser usados como preditores diretos `mortos`, `feridos_graves`, `feridos_leves`, `total_vitimas`, `acidente_grave`, `indice_risco` e `acidente_fatal`. Causa do acidente e tipo de acidente são úteis para análise descritiva, mas podem ser informações registradas somente após a ocorrência; isso deve ser considerado em um futuro modelo preditivo.
