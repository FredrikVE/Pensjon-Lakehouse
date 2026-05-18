"""
Pensjon Lakehouse Pipeline.

Orkestrerer Bronze → Silver → Gold → Export.
Bruker DuckDB med schemas som arbeidsmodell
og Parquet som eksportformat.
"""

import duckdb
import pandas as pd

from pensjon.datasource.befolkning_datasource import BefolkningDataSource
from pensjon.datasource.lonn_datasource import LonnSysselsettingDataSource
from pensjon.datasource.jsonstat_parser import parse_jsonstat2
from pensjon.repository.befolkning_repository import BefolkningRepository
from pensjon.repository.lonn_repository import LonnSysselsettingRepository

from pensjon.lakehouse.config import LakehouseConfig
from pensjon.lakehouse.stages.bronze_stage import BronzeStage
from pensjon.lakehouse.stages.silver_stage import SilverStage
from pensjon.lakehouse.stages.gold_stage import GoldStage
from pensjon.lakehouse.stages.export_stage import ExportStage
from pensjon.sql_loader import load_sql


class PensjonLakehousePipeline:
    def __init__(self, config: LakehouseConfig | None = None, use_testdata: bool = False):
        self.config = config or LakehouseConfig()
        self.use_testdata = use_testdata

    def run(self) -> None:
        self._print_header()

        db = duckdb.connect(self.config.db_path)

        try:
            db.execute(load_sql("schemas/create_schemas.sql"))

            if self.use_testdata:
                self._ingest_testdata(db)
            else:
                befolkning_ds = BefolkningDataSource()
                lonn_ds = LonnSysselsettingDataSource()
                befolkning_repo = BefolkningRepository(befolkning_ds)
                lonn_repo = LonnSysselsettingRepository(lonn_ds)
                BronzeStage(befolkning_repo, lonn_repo, db).run()

            SilverStage(db).run()
            GoldStage(db).run()
            ExportStage(db, self.config).run()

            self._print_schema_overview(db)
            self._print_success()
        finally:
            db.close()

    def _ingest_testdata(self, db: duckdb.DuckDBPyConnection) -> None:
        """Bruk generert testdata i stedet for SSB API."""
        from tests.testdata import generate_befolkning_response, generate_lonn_response

        print("\n" + "─" * 64)
        print("  BRONZE – Laster testdata (SSB API ikke tilgjengelig)")
        print("─" * 64)

        bef_rows = parse_jsonstat2(generate_befolkning_response())
        df_bef = pd.DataFrame(bef_rows)
        db.execute("CREATE OR REPLACE TEMP TABLE raw_befolkning_staging AS SELECT * FROM df_bef")
        db.execute(load_sql("bronze/ingest_befolkning.sql", batch_id="testdata_batch"))
        db.execute("DROP TABLE IF EXISTS raw_befolkning_staging")
        count_bef = db.execute("SELECT COUNT(*) FROM bronze.ssb_befolkning_raw").fetchone()[0]
        print(f"  ✓ Befolkning: {count_bef} rader")

        lonn_rows = parse_jsonstat2(generate_lonn_response())
        df_lonn = pd.DataFrame(lonn_rows)
        db.execute("CREATE OR REPLACE TEMP TABLE raw_lonn_syss_staging AS SELECT * FROM df_lonn")
        db.execute(load_sql("bronze/ingest_lonn_sysselsetting.sql", batch_id="testdata_batch"))
        db.execute("DROP TABLE IF EXISTS raw_lonn_syss_staging")
        count_lonn = db.execute("SELECT COUNT(*) FROM bronze.ssb_lonn_sysselsetting_raw").fetchone()[0]
        print(f"  ✓ Lønn/sysselsetting: {count_lonn} rader")

        print(f"\n  ✓ Bronze totalt: {count_bef + count_lonn} rader (testdata)")

    def _print_schema_overview(self, db: duckdb.DuckDBPyConnection) -> None:
        print("\n" + "─" * 64)
        print("  DATABASE-OVERSIKT")
        print("─" * 64)

        for schema in ["bronze", "silver", "gold"]:
            tables = db.execute(
                f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
            ).fetchall()

            print(f"\n  {schema}/")
            for (table_name,) in tables:
                count = db.execute(
                    f"SELECT COUNT(*) FROM {schema}.{table_name}"
                ).fetchone()[0]
                print(f"    ├── {table_name}: {count} rader")

    def _print_header(self) -> None:
        print("=" * 64)
        print("  PENSJON LAKEHOUSE")
        print("  SSB API → Bronze → Silver → Gold → Parquet")
        print("=" * 64)

    def _print_success(self) -> None:
        print("\n" + "=" * 64)
        print("  ✓ Pipeline fullført")
        print(f"  ✓ Database: {self.config.db_path}")
        print(f"  ✓ Parquet:  {self.config.export_path}/gold/")
        print("=" * 64)
