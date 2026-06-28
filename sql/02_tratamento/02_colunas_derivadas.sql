-- PostgreSQL
-- Exemplo de criação de colunas derivadas em uma consulta.

SELECT
    *,
    EXTRACT(YEAR FROM data_inversa)::INT AS ano_calc,
    EXTRACT(MONTH FROM data_inversa)::INT AS mes_calc,
    EXTRACT(HOUR FROM horario::TIME)::INT AS hora_calc,
    CASE
        WHEN EXTRACT(HOUR FROM horario::TIME) BETWEEN 0 AND 5 THEN 'Madrugada'
        WHEN EXTRACT(HOUR FROM horario::TIME) BETWEEN 6 AND 11 THEN 'Manhã'
        WHEN EXTRACT(HOUR FROM horario::TIME) BETWEEN 12 AND 17 THEN 'Tarde'
        ELSE 'Noite'
    END AS faixa_horario_calc,
    feridos_leves + feridos_graves AS total_feridos_calc,
    mortos + feridos_leves + feridos_graves AS total_vitimas_calc,
    CASE WHEN mortos >= 1 THEN 1 ELSE 0 END AS acidente_fatal_calc,
    CASE WHEN mortos > 0 OR feridos_graves > 0 THEN 'Sim' ELSE 'Não' END AS acidente_grave_calc
FROM tratado.ocorrencias;
