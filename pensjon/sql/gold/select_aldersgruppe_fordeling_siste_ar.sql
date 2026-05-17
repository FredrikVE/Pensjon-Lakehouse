-- Pensjon-Lakehouse/pensjon/sql/gold/select_aldersgruppe_fordeling_siste_ar.sql
SELECT aldersgruppe, befolkning,
    CAST(ROUND(andel * 100, 1) AS DECIMAL(5, 1)) AS "andel_%"
    FROM read_parquet('$lake/gold/aldersgruppe_fordeling_siste_ar.parquet')

ORDER BY aldersgruppe_sortering;