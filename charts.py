"""
charts.py — All Plotly chart builders for Runner Dashboard
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date, timedelta
from utils import seconds_to_pace_str

BG         = "rgba(0,0,0,0)"
GRID       = "rgba(255,255,255,0.06)"
ACCENT     = "#C8F04B"
ACCENT2    = "#4BF0C8"
MUTED      = "rgba(255,255,255,0.35)"
TEXT_MAIN  = "#F0F0EB"
FONT       = "DM Mono, monospace"


def _base_layout(title="", height=320):
    return dict(
        title=dict(text=title, font=dict(color=TEXT_MAIN, size=13, family=FONT), x=0.02),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT, color=MUTED, size=11),
        height=height,
        margin=dict(l=12, r=12, t=36, b=12),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=10)),
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
    )


def heatmap_calendar(df: pd.DataFrame) -> go.Figure:
    today = date.today()
    start = today - timedelta(weeks=52)
    all_dates = pd.date_range(start=start, end=today, freq="D")
    cal = pd.DataFrame({"date": all_dates})
    cal["date_only"] = cal["date"].dt.date

    # Valores: -1 = sin datos, 0 = descanso, 1 = entrenamiento, 2 = carrera oficial
    cal["val"]   = 0.0
    cal["km"]    = 0.0
    cal["label"] = ""

    if not df.empty and "date" in df.columns:
        active = df.copy()
        active["date_only"] = pd.to_datetime(active["date"]).dt.date

        # km por día
        agg_km = active.groupby("date_only")["distance_km"].sum().reset_index()
        agg_km.columns = ["date_only", "km"]

        # ¿tiene carrera oficial ese día?
        races = active[active["type"] == "Carrera Oficial"]["date_only"].unique()

        cal = cal.merge(agg_km, on="date_only", how="left", suffixes=("","_new"))
        if "km_new" in cal.columns:
            cal["km"] = cal["km_new"].fillna(0)
            cal.drop(columns=["km_new"], inplace=True)
        else:
            cal["km"] = cal["km"].fillna(0)

        # Asignar valor: 2=carrera, 1=entrenamiento, 0=descanso
        cal.loc[cal["km"] > 0, "val"] = 1.0
        cal.loc[cal["date_only"].isin(races), "val"] = 2.0

    cal["dow"]  = cal["date"].dt.dayofweek
    cal["week"] = ((cal["date"] - pd.Timestamp(start)).dt.days // 7)

    z    = np.zeros((7, 53))
    text = [["" for _ in range(53)] for _ in range(7)]

    for _, row in cal.iterrows():
        w, d = int(row["week"]), int(row["dow"])
        if w < 53:
            z[d][w] = float(row["val"])
            km_str = f" · {row['km']:.1f} km" if row["km"] > 0 else ""
            text[d][w] = f"{row['date_only']}{km_str}"

    # 0 = descanso (gris oscuro), 1 = entrenamiento (verde), 2 = carrera (amarillo)
    colorscale = [
        [0.0,  "#1E1E1E"],   # 0: descanso → gris oscuro
        [0.49, "#1E1E1E"],
        [0.50, "#2E6B28"],   # 1: entrenamiento → verde medio
        [0.74, ACCENT],      # verde lima brillante
        [0.75, "#F0C84B"],   # 2: carrera oficial → amarillo
        [1.0,  "#FFD700"],   # amarillo dorado
    ]

    fig = go.Figure(go.Heatmap(
        z=z, text=text,
        hovertemplate="%{text}<extra></extra>",
        colorscale=colorscale,
        zmin=0, zmax=2,
        showscale=False,
        xgap=3, ygap=3,
    ))

    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    layout = _base_layout("Actividad — Últimas 52 Semanas", height=200)
    layout["yaxis"] = dict(
        tickvals=list(range(7)), ticktext=day_labels,
        showgrid=False, zeroline=False,
        tickfont=dict(size=9, color=MUTED),
    )
    layout["xaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_layout(**layout)
    return fig


def weekly_km_bars(weekly: pd.DataFrame) -> go.Figure:
    if weekly.empty:
        return _empty_fig("Sin datos aún")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly["week"], y=weekly["km"],
        marker=dict(color=weekly["km"], colorscale=[[0,"#1D3318"],[1,ACCENT]], line=dict(width=0)),
        hovertemplate="<b>%{x|%d %b}</b><br>%{y:.1f} km<extra></extra>",
        name="km semanales",
    ))
    fig.update_layout(**_base_layout("Kilómetros por Semana", height=280))
    fig.update_xaxes(tickformat="%d %b", tickangle=-30)
    return fig


def pace_evolution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "pace_s_km" not in df.columns:
        return _empty_fig("Sin datos aún")
    d = df.dropna(subset=["pace_s_km"]).sort_values("date")
    if d.empty:
        return _empty_fig("Sin datos de ritmo")
    fig = go.Figure()
    d["pace_roll"] = d["pace_s_km"].rolling(5, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["pace_s_km"]/60, mode="markers",
        marker=dict(size=6, color=ACCENT2, opacity=0.55),
        name="Ritmo real",
        hovertemplate="%{x|%d %b}<br>%{customdata} /km<extra></extra>",
        customdata=[seconds_to_pace_str(int(v)) for v in d["pace_s_km"]],
    ))
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["pace_roll"]/60, mode="lines",
        line=dict(color=ACCENT, width=2.5, shape="spline"),
        name="Media móvil (5)",
        hovertemplate="%{x|%d %b}<br>Tend: %{customdata} /km<extra></extra>",
        customdata=[seconds_to_pace_str(int(v)) for v in d["pace_roll"]],
    ))
    fig.update_yaxes(autorange="reversed", tickformat=".1f",
                     title=dict(text="min/km", font=dict(size=10, color=MUTED)))
    fig.update_layout(**_base_layout("Evolución del Ritmo", height=300))
    return fig


def distance_by_type(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig("Sin datos aún")
    agg = df.groupby("type")["distance_km"].sum().reset_index().sort_values("distance_km", ascending=True)
    colors = [ACCENT if i == len(agg)-1 else ACCENT2 for i in range(len(agg))]
    fig = go.Figure(go.Bar(
        x=agg["distance_km"], y=agg["type"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="%{y}<br><b>%{x:.1f} km</b><extra></extra>",
    ))
    fig.update_layout(**_base_layout("km por Tipo de Entrenamiento", height=260))
    fig.update_xaxes(title=dict(text="km", font=dict(size=10, color=MUTED)), showgrid=True, gridcolor=GRID)
    fig.update_yaxes(showgrid=False)
    return fig


def marathon_phase_gauge(km_done: float, km_target: float, phase_name: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=km_done,
        delta={"reference": km_target, "valueformat": ".0f",
               "increasing": {"color": ACCENT}, "suffix": " km meta"},
        number={"suffix": " km", "font": {"color": TEXT_MAIN, "size": 28, "family": FONT}},
        gauge={
            "axis": {"range": [0, km_target], "tickcolor": MUTED, "tickfont": {"size": 9, "color": MUTED}},
            "bar": {"color": ACCENT, "thickness": 0.25},
            "bgcolor": "#111", "bordercolor": GRID,
            "steps": [
                {"range": [0, km_target*0.5], "color": "#1A2A1A"},
                {"range": [km_target*0.5, km_target*0.8], "color": "#1D3318"},
                {"range": [km_target*0.8, km_target], "color": "#2E5020"},
            ],
            "threshold": {"line": {"color": ACCENT2, "width": 3}, "thickness": 0.8, "value": km_target},
        },
        title={"text": phase_name, "font": {"color": MUTED, "size": 11, "family": FONT}},
    ))
    fig.update_layout(paper_bgcolor=BG, height=220, margin=dict(l=20, r=20, t=40, b=10))
    return fig


def _empty_fig(msg="Sin datos"):
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color=MUTED, size=14, family=FONT))
    fig.update_layout(**_base_layout(height=200))
    return fig
