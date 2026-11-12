from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tb_insights.charts import (  # noqa: E402
    cluster_region_share_figure,
    kmeans_model_selection_figure,
    trend_figure,
)
from tb_insights.data import (  # noqa: E402
    load_cluster_data,
    load_country_data,
    load_kmeans_benchmark,
    validate_inputs,
    yearly_weighted_summary,
)


class FinalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.country = load_country_data()
        cls.clusters = load_cluster_data()
        cls.benchmark = load_kmeans_benchmark()

    def test_model_benchmark_contains_21_configurations(self):
        self.assertEqual(len(self.benchmark), 21)
        self.assertEqual(int(self.benchmark.is_selected.sum()), 1)
        chosen = self.benchmark[self.benchmark.is_selected].iloc[0]
        self.assertEqual(chosen.preprocessing, "RobustScaler - raw")
        self.assertEqual(int(chosen.k), 2)
        self.assertAlmostEqual(float(chosen.silhouette), 0.66376, places=4)

    def test_model_selection_chart_highlights_selected_configuration(self):
        fig = kmeans_model_selection_figure(self.benchmark)
        names = [trace.name for trace in fig.data]
        self.assertIn("Cấu hình được chọn", names)
        self.assertEqual(len(fig.data), 4)

    def test_region_share_chart_sums_to_100_percent(self):
        fig = cluster_region_share_figure(self.clusters)
        region_totals = {}
        for trace in fig.data:
            for region, value in zip(trace.y, trace.x):
                region_totals[region] = region_totals.get(region, 0.0) + float(value)
        self.assertTrue(region_totals)
        for value in region_totals.values():
            self.assertAlmostEqual(value, 100.0, places=5)

    def test_trend_chart_hover_shows_data_coverage(self):
        summary = yearly_weighted_summary(self.country)
        fig = trend_figure(summary, "inc_rate", "Tỷ suất mắc mới", "#123456", " ca/100.000 dân")
        self.assertIn("Số quốc gia/vùng lãnh thổ có dữ liệu", fig.data[0].hovertemplate)
        self.assertEqual(len(fig.data[0].customdata), 25)

    def test_cluster_rows_match_2024_country_source(self):
        self.assertEqual(validate_inputs(self.country, self.clusters), [])
        damaged = self.clusters.copy()
        damaged.loc[0, "e_inc_100k"] += 1
        problems = validate_inputs(self.country, damaged)
        self.assertTrue(any("do not match" in x for x in problems))

    def test_2024_top_rate_and_top_absolute_cases_are_distinguished(self):
        latest = self.country[self.country["year"].eq(2024)]
        top_rate = latest.dropna(subset=["e_inc_100k"]).nlargest(1, "e_inc_100k").iloc[0]
        top_cases = latest.dropna(subset=["e_inc_num"]).nlargest(1, "e_inc_num").iloc[0]
        self.assertEqual(top_rate["iso3"], "KIR")
        self.assertAlmostEqual(float(top_rate["e_inc_100k"]), 945.0, places=1)
        self.assertEqual(top_cases["iso3"], "IND")
        self.assertEqual(int(top_cases["e_inc_num"]), 2_710_000)

    def test_vietnam_wpr_comparison_reference_values(self):
        latest = self.country[self.country["year"].eq(2024)]
        wpr = latest[latest["g_whoregion"].eq("WPR")]
        vn = wpr[wpr["iso3"].eq("VNM")].iloc[0]
        self.assertAlmostEqual(float(vn["e_inc_100k"]), 182.0, places=1)
        self.assertAlmostEqual(float(wpr["e_inc_100k"].median()), 55.0, places=1)
        self.assertAlmostEqual(float(vn["e_mort_100k"]), 12.0, places=1)
        self.assertAlmostEqual(float(wpr["e_mort_100k"].median()), 5.7, places=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
