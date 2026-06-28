# Contexto do problema

O problema analítico central do projeto é: **quais fatores estão associados a acidentes com vítimas fatais nas rodovias federais brasileiras?** Para responder a essa pergunta, o projeto cria a variável-alvo `acidente_fatal`, derivada do campo original `mortos`.

Essa variável não é a mesma coisa que a fórmula do índice de risco. A regra é simples: quando `mortos >= 1`, `acidente_fatal = 1`; quando `mortos = 0`, `acidente_fatal = 0`. Assim, `mortos` continua sendo a medida original de óbitos, enquanto `acidente_fatal` indica se a ocorrência pertence ou não ao grupo de acidentes fatais.

Acidentes de trânsito em rodovias federais geram impactos humanos, sociais e econômicos. Além das mortes e feridos, eles afetam famílias, serviços de saúde, logística, deslocamentos e custos públicos.

Analisar esses registros ajuda a transformar uma base grande de dados em informação compreensível. O objetivo não é apontar culpados individualmente, mas observar padrões: onde os acidentes se concentram, em quais horários acontecem com mais frequência, quais causas aparecem mais, quais rodovias acumulam maior volume e quais ocorrências têm maior gravidade.

Neste projeto, os acidentes são avaliados por dimensões como local, UF, município, BR, mês, dia da semana, faixa de horário, causa, tipo de acidente, fase do dia, clima, tipo de pista e gravidade. Essa organização permite comparar volume e severidade, que nem sempre contam a mesma história. Uma UF pode ter muitos acidentes, enquanto outra pode ter menos ocorrências, mas maior proporção de mortes ou feridos graves.

A análise é útil em contexto educacional porque mostra um fluxo completo de dados: coleta, organização, limpeza, modelagem, visualização, interpretação e comunicação dos resultados.
