-- Gold: Top 20 kommuner med høyest andel 55+ (siste år)

CREATE OR REPLACE TABLE gold.top_kommuner_pensjonsalder AS
SELECT
    kommune_code,
    kommune_label,
    year,
    total_befolkning,
    pension_age_befolkning,
    pension_age_share
FROM silver.befolkning_pensjon
WHERE year = (SELECT MAX(year) FROM silver.befolkning_pensjon)
ORDER BY pension_age_share DESC
LIMIT 20;
