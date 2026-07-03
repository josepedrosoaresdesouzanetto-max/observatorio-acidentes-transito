# Mapas locais

`brasil_ufs.geojson` contém os polígonos das Unidades Federativas do Brasil usados na aba Visão Geográfica do dashboard.

Fonte pública original: https://github.com/codeforamerica/click_that_hood/blob/master/public/data/brazil-states.geojson

O arquivo local foi simplificado para manter apenas propriedades necessárias (`sigla`, `name`, `id`, `codigo_ibg`) e coordenadas arredondadas, evitando dependência de internet em tempo de execução.
