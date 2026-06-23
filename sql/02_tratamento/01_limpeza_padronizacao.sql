UPDATE tratado.ocorrencias
SET municipio = COALESCE(NULLIF(TRIM(municipio), ''), 'Nao informado'),
    causa_acidente = COALESCE(NULLIF(TRIM(causa_acidente), ''), 'Nao informado'),
    condicao_metereologica = COALESCE(NULLIF(TRIM(condicao_metereologica), ''), 'Nao informado');
