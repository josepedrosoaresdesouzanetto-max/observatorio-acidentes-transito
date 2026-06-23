-- PostgreSQL
CREATE TABLE IF NOT EXISTS modelado.dim_tempo AS
SELECT DISTINCT data_inversa, ano, mes, dia_semana, hora, faixa_horario, final_de_semana
FROM tratado.ocorrencias;
