-- Pensjon-Lakehouse/pensjon/sql/gold/select_top_kommuner.py
SELECT
    kommune_label AS kommune,
    total_befolkning AS innbyggere,
    pension_age_befolkning AS "55+",
    CAST(ROUND(pension_age_share * 100, 1) AS DECIMAL(5, 1)) AS "andel_%"
FROM read_parquet('$lake/gold/top_kommuner_pensjonsalder.parquet')
LIMIT 10;