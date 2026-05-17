#Pensjon-Lakehouse/pensjon/lakehouse/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LakehouseConfig:
    lake_path: Path = Path("/tmp/pensjon_lakehouse")