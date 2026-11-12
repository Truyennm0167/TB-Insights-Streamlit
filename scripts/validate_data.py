from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tb_insights.data import (  # noqa: E402
    cluster_profiles, load_cluster_data, load_country_data, load_kmeans_benchmark,
    validate_inputs, weighted_summary, yearly_weighted_summary,
)

country = load_country_data()
clusters = load_cluster_data()
benchmark = load_kmeans_benchmark()
issues = validate_inputs(country, clusters)
if issues:
    raise SystemExit("\n".join(issues))

if len(benchmark) != 21:
    raise SystemExit(f"Expected 21 K-means benchmark configurations; found {len(benchmark)}.")
if int(benchmark["is_selected"].sum()) != 1:
    raise SystemExit("Benchmark must identify exactly one selected configuration.")
selected = benchmark[benchmark["is_selected"]].iloc[0]
if selected["preprocessing"] != "RobustScaler - raw" or int(selected["k"]) != 2:
    raise SystemExit("Selected K-means configuration does not match the documented model.")

summary = weighted_summary(country[country["year"].eq(2024)])
if int(summary["inc_cases"]) != 10_553_581 or int(summary["mort_cases"]) != 1_198_800:
    raise SystemExit("2024 KPI cross-check failed.")

print(f"Country-year rows: {len(country):,}")
print(f"ISO3 entities: {country['iso3'].nunique():,}")
print(f"Years: {country['year'].min()}–{country['year'].max()}")
print(f"Cluster rows: {len(clusters):,}")
print(f"K-means benchmark rows: {len(benchmark)}")
print("2024 project aggregate:")
print(json.dumps({k: summary[k] for k in ["countries_inc", "inc_cases", "inc_rate", "countries_mort", "mort_cases", "mort_rate"]}, ensure_ascii=False, indent=2))
print("Cluster profiles:")
print(cluster_profiles(clusters).to_string(index=False))
print("Yearly summary rows:", len(yearly_weighted_summary(country)))
print("Validation: PASS")
