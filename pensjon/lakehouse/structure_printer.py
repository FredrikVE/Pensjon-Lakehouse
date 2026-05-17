#Pensjon-Lakehouse/pensjon/lakehouse/structure_printer.py
import os
from pensjon.lakehouse.config import LakehouseConfig

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