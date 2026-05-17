-- Pensjon-Lakehouse/pensjon/sql/gold/build_aldersgruppe_fordeling_siste_ar.sql
COPY (
    SELECT
        aldersgruppe,
        aldersgruppe_sortering,
        SUM(befolkning) AS befolkning,
        ROUND(
            SUM(befolkning)::FLOAT
            / NULLIF(
                SUM(SUM(befolkning)) OVER (),
                0
            ),
            4
        ) AS andel
    FROM read_parquet('$lake/silver/befolkning_aldersgrupper.parquet')
    WHERE year = (
        SELECT MAX(year)
        FROM read_parquet('$lake/silver/befolkning_aldersgrupper.parquet')
    )
    GROUP BY
        aldersgruppe,
        aldersgruppe_sortering
    ORDER BY aldersgruppe_sortering
) TO '$lake/gold/aldersgruppe_fordeling_siste_ar.parquet'
  (FORMAT PARQUET);