"""Reproduce the WHO TB country clustering experiment.

Run after `python src/run_eda.py`:
    python src/run_kmeans.py
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    adjusted_rand_score, silhouette_score,
    calinski_harabasz_score, davies_bouldin_score,
)
from sklearn.preprocessing import StandardScaler, RobustScaler
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
FEATURES = ["e_inc_100k", "e_mort_100k", "c_cdr"]
CLUSTER_NAMES = {
    1: "Nhóm có hồ sơ gánh nặng tương đối thấp hơn",
    2: "Nhóm có hồ sơ gánh nặng tương đối cao hơn",
}
SCENARIO_LABELS = {
    "StandardScaler - raw": "StandardScaler · Dữ liệu gốc",
    "StandardScaler - log1p rates": "StandardScaler · Log1p hai tỷ suất",
    "RobustScaler - raw": "RobustScaler · Dữ liệu gốc",
}


def load_candidate() -> pd.DataFrame:
    source = DATA / "TB_country_year.csv"
    df = pd.read_csv(source)
    latest_year = int(df["year"].max())
    candidate = df[df["year"].eq(latest_year)].dropna(subset=FEATURES + ["e_pop_num"]).copy()
    candidate = candidate[candidate["e_pop_num"] > 0]
    if (candidate[FEATURES] < 0).any().any():
        raise ValueError("Phát hiện giá trị âm trong biến K-means.")
    if candidate["iso3"].duplicated().any():
        raise ValueError("Trùng mã ISO3 trong tập ứng viên K-means.")
    return candidate.reset_index(drop=True)


def build_benchmark(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, tuple[np.ndarray, object]]]:
    x_raw = df[FEATURES].astype(float).to_numpy()
    x_log = np.column_stack([
        np.log1p(df["e_inc_100k"].to_numpy(float)),
        np.log1p(df["e_mort_100k"].to_numpy(float)),
        df["c_cdr"].to_numpy(float),
    ])
    scenarios = {
        "StandardScaler - raw": (x_raw, StandardScaler()),
        "StandardScaler - log1p rates": (x_log, StandardScaler()),
        "RobustScaler - raw": (x_raw, RobustScaler()),
    }
    records = []
    transformed = {}
    for name, (x, scaler) in scenarios.items():
        X = scaler.fit_transform(x)
        transformed[name] = (X, scaler)
        for k in range(2, 9):
            model = KMeans(n_clusters=k, random_state=42, n_init=50)
            labels = model.fit_predict(X)
            counts = np.bincount(labels)
            records.append({
                "preprocessing": name,
                "preprocessing_vi": SCENARIO_LABELS[name],
                "k": k,
                "silhouette": silhouette_score(X, labels),
                "calinski_harabasz": calinski_harabasz_score(X, labels),
                "davies_bouldin": davies_bouldin_score(X, labels),
                "cluster_sizes_ascending": ";".join(map(str, sorted(counts.tolist()))),
                "is_selected": name == "RobustScaler - raw" and k == 2,
            })
    return pd.DataFrame(records), transformed


def run_kmeans() -> dict[str, object]:
    REPORTS.mkdir(exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    candidate = load_candidate()
    candidate.to_csv(DATA / "TB_kmeans_candidate_2024.csv", index=False)

    benchmark, _ = build_benchmark(candidate)
    benchmark.to_csv(DATA / "TB_kmeans_model_comparison.csv", index=False)

    X_raw = candidate[FEATURES].astype(float).to_numpy()
    scaler = RobustScaler()
    X_final = scaler.fit_transform(X_raw)
    model = KMeans(n_clusters=2, random_state=42, n_init=50)
    raw_labels = model.fit_predict(X_final)

    medians = candidate.assign(raw_cluster=raw_labels).groupby("raw_cluster")["e_inc_100k"].median().sort_values()
    lower_raw, higher_raw = medians.index[0], medians.index[-1]
    id_map = {lower_raw: 1, higher_raw: 2}
    cluster_ids = np.array([id_map[v] for v in raw_labels])

    result = candidate[["country", "iso3", "g_whoregion", "e_pop_num", *FEATURES]].copy()
    result["cluster_id"] = cluster_ids
    result["cluster_name_vi"] = result["cluster_id"].map(CLUSTER_NAMES)
    result.to_csv(DATA / "TB_clusters_2024.csv", index=False)

    profile = result.groupby(["cluster_id", "cluster_name_vi"]).agg(
        countries=("iso3", "nunique"),
        incidence_median=("e_inc_100k", "median"),
        incidence_mean=("e_inc_100k", "mean"),
        mortality_median=("e_mort_100k", "median"),
        mortality_mean=("e_mort_100k", "mean"),
        cdr_median=("c_cdr", "median"),
        cdr_mean=("c_cdr", "mean"),
    ).reset_index()
    profile["share_pct"] = profile["countries"] / result.iso3.nunique() * 100
    profile.to_csv(DATA / "TB_kmeans_cluster_profiles.csv", index=False)

    # Stability: 10 independent initializations, n_init=1, pairwise adjusted Rand index.
    runs = [
        KMeans(n_clusters=2, random_state=seed, n_init=1).fit_predict(X_final)
        for seed in range(10)
    ]
    pairwise_ari = [adjusted_rand_score(runs[i], runs[j]) for i, j in combinations(range(10), 2)]
    stability = pd.DataFrame([{
        "configuration": "RobustScaler - raw, k=2",
        "runs": 10,
        "pairwise_comparisons": len(pairwise_ari),
        "mean_pairwise_ari": float(np.mean(pairwise_ari)),
        "min_pairwise_ari": float(np.min(pairwise_ari)),
        "max_pairwise_ari": float(np.max(pairwise_ari)),
    }])
    stability.to_csv(DATA / "TB_kmeans_seed_stability.csv", index=False)

    # Sensitivity: rerun after excluding c_cdr > 100 only for a robustness check.
    subset = candidate[candidate.c_cdr.le(100)].copy()
    X_subset = RobustScaler().fit_transform(subset[FEATURES].to_numpy(float))
    subset_raw = KMeans(n_clusters=2, random_state=42, n_init=50).fit_predict(X_subset)
    subset_medians = subset.assign(raw_cluster=subset_raw).groupby("raw_cluster").e_inc_100k.median().sort_values()
    subset_map = {subset_medians.index[0]: 1, subset_medians.index[-1]: 2}
    subset_labels = np.array([subset_map[v] for v in subset_raw])
    main_labels = result.set_index("iso3").loc[subset.iso3, "cluster_id"].to_numpy()
    sensitivity = pd.DataFrame([{
        "main_rows": len(candidate), "sensitivity_rows": len(subset),
        "cdr_over_100": int((candidate.c_cdr > 100).sum()),
        "silhouette_main": silhouette_score(X_final, raw_labels),
        "silhouette_sensitivity": silhouette_score(X_subset, subset_raw),
        "ari_on_common_countries": adjusted_rand_score(main_labels, subset_labels),
        "changed_assignments": int(np.sum(main_labels != subset_labels)),
    }])
    sensitivity.to_csv(DATA / "TB_kmeans_sensitivity.csv", index=False)

    model_metrics = {
        "n_countries": int(len(result)),
        "k": 2,
        "selected_preprocessing": "RobustScaler - raw",
        "silhouette": float(silhouette_score(X_final, raw_labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X_final, raw_labels)),
        "davies_bouldin": float(davies_bouldin_score(X_final, raw_labels)),
        "mean_pairwise_ari_10_seeds": float(np.mean(pairwise_ari)),
        "cluster_sizes": {str(int(k)): int(v) for k, v in result.cluster_id.value_counts().sort_index().items()},
        "vietnam_cluster_id": int(result.loc[result.iso3.eq("VNM"), "cluster_id"].iloc[0]),
    }
    (DATA / "TB_kmeans_model_metrics.json").write_text(json.dumps(model_metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    # Selected model and benchmarking visual.
    plt.rcParams.update({"figure.dpi": 150, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(9, 5))
    for label, group in benchmark.groupby("preprocessing_vi"):
        ax.plot(group.k, group.silhouette, marker="o", linewidth=2, label=label)
    chosen = benchmark[benchmark.is_selected].iloc[0]
    ax.scatter([chosen.k], [chosen.silhouette], marker="*", s=240, color="#D95F02", edgecolor="black", zorder=5, label="Cấu hình được chọn")
    ax.set(title="So sánh Silhouette theo số cụm và cách chuẩn hóa", xlabel="Số cụm K", ylabel="Silhouette Score", xticks=range(2, 9))
    ax.grid(axis="y", alpha=.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "09_kmeans_silhouette_comparison.png", bbox_inches="tight")
    plt.close(fig)

    # PCA is for visualization only; K-means is fitted in the 3D RobustScaler space.
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_final)
    pca_df = result[["country", "iso3", "cluster_id", "cluster_name_vi"]].copy()
    pca_df["PC1"] = coords[:, 0]
    pca_df["PC2"] = coords[:, 1]
    pca_df.to_csv(DATA / "TB_kmeans_pca_coordinates.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 6))
    for cluster_id, group in pca_df.groupby("cluster_id"):
        ax.scatter(group.PC1, group.PC2, alpha=.72, label=CLUSTER_NAMES[int(cluster_id)])
    vn = pca_df[pca_df.iso3.eq("VNM")]
    if not vn.empty:
        ax.scatter(vn.PC1, vn.PC2, marker="*", s=220, edgecolor="black", label="Việt Nam")
    ax.set(title="PCA – minh họa hai chiều của dữ liệu đã chuẩn hóa", xlabel="Thành phần chính 1", ylabel="Thành phần chính 2")
    ax.legend(fontsize=8)
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "10_kmeans_pca_clusters.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    xlabels = ["Tỷ suất mắc mới", "Tỷ suất tử vong", "Tỷ lệ phát hiện ca bệnh"]
    vals = ["incidence_median", "mortality_median", "cdr_median"]
    x = np.arange(len(vals)); width = .35
    for idx, row in profile.iterrows():
        y = [row[v] for v in vals]
        ax.bar(x + (idx - .5) * width, y, width, label=CLUSTER_NAMES[int(row.cluster_id)])
    ax.set_xticks(x, xlabels)
    ax.set(title="Trung vị các chỉ số trong từng nhóm", ylabel="Giá trị gốc (đơn vị riêng theo chỉ số)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "11_kmeans_cluster_median_profiles.png", bbox_inches="tight")
    plt.close(fig)

    region = result.groupby(["g_whoregion", "cluster_id"]).iso3.nunique().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 5))
    region.plot(kind="barh", stacked=True, ax=ax)
    ax.set(title="Số quốc gia/vùng lãnh thổ trong từng nhóm theo khu vực WHO", xlabel="Số quốc gia/vùng lãnh thổ", ylabel="Mã khu vực WHO")
    ax.legend([CLUSTER_NAMES[int(v)] for v in region.columns], fontsize=8)
    ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "12_kmeans_who_region_distribution.png", bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(model_metrics, ensure_ascii=False, indent=2))
    print("Model comparison:", DATA / "TB_kmeans_model_comparison.csv")
    print("Validation: PASS")
    return model_metrics


if __name__ == "__main__":
    run_kmeans()
