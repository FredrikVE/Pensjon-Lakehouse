-- Pensjon-Lakehouse/pensjon/sql/gold/build_aldersfordeling_siste_ar.sql
COPY (
    WITH alder AS (
        SELECT
            year,
            CAST(split_part(alder_label, ' ', 1) AS INTEGER) AS alder,
            antall
        FROM read_parquet('$lake/bronze/befolkning/data.parquet')
    ),

    siste_ar AS (
        SELECT MAX(year) AS year
        FROM alder
    ),

    aggregated AS (
        SELECT
            alder.year,
            alder.alder,
            SUM(alder.antall) AS befolkning
        FROM alder
        JOIN siste_ar
            ON alder.year = siste_ar.year
        GROUP BY
            alder.year,
            alder.alder
    )

    SELECT
        year,
        alder,
        befolkning,
        ROUND(
            befolkning::FLOAT
            / NULLIF(SUM(befolkning) OVER (), 0),
            6
        ) AS andel
    FROM aggregated
    ORDER BY alder
) TO '$lake/gold/aldersfordeling_siste_ar.parquet'
  (FORMAT PARQUET);