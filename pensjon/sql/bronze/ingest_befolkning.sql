CREATE OR REPLACE TABLE bronze.ssb_befolkning_raw AS
SELECT
    *,
    CURRENT_TIMESTAMP AS _ingest_ts,
    'ssb_07459'        AS _source,
    '$batch_id'        AS _batch_id
FROM raw_befolkning_staging;
