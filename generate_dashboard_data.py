#!/usr/bin/env python3
"""
Reads all quarter CSVs and writes public/dashboard_data.json
so the React frontend can fetch live data instead of using hardcoded values.

Run directly:  python3 generate_dashboard_data.py
Or via:        ./run.sh  (called automatically after main.py)
"""

import sys
import json
from pathlib import Path

import pandas as pd

# ── project paths ────────────────────────────────────────────────────
BASE = Path(__file__).parent
sys.path.append(str(BASE))
from src.data_loader_with_org_id import load_csv_file

DATA_DIR = BASE / "data"
OUT_FILE = BASE / "public" / "dashboard_data.json"

# ── quarter catalogue  ── add new quarters here as new CSVs arrive ───
# Order: (sort_key, csv_filename, key, short_label, full_label)
QUARTER_CATALOGUE = [
    (0,  "spring23.csv", "Spring_23", "SP '23", "Spring 2023"),
    (1,  "fall23.csv",   "Fall_23",   "FA '23", "Fall 2023"),
    (2,  "winter24.csv", "Winter_24", "WI '24", "Winter 2024"),
    (3,  "spring24.csv", "Spring_24", "SP '24", "Spring 2024"),
    (4,  "fall24.csv",   "Fall_24",   "FA '24", "Fall 2024"),
    (5,  "winter25.csv", "Winter_25", "WI '25", "Winter 2025"),
    (6,  "spring25.csv", "Spring_25", "SP '25", "Spring 2025"),
    (7,  "fall25.csv",   "Fall_25",   "FA '25", "Fall 2025"),
    (8,  "winter26.csv", "Winter_26", "WI '26", "Winter 2026"),
    (9,  "spring26.csv", "Spring_26", "SP '26", "Spring 2026"),
    (10, "fall26.csv",   "Fall_26",   "FA '26", "Fall 2026"),
]

MONTH_ORDER = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
)}
DIST_BINS   = [0, 100, 250, 500, 1_000, 2_500, 5_000, 1e9]
DIST_LABELS = ["<$100", "$100\u2013250", "$250\u2013500", "$500\u20131K",
               "$1K\u20132.5K", "$2.5K\u20135K", "$5K+"]

# Academic year mapping: each AY runs Fall -> Winter -> Spring
ACADEMIC_YEARS = {
    "'22\u201323": ["Spring_23"],
    "'23\u201324": ["Fall_23", "Winter_24", "Spring_24"],
    "'24\u201325": ["Fall_24", "Winter_25", "Spring_25"],
    "'25\u201326": ["Fall_25", "Winter_26", "Spring_26"],
}

# ── helpers ──────────────────────────────────────────────────────────

def compute_quarter_stats(df: pd.DataFrame, key: str) -> dict:
    """Compute all per-quarter stats needed by the dashboard."""
    df = df.copy()
    df["_mon"] = df["Event_Date"].dt.strftime("%b")
    mo_raw = (
        df.groupby("_mon")["Amount"]
        .agg(t="sum", e="count")
        .reset_index()
        .rename(columns={"_mon": "m"})
        .sort_values("m", key=lambda x: x.map(MONTH_ORDER))
    )
    mo = [{"m": r.m, "t": round(r.t), "e": int(r.e)} for r in mo_raw.itertuples()]

    top_raw = (
        df.groupby("Organization")["Amount"]
        .agg(t="sum", e="count")
        .reset_index()
        .sort_values("t", ascending=False)
        .head(10)
    )
    top = [{"o": str(r.Organization), "t": round(r.t), "e": int(r.e)}
           for r in top_raw.itertuples()]

    df["_bin"] = pd.cut(df["Amount"], bins=DIST_BINS, labels=DIST_LABELS)
    dist_counts = df["_bin"].value_counts().reindex(DIST_LABELS).fillna(0).astype(int)
    dist = [{"r": lbl, "c": int(cnt)} for lbl, cnt in zip(DIST_LABELS, dist_counts)]

    return {
        "q":    key,
        "t":    round(df["Amount"].sum()),
        "n":    len(df),
        "a":    round(df["Amount"].mean()),
        "md":   round(df["Amount"].median()),
        "mx":   round(df["Amount"].max()),
        "top":  top,
        "mo":   mo,
        "dist": dist,
    }


def compute_top_orgs(loaded: list[tuple[str, pd.DataFrame]], top_n: int = 15) -> list[dict]:
    """Compute cross-quarter TOP_ORGS data."""
    frames = []
    for key, df in loaded:
        tmp = df[["Organization", "Amount"]].copy()
        tmp["_qkey"] = key
        frames.append(tmp)
    all_df = pd.concat(frames, ignore_index=True)

    org_totals = (
        all_df.groupby("Organization")["Amount"]
        .agg(t="sum", e="count")
        .sort_values("t", ascending=False)
        .head(top_n)
        .reset_index()
    )

    qkey_order = [q[2] for q in QUARTER_CATALOGUE]
    rows = []
    for r in org_totals.itertuples():
        org_rows = all_df[all_df["Organization"] == r.Organization]
        qb_raw = (
            org_rows.groupby("_qkey")["Amount"]
            .sum()
            .round()
            .astype(int)
            .to_dict()
        )
        qb = {k: qb_raw[k] for k in qkey_order if k in qb_raw}
        rows.append({
            "o":  str(r.Organization),
            "t":  round(r.t),
            "e":  int(r.e),
            "av": round(r.t / max(len(qb), 1)),
            "nq": len(qb),
            "qb": qb,
        })
    return rows


def compute_seasonality(loaded: list[tuple[str, pd.DataFrame]]) -> list[dict]:
    """Compute quarter-type seasonality averages from actual data."""
    by_type = {"Spring": [], "Winter": [], "Fall": []}
    for key, df in loaded:
        qtype = "Spring" if key.startswith("Spring") else "Winter" if key.startswith("Winter") else "Fall"
        by_type[qtype].append({
            "total": round(df["Amount"].sum()),
            "events": len(df),
            "avg_per": round(df["Amount"].mean()),
        })

    result = []
    for qtype in ["Spring", "Fall", "Winter"]:
        entries = by_type[qtype]
        if not entries:
            continue
        avg_total = round(sum(e["total"] for e in entries) / len(entries))
        avg_events = round(sum(e["events"] for e in entries) / len(entries))
        avg_per = round(sum(e["avg_per"] for e in entries) / len(entries))
        result.append({
            "type": qtype,
            "avg": avg_total,
            "avgE": avg_events,
            "avgPer": avg_per,
            "samples": len(entries),
        })
    return result


def compute_academic_years(loaded: list[tuple[str, pd.DataFrame]]) -> list[dict]:
    """Compute academic year totals from actual data."""
    loaded_map = {key: df for key, df in loaded}
    result = []
    for ay_label, quarters in ACADEMIC_YEARS.items():
        total = 0
        events = 0
        present = 0
        for q in quarters:
            if q in loaded_map:
                total += round(loaded_map[q]["Amount"].sum())
                events += len(loaded_map[q])
                present += 1
        if present == 0:
            continue
        result.append({
            "year": ay_label,
            "total": total,
            "events": events,
            "note": f"{present}Q" if present < len(quarters) else f"{present}Q",
        })
    return result


def compute_forecast(loaded: list[tuple[str, pd.DataFrame]]) -> dict:
    """Compute forecast data from historical quarter-type data."""
    by_type = {"Spring": [], "Winter": [], "Fall": []}
    for key, df in loaded:
        qtype = "Spring" if key.startswith("Spring") else "Winter" if key.startswith("Winter") else "Fall"
        by_type[qtype].append(round(df["Amount"].sum()))

    projections = []
    for qtype, label in [("Winter", "Winter '26"), ("Spring", "Spring '26")]:
        vals = by_type[qtype]
        avg = round(sum(vals) / len(vals)) if vals else 0
        if len(vals) >= 2:
            slope = (vals[-1] - vals[0]) / (len(vals) - 1)
            trend = round(vals[-1] + slope)
        else:
            trend = avg
        projections.append({
            "q": label,
            "type": qtype,
            "avg": avg,
            "trend": trend,
            "samples": len(vals),
        })

    fall_vals = by_type["Fall"]
    fall_avg = round(sum(fall_vals) / len(fall_vals)) if fall_vals else 0

    return {
        "projections": projections,
        "fullYearAvg": fall_avg + sum(p["avg"] for p in projections),
        "fullYearTrend": fall_avg + sum(p["trend"] for p in projections),
        "historicalByType": {k: v for k, v in by_type.items()},
    }


# ── main ─────────────────────────────────────────────────────────────

def main():
    print("Generating dashboard data from CSVs...")

    loaded: list[tuple[str, pd.DataFrame]] = []
    for _, csv_name, key, short_lbl, full_lbl in QUARTER_CATALOGUE:
        path = DATA_DIR / csv_name
        if not path.exists():
            continue
        df = load_csv_file(path)
        if df is None or df.empty:
            print(f"  \u26a0  {csv_name} \u2014 no usable rows, skipping")
            continue
        loaded.append((key, df))
        print(f"  \u2713  {csv_name} \u2192 {key}  ({len(df)} events, ${df['Amount'].sum():,.0f})")

    if not loaded:
        print("No data loaded \u2014 aborting.")
        sys.exit(1)

    # Build quarter metadata from what's actually loaded
    loaded_keys = {key for key, _ in loaded}
    active = [(sk, fn, k, sl, fl) for sk, fn, k, sl, fl in QUARTER_CATALOGUE if k in loaded_keys]

    qo = [k for *_, k, sl, fl in active]
    ql = {k: sl for *_, k, sl, fl in active}
    qf = {k: fl for *_, k, sl, fl in active}

    # Per-quarter stats
    qs = [compute_quarter_stats(df, key) for key, df in loaded]

    # Cross-quarter top orgs
    top_orgs = compute_top_orgs(loaded)

    # Grand totals
    all_amounts = pd.concat([df["Amount"] for _, df in loaded])
    all_orgs = pd.concat([df["Organization"] for _, df in loaded])

    # Seasonality & academic years (computed, not hardcoded)
    seasonality = compute_seasonality(loaded)
    academic_years = compute_academic_years(loaded)
    forecast = compute_forecast(loaded)

    data = {
        "QO": qo,
        "QL": ql,
        "QF": qf,
        "QS": qs,
        "TOP_ORGS": top_orgs,
        "GRAND": {
            "total": round(all_amounts.sum()),
            "events": sum(len(df) for _, df in loaded),
            "orgs": int(all_orgs.nunique()),
        },
        "seasonality": seasonality,
        "academicYears": academic_years,
        "forecast": forecast,
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n\u2713 {OUT_FILE} written")
    print(f"  {len(loaded)} quarters \u00b7 {data['GRAND']['events']} events \u00b7 ${data['GRAND']['total']:,} total \u00b7 {data['GRAND']['orgs']} unique orgs")


if __name__ == "__main__":
    main()
