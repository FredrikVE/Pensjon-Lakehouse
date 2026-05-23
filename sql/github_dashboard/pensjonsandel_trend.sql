SELECT
    CAST(year AS INT) AS year,
    pensjonsandel_pst
FROM ${catalog}.${schema}.pensjonsandel_trend
ORDER BY year
