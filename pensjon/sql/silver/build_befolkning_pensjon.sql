-- Silver: Befolkning per kommune med pensjonsandel (55+)
-- Filtrerer bort fylker/land (ikke 4-sifret), null-verdier,
-- og ikke-numeriske aldre.

CREATE OR REPLACE TABLE silver.befolkning_pensjon AS
SELECT
    Region_code  AS kommune_code,
    Region_label AS kommune_label,
    Tid_code     AS year,
    SUM(value)   AS total_befolkning,
    SUM(
        CASE
            WHEN TRY_CAST(split_part(Alder_label, ' ', 1) AS INTEGER) >= 55
            THEN value
            ELSE 0
        END
    ) AS pension_age_befolkning,
    ROUND(
        SUM(
            CASE
                WHEN TRY_CAST(split_part(Alder_label, ' ', 1) AS INTEGER) >= 55
                THEN value
                ELSE 0
            END
        )::FLOAT / NULLIF(SUM(value), 0),
        4
    ) AS pension_age_share,
    CURRENT_TIMESTAMP AS _cleaned_ts
FROM bronze.ssb_befolkning_raw
WHERE LENGTH(Region_code) = 4
  AND value IS NOT NULL
  AND TRY_CAST(split_part(Alder_label, ' ', 1) AS INTEGER) IS NOT NULL
GROUP BY Region_code, Region_label, Tid_code
HAVING SUM(value) > 0
ORDER BY Tid_code, pension_age_share DESC;
