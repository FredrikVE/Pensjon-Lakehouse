#Pensjon-Lakehouse/pensjon/lakehouse/stages/silver_stage.py
import duckdb

from pensjon.lakehouse.config import LakehouseConfig
from pensjon.sql_loader import load_sql

class SilverStage:
    def __init__(self, db: duckdb.DuckDBPyConnection, config: LakehouseConfig):
        self.db = db
        self.config = config
        self.lake = config.lake_path

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  SILVER – Rensing og kobling")
        print("─" * 64)

        self._build_befolkning_pensjon()
        self._build_befolkning_aldersgrupper()
        self._build_naering_pensjon()

    def _build_befolkning_pensjon(self) -> None:
        self.db.execute(
            load_sql(
                "silver/build_befolkning_pensjon.sql",
                lake=self.lake,
            )
        )

        count = self._count_parquet("silver/befolkning_pensjon.parquet")
        print(f"  ✓ Befolkning pensjonsandel: {count} rader (kommune × år)")

    def _build_naering_pensjon(self) -> None:
        self.db.execute(
            load_sql(
                "silver/build_naering_pensjon.sql",
                lake=self.lake,
            )
        )

        count = self._count_parquet("silver/naering_pensjon.parquet")
        print(f"  ✓ Næring pensjonsvolum: {count} rader")

    def _build_befolkning_aldersgrupper(self) -> None:
        self.db.execute(
            load_sql(
                "silver/build_befolkning_aldersgrupper.sql",
                lake=self.lake,
            )
        )

        count = self._count_parquet("silver/befolkning_aldersgrupper.parquet")
        print(f"  ✓ Befolkning aldersgrupper: {count} rader")

    def _count_parquet(self, relative_path: str) -> int:
        parquet_path = self.lake / relative_path

        return self.db.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')").fetchone()[0]