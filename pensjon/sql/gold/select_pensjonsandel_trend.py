SQL = """
SELECT *
FROM read_parquet('$lake/gold/pensjonsandel_trend.parquet');
"""
