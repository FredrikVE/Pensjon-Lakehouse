SQL = """
COPY (
    SELECT *,
           CURRENT_TIMESTAMP AS _ingest_ts,
           'ssb_07459' AS _source,
           '$batch_id' AS _batch_id
    FROM raw_befolkning
) TO '$lake/bronze/befolkning/data.parquet'
  (FORMAT PARQUET, COMPRESSION ZSTD);
"""
