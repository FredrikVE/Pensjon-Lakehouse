from pathlib import Path
from runpy import run_path
from string import Template


SQL_DIR = Path(__file__).resolve().parent / "sql"


def load_sql(relative_path: str, **params) -> str:
    '''
    Leser en Python-basert SQL-fil fra pensjon/sql og erstatter variabler.

    Eksempel:
        load_sql("silver/build_befolkning_pensjon.py", lake=LAKE)

    SQL-filene er Python-filer som eksporterer variabelen SQL.

    Eksempel på SQL-fil:

        SQL = """
        SELECT *
        FROM some_table;
        """

    I SQL-strengene brukes variabler som:
        $lake
        $batch_id
    '''
    sql_path = SQL_DIR / relative_path

    if not sql_path.exists():
        raise FileNotFoundError(f"Fant ikke SQL-fil: {sql_path}")

    namespace = run_path(str(sql_path))

    if "SQL" not in namespace:
        raise ValueError(f"Filen mangler variabelen SQL: {sql_path}")

    template = Template(namespace["SQL"])

    return template.substitute(
        {key: str(value) for key, value in params.items()}
    )