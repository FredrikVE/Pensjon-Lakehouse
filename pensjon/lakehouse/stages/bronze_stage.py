"""
Bronze Stage: Henter rådata fra SSB og lagrer i bronze-schema.

Bronze inneholder ufiltrert, uprosessert data slik SSB returnerte den.
Eneste tillegg er metadata (_ingest_ts, _source, _batch_id).
"""

from datetime import datetime

import duckdb
import pandas as pd

from pensjon.repository.befolkning_repository import BefolkningRepository
from pensjon.repository.lonn_repository import LonnSysselsettingRepository
from pensjon.sql_loader import load_sql

class BronzeStage:
    def __init__(self, befolkning_repo: BefolkningRepository, lonn_repo: LonnSysselsettingRepository, db: duckdb.DuckDBPyConnection):
        self.befolkning_repo = befolkning_repo
        self.lonn_repo = lonn_repo
        self.db = db

    def run(self) -> dict:
        """Kjør Bronze-ingest. Returnerer radtall for audit."""
        print("\n" + "─" * 64)
        print("  BRONZE – Henter rådata fra SSB")
        print("─" * 64)

        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        bef_count = self._ingest_befolkning(batch_id)
        ls_count = self._ingest_lonn_sysselsetting(batch_id)

        print(f"\n  ✓ Batch: {batch_id}")
        print(f"  ✓ Bronze totalt: {bef_count + ls_count} rader")

        return {
            "batch_id": batch_id,
            "befolkning_rows": bef_count,
            "lonn_sysselsetting_rows": ls_count,
        }

    def _ingest_befolkning(self, batch_id: str) -> int:
        print("\n  Henter befolkningsdata (tabell 07459)...")

        rows = self.befolkning_repo.get_raw()
        df = pd.DataFrame(rows)

        # Registrer som midlertidig staging-tabell
        self.db.execute(
            "CREATE OR REPLACE TEMP TABLE raw_befolkning_staging AS SELECT * FROM df"
        )

        # Flytt til bronze-schema med metadata
        self.db.execute(load_sql("bronze/ingest_befolkning.sql", batch_id=batch_id))

        # Rydd opp staging
        self.db.execute("DROP TABLE IF EXISTS raw_befolkning_staging")

        count = self.db.execute(
            "SELECT COUNT(*) FROM bronze.ssb_befolkning_raw"
        ).fetchone()[0]

        print(f"  ✓ Befolkning: {count} rader")
        return count

    def _ingest_lonn_sysselsetting(self, batch_id: str) -> int:
        print("  Henter lønn/sysselsetting (tabell 11654)...")

        rows = self.lonn_repo.get_raw()
        df = pd.DataFrame(rows)

        self.db.execute(
            "CREATE OR REPLACE TEMP TABLE raw_lonn_syss_staging AS SELECT * FROM df"
        )

        self.db.execute(
            load_sql("bronze/ingest_lonn_sysselsetting.sql", batch_id=batch_id)
        )

        self.db.execute("DROP TABLE IF EXISTS raw_lonn_syss_staging")

        count = self.db.execute(
            "SELECT COUNT(*) FROM bronze.ssb_lonn_sysselsetting_raw"
        ).fetchone()[0]

        print(f"  ✓ Lønn/sysselsetting: {count} rader")
        return count
