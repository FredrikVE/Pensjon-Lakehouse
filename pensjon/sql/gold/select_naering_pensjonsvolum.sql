-- Pensjon-Lakehouse/pensjon/sql/gold/select_naering_pensjonsvolum.py
SELECT
    naering_label AS næring,
    lonsstakere AS lønnstakere,
    manedslonn AS "mnd.lønn",
    estimert_pensjonsvolum AS "est.volum"
FROM read_parquet('$lake/gold/naering_pensjonsvolum.parquet')
LIMIT 10;
