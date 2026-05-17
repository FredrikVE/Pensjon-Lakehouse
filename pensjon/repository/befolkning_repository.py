"""
Repository for befolkningsdata.

Tilsvarer LocationForecastRepository.js – cache, rensing
og transformering av SSB-rådata til brukbare objekter.

Repository vet IKKE om Bronze/Silver/Gold – det er et rent
data-access-lag som returnerer rene Python-objekter.
"""

from __future__ import annotations

from pensjon.datasource.befolkning_datasource import BefolkningDataSource
from pensjon.datasource.jsonstat_parser import parse_jsonstat2


class BefolkningRepository:
    """Cache, rensing og transformering av befolkningsdata."""

    PENSION_MIN_AGE = 55

    def __init__(self, datasource: BefolkningDataSource):
        self._datasource = datasource
        self._cache: dict | None = None

    async def _fetch_and_parse(self, years: list[str] | None = None) -> list[dict]:
        """Hent og parse, med enkel caching."""
        cache_key = str(years)
        if self._cache and cache_key in self._cache:
            return self._cache[cache_key]

        raw = self._datasource.fetch_befolkning(years)
        rows = parse_jsonstat2(raw)

        if self._cache is None:
            self._cache = {}
        self._cache[cache_key] = rows
        return rows

    def get_befolkning_raw(self, years: list[str] | None = None) -> list[dict]:
        """
        Hent alle befolkningsrader (alle kommuner, alle aldersgrupper).

        Returnerer rå parsede rader – Bronze-nivå.
        """
        raw = self._datasource.fetch_befolkning(years)
        return parse_jsonstat2(raw)

    @staticmethod
    def _parse_age(alder_label: str) -> int | None:
        """Ekstraher alder som tall fra SSB-label. '55 år' → 55, '105 år eller eldre' → 105."""
        age_str = alder_label.split()[0]
        return int(age_str) if age_str.isdigit() else None

    def get_befolkning_by_kommune(self, years: list[str] | None = None) -> list[dict]:
        """
        Hent befolkning gruppert per kommune og aldersgruppe.

        Renser bort fylkes-aggregater (4-sifrede kommunekoder).
        Tilsvarer koordinatvasking i LocationForecastRepository.

        Returnerer rader med:
            kommune_code, kommune_label, alder_label, year, antall
        """
        rows = self.get_befolkning_raw(years)
        cleaned = []

        for row in rows:
            code = row.get("Region_code", "")
            # Filtrer bort fylker (2-sifret) og landet (1-sifret "0")
            if len(code) != 4:
                continue

            # Filtrer bort rader med None/manglende verdi
            if row["value"] is None:
                continue

            cleaned.append({
                "kommune_code": code,
                "kommune_label": row["Region_label"],
                "alder_label": row["Alder_label"],
                "year": row["Tid_code"],
                "antall": int(row["value"]),
            })

        return cleaned

    def get_pension_age_share(self, years: list[str] | None = None) -> list[dict]:
        """
        Beregn andel av befolkning som er 55+ per kommune.

        Denne mapping-logikken tilsvarer getCurrentWeather()
        i GetCurrentWeatherUseCase – vi beregner en avledet verdi.
        """
        by_kommune = self.get_befolkning_by_kommune(years)

        # Grupper per (kommune, år)
        groups: dict[tuple, dict] = {}
        for row in by_kommune:
            key = (row["kommune_code"], row["kommune_label"], row["year"])
            if key not in groups:
                groups[key] = {"total": 0, "pension_age": 0}

            groups[key]["total"] += row["antall"]

            age = self._parse_age(row["alder_label"])
            if age is not None and age >= self.PENSION_MIN_AGE:
                groups[key]["pension_age"] += row["antall"]

        result = []
        for (code, label, year), counts in groups.items():
            total = counts["total"]
            pension = counts["pension_age"]
            result.append({
                "kommune_code": code,
                "kommune_label": label,
                "year": year,
                "total_befolkning": total,
                "pension_age_befolkning": pension,
                "pension_age_share": round(pension / total, 4) if total > 0 else 0,
            })

        return result