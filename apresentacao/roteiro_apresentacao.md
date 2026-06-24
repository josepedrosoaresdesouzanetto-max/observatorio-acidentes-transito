# Observatório de Acidentes de Trânsito no Brasil

## Roteiro de apresentação

Bom dia, pessoal. Meu projeto se chama **Observatório de Acidentes de Trânsito no Brasil**.

A ideia dele foi pegar dados públicos da Polícia Rodoviária Federal, organizar esses dados e transformar tudo em uma análise mais fácil de entender. Em vez de olhar só para uma planilha grande, cheia de colunas e milhares de linhas, eu quis construir um projeto que mostrasse padrões: onde acontecem mais acidentes, quais causas aparecem mais, quais rodovias se destacam e onde os casos parecem mais graves.

Eu escolhi esse tema porque trânsito é um assunto muito presente no Brasil. Todo mundo conhece alguma estrada perigosa, algum trecho complicado ou já ouviu notícias sobre acidentes em rodovias. Então, trabalhar com esses dados faz sentido não só como exercício técnico, mas também como uma forma de entender melhor um problema real.

A fonte dos dados foi a PRF, que disponibiliza bases públicas sobre acidentes em rodovias federais. Essas bases trazem informações como data, horário, estado, município, BR, causa do acidente, tipo de acidente, clima, fase do dia e também dados de gravidade, como mortos, feridos leves e feridos graves.

No projeto, eu trabalhei principalmente com os anos de **2024, 2025 e 2026**. Um ponto importante é que **2026 ainda é um ano parcial**, então ele não pode ser comparado diretamente com anos fechados como se tivesse o mesmo peso. Eu deixei isso sinalizado no README, na documentação, no relatório e no dashboard para evitar uma interpretação errada.

Antes da análise, foi preciso organizar os dados. Eu separei o projeto em camadas: primeiro os dados brutos, depois os dados tratados e depois os dados modelados. Na limpeza, eu padronizei nomes de colunas, tratei datas e horários, organizei valores nulos, removi duplicidades quando necessário e criei algumas colunas novas que ajudam na análise.

Por exemplo, a partir da data e do horário eu criei informações como ano, mês, hora e faixa de horário. Também criei campos como total de vítimas, total de feridos e uma marcação de acidente grave. Isso facilita muito porque, depois do tratamento, a análise fica mais direta.

Depois dessa etapa, eu gerei gráficos e tabelas para responder algumas perguntas principais. Uma delas é: quais estados concentram mais acidentes? Outra é: quais causas aparecem com mais frequência? Também olhei para horários, dias da semana, condição meteorológica, tipos de acidente e ranking de rodovias.

Uma parte importante do projeto foi o **índice de risco**. Ele não é uma previsão oficial e também não é um indicador do governo. É uma métrica educacional, criada para combinar volume de acidentes com gravidade. A lógica é simples: acidentes contam com peso 1, mortes têm peso 5, feridos graves têm peso 3 e feridos leves têm peso 1.

Com isso, dá para perceber uma coisa importante: nem sempre o local com mais acidentes é o local mais crítico quando olhamos gravidade. Às vezes um trecho ou uma causa pode ter menos registros, mas apresentar mais mortes ou feridos graves. Então o índice ajuda a olhar além da quantidade bruta.

Nesse ponto eu também criei um dashboard em Streamlit. A ideia do dashboard é permitir que a análise seja explorada de forma interativa. Ele tem filtros por ano, UF, BR, causa, tipo de acidente, fase do dia, condição meteorológica e faixa de horário.

Na primeira parte do dashboard aparecem cards com indicadores gerais, como total de acidentes, mortos, feridos graves, feridos leves, vítimas, acidentes graves e percentual de acidentes graves. Depois, nas abas, dá para navegar por visão geral, perfil dos acidentes, gravidade, rodovias e locais críticos, e índice de risco.

Se eu estivesse apresentando com o dashboard aberto, aqui eu mostraria rapidamente os filtros e explicaria que, quando nenhum filtro está selecionado, o painel considera todos os dados. Depois eu escolheria um ano ou uma UF para mostrar como os gráficos mudam. Isso deixa a apresentação mais visual e ajuda a mostrar que o projeto não é só um relatório estático.

O principal aprendizado do projeto foi perceber que análise de dados não é só gerar gráfico. A parte mais trabalhosa é organizar a base, entender as colunas, tomar cuidado com dados parciais e explicar as limitações. No caso desse projeto, a limitação mais importante é o ano de 2026, porque ele ainda não está completo.

Também é importante lembrar que os dados mostram padrões, mas não provam causalidade sozinhos. Se uma causa aparece muito, isso não significa automaticamente que ela explica tudo. Para uma análise mais profunda, seria interessante cruzar os dados com frota de veículos, população, fluxo nas rodovias ou características de infraestrutura.

Como próximos passos, eu melhoraria os notebooks com mais saídas executadas, adicionaria mais anos históricos quando estiverem disponíveis e refinaria o índice de risco. Também daria para evoluir o dashboard com mais comparativos e talvez mapas.

Para concluir, esse projeto mostra como dados públicos podem ser tratados e transformados em informação útil. Ele organiza uma base grande, cria análises, gera gráficos, monta um relatório e entrega um dashboard interativo. Mais do que apontar um único resultado, ele ajuda a enxergar melhor o comportamento dos acidentes em rodovias federais brasileiras.
