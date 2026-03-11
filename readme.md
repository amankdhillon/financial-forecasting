# AS Funding Analytics

A dashboard and analysis suite for UCSD Associated Students quarterly funding data. Python processes CSV data and generates a JSON dataset; a React frontend visualizes it interactively.

## Directory Structure

```
finance/
├── data/                        # Quarterly CSV data files
├── src/                         # Python source code
│   ├── data_loader_with_org_id.py  # CSV loading & cleaning
│   ├── quarterly_analysis.py       # Per-quarter visualizations
│   └── comprehensive_analysis.py   # Cross-quarter analysis
├── config/
│   └── settings.py              # Paths, constants, column mappings
├── public/
│   └── dashboard_data.json      # Generated data consumed by frontend
├── outputs/                     # Generated static charts & reports
├── as_funding_dashboard.jsx     # React dashboard (main UI)
├── dashboard.css                # All frontend styles
├── main.jsx                     # React entry point
├── index.html                   # HTML shell
├── generate_dashboard_data.py   # Builds dashboard_data.json from CSVs
├── main.py                      # Runs Python analyses
├── vite.config.js               # Vite dev server config
├── package.json                 # JS dependencies
├── requirements.txt             # Python dependencies
├── run.sh                       # Refresh data (Unix/macOS)
├── run.bat                      # Refresh data (Windows)
└── start.sh                     # Start dashboard dev server
```

## Quick Start

### 1. Refresh data from CSVs
```bash
./run.sh
```
This installs Python deps, runs all analyses, and generates `public/dashboard_data.json`.

### 2. Start the dashboard
```bash
./start.sh
```
Opens the React dashboard at `http://localhost:5173`. Hot-reloads on file changes.

### Manual steps
```bash
# Python
pip3 install -r requirements.txt
python3 main.py                      # static charts → outputs/
python3 generate_dashboard_data.py   # JSON data → public/

# Frontend
npm install
npm run dev
```

## How It Works

**Backend (Python)**
- Reads quarterly CSVs from `data/`
- Cleans amounts, parses dates, validates rows
- Computes per-quarter stats, cross-quarter org rankings, seasonality averages, academic year totals, and forecast projections
- Writes everything to `public/dashboard_data.json`

**Frontend (React + Recharts)**
- Fetches `dashboard_data.json` at runtime (no hardcoded values)
- Five tabs: Overview, Quarter Drill, Org Tracker, Forecasting, Insights
- Styles live in `dashboard.css` (light beige theme with dark blue/red/burgundy accents)

## Adding New Quarter Data

1. Drop the new CSV into `data/` (e.g., `winter26.csv`)
2. Add an entry to `QUARTER_CATALOGUE` in `generate_dashboard_data.py`
3. Run `./run.sh` to regenerate the JSON
4. The dashboard picks up the new data automatically

## CSV File Format

Expected columns (after header row):
```
ORG_ID | FIN-ID # | ORGANIZATION | NAME OF EVENT | DATE | VENUE | AWARDED | TRANSACTION ID | UPDATED
```

Files without an `ORG_ID` column are handled gracefully.

## Output Files

Static charts in `outputs/`:
- `individual_quarters/` — per-quarter plots
- `1_quarterly_spending.png` — quarterly comparison
- `2_academic_year_totals.png` — academic year totals
- `3_spending_trends.png` — trend lines
- `comprehensive_analysis_report.txt` — text summary

## Dependencies

**Python 3.7+**: pandas, matplotlib, seaborn, numpy

**Node.js 18+**: react, react-dom, recharts, vite
