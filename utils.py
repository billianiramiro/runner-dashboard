"""utils.py — Conversion helpers for pace / time / distance"""


def seconds_to_hms(seconds):
    if seconds is None: return ""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}"


def hms_to_seconds(hms):
    hms = (hms or "").strip()
    if not hms: return None
    parts = hms.split(":")
    try:
        if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        return int(parts[0])
    except ValueError:
        return None


def seconds_to_pace_str(pace_s_km):
    if pace_s_km is None: return ""
    m = int(pace_s_km) // 60
    s = int(pace_s_km) % 60
    return f"{m}:{s:02d}"


def pace_str_to_seconds(pace_str):
    return hms_to_seconds(pace_str)


def calc_pace(distance_km, duration_s):
    if not distance_km or not duration_s: return None
    return int(duration_s / distance_km)


def calc_duration(distance_km, pace_s_km):
    if not distance_km or not pace_s_km: return None
    return int(distance_km * pace_s_km)


def calc_distance(duration_s, pace_s_km):
    if not duration_s or not pace_s_km: return None
    return round(duration_s / pace_s_km, 2)
