SELECT
    CAST(year AS INT) AS year,
    pensjonsandel_pst,
    total_55_pluss,
    total_befolkning
FROM ${catalog}.${schema}.pensjonsandel_trend
ORDER BY year DESC
LIMIT 1
