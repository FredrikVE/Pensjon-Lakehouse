"""
Repository for lønn og sysselsetting fra SSB tabell 11654.

Henter og parser JSON-stat2 til rader.
Pivotering og transformasjon skjer i SQL (Silver/Gold), ikke her.
"""

from __future__ import annotations

from pensjon.datasource.lonn_datasource import LonnSysselsettingDataSource
from pensjon.datasource.jsonstat_parser import parse_jsonstat2


class LonnSysselsettingRepository:
    """Henter og parser lønns-/sysselsettingsdata."""

    def __init__(self, datasource: LonnSysselsettingDataSource):
        self._datasource = datasource

    def get_raw(self, quarters: list[str] | None = None) -> list[dict]:
        """
        Hent alle rader uten pivotering eller filtrering.

        Returnerer rå parsede rader med separate rader for
        lønnstakere og månedslønn (ContentsCode).
        Pivotering skjer i Silver-laget via SQL.
        """
        raw = self._datasource.fetch(quarters)
        return parse_jsonstat2(raw)
