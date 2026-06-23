-- PostgreSQL
-- Índice educacional: total_acidentes + mortos*5 + feridos_graves*3 + feridos_leves.

CREATE OR REPLACE VIEW modelado.vw_indice_risco_uf AS
SELECT uf,
       COUNT(*) AS total_acidentes,
       SUM(mortos) AS mortos,
       SUM(feridos_graves) AS feridos_graves,
       SUM(feridos_leves) AS feridos_leves,
       COUNT(*) + SUM(mortos) * 5 + SUM(feridos_graves) * 3 + SUM(feridos_leves) AS indice_risco
FROM tratado.ocorrencias
GROUP BY uf;

CREATE OR REPLACE VIEW modelado.vw_indice_risco_br AS
SELECT br,
       COUNT(*) AS total_acidentes,
       SUM(mortos) AS mortos,
       SUM(feridos_graves) AS feridos_graves,
       SUM(feridos_leves) AS feridos_leves,
       COUNT(*) + SUM(mortos) * 5 + SUM(feridos_graves) * 3 + SUM(feridos_leves) AS indice_risco
FROM tratado.ocorrencias
GROUP BY br;

CREATE OR REPLACE VIEW modelado.vw_indice_risco_causa AS
SELECT causa_acidente,
       COUNT(*) AS total_acidentes,
       SUM(mortos) AS mortos,
       SUM(feridos_graves) AS feridos_graves,
       SUM(feridos_leves) AS feridos_leves,
       COUNT(*) + SUM(mortos) * 5 + SUM(feridos_graves) * 3 + SUM(feridos_leves) AS indice_risco
FROM tratado.ocorrencias
GROUP BY causa_acidente;
