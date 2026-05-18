-- Eksporter Gold-tabeller til Parquet for deling/BI/Azure

COPY gold.top_kommuner_pensjonsalder
  TO '$export_path/gold/top_kommuner_pensjonsalder.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

COPY gold.pensjonsandel_trend
  TO '$export_path/gold/pensjonsandel_trend.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

COPY gold.naering_pensjonsvolum
  TO '$export_path/gold/naering_pensjonsvolum.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

COPY gold.aldersgruppe_fordeling
  TO '$export_path/gold/aldersgruppe_fordeling.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

COPY gold.aldersgruppe_trend
  TO '$export_path/gold/aldersgruppe_trend.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
