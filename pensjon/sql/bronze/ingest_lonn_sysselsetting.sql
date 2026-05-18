CREATE OR REPLACE TABLE bronze.ssb_lonn_sysselsetting_raw AS
SELECT
    *,
    CURRENT_TIMESTAMP AS _ingest_ts,
    'ssb_11654'        AS _source,
    '$batch_id'        AS _batch_id
FROM raw_lonn_syss_staging;
