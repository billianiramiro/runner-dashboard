"""
database.py — Supabase backend para Runner Dashboard
"""

import os
import pandas as pd

try:
    import streamlit as st
    def _get_creds():
        return st.secrets["supabase"]["url"], st.secrets["supabase"]["key"]
except Exception:
    def _get_creds():
        return os.environ.get("SUPABASE_URL",""), os.environ.get("SUPABASE_KEY","")

from supabase import create_client

def get_client():
    url, key = _get_creds()
    return create_client(url, key)


TRAINING_TYPES = [
    "Fondo",
    "Pasadas / Intervalos",
    "Carrera Oficial",
    "Recuperación",
    "Rodaje Suave",
    "Tempo / Umbral",
]

MARATHON_PHASES = [
    {"id":1,"year":"Año 1","sub":"Subfase 1.1","name":"Construcción de Base",
     "start":"2025-10-13","end":"2026-04-12","km_target":180,
     "desc":"Adaptar el cuerpo a correr, salidas cortas y constantes","weekly_ref":"~7 km/sem"},
    {"id":2,"year":"Año 1","sub":"Subfase 1.2","name":"Desarrollo Aeróbico",
     "start":"2026-04-13","end":"2026-10-13","km_target":280,
     "desc":"Aumentar volumen gradualmente, primeras carreras cortas","weekly_ref":"~11 km/sem"},
    {"id":3,"year":"Año 2","sub":"Subfase 2.1","name":"Potencia y Umbral",
     "start":"2026-10-14","end":"2027-04-12","km_target":380,
     "desc":"Introducir series y tempo, mejorar ritmo base","weekly_ref":"~15 km/sem"},
    {"id":4,"year":"Año 2","sub":"Subfase 2.2","name":"Resistencia Específica",
     "start":"2027-04-13","end":"2027-10-12","km_target":500,
     "desc":"Tiradas largas, primera media maratón como test","weekly_ref":"~20 km/sem"},
    {"id":5,"year":"Año 3","sub":"Subfase 3.1","name":"Preparación Maratón",
     "start":"2027-10-13","end":"2028-08-27","km_target":900,
     "desc":"Peak de volumen, long runs de 30-35 km, simulacros","weekly_ref":"~30 km/sem"},
    {"id":6,"year":"Año 3","sub":"Subfase 3.2","name":"Taper Final",
     "start":"2028-08-28","end":"2028-09-14","km_target":40,
     "desc":"Reducción de carga, llegada fresco al día de la carrera","weekly_ref":"~10 km/sem"},
]


def initialize_db():
    """No hace nada — las tablas ya fueron creadas en Supabase via SQL Editor."""
    pass


def insert_workout(workout_date, training_type, distance_km, duration_s, pace_s_km, notes="", race_name=""):
    client = get_client()
    data = {
        "date": workout_date, "type": training_type,
        "distance_km": distance_km, "duration_s": duration_s,
        "pace_s_km": pace_s_km, "notes": notes, "race_name": race_name,
    }
    res = client.table("workouts").insert(data).execute()
    return res.data[0]["id"] if res.data else None


def delete_workout(workout_id):
    client = get_client()
    client.table("workouts").delete().eq("id", workout_id).execute()


def get_all_workouts():
    client = get_client()
    res = client.table("workouts").select("*").order("date", desc=True).execute()
    if not res.data:
        return pd.DataFrame()
    df = pd.DataFrame(res.data)
    df["date"]         = pd.to_datetime(df["date"])
    df["pace_min_km"]  = df["pace_s_km"] / 60
    df["duration_min"] = df["duration_s"] / 60
    return df


def get_weekly_summary():
    df = get_all_workouts()
    if df.empty:
        return pd.DataFrame()
    df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    return df.groupby("week").agg(
        km=("distance_km","sum"),
        sessions=("id","count"),
        avg_pace_s=("pace_s_km","mean"),
    ).reset_index()


def get_total_km_since(since_date):
    client = get_client()
    res = (client.table("workouts").select("distance_km")
           .gte("date", since_date).execute())
    if not res.data:
        return 0.0
    return round(sum(r["distance_km"] or 0 for r in res.data), 1)


def get_km_between(start_date, end_date):
    client = get_client()
    res = (client.table("workouts").select("distance_km")
           .gte("date", start_date).lte("date", end_date).execute())
    if not res.data:
        return 0.0
    return round(sum(r["distance_km"] or 0 for r in res.data), 1)
