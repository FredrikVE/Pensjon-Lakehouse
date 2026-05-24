SELECT
    CAST(year AS INT) AS year,
    aldersgruppe,
    aldersgruppe_sortering,
    andel
FROM ${catalog}.${schema}.aldersgruppe_trend
ORDER BY year, aldersgruppe_sortering
