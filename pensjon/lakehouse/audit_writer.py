#Pensjon-Lakehouse/pensjon/lakehouse/audit_writer.py
import json
from datetime import datetime

from pensjon.lakehouse.config import LakehouseConfig

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