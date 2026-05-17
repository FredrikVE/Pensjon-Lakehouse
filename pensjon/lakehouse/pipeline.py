#Pensjon-Lakehouse/pensjon/lakehouse/pipeline.py
import shutil

import duckdb

from pensjon.di.dependencies import Dependencies
from pensjon.lakehouse.config import LakehouseConfig
from pensjon.lakehouse.stages.bronze_stage import BronzeStage
from pensjon.lakehouse.stages.silver_stage import SilverStage
from pensjon.lakehouse.stages.gold_stage import GoldStage
from pensjon.lakehouse.structure_printer import LakehouseStructurePrinter


class PensjonLakehousePipeline:
    def __init__(self, deps: Dependencies, config: LakehouseConfig | None = None ):
        self.deps = deps
        self.config = config or LakehouseConfig()
        self.lake = self.config.lake_path

    def run(self) -> None:
        self._print_header()
        self._setup_lakehouse()

        db = duckdb.connect()

        try:
            BronzeStage(deps=self.deps, db=db, config=self.config).run()

            SilverStage(db=db,
                config=self.config,
            ).run()

            GoldStage(
                db=db,
                config=self.config,
            ).run()

            LakehouseStructurePrinter(
                config=self.config,
            ).print()

            self._print_success()

        finally:
            db.close()

    def _setup_lakehouse(self) -> None:
        if self.lake.exists():
            shutil.rmtree(self.lake)

        folders = [
            "bronze/befolkning",
            "bronze/lonn_sysselsetting",
            "silver",
            "gold",
            "_audit",
        ]

        for folder in folders:
            (self.lake / folder).mkdir(parents=True, exist_ok=True)

    def _print_header(self) -> None:
        print("=" * 64)
        print("  PENSJON LAKEHOUSE")
        print("  SSB-data → Bronze → Silver → Gold")
        print("=" * 64)

    def _print_success(self) -> None:
        print("\n" + "=" * 64)
        print("  ✓ Pipeline fullført")
        print("=" * 64)