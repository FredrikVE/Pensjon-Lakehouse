# pensjon-lakehouse/dashboard/app.py
import streamlit as st
import duckdb
import plotly.express as px

DB_PATH = "pensjon.duckdb"

@st.cache_resource
def get_db():
    return duckdb.connect(DB_PATH, read_only=True)


def query(sql: str):
    return get_db().execute(sql).fetchdf()


##########################
# Page config           #
#########################

st.set_page_config(
    page_title="Pensjon Lakehouse",
    layout="wide",
)

st.title("Pensjon Lakehouse — Gold-laget")
st.caption("Analyser basert på SSB befolknings- og lønnsdata  ·  DuckDB Bronze → Silver → Gold")

##########################
# KPIs                  #
#########################

trend = query("SELECT * FROM gold.pensjonsandel_trend ORDER BY year")

if not trend.empty:
    latest = trend.iloc[-1]
    prev = trend.iloc[-2] if len(trend) > 1 else latest

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Pensjonsandel (55+)",
        f"{latest['pensjonsandel_pst']:.1f} %",
        f"{latest['pensjonsandel_pst'] - prev['pensjonsandel_pst']:.2f} pp" if len(trend) > 1 else None,
    )
    col2.metric(
        "Totalt 55+",
        f"{int(latest['total_55_pluss']):,}".replace(",", " "),
    )
    col3.metric(
        "Total befolkning",
        f"{int(latest['total_befolkning']):,}".replace(",", " "),
    )

st.divider()

#########################
# Layout: two columns   #
#########################

left, right = st.columns(2)

#########################
# Pensjonsandel-trend   #
#########################

with left:
    st.subheader("Pensjonsandel-trend (vektet nasjonalt)")

    fig_trend = px.line(
        trend,
        x="year",
        y="pensjonsandel_pst",
        markers=True,
        labels={"year": "År", "pensjonsandel_pst": "Andel 55+ (%)"},
    )
    fig_trend.update_layout(
        yaxis_range=[
            max(0, trend["pensjonsandel_pst"].min() - 1),
            trend["pensjonsandel_pst"].max() + 1,
        ],
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

##########################
# Aldersgruppe-fordeling #
#########################

with right:
    st.subheader("Aldersfordeling siste år")

    aldersgrupper = query(
        "SELECT aldersgruppe, befolkning, andel FROM gold.aldersgruppe_fordeling ORDER BY aldersgruppe_sortering"
    )

    fig_alder = px.bar(
        aldersgrupper,
        x="aldersgruppe",
        y="befolkning",
        text=aldersgrupper["andel"].apply(lambda x: f"{x*100:.1f}%"),
        labels={"aldersgruppe": "Aldersgruppe", "befolkning": "Befolkning"},
        color="aldersgruppe",
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )
    fig_alder.update_layout(
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_alder, use_container_width=True)

st.divider()

left2, right2 = st.columns(2)

##########################
# Top kommuner          #
#########################

with left2:
    st.subheader("Kommuner med høyest andel 55+")

    kommuner = query("""
        SELECT
            kommune_label AS kommune,
            total_befolkning AS innbyggere,
            pension_age_befolkning AS "55+",
            ROUND(pension_age_share * 100, 1) AS andel_pst
        FROM gold.top_kommuner_pensjonsalder
        ORDER BY andel_pst DESC
        LIMIT 10
    """)

    fig_kommuner = px.bar(
        kommuner,
        x="andel_pst",
        y="kommune",
        orientation="h",
        text="andel_pst",
        labels={"andel_pst": "Andel 55+ (%)", "kommune": ""},
        color="andel_pst",
        color_continuous_scale="OrRd",
    )
    fig_kommuner.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig_kommuner.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig_kommuner, use_container_width=True)

################################
# Næringer etter pensjonsvolum #
###############################

with right2:
    st.subheader("Næringer etter estimert pensjonsvolum")

    naeringer = query("""
        SELECT
            naering_label AS naering,
            lonsstakere,
            manedslonn,
            ROUND(estimert_pensjonsvolum / 1e9, 2) AS volum_mrd
        FROM gold.naering_pensjonsvolum
        WHERE naering_label != 'Alle næringer'
        ORDER BY volum_mrd DESC
        LIMIT 10
    """)

    fig_naering = px.bar(
        naeringer,
        x="volum_mrd",
        y="naering",
        orientation="h",
        text="volum_mrd",
        labels={"volum_mrd": "Est. pensjonsvolum (mrd kr)", "naering": ""},
        color="volum_mrd",
        color_continuous_scale="Blues",
    )
    fig_naering.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig_naering.update_traces(texttemplate="%{text:.1f} mrd", textposition="outside")
    st.plotly_chart(fig_naering, use_container_width=True)

##########################
# Aldersgruppe-trend     #
#########################

st.divider()
st.subheader("Aldersgruppe-trend over tid")

ag_trend = query("""
    SELECT year, aldersgruppe, ROUND(andel * 100, 1) AS andel_pst
    FROM gold.aldersgruppe_trend
    ORDER BY year, aldersgruppe_sortering
""")

fig_ag = px.area(
    ag_trend,
    x="year",
    y="andel_pst",
    color="aldersgruppe",
    labels={"year": "År", "andel_pst": "Andel (%)", "aldersgruppe": "Aldersgruppe"},
    color_discrete_sequence=px.colors.sequential.Tealgrn,
)
fig_ag.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=-0.3),
)
st.plotly_chart(fig_ag, use_container_width=True)

##########################
# Footer                #
#########################

st.divider()
st.caption(
    "Data: SSB tabell 07459 (befolkning) og 11654 (lønn/sysselsetting)  ·  "
    "Arkitektur: Python → DuckDB (Bronze/Silver/Gold) → Parquet → Streamlit"
)
