# Databricks notebook source


# COMMAND ----------

# MAGIC %md
# MAGIC # Pensjon Lakehouse
# MAGIC
# MAGIC Analyse av pensjonsrelatert demografi og estimert pensjonsvolum basert på SSB-data.
# MAGIC
# MAGIC **Dataflyt**
# MAGIC
# MAGIC SSB API → Python → DuckDB Bronze/Silver/Gold → Parquet → Azure Data Lake Storage Gen2 → Databricks
# MAGIC
# MAGIC **Kilder**
# MAGIC
# MAGIC - SSB 07459: befolkning etter kommune, alder og år
# MAGIC - SSB 11654: lønn og sysselsetting etter næring
# MAGIC
# MAGIC **Tilgang**
# MAGIC
# MAGIC Azure Key Vault → Databricks secret scope → Spark config på cluster
# MAGIC
# MAGIC Notebooken forutsetter at clusteret allerede har tilgang til storage accounten. Ingen nøkler eller secrets ligger i notebooken.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Last inn Gold-data
# MAGIC
# MAGIC Vi leser fem ferdig bearbeidede Gold-tabeller fra Azure Data Lake Storage Gen2.
# MAGIC
# MAGIC Dette er de samme datasettene som brukes i Streamlit-dashboardet.

# COMMAND ----------

base_path = "abfss://lakehouse@pensjonlakehouse.dfs.core.windows.net/gold"

pensjonsandel_trend = spark.read.parquet(f"{base_path}/pensjonsandel_trend.parquet")
top_kommuner = spark.read.parquet(f"{base_path}/top_kommuner_pensjonsalder.parquet")
naering_pensjonsvolum = spark.read.parquet(f"{base_path}/naering_pensjonsvolum.parquet")
aldersgruppe_fordeling = spark.read.parquet(f"{base_path}/aldersgruppe_fordeling.parquet")
aldersgruppe_trend = spark.read.parquet(f"{base_path}/aldersgruppe_trend.parquet")

for name, df in [
    ("pensjonsandel_trend", pensjonsandel_trend),
    ("top_kommuner", top_kommuner),
    ("naering_pensjonsvolum", naering_pensjonsvolum),
    ("aldersgruppe_fordeling", aldersgruppe_fordeling),
    ("aldersgruppe_trend", aldersgruppe_trend),
]:
    df.createOrReplaceTempView(name)

print("✓ 5 Gold-tabeller lastet fra ADLS Gen2 og registrert som SQL-views")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Dashboard-stil
# MAGIC
# MAGIC Vi bruker Plotly Express, slik Streamlit-dashboardet gjør.
# MAGIC
# MAGIC Notebooken bruker et konsistent **Viridis-fargeskjema** på tvers av grafene, med mørk bakgrunn og enkle visualiseringer.

# COMMAND ----------

import plotly.express as px
from pyspark.sql.functions import col

DARK_BG = "#0E1117"
GRID = "#303846"
TEXT = "#FAFAFA"

COLOR_SCALE = px.colors.sequential.Viridis
MAIN_COLOR = COLOR_SCALE[5]

def dashboard_layout(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=TEXT),
        height=height,
        margin=dict(l=20, r=20, t=55, b=35),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. KPI-er
# MAGIC
# MAGIC Disse nøkkeltallene viser siste observerte pensjonsandel, totalt antall personer 55+ og total befolkning.
# MAGIC
# MAGIC Endringen i pensjonsandel vises i prosentpoeng fra forrige år.

# COMMAND ----------

trend_pdf = pensjonsandel_trend.orderBy("year").toPandas()
trend_pdf["year"] = trend_pdf["year"].astype(int)

latest = trend_pdf.iloc[-1]
previous = trend_pdf.iloc[-2] if len(trend_pdf) > 1 else latest
delta_pp = latest["pensjonsandel_pst"] - previous["pensjonsandel_pst"]

kpi_rows = [
    ("Pensjonsandel (55+)", f"{latest['pensjonsandel_pst']:.1f} %", f"{delta_pp:+.2f} pp"),
    ("Totalt 55+", f"{int(latest['total_55_pluss']):,}".replace(",", " "), ""),
    ("Total befolkning", f"{int(latest['total_befolkning']):,}".replace(",", " "), ""),
]

kpi_df = spark.createDataFrame(kpi_rows, ["KPI", "Verdi", "Endring"])
display(kpi_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Pensjonsandel-trend
# MAGIC
# MAGIC Tabellen viser utviklingen i andel innbyggere 55+ over tid.
# MAGIC
# MAGIC Dette er et vektet nasjonalt mål: total 55+ delt på total befolkning.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     year,
# MAGIC     pensjonsandel_pst,
# MAGIC     total_55_pluss,
# MAGIC     total_befolkning
# MAGIC FROM pensjonsandel_trend
# MAGIC ORDER BY year;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Graf: pensjonsandel-trend
# MAGIC
# MAGIC Grafen viser utviklingen i pensjonsandelen over tid.
# MAGIC
# MAGIC Den tilsvarer første hovedgraf i Streamlit-dashboardet.

# COMMAND ----------

fig_trend = px.line(
    trend_pdf,
    x="year",
    y="pensjonsandel_pst",
    markers=True,
    labels={
        "year": "År",
        "pensjonsandel_pst": "Andel 55+ (%)",
    },
    title="Pensjonsandel-trend (vektet nasjonalt)",
)

fig_trend.update_layout(
    yaxis_range=[
        max(0, trend_pdf["pensjonsandel_pst"].min() - 1),
        trend_pdf["pensjonsandel_pst"].max() + 1,
    ]
)

fig_trend.update_traces(line_width=2.5, marker_size=7, line_color=MAIN_COLOR, marker_color=MAIN_COLOR)
dashboard_layout(fig_trend, height=380)
fig_trend.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Aldersfordeling siste år
# MAGIC
# MAGIC Tabellen viser hvordan befolkningen fordeler seg på aldersgrupper i siste tilgjengelige år.
# MAGIC
# MAGIC Den viser både antall personer og andel av total befolkning.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     aldersgruppe,
# MAGIC     befolkning,
# MAGIC     ROUND(andel * 100, 1) AS andel_pst
# MAGIC FROM aldersgruppe_fordeling
# MAGIC ORDER BY aldersgruppe_sortering;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aldersstruktur: under 55 vs 55+
# MAGIC
# MAGIC De fleste innbyggere er fortsatt under 55 år.
# MAGIC
# MAGIC 55+ utgjør en betydelig del av befolkningen. Denne andelen øker over tid.

# COMMAND ----------

import pandas as pd

aldersfordeling_pdf = aldersgruppe_fordeling.orderBy("aldersgruppe_sortering").toPandas()
aldersfordeling_pdf["andel_pst"] = aldersfordeling_pdf["andel"] * 100

pensjonsgrupper = ["55-61", "62-66", "67-74", "75+"]

andel_55_pluss = (
    aldersfordeling_pdf
    .loc[aldersfordeling_pdf["aldersgruppe"].isin(pensjonsgrupper), "andel"]
    .sum() * 100
)

andel_under_55 = 100 - andel_55_pluss

split_pdf = pd.DataFrame({
    "gruppe": ["Under 55", "55+"],
    "andel_pst": [andel_under_55, andel_55_pluss],
})

fig_alder_split = px.bar(
    split_pdf,
    x="andel_pst",
    y=["Befolkning"] * len(split_pdf),
    color="gruppe",
    orientation="h",
    text=split_pdf["andel_pst"].map(lambda x: f"{x:.1f}%"),
    labels={
        "andel_pst": "Andel av befolkningen (%)",
        "y": "",
        "gruppe": "",
    },
    color_discrete_map={
        "Under 55": "#31688e",  # Viridis blue/teal
        "55+": "#fde725",       # Viridis yellow
    },
    title=f"Aldersstruktur: {andel_under_55:.1f}% under 55 og {andel_55_pluss:.1f}% 55+",
)

fig_alder_split.update_layout(
    barmode="stack",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis_range=[0, 100],
    yaxis_title="",
)

fig_alder_split.update_traces(
    textposition="inside",
    insidetextanchor="middle",
)

dashboard_layout(fig_alder_split, height=260)
fig_alder_split.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Aldersfordeling siste år
# MAGIC
# MAGIC Denne grafen viser befolkningen fordelt på aldersgrupper.
# MAGIC
# MAGIC Viridis-fargene brukes fra mørkere blå/grønn for yngre grupper til lysere gul/grønn for eldre grupper.

# COMMAND ----------

aldersfordeling_pdf["viridis_sortering"] = aldersfordeling_pdf["aldersgruppe_sortering"]

fig_alder = px.bar(
    aldersfordeling_pdf,
    x="aldersgruppe",
    y="befolkning",
    text=aldersfordeling_pdf["andel_pst"].map(lambda x: f"{x:.1f}%"),
    labels={
        "aldersgruppe": "Aldersgruppe",
        "befolkning": "Befolkning",
        "viridis_sortering": "Aldersgruppe",
    },
    color="viridis_sortering",
    color_continuous_scale="Viridis",
    title="Aldersfordeling siste år",
)

fig_alder.update_layout(
    showlegend=False,
    coloraxis_showscale=False,
)

fig_alder.update_traces(
    textposition="outside",
)

dashboard_layout(fig_alder, height=380)
fig_alder.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Kommuner med høyest andel 55+
# MAGIC
# MAGIC Tabellen viser kommunene med høyest andel innbyggere i aldersgruppen 55+.
# MAGIC
# MAGIC Dette identifiserer geografiske områder med høy demografisk pensjonsrelevans.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     kommune_label AS kommune,
# MAGIC     total_befolkning AS innbyggere,
# MAGIC     pension_age_befolkning AS antall_55_pluss,
# MAGIC     ROUND(pension_age_share * 100, 1) AS andel_pst
# MAGIC FROM top_kommuner
# MAGIC ORDER BY pension_age_share DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Graf: kommuner med høyest andel 55+
# MAGIC
# MAGIC Grafen rangerer de ti kommunene med høyest andel 55+.
# MAGIC
# MAGIC Den er laget som horisontal stolpegraf, slik som i Streamlit-dashboardet.

# COMMAND ----------

kommuner_pdf = (
    top_kommuner
    .withColumn("andel_pst", col("pension_age_share") * 100)
    .orderBy("pension_age_share", ascending=False)
    .limit(10)
    .toPandas()
)

fig_kommuner = px.bar(
    kommuner_pdf,
    x="andel_pst",
    y="kommune_label",
    orientation="h",
    text="andel_pst",
    labels={
        "andel_pst": "Andel 55+ (%)",
        "kommune_label": "",
    },
    color="andel_pst",
    color_continuous_scale="Viridis",
    title="Kommuner med høyest andel 55+",
)

fig_kommuner.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
)

fig_kommuner.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
dashboard_layout(fig_kommuner, height=430)
fig_kommuner.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Næringer etter estimert pensjonsvolum
# MAGIC
# MAGIC Tabellen viser næringer rangert etter estimert pensjonsvolum.
# MAGIC
# MAGIC Beregningen er:
# MAGIC
# MAGIC lønnstakere × månedslønn × 12 × 2 %
# MAGIC
# MAGIC Dette er ikke en faktisk premieprognose, men en enkel indikator for å sammenligne næringer.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     naering_label AS naering,
# MAGIC     lonsstakere,
# MAGIC     manedslonn,
# MAGIC     ROUND(estimert_pensjonsvolum / 1000000000.0, 2) AS volum_mrd
# MAGIC FROM naering_pensjonsvolum
# MAGIC WHERE naering_label != 'Alle næringer'
# MAGIC ORDER BY estimert_pensjonsvolum DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Graf: næringer etter estimert pensjonsvolum
# MAGIC
# MAGIC Grafen viser hvilke næringer som har høyest estimert pensjonsvolum.
# MAGIC
# MAGIC Den følger samme horisontale format som Streamlit-dashboardet.

# COMMAND ----------

naeringer_pdf = (
    naering_pensjonsvolum
    .filter(col("naering_label") != "Alle næringer")
    .withColumn("volum_mrd", col("estimert_pensjonsvolum") / 1000000000.0)
    .orderBy("estimert_pensjonsvolum", ascending=False)
    .limit(10)
    .toPandas()
)

fig_naering = px.bar(
    naeringer_pdf,
    x="volum_mrd",
    y="naering_label",
    orientation="h",
    text="volum_mrd",
    labels={
        "volum_mrd": "Est. pensjonsvolum (mrd kr)",
        "naering_label": "",
    },
    color="volum_mrd",
    color_continuous_scale="Viridis",
    title="Næringer etter estimert pensjonsvolum",
)

fig_naering.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
)

fig_naering.update_traces(texttemplate="%{text:.1f} mrd", textposition="outside")
dashboard_layout(fig_naering, height=430)
fig_naering.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12. Aldersgruppe-trend over tid
# MAGIC
# MAGIC Tabellen viser hvordan aldersgruppenes andel av befolkningen utvikler seg over tid.
# MAGIC
# MAGIC Dette gjør det mulig å se demografiske forskyvninger mellom yngre og eldre aldersgrupper.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     year,
# MAGIC     aldersgruppe,
# MAGIC     ROUND(andel * 100, 1) AS andel_pst
# MAGIC FROM aldersgruppe_trend
# MAGIC ORDER BY year, aldersgruppe_sortering;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13. Graf: aldersgruppe-trend over tid
# MAGIC
# MAGIC Grafen viser aldersgruppene som andel av befolkningen over tid.
# MAGIC
# MAGIC Dette tilsvarer arealgrafen nederst i Streamlit-dashboardet.

# COMMAND ----------

aldersgruppe_trend_pdf = aldersgruppe_trend.orderBy("year", "aldersgruppe_sortering").toPandas()
aldersgruppe_trend_pdf["andel_pst"] = aldersgruppe_trend_pdf["andel"] * 100

fig_ag = px.area(
    aldersgruppe_trend_pdf,
    x="year",
    y="andel_pst",
    color="aldersgruppe",
    labels={
        "year": "År",
        "andel_pst": "Andel (%)",
        "aldersgruppe": "Aldersgruppe",
    },
    color_discrete_sequence=COLOR_SCALE,
    title="Aldersgruppe-trend over tid",
)

fig_ag.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=-0.35),
)

dashboard_layout(fig_ag, height=430)
fig_ag.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Oppsummering
# MAGIC
# MAGIC Notebooken viser at Gold-laget fra Pensjon Lakehouse kan brukes direkte i Databricks.
# MAGIC
# MAGIC Analysen viser:
# MAGIC
# MAGIC - utvikling i pensjonsrelatert befolkningsandel over tid
# MAGIC - aldersfordeling i siste tilgjengelige år
# MAGIC - kommuner med høyest andel innbyggere 55+
# MAGIC - næringer med høyest estimert pensjonsvolum
# MAGIC - aldersgruppeutvikling over tid
# MAGIC
# MAGIC **Neste steg**
# MAGIC
# MAGIC - lage Databricks SQL Dashboard
# MAGIC - registrere Gold-data som permanente tabeller
# MAGIC - bruke Unity Catalog med Managed Identity
# MAGIC - koble Power BI til Databricks SQL Warehouse
# MAGIC
# MAGIC Data: SSB 07459 og SSB 11654  
# MAGIC Arkitektur: Python → DuckDB Bronze/Silver/Gold → Parquet → ADLS Gen2 → Databricks
