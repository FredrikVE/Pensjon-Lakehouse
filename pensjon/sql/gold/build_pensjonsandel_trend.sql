-- Pensjon-Lakehouse/pensjon/sql/gold/build_pensjonsandel_trend.sql
COPY (
    SELECT
        year,
        ROUND(AVG(pension_age_share) * 100, 2) AS snitt_pensjonsandel_pst,
        SUM(pension_age_befolkning) AS total_55_pluss,
        SUM(total_befolkning) AS total_befolkning
    FROM read_parquet('$lake/silver/befolkning_pensjon.parquet')
    GROUP BY year
    ORDER BY year
) TO '$lake/gold/pensjonsandel_trend.parquet'
  (FORMAT PARQUET);
