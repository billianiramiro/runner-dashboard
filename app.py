"""
app.py — Runner Dashboard  |  Operación Maratón 2028
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date

from database import (
    initialize_db, insert_workout, delete_workout,
    get_all_workouts, get_weekly_summary,
    get_total_km_since, get_km_between,
    TRAINING_TYPES, MARATHON_PHASES,
)
from utils import (
    hms_to_seconds, seconds_to_hms, seconds_to_pace_str,
    pace_str_to_seconds, calc_pace, calc_duration, calc_distance,
)
from charts import (
    heatmap_calendar, weekly_km_bars, pace_evolution,
    distance_by_type, marathon_phase_gauge,
)
from styles import CSS

st.set_page_config(
    page_title="Runner Dashboard · 2028",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)
initialize_db()

for k, v in [("dist",""),("time_str",""),("pace_str",""),("auto_field",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

def _f(v):
    try: return float(v)
    except: return None

def on_change():
    dist = _f(st.session_state.get("_dist"))
    t_s  = hms_to_seconds(st.session_state.get("_time",""))
    p_s  = pace_str_to_seconds(st.session_state.get("_pace",""))
    st.session_state["dist"]     = st.session_state.get("_dist","")
    st.session_state["time_str"] = st.session_state.get("_time","")
    st.session_state["pace_str"] = st.session_state.get("_pace","")
    st.session_state["auto_field"] = None
    if dist and t_s and not p_s:
        pace = calc_pace(dist, t_s)
        if pace:
            st.session_state["pace_str"] = seconds_to_pace_str(pace)
            st.session_state["auto_field"] = "pace"
    elif dist and p_s and not t_s:
        dur = calc_duration(dist, p_s)
        if dur:
            st.session_state["time_str"] = seconds_to_hms(dur)
            st.session_state["auto_field"] = "tiempo"
    elif t_s and p_s and not dist:
        d = calc_distance(t_s, p_s)
        if d:
            st.session_state["dist"] = str(d)
            st.session_state["auto_field"] = "distancia"

def clear_form():
    for k in ["dist","time_str","pace_str","auto_field","_dist","_time","_pace"]:
        st.session_state[k] = "" if k != "auto_field" else None

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='font-family:Syne,sans-serif;font-size:1rem;"
        "letter-spacing:0.1em;text-transform:uppercase;color:#C8F04B;"
        "margin-bottom:1.2rem'>⚡ Nuevo Entrenamiento</h2>",
        unsafe_allow_html=True)

    workout_date  = st.date_input("Fecha", value=date.today())
    training_type = st.selectbox("Tipo", TRAINING_TYPES)
    race_name = ""
    if training_type == "Carrera Oficial":
        race_name = st.text_input("Nombre de la carrera", placeholder="Maratón de Buenos Aires")

    st.markdown("<p style='font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;"
                "color:rgba(240,240,235,0.35);margin:1rem 0 0.3rem'>Métricas</p>",
                unsafe_allow_html=True)

    auto = st.session_state.get("auto_field")

    st.text_input(
        "Distancia (km)" + (" 🔄" if auto=="distancia" else ""),
        value=st.session_state["dist"],
        placeholder="21.1", key="_dist", on_change=on_change)
    st.text_input(
        "Tiempo (h:mm:ss)" + (" 🔄" if auto=="tiempo" else ""),
        value=st.session_state["time_str"],
        placeholder="1:45:00", key="_time", on_change=on_change)
    st.text_input(
        "Ritmo (mm:ss /km)" + (" 🔄" if auto=="pace" else ""),
        value=st.session_state["pace_str"],
        placeholder="5:00", key="_pace", on_change=on_change)

    if auto:
        st.markdown(f"<p class='auto-calc-badge'>✦ {auto} calculado automáticamente</p>",
                    unsafe_allow_html=True)

    notes = st.text_area("Notas", placeholder="Sensaciones, clima, RPE…", height=68)
    c1, c2 = st.columns(2)
    save  = c1.button("Guardar",  use_container_width=True)
    clear = c2.button("Limpiar",  use_container_width=True)

    if clear:
        clear_form(); st.rerun()

    if save:
        dist_f = _f(st.session_state.get("_dist") or st.session_state["dist"])
        t_s    = hms_to_seconds(st.session_state.get("_time") or st.session_state["time_str"])
        p_s    = pace_str_to_seconds(st.session_state.get("_pace") or st.session_state["pace_str"])
        if not any([dist_f, t_s, p_s]):
            st.error("Ingresá al menos una métrica.")
        else:
            try:
                insert_workout(workout_date.isoformat(), training_type,
                               dist_f, t_s, p_s, notes, race_name)
                st.success("✓ Guardado")
                clear_form()
                import time; time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    st.markdown("<hr><p style='font-size:0.62rem;color:rgba(240,240,235,0.18);"
                "text-align:center;letter-spacing:0.08em'>"
                "OPERACIÓN MARATÓN<br>SEPTIEMBRE 2028</p>", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────
st.markdown(
    "<h1 style='font-family:Syne,sans-serif;font-size:1.9rem;"
    "letter-spacing:-0.03em;color:#F0F0EB;margin-bottom:0'>"
    "Runner Dashboard</h1>"
    "<p style='font-size:0.7rem;letter-spacing:0.18em;text-transform:uppercase;"
    "color:rgba(240,240,235,0.3);margin-top:0.1rem'>"
    "Operación Maratón · 14 Sep 2028</p>",
    unsafe_allow_html=True)

df_all   = get_all_workouts()
today    = date.today()
km_month = get_total_km_since(today.replace(day=1).isoformat())
km_year  = get_total_km_since(f"{today.year}-01-01")
km_proj  = get_total_km_since("2025-10-13")
sessions = len(df_all)
avg_pace = df_all["pace_s_km"].dropna().mean() if not df_all.empty else None
last_run = df_all.iloc[0]["date"].strftime("%d %b %Y") if not df_all.empty else "—"

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("km este mes",    f"{km_month:.1f}")
k2.metric("km este año",    f"{km_year:.1f}")
k3.metric("Sesiones total", str(sessions))
k4.metric("Ritmo prom.",    seconds_to_pace_str(int(avg_pace))+"/km" if avg_pace else "—")
k5.metric("Último run",     last_run)
st.markdown("<hr>", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊  Overview","📈  Analítica","🏁  Maratón 2028","📋  Historial"])

# ── Tab 1 ─────────────────────────────────────────────────
with t1:
    st.markdown("#### Actividad")
    st.plotly_chart(heatmap_calendar(df_all), use_container_width=True,
                    key="chart_heatmap", config={"displayModeBar":False})

    st.markdown(
        "<p style='font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;"
        "color:rgba(240,240,235,0.35);margin:1.2rem 0 0.4rem'>Intensidad por Mes</p>",
        unsafe_allow_html=True)

    if df_all.empty:
        st.info("Cargá entrenamientos para ver el mapa de calor.")
    else:
        import plotly.graph_objects as go
        import numpy as np
        from scipy.ndimage import gaussian_filter

        d = df_all.copy()
        d["mes_num"] = d["date"].dt.month + (d["date"].dt.year - d["date"].dt.year.min()) * 12

        # Construir todos los meses desde el primero hasta hoy
        first_date = d["date"].min()
        last_date  = pd.Timestamp(today)
        all_months = pd.period_range(
            start=first_date.to_period("M"),
            end=last_date.to_period("M"),
            freq="M"
        )

        month_names = []
        km_per_month = []
        for p in all_months:
            names = ["","Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
            month_names.append(f"{names[p.month]} {str(p.year)[2:]}")
            mask = (d["date"].dt.year == p.year) & (d["date"].dt.month == p.month)
            km_per_month.append(d.loc[mask, "distance_km"].sum())

        n = len(km_per_month)
        # Repetir cada mes en varias filas para dar altura y suavizar
        rows   = 8
        z_raw  = np.array([km_per_month] * rows, dtype=float)

        # Suavizado gaussiano — crea el efecto de gradiente continuo
        z_smooth = gaussian_filter(z_raw, sigma=[1.2, 1.5])

        colorscale = [
            [0.0,  "#0D0D0D"],
            [0.15, "#0A1A0A"],
            [0.30, "#1A3A0A"],
            [0.50, "#4A8A10"],
            [0.70, "#C8F04B"],
            [0.85, "#FFD700"],
            [1.0,  "#FF4500"],
        ]

        hover = [[
            f"<b>{month_names[j]}</b><br>{km_per_month[j]:.1f} km"
            for j in range(n)
        ] * rows][0]
        hover_matrix = [hover] * rows

        fig_smooth = go.Figure(go.Heatmap(
            z=z_smooth,
            x=month_names,
            text=hover_matrix,
            hovertemplate="%{text}<extra></extra>",
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                thickness=10,
                tickfont=dict(size=9, color="rgba(240,240,235,0.45)",
                              family="DM Mono, monospace"),
                title=dict(text="km", side="right",
                           font=dict(size=10, color="rgba(240,240,235,0.45)",
                                     family="DM Mono, monospace")),
                bgcolor="rgba(0,0,0,0)",
                outlinewidth=0,
            ),
            xgap=0, ygap=0,
            zsmooth="best",
        ))

        fig_smooth.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=220,
            margin=dict(l=12, r=60, t=10, b=40),
            font=dict(family="DM Mono, monospace",
                      color="rgba(240,240,235,0.45)", size=10),
            xaxis=dict(
                showgrid=False, zeroline=False,
                tickangle=-30, tickfont=dict(size=9),
                tickmode="array",
                tickvals=list(range(n)),
                ticktext=month_names,
            ),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        st.plotly_chart(fig_smooth, use_container_width=True,
                        key="chart_heat2", config={"displayModeBar":False})

# ── Tab 2 ─────────────────────────────────────────────────
with t2:
    from datetime import timedelta

    st.plotly_chart(pace_evolution(df_all), use_container_width=True,
                    key="chart_pace", config={"displayModeBar":False})

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;"
        "color:rgba(240,240,235,0.35);margin-bottom:1rem'>Últimas 52 Semanas</p>",
        unsafe_allow_html=True)

    if df_all.empty:
        st.info("Registrá tus primeros entrenamientos para ver la analítica.")
    else:
        # ── Calcular estadísticas 52 semanas ──────────────
        since_52 = (today - timedelta(weeks=52)).isoformat()
        df_52 = df_all[df_all["date"] >= since_52].copy()

        total_days_period = 364
        dias_corridos     = df_52["date"].dt.date.nunique()
        dias_descanso     = total_days_period - dias_corridos
        km_total_52       = df_52["distance_km"].sum()
        sesiones_52       = len(df_52)
        mejor_ritmo       = df_52["pace_s_km"].dropna().min()
        km_max_semana     = 0
        if not df_52.empty:
            df_52["week"] = df_52["date"].dt.to_period("W")
            km_max_semana = df_52.groupby("week")["distance_km"].sum().max()

        # ── Fila de stats ──────────────────────────────────
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Días corridos",  str(dias_corridos))
        s2.metric("Días descanso",  str(dias_descanso))
        s3.metric("km totales",     f"{km_total_52:.1f}")
        s4.metric("Mejor ritmo",    seconds_to_pace_str(int(mejor_ritmo)) + "/km" if mejor_ritmo else "—")
        s5.metric("Mejor semana",   f"{km_max_semana:.1f} km" if km_max_semana else "—")

        # ── Gráfico de dona + listado tipos ───────────────
        col_pie, col_list = st.columns([2, 1])

        with col_pie:
            if not df_52.empty:
                import plotly.graph_objects as go
                type_agg = df_52.groupby("type")["distance_km"].sum().reset_index()
                type_agg.columns = ["tipo", "km"]
                type_agg = type_agg[type_agg["km"] > 0].sort_values("km", ascending=False)

                COLORS = ["#C8F04B","#4BF0C8","#F0C84B","#F04B8A","#8A4BF0","#4B8AF0"]

                fig_donut = go.Figure(go.Pie(
                    labels=type_agg["tipo"],
                    values=type_agg["km"],
                    hole=0.55,
                    marker=dict(colors=COLORS[:len(type_agg)],
                                line=dict(color="#0D0D0D", width=2)),
                    textinfo="percent",
                    textfont=dict(size=11, color="#F0F0EB", family="DM Mono, monospace"),
                    hovertemplate="<b>%{label}</b><br>%{value:.1f} km · %{percent}<extra></extra>",
                ))
                fig_donut.add_annotation(
                    text=f"<b>{km_total_52:.0f}</b><br><span style='font-size:10px'>km</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, color="#C8F04B", family="Syne, sans-serif"),
                )
                fig_donut.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=280,
                    margin=dict(l=10, r=10, t=20, b=10),
                )
                st.plotly_chart(fig_donut, use_container_width=True,
                                key="chart_donut", config={"displayModeBar":False})

        with col_list:
            st.markdown("<div style='padding-top:0.6rem'>", unsafe_allow_html=True)
            if not df_52.empty:
                type_agg2 = df_52.groupby("type").agg(
                    km=("distance_km","sum"),
                    sesiones=("id","count")
                ).reset_index().sort_values("km", ascending=False)

                for i, (_, row) in enumerate(type_agg2.iterrows()):
                    color = COLORS[i % len(COLORS)]
                    pct   = int(row["km"] / km_total_52 * 100) if km_total_52 > 0 else 0
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:10px;"
                        f"margin-bottom:10px'>"
                        f"<div style='width:10px;height:10px;border-radius:50%;"
                        f"background:{color};flex-shrink:0'></div>"
                        f"<div style='flex:1'>"
                        f"<p style='font-size:0.78rem;font-weight:500;margin:0;color:#F0F0EB'>{row['type']}</p>"
                        f"<p style='font-size:0.68rem;color:rgba(240,240,235,0.4);margin:0'>"
                        f"{row['km']:.1f} km · {int(row['sesiones'])} ses. · {pct}%</p>"
                        f"</div></div>",
                        unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ── Tab 3: Maratón 2028 ───────────────────────────────────
with t3:
    marathon_date = date(2028, 9, 14)
    days_left     = (marathon_date - today).days
    weeks_left    = days_left // 7

    # ── Countdown hero ────────────────────────────────────
    st.markdown(
        f"<div style='text-align:center;padding:1.2rem 0 1.8rem'>"
        f"<p style='font-size:0.68rem;letter-spacing:0.2em;text-transform:uppercase;"
        f"color:rgba(240,240,235,0.38)'>Faltan</p>"
        f"<h2 style='font-size:3.2rem;font-family:Syne,sans-serif;"
        f"letter-spacing:-0.04em;color:#C8F04B;margin:0'>{days_left:,}</h2>"
        f"<p style='font-size:0.78rem;color:rgba(240,240,235,0.42)'>"
        f"días · {weeks_left} semanas · Maratón 14 Sep 2028</p>"
        f"</div>",
        unsafe_allow_html=True)

    # ── Plan Maestro por años ─────────────────────────────
    st.markdown(
        "<p style='font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;"
        "color:rgba(240,240,235,0.35);margin-bottom:1rem'>Plan Maestro</p>",
        unsafe_allow_html=True)

    # Group phases by year
    years = {}
    for phase in MARATHON_PHASES:
        y = phase["year"]
        if y not in years:
            years[y] = []
        years[y].append(phase)

    YEAR_COLORS = {
        "Año 1": {"accent": "#C8F04B", "track": "#1A2A0A"},
        "Año 2": {"accent": "#4BF0C8", "track": "#0A1A1A"},
        "Año 3": {"accent": "#F04B8A", "track": "#1A0A12"},
    }

    for year_label, phases in years.items():
        yc = YEAR_COLORS.get(year_label, {"accent": "#C8F04B", "track": "#1A1A1A"})
        accent = yc["accent"]
        track_bg = yc["track"]

        st.markdown(
            f"<p style='font-size:0.72rem;font-weight:600;letter-spacing:0.14em;"
            f"text-transform:uppercase;color:{accent};margin:1.4rem 0 0.6rem'>"
            f"── {year_label}</p>",
            unsafe_allow_html=True)

        for phase in phases:
            p_start    = date.fromisoformat(phase["start"])
            p_end      = date.fromisoformat(phase["end"])
            km_target  = phase["km_target"]
            km_done    = get_km_between(phase["start"], phase["end"])
            km_done    = min(km_done, km_target)

            total_days   = max((p_end - p_start).days, 1)
            elapsed_days = max(min((today - p_start).days, total_days), 0)
            time_pct     = int(elapsed_days / total_days * 100)
            km_pct       = int(km_done / km_target * 100) if km_target else 0

            if today < p_start:
                status, status_color, dot = "Próxima", "rgba(240,240,235,0.28)", "○"
            elif today > p_end:
                status, status_color, dot = "Completada", "#4BF0C8", "✓"
            else:
                status, status_color, dot = "En curso", accent, "●"

            # Days remaining or days ago
            if today < p_start:
                days_info = f"Empieza en {(p_start - today).days} días"
            elif today > p_end:
                days_info = f"Finalizó hace {(today - p_end).days} días"
            else:
                days_info = f"{(p_end - today).days} días restantes"

            weekly_ref = phase.get("weekly_ref", "")
            st.markdown(f"""
<div style='background:#141414;border:1px solid rgba(255,255,255,0.07);
     border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem'>

  <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>
    <div>
      <span style='font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;
            color:rgba(240,240,235,0.35)'>{phase["sub"]}</span>
      <p style='font-size:0.95rem;font-weight:600;color:#F0F0EB;margin:2px 0 0'>{phase["name"]}</p>
      <p style='font-size:0.7rem;color:rgba(240,240,235,0.35);margin:1px 0 0'>{phase["desc"]}</p>
      <p style='font-size:0.68rem;color:{accent};margin:3px 0 0'>Objetivo: {weekly_ref} · {km_target} km totales</p>
    </div>
    <div style='text-align:right;flex-shrink:0;margin-left:12px'>
      <span style='font-size:0.72rem;color:{status_color}'>{dot} {status}</span><br>
      <span style='font-size:0.65rem;color:rgba(240,240,235,0.3)'>{days_info}</span>
    </div>
  </div>

  <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
    <span style='font-size:0.65rem;color:rgba(240,240,235,0.4)'>
      {p_start.strftime('%d %b %Y')} → {p_end.strftime('%d %b %Y')}
    </span>
    <span style='font-size:0.65rem;color:rgba(240,240,235,0.4)'>
      {km_done:.0f} / {km_target} km &nbsp;·&nbsp; {km_pct}%
    </span>
  </div>

  <div style='position:relative;height:6px;background:{track_bg};
       border-radius:99px;overflow:hidden;margin-bottom:5px'>
    <div style='position:absolute;left:0;top:0;height:100%;width:{time_pct}%;
         background:rgba(255,255,255,0.1);border-radius:99px'></div>
    <div style='position:absolute;left:0;top:0;height:100%;width:{km_pct}%;
         background:linear-gradient(90deg,{track_bg},{accent});
         border-radius:99px;transition:width 0.6s'></div>
  </div>

  <div style='display:flex;justify-content:space-between'>
    <span style='font-size:0.6rem;color:rgba(240,240,235,0.25)'>
      Tiempo transcurrido: {time_pct}%
    </span>
    <span style='font-size:0.6rem;color:{accent}'>
      km completados: {km_pct}%
    </span>
  </div>

</div>""", unsafe_allow_html=True)

    # ── Resumen total con ritmo adaptativo ────────────────
    from datetime import timedelta
    total_target = sum(p["km_target"] for p in MARATHON_PHASES)

    # Fase activa actual
    active_phase = next(
        (p for p in MARATHON_PHASES
         if date.fromisoformat(p["start"]) <= today <= date.fromisoformat(p["end"])),
        None
    )

    # km/sem necesarios = km restantes de la fase activa / semanas hasta que termina
    if active_phase:
        phase_end      = date.fromisoformat(active_phase["end"])
        weeks_to_end   = max((phase_end - today).days / 7, 0.5)
        km_done_phase  = get_km_between(active_phase["start"], active_phase["end"])
        km_left_phase  = max(active_phase["km_target"] - km_done_phase, 0)
        weekly_need    = km_left_phase / weeks_to_end
        phase_context  = f"para terminar {active_phase['sub']}"
    else:
        # Si no hay fase activa, usar semanas hasta el maratón
        weekly_need   = (total_target - km_proj) / weeks_left if weeks_left > 0 else 0
        phase_context = "para cumplir el plan"

    # Ritmo reciente: últimas 4 semanas, pero si hay 0 km
    # buscamos hacia atrás hasta encontrar actividad (máx 12 semanas)
    avg_weekly_recent = 0.0
    weeks_sampled     = 4
    for w in [4, 8, 12]:
        since = (today - timedelta(weeks=w)).isoformat()
        km_w  = get_total_km_since(since)
        if km_w > 0:
            avg_weekly_recent = km_w / w
            weeks_sampled     = w
            break

    diff = avg_weekly_recent - weekly_need

    if avg_weekly_recent == 0:
        ref_str = active_phase.get("weekly_ref", "~7 km/sem") if active_phase else "~7 km/sem"
        trend_color = "#F04B4B"
        trend_icon  = "▼"
        trend_title = "Sin actividad reciente"
        trend_label = f"Empezá con {ref_str} e irás aumentando progresivamente"
    elif diff >= 0:
        trend_color = "#C8F04B"
        trend_icon  = "▲"
        trend_title = "En ritmo 🎯"
        trend_label = f"+{diff:.1f} km/sem sobre la meta · vas bien"
    elif diff >= -8:
        trend_color = "#F0C84B"
        trend_icon  = "◆"
        trend_title = "Cerca de la meta"
        trend_label = f"Te faltan {abs(diff):.1f} km/sem para alcanzar el objetivo"
    else:
        trend_color = "#F04B4B"
        trend_icon  = "▼"
        trend_title = "Necesitás subir el volumen"
        trend_label = f"Estás {abs(diff):.1f} km/sem por debajo de lo necesario"

    reciente_label = f"últ. {weeks_sampled} sem" if avg_weekly_recent > 0 else "sin actividad"

    st.markdown(
        f"<div style='display:flex;gap:1rem;margin-top:1.2rem;flex-wrap:wrap'>"

        f"<div class='runner-card' style='flex:1;min-width:120px;text-align:center'>"
        f"<p style='font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;"
        f"color:rgba(240,240,235,0.38);margin:0'>km acumulados</p>"
        f"<p style='font-size:1.8rem;font-family:Syne;color:#C8F04B;margin:4px 0'>{km_proj:.0f}</p>"
        f"<p style='font-size:0.66rem;color:rgba(240,240,235,0.3)'>de {total_target} km totales</p>"
        f"</div>"

        f"<div class='runner-card' style='flex:1;min-width:120px;text-align:center'>"
        f"<p style='font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;"
        f"color:rgba(240,240,235,0.38);margin:0'>ritmo reciente</p>"
        f"<p style='font-size:1.8rem;font-family:Syne;color:#4BF0C8;margin:4px 0'>{avg_weekly_recent:.1f}</p>"
        f"<p style='font-size:0.66rem;color:rgba(240,240,235,0.3)'>km/sem · {reciente_label}</p>"
        f"</div>"

        f"<div class='runner-card' style='flex:1;min-width:120px;text-align:center'>"
        f"<p style='font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;"
        f"color:rgba(240,240,235,0.38);margin:0'>meta fase actual</p>"
        f"<p style='font-size:1.8rem;font-family:Syne;color:rgba(240,240,235,0.7);margin:4px 0'>{weekly_need:.1f}</p>"
        f"<p style='font-size:0.66rem;color:rgba(240,240,235,0.3)'>{phase_context}</p>"
        f"</div>"

        f"</div>"

        f"<div style='background:#141414;border:1px solid rgba(255,255,255,0.07);"
        f"border-left:3px solid {trend_color};border-radius:0 10px 10px 0;"
        f"padding:0.8rem 1.1rem;margin-top:0.6rem;display:flex;align-items:center;gap:10px'>"
        f"<span style='font-size:1.2rem;color:{trend_color}'>{trend_icon}</span>"
        f"<div>"
        f"<p style='font-size:0.78rem;font-weight:600;color:{trend_color};margin:0'>{trend_title}</p>"
        f"<p style='font-size:0.68rem;color:rgba(240,240,235,0.4);margin:2px 0 0'>{trend_label}</p>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True)

# ── Tab 4 ─────────────────────────────────────────────────
with t4:
    if df_all.empty:
        st.info("No hay entrenamientos registrados aún. ¡Usá el formulario lateral para empezar!")
    else:
        fc1,fc2,fc3 = st.columns(3)
        type_filter = fc1.multiselect("Tipo", TRAINING_TYPES, default=[])
        year_opts   = ["Todos"] + sorted(df_all["date"].dt.year.unique().tolist(), reverse=True)
        year_filter = fc2.selectbox("Año", year_opts)
        sort_by     = fc3.selectbox("Ordenar", ["Fecha ↓","Distancia ↓","Ritmo ↑"])

        disp = df_all.copy()
        if type_filter:
            disp = disp[disp["type"].isin(type_filter)]
        if year_filter != "Todos":
            disp = disp[disp["date"].dt.year == int(year_filter)]

        sort_map = {"Fecha ↓":("date",False),"Distancia ↓":("distance_km",False),"Ritmo ↑":("pace_s_km",True)}
        sc, sa = sort_map[sort_by]
        disp = disp.sort_values(sc, ascending=sa)

        for _, row in disp.head(60).iterrows():
            dist_s = f"{row['distance_km']:.2f} km" if pd.notna(row.get("distance_km")) else "—"
            dur_s  = seconds_to_hms(int(row["duration_s"])) if pd.notna(row.get("duration_s")) else "—"
            pace_s = seconds_to_pace_str(int(row["pace_s_km"]))+"/km" if pd.notna(row.get("pace_s_km")) else "—"
            notes  = row.get("notes") or ""
            rname  = row.get("race_name") or ""
            race_badge = (f'&nbsp;<span class="stat-pill" style="border-color:rgba(75,240,200,0.3);'
                         f'color:#4BF0C8">{rname}</span>' if rname else "")
            ca, cb = st.columns([12,1])
            with ca:
                st.markdown(
                    f"<div class='runner-card' style='margin-bottom:0.35rem'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                    f"<div><span style='font-size:0.68rem;color:rgba(240,240,235,0.38)'>"
                    f"{row['date'].strftime('%a %d %b %Y')}</span>&nbsp;"
                    f"<span class='stat-pill'>{row['type']}</span>{race_badge}</div>"
                    f"<div style='display:flex;gap:0.8rem'>"
                    f"<b style='font-size:0.82rem;color:#C8F04B'>{dist_s}</b>"
                    f"<span style='font-size:0.82rem;color:rgba(240,240,235,0.55)'>{dur_s}</span>"
                    f"<span style='font-size:0.82rem;color:rgba(240,240,235,0.55)'>{pace_s}</span>"
                    f"</div></div>"
                    f"{'<p style=\"font-size:0.72rem;color:rgba(240,240,235,0.32);margin:5px 0 0\">' + notes + '</p>' if notes else ''}"
                    f"</div>", unsafe_allow_html=True)
            with cb:
                if st.button("✕", key=f"del_{row['id']}"):
                    delete_workout(int(row["id"])); st.rerun()


