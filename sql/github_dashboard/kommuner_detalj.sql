SELECT
    kommune_label AS kommune,
    total_befolkning AS innbyggere,
    pension_age_befolkning AS innbyggere_55_pluss,
    ROUND(pension_age_share * 100, 1) AS andel_pst
FROM ${catalog}.${schema}.kommuner_pensjonsalder
ORDER BY andel_pst DESC
