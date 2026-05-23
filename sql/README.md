# SQL for GitHub Pages-dashboard

Denne mappen inneholder SQL-spørringene som brukes av `notebooks/05_generate_github_dashboard.ipynb`
for å generere den statiske GitHub Pages-versjonen av dashboardet.

## Struktur

```text
sql/
└── github_dashboard/
    ├── pensjonsandel_latest.sql
    ├── pensjonsandel_trend.sql
    ├── aldersfordeling.sql
    ├── top_kommuner.sql
    ├── top_naeringer.sql
    ├── aldersgruppe_trend.sql
    └── kommuner_detalj.sql
```

## Template-variabler

SQL-filene bruker disse plassholderne:

```sql
${catalog}
${schema}
```

Notebooken fyller dem inn med:

```python
CATALOG = "pensjon_lakehouse"
SCHEMA = "gold"
```

Eksempel:

```python
from string import Template

def read_sql_template(name: str) -> str:
    path = SQL_DIR / f"{name}.sql"
    template = Template(path.read_text(encoding="utf-8"))

    return template.safe_substitute({
        "catalog": CATALOG,
        "schema": SCHEMA,
    })
```

Da blir for eksempel:

```sql
FROM ${catalog}.${schema}.pensjonsandel_trend
```

til:

```sql
FROM pensjon_lakehouse.gold.pensjonsandel_trend
```

## Anbefalt ansvar

- `sql/github_dashboard/*.sql` eier spørringene.
- `templates/index.html.tpl` eier HTML-strukturen.
- `assets/css/*.css` eier design.
- `assets/js/*.js` eier frontend-logikk.
- `notebooks/05_generate_github_dashboard.ipynb` orkestrerer og genererer `index.html` + `assets/js/data.js`.
