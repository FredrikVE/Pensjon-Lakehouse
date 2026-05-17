SQL = """
COPY (
    SELECT
        naering_code,
        naering_label,
        kvartal,
        lonsstakere,
        manedslonn,
        ROUND(lonsstakere * COALESCE(manedslonn, 0) * 12 * 0.02) AS estimert_pensjonsvolum,
        CURRENT_TIMESTAMP AS _cleaned_ts
    FROM read_parquet('$lake/bronze/lonn_sysselsetting/data.parquet')
    WHERE lonsstakere IS NOT NULL
    ORDER BY estimert_pensjonsvolum DESC NULLS LAST
) TO '$lake/silver/naering_pensjon.parquet'
  (FORMAT PARQUET, COMPRESSION ZSTD);
"""
