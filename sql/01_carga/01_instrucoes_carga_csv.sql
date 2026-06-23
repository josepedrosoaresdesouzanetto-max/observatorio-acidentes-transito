-- PostgreSQL
-- Instruções de carga dos CSVs tratados.
-- Antes de executar, gere os arquivos com:
-- python -m src.limpar_dados
--
-- Ajuste os caminhos absolutos conforme a sua máquina, pois o PostgreSQL precisa
-- conseguir ler os arquivos a partir do servidor.

-- Exemplo:
-- COPY tratado.ocorrencias
-- FROM 'C:/caminho/observatorio-acidentes-transito/dados/02_tratados/ocorrencias_tratadas.csv'
-- WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');

-- COPY tratado.pessoas
-- FROM 'C:/caminho/observatorio-acidentes-transito/dados/02_tratados/pessoas_tratadas.csv'
-- WITH (FORMAT csv, HEADER true, DELIMITER ';', ENCODING 'UTF8');
