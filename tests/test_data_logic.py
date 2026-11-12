from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tb_insights.data import (  # noqa: E402
    cluster_profiles,
    data_quality_summary,
    load_cluster_data,
    load_country_data,
    region_label,
    validate_inputs,
    weighted_summary,
    yearly_weighted_summary,
)


class DataLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.country = load_country_data()
        cls.clusters = load_cluster_data()

    def test_expected_dimensions(self):
        self.assertEqual(len(self.country), 5347)
        self.assertEqual(self.country["year"].min(), 2000)
        self.assertEqual(self.country["year"].max(), 2024)
        self.assertEqual(len(self.clusters), 193)

    def test_2024_weighted_kpis(self):
        y = self.country[self.country["year"].eq(2024)]
        result = weighted_summary(y)
        self.assertEqual(int(result["inc_cases"]), 10_553_581)
        self.assertEqual(int(result["mort_cases"]), 1_198_800)
        self.assertAlmostEqual(result["inc_rate"], 130.1754, places=3)
        self.assertAlmostEqual(result["mort_rate"], 14.7869, places=3)

    def test_yearly_summary_has_full_range(self):
        summary = yearly_weighted_summary(self.country)
        self.assertEqual(int(summary["year"].min()), 2000)
        self.assertEqual(int(summary["year"].max()), 2024)
        self.assertEqual(len(summary), 25)

    def test_cluster_profiles(self):
        profiles = cluster_profiles(self.clusters)
        self.assertEqual(int(profiles["countries"].sum()), 193)
        self.assertEqual(sorted(profiles["countries"].tolist()), [26, 167])

    def test_inputs_validate(self):
        self.assertEqual(validate_inputs(self.country, self.clusters), [])

    def test_vietnam_cluster_membership(self):
        vn = self.clusters[self.clusters["iso3"].eq("VNM")]
        self.assertEqual(len(vn), 1)
        self.assertEqual(int(vn.iloc[0]["cluster_id"]), 1)

    def test_sea_region_alias_is_localized(self):
        self.assertEqual(region_label("SEA"), "Khu vực Đông Nam Á")
        self.assertEqual(region_label("SEAR"), "Khu vực Đông Nam Á")

    def test_data_quality_summary_has_expected_missing_values(self):
        quality = data_quality_summary(self.country).set_index("Cột")
        self.assertEqual(int(quality.loc["c_cdr", "Thiếu"]), 364)
        self.assertEqual(int(quality.loc["e_inc_num", "Thiếu"]), 25)

    def test_cluster_profiles_on_filtered_rows_are_rebased(self):
        filtered = self.clusters[self.clusters["g_whoregion"].eq("SEA")]
        profiles = cluster_profiles(filtered)
        self.assertAlmostEqual(float(profiles["share_pct"].sum()), 100.0, places=6)
        self.assertEqual(int(profiles["countries"].sum()), filtered["iso3"].nunique())

    def test_validate_inputs_handles_missing_columns(self):
        bad_country = self.country.drop(columns=["e_inc_num"])
        issues = validate_inputs(bad_country, self.clusters)
        self.assertTrue(any("e_inc_num" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
