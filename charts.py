"""
charts.py — All chart/visualization functions (Plotly Interactive)
TerraTrend Climate Atlas
Premium Climate Intelligence Platform Theme
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ─── CLIMATE INTELLIGENCE THEME ─────────────────────────────────────────────
DEEP_SPACE   = "#0B1220"
CARD_BG      = "#111827"
PANEL_BG     = "#1A2332"
OCEAN_BLUE   = "#2563EB"
CLIMATE_CYAN = "#06B6D4"
WARM_ORANGE  = "#F97316"
ALERT_RED    = "#EF4444"
GOLD         = "#FBBF24"
TEXT_PRIMARY = "#F1F5F9"
TEXT_MUTED   = "#94A3B8"
GRID_COLOR   = "#1E293B"
BORDER       = "#334155"

PALETTE = [OCEAN_BLUE, ALERT_RED, GOLD, "#8B5CF6", "#10B981",
           WARM_ORANGE, CLIMATE_CYAN, "#EC4899", "#14B8A6", "#A78BFA"]

SOURCE_COLORS = {"GCAG": OCEAN_BLUE, "GISTEMP": ALERT_RED}
SEASON_COLORS = {"Winter": "#60A5FA", "Spring": "#34D399", "Summer": "#FBBF24", "Autumn": "#F97316"}


def _base_layout(title="", height=480, show_legend=True):
    """Return a consistent Plotly layout dict."""
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=12),
        title=dict(text=title, font=dict(size=16, color=TEXT_PRIMARY, weight=600), x=0.01, y=0.97),
        margin=dict(l=50, r=30, t=50, b=50),
        height=height,
        showlegend=show_legend,
        legend=dict(
            bgcolor="rgba(17,24,39,0.7)",
            bordercolor=BORDER,
            borderwidth=1,
            font=dict(size=11, color=TEXT_PRIMARY),
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR, gridwidth=0.5,
            zerolinecolor=BORDER, zerolinewidth=1,
            tickfont=dict(size=10, color=TEXT_MUTED),
            title_font=dict(size=12, color=TEXT_MUTED),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR, gridwidth=0.5,
            zerolinecolor=BORDER, zerolinewidth=1,
            tickfont=dict(size=10, color=TEXT_MUTED),
            title_font=dict(size=12, color=TEXT_MUTED),
        ),
        hoverlabel=dict(
            bgcolor=CARD_BG, bordercolor=BORDER,
            font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRIMARY),
        ),
        transition=dict(duration=500),
    )


def _empty_fig(msg="No data available"):
    """Return an empty figure with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=16, color=TEXT_MUTED),
    )
    fig.update_layout(**_base_layout(height=300, show_legend=False))
    return fig


def _modebar_config():
    """Return common modebar config for chart display."""
    return {
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "displaylogo": False,
    }


# ─── 1. LINE CHART — Annual mean anomaly trend ─────────────────────────────
def line_chart(df):
    if df.empty:
        return _empty_fig("Line Chart — No data")

    fig = go.Figure()

    for source, color in SOURCE_COLORS.items():
        sub = df[df["Source"] == source].sort_values("Date")
        if sub.empty:
            continue
        yearly = sub.groupby("YearNum")["Mean"].mean().reset_index()

        # Main line
        fig.add_trace(go.Scatter(
            x=yearly["YearNum"], y=yearly["Mean"],
            mode="lines", name=source,
            line=dict(color=color, width=2.5, shape="spline"),
            hovertemplate="<b>%{x}</b><br>Anomaly: %{y:.3f}°C<extra>" + source + "</extra>",
        ))

    # Zero baseline
    fig.add_hline(y=0, line=dict(color=GOLD, width=1, dash="dot"), opacity=0.5)

    # Fill between for GCAG
    gcag = df[df["Source"] == "GCAG"]
    if not gcag.empty:
        yearly_gcag = gcag.groupby("YearNum")["Mean"].mean().reset_index()
        pos = yearly_gcag.copy()
        neg = yearly_gcag.copy()
        pos.loc[pos["Mean"] < 0, "Mean"] = 0
        neg.loc[neg["Mean"] > 0, "Mean"] = 0

        fig.add_trace(go.Scatter(
            x=pos["YearNum"], y=pos["Mean"],
            fill="tozeroy", fillcolor="rgba(239,68,68,0.1)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=neg["YearNum"], y=neg["Mean"],
            fill="tozeroy", fillcolor="rgba(37,99,235,0.1)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))

    layout = _base_layout("Annual Mean Temperature Anomaly Trend", height=460)
    layout["xaxis"]["title"] = dict(text="Year", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Temperature Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 2. AREA CHART — Cumulative anomaly ─────────────────────────────────────
def area_chart(df):
    if df.empty:
        return _empty_fig("Area Chart — No data")

    fig = go.Figure()

    for source, color in SOURCE_COLORS.items():
        sub = df[df["Source"] == source].sort_values("Date")
        if sub.empty:
            continue
        yearly = sub.groupby("YearNum")["Mean"].mean().reset_index()
        yearly["Cumulative"] = yearly["Mean"].cumsum()

        fig.add_trace(go.Scatter(
            x=yearly["YearNum"], y=yearly["Cumulative"],
            fill="tozeroy", name=source,
            line=dict(color=color, width=2),
            fillcolor=color.replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in color else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
            hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.2f}°C<extra>" + source + "</extra>",
        ))

    fig.add_hline(y=0, line=dict(color=GOLD, width=1, dash="dot"), opacity=0.4)

    layout = _base_layout("Cumulative Temperature Anomaly Over Time", height=460)
    layout["xaxis"]["title"] = dict(text="Year", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Cumulative Mean Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 3. BAR CHART — Average anomaly by decade ──────────────────────────────
def bar_chart(df):
    if df.empty:
        return _empty_fig("Bar Chart — No data")

    decade_avg = df.groupby("Decade")["Mean"].mean().reset_index().sort_values("Decade")
    colors = [ALERT_RED if v > 0 else OCEAN_BLUE for v in decade_avg["Mean"]]

    fig = go.Figure(go.Bar(
        x=decade_avg["Decade"], y=decade_avg["Mean"],
        marker=dict(color=colors, line=dict(width=0), opacity=0.85),
        text=[f"{v:+.2f}" for v in decade_avg["Mean"]],
        textposition="outside",
        textfont=dict(size=10, color=TEXT_PRIMARY),
        hovertemplate="<b>%{x}</b><br>Mean Anomaly: %{y:.3f}°C<extra></extra>",
    ))

    fig.add_hline(y=0, line=dict(color=GOLD, width=1, dash="dash"), opacity=0.5)

    layout = _base_layout("Average Temperature Anomaly by Decade")
    layout["xaxis"]["title"] = dict(text="Decade", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Mean Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 4. PIE CHART — Warm vs Cool months ────────────────────────────────────
def pie_chart(df):
    if df.empty:
        return _empty_fig("Pie Chart — No data")

    counts = df["AnomalyType"].value_counts()
    color_map = {"Warm": ALERT_RED, "Cool": OCEAN_BLUE, "Neutral": GOLD}
    colors = [color_map.get(l, TEXT_MUTED) for l in counts.index]

    fig = go.Figure(go.Pie(
        labels=counts.index.tolist(),
        values=counts.values.tolist(),
        marker=dict(colors=colors, line=dict(color=DEEP_SPACE, width=2)),
        hole=0.45,
        textinfo="percent+label",
        textfont=dict(size=11, color=TEXT_PRIMARY),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>",
        pull=[0.03] * len(counts),
    ))

    layout = _base_layout("Warm vs Cool Anomaly Months", show_legend=True)
    layout["legend"]["orientation"] = "h"
    layout["legend"]["y"] = -0.05
    layout["legend"]["x"] = 0.5
    layout["legend"]["xanchor"] = "center"
    fig.update_layout(**layout)
    return fig


# ─── 5. HISTOGRAM — Anomaly distribution ───────────────────────────────────
def histogram(df):
    if df.empty:
        return _empty_fig("Histogram — No data")

    fig = go.Figure()

    for source, color in SOURCE_COLORS.items():
        sub = df[df["Source"] == source]["Mean"]
        if sub.empty:
            continue
        fig.add_trace(go.Histogram(
            x=sub, name=source,
            marker=dict(color=color, opacity=0.65, line=dict(width=0.5, color=DEEP_SPACE)),
            nbinsx=30,
            hovertemplate="<b>%{x:.2f}°C</b><br>Count: %{y}<extra>" + source + "</extra>",
        ))

    fig.add_vline(x=0, line=dict(color=GOLD, width=1.5, dash="dash"), opacity=0.6,
                  annotation_text="Zero baseline", annotation_font_color=GOLD, annotation_font_size=10)

    layout = _base_layout("Distribution of Monthly Temperature Anomalies")
    layout["barmode"] = "overlay"
    layout["xaxis"]["title"] = dict(text="Temperature Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Frequency", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 6. BOX PLOT — Anomaly by season ───────────────────────────────────────
def box_plot(df):
    if df.empty:
        return _empty_fig("Box Plot — No data")

    seasons = ["Winter", "Spring", "Summer", "Autumn"]
    present = [s for s in seasons if s in df["Season"].values]

    fig = go.Figure()
    for s in present:
        sub = df[df["Season"] == s]["Mean"]
        fig.add_trace(go.Box(
            y=sub, name=s,
            marker=dict(color=SEASON_COLORS.get(s, TEXT_MUTED), opacity=0.7),
            line=dict(color=SEASON_COLORS.get(s, TEXT_MUTED)),
            fillcolor=f"rgba({int(SEASON_COLORS.get(s, '#888')[1:3],16)},{int(SEASON_COLORS.get(s, '#888')[3:5],16)},{int(SEASON_COLORS.get(s, '#888')[5:7],16)},0.3)",
            boxmean="sd",
            hovertemplate="<b>%{x}</b><br>Value: %{y:.3f}°C<extra></extra>",
        ))

    fig.add_hline(y=0, line=dict(color=GOLD, width=1, dash="dot"), opacity=0.4)

    layout = _base_layout("Anomaly Spread by Season")
    layout["xaxis"]["title"] = dict(text="Season", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Temperature Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 7. VIOLIN PLOT — Anomaly by source ────────────────────────────────────
def violin_plot(df):
    if df.empty:
        return _empty_fig("Violin Plot — No data")

    fig = go.Figure()
    for source, color in SOURCE_COLORS.items():
        sub = df[df["Source"] == source]["Mean"]
        if sub.empty:
            continue
        hex_r, hex_g, hex_b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Violin(
            y=sub, name=source,
            line_color=color,
            fillcolor=f"rgba({hex_r},{hex_g},{hex_b},0.3)",
            meanline_visible=True,
            box_visible=True,
            hovertemplate="<b>%{x}</b><br>Value: %{y:.3f}°C<extra></extra>",
        ))

    fig.add_hline(y=0, line=dict(color=GOLD, width=1, dash="dot"), opacity=0.4)

    layout = _base_layout("Anomaly Distribution & Density by Source")
    layout["xaxis"]["title"] = dict(text="Data Source", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Temperature Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 8. COUNT PLOT — Records per decade by source ──────────────────────────
def count_plot(df):
    if df.empty:
        return _empty_fig("Count Plot — No data")

    decade_counts = df.groupby(["Decade", "Source"]).size().reset_index(name="Count")
    decades = sorted(decade_counts["Decade"].unique())

    fig = go.Figure()
    for source, color in SOURCE_COLORS.items():
        src_data = decade_counts[decade_counts["Source"] == source]
        vals = [src_data[src_data["Decade"] == d]["Count"].sum() if d in src_data["Decade"].values else 0 for d in decades]
        fig.add_trace(go.Bar(
            x=decades, y=vals, name=source,
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            text=[str(v) if v > 0 else "" for v in vals],
            textposition="outside",
            textfont=dict(size=9, color=TEXT_MUTED),
            hovertemplate="<b>%{x}</b><br>" + source + ": %{y:,} records<extra></extra>",
        ))

    layout = _base_layout("Monthly Records per Decade by Source")
    layout["barmode"] = "group"
    layout["xaxis"]["title"] = dict(text="Decade", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Number of Records", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 9. SCATTER PLOT — Year vs Anomaly ─────────────────────────────────────
def scatter_plot(df):
    if df.empty:
        return _empty_fig("Scatter Plot — No data")

    fig = go.Figure()
    for source, color in SOURCE_COLORS.items():
        sub = df[df["Source"] == source]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["YearNum"], y=sub["Mean"],
            mode="markers", name=source,
            marker=dict(
                color=color, size=4, opacity=0.4,
                symbol="circle" if source == "GCAG" else "triangle-up",
            ),
            hovertemplate="<b>%{x}</b><br>Anomaly: %{y:.3f}°C<extra>" + source + "</extra>",
        ))

    fig.add_hline(y=0, line=dict(color=GOLD, width=1, dash="dot"), opacity=0.4)

    layout = _base_layout("Monthly Anomaly Distribution Over Time", height=460)
    layout["xaxis"]["title"] = dict(text="Year", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Temperature Anomaly (°C)", font=dict(size=12, color=TEXT_MUTED))
    fig.update_layout(**layout)
    return fig


# ─── 10. HEATMAP — Correlation matrix ─────────────────────────────────────
def heatmap(df):
    if df.empty:
        return _empty_fig("Heatmap — No data")

    num_df = df[["YearNum", "Month", "Mean"]].dropna()
    if num_df.shape[0] < 3:
        return _empty_fig("Heatmap — Not enough data")

    corr = num_df.corr()
    labels = ["Year", "Month", "Anomaly"]

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(size=14, color=TEXT_PRIMARY),
        hovertemplate="<b>%{x} × %{y}</b><br>Correlation: %{z:.3f}<extra></extra>",
        colorbar=dict(
            title=dict(text="r", font=dict(color=TEXT_MUTED)),
            tickfont=dict(color=TEXT_MUTED),
        ),
    ))

    layout = _base_layout("Correlation Matrix", show_legend=False)
    layout["xaxis"]["tickfont"] = dict(size=12, color=TEXT_PRIMARY)
    layout["yaxis"]["tickfont"] = dict(size=12, color=TEXT_PRIMARY)
    layout["yaxis"]["autorange"] = "reversed"
    fig.update_layout(**layout)
    return fig


# ─── 11. PAIR PLOT — Scatter matrix ───────────────────────────────────────
def pair_plot(df):
    if df.empty or df.shape[0] < 5:
        return _empty_fig("Pair Plot — Not enough data")

    sub = df[["YearNum", "Month", "Mean", "Source"]].dropna()
    if sub.shape[0] > 3000:
        sub = sub.sample(3000, random_state=42)

    fig = px.scatter_matrix(
        sub,
        dimensions=["YearNum", "Month", "Mean"],
        color="Source",
        color_discrete_map=SOURCE_COLORS,
        labels={"YearNum": "Year", "Month": "Month", "Mean": "Anomaly"},
        opacity=0.4,
    )

    fig.update_traces(
        diagonal_visible=True,
        marker=dict(size=3),
    )

    layout = _base_layout("Pair Plot — Year, Month, Anomaly", height=520, show_legend=True)
    fig.update_layout(**layout)
    return fig


# ─── 12. MONTHLY HEATMAP — Year × Month grid ──────────────────────────────
def monthly_heatmap(df):
    if df.empty:
        return _empty_fig("Monthly Heatmap — No data")

    source = "GCAG" if "GCAG" in df["Source"].values else df["Source"].iloc[0]
    sub = df[df["Source"] == source].copy()

    pivot = sub.pivot_table(index="YearNum", columns="Month", values="Mean", aggfunc="mean")
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    years = pivot.index.tolist()
    months_present = [c for c in range(1, 13) if c in pivot.columns]
    z_data = pivot.reindex(columns=range(1, 13)).values
    month_text = [month_labels[m - 1] for m in range(1, 13)]

    # Compute dynamic height
    n_years = len(years)
    chart_height = max(500, min(1200, n_years * 5 + 100))

    fig = go.Figure(go.Heatmap(
        z=z_data,
        x=month_text,
        y=years,
        colorscale=[
            [0, OCEAN_BLUE],
            [0.5, "#111827"],
            [1, ALERT_RED],
        ],
        zmid=0,
        hovertemplate="<b>%{y} %{x}</b><br>Anomaly: %{z:.3f}°C<extra></extra>",
        colorbar=dict(
            title=dict(text="Anomaly (°C)", font=dict(color=TEXT_MUTED, size=11)),
            tickfont=dict(color=TEXT_MUTED, size=10),
        ),
    ))

    layout = _base_layout(f"Monthly Temperature Anomaly Grid ({source})", height=chart_height, show_legend=False)
    layout["xaxis"]["title"] = dict(text="Month", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["title"] = dict(text="Year", font=dict(size=12, color=TEXT_MUTED))
    layout["yaxis"]["autorange"] = "reversed"
    layout["yaxis"]["dtick"] = 10
    fig.update_layout(**layout)
    return fig


# ─── SPARKLINE — Mini chart for KPI cards ──────────────────────────────────
def sparkline_svg(df, width=120, height=32):
    """Generate a simple SVG sparkline string for inline use in KPI cards."""
    if df.empty:
        return ""

    yearly = df.groupby("YearNum")["Mean"].mean().reset_index().sort_values("YearNum")
    if len(yearly) < 2:
        return ""

    values = yearly["Mean"].values
    years = yearly["YearNum"].values

    # Normalize to SVG coordinates
    y_min, y_max = values.min(), values.max()
    y_range = y_max - y_min if y_max != y_min else 1
    x_min, x_max = years.min(), years.max()
    x_range = x_max - x_min if x_max != x_min else 1

    padding = 2
    usable_w = width - 2 * padding
    usable_h = height - 2 * padding

    points = []
    for x_val, y_val in zip(years, values):
        sx = padding + (x_val - x_min) / x_range * usable_w
        sy = padding + (1 - (y_val - y_min) / y_range) * usable_h
        points.append(f"{sx:.1f},{sy:.1f}")

    polyline = " ".join(points)

    # Gradient fill
    fill_points = [f"{padding:.1f},{usable_h + padding:.1f}"] + points + [f"{usable_w + padding:.1f},{usable_h + padding:.1f}"]
    fill_polyline = " ".join(fill_points)

    trend_color = ALERT_RED if values[-1] > values[0] else OCEAN_BLUE
    hex_r, hex_g, hex_b = int(trend_color[1:3], 16), int(trend_color[3:5], 16), int(trend_color[5:7], 16)

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgba({hex_r},{hex_g},{hex_b},0.3)"/>
      <stop offset="100%" stop-color="rgba({hex_r},{hex_g},{hex_b},0.02)"/>
    </linearGradient>
  </defs>
  <polygon points="{fill_polyline}" fill="url(#sparkFill)"/>
  <polyline points="{polyline}" fill="none" stroke="{trend_color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
    return svg
