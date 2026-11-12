"""Reproducible data preparation and EDA outputs for TB Insights.

Run from the project root:
    python src/run_eda.py

The raw WHO file is never modified. Outputs are written to data/ and reports/.
"""
from __future__ import annotations

from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw" / "TB_burden_countries_2026-10-29.csv"
DICTIONARY = DATA / "TB_data_dictionary.csv"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

APP_COLUMNS = [
    "country", "iso2", "iso3", "g_whoregion", "year", "e_pop_num",
    "e_inc_100k", "e_inc_100k_lo", "e_inc_100k_hi", "e_inc_num",
    "e_inc_num_lo", "e_inc_num_hi", "e_mort_100k", "e_mort_100k_lo",
    "e_mort_100k_hi", "e_mort_num", "e_mort_num_lo", "e_mort_num_hi",
    "c_newinc_100k", "c_cdr", "c_cdr_lo", "c_cdr_hi", "cfr_pct",
    "cfr_pct_lo", "cfr_pct_hi",
]
CORE_QUALITY = {
    "Tỷ suất mắc mới ước tính": "e_inc_100k",
    "Số ca mắc mới ước tính": "e_inc_num",
    "Tỷ suất tử vong ước tính": "e_mort_100k",
    "Số ca tử vong ước tính": "e_mort_num",
    "Tỷ lệ phát hiện ca bệnh (c_cdr)": "c_cdr",
    "Dân số ước tính": "e_pop_num",
}


def read_and_clean() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not RAW.exists():
        raise FileNotFoundError(f"Không tìm thấy dữ liệu gốc: {RAW}")
    raw = pd.read_csv(RAW)
    clean = raw.dropna(axis=1, how="all").copy()

    for col in clean.columns:
        if col not in {"country", "iso2", "iso3", "g_whoregion"}:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")
    for col in ["country", "iso2", "iso3", "g_whoregion"]:
        if col in clean:
            clean[col] = clean[col].astype("string").str.strip()
            clean[col] = clean[col].replace("", pd.NA)
    clean["year"] = clean["year"].astype("Int64")

    missing_columns = [c for c in APP_COLUMNS if c not in clean.columns]
    if missing_columns:
        raise ValueError(f"Thiếu cột cần cho dashboard: {missing_columns}")
    app = clean[APP_COLUMNS].copy()

    if app.duplicated(["iso3", "year"]).any():
        raise ValueError("Phát hiện khóa ISO3–năm bị trùng; dừng để kiểm tra nguồn.")
    return raw, clean, app


def weighted_by_year(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, group in df.groupby("year", dropna=True):
        inc = group.dropna(subset=["e_inc_num", "e_pop_num"])
        mort = group.dropna(subset=["e_mort_num", "e_pop_num"])
        inc_pop = inc.loc[inc.e_pop_num > 0, "e_pop_num"].sum()
        mort_pop = mort.loc[mort.e_pop_num > 0, "e_pop_num"].sum()
        inc_cases = inc.loc[inc.e_pop_num > 0, "e_inc_num"].sum()
        mort_cases = mort.loc[mort.e_pop_num > 0, "e_mort_num"].sum()
        rows.append({
            "year": int(year),
            "incidence_entities": inc.iso3.nunique(),
            "mortality_entities": mort.iso3.nunique(),
            "incidence_cases_estimated": inc_cases,
            "incidence_population_covered": inc_pop,
            "incidence_rate_project_aggregate": inc_cases / inc_pop * 100000 if inc_pop else np.nan,
            "mortality_cases_estimated": mort_cases,
            "mortality_population_covered": mort_pop,
            "mortality_rate_project_aggregate": mort_cases / mort_pop * 100000 if mort_pop else np.nan,
        })
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def _save_figures(df: pd.DataFrame, yearly: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 150, "axes.spines.top": False, "axes.spines.right": False})

    vn = df[df.iso3.eq("VNM")].sort_values("year")
    charts = [
        ("01_vietnam_incidence_trend.png", "e_inc_100k", "Tỷ suất mắc mới ước tính tại Việt Nam", "Ca/100.000 dân"),
        ("02_vietnam_mortality_trend.png", "e_mort_100k", "Tỷ suất tử vong ước tính tại Việt Nam", "Ca/100.000 dân"),
        ("03_vietnam_cdr_trend.png", "c_cdr", "Tỷ lệ phát hiện ca bệnh tại Việt Nam", "%"),
    ]
    for filename, col, title, ylabel in charts:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(vn.year, vn[col], marker="o", linewidth=2)
        ax.set(title=title, xlabel="Năm", ylabel=ylabel)
        ax.grid(axis="y", alpha=.25)
        fig.tight_layout()
        fig.savefig(FIGURES / filename, bbox_inches="tight")
        plt.close(fig)

    latest = df[df.year.eq(int(df.year.max()))]
    top_rate = latest.dropna(subset=["e_inc_100k"]).nlargest(10, "e_inc_100k").sort_values("e_inc_100k")
    top_cases = latest.dropna(subset=["e_inc_num"]).nlargest(10, "e_inc_num").sort_values("e_inc_num")
    for data, metric, title, filename, xlabel in [
        (top_rate, "e_inc_100k", "10 quốc gia/vùng lãnh thổ có tỷ suất mắc mới cao nhất", "04_top10_incidence_rate.png", "Ca/100.000 dân"),
        (top_cases, "e_inc_num", "10 quốc gia/vùng lãnh thổ có số ca mắc mới ước tính lớn nhất", "05_top10_incident_cases.png", "Số ca ước tính"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.barh(data.country, data[metric])
        ax.set(title=title, xlabel=xlabel)
        ax.grid(axis="x", alpha=.25)
        fig.tight_layout()
        fig.savefig(FIGURES / filename, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(yearly.year, yearly.incidence_rate_project_aggregate, marker="o", label="Tỷ suất mắc mới")
    ax.plot(yearly.year, yearly.mortality_rate_project_aggregate, marker="o", label="Tỷ suất tử vong")
    ax.set(title="Xu hướng tỷ suất tổng hợp tính từ các dòng quốc gia có dữ liệu", xlabel="Năm", ylabel="Ca/100.000 dân")
    ax.legend()
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "06_project_weighted_global_trends.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    valid = latest.dropna(subset=["e_inc_100k", "e_mort_100k"])
    ax.scatter(valid.e_inc_100k, valid.e_mort_100k, alpha=.7)
    vnrow = valid[valid.iso3.eq("VNM")]
    if not vnrow.empty:
        ax.scatter(vnrow.e_inc_100k, vnrow.e_mort_100k, marker="*", s=180, label="Việt Nam")
        ax.legend()
    ax.set(title="Mối liên hệ mô tả giữa tỷ suất mắc mới và tử vong (2024)", xlabel="Tỷ suất mắc mới/100.000 dân", ylabel="Tỷ suất tử vong/100.000 dân")
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "07_incidence_vs_mortality_2024.png", bbox_inches="tight")
    plt.close(fig)


def run_eda() -> dict[str, object]:
    DATA.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    raw, clean, app = read_and_clean()

    clean.to_csv(DATA / "TB_cleaned_full.csv", index=False)
    app.to_csv(DATA / "TB_country_year.csv", index=False)

    quality_rows = []
    for label, col in CORE_QUALITY.items():
        missing = int(app[col].isna().sum())
        quality_rows.append({
            "indicator": label, "column": col, "missing": missing,
            "available": len(app) - missing,
            "completeness_pct": (len(app) - missing) / len(app) * 100,
        })
    quality = pd.DataFrame(quality_rows)
    quality.to_csv(DATA / "TB_data_quality_summary.csv", index=False)

    yearly = weighted_by_year(app)
    yearly.to_csv(DATA / "TB_yearly_weighted_summary.csv", index=False)

    coverage_rows = []
    for year, group in app.groupby("year"):
        coverage_rows.append({
            "year": int(year),
            "entities": int(group.iso3.nunique()),
            "incidence_available": int(group.dropna(subset=["e_inc_num", "e_pop_num"]).iso3.nunique()),
            "mortality_available": int(group.dropna(subset=["e_mort_num", "e_pop_num"]).iso3.nunique()),
            "cdr_available": int(group.dropna(subset=["c_cdr"]).iso3.nunique()),
        })
    coverage = pd.DataFrame(coverage_rows).sort_values("year")
    coverage.to_csv(DATA / "TB_year_coverage.csv", index=False)

    latest_year = int(app.year.max())
    latest = app[app.year.eq(latest_year)].copy()
    latest.to_csv(DATA / f"TB_country_comparison_{latest_year}.csv", index=False)
    vn = app[app.iso3.eq("VNM")].sort_values("year")
    vn.to_csv(DATA / "TB_vietnam_timeseries.csv", index=False)

    candidate = latest.dropna(subset=["e_inc_100k", "e_mort_100k", "c_cdr", "e_pop_num"]).copy()
    candidate = candidate[candidate.e_pop_num > 0]
    candidate.to_csv(DATA / f"TB_kmeans_candidate_{latest_year}.csv", index=False)

    _save_figures(app, yearly)

    summary = {
        "raw_rows": int(len(raw)), "raw_columns": int(len(raw.columns)),
        "clean_rows": int(len(clean)), "clean_columns": int(len(clean.columns)),
        "app_columns": int(len(app.columns)),
        "iso3_entities": int(app.iso3.nunique()),
        "year_min": int(app.year.min()), "year_max": int(app.year.max()),
        "duplicate_iso3_year": int(app.duplicated(["iso3", "year"]).sum()),
        "all_null_columns_removed": [c for c in raw.columns if c not in clean.columns],
        "kmeans_candidates_latest_year": int(candidate.iso3.nunique()),
    }
    (DATA / "TB_eda_run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run_eda()
