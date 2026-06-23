-- PostgreSQL
-- Exemplos de limpeza depois da carga.

UPDATE tratado.ocorrencias
SET municipio = COALESCE(NULLIF(TRIM(municipio), ''), 'Não informado'),
    causa_acidente = COALESCE(NULLIF(TRIM(causa_acidente), ''), 'Não informado'),
    tipo_acidente = COALESCE(NULLIF(TRIM(tipo_acidente), ''), 'Não informado'),
    condicao_metereologica = COALESCE(NULLIF(TRIM(condicao_metereologica), ''), 'Não informado');

UPDATE tratado.ocorrencias
SET mortos = COALESCE(mortos, 0),
    feridos_leves = COALESCE(feridos_leves, 0),
    feridos_graves = COALESCE(feridos_graves, 0),
    ilesos = COALESCE(ilesos, 0),
    veiculos = COALESCE(veiculos, 0);
