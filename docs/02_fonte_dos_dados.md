# Fonte dos dados

Os dados utilizados são públicos e foram disponibilizados pela Polícia Rodoviária Federal (PRF). Eles registram acidentes ocorridos em rodovias federais brasileiras.

O projeto trabalha com dois tipos principais de arquivo:

- **Ocorrência:** arquivos conhecidos como `datatran`, com uma linha por acidente. Eles trazem informações como data, horário, UF, município, BR, km, causa, tipo de acidente, condições da via, clima e totais de mortos, feridos e veículos.
- **Pessoa/envolvido:** arquivos conhecidos como `acidentes`, com informações dos envolvidos nas ocorrências. Eles incluem colunas como tipo de envolvido, estado físico, idade e sexo, quando disponíveis.

A análise principal usa os anos de 2024, 2025 e 2026. Os arquivos de 2022 e 2023 foram preservados como histórico bruto, mas não são o foco do relatório principal. O ano de 2026 deve ser interpretado como parcial, pois ainda está em andamento e não pode ser comparado diretamente com anos fechados sem esse cuidado.

Os CSVs originais foram preservados e também copiados para `dados/01_brutos/` com nomes padronizados. A fonte principal dos scripts é sempre a pasta `dados/01_brutos/`.
