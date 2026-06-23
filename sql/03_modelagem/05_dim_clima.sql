-- PostgreSQL
CREATE TABLE IF NOT EXISTS modelado.dim_clima AS
SELECT DISTINCT condicao_metereologica, fase_dia
FROM tratado.ocorrencias;
