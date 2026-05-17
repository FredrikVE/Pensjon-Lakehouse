#Pensjon-Lakehouse/pensjon/sql_loader.py
from pathlib import Path
from string import Template

SQL_DIR = Path(__file__).resolve().parent / "sql"

def load_sql(relative_path: str, **params) -> str:
    sql_path = SQL_DIR / relative_path

    if not sql_path.exists():
        raise FileNotFoundError(f"Fant ikke SQL-fil: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")
    template = Template(sql)

    return template.substitute(
        {key: str(value) for key, value in params.items()}
    )