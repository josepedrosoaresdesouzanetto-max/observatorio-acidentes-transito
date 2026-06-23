# Roteiro de apresentação

## Fala sugerida para 5 a 7 minutos

Bom dia. O tema do meu projeto é o **Observatório de Acidentes de Trânsito no Brasil**, com foco em acidentes registrados em rodovias federais brasileiras.

O objetivo foi organizar e analisar dados públicos da Polícia Rodoviária Federal para entender padrões de acidentes. Eu quis responder perguntas como: em quais estados e rodovias há mais registros, quais causas aparecem com mais frequência, em quais horários os acidentes acontecem mais e onde os acidentes são mais graves.

A fonte escolhida foi a PRF porque ela disponibiliza dados públicos e estruturados sobre acidentes em rodovias federais. Esses dados são adequados para um projeto de análise porque têm informações de tempo, local, causa, tipo de acidente, condição meteorológica, características da via e gravidade.

Foram analisados principalmente os anos de 2024, 2025 e 2026. O ano de 2026 foi tratado como parcial, porque ainda está em andamento. Então, ele não deve ser comparado diretamente com anos fechados sem esse cuidado.

As colunas consideradas mais úteis foram data, dia da semana, horário, UF, município, BR, km, causa do acidente, tipo de acidente, fase do dia, condição meteorológica, tipo de pista, traçado da via, mortos, feridos leves, feridos graves, ilesos e veículos. A partir delas, criei colunas derivadas como ano, mês, hora, faixa de horário, final de semana, total de feridos, total de vítimas, acidente grave e nível de gravidade.

No tratamento, os arquivos foram organizados em camadas. Primeiro ficam os dados brutos, depois os dados tratados e por fim os dados modelados. Também foram padronizados nomes de colunas, datas, horários, valores nulos, duplicados e campos numéricos.

Foram gerados gráficos de acidentes por ano, por UF, por faixa de horário, por dia da semana, principais causas, tipos de acidente, condição meteorológica, acidentes graves por UF, ranking de rodovias e índice de risco. O projeto também conta com um dashboard interativo em Streamlit para explorar os filtros, os cards e os rankings de forma visual.

O índice de risco é uma métrica simples criada para fins educacionais. Ele combina quantidade de acidentes e gravidade usando a fórmula: total de acidentes, mais mortos com peso 5, feridos graves com peso 3 e feridos leves com peso 1. Ele não é um indicador oficial, mas ajuda a comparar locais, rodovias e causas de forma transparente.

A principal descoberta do projeto é que volume e gravidade precisam ser analisados juntos. Um local pode ter muitos acidentes, mas outro pode se destacar quando olhamos mortes e feridos graves. Por isso, rankings simples de quantidade não contam toda a história.

As limitações são importantes: 2026 é parcial, os dados dependem da qualidade dos registros disponíveis, a análise cobre o escopo da PRF e os resultados mostram padrões, não causalidade absoluta.

Como próximos passos, eu melhoraria os notebooks com mais saídas executadas, incluiria mais anos históricos quando disponíveis, cruzaria os resultados com dados de frota, população ou fluxo de veículos e refinaria o índice de risco.

Em resumo, o projeto mostra como dados públicos podem ser organizados e analisados para gerar uma visão mais clara sobre acidentes em rodovias federais brasileiras.
