SQL = """
COPY (
    SELECT *,
           CURRENT_TIMESTAMP AS _ingest_ts,
           'ssb_11654' AS _source,
           '$batch_id' AS _batch_id
    FROM raw_lonn_syss
) TO '$lake/bronze/lonn_sysselsetting/data.parquet'
  (FORMAT PARQUET, COMPRESSION ZSTD);
"""
