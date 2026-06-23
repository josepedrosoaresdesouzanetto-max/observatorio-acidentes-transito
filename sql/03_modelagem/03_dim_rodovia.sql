-- PostgreSQL
CREATE TABLE IF NOT EXISTS modelado.dim_rodovia AS
SELECT DISTINCT br, km, tipo_pista, tracado_via
FROM tratado.ocorrencias;
