-- Gold: Pensjonsandel-trend (vektet landsgjennomsnitt)
--
-- VIKTIG: Bruker SUM(55+) / SUM(total), IKKE AVG(andel).
-- Et uvektet kommunesnitt ville gitt feil bilde fordi
-- små kommuner ville veid like mye som store.

CREATE OR REPLACE TABLE gold.pensjonsandel_trend AS
SELECT
    year,
    SUM(pension_age_befolkning) AS total_55_pluss,
    SUM(total_befolkning)       AS total_befolkning,
    ROUND(
        SUM(pension_age_befolkning)::FLOAT
        / NULLIF(SUM(total_befolkning), 0)
        * 100,
        2
    ) AS pensjonsandel_pst
FROM silver.befolkning_pensjon
GROUP BY year
ORDER BY year;
