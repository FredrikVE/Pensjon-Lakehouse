# Pensjon Lakehouse

## Om prosjektet
Et Databricks, Python, SQL og Git-prosjekt for å lære å enke "Lakehouse-arkitektur" i skymiljø i form av Azure.

Lakehouse-prosjekt for foretar en enkel alalyse av aldersfordelingen i Norske kommuner for å undersøke hvor "eldrebølgen" 
er mest fremtredende, og dermed risikoen for et tenkt forsikrings-selskap.

Prosjektet henter åpne data fra SSB, og "foredler" og modellerer disse gjennom følgende arkitkekturlag.

1) Bronze
2) Silver
3) Gold

Og lagrer disse dataene på "gold-format" i Databricks med Unity Catalog. 
Deretter visualiseres resultatet i et interaktivt Databricks dashboard.


## Dashboard

<p align="center">
  <a href="https://fredrikve.github.io/Pensjon-Lakehouse/">
    <img src="docs/dashboard_button.svg" alt="Åpne live dashboard">
  </a>
</p>

### Screenshot av dashboard i Databricks

![Dashboard](docs/Dashboard.png)





## Problemstilling

Hvilke kommuner og næringer har størst demografisk pensjonsrelevans i Norge?

Prosjektet kombinerer befolkningsdata (alder per kommune) med lønns- og sysselsettingsdata (per næring) for å belyse:

- Hvor stor andel av befolkningen er i pensjonsrelevant alder (55+)?
- Hvordan utvikler denne andelen seg over tid?
- Hvilke næringer har størst estimert pensjonsvolum?

## Prosjektstruktur
```
Pensjon-Lakehouse/
├── README.md
├── index.html                          # Gjenskaping av Dashboard med GitHub Pages
├── docs/
└── notebooks/
    ├── 01_bronze_ingest.ipynb
    ├── 02_silver.ipynb
    ├── 03_gold.ipynb
    ├── 04_dashboard_setup.ipynb
    ├── 05_generate_github_dashboard.ipynb
    └── pensjon_dashboard.lvdash.json   # Databricks Lakeview dashboard-config (Vises visuelt i Databriks)
```

## Arkitektur

![Arkitektur](docs/architecture.svg)


## Datakilder

| Kilde | SSB-tabell | Innhold |
|-------|-----------|---------|
| Befolkning | [07459](https://www.ssb.no/statbank/table/07459) | Befolkning etter alder og kommune |
| Lønn/sysselsetting | [11654](https://www.ssb.no/statbank/table/11654) | Lønnstakere og månedslønn per næring |



## Lagdeling

| Lag | Innhold | Prinsipp |
|-----|---------|----------|
| **Bronze** | Rå SSB-data, alle dimensjoner, metadata (_ingest_ts, _source, _batch_id) | Ufiltrert, reproduserbar |
| **Silver** | Filtrert til kommuner, renset alder, pivotering, pensjonsandel | Renset, koblet |
| **Gold** | Trender, topp-kommuner, næringsprofil, aldersfordeling | Forretningsklart |

## Gold-tabeller

| Tabell | Beskrivelse |
|--------|-------------|
| `pensjonsandel_trend` | Vektet landsgjennomsnitt 55+ per år |
| `top_kommuner_pensjonsalder` | Topp 20 kommuner med høyest andel 55+ |
| `naering_pensjonsvolum` | Næringer rangert etter estimert pensjonsvolum |
| `aldersgruppe_fordeling` | Fordeling på 8 aldersgrupper, siste år |
| `aldersgruppe_trend` | Aldersgruppe-andeler over tid |


## Notebooks

| # | Notebook | Beskrivelse |
|---|----------|-------------|
| 01 | `01_bronze_ingest` | Henter data fra SSB API, skriver til bronze Delta-tabeller |
| 02 | `02_silver` | Bygger silver-tabeller med ren SQL |
| 03 | `03_gold` | Bygger gold-tabeller med ren SQL |
| 04 | `04_dashboard_setup` | SQL-spørringer og guide for Databricks-dashboardet |
| 05 | `05_generate_github_dashboard` | Genererer statisk HTML-dashboard fra Gold-data |


## Kjøring

Forutsetninger: Databricks workspace med Unity Catalog og tilgang til en SQL Warehouse eller cluster.

**Kjør i rekkefølge:**

1. Importer notebooks fra `notebooks/`-mappen
2. Kjør `01_bronze_ingest` — henter data fra SSB og oppretter bronze-tabeller
3. Kjør `02_silver` — bygger silver-tabeller
4. Kjør `03_gold` — bygger gold-tabeller

## Forklaring av mappestruktur

De mest relevante og interessante filene for dette prosjektet finne du i denne delen av filstrukturen.

```bash
.
├── README.md
├── assets                        -> ting som har med styling av html/css for github-showcase tabell å gjøre
├── docs                          -> Bilder og dokumentasjon
├── index.html                    -> filen som kjører showcasen av tabellen inne i README
├── notebooks                     -> Her er Databricks notebookene
│   ├── 01_bronze_ingest.ipynb
│   ├── 02_silver.ipynb
│   ├── 03_gold.ipynb
│   ├── 04_dashboard_setup.ipynb
│   ├── 05_generate_github_dashboard.ipynb
│   └── Pensjon Dashboard.lvdash.json
└── robots.txt
```

Men for deg som er ekstra interessert, så ligger formateringen av den HTML/JavaScript/CSS-baserte
showcase tabellen som det linkes til øverst i README-filen igjennom GitHub-pages i denne delen av mappestrukturen.


```bash
index.html
assets/
├── css/
│   ├── main.css
│   ├── tokens.css
│   ├── base.css
│   ├── layout.css
│   ├── components.css
│   ├── table.css
│   └── responsive.css
└── js/
    ├── data.js
    ├── charts.js
    ├── table.js
    └── main.js
```

## Designvalg

**Vektet nasjonalt gjennomsnitt.** <br>
Pensjonsandel-trend beregnes som `SUM(55+) / SUM(total)`, ikke `AVG(kommuneandeler)`. Et uvektet snitt ville gitt feil bilde fordi små kommuner ville veid like mye som store.

**SQL eier transformasjonslogikken.** <br>
Python henter data og orkestrerer, men all rensing, kobling og aggregering skjer i SQL. Det gjør logikken transparent og enkel å endre.

**Bronze er rå.** <br>
Bronze inneholder ufiltrert SSB-data med alle dimensjoner. Filtrering skjer først i Silver, slik at regler kan endres uten å hente data på nytt.

**Estimert pensjonsvolum.** <br> 
Beregnet som `lønnstakere × månedslønn × 12 × 2 % OTP` — en forenkling, men gir et relativt bilde av næringenes pensjonsrelevans.

## Teknologier

<table>
  <tbody>
    <tr>
      <td>1</td>
      <td>Python</td>
    </tr>
    <tr>
      <td>2</td>
      <td>SQL</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Databricks</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Azure</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Chart.js</td>
    </tr>
    <tr>
      <td>6</td>
      <td>GitHub Pages</td>
    </tr>
  </tbody>
</table>
