"""
Parser for JSON-stat2 format fra SSB.

JSON-stat2 lagrer verdier i en flat array i row-major order.
Dimensjonene beskrives i metadata, og vi folder ut arrayen til rader.
"""

from __future__ import annotations

def parse_jsonstat2(response: dict) -> list[dict]:
    """
    Konverter en JSON-stat2 response til en liste av rader.

    Args:
        response: Rå JSON-stat2 dict fra SSB

    Returns:
        Liste av dicts, f.eks.:
        [{"Region_code": "0301", "Region_label": "Oslo", "value": 42351}, ...]
    """
    dim_ids = response["id"]
    dim_sizes = response["size"]

    # Valider at dimensjoner matcher verdier
    expected = 1
    for size in dim_sizes:
        expected *= size

    values = response["value"]
    if len(values) != expected:
        raise ValueError(
            f"Forventet {expected} verdier basert på dimensjoner, fikk {len(values)}"
        )

    # Bygg label-lookup for hver dimensjon
    dim_codes = {}
    dim_labels = {}
    for dim_id in dim_ids:
        dim_meta = response["dimension"][dim_id]
        cat = dim_meta["category"]

        index = cat["index"]
        label = cat.get("label", {})

        if isinstance(index, dict):
            sorted_codes = sorted(index.keys(), key=lambda k: index[k])
        else:
            sorted_codes = index

        dim_codes[dim_id] = sorted_codes
        dim_labels[dim_id] = {code: label.get(code, code) for code in sorted_codes}

    rows = []
    total = len(values)

    for flat_idx in range(total):
        row = {}
        remainder = flat_idx

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
