-- PostgreSQL

-- Datas nulas
SELECT COUNT(*) AS datas_nulas
FROM tratado.ocorrencias
WHERE data_inversa IS NULL;

-- Duplicados por id
SELECT id, COUNT(*) AS total
FROM tratado.ocorrencias
GROUP BY id
HAVING COUNT(*) > 1;

-- Datas inválidas/futuras
SELECT COUNT(*) AS datas_futuras
FROM tratado.ocorrencias
WHERE data_inversa > CURRENT_DATE;

-- Valores negativos
SELECT COUNT(*) AS valores_negativos
FROM tratado.ocorrencias
WHERE mortos < 0
   OR feridos_leves < 0
   OR feridos_graves < 0
   OR ilesos < 0
   OR veiculos < 0;

-- Total de feridos inconsistente
SELECT COUNT(*) AS total_feridos_inconsistente
FROM tratado.ocorrencias
WHERE total_feridos <> feridos_leves + feridos_graves;

-- Total de vítimas inconsistente
SELECT COUNT(*) AS total_vitimas_inconsistente
FROM tratado.ocorrencias
WHERE total_vitimas <> mortos + feridos_leves + feridos_graves;
