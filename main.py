#!/usr/bin/env python3
"""
Pensjon Lakehouse – SSB-data → Bronze → Silver → Gold.

Henter ekte data fra SSBs API via DataSource → Repository → UseCase,
og lander dem i en Lakehouse-pipeline med DuckDB.

Datakilder:
  - SSB 07459: Befolkning per alder og kommune
  - SSB 11654: Lønnstakere og månedslønn per næring

Kjør: python3 main.py
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from pensjon.dependencies import Dependencies


LAKE = Path("/tmp/pensjon_lakehouse")


def setup():
    if LAKE.exists():
        shutil.rmtree(LAKE)
    for d in ["bronze/befolkning", "bronze/lonn_sysselsetting",
              "silver", "gold", "_audit"]:
        (LAKE / d).mkdir(parents=True, exist_ok=True)


# ════════════════════════════════════════════
# BRONZE – Land rådata fra SSB som Parquet
# ════════════════════════════════════════════

def ingest_bronze(deps: Dependencies, db: duckdb.DuckDBPyConnection):
    print("\n" + "─" * 64)
    print("  BRONZE – Henter data fra SSB")
    print("─" * 64)

    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 1. Befolkning per kommune og aldersgruppe
    print("\n  Henter befolkningsdata (tabell 07459)...")
    befolkning = deps.befolkning_repo.get_befolkning_by_kommune()
    df_bef = pd.DataFrame(befolkning)
    db.execute("CREATE OR REPLACE TABLE raw_befolkning AS SELECT * FROM df_bef")
    db.execute(f"""
        COPY (
            SELECT *, CURRENT_TIMESTAMP AS _ingest_ts,
                   'ssb_07459' AS _source, '{batch_id}' AS _batch_id
            FROM raw_befolkning
        ) TO '{LAKE}/bronze/befolkning/data.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    bef_count = db.execute("SELECT COUNT(*) FROM raw_befolkning").fetchone()[0]
    print(f"  ✓ Befolkning: {bef_count} rader")

    # 2. Lønn og sysselsetting per næring
    print("  Henter lønn/sysselsetting (tabell 11654)...")
    lonn_syss = deps.lonn_syss_repo.get_per_naering()
    df_ls = pd.DataFrame(lonn_syss)
    db.execute("CREATE OR REPLACE TABLE raw_lonn_syss AS SELECT * FROM df_ls")
    db.execute(f"""
        COPY (
            SELECT *, CURRENT_TIMESTAMP AS _ingest_ts,
                   'ssb_11654' AS _source, '{batch_id}' AS _batch_id
            FROM raw_lonn_syss
        ) TO '{LAKE}/bronze/lonn_sysselsetting/data.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    ls_count = db.execute("SELECT COUNT(*) FROM raw_lonn_syss").fetchone()[0]
    print(f"  ✓ Lønn/sysselsetting: {ls_count} rader")

    # Audit
    audit = {
        "version": 0, "timestamp": datetime.now().isoformat(),
        "operation": "INGEST", "batch_id": batch_id,
        "sources": {
            "befolkning": {"table": "07459", "rows": bef_count},
            "lonn_sysselsetting": {"table": "11654", "rows": ls_count},
        }
    }
    with open(LAKE / "_audit" / "bronze.json", "w") as f:
        json.dump([audit], f, indent=2)

    print(f"\n  ✓ Batch: {batch_id}")
    print(f"  ✓ Totalt: {bef_count + ls_count} rader i Bronze")


# ════════════════════════════════════════════
# SILVER – Rens og kombiner
# ════════════════════════════════════════════

def transform_silver(db: duckdb.DuckDBPyConnection):
    print("\n" + "─" * 64)
    print("  SILVER – Rensing og kobling")
    print("─" * 64)

    # Befolkning: beregn pensjonsalder-andel per kommune og år
    db.execute(f"""
        COPY (
            SELECT
                kommune_code,
                kommune_label,
                year,
                SUM(antall) AS total_befolkning,
                SUM(CASE
                    WHEN CAST(split_part(alder_label, ' ', 1) AS INTEGER) >= 55
                    THEN antall ELSE 0
                END) AS pension_age_befolkning,
                ROUND(
                    SUM(CASE
                        WHEN CAST(split_part(alder_label, ' ', 1) AS INTEGER) >= 55
                        THEN antall ELSE 0
                    END)::FLOAT / NULLIF(SUM(antall), 0), 4
                ) AS pension_age_share,
                CURRENT_TIMESTAMP AS _cleaned_ts
            FROM read_parquet('{LAKE}/bronze/befolkning/data.parquet')
            GROUP BY kommune_code, kommune_label, year
            HAVING SUM(antall) > 0
            ORDER BY year, pension_age_share DESC
        ) TO '{LAKE}/silver/befolkning_pensjon.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    bef_count = db.execute(f"""
        SELECT COUNT(*) FROM read_parquet('{LAKE}/silver/befolkning_pensjon.parquet')
    """).fetchone()[0]
    print(f"  ✓ Befolkning pensjonsandel: {bef_count} rader (kommune × år)")

    # Lønn/sysselsetting: beregn estimert pensjonsvolum per næring
    db.execute(f"""
        COPY (
            SELECT
                naering_code,
                naering_label,
                kvartal,
                lonsstakere,
                manedslonn,
                ROUND(lonsstakere * COALESCE(manedslonn, 0) * 12 * 0.02) AS estimert_pensjonsvolum,
                CURRENT_TIMESTAMP AS _cleaned_ts
            FROM read_parquet('{LAKE}/bronze/lonn_sysselsetting/data.parquet')
            WHERE lonsstakere IS NOT NULL
            ORDER BY estimert_pensjonsvolum DESC NULLS LAST
        ) TO '{LAKE}/silver/naering_pensjon.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    naer_count = db.execute(f"""
        SELECT COUNT(*) FROM read_parquet('{LAKE}/silver/naering_pensjon.parquet')
    """).fetchone()[0]
    print(f"  ✓ Næring pensjonsvolum: {naer_count} rader")


# ════════════════════════════════════════════
# GOLD – Forretningsklare analyser
# ════════════════════════════════════════════

def build_gold(db: duckdb.DuckDBPyConnection):
    print("\n" + "─" * 64)
    print("  GOLD – Forretningsklare analyser")
    print("─" * 64)

    # Gold 1: Top 20 kommuner med høyest pensjonsandel (siste år)
    db.execute(f"""
        COPY (
            SELECT kommune_code, kommune_label, year,
                   total_befolkning, pension_age_befolkning, pension_age_share
            FROM read_parquet('{LAKE}/silver/befolkning_pensjon.parquet')
            WHERE year = (
                SELECT MAX(year) FROM read_parquet('{LAKE}/silver/befolkning_pensjon.parquet')
            )
            ORDER BY pension_age_share DESC
            LIMIT 20
        ) TO '{LAKE}/gold/top_kommuner_pensjonsalder.parquet' (FORMAT PARQUET)
    """)

    print("\n  Top 10 kommuner med høyest andel 55+:\n")
    result = db.execute(f"""
        SELECT kommune_label AS kommune,
               total_befolkning AS innbyggere,
               pension_age_befolkning AS "55+",
               ROUND(pension_age_share * 100, 1) AS "andel_%"
        FROM read_parquet('{LAKE}/gold/top_kommuner_pensjonsalder.parquet')
        LIMIT 10
    """).fetchdf()
    print(result.to_string(index=False))

    # Gold 2: Næringer rangert etter estimert pensjonsvolum (siste kvartal)
    db.execute(f"""
        COPY (
            SELECT naering_code, naering_label, kvartal,
                   lonsstakere, manedslonn, estimert_pensjonsvolum
            FROM read_parquet('{LAKE}/silver/naering_pensjon.parquet')
            WHERE kvartal = (
                SELECT MAX(kvartal) FROM read_parquet('{LAKE}/silver/naering_pensjon.parquet')
            )
            AND estimert_pensjonsvolum IS NOT NULL
            ORDER BY estimert_pensjonsvolum DESC
        ) TO '{LAKE}/gold/naering_pensjonsvolum.parquet' (FORMAT PARQUET)
    """)

    print("\n\n  Næringer etter estimert pensjonsvolum (siste kvartal):\n")
    result = db.execute(f"""
        SELECT naering_label AS næring,
               lonsstakere AS lønnstakere,
               manedslonn AS "mnd.lønn",
               estimert_pensjonsvolum AS "est.volum"
        FROM read_parquet('{LAKE}/gold/naering_pensjonsvolum.parquet')
        LIMIT 10
    """).fetchdf()
    print(result.to_string(index=False))

    # Gold 3: Pensjonsandel-utvikling over tid (landsgjennomsnitt)
    db.execute(f"""
        COPY (
            SELECT year,
                   ROUND(AVG(pension_age_share) * 100, 2) AS snitt_pensjonsandel_pst,
                   SUM(pension_age_befolkning) AS total_55_pluss,
                   SUM(total_befolkning) AS total_befolkning
            FROM read_parquet('{LAKE}/silver/befolkning_pensjon.parquet')
            GROUP BY year
            ORDER BY year
        ) TO '{LAKE}/gold/pensjonsandel_trend.parquet' (FORMAT PARQUET)
    """)

    print("\n\n  Pensjonsandel-trend (landsgjennomsnitt):\n")
    result = db.execute(f"""
        SELECT * FROM read_parquet('{LAKE}/gold/pensjonsandel_trend.parquet')
    """).fetchdf()
    print(result.to_string(index=False))


# ════════════════════════════════════════════
# FILSTRUKTUR
# ════════════════════════════════════════════

def show_structure():
    print("\n" + "─" * 64)
    print("  FILSTRUKTUR")
    print("─" * 64 + "\n")
    root_str = str(LAKE)
    for root, dirs, files in sorted(os.walk(root_str)):
        level = root.replace(root_str, "").count(os.sep)
        indent = "  " + "  │ " * level
        dirname = os.path.basename(root) or "pensjon_lakehouse"
        parquets = [f for f in files if f.endswith(".parquet")]
        jsons = [f for f in files if f.endswith(".json")]
        parts = []
        if parquets:
            size = sum(os.path.getsize(os.path.join(root, f)) for f in parquets)
            parts.append(f"{len(parquets)} parquet ({size/1024:.0f} KB)")
        if jsons:
            parts.append(f"{len(jsons)} json")
        suffix = f"  ← {', '.join(parts)}" if parts else ""
        print(f"{indent}{dirname}/{suffix}")


# ════════════════════════════════════════════
# KJØR
# ════════════════════════════════════════════

if __name__ == "__main__":
    setup()

    print("=" * 64)
    print("  PENSJON LAKEHOUSE")
    print("  SSB-data → Bronze → Silver → Gold")
    print("=" * 64)

    deps = Dependencies()
    db = duckdb.connect()

    try:
        ingest_bronze(deps, db)
        transform_silver(db)
        build_gold(db)
        show_structure()

        print("\n" + "=" * 64)
        print("  ✓ Pipeline fullført")
        print("=" * 64)
    finally:
        db.close()