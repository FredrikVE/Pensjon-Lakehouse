"""
DataSource for SSB tabell 07459: Befolkning etter kjønn og alder, kommuner.
"""

from pensjon.datasource.ssb_datasource import SSBDataSource


class BefolkningDataSource(SSBDataSource):
    """Henter befolkningsdata per aldersgruppe og kommune fra SSB."""

    TABLE_ID = "07459"

    def fetch(self, years: list[str] | None = None) -> dict:
        """
        Hent befolkning per enkeltårs-alder, alle kommuner, begge kjønn.

        Args:
            years: Liste med årstall, f.eks. ["2020", "2024"].
                   Default: siste 5 år via "top"-filter.

        Returns:
            Rå JSON-stat2 response
        """
        time_filter = (
            {"code": "Tid", "selection": {"filter": "item", "values": years}}
            if years
            else {"code": "Tid", "selection": {"filter": "top", "values": ["5"]}}
        )

        query = {
            "query": [
                {
                    "code": "Region",
                    "selection": {"filter": "all", "values": ["*"]},
                },
                {
                    "code": "Alder",
                    "selection": {"filter": "all", "values": ["*"]},
                },
                {
                    "code": "ContentsCode",
                    "selection": {"filter": "item", "values": ["Personer1"]},
                },
                time_filter,
            ],
            "response": {"format": "json-stat2"},
        }

        return self.post(self.TABLE_ID, query)
