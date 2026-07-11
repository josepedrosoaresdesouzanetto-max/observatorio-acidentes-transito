# Sincronização controlada dos dados da PRF

## Objetivo

Esta rotina monitora os CSVs oficiais publicados pela Polícia Rodoviária Federal, baixa arquivos para uma área isolada, valida seu formato e permite compará-los com os dados brutos locais. **O projeto monitora, baixa, valida e compara automaticamente, mas não substitui a base oficial sem confirmação explícita.**

Uma alteração no arquivo remoto não significa automaticamente uma ocorrência nova. A publicação pode conter correções, remoções, mudanças de schema ou reprocessamentos. Somente a comparação por uma chave validada classifica registros novos, alterados, removidos e inalterados.

## Arquitetura

- `src/verificar_dados_publicos.py`: verificação semanal existente e status resumido, sempre sem aplicação.
- `src/sincronizar_dados_prf.py`: consulta de metadados, download temporário, manifesto, relatórios, CLI, backup e rollback.
- `src/comparar_arquivos_prf.py`: leitura de CSV, normalização somente em memória, seleção de chave e comparação de registros.
- `dados/temporarios/prf/`: downloads validados, ignorados pelo Git.
- `dados/backups/`: cópias anteriores à aplicação, ignoradas pelo Git e nunca apagadas automaticamente.
- `logs/manifesto_dados_remotos.json`: último estado remoto observado.
- `logs/relatorio_sincronizacao_prf.md`: relatório detalhado da comparação.

## Manifesto remoto e detecção de mudança

Para cada publicação são registrados URL, nome, ano, tipo, `Content-Length`, `Last-Modified`, ETag, SHA-256 quando o arquivo foi baixado e data da verificação. A detecção prioriza SHA-256, ETag, data de modificação e tamanho. Se esses metadados não estiverem disponíveis, a situação fica como `comparação pendente` até que o conteúdo seja baixado e validado.

Os estados resumidos são: `sem mudança detectada`, `possível atualização detectada`, `novo arquivo publicado`, `comparação pendente`, `comparação concluída` e `atualização aguardando confirmação`.

## Download temporário

O download é escrito primeiro como `.part` em `dados/temporarios/prf/`. Antes da renomeação definitiva, a rotina:

- exige resposta HTTP válida e aplica timeout;
- confere o tamanho recebido quando `Content-Length` existe;
- rejeita arquivo vazio e HTML disfarçado de CSV;
- mantém o destino dentro da pasta temporária;
- detecta encoding entre UTF-8, UTF-8 com BOM, Latin-1 e CP1252;
- detecta `;` ou `,` como separador;
- registra linhas, colunas e SHA-256.

Nada é gravado diretamente sobre `dados/01_brutos/` durante o download.

## Critérios de chave e comparação

Os nomes das colunas, espaços e nulos são normalizados apenas em cópias em memória. Os arquivos de entrada permanecem imutáveis.

A chave é escolhida nesta ordem:

1. `id`, se existir, não tiver nulos e for única nos dois arquivos;
2. combinações conhecidas de campos estáveis, incluindo `id + pesid` para a base de pessoas;
3. hash da linha normalizada, como último recurso.

Cada chave é validada quanto a presença, nulos e duplicidade. Se nem o hash de linha for único, a comparação individual é bloqueada com a mensagem: **“Não foi possível identificar registros de forma segura.”** O fallback por hash identifica inclusões e remoções de linhas idênticas, mas uma correção de conteúdo pode aparecer como uma remoção e uma inclusão.

A comparação informa registros novos, alterados, removidos, inalterados, duplicados e sem chave. Para alterações, registra chave, coluna e valores local/remoto, redigindo campos potencialmente sensíveis.

## Relatórios

O relatório Markdown registra URL, ano, tipo, hashes, tamanhos, linhas, chave, formato detectado, contagens e recomendação. Quando há diferenças, são produzidos:

- `relatorios/tabelas/resumo_sincronizacao.csv`;
- `relatorios/tabelas/novas_ocorrencias.csv`;
- `relatorios/tabelas/ocorrencias_alteradas.csv`;
- `relatorios/tabelas/ocorrencias_removidas.csv`.

Arquivos grandes, temporários, logs e backups não são versionados automaticamente.

## CLI

```powershell
.\.venv\Scripts\python.exe -m src.sincronizar_dados_prf --verificar
.\.venv\Scripts\python.exe -m src.sincronizar_dados_prf --baixar-temporario --ano 2025 --tipo ocorrencias
.\.venv\Scripts\python.exe -m src.sincronizar_dados_prf --comparar --ano 2025 --tipo ocorrencias
.\.venv\Scripts\python.exe -m src.sincronizar_dados_prf --aplicar-atualizacao --ano 2025 --tipo ocorrencias --confirmar
```

`--verificar` consulta o catálogo e os metadados. `--baixar-temporario` baixa sem alterar a base. `--comparar` usa o arquivo temporário. `--aplicar-atualizacao` é recusado sem `--confirmar`.

## Confirmação, backup e rollback

Na aplicação confirmada, o arquivo temporário é validado novamente, o arquivo local recebe backup com timestamp, a substituição ocorre por arquivo intermediário e a nova cópia é validada. Qualquer falha após o backup restaura automaticamente a versão anterior. Falha de backup impede a substituição; falha de rollback é reportada explicitamente.

Esta operação nunca deve ser acionada pelo agendamento semanal. Os backups não são excluídos automaticamente.

## Segurança e tratamento de erros

As mensagens operacionais tratam timeout, DNS, HTTP 403/404/429/500, conteúdo incompleto, arquivo vazio, HTML, encoding, schema, duplicidades, ausência de chave, permissão, backup e rollback. A CLI apresenta mensagens controladas sem traceback bruto para erros esperados.

## Agendamento semanal

O agendamento existente continua executando somente `src.verificar_dados_publicos --salvar-relatorio`. Ele consulta e relata; não contém `--aplicar-atualizacao` nem confirmação. O status do manifesto é incorporado ao relatório semanal.

## Limitações

- A página oficial pode mudar seu HTML e exigir adaptação do parser.
- Ausência de cabeçalhos HTTP reduz a detecção preliminar a uma comparação pendente.
- Hash de linha não reconhece uma linha alterada como a mesma entidade.
- A aplicação confirmada substitui um arquivo bruto inteiro; a revisão humana do relatório continua obrigatória.
- A rotina não executa Machine Learning nem transforma os dados tratados automaticamente.
