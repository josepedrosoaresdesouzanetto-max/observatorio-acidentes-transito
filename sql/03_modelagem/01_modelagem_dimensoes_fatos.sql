CREATE TABLE modelado.dim_tempo AS
SELECT DISTINCT data_inversa, ano, mes, dia_semana, hora, faixa_horario, final_de_semana
FROM tratado.ocorrencias;

CREATE TABLE modelado.dim_local AS
SELECT DISTINCT uf, municipio
FROM tratado.ocorrencias;

CREATE TABLE modelado.dim_rodovia AS
SELECT DISTINCT br, km, tipo_pista, tracado_via
FROM tratado.ocorrencias;

CREATE TABLE modelado.dim_causa AS
SELECT DISTINCT causa_acidente, tipo_acidente, classificacao_acidente
FROM tratado.ocorrencias;

CREATE TABLE modelado.dim_clima AS
SELECT DISTINCT condicao_metereologica, fase_dia
FROM tratado.ocorrencias;

CREATE TABLE modelado.fato_acidentes AS
SELECT * FROM tratado.ocorrencias;
