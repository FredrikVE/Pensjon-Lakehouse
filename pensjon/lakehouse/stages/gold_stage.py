"""
Gold Stage: Forretningsklare analysetabeller.

Leser fra silver-schema, skriver til gold-schema.
Disse tabellene er klare for dashboard og rapportering.
"""

import duckdb

from pensjon.sql_loader import load_sql


class GoldStage:
    def __init__(self, db: duckdb.DuckDBPyConnection):
        self.db = db

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  GOLD – Forretningsklare analyser")
        print("─" * 64)

        self._build("gold/build_top_kommuner.sql", "gold.top_kommuner_pensjonsalder")
        self._build("gold/build_pensjonsandel_trend.sql", "gold.pensjonsandel_trend")
        self._build("gold/build_naering_pensjonsvolum.sql", "gold.naering_pensjonsvolum")
        self._build("gold/build_aldersgruppe_fordeling.sql", "gold.aldersgruppe_fordeling")
        self._build("gold/build_aldersgruppe_trend.sql", "gold.aldersgruppe_trend")

    def _build(self, sql_file: str, table_name: str) -> None:
        self.db.execute(load_sql(sql_file))
        count = self.db.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  ✓ {table_name}: {count} rader")
