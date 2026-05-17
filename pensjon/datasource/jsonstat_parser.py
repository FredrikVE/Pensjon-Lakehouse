#Pensjon-Lakehouse/pensjon/datasource/jsonstat_parser.py
"""
Parser for JSON-stat2 format fra SSB.

SSB returnerer data i JSON-stat2, et kompakt statistikkformat
der verdiene er en flat array og dimensjonene beskrevet i metadata.
Denne parseren konverterer til en liste av dicts (rader).
"""

from __future__ import annotations


def parse_jsonstat2(response: dict) -> list[dict]:
    """
    Konverter en JSON-stat2 response til en liste av rader.

    JSON-stat2 lagrer verdier i en flat array i row-major order.
    Dimensjonene (region, alder, år osv.) er beskrevet i metadata,
    og vi "folder ut" arrayen til rader med én dict per celle.

    Args:
        response: Rå JSON-stat2 dict fra SSB

    Returns:
        Liste av dicts, f.eks.:
        [{"Region": "0301", "Alder": "20-24", "Tid": "2024", "value": 42351}, ...]
    """
    # Dimensjoner i rekkefølge (bestemt av "id"-listen)
    dim_ids = response["id"]          # f.eks. ["Region", "Kjonn", "Alder", "Tid", "ContentsCode"]
    dim_sizes = response["size"]      # f.eks. [357, 1, 21, 5, 1]

    # Bygg label-lookup for hver dimensjon
    dim_labels = {}
    dim_codes = {}
    for dim_id in dim_ids:
        dim_meta = response["dimension"][dim_id]
        cat = dim_meta["category"]

        # index: {"0301": 0, "0101": 1, ...} eller {"2020": 0, "2021": 1, ...}
        index = cat["index"]
        # label: {"0301": "Oslo", "0101": "Halden", ...}
        label = cat.get("label", {})

        # Sorter etter index-posisjon for å matche row-major order
        if isinstance(index, dict):
            sorted_codes = sorted(index.keys(), key=lambda k: index[k])
        else:
            sorted_codes = index

        dim_codes[dim_id] = sorted_codes
        dim_labels[dim_id] = {code: label.get(code, code) for code in sorted_codes}

    values = response["value"]
    rows = []

    # Fold ut flat array til rader
    total = len(values)
    for flat_idx in range(total):
        row = {}
        remainder = flat_idx

        # Beregn indeks for hver dimensjon (row-major)
        for i, dim_id in enumerate(dim_ids):
            stride = 1
            for j in range(i + 1, len(dim_ids)):
                stride *= dim_sizes[j]

            dim_idx = remainder // stride
            remainder = remainder % stride

            code = dim_codes[dim_id][dim_idx]
            row[f"{dim_id}_code"] = code
            row[f"{dim_id}_label"] = dim_labels[dim_id][code]

        row["value"] = values[flat_idx]
        rows.append(row)

    return rows
