# Pensjon Lakehouse

En datapipeline som henter **ekte data fra SSB** (Statistisk sentralbyrå) og lander dem i en **Data Lakehouse-arkitektur** (Bronze → Silver → Gold) for å analysere pensjonsrelevante mønstre i norske kommuner og næringer.

Prosjektet er bygget for å demonstrere hele kjeden fra API-innhenting til forretningsklare analyser, med tydelig lagdeling inspirert av MVVM-mønsteret.

---

## Hva prosjektet gjør

Pipelinen henter to datasett fra SSBs åpne API:

| Kilde | SSB-tabell | Innhold |
|---|---|---|
| Befolkning | [07459](https://www.ssb.no/statbank/table/07459) | Befolkning per aldersgruppe og kommune, 5 siste år |
| Lønn/sysselsetting | [11654](https://www.ssb.no/statbank/table/11654) | Antall lønnstakere og gjennomsnittlig månedslønn per næring, kvartalsvis |

Dataene landes som Parquet-filer i en Lakehouse-struktur og transformeres gjennom tre lag:

**Bronze** – Rådata fra SSB, uendret, med governance-metadata (kilde, batch-ID, tidsstempel).

**Silver** – Renset og koblet: befolkning aggregert til pensjonsandel per kommune, lønn og sysselsetting koblet per næring med estimert pensjonsvolum.

**Gold** – Tre forretningsklare analyser:
- Kommuner med høyest andel 55+ (pensjonsmodenhet)
- Næringer rangert etter estimert pensjonsvolum (lønnstakere × lønn × 12 × 2% OTP)
- Pensjonsandel-trend over tid (landsgjennomsnitt)

---

## Arkitektur

Koden følger et DataSource → Repository → UseCase-mønster, det samme mønsteret som brukes i [Opplett](https://github.com/) (et MVVM-basert værprosjekt i React), men her i Python:

```
pensjon_lakehouse/
├── main.py                              ← Pipeline: SSB → Bronze → Silver → Gold
└── pensjon/
    ├── dependencies.py                  ← Composition root (dependency injection)
    ├── datasource/
    │   ├── ssb_datasource.py            ← Base HTTP-klient mot SSB (POST)
    │   ├── befolkning_datasource.py     ← Tabell 07459
    │   ├── lonn_datasource.py           ← Tabell 11654
    │   └── jsonstat_parser.py           ← Parser for JSON-stat2 format
    ├── repository/
    │   ├── befolkning_repository.py     ← Cache, rensing, pensjonsaldersberegning
    │   └── arbeidsmarked_repository.py  ← Pivoterer lønn + sysselsetting per næring
    └── usecase/
        └── pensjon_usecases.py          ← Forretningslogikk og avledede beregninger
```

### Mapping til MVVM-mønsteret

| Lag | Ansvar | Tilsvarer i Opplett (React) |
|---|---|---|
| `SSBDataSource` | Lavnivå HTTP mot SSB API | `DataSource.js` |
| `BefolkningDataSource` | Bygger JSON-spørring for tabell 07459 | `LocationForecastDataSource.js` |
| `BefolkningRepository` | Cache, koordinatvasking, transformering | `LocationForecastRepository.js` |
| `GetPensionAgeShareUseCase` | Forretningslogikk – beregn pensjonsandel | `GetCurrentWeatherUseCase.js` |
| `Dependencies` | Composition root, oppretter objektgrafen | `dependencies.js` |

### Dataflyt

```
SSB API (07459, 11654)
    ↓ POST med JSON-spørring
DataSource
    ↓ Rå JSON-stat2
Repository (parse, cache, rens)
    ↓ Python dicts
UseCase (forretningslogikk)
    ↓ Pandas DataFrame
DuckDB → Bronze (Parquet)
    ↓ SQL-transformasjoner
Silver (Parquet)
    ↓ Aggregering
Gold (Parquet) → Analyseresultater
```

---

## Kjøring

### Forutsetninger

- Python 3.11+
- `pip install duckdb pandas requests`

### Start

```bash
python3 main.py
```

Pipelinen henter data direkte fra SSBs API (krever internett), lander dem i `/tmp/pensjon_lakehouse/` som Parquet-filer, og printer analyseresultatene.

### Forventet output

```
================================================================
  PENSJON LAKEHOUSE
  SSB-data → Bronze → Silver → Gold
================================================================

  BRONZE – Henter data fra SSB
  ✓ Befolkning: ~504 000 rader
  ✓ Lønn/sysselsetting: ~72 rader

  SILVER – Rensing og kobling
  ✓ Befolkning pensjonsandel: ~1 783 rader (kommune × år)
  ✓ Næring pensjonsvolum: ~72 rader

  GOLD – Forretningsklare analyser
  Top 10 kommuner med høyest andel 55+
  Næringer etter estimert pensjonsvolum
  Pensjonsandel-trend (landsgjennomsnitt)

  ✓ Pipeline fullført
================================================================
```

---

## Teknologier

| Teknologi | Rolle |
|---|---|
| [DuckDB](https://duckdb.org/) | Analytisk SQL-motor, in-process. Leser/skriver Parquet direkte |
| [SSB PxWebApi](https://www.ssb.no/api) | Åpent API for alle 7 500+ tabeller i Statistikkbanken |
| [Parquet](https://parquet.apache.org/) | Kolonnebasert filformat med ZSTD-komprimering |
| [Pandas](https://pandas.pydata.org/) | Bro mellom Python-lister og DuckDB |
| [JSON-stat2](https://json-stat.org/) | SSBs responsformat – egenutviklet parser i prosjektet |

---

## SSB API

SSBs PxWebApi (v1) bruker POST med JSON-body for å hente data. Spørringene definerer hvilke variabler, filtere og tidsperioder som skal hentes. Eksempel:

```json
{
  "query": [
    {"code": "NACE2007", "selection": {"filter": "all", "values": ["*"]}},
    {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Lonsstakere", "GjMdTotal"]}},
    {"code": "Tid", "selection": {"filter": "top", "values": ["4"]}}
  ],
  "response": {"format": "json-stat2"}
}
```

Responsen er JSON-stat2, et kompakt format der verdiene er en flat array og dimensjonene beskrevet i metadata. `jsonstat_parser.py` konverterer dette til en liste av dicts.

API-et er åpent, krever ingen registrering, og bruker CC BY 4.0-lisens.

---

## Kjente begrensninger og gjenstående arbeid

### Må fikses

- **Aldersgruppe-filtrering:** Pensjonsandel-beregningen i Silver gir 0 fordi aldersgruppe-labelene fra SSB ikke matcher hardkodede strenger (`'55-59'`, `'60-64'` osv.). Labelene fra API-et må sjekkes og filteret oppdateres.

### Forbedringer

- **Feilhåndtering:** Pipelinen stopper ved første feil. Bør ha try/catch per datakilde slik at resten av pipelinen kjører selv om én kilde feiler.
- **Inkrementell innlasting:** Bronze overskriver alt ved hver kjøring. Bør støtte append med deduplisering.
- **Tester:** Ingen tester ennå. Unit-tester for JSON-stat-parseren og repository-logikken bør legges til.
- **Konfigurasjon:** Tabellnummer, filterverdier og Parquet-stier er hardkodet. Bør flyttes til en config-fil.

### Mulige utvidelser

- **Dashboard:** Koble Gold-tabellene til et Power BI-dashboard eller en interaktiv HTML-rapport.
- **Flere datakilder:** Finans Norge har [markedsstatistikk for pensjon og sparing](https://www.finansnorge.no/tema/statistikk-og-analyse/pensjon-og-sparing/markedsstatistikk-pensjon-og-sparing/) med data om innskuddspensjon, fripoliser og OTP-satser per næring.
- **Kobling befolkning × næring:** I dag er befolkningsdata på kommunenivå og næringsdata på nasjonalt nivå. SSBs sysselsettingsstatistikk per kommune (tabell 13470) kunne koble de to og gi pensjonsvolum-estimater per kommune × næring.
- **SSB PxWebApi v2:** SSB lanserte v2 i oktober 2025 med støtte for GET-spørringer. Å migrere til v2 ville gjøre DataSource-laget mer likt GET-baserte API-klienter.

---

## Datakilder og lisens

| Kilde | Lisens |
|---|---|
| [Statistisk sentralbyrå (SSB)](https://www.ssb.no/) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Prosjektkoden er tilgjengelig for gjennomgang som porteføljeprosjekt.
