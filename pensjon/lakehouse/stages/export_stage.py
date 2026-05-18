"""
Export Stage: Eksporterer Gold-tabeller til Parquet-filer.

Parquet brukes for deling, BI-verktøy og eventuell
opplasting til Azure Data Lake Storage Gen2.
"""

from pathlib import Path

import duckdb

from pensjon.lakehouse.config import LakehouseConfig


class ExportStage:
    def __init__(self, db: duckdb.DuckDBPyConnection, config: LakehouseConfig):
        self.db = db
        self.config = config

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  EXPORT – Parquet-filer for BI/Azure")
        print("─" * 64)

        export_path = self.config.export_path / "gold"
        export_path.mkdir(parents=True, exist_ok=True)

        tables = [
            "top_kommuner_pensjonsalder",
            "pensjonsandel_trend",
            "naering_pensjonsvolum",
            "aldersgruppe_fordeling",
            "aldersgruppe_trend",
        ]

        for table in tables:
            parquet_path = export_path / f"{table}.parquet"
            self.db.execute(
                f"COPY gold.{table} TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            print(f"  ✓ {parquet_path}")

        print(f"\n  ✓ {len(tables)} Parquet-filer eksportert")
