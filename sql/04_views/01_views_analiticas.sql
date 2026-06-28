-- PostgreSQL

CREATE OR REPLACE VIEW modelado.vw_acidentes_por_ano AS
SELECT ano,
       COUNT(*) AS total_acidentes,
       SUM(acidente_fatal) AS acidentes_fatais,
       ROUND(SUM(acidente_fatal)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS percentual_fatalidade,
       SUM(mortos) AS mortos,
       SUM(feridos_graves) AS feridos_graves
FROM tratado.ocorrencias
GROUP BY ano;

CREATE OR REPLACE VIEW modelado.vw_acidentes_por_uf AS
SELECT uf,
       COUNT(*) AS total_acidentes,
       SUM(acidente_fatal) AS acidentes_fatais,
       ROUND(SUM(acidente_fatal)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS percentual_fatalidade,
       SUM(mortos) AS mortos,
       SUM(feridos_graves) AS feridos_graves
FROM tratado.ocorrencias
GROUP BY uf;

CREATE OR REPLACE VIEW modelado.vw_acidentes_por_br AS
SELECT br,
       COUNT(*) AS total_acidentes,
       SUM(acidente_fatal) AS acidentes_fatais,
       ROUND(SUM(acidente_fatal)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS percentual_fatalidade,
       SUM(mortos) AS mortos,
       SUM(feridos_graves) AS feridos_graves
FROM tratado.ocorrencias
GROUP BY br;

CREATE OR REPLACE VIEW modelado.vw_acidentes_por_horario AS
SELECT faixa_horario, COUNT(*) AS total_acidentes
FROM tratado.ocorrencias
GROUP BY faixa_horario;

CREATE OR REPLACE VIEW modelado.vw_causas_mais_comuns AS
SELECT causa_acidente, COUNT(*) AS total_acidentes
FROM tratado.ocorrencias
GROUP BY causa_acidente
ORDER BY total_acidentes DESC;

CREATE OR REPLACE VIEW modelado.vw_acidentes_graves AS
SELECT *
FROM tratado.ocorrencias
WHERE acidente_grave = 'Sim';

CREATE OR REPLACE VIEW modelado.vw_comparativo_anual AS
SELECT ano,
       COUNT(*) AS total_acidentes,
       SUM(acidente_fatal) AS acidentes_fatais,
       ROUND(SUM(acidente_fatal)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS percentual_fatalidade,
       SUM(mortos) AS mortos,
       SUM(total_vitimas) AS total_vitimas
FROM tratado.ocorrencias
GROUP BY ano
ORDER BY ano;
