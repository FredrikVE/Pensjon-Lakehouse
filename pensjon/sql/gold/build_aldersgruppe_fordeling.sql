-- Gold: Aldersgruppe-fordeling for hele landet, siste år

CREATE OR REPLACE TABLE gold.aldersgruppe_fordeling AS
SELECT
    aldersgruppe,
    aldersgruppe_sortering,
    SUM(befolkning) AS befolkning,
    ROUND(
        SUM(befolkning)::FLOAT
        / NULLIF(SUM(SUM(befolkning)) OVER (), 0),
        4
    ) AS andel
FROM silver.befolkning_aldersgrupper
WHERE year = (SELECT MAX(year) FROM silver.befolkning_aldersgrupper)
GROUP BY aldersgruppe, aldersgruppe_sortering
ORDER BY aldersgruppe_sortering;
