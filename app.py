import streamlit as st
import pandas as pd
import sqlite3

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Metal Price Tracker",
    page_icon="⚜️",
    layout="wide",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

/* ── ROOT PALETTE ───────────────────────────────── */
:root {
    --bg-deep:    #080c14;
    --bg-mid:     #0e1624;
    --bg-card:    #111927;
    --border:     rgba(195,155,80,0.18);
    --gold:       #c39b50;
    --gold-light: #e8c97e;
    --gold-dim:   rgba(195,155,80,0.08);
    --silver:     #a8b8cc;
    --silver-dim: rgba(168,184,204,0.08);
    --copper:     #c8724a;
    --copper-dim: rgba(200,114,74,0.08);
    --plat:       #8fb3c8;
    --plat-dim:   rgba(143,179,200,0.08);
    --text-hi:    #f0e8d8;
    --text-mid:   #8a9ab0;
    --text-lo:    #4a5a6a;
    --radius:     14px;
    --shadow:     0 8px 32px rgba(0,0,0,0.55);
}

/* ── BODY / BACKGROUND ──────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg-deep) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-hi);
}

/* subtle grain texture */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    background-size: 180px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* ── MAIN CONTENT Z-INDEX FIX ───────────────────── */
[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }

/* ── HERO TITLE ─────────────────────────────────── */
.hero-wrap {
    text-align: center;
    padding: 48px 0 36px;
    position: relative;
}
.hero-wrap::after {
    content: '';
    display: block;
    width: 80px;
    height: 2px;
    margin: 20px auto 0;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    font-size: 11px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 10px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 700;
    color: var(--text-hi);
    line-height: 1.1;
    margin: 0;
}
.hero-title span { color: var(--gold-light); }

/* ── SECTION LABEL ───────────────────────────────── */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--text-lo);
    margin-bottom: 16px;
}

/* ── METAL SELECTOR BUTTONS ──────────────────────── */
div.stButton > button {
    width: 100%;
    min-height: 130px;
    border-radius: var(--radius);
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    font-weight: 500;
    background: var(--bg-card);
    color: var(--text-mid);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.23,1,0.32,1);
    line-height: 1.7;
    padding: 20px 12px;
    white-space: pre-line;
}
div.stButton > button:hover {
    transform: translateY(-5px);
    border-color: var(--gold);
    color: var(--gold-light);
    background: linear-gradient(135deg, rgba(195,155,80,0.1), var(--bg-card));
    box-shadow: 0 16px 40px rgba(0,0,0,0.6), 0 0 0 1px var(--gold);
}
div.stButton > button:focus:not(:focus-visible) {
    outline: none !important;
    box-shadow: var(--shadow) !important;
}
div.stButton > button:focus-visible {
    outline: 2px solid var(--gold) !important;
}

/* ── METRIC CARDS ────────────────────────────────── */
.m-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 24px;
    text-align: center;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease;
}
.m-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.m-card-icon {
    font-size: 22px;
    margin-bottom: 8px;
    display: block;
}
.m-card-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-lo);
    margin-bottom: 10px;
}
.m-card-value {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 700;
    color: var(--gold-light);
    line-height: 1;
    margin-bottom: 6px;
}
.m-card-date {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: var(--text-lo);
}

/* min card accent */
.m-card.min .m-card-value { color: #7ecfa0; }
.m-card.min::before { background: linear-gradient(90deg, transparent, #7ecfa0, transparent); }

/* max card accent */
.m-card.max .m-card-value { color: #e87070; }
.m-card.max::before { background: linear-gradient(90deg, transparent, #e87070, transparent); }

/* ── DIVIDER ─────────────────────────────────────── */
hr[data-testid="stDivider"] {
    border-color: var(--border) !important;
    margin: 32px 0 !important;
}

/* ── RADIO (view toggle) ─────────────────────────── */
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    gap: 12px;
}
div[data-testid="stRadio"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-mid) !important;
    cursor: pointer;
}
div[data-testid="stRadio"] label:hover {
    color: var(--gold-light) !important;
}
div[data-testid="stRadio"] span[data-baseweb="radio"] {
    border-color: var(--gold) !important;
}

/* ── CHART ───────────────────────────────────────── */
[data-testid="stVegaLiteChart"] canvas,
[data-testid="stArrowVegaLiteChart"] {
    border-radius: 12px;
}

/* ── DATAFRAME ───────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius) !important;
    overflow: hidden;
    border: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] table {
    background: var(--bg-card) !important;
    color: var(--text-hi) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-mid) !important;
    color: var(--gold) !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text-mid) !important;
    border-bottom: 1px solid rgba(255,255,255,0.03) !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
}
[data-testid="stDataFrame"] tr:hover td {
    background: var(--gold-dim) !important;
    color: var(--gold-light) !important;
}

/* ── WARNING / INFO ──────────────────────────────── */
[data-testid="stAlert"] {
    background: var(--gold-dim) !important;
    border: 1px solid var(--gold) !important;
    border-radius: var(--radius) !important;
    color: var(--gold-light) !important;
}

/* ── SELECTED METAL BADGE ────────────────────────── */
.selected-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, rgba(195,155,80,0.12), rgba(195,155,80,0.04));
    border: 1px solid rgba(195,155,80,0.35);
    border-radius: 999px;
    padding: 6px 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--gold-light);
    margin-bottom: 24px;
}

/* ── CHART CONTAINER ─────────────────────────────── */
.chart-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow);
}
.chart-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    color: var(--text-hi);
    margin-bottom: 4px;
}
.chart-sub {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-lo);
    margin-bottom: 20px;
}

/* opacity override */
[data-testid="stAppViewContainer"] * { opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
conn = sqlite3.connect("metals.db")
df = pd.read_sql("SELECT * FROM metals", conn)
conn.close()

if df.empty:
    st.warning("No data available. Run scraper first.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df["display_date"] = df["date"].apply(lambda d: f"{d.day} {d.strftime('%B')} {d.year}")
metals = df["metal"].unique()

if "selected_metal" not in st.session_state:
    st.session_state.selected_metal = metals[0]


# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">⚜ &nbsp; Live Market Intelligence</div>
    <h1 class="hero-title">Metal <span>Price</span> Tracker</h1>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  METAL CONFIG
# ─────────────────────────────────────────────
METAL_META = {
    "Gold 24K": {
        "icon": "🥇",
        "label": "Gold 24K",
        "desc": "Pure bullion",
        "accent": "#c39b50",
    },
    "Silver": {
        "icon": "🥈",
        "label": "Silver",
        "desc": "Fine grade",
        "accent": "#a8b8cc",
    },
    "Copper": {
        "icon": "🔶",
        "label": "Copper",
        "desc": "Industrial",
        "accent": "#c8724a",
    },
    "Platinum": {
        "icon": "💎",
        "label": "Platinum",
        "desc": "Rare metal",
        "accent": "#8fb3c8",
    },
}


# ─────────────────────────────────────────────
#  METAL SELECTOR
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Select Commodity</div>', unsafe_allow_html=True)

cols = st.columns(len(metals), gap="medium")
for i, metal in enumerate(metals):
    m = METAL_META.get(metal, {"icon": "⬜", "label": metal, "desc": ""})
    with cols[i]:
        label = f"{m['icon']}\n{m['label']}\n{m['desc'].upper()}"
        if st.button(label, key=f"btn_{metal}", use_container_width=True):
            st.session_state.selected_metal = metal

selected_metal = st.session_state.selected_metal
meta = METAL_META.get(selected_metal, {"icon": "⬜", "label": selected_metal, "desc": "", "accent": "#c39b50"})

st.markdown(f"""
<div style="margin-top:16px">
    <span class="selected-badge">{meta['icon']} &nbsp; {meta['label']} selected</span>
</div>
""", unsafe_allow_html=True)

st.divider()


# ─────────────────────────────────────────────
#  FILTER
# ─────────────────────────────────────────────
filtered = df[df["metal"] == selected_metal].sort_values("date")
latest = filtered.iloc[-1]
min_row = filtered.loc[filtered["price"].idxmin()]
max_row = filtered.loc[filtered["price"].idxmax()]

# price change
price_change = ""
price_change_color = "var(--text-lo)"
if len(filtered) >= 2:
    prev = filtered.iloc[-2]["price"]
    curr = latest["price"]
    diff = curr - prev
    pct = (diff / prev) * 100
    sign = "▲" if diff >= 0 else "▼"
    price_change_color = "#7ecfa0" if diff >= 0 else "#e87070"
    price_change = f'<span style="color:{price_change_color};font-size:13px">{sign} ₹{abs(diff):,.0f} ({pct:+.2f}% today)</span>'


# ─────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Market Overview</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown(f"""
    <div class="m-card">
        <span class="m-card-icon">💰</span>
        <div class="m-card-label">Latest Price</div>
        <div class="m-card-value">₹ {latest['price']:,}</div>
        <div class="m-card-date">{latest['display_date']}</div>
        <div style="margin-top:8px">{price_change}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="m-card min">
        <span class="m-card-icon">📉</span>
        <div class="m-card-label">52-Week Low</div>
        <div class="m-card-value">₹ {min_row['price']:,}</div>
        <div class="m-card-date">{min_row['display_date']}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="m-card max">
        <span class="m-card-icon">📈</span>
        <div class="m-card-label">52-Week High</div>
        <div class="m-card-value">₹ {max_row['price']:,}</div>
        <div class="m-card-date">{max_row['display_date']}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ─────────────────────────────────────────────
#  VIEW TOGGLE
# ─────────────────────────────────────────────
view = st.radio("View Mode", ["📈  Price Chart", "📋  Historical Data"], horizontal=True, label_visibility="collapsed")

st.markdown("")

# ── CHART ─────────────────────────────────────
if "Chart" in view:
    import altair as alt

    chart_df = filtered[["date", "price"]].copy()

    # Decide tick count based on date range
    date_range_days = (chart_df["date"].max() - chart_df["date"].min()).days
    if date_range_days <= 30:
        tick_count = "week"
        date_fmt = "%d %b"
    elif date_range_days <= 180:
        tick_count = "month"
        date_fmt = "%d %b"
    else:
        tick_count = "month"
        date_fmt = "%b '%y"

    line = alt.Chart(chart_df).mark_line(
        color="#c39b50",
        strokeWidth=2.5,
        interpolate="monotone",
    ).encode(
        x=alt.X("date:T", axis=alt.Axis(
            format=date_fmt,
            tickCount=tick_count,
            tickColor="#2a3a4a",
            gridColor="#1a2a3a",
            labelColor="#8a9ab0",
            titleColor="#4a5a6a",
            labelAngle=-40,
            labelFontSize=11,
            labelPadding=8,
            title="",
        )),
        y=alt.Y("price:Q", axis=alt.Axis(
            format=",.0f",
            tickColor="#2a3a4a",
            gridColor="#1a2a3a",
            labelColor="#8a9ab0",
            titleColor="#4a5a6a",
            titleFontSize=11,
            labelFontSize=11,
            title="Price (₹/gm)",
        )),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%d %B %Y"),
            alt.Tooltip("price:Q", title="Price (₹)", format=",.2f"),
        ],
    )

    area = alt.Chart(chart_df).mark_area(
        opacity=0.12,
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#c39b50", offset=0),
                alt.GradientStop(color="transparent", offset=1),
            ],
            x1=1, x2=1, y1=1, y2=0,
        ),
        interpolate="monotone",
    ).encode(
        x="date:T",
        y="price:Q",
    )

    points = alt.Chart(chart_df.tail(1)).mark_point(
        color="#e8c97e",
        filled=True,
        size=80,
    ).encode(x="date:T", y="price:Q")

    chart = (area + line + points).properties(
        height=360,
        background="transparent",
        padding={"left": 8, "right": 8, "top": 16, "bottom": 24},
    ).configure_view(
        strokeWidth=0,
        fill="transparent",
    ).configure_axis(
        domain=False,
    )

    st.markdown(f"""
    <div class="chart-wrap">
        <div class="chart-title">{meta['icon']} {meta['label']} — Price Trend</div>
        <div class="chart-sub">Historical performance · ₹ per gram</div>
    </div>
    """, unsafe_allow_html=True)

    st.altair_chart(chart, use_container_width=True)

# ── TABLE ──────────────────────────────────────
else:
    table_df = filtered[["display_date", "price"]].copy()
    table_df = table_df.rename(columns={"display_date": "Date", "price": "Price (₹/gm)"})
    table_df = table_df.iloc[::-1].reset_index(drop=True)  # newest first
    table_df["Price (₹/gm)"] = table_df["Price (₹/gm)"].apply(lambda x: f"₹ {x:,}")

    st.markdown('<div class="section-label">Historical Data — Newest First</div>', unsafe_allow_html=True)
    st.dataframe(table_df, use_container_width=True, hide_index=True, height=420)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:48px 0 24px;font-family:'DM Sans',sans-serif;
font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#2a3a4a">
⚜ &nbsp; Metal Price Tracker &nbsp; · &nbsp; Data auto-refreshed via scraper
</div>
""", unsafe_allow_html=True)