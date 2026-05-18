"""
Silver Stage: Rensing, filtrering og kobling.

Leser fra bronze-schema, skriver til silver-schema.
All transformasjonslogikk er i SQL-filer.
"""

import duckdb

from pensjon.sql_loader import load_sql


class SilverStage:
    def __init__(self, db: duckdb.DuckDBPyConnection):
        self.db = db

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  SILVER – Rensing og kobling")
        print("─" * 64)

        self._build("silver/build_befolkning_pensjon.sql", "silver.befolkning_pensjon")
        self._build("silver/build_befolkning_aldersgrupper.sql", "silver.befolkning_aldersgrupper")
        self._build("silver/build_naering_pensjon.sql", "silver.naering_pensjon")

    def _build(self, sql_file: str, table_name: str) -> None:
        self.db.execute(load_sql(sql_file))
        count = self.db.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  ✓ {table_name}: {count} rader")
