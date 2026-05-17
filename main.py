#!/usr/bin/env python3
"""
Pensjon Lakehouse – SSB-data → Bronze → Silver → Gold.

Henter ekte data fra SSBs API via DataSource → Repository → UseCase,
og lander dem i en Lakehouse-pipeline med DuckDB.

Datakilder:
  - SSB 07459: Befolkning per alder og kommune
  - SSB 11654: Lønnstakere og månedslønn per næring

Kjør:
    python3 main.py
"""

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from pensjon.di.dependencies import Dependencies
from pensjon.sql_loader import load_sql


@dataclass(frozen=True)
class LakehouseConfig:
    lake_path: Path = Path("/tmp/pensjon_lakehouse")


class AuditWriter:
    def __init__(self, config: LakehouseConfig):
        self.config = config
        self.lake = config.lake_path

    def write_bronze_audit(
        self,
        batch_id: str,
        bef_count: int,
        ls_count: int,
    ) -> None:
        audit = {
            "version": 0,
            "timestamp": datetime.now().isoformat(),
            "operation": "INGEST",
            "batch_id": batch_id,
            "sources": {
                "befolkning": {
                    "table": "07459",
                    "rows": bef_count,
                },
                "lonn_sysselsetting": {
                    "table": "11654",
                    "rows": ls_count,
                },
            },
        }

        audit_path = self.lake / "_audit" / "bronze.json"

        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump([audit], f, indent=2, ensure_ascii=False)


class LakehouseStructurePrinter:
    def __init__(self, config: LakehouseConfig):
        self.config = config
        self.lake = config.lake_path

    def print(self) -> None:
        print("\n" + "─" * 64)
        print("  FILSTRUKTUR")
        print("─" * 64 + "\n")

        root_str = str(self.lake)

        for root, dirs, files in sorted(os.walk(root_str)):
            level = root.replace(root_str, "").count(os.sep)
            indent = "  " + "  │ " * level
            dirname = os.path.basename(root) or "pensjon_lakehouse"

            parquets = [f for f in files if f.endswith(".parquet")]
            jsons = [f for f in files if f.endswith(".json")]

            parts = []

            if parquets:
                size = sum(
                    os.path.getsize(os.path.join(root, f))
                    for f in parquets
                )
                parts.append(f"{len(parquets)} parquet ({size / 1024:.0f} KB)")

            if jsons:
                parts.append(f"{len(jsons)} json")

            suffix = f"  ← {', '.join(parts)}" if parts else ""

            print(f"{indent}{dirname}/{suffix}")


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
                "bronze/copy_befolkning_to_bronze.py",
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
                "bronze/copy_lonn_syss_to_bronze.py",
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


class SilverStage:
    def __init__(
        self,
        db: duckdb.DuckDBPyConnection,
        config: LakehouseConfig,
    ):
        self.db = db
        self.config = config
        self.lake = config.lake_path

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  SILVER – Rensing og kobling")
        print("─" * 64)

        self._build_befolkning_pensjon()
        self._build_naering_pensjon()

    def _build_befolkning_pensjon(self) -> None:
        self.db.execute(
            load_sql(
                "silver/build_befolkning_pensjon.py",
                lake=self.lake,
            )
        )

        count = self._count_parquet("silver/befolkning_pensjon.parquet")

        print(f"  ✓ Befolkning pensjonsandel: {count} rader (kommune × år)")

    def _build_naering_pensjon(self) -> None:
        self.db.execute(
            load_sql(
                "silver/build_naering_pensjon.py",
                lake=self.lake,
            )
        )

        count = self._count_parquet("silver/naering_pensjon.parquet")

        print(f"  ✓ Næring pensjonsvolum: {count} rader")

    def _count_parquet(self, relative_path: str) -> int:
        parquet_path = self.lake / relative_path

        return self.db.execute(f"""
            SELECT COUNT(*)
            FROM read_parquet('{parquet_path}')
        """).fetchone()[0]


class GoldStage:
    def __init__(
        self,
        db: duckdb.DuckDBPyConnection,
        config: LakehouseConfig,
    ):
        self.db = db
        self.config = config
        self.lake = config.lake_path

    def run(self) -> None:
        print("\n" + "─" * 64)
        print("  GOLD – Forretningsklare analyser")
        print("─" * 64)

        self._build_top_kommuner_pensjonsalder()
        self._build_naering_pensjonsvolum()
        self._build_pensjonsandel_trend()

    def _build_top_kommuner_pensjonsalder(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_top_kommuner_pensjonsalder.py",
                lake=self.lake,
            )
        )

        print("\n  Top 10 kommuner med høyest andel 55+:\n")

        result = self.db.execute(
            load_sql(
                "gold/select_top_kommuner.py",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))

    def _build_naering_pensjonsvolum(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_naering_pensjonsvolum.py",
                lake=self.lake,
            )
        )

        print("\n\n  Næringer etter estimert pensjonsvolum (siste kvartal):\n")

        result = self.db.execute(
            load_sql(
                "gold/select_naering_pensjonsvolum.py",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))

    def _build_pensjonsandel_trend(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_pensjonsandel_trend.py",
                lake=self.lake,
            )
        )

        print("\n\n  Pensjonsandel-trend (landsgjennomsnitt):\n")

        result = self.db.execute(
            load_sql(
                "gold/select_pensjonsandel_trend.py",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))


class PensjonLakehousePipeline:
    def __init__(
        self,
        deps: Dependencies,
        config: LakehouseConfig | None = None,
    ):
        self.deps = deps
        self.config = config or LakehouseConfig()
        self.lake = self.config.lake_path

    def run(self) -> None:
        self._print_header()
        self._setup_lakehouse()

        db = duckdb.connect()

        try:
            BronzeStage(
                deps=self.deps,
                db=db,
                config=self.config,
            ).run()

            SilverStage(
                db=db,
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


if __name__ == "__main__":
    pipeline = PensjonLakehousePipeline(
        deps=Dependencies(),
    )

    pipeline.run()
