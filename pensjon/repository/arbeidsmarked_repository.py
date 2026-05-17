"""
Repository for lønn og sysselsetting (tabell 11654).

Henter og transformerer data med både antall lønnstakere
og gjennomsnittlig månedslønn per næring.
"""

from __future__ import annotations

from pensjon.datasource.lonn_datasource import LonnSysselsettingDataSource
from pensjon.datasource.jsonstat_parser import parse_jsonstat2


class LonnSysselsettingRepository:
    """Cache og transformering av lønns- og sysselsettingsdata."""

    def __init__(self, datasource: LonnSysselsettingDataSource):
        self._datasource = datasource

    def get_raw(self, quarters: list[str] | None = None) -> list[dict]:
        raw = self._datasource.fetch(quarters)
        return parse_jsonstat2(raw)

    def get_per_naering(self, quarters: list[str] | None = None) -> list[dict]:
        """
        Hent lønnstakere og månedslønn per næring og kvartal.

        Pivoter slik at hver rad har både antall og lønn.
        """
        rows = self.get_raw(quarters)

        # Grupper per (næring, kvartal), samle ContentsCode-verdier
        groups: dict[tuple, dict] = {}
        for row in rows:
            key = (row["NACE2007_code"], row["NACE2007_label"], row["Tid_code"])
            if key not in groups:
                groups[key] = {"lonsstakere": None, "manedslonn": None}

            code = row.get("ContentsCode_code", "")
            if code == "Lonsstakere" and row["value"] is not None:
                groups[key]["lonsstakere"] = int(row["value"])
            elif code == "GjMdTotal" and row["value"] is not None:
                groups[key]["manedslonn"] = int(row["value"])

        result = []
        for (naering_code, naering_label, kvartal), vals in groups.items():
            if vals["lonsstakere"] is None:
                continue
            result.append({
                "naering_code": naering_code,
                "naering_label": naering_label,
                "kvartal": kvartal,
                "lonsstakere": vals["lonsstakere"],
                "manedslonn": vals["manedslonn"],
            })

        return result
