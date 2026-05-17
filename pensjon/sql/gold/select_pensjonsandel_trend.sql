-- Pensjon-Lakehouse/pensjon/sql/gold/select_pensjonsandel_trend.sql

SELECT * FROM read_parquet('$lake/gold/pensjonsandel_trend.parquet');
