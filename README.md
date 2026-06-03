# TerraTrend Climate Atlas

Interactive Streamlit dashboard for exploring monthly global mean surface temperature anomalies from NASA GISTEMP and NOAA GCAG.

Data window: January 1850 to March 2026.

This repo includes two deploy surfaces:

- `index.html` for Vercel static hosting from GitHub
- `app.py` for Streamlit-compatible hosting such as Streamlit Community Cloud or Render

## What It Includes

- KPI cards for record count, peak anomaly, decadal trend, and warm-month share
- Interactive Plotly charts for trends, cumulative anomaly, distributions, correlations, and monthly heatmaps
- Sidebar filters for source, year range, season, anomaly range, decade, and search
- Exportable filtered CSV dataset
- Streamlit deployment config and platform `Procfile`

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy

### Vercel from GitHub

1. Push this repository to GitHub.
2. In Vercel, choose **Add New Project** and import the GitHub repository.
3. Set Framework Preset to **Other** if Vercel does not select it automatically.
4. Leave Build Command and Output Directory empty.
5. Deploy.

Vercel serves the static dashboard from `index.html` and reads the bundled dataset from `data/monthly.csv`.

> If you see a Vercel error about `services`, change the project Framework Preset to **Other / Static Site** in the Vercel project settings. The repo is configured as a static site, not a service.

### Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Create a new app in Streamlit Community Cloud.
3. Set the main file path to `app.py`.
4. Deploy. No secrets or external services are required.

### Render, Railway, Heroku, or Similar

Use the included `Procfile`:

```bash
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

The app is self-contained: the dataset is bundled in `data/monthly.csv`, dependencies are listed in `requirements.txt`, and Streamlit runtime settings are in `.streamlit/config.toml`.

## Project Structure

```text
dashboard_project_climate/
├── index.html
├── app.py
├── charts.py
├── filters.py
├── style.css
├── vercel.json
├── requirements.txt
├── Procfile
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
│   └── monthly.csv
└── notebooks/
    └── analysis.ipynb
```

## Data Source

Monthly global mean surface temperature anomalies from:

- NASA GISTEMP
- NOAA GCAG

Source package: Datahub.io Global Temperature dataset.
