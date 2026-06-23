-- PostgreSQL
CREATE TABLE IF NOT EXISTS modelado.dim_local AS
SELECT DISTINCT uf, municipio
FROM tratado.ocorrencias;
