-- Silver: Lønn og sysselsetting per næring
-- Pivoter ContentsCode slik at hver rad har både antall og lønn.
-- Beregn estimert pensjonsvolum: lønnstakere × månedslønn × 12 × 2% OTP.

CREATE OR REPLACE TABLE silver.naering_pensjon AS
WITH pivoted AS (
    SELECT
        NACE2007_code  AS naering_code,
        NACE2007_label AS naering_label,
        Tid_code       AS kvartal,
        MAX(CASE WHEN ContentsCode_code = 'Lonsstakere' THEN value END) AS lonsstakere,
        MAX(CASE WHEN ContentsCode_code = 'GjMdTotal'   THEN value END) AS manedslonn
    FROM bronze.ssb_lonn_sysselsetting_raw
    WHERE value IS NOT NULL
    GROUP BY NACE2007_code, NACE2007_label, Tid_code
)

SELECT
    naering_code,
    naering_label,
    kvartal,
    CAST(lonsstakere AS INTEGER) AS lonsstakere,
    CAST(manedslonn AS INTEGER)  AS manedslonn,
    ROUND(lonsstakere * COALESCE(manedslonn, 0) * 12 * 0.02) AS estimert_pensjonsvolum,
    CURRENT_TIMESTAMP AS _cleaned_ts
FROM pivoted
WHERE lonsstakere IS NOT NULL
ORDER BY estimert_pensjonsvolum DESC NULLS LAST;
