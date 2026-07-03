# Fonte dos dados

Os dados utilizados são públicos e foram disponibilizados pela Polícia Rodoviária Federal (PRF). Eles registram acidentes ocorridos em rodovias federais brasileiras.

O projeto trabalha com dois tipos principais de arquivo:

- **Ocorrência:** arquivos conhecidos como `datatran`, com uma linha por acidente. Eles trazem informações como data, horário, UF, município, BR, km, causa, tipo de acidente, condições da via, clima e totais de mortos, feridos e veículos.
- **Pessoa/envolvido:** arquivos conhecidos como `acidentes`, com informações dos envolvidos nas ocorrências. Eles incluem colunas como tipo de envolvido, estado físico, idade e sexo, quando disponíveis.

A análise principal detecta automaticamente os anos disponíveis nos arquivos brutos de ocorrência a partir de 2024. No recorte local atual, isso cobre 2024, 2025 e 2026. Os arquivos de 2022 e 2023 foram preservados como histórico bruto, mas não são o foco do relatório principal. O ano corrente deve ser interpretado como parcial quando estiver presente no recorte; em 2026, isso significa tratar 2026 como parcial.

Os CSVs originais foram preservados e também copiados para `dados/01_brutos/` com nomes padronizados. A fonte principal dos scripts é sempre a pasta `dados/01_brutos/`.

## Atualização do recorte

O pipeline detecta automaticamente os anos disponíveis nos arquivos brutos de ocorrência a partir de 2024. Assim, quando um novo arquivo público for adicionado em `dados/01_brutos/ocorrencia/`, por exemplo `acidentes_2027_ocorrencia.csv`, o ano passa a entrar no processamento ao rodar novamente:

```bash
python -m src.limpar_dados
python -m src.modelar_dados
python -m src.calcular_indice_risco
```

A rotina `src/verificar_dados_publicos.py` consulta a página oficial de dados abertos da PRF, identifica os arquivos de acidentes publicados por ano e compara com os CSVs locais em `dados/01_brutos/`. Ela apenas informa o status; não baixa, sobrescreve nem processa arquivos automaticamente.

Para atualizar os arquivos tratados e modelados a partir dos CSVs brutos locais, use:

```bash
python -m src.atualizar_projeto
```

Essa rotina orquestra verificação, limpeza, modelagem, recálculo de índices e verificação final. Depois dela, o dashboard passa a refletir os CSVs tratados/modelados atualizados ao ser recarregado.

## Automação recomendada

Para uso contínuo, a checagem pública deve ser automatizada em frequência semanal. A rotina não baixa nem sobrescreve dados brutos; ela apenas consulta a página oficial da PRF, compara os anos publicados com os arquivos locais e grava um relatório de status.

Comando manual:

```powershell
python -m src.verificar_dados_publicos --salvar-relatorio
```

Script operacional:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verificar_dados_publicos_semanal.ps1
```

Instalação no Agendador de Tarefas do Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\instalar_agendamento_verificacao.ps1
```

Configuração padrão: toda segunda-feira às 09:00. Os logs e relatórios ficam em `logs/`, que não deve ser versionada.

## Manifesto dos dados brutos

O projeto possui uma rotina de auditoria para gerar manifesto dos CSVs usados pelo pipeline:

```powershell
python -m src.auditar_dados
```

O manifesto registra:

- caminho relativo do arquivo;
- tipo de base (`ocorrencia` ou `pessoa`);
- ano identificado no nome do arquivo;
- tamanho em bytes;
- data de modificação;
- hash SHA-256.

O hash permite verificar se um CSV bruto mudou entre execuções, sem depender apenas do nome do arquivo.
