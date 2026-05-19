"""
Repository for befolkningsdata fra SSB tabell 07459.

Henter og parser JSON-stat2 til rader.
Filtrering og transformasjon skjer i SQL (Silver/Gold), ikke her.
"""

from __future__ import annotations

from pensjon.datasource.befolkning_datasource import BefolkningDataSource
from pensjon.datasource.jsonstat_parser import parse_jsonstat2

class BefolkningRepository:
    """Henter og parser befolkningsdata."""

    def __init__(self, datasource: BefolkningDataSource):
        self._datasource = datasource

    def get_raw(self, years: list[str]) -> list[dict]:
        """
        Hent alle befolkningsrader uten filtrering.

        Returnerer rå parsede rader — alle regioner, alle aldre,
        inkludert fylkesaggregater og null-verdier.
        Filtrering skjer i Silver-laget via SQL.
        """
        raw = self._datasource.fetch(years)
        return parse_jsonstat2(raw)
