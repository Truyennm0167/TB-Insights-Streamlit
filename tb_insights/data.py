from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
COUNTRY_DATA_PATH = DATA_DIR / "TB_country_year.csv"
CLUSTER_DATA_PATH = DATA_DIR / "TB_clusters_2024.csv"
KMEANS_BENCHMARK_PATH = DATA_DIR / "TB_kmeans_model_comparison.csv"

NUMERIC_COUNTRY_COLUMNS = [
    "year", "e_pop_num", "e_inc_100k", "e_inc_100k_lo", "e_inc_100k_hi",
    "e_inc_num", "e_inc_num_lo", "e_inc_num_hi", "e_mort_100k",
    "e_mort_100k_lo", "e_mort_100k_hi", "e_mort_num", "e_mort_num_lo",
    "e_mort_num_hi", "c_newinc_100k", "c_cdr", "c_cdr_lo", "c_cdr_hi",
    "cfr_pct", "cfr_pct_lo", "cfr_pct_hi",
]

# WHO's country-burden file uses SEA. SEAR is retained as an alias because it
# appears in other WHO materials and older exports.
WHO_REGION_NAMES = {
    "AFR": "Khu vực Châu Phi",
    "AMR": "Khu vực Châu Mỹ",
    "EMR": "Khu vực Đông Địa Trung Hải",
    "EUR": "Khu vực Châu Âu",
    "SEA": "Khu vực Đông Nam Á",
    "SEAR": "Khu vực Đông Nam Á",
    "WPR": "Khu vực Tây Thái Bình Dương",
}

# Short labels are used in controls and chart legends to prevent clipping.
CLUSTER_DISPLAY_NAMES = {
    "Nhóm có hồ sơ gánh nặng tương đối thấp hơn": "Gánh nặng thấp hơn",
    "Nhóm có hồ sơ gánh nặng tương đối cao hơn": "Gánh nặng cao hơn",
}

WHO_REGION_SHORT_NAMES = {
    "AFR": "Châu Phi",
    "AMR": "Châu Mỹ",
    "EMR": "Đông Địa Trung Hải",
    "EUR": "Châu Âu",
    "SEA": "Đông Nam Á",
    "SEAR": "Đông Nam Á",
    "WPR": "Tây Thái Bình Dương",
}

CLUSTER_COLORS = {
    "Nhóm có hồ sơ gánh nặng tương đối thấp hơn": "#2C9C8C",
    "Nhóm có hồ sơ gánh nặng tương đối cao hơn": "#E58A4E",
}

CORE_QUALITY_COLUMNS = {
    "Dân số ước tính": "e_pop_num",
    "Tỷ suất mắc mới ước tính": "e_inc_100k",
    "Số ca mắc mới ước tính": "e_inc_num",
    "Tỷ suất tử vong ước tính": "e_mort_100k",
    "Số ca tử vong ước tính": "e_mort_num",
    "Số ca mới/tái phát được thông báo trên 100.000 dân": "c_newinc_100k",
    "Tỷ lệ phát hiện ca bệnh / bao phủ điều trị": "c_cdr",
}


def load_country_data(path: str | Path = COUNTRY_DATA_PATH) -> pd.DataFrame:
    """Load country-year WHO estimates; preserve missing values."""
    df = pd.read_csv(path)
    for col in NUMERIC_COUNTRY_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "year" in df.columns:
        df["year"] = df["year"].astype("Int64")
    for col in ["country", "iso2", "iso3", "g_whoregion"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace("", pd.NA)
    return df


def load_cluster_data(path: str | Path = CLUSTER_DATA_PATH) -> pd.DataFrame:
    """Load the pre-computed 2024 K-means membership table."""
    df = pd.read_csv(path)
    for col in ["e_pop_num", "e_inc_100k", "e_mort_100k", "c_cdr", "cluster_id"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["country", "iso3", "g_whoregion", "cluster_name_vi"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace("", pd.NA)
    return df


def load_kmeans_benchmark(path: str | Path = KMEANS_BENCHMARK_PATH) -> pd.DataFrame:
    """Load the reproducible comparison of preprocessing choices and K values."""
    df = pd.read_csv(path)
    for col in ["k", "silhouette", "calinski_harabasz", "davies_bouldin"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "is_selected" in df.columns:
        df["is_selected"] = df["is_selected"].astype(str).str.lower().isin({"true", "1", "yes"})
    return df


def available_years(df: pd.DataFrame) -> list[int]:
    return sorted(int(v) for v in df["year"].dropna().unique())


def available_regions(df: pd.DataFrame) -> list[str]:
    return sorted(str(v) for v in df["g_whoregion"].dropna().unique())


def region_label(code: str) -> str:
    return WHO_REGION_NAMES.get(str(code), str(code))


def cluster_display_name(value: str) -> str:
    """Return a short Vietnamese label for use in dashboard controls/charts."""
    return CLUSTER_DISPLAY_NAMES.get(str(value), str(value))


def filter_region(df: pd.DataFrame, regions: Iterable[str] | None) -> pd.DataFrame:
    if not regions:
        return df.copy()
    return df[df["g_whoregion"].isin(list(regions))].copy()


def weighted_summary(data: pd.DataFrame) -> dict[str, float | int]:
    """Aggregate country estimates using only rows with numerator and population.

    This is a project-level aggregation from country rows, not an official WHO
    global aggregate. The denominator follows the rows with a valid numerator.
    """
    result: dict[str, float | int] = {"countries_inc": 0, "countries_mort": 0}
    for key, numerator in [("inc", "e_inc_num"), ("mort", "e_mort_num")]:
        valid = (
            data[numerator].notna()
            & data["e_pop_num"].notna()
            & (data["e_pop_num"] > 0)
        )
        subset = data.loc[valid]
        total_cases = float(subset[numerator].sum()) if len(subset) else np.nan
        total_population = float(subset["e_pop_num"].sum()) if len(subset) else np.nan
        result[f"{key}_cases"] = total_cases
        result[f"{key}_population"] = total_population
        result[f"{key}_rate"] = (
            total_cases / total_population * 100_000
            if pd.notna(total_population) and total_population > 0
            else np.nan
        )
        result[f"countries_{key}"] = int(subset["iso3"].nunique())
    result["countries"] = int(data["iso3"].nunique())
    return result


def yearly_weighted_summary(
    df: pd.DataFrame, regions: Iterable[str] | None = None
) -> pd.DataFrame:
    scoped = filter_region(df, regions)
    rows: list[dict[str, float | int]] = []
    for year, group in scoped.groupby("year", dropna=True):
        summary = weighted_summary(group)
        summary["year"] = int(year)
        rows.append(summary)
    if not rows:
        return pd.DataFrame(
            columns=["year", "inc_cases", "inc_rate", "mort_cases", "mort_rate"]
        )
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def region_weighted_summary(df: pd.DataFrame, year: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    subset = df[df["year"].eq(year)]
    for code, group in subset.groupby("g_whoregion", dropna=True):
        values = weighted_summary(group)
        rows.append({
            "region_code": str(code),
            "region": region_label(str(code)),
            "inc_rate": values["inc_rate"],
            "mort_rate": values["mort_rate"],
            "inc_cases": values["inc_cases"],
            "mort_cases": values["mort_cases"],
            "countries": values["countries_inc"],
        })
    if not rows:
        return pd.DataFrame(columns=["region_code", "region", "inc_rate", "mort_rate", "inc_cases", "mort_cases", "countries"])
    return pd.DataFrame(rows).sort_values("inc_rate", ascending=False).reset_index(drop=True)


def country_year_row(df: pd.DataFrame, iso3: str, year: int) -> pd.Series | None:
    rows = df[df["iso3"].eq(iso3) & df["year"].eq(year)]
    return rows.iloc[0] if not rows.empty else None


def top_countries(df: pd.DataFrame, year: int, metric: str, n: int = 10) -> pd.DataFrame:
    subset = df[df["year"].eq(year)].copy()
    return subset.dropna(subset=[metric]).nlargest(n, metric)


def cluster_profiles(cluster_df: pd.DataFrame) -> pd.DataFrame:
    if cluster_df.empty:
        return pd.DataFrame(columns=[
            "cluster_id", "cluster_name_vi", "countries", "incidence_median",
            "mortality_median", "cdr_median", "share_pct",
        ])
    grouped = cluster_df.groupby(["cluster_id", "cluster_name_vi"], dropna=False)
    result = grouped.agg(
        countries=("iso3", "nunique"),
        incidence_median=("e_inc_100k", "median"),
        mortality_median=("e_mort_100k", "median"),
        cdr_median=("c_cdr", "median"),
    ).reset_index()
    total = int(cluster_df["iso3"].nunique())
    result["share_pct"] = result["countries"] / total * 100 if total else 0.0
    return result.sort_values("cluster_id").reset_index(drop=True)


def data_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize completeness of the main indicators across the full dataset."""
    rows = []
    total = len(df)
    for label, column in CORE_QUALITY_COLUMNS.items():
        missing = int(df[column].isna().sum()) if column in df.columns else total
        rows.append({
            "Chỉ số": label,
            "Cột": column,
            "Thiếu": missing,
            "Đầy đủ": total - missing,
            "Tỷ lệ đầy đủ (%)": (total - missing) / total * 100 if total else np.nan,
        })
    return pd.DataFrame(rows)


def year_coverage_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count available entities for core indicators by year."""
    rows = []
    for year, group in df.groupby("year", dropna=True):
        rows.append({
            "year": int(year),
            "entities": int(group["iso3"].nunique()),
            "incidence_available": int(group.dropna(subset=["e_inc_num", "e_pop_num"])["iso3"].nunique()),
            "mortality_available": int(group.dropna(subset=["e_mort_num", "e_pop_num"])["iso3"].nunique()),
            "cdr_available": int(group.dropna(subset=["c_cdr"])["iso3"].nunique()),
        })
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def format_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):,.0f}".replace(",", ".")


def format_decimal(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_signed(value: float | int | None, digits: int = 1, integer: bool = False) -> str | None:
    if value is None or pd.isna(value):
        return None
    body = format_int(abs(value)) if integer else format_decimal(abs(value), digits)
    sign = "+" if float(value) > 0 else "-" if float(value) < 0 else ""
    return f"{sign}{body}"


def validate_inputs(country_df: pd.DataFrame, cluster_df: pd.DataFrame) -> list[str]:
    problems: list[str] = []
    required_country = {
        "country", "iso3", "g_whoregion", "year", "e_pop_num", "e_inc_100k",
        "e_inc_num", "e_mort_100k", "e_mort_num", "c_cdr",
    }
    required_cluster = {
        "country", "iso3", "g_whoregion", "e_pop_num", "e_inc_100k",
        "e_mort_100k", "c_cdr", "cluster_id", "cluster_name_vi",
    }
    missing_c = required_country - set(country_df.columns)
    missing_k = required_cluster - set(cluster_df.columns)
    if missing_c:
        problems.append(f"Country dataset is missing columns: {sorted(missing_c)}")
    if missing_k:
        problems.append(f"Cluster dataset is missing columns: {sorted(missing_k)}")
    if not missing_c and country_df.duplicated(["iso3", "year"]).any():
        problems.append("Country dataset contains duplicate ISO3-year rows.")
    if not missing_k and cluster_df["iso3"].duplicated().any():
        problems.append("Cluster dataset contains duplicate ISO3 rows.")
    if not missing_k and len(cluster_df) != 193:
        problems.append(f"Expected 193 complete-case cluster rows; found {len(cluster_df)}.")
    if not missing_k:
        if cluster_df["cluster_id"].isna().any() or not set(cluster_df["cluster_id"].dropna().astype(int).unique()).issubset({1, 2}):
            problems.append("Cluster IDs must be non-null and limited to 1 and 2.")
        if cluster_df["cluster_name_vi"].isna().any():
            problems.append("Cluster names contain missing values.")
        if (cluster_df[["e_inc_100k", "e_mort_100k", "e_pop_num"]] < 0).any().any():
            problems.append("Cluster data contain negative rates or population values.")
    if not missing_c and not missing_k:
        country_2024 = country_df[country_df["year"].eq(2024)].set_index("iso3")
        cluster_indexed = cluster_df.set_index("iso3")
        absent = sorted(set(cluster_indexed.index) - set(country_2024.index))
        if absent:
            problems.append(f"Cluster rows not found in country-year dataset for 2024: {absent[:5]}.")
        else:
            for col in ["e_pop_num", "e_inc_100k", "e_mort_100k", "c_cdr"]:
                left = pd.to_numeric(cluster_indexed[col], errors="coerce")
                right = pd.to_numeric(country_2024.loc[cluster_indexed.index, col], errors="coerce")
                if not np.allclose(left.to_numpy(float), right.to_numpy(float), equal_nan=True, rtol=0, atol=1e-9):
                    problems.append(f"Cluster values do not match the 2024 source data for field {col}.")
                    break
    return problems
