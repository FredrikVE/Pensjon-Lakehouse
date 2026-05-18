# Pensjon Lakehouse

Et hands-on lakehouse-prosjekt for pensjonsanalyse. Henter åpne SSB-data med Python, modellerer data gjennom Bronze-, Silver- og Gold-lag i DuckDB, eksporterer analyseklare datasett til Parquet, og er designet for videre publisering til Azure Data Lake Storage Gen2, Databricks og Power BI.

## Problemstilling

Hvilke kommuner og næringer har størst demografisk pensjonsrelevans i Norge? Prosjektet kombinerer befolkningsdata (alder per kommune) med lønns- og sysselsettingsdata (per næring) for å belyse:

- Hvor stor andel av befolkningen er i pensjonsrelevant alder (55+)?
- Hvordan utvikler denne andelen seg over tid?
- Hvilke næringer har størst estimert pensjonsvolum?

## Arkitektur

```
SSB API (07459, 11654)
    │
    ▼
┌─────────────────────────────────────────┐
│  Python: DataSource → Repository        │
│  Henter og parser JSON-stat2            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  DuckDB: pensjon.duckdb                 │
│                                         │
│  bronze/                                │
│    ├── ssb_befolkning_raw               │
│    └── ssb_lonn_sysselsetting_raw       │
│                                         │
│  silver/                                │
│    ├── befolkning_pensjon               │
│    ├── befolkning_aldersgrupper         │
│    └── naering_pensjon                  │
│                                         │
│  gold/                                  │
│    ├── pensjonsandel_trend              │
│    ├── top_kommuner_pensjonsalder       │
│    ├── naering_pensjonsvolum            │
│    ├── aldersgruppe_fordeling           │
│    └── aldersgruppe_trend               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Parquet-eksport (exports/gold/)        │
│  → Power BI / Databricks / Azure ADLS   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Streamlit Dashboard                    │
│  Leser direkte fra Gold-schema          │
└─────────────────────────────────────────┘
```

## Lagdeling

| Lag | Innhold | Prinsipp |
|-----|---------|----------|
| **Bronze** | Rå SSB-data, alle dimensjoner, inkl. fylker og null-verdier | Ufiltrert, reproduserbar |
| **Silver** | Filtrert til kommuner, renset alder, pivotering, pensjonsandel | Renset, koblet |
| **Gold** | Analyseklare tabeller: trender, topp-kommuner, næringsprofil | Forretningsklart |
| **Export** | Parquet-filer fra Gold for BI/skyplattform | Åpent format, delbart |

## Kjøring

```bash
# Installer avhengigheter
pip install duckdb pandas requests streamlit plotly

# Kjør pipeline (henter fra SSB API)
python main.py

# Kjør med testdata (uten internett)
python -c "
from pensjon.lakehouse.pipeline import PensjonLakehousePipeline
PensjonLakehousePipeline(use_testdata=True).run()
"

# Start dashboard
streamlit run dashboard/app.py
```

## Prosjektstruktur

```
Pensjon-Lakehouse/
├── main.py                          # Entrypoint
├── pensjon.duckdb                   # Persistent database (generert)
├── pensjon/
│   ├── datasource/
│   │   ├── ssb_datasource.py        # Base HTTP-klient for SSB
│   │   ├── befolkning_datasource.py # Tabell 07459
│   │   ├── lonn_datasource.py       # Tabell 11654
│   │   └── jsonstat_parser.py       # JSON-stat2 → rader
│   ├── repository/
│   │   ├── befolkning_repository.py # Rå data-tilgang
│   │   └── lonn_repository.py       # Rå data-tilgang
│   ├── lakehouse/
│   │   ├── config.py
│   │   ├── pipeline.py              # Orkestrering
│   │   └── stages/
│   │       ├── bronze_stage.py      # SSB → bronze-schema
│   │       ├── silver_stage.py      # bronze → silver (SQL)
│   │       ├── gold_stage.py        # silver → gold (SQL)
│   │       └── export_stage.py      # gold → Parquet
│   └── sql/
│       ├── schemas/
│       │   └── create_schemas.sql
│       ├── bronze/
│       │   ├── ingest_befolkning.sql
│       │   └── ingest_lonn_sysselsetting.sql
│       ├── silver/
│       │   ├── build_befolkning_pensjon.sql
│       │   ├── build_befolkning_aldersgrupper.sql
│       │   └── build_naering_pensjon.sql
│       └── gold/
│           ├── build_top_kommuner.sql
│           ├── build_pensjonsandel_trend.sql
│           ├── build_naering_pensjonsvolum.sql
│           ├── build_aldersgruppe_fordeling.sql
│           └── build_aldersgruppe_trend.sql
├── exports/gold/                    # Parquet-filer (generert)
├── dashboard/
│   └── app.py                       # Streamlit dashboard
└── tests/
    └── testdata.py                  # Testdata-generator
```

## Designvalg

**DuckDB med schemas fremfor bare Parquet-filer.** Schemas gjør lagdelingen eksplisitt og spørrbar — du kan utforske data direkte med SQL etter at pipelinen har kjørt, uten å lese filer på nytt.

**Bronze er rå.** Bronze inneholder ufiltrert SSB-data med alle dimensjoner. Filtrering (f.eks. fjerne fylker, rense alder) skjer først i Silver. Det betyr at Silver-regler kan endres uten å hente data på nytt fra SSB.

**SQL eier transformasjonslogikken.** Python orkestrerer og henter data, men all rensing, kobling og aggregering skjer i SQL-filer. Det gjør logikken transparent og enkel å endre.

**Vektet nasjonalt gjennomsnitt.** Pensjonsandel-trend beregnes som SUM(55+) / SUM(total), ikke AVG(kommuneandeler). Et uvektet snitt ville gitt feil bilde fordi små kommuner ville veid like mye som store.

**Parquet som eksport, ikke primærformat.** Gold-tabellene lever i DuckDB. Parquet eksporteres som et eget steg for deling med BI-verktøy eller opplasting til skyplattform.

## Planlagt: Azure-utvidelse

```
DuckDB Gold → Parquet → Azure Data Lake Storage Gen2 → Databricks / Power BI
```

- Python-script for opplasting til Azure Blob/ADLS Gen2
- Databricks-notebook som registrerer tabeller i Unity Catalog
- Power BI-rapport koblet mot Parquet i ADLS eller Databricks SQL Warehouse

## Datakilder

- **SSB tabell 07459**: Befolkning etter kjønn og alder, kommuner
- **SSB tabell 11654**: Lønnstakere, jobber, lønn og lønnsindeks

## Teknologier

Python · DuckDB · SQL · Pandas · Parquet · Streamlit · Plotly
