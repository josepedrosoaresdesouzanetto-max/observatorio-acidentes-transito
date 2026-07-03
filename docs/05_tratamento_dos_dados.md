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

## Variável-alvo

A coluna `acidente_fatal` é criada a partir do campo `mortos`.

- `acidente_fatal = 1` quando `mortos >= 1`
- `acidente_fatal = 0` quando `mortos = 0`

Essa coluna é a variável-alvo do projeto. Ela permite comparar ocorrências fatais e não fatais por UF, BR, horário, causa, tipo de acidente, clima, pista e outras dimensões.

## Nomes de colunas

Os nomes são normalizados para evitar diferenças entre arquivos e anos. A normalização reduz acentos, espaços e variações de escrita.

## Anos diferentes

Os scripts detectam automaticamente os anos disponíveis na camada bruta de ocorrência a partir de 2024. Atualmente, 2024, 2025 e 2026 aparecem no recorte local. Os anos 2022 e 2023 permanecem preservados como histórico bruto.

## Ano corrente parcial

Quando o ano corrente aparece no recorte, seus resultados devem ser tratados como parciais. Em 2026, isso vale para 2026; quando o projeto avançar para 2027, a regra passa naturalmente a valer para 2027.

## Auditoria de qualidade

Depois do tratamento, a rotina `src.auditar_dados` gera controles de qualidade sobre `ocorrencias_tratadas.csv`.

Ela verifica:

- total de linhas;
- IDs duplicados;
- nulos em colunas essenciais;
- valores negativos em mortos e feridos;
- categorias raras em campos categóricos relevantes;
- manifesto dos CSVs brutos com hash SHA-256.

Comando:

```powershell
python -m src.auditar_dados
```

Saídas principais:

```text
relatorios/qualidade_dados.md
relatorios/tabelas/qualidade_ocorrencias.csv
relatorios/tabelas/manifesto_dados_brutos.csv
```
