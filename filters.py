"""
filters.py — Data loading, cleaning, and filtering logic
TerraTrend Climate Atlas
"""

import pandas as pd
import numpy as np
import os


def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "monthly.csv")
    df = pd.read_csv(path)
    df = clean_data(df)
    return df


def clean_data(df):
    df = df.dropna(subset=["Source", "Year", "Mean"])
    df["Mean"] = pd.to_numeric(df["Mean"], errors="coerce")
    df = df.dropna(subset=["Mean"])

    # Parse YYYY-MM into separate columns
    df["Date"] = pd.to_datetime(df["Year"], format="%Y-%m", errors="coerce")
    df = df.dropna(subset=["Date"])
    df["YearNum"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%b")
    df["Decade"] = (df["YearNum"] // 10 * 10).astype(str) + "s"
    df["Quarter"] = df["Date"].dt.quarter.map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})

    # Season mapping
    def get_season(m):
        if m in [12, 1, 2]:
            return "Winter"
        elif m in [3, 4, 5]:
            return "Spring"
        elif m in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"

    df["Season"] = df["Month"].apply(get_season)

    # Anomaly classification
    df["AnomalyType"] = df["Mean"].apply(
        lambda x: "Warm" if x > 0 else ("Cool" if x < 0 else "Neutral")
    )

    df = df.drop_duplicates()
    df = df.sort_values(["Date", "Source"]).reset_index(drop=True)
    return df


def get_filter_defaults(df):
    return {
        "year_min": int(df["YearNum"].min()),
        "year_max": int(df["YearNum"].max()),
        "anomaly_min": float(df["Mean"].min()),
        "anomaly_max": float(df["Mean"].max()),
        "sources": sorted(df["Source"].dropna().unique().tolist()),
        "seasons": ["Winter", "Spring", "Summer", "Autumn"],
        "decades": sorted(df["Decade"].dropna().unique().tolist()),
    }


def apply_filters(df, source_sel, year_range, season_sel, anomaly_range, decade_sel, search_text):
    filtered = df.copy()

    if source_sel:
        filtered = filtered[filtered["Source"].isin(source_sel)]

    filtered = filtered[
        (filtered["YearNum"] >= year_range[0]) & (filtered["YearNum"] <= year_range[1])
    ]

    if season_sel:
        filtered = filtered[filtered["Season"].isin(season_sel)]

    if decade_sel:
        filtered = filtered[filtered["Decade"].isin(decade_sel)]

    filtered = filtered[
        (filtered["Mean"] >= anomaly_range[0]) & (filtered["Mean"] <= anomaly_range[1])
    ]

    if search_text and search_text.strip():
        q = search_text.strip().lower()
        mask = (
            filtered["Source"].str.lower().str.contains(q, na=False)
            | filtered["Decade"].str.lower().str.contains(q, na=False)
            | filtered["Season"].str.lower().str.contains(q, na=False)
            | filtered["Year"].str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    return filtered.reset_index(drop=True)


def compute_trends(df):
    """Compute trend data for KPI indicators."""
    if df.empty or df.shape[0] < 10:
        return {"trend_direction": "neutral", "trend_value": 0.0, "rate_per_decade": 0.0}

    decades = sorted(df["Decade"].unique())
    if len(decades) >= 2:
        last_decade = df[df["Decade"] == decades[-1]]["Mean"].mean()
        prev_decade = df[df["Decade"] == decades[-2]]["Mean"].mean()
        change = last_decade - prev_decade
        direction = "up" if change > 0 else ("down" if change < 0 else "neutral")
    else:
        change = 0.0
        direction = "neutral"

    # Linear rate per decade
    yearly = df.groupby("YearNum")["Mean"].mean().reset_index()
    if len(yearly) >= 2:
        coeffs = np.polyfit(yearly["YearNum"], yearly["Mean"], 1)
        rate = coeffs[0] * 10  # per decade
    else:
        rate = 0.0

    return {
        "trend_direction": direction,
        "trend_value": float(round(change, 3)),
        "rate_per_decade": float(round(rate, 3)),
    }
