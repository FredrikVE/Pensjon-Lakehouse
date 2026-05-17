# Pensjon-Lakehouse/pensjon/lakehouse/stages/gold_stage.py

import duckdb

from pensjon.lakehouse.config import LakehouseConfig
from pensjon.sql_loader import load_sql


class GoldStage:
    def __init__(self, db: duckdb.DuckDBPyConnection, config: LakehouseConfig):
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
        self._build_aldersgruppe_fordeling_siste_ar()
        self._build_aldersgruppe_trend()

    def _build_top_kommuner_pensjonsalder(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_top_kommuner_pensjonsalder.sql",
                lake=self.lake,
            )
        )

        print("\n  Top 10 kommuner med høyest andel 55+:\n")

        result = self.db.execute(
            load_sql(
                "gold/select_top_kommuner.sql",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))

    def _build_naering_pensjonsvolum(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_naering_pensjonsvolum.sql",
                lake=self.lake,
            )
        )

        print("\n\n  Næringer etter estimert pensjonsvolum (siste kvartal):\n")

        result = self.db.execute(
            load_sql(
                "gold/select_naering_pensjonsvolum.sql",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))

    def _build_pensjonsandel_trend(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_pensjonsandel_trend.sql",
                lake=self.lake,
            )
        )

        print("\n\n  Pensjonsandel-trend (landsgjennomsnitt):\n")

        result = self.db.execute(
            load_sql(
                "gold/select_pensjonsandel_trend.sql",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))

    def _build_aldersgruppe_fordeling_siste_ar(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_aldersgruppe_fordeling_siste_ar.sql",
                lake=self.lake,
            )
        )

        print("\n\n  Aldersgruppefordeling siste år:\n")

        result = self.db.execute(
            load_sql(
                "gold/select_aldersgruppe_fordeling_siste_ar.sql",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))

    def _build_aldersgruppe_trend(self) -> None:
        self.db.execute(
            load_sql(
                "gold/build_aldersgruppe_trend.sql",
                lake=self.lake,
            )
        )

        print("\n\n  Aldersgruppe-trend, andel av befolkning per år:\n")

        result = self.db.execute(
            load_sql(
                "gold/select_aldersgruppe_trend.sql",
                lake=self.lake,
            )
        ).fetchdf()

        print(result.to_string(index=False))