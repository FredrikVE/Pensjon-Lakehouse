-- Gold: Næringer med størst estimert pensjonsvolum (siste kvartal)

CREATE OR REPLACE TABLE gold.naering_pensjonsvolum AS
SELECT
    naering_code,
    naering_label,
    kvartal,
    lonsstakere,
    manedslonn,
    estimert_pensjonsvolum
FROM silver.naering_pensjon
WHERE kvartal = (SELECT MAX(kvartal) FROM silver.naering_pensjon)
  AND estimert_pensjonsvolum IS NOT NULL
ORDER BY estimert_pensjonsvolum DESC;
