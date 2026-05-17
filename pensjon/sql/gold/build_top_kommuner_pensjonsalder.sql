-- /Users/fredrik/Koding/Pensjon-Lakehouse/pensjon/sql/gold/build_top_kommuner_pensjonsalder.sql
COPY (
    SELECT
        kommune_code,
        kommune_label,
        year,
        total_befolkning,
        pension_age_befolkning,
        pension_age_share
    FROM read_parquet('$lake/silver/befolkning_pensjon.parquet')
    WHERE year = (
        SELECT MAX(year)
        FROM read_parquet('$lake/silver/befolkning_pensjon.parquet')
    )
    ORDER BY pension_age_share DESC
    LIMIT 20
) TO '$lake/gold/top_kommuner_pensjonsalder.parquet'
  (FORMAT PARQUET);
