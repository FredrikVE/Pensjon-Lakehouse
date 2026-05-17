#Pensjon-Lakehouse/pensjon/usecase/pensjon_usecases.py
"""
Use cases for pensjonsanalyse.

Forretningslogikk som kombinerer data fra repositories.
"""

from __future__ import annotations

from pensjon.repository.befolkning_repository import BefolkningRepository
from pensjon.repository.arbeidsmarked_repository import LonnSysselsettingRepository


class GetPensionAgeShareUseCase:
    """Hent andel 55+ per kommune."""

    def __init__(self, befolkning_repo: BefolkningRepository):
        self._repo = befolkning_repo

    def execute(self, years: list[str] | None = None) -> list[dict]:
        return self._repo.get_pension_age_share(years)


class GetNaeringProfilUseCase:
    """
    Kombiner sysselsetting og lønn per næring.

    Beregner estimert pensjonsvolum:
    lønnstakere × månedslønn × 12 × typisk OTP-sats (2%)
    """

    def __init__(self, lonn_syss_repo: LonnSysselsettingRepository):
        self._repo = lonn_syss_repo

    def execute(self, quarters: list[str] | None = None) -> list[dict]:
        rows = self._repo.get_per_naering(quarters)

        result = []
        for row in rows:
            estimert_volum = None
            if row["manedslonn"] and row["lonsstakere"]:
                estimert_volum = round(row["lonsstakere"] * row["manedslonn"] * 12 * 0.02)

            result.append({
                **row,
                "estimert_pensjonsvolum": estimert_volum,
            })

        return result
