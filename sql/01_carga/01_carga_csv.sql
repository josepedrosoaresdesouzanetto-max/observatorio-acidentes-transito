-- Exemplo PostgreSQL. Ajuste o caminho local conforme necessario.
COPY tratado.ocorrencias
FROM 'dados/02_tratados/ocorrencias_tratadas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');
