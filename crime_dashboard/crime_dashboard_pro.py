# =========================
# CRIME DASHBOARD PRO
# =========================

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import calendar

from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# =========================
# CONFIG
# =========================
base_path = r"C:\Users\ACER\Downloads"
os.makedirs(base_path, exist_ok=True)
os.chdir(base_path)

detail_file_id = "1mnGy6EMP9P-ukX-xRfbM12kMXgktGNWs"
agg_file_id = "1l1ZfgMdK667qkLALpk0LI3eJxDbHv5lP"

PRIMARY = "#7C3AED"
SECONDARY = "#5B21B6"
ACCENT = "#F43F5E"
BG = "#F4F7FC"
CARD = "#FFFFFF"
TEXT = "#1E293B"

# =========================
# URL
# =========================
def gdrive_to_download_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}"

detail_url = gdrive_to_download_url(detail_file_id)
agg_url = gdrive_to_download_url(agg_file_id)

# =========================
# LOAD DATA
# =========================
def safe_read_csv(url):
    try:
        df = pd.read_csv(url)
        print(f"✅ Loaded -> {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame()

df_agg = safe_read_csv(agg_url)
df_detail = safe_read_csv(detail_url)

# =========================
# CLEANING
# =========================
def normalize_cols(df):
    df.columns = [
        c.strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df

if not df_agg.empty:
    df_agg = normalize_cols(df_agg)

if not df_detail.empty:
    df_detail = normalize_cols(df_detail)

# =========================
# AREA NAME
# =========================
def ensure_area_name(df):
    if "area_name" not in df.columns:
        area_cols = [c for c in df.columns if "area" in c]
        if area_cols:
            df["area_name"] = df[area_cols[0]]
        else:
            df["area_name"] = "Unknown"

    df["area_name"] = (
        df["area_name"]
        .astype(str)
        .str.title()
        .str.strip()
    )

    return df

df_agg = ensure_area_name(df_agg)
df_detail = ensure_area_name(df_detail)

# =========================
# DATE
# =========================
date_cols = [
    "date_time_occ",
    "date_rptd",
    "date_occ"
]

for col in date_cols:
    if col in df_detail.columns:
        df_detail[col] = pd.to_datetime(df_detail[col], errors="coerce")

# =========================
# TIME FEATURES
# =========================
if "date_time_occ" in df_detail.columns:

    df_detail["hour_occ"] = df_detail["date_time_occ"].dt.hour
    df_detail["day_name"] = df_detail["date_time_occ"].dt.day_name()
    df_detail["day_of_week"] = df_detail["date_time_occ"].dt.weekday

# =========================
# SUMMARY
# =========================
summary = (
    df_detail.groupby("area_name")
    .size()
    .reset_index(name="total_crimes")
)

areas = sorted(df_detail["area_name"].dropna().unique())

# =========================
# APP
# =========================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]
)

app.title = "Crime Analytics Dashboard"

# =========================
# CARD STYLE
# =========================
CARD_STYLE = {
    "backgroundColor": CARD,
    "borderRadius": "16px",
    "padding": "16px",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.08)",
    "border": "none"
}

# =========================
# LAYOUT
# =========================
app.layout = dbc.Container([

    html.Br(),

    html.H2(
        "🚨 Crime Analytics Dashboard",
        style={
            "fontWeight": "700",
            "color": TEXT,
            "textAlign": "center"
        }
    ),

    html.P(
        "Analisis pola kriminalitas berdasarkan wilayah, waktu, dan hotspot kejadian.",
        style={
            "textAlign": "center",
            "color": "#64748B"
        }
    ),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Label(
                "Pilih Wilayah",
                style={"fontWeight": "600"}
            ),

            dcc.Dropdown(
                id="area-select",
                options=[
                    {"label": a, "value": a}
                    for a in areas
                ],
                value=areas[0],
                clearable=False
            )
        ], width=5)
    ], className="mb-4"),

    dbc.Row(id="kpi-row", className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id="heatmap-day-hour",
                        style={"height": "650px"}
                    )
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ], className="mb-4"),

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="hour-line")
                ])
            ], style=CARD_STYLE)
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="day-bar")
                ])
            ], style=CARD_STYLE)
        ], width=6)

    ], className="mb-4"),

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="map-chart")
                ])
            ], style=CARD_STYLE)
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="crime-chart")
                ])
            ], style=CARD_STYLE)
        ], width=6)

    ], className="mb-4"),

    html.Br(),

    dbc.Card([
        dbc.CardBody([

            html.H4(
                "📋 Detail Data",
                style={"fontWeight": "600"}
            ),

            dash_table.DataTable(
                id='data-table',

                page_size=10,

                style_table={
                    'overflowX': 'auto'
                },

                style_header={
                    'backgroundColor': PRIMARY,
                    'color': 'white',
                    'fontWeight': 'bold'
                },

                style_cell={
                    'padding': '10px',
                    'fontFamily': 'Segoe UI',
                    'fontSize': '14px',
                    'textAlign': 'left'
                },

                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#F8FAFC'
                    }
                ]
            )

        ])
    ], style=CARD_STYLE),

    html.Br()

], fluid=True, style={"backgroundColor": BG})

# =========================
# CALLBACK
# =========================
@app.callback(

    [
        Output("kpi-row", "children"),
        Output("heatmap-day-hour", "figure"),
        Output("hour-line", "figure"),
        Output("day-bar", "figure"),
        Output("map-chart", "figure"),
        Output("crime-chart", "figure"),
        Output("data-table", "data"),
        Output("data-table", "columns")
    ],

    [Input("area-select", "value")]
)

def update_dashboard(selected_area):

    dff = df_detail[
        df_detail["area_name"] == selected_area
    ]

    # =========================
    # KPI
    # =========================
    total_cases = len(dff)

    peak_hour = (
        dff["hour_occ"]
        .mode()[0]
        if not dff.empty else "-"
    )

    peak_day = (
        dff["day_name"]
        .mode()[0]
        if not dff.empty else "-"
    )

    top_crime = (
        dff["crm"]
        .mode()[0]
        if "crm" in dff.columns and not dff.empty
        else "-"
    )

    def build_card(title, value):

        return dbc.Col([

            dbc.Card([
                dbc.CardBody([

                    html.P(
                        title,
                        style={
                            "color": "#64748B",
                            "marginBottom": "5px"
                        }
                    ),

                    html.H2(
                        str(value),
                        style={
                            "fontWeight": "700",
                            "color": PRIMARY
                        }
                    )

                ])
            ], style=CARD_STYLE)

        ], width=3)

    kpi_row = [

        build_card("Total Kasus", total_cases),
        build_card("Jam Tersibuk", f"{peak_hour}:00"),
        build_card("Hari Tersibuk", peak_day),
        build_card("Top Crime", top_crime)

    ]

    # =========================
    # HEATMAP
    # =========================
    heat = (
        dff.groupby(["day_of_week", "hour_occ"])
        .size()
        .reset_index(name="count")
    )

    full = pd.MultiIndex.from_product(
        [range(7), range(24)],
        names=["day_of_week", "hour_occ"]
    ).to_frame(index=False)

    heat = (
        pd.merge(
            full,
            heat,
            on=["day_of_week", "hour_occ"],
            how="left"
        )
        .fillna(0)
    )

    heat["day_name"] = heat["day_of_week"].apply(
        lambda x: calendar.day_name[x]
    )

    heatmat = heat.pivot_table(
        index="day_name",
        columns="hour_occ",
        values="count"
    )

    day_order = [
        calendar.day_name[i]
        for i in range(7)
    ]

    heatmat = heatmat.reindex(day_order)

    fig_heat = px.imshow(
        heatmat.values,

        x=list(range(24)),
        y=heatmat.index,

        color_continuous_scale=[
            [0, "#1E1B4B"],
            [0.5, "#7C3AED"],
            [1, "#F43F5E"]
        ],

        labels={
            "x": "Jam",
            "y": "Hari",
            "color": "Total"
        },

        title="Heatmap Hari × Jam"
    )

    fig_heat.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font_color=TEXT
    )

    # =========================
    # HOUR LINE
    # =========================
    hour_counts = (
        dff.groupby("hour_occ")
        .size()
        .reset_index(name="count")
    )

    fig_hour = px.line(
        hour_counts,
        x="hour_occ",
        y="count",
        markers=True,
        title="Total Kejahatan per Jam"
    )

    fig_hour.update_traces(
        line_color=PRIMARY
    )

    fig_hour.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font_color=TEXT
    )

    # =========================
    # DAY BAR
    # =========================
    day_counts = (
        dff["day_name"]
        .value_counts()
        .reset_index()
    )

    day_counts.columns = ["Hari", "Jumlah"]

    fig_day = px.bar(
        day_counts,
        x="Hari",
        y="Jumlah",
        color="Jumlah",
        color_continuous_scale="purples",
        title="Total Kejahatan per Hari"
    )

    fig_day.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font_color=TEXT,
        coloraxis_showscale=False
    )

    # =========================
    # MAP
    # =========================
    fig_map = go.Figure()

    if "lat" in dff.columns and "lon" in dff.columns:

        pts = dff.dropna(subset=["lat", "lon"])

        fig_map = px.density_mapbox(
            pts,
            lat="lat",
            lon="lon",
            radius=8,
            zoom=10,

            mapbox_style="carto-darkmatter",

            color_continuous_scale="magma",

            title="Hotspot Lokasi Kejahatan"
        )

        fig_map.update_layout(
            margin=dict(t=50)
        )

    # =========================
    # TOP CRIME
    # =========================
    crime_counts = (
        dff["crm"]
        .value_counts()
        .nlargest(10)
        .reset_index()
    )

    crime_counts.columns = ["Crime", "Total"]

    fig_crime = px.bar(
        crime_counts,
        x="Crime",
        y="Total",
        color="Total",
        color_continuous_scale="purples",
        title="Top 10 Jenis Kejahatan"
    )

    fig_crime.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font_color=TEXT,
        coloraxis_showscale=False
    )

    # =========================
    # TABLE
    # =========================
    table_data = dff.head(200).to_dict("records")

    table_columns = [
        {"name": i, "id": i}
        for i in dff.columns
    ]

    return (
        kpi_row,
        fig_heat,
        fig_hour,
        fig_day,
        fig_map,
        fig_crime,
        table_data,
        table_columns
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":

    print("🚀 Dashboard running at http://127.0.0.1:8050")

    app.run(debug=True)