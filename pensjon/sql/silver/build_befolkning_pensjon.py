SQL = """
COPY (
    SELECT
        kommune_code,
        kommune_label,
        year,
        SUM(antall) AS total_befolkning,
        SUM(CASE
            WHEN CAST(split_part(alder_label, ' ', 1) AS INTEGER) >= 55
            THEN antall ELSE 0
        END) AS pension_age_befolkning,
        ROUND(
            SUM(CASE
                WHEN CAST(split_part(alder_label, ' ', 1) AS INTEGER) >= 55
                THEN antall ELSE 0
            END)::FLOAT / NULLIF(SUM(antall), 0), 4
        ) AS pension_age_share,
        CURRENT_TIMESTAMP AS _cleaned_ts
    FROM read_parquet('$lake/bronze/befolkning/data.parquet')
    GROUP BY kommune_code, kommune_label, year
    HAVING SUM(antall) > 0
    ORDER BY year, pension_age_share DESC
) TO '$lake/silver/befolkning_pensjon.parquet'
  (FORMAT PARQUET, COMPRESSION ZSTD);
"""
