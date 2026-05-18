"""
Last opp lakehouse-data til Azure Data Lake Storage Gen2.

Leser connection string fra .env-fil i prosjektroten.
Kjør: python -m pensjon.azure.upload_to_adls
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pensjon.azure import DataLakeServiceClient

# Last .env fra prosjektroten
load_dotenv()

CONTAINER = "lakehouse"


def get_client() -> DataLakeServiceClient:
    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise RuntimeError(
            "Mangler AZURE_STORAGE_CONNECTION_STRING.\n"
            "Legg den i .env-filen i prosjektroten:\n"
            "AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;..."
        )
    return DataLakeServiceClient.from_connection_string(conn_str)


def upload_file(fs_client, local_path: Path, remote_path: str) -> None:
    """Last opp én fil til ADLS Gen2."""
    dir_name = str(Path(remote_path).parent)
    file_name = Path(remote_path).name

    dir_client = fs_client.get_directory_client(dir_name)
    dir_client.create_directory()

    file_client = dir_client.get_file_client(file_name)
    with open(local_path, "rb") as f:
        file_client.upload_data(f, overwrite=True)

    size_kb = local_path.stat().st_size / 1024
    print(f"  ✓ {remote_path} ({size_kb:.0f} KB)")


def main():
    client = get_client()
    fs_client = client.get_file_system_client(CONTAINER)

    print("=" * 60)
    print("  AZURE UPLOAD — Pensjon Lakehouse")
    print(f"  Container: {CONTAINER}")
    print("=" * 60)

    # Gold-laget (eksporterte Parquet-filer)
    export_dir = Path("exports/gold")
    if not export_dir.exists():
        raise RuntimeError(
            "Finner ikke exports/gold/. Kjør main.py først for å generere Parquet-filer."
        )

    parquet_files = sorted(export_dir.glob("*.parquet"))
    if not parquet_files:
        raise RuntimeError("Ingen Parquet-filer funnet i exports/gold/.")

    print(f"\n  Laster opp {len(parquet_files)} Gold-filer...\n")

    for parquet_file in parquet_files:
        remote_path = f"gold/{parquet_file.name}"
        upload_file(fs_client, parquet_file, remote_path)

    print(f"\n{'=' * 60}")
    print(f"  ✓ {len(parquet_files)} filer lastet opp til ADLS Gen2")
    print(f"  ✓ Sti: lakehouse/gold/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
