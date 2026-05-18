"""
DataSource for SSB tabell 11654: Lønnstakere, jobber, lønn og lønnsindeks.
"""

from pensjon.datasource.ssb_datasource import SSBDataSource


class LonnSysselsettingDataSource(SSBDataSource):
    """Henter lønn og sysselsetting per næring fra SSB tabell 11654."""

    TABLE_ID = "11654"

    def fetch(self, quarters: list[str] | None = None) -> dict:
        """
        Hent antall lønnstakere og gjennomsnittlig månedslønn per næring.

        Args:
            quarters: F.eks. ["2024K1"]. Default: siste 4 kvartaler.

        Returns:
            Rå JSON-stat2 response
        """
        time_filter = (
            {"code": "Tid", "selection": {"filter": "item", "values": quarters}}
            if quarters
            else {"code": "Tid", "selection": {"filter": "top", "values": ["4"]}}
        )

        query = {
            "query": [
                {
                    "code": "NACE2007",
                    "selection": {"filter": "all", "values": ["*"]},
                },
                {
                    "code": "ContentsCode",
                    "selection": {
                        "filter": "item",
                        "values": ["Lonsstakere", "GjMdTotal"],
                    },
                },
                time_filter,
            ],
            "response": {"format": "json-stat2"},
        }

        return self.post(self.TABLE_ID, query)
