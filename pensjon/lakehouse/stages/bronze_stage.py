#Pensjon-Lakehouse/pensjon/lakehouse/stages/bronze_stage.py
from datetime import datetime

import duckdb
import pandas as pd

from pensjon.di.dependencies import Dependencies
from pensjon.lakehouse.audit_writer import AuditWriter
from pensjon.lakehouse.config import LakehouseConfig
from pensjon.sql_loader import load_sql


class BronzeStage:
    def __init__(
        self,
        deps: Dependencies,
        db: duckdb.DuckDBPyConnection,
        config: LakehouseConfig,
    ):
        self.deps = deps
        self.db = db
        self.config = config
        self.lake = config.lake_path

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  BRONZE – Henter data fra SSB")
        print("─" * 64)

        batch_id = self._new_batch_id()

        bef_count = self._ingest_befolkning(batch_id)
        ls_count = self._ingest_lonn_sysselsetting(batch_id)

        AuditWriter(self.config).write_bronze_audit(
            batch_id=batch_id,
            bef_count=bef_count,
            ls_count=ls_count,
        )

        print(f"\n  ✓ Batch: {batch_id}")
        print(f"  ✓ Totalt: {bef_count + ls_count} rader i Bronze")

    def _ingest_befolkning(self, batch_id: str) -> int:
        print("\n  Henter befolkningsdata (tabell 07459)...")

        befolkning = self.deps.befolkning_repo.get_befolkning_by_kommune()
        df_bef = pd.DataFrame(befolkning)

        self.db.execute(
            "CREATE OR REPLACE TABLE raw_befolkning AS SELECT * FROM df_bef"
        )

        self.db.execute(
            load_sql(
                "bronze/copy_befolkning_to_bronze.sql",
                lake=self.lake,
                batch_id=batch_id,
            )
        )

        count = self._count_table("raw_befolkning")

        print(f"  ✓ Befolkning: {count} rader")

        return count

    def _ingest_lonn_sysselsetting(self, batch_id: str) -> int:
        print("  Henter lønn/sysselsetting (tabell 11654)...")

        lonn_syss = self.deps.lonn_syss_repo.get_per_naering()
        df_ls = pd.DataFrame(lonn_syss)

        self.db.execute(
            "CREATE OR REPLACE TABLE raw_lonn_syss AS SELECT * FROM df_ls"
        )

        self.db.execute(
            load_sql(
                "bronze/copy_lonn_syss_to_bronze.sql",
                lake=self.lake,
                batch_id=batch_id,
            )
        )

        count = self._count_table("raw_lonn_syss")

        print(f"  ✓ Lønn/sysselsetting: {count} rader")

        return count

    def _count_table(self, table_name: str) -> int:
        return self.db.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

    def _new_batch_id(self) -> str:
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"