SQL = """
COPY (
    SELECT
        naering_code,
        naering_label,
        kvartal,
        lonsstakere,
        manedslonn,
        estimert_pensjonsvolum
    FROM read_parquet('$lake/silver/naering_pensjon.parquet')
    WHERE kvartal = (
        SELECT MAX(kvartal)
        FROM read_parquet('$lake/silver/naering_pensjon.parquet')
    )
    AND estimert_pensjonsvolum IS NOT NULL
    ORDER BY estimert_pensjonsvolum DESC
) TO '$lake/gold/naering_pensjonsvolum.parquet'
  (FORMAT PARQUET);
"""
