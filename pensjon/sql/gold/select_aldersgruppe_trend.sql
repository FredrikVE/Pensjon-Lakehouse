-- Pensjon-Lakehouse/pensjon/sql/gold/select_aldersgruppe_trend.sql
SELECT year,
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '0-19'  THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "0-19_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '20-34' THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "20-34_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '35-49' THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "35-49_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '50-54' THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "50-54_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '55-61' THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "55-61_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '62-66' THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "62-66_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '67-74' THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "67-74_%",
    CAST(ROUND(SUM(CASE WHEN aldersgruppe = '75+'   THEN andel ELSE 0 END) * 100, 1) AS DECIMAL(5, 1)) AS "75+_%"
FROM read_parquet('$lake/gold/aldersgruppe_trend.parquet')
GROUP BY year
ORDER BY year;