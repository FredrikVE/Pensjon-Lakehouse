-- Pensjon-Lakehouse/pensjon/sql/gold/build_aldersgruppe_trend.sql

COPY (
    SELECT
        year,
        aldersgruppe,
        aldersgruppe_sortering,
        SUM(befolkning) AS befolkning,
        ROUND(
            SUM(befolkning)::FLOAT
            / NULLIF(
                SUM(SUM(befolkning)) OVER (
                    PARTITION BY year
                ),
                0
            ),
            4
        ) AS andel
    FROM read_parquet('$lake/silver/befolkning_aldersgrupper.parquet')
    GROUP BY
        year,
        aldersgruppe,
        aldersgruppe_sortering
    ORDER BY
        year,
        aldersgruppe_sortering
) TO '$lake/gold/aldersgruppe_trend.parquet'
  (FORMAT PARQUET);