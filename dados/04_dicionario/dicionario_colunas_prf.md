# Dicionário de colunas

## Tempo

- `data_inversa`: data do acidente. Permite análises por ano, mês e evolução temporal.
- `dia_semana`: dia da semana informado. Ajuda a comparar dias úteis e finais de semana.
- `horario`: horário registrado da ocorrência.
- `ano`, `mes`, `hora`, `faixa_horario`: colunas derivadas para resumir períodos e facilitar gráficos.

## Localização

- `uf`: unidade federativa onde ocorreu o acidente.
- `municipio`: município registrado.
- `br`: rodovia federal.
- `km`: marco quilométrico aproximado.

## Causa

- `causa_acidente`: causa principal registrada. É uma das colunas mais úteis para entender padrões recorrentes.

## Tipo de acidente

- `tipo_acidente`: descreve a natureza da ocorrência, como colisão, saída de pista, tombamento ou atropelamento.
- `classificacao_acidente`: classificação informada pela base, geralmente associada à severidade.

## Condições da via

- `tipo_pista`: pista simples, dupla ou múltipla.
- `tracado_via`: característica do traçado, como reta, curva ou cruzamento.
- `sentido_via`: sentido registrado da via.
- `uso_solo`: indica presença ou ausência de ocupação urbana nas proximidades.

## Condições ambientais

- `fase_dia`: fase de luminosidade, como dia, noite ou amanhecer.
- `condicao_metereologica`: condição do tempo no momento da ocorrência.

## Gravidade

- `mortos`: total de mortes registradas na ocorrência.
- `feridos_leves`: total de feridos leves.
- `feridos_graves`: total de feridos graves.
- `ilesos`: total de pessoas ilesas.
- `veiculos`: total de veículos envolvidos.
- `total_feridos`: soma de feridos leves e graves.
- `total_vitimas`: soma de mortos, feridos leves e feridos graves.
- `teve_morte`: indica se houve pelo menos uma morte.
- `acidente_grave`: indica se houve morte ou ferido grave.
- `nivel_gravidade`: classifica a ocorrência como sem vítimas, leve, grave ou fatal.

## Pessoas envolvidas

- `tipo_envolvido`: papel do envolvido na ocorrência.
- `estado_fisico`: condição física informada.
- `idade`: idade do envolvido, quando disponível.
- `sexo`: sexo informado na base.

## Colunas derivadas

As colunas derivadas foram criadas para facilitar análise e visualização. Elas não substituem os dados originais; apenas resumem informações importantes de forma mais analítica.
