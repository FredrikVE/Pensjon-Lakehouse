from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LakehouseConfig:
    """Konfigurasjon for lakehouse-pipeline."""

    # DuckDB-databasefil (persistent)
    db_path: str = "pensjon.duckdb"

    # Mappe for Parquet-eksport
    export_path: Path = field(default_factory=lambda: Path("exports"))
