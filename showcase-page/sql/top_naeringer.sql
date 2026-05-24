SELECT
    naering_label AS naering,
    lonsstakere,
    manedslonn,
    ROUND(estimert_pensjonsvolum / 1e9, 2) AS volum_mrd
FROM ${catalog}.${schema}.naering_pensjonsvolum
WHERE naering_label != 'Alle næringer'
ORDER BY volum_mrd DESC
LIMIT 10
