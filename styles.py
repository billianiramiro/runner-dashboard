"""
styles.py — Injected CSS for the ultra-modern dark runner aesthetic
Palette: deep matte black + electric lime accent + mono typeface
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

/* ── Reset & root ───────────────────────────────────────── */
:root {
    --bg:        #0D0D0D;
    --bg2:       #141414;
    --bg3:       #1C1C1C;
    --border:    rgba(255,255,255,0.07);
    --accent:    #C8F04B;
    --accent2:   #4BF0C8;
    --text:      #F0F0EB;
    --muted:     rgba(240,240,235,0.45);
    --danger:    #FF5C5C;
    --font-mono: 'DM Mono', monospace;
    --font-head: 'Syne', sans-serif;
    --radius:    12px;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-mono) !important; }

/* ── Typography ─────────────────────────────────────────── */
h1, h2, h3 {
    font-family: var(--font-head) !important;
    color: var(--text) !important;
    letter-spacing: -0.02em;
}
p, label, div, span, li, td, th {
    font-family: var(--font-mono) !important;
    color: var(--text) !important;
}
.stMarkdown { color: var(--text) !important; }

/* ── Metric cards ───────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-head) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
}
[data-testid="stMetricDelta"] { font-size: 0.72rem !important; }

/* ── Inputs ─────────────────────────────────────────────── */
input[type="text"], input[type="number"], textarea, select,
.stTextInput > div > div > input,
.stNumberInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.88rem !important;
}
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(200,240,75,0.15) !important;
}
.stSelectbox > div > div {
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
}

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: #0D0D0D !important;
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    background: #d8ff55 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(200,240,75,0.25) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg3) !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
}

/* ── Tabs ───────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0.2rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 0.5rem 1rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── Divider ────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Dataframe / tables ─────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Sidebar specifics ──────────────────────────────────── */
[data-testid="stSidebarContent"] {
    padding-top: 1.5rem !important;
}

/* ── Info / success banners ────────────────────────────── */
.stAlert {
    border-radius: var(--radius) !important;
    border-left: 3px solid var(--accent) !important;
    background: rgba(200,240,75,0.06) !important;
}

/* ── Card utility class ─────────────────────────────────── */
.runner-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.stat-pill {
    display: inline-block;
    background: rgba(200,240,75,0.1);
    border: 1px solid rgba(200,240,75,0.25);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    color: var(--accent);
    margin: 2px;
}
.phase-bar-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.phase-bar-track {
    background: #1A1A1A;
    border-radius: 99px;
    height: 8px;
    overflow: hidden;
    margin-top: 6px;
}
.phase-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #2E5020, var(--accent));
    transition: width 0.6s ease;
}
.auto-calc-badge {
    font-size: 0.7rem;
    color: var(--accent2);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Hide Streamlit branding ────────────────────────────── */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Siempre mostrar el botón de abrir/cerrar sidebar ───── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
</style>
"""
