-- PostgreSQL
CREATE TABLE IF NOT EXISTS modelado.dim_causa AS
SELECT DISTINCT causa_acidente, tipo_acidente, classificacao_acidente
FROM tratado.ocorrencias;
