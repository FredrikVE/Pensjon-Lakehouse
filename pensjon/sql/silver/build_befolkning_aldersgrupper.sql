-- Silver: Befolkning per kommune, år og aldersgruppe
-- Grupper som er relevante for pensjonsanalyse

CREATE OR REPLACE TABLE silver.befolkning_aldersgrupper AS
WITH alder AS (
    SELECT
        Region_code  AS kommune_code,
        Region_label AS kommune_label,
        Tid_code     AS year,
        TRY_CAST(split_part(Alder_label, ' ', 1) AS INTEGER) AS alder,
        value AS antall
    FROM bronze.ssb_befolkning_raw
    WHERE LENGTH(Region_code) = 4
      AND value IS NOT NULL
      AND TRY_CAST(split_part(Alder_label, ' ', 1) AS INTEGER) IS NOT NULL
),

grouped AS (
    SELECT
        kommune_code,
        kommune_label,
        year,
        CASE
            WHEN alder BETWEEN  0 AND 19 THEN '0-19'
            WHEN alder BETWEEN 20 AND 34 THEN '20-34'
            WHEN alder BETWEEN 35 AND 49 THEN '35-49'
            WHEN alder BETWEEN 50 AND 54 THEN '50-54'
            WHEN alder BETWEEN 55 AND 61 THEN '55-61'
            WHEN alder BETWEEN 62 AND 66 THEN '62-66'
            WHEN alder BETWEEN 67 AND 74 THEN '67-74'
            ELSE '75+'
        END AS aldersgruppe,
        CASE
            WHEN alder BETWEEN  0 AND 19 THEN 1
            WHEN alder BETWEEN 20 AND 34 THEN 2
            WHEN alder BETWEEN 35 AND 49 THEN 3
            WHEN alder BETWEEN 50 AND 54 THEN 4
            WHEN alder BETWEEN 55 AND 61 THEN 5
            WHEN alder BETWEEN 62 AND 66 THEN 6
            WHEN alder BETWEEN 67 AND 74 THEN 7
            ELSE 8
        END AS aldersgruppe_sortering,
        SUM(antall) AS befolkning
    FROM alder
    GROUP BY
        kommune_code, kommune_label, year,
        aldersgruppe, aldersgruppe_sortering
)

SELECT
    *,
    ROUND(
        befolkning::FLOAT
        / NULLIF(SUM(befolkning) OVER (PARTITION BY kommune_code, year), 0),
        4
    ) AS aldersgruppe_andel,
    CURRENT_TIMESTAMP AS _cleaned_ts
FROM grouped
ORDER BY year, kommune_label, aldersgruppe_sortering;
