#Pensjon-Lakehouse/pensjon/datasource/ssb_datasource.py
"""
Base DataSource for SSB Statistikkbanken.

Tilsvarer DataSource.js i værappen – en lavnivå HTTP-klient
som håndterer POST-spørringer mot SSBs PxWebApi.

SSB bruker POST med JSON-body i stedet for GET med query-params,
men mønsteret er det samme: sanitize → request → parse → return.
"""

import time
import requests


class SSBDataSource:
    """Base-klasse for alle SSB-datasources."""

    BASE_URL = "https://data.ssb.no/api/v0/no/table"

    def __init__(self):
        self.api_call_count = 0

    def post(self, table_id: str, query: dict) -> dict:
        """
        POST en JSON-spørring mot en SSB-tabell.

        Tilsvarer DataSource.get(path) i værappen,
        men SSB bruker POST med JSON-body.

        Args:
            table_id: SSB-tabellnummer, f.eks. "07459"
            query:    JSON-spørring i SSB-format

        Returns:
            Rå JSON-stat response som dict
        """
        self.api_call_count += 1
        url = f"{self.BASE_URL}/{table_id}"

        who = type(self).__name__
        started_at = time.perf_counter()
        print(f"[SSB][{who}] API-kall #{self.api_call_count} -> {url}")

        response = requests.post(
            url,
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        ms = round((time.perf_counter() - started_at) * 1000)

        if not response.ok:
            print(f"[SSB][{who}] API-kall #{self.api_call_count} FEIL ({response.status_code}) etter {ms}ms")
            print(f"[SSB][{who}] Response: {response.text[:500]}")
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")

        print(f"[SSB][{who}] API-kall #{self.api_call_count} OK ({response.status_code}) etter {ms}ms")
        return response.json()
