-- Gold: Aldersgruppe-andeler per år for hele landet

CREATE OR REPLACE TABLE gold.aldersgruppe_trend AS
SELECT
    year,
    aldersgruppe,
    aldersgruppe_sortering,
    SUM(befolkning) AS befolkning,
    ROUND(
        SUM(befolkning)::FLOAT
        / NULLIF(SUM(SUM(befolkning)) OVER (PARTITION BY year), 0),
        4
    ) AS andel
FROM silver.befolkning_aldersgrupper
GROUP BY year, aldersgruppe, aldersgruppe_sortering
ORDER BY year, aldersgruppe_sortering;
