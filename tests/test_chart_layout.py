from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tb_insights.charts import (  # noqa: E402
    cluster_profile_comparison,
    cluster_region_figure,
    clustering_scatter,
    cluster_region_share_figure,
    kmeans_model_selection_figure,
)
from tb_insights.data import cluster_profiles, load_cluster_data, load_kmeans_benchmark  # noqa: E402


class ClusterChartLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clusters = load_cluster_data()
        cls.profiles = cluster_profiles(cls.clusters)

    def test_scatter_has_no_duplicate_title_or_raw_legend_field(self):
        fig = clustering_scatter(self.clusters)
        self.assertFalse(fig.layout.title.text)
        self.assertIn("Tỷ suất mắc mới", fig.layout.xaxis.title.text)
        self.assertIn("Tỷ suất tử vong", fig.layout.yaxis.title.text)
        self.assertIn("Gánh nặng thấp hơn", [trace.name for trace in fig.data])
        self.assertIn("Gánh nặng cao hơn", [trace.name for trace in fig.data])
        self.assertNotEqual(fig.layout.legend.title.text if fig.layout.legend.title else "", "cluster_label")

    def test_region_chart_uses_short_vietnamese_labels_and_no_duplicate_title(self):
        fig = cluster_region_figure(self.clusters)
        self.assertFalse(fig.layout.title.text)
        self.assertEqual(fig.layout.yaxis.title.text, "")
        labels = list(fig.layout.yaxis.categoryarray or [])
        self.assertTrue(all(label not in {"African Region", "European Region", "South-East Asia Region"} for label in labels))
        self.assertTrue(any("Đông Nam Á" in str(label) for label in labels))
        self.assertEqual(fig.layout.barmode, "stack")

    def test_profile_chart_uses_full_sample_reference_when_one_cluster_selected(self):
        low_label = self.clusters.loc[self.clusters["cluster_id"].eq(1), "cluster_name_vi"].iloc[0]
        only_low = self.clusters[self.clusters["cluster_id"].eq(1)]
        filtered_profile = cluster_profiles(only_low)
        fig = cluster_profile_comparison(filtered_profile, self.profiles)
        self.assertEqual(fig.layout.barmode, "group")
        self.assertEqual(len(fig.data), 1)
        values = list(fig.data[0].x)
        self.assertTrue(any(value < 99.9 for value in values))
        self.assertNotEqual(fig.data[0].name, low_label)
        self.assertFalse(fig.layout.title.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
