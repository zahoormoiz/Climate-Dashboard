"""
app.py — Main Streamlit dashboard for TerraTrend Climate Atlas
Global temperature anomalies — GISS & NOAA (January 1850 to March 2026)
"""

import streamlit as st
from filters import load_data, get_filter_defaults, apply_filters, compute_trends
import charts
import os

APP_NAME = "TerraTrend Climate Atlas"
APP_TAGLINE = "Global Surface Temperature Anomalies Explorer"
APP_DATA_WINDOW = "January 1850 to March 2026"
EXPORT_FILENAME = "terratrend_climate_atlas_export.csv"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df_full = get_data()
defaults = get_filter_defaults(df_full)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Parameters")
    st.markdown("---")

    if st.button("🔄 Reset View"):
        for k in ["source_sel", "year_range", "season_sel", "anomaly_range", "decade_sel", "search_text"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.markdown("---")

    source_sel = st.multiselect(
        "📡 Data Source",
        options=defaults["sources"],
        default=st.session_state.get("source_sel", defaults["sources"]),
        key="source_sel",
    )

    year_range = st.slider(
        "📅 Year Range",
        min_value=defaults["year_min"],
        max_value=defaults["year_max"],
        value=st.session_state.get("year_range", (defaults["year_min"], defaults["year_max"])),
        step=1,
        key="year_range",
    )

    season_sel = st.multiselect(
        "🍂 Season",
        options=defaults["seasons"],
        default=st.session_state.get("season_sel", defaults["seasons"]),
        key="season_sel",
    )

    anomaly_range = st.slider(
        "🌡️ Anomaly Range (°C)",
        min_value=defaults["anomaly_min"],
        max_value=defaults["anomaly_max"],
        value=st.session_state.get("anomaly_range", (defaults["anomaly_min"], defaults["anomaly_max"])),
        step=0.01,
        format="%.2f",
        key="anomaly_range",
    )

    decade_sel = st.multiselect(
        "📆 Decade",
        options=defaults["decades"],
        default=st.session_state.get("decade_sel", []),
        key="decade_sel",
        placeholder="All decades",
    )

    search_text = st.text_input(
        "🔍 Search Engine",
        value=st.session_state.get("search_text", ""),
        placeholder="e.g. GCAG, 1990s, Winter",
        key="search_text",
    )

# ── Apply filters ─────────────────────────────────────────────────────────────
df = apply_filters(
    df_full,
    source_sel=source_sel if source_sel else defaults["sources"],
    year_range=year_range,
    season_sel=season_sel if season_sel else defaults["seasons"],
    anomaly_range=anomaly_range,
    decade_sel=decade_sel,
    search_text=search_text,
)

# ── Navigation & Hero ─────────────────────────────────────────────────────────
st.markdown(f"""
<div id="top"></div>
<div class="sticky-nav">
    <a href="#overview">Overview</a>
    <a href="#comparisons">Comparisons</a>
    <a href="#distributions">Distributions</a>
    <a href="#relationships">Relationships</a>
    <a href="#historical-grid">Historical Grid</a>
    <a href="#data-explorer">Data Explorer</a>
</div>

<div class="hero-container">
    <h1 class="hero-title">{APP_NAME}</h1>
    <div style="color: #94A3B8; font-size: 1.1rem; margin-bottom: 4px;">
        {APP_TAGLINE}
    </div>
    <div style="color: #64748B; font-size: 0.88rem;">
        Data window: {APP_DATA_WINDOW}
    </div>
    <div class="hero-badge">
        <div class="pulse-dot"></div>
        Active Warming Trend Detected
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total = len(df)
trends = compute_trends(df)

if total > 0:
    max_anomaly = df["Mean"].max()
    max_row = df.loc[df["Mean"].idxmax()]
    min_anomaly = df["Mean"].min()
    min_row = df.loc[df["Mean"].idxmin()]
    avg_anomaly = df["Mean"].mean()
    warm_pct = (df["AnomalyType"] == "Warm").mean() * 100
else:
    max_anomaly = min_anomaly = avg_anomaly = warm_pct = 0
    max_row = min_row = None

# Generate sparklines
spark_gcag = charts.sparkline_svg(df[df["Source"] == "GCAG"]) if "GCAG" in df["Source"].values else ""
spark_gistemp = charts.sparkline_svg(df[df["Source"] == "GISTEMP"]) if "GISTEMP" in df["Source"].values else ""

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='kpi-card card-neutral'>
        <div class='kpi-header'>
            <span class='kpi-title'>Total Records</span>
            <div class='kpi-icon icon-gold'>📊</div>
        </div>
        <div class='kpi-value'>{total:,}</div>
        <div class='kpi-footer'>
            <span style='color: #94A3B8; font-size: 0.85rem;'>Filtered dataset</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    date_str = f"{max_row['Year']}" if max_row is not None else ""
    st.markdown(f"""
    <div class='kpi-card card-hot'>
        <div class='kpi-header'>
            <span class='kpi-title'>Peak Warming</span>
            <div class='kpi-icon icon-red'>🔥</div>
        </div>
        <div class='kpi-value' style='color:#EF4444'>+{max_anomaly:.2f}°C</div>
        <div class='kpi-footer'>
            <span style='color: #94A3B8; font-size: 0.85rem;'>Recorded in {date_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='kpi-card card-hot'>
        <div class='kpi-header'>
            <span class='kpi-title'>Decadal Trend</span>
            <div class='kpi-icon icon-cyan'>📈</div>
        </div>
        <div class='kpi-value'>{trends['trend_value']:+.2f}°C</div>
        <div class='kpi-footer'>
            <span class='trend-indicator trend-{trends["trend_direction"]}'>
                {"↑" if trends["trend_direction"] == "up" else "↓" if trends["trend_direction"] == "down" else "→"} {abs(trends['rate_per_decade']):.2f}°/dec
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='kpi-card card-hot'>
        <div class='kpi-header'>
            <span class='kpi-title'>Warm Months</span>
            <div class='kpi-icon icon-red'>🌡️</div>
        </div>
        <div class='kpi-value'>{warm_pct:.1f}%</div>
        <div class='sparkline-container'>
            {spark_gcag if spark_gcag else spark_gistemp}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="overview" class="analytic-section">
    <div class="section-header">
        <span class="section-icon">📈</span>
        <div>
            <h2 class="section-title">Climate Overview</h2>
            <p class="section-desc">Macro-level trends and cumulative warming trajectories.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.plotly_chart(charts.line_chart(df), width="stretch")
st.plotly_chart(charts.area_chart(df), width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — COMPARISONS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="comparisons" class="analytic-section">
    <div class="section-header">
        <span class="section-icon">⚖️</span>
        <div>
            <h2 class="section-title">Comparative Analysis</h2>
            <p class="section-desc">Decadal shifts and the ratio of warm to cool periods.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(charts.bar_chart(df), width="stretch")
with col_b:
    st.plotly_chart(charts.pie_chart(df), width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="distributions" class="analytic-section">
    <div class="section-header">
        <span class="section-icon">📊</span>
        <div>
            <h2 class="section-title">Distribution Analytics</h2>
            <p class="section-desc">Statistical spread, seasonality, and data density.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(charts.histogram(df), width="stretch")
with col_b:
    st.plotly_chart(charts.box_plot(df), width="stretch")

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(charts.violin_plot(df), width="stretch")
with col_b:
    st.plotly_chart(charts.count_plot(df), width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — RELATIONSHIPS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="relationships" class="analytic-section">
    <div class="section-header">
        <span class="section-icon">🔗</span>
        <div>
            <h2 class="section-title">Correlations & Relationships</h2>
            <p class="section-desc">Multi-dimensional variable interactions and patterns.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.plotly_chart(charts.scatter_plot(df), width="stretch")

col_a, col_b = st.columns([1, 2])
with col_a:
    st.plotly_chart(charts.heatmap(df), width="stretch")
with col_b:
    st.plotly_chart(charts.pair_plot(df), width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — HISTORICAL GRID
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="historical-grid" class="analytic-section">
    <div class="section-header">
        <span class="section-icon">📅</span>
        <div>
            <h2 class="section-title">Historical Heatmap</h2>
            <p class="section-desc">Comprehensive year-by-month temperature grid.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.plotly_chart(charts.monthly_heatmap(df), width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="data-explorer" class="analytic-section" style="margin-bottom: 60px;">
    <div class="section-header">
        <span class="section-icon">🗄️</span>
        <div>
            <h2 class="section-title">Data Explorer</h2>
            <p class="section-desc">Searchable, sortable raw data access.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

display_df = df[["Source", "Year", "Mean", "YearNum", "MonthName", "Season", "Decade", "AnomalyType"]].copy()
display_df.columns = ["Source", "Date", "Anomaly (°C)", "Year", "Month", "Season", "Decade", "Type"]

st.dataframe(display_df, width="stretch", height=400, hide_index=True)

csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Export CSV",
    data=csv,
    file_name=EXPORT_FILENAME,
    mime="text/csv",
    help="Download the current filtered dataset"
)

st.markdown("</div>", unsafe_allow_html=True)

# ── Footer & Back to Top ──────────────────────────────────────────────────────
st.markdown(f"""
<a href="#top" class="back-to-top" title="Back to top">↑</a>
<div style='text-align:center; color:#64748B; font-size:0.85rem; padding: 20px 0 40px 0; border-top: 1px solid #1E293B;'>
    <strong>{APP_NAME}</strong><br>
    NASA GISTEMP & NOAA GCAG · {APP_DATA_WINDOW}
</div>
""", unsafe_allow_html=True)
