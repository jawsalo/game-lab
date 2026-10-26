"""Regression checks for the provisioned Game Lab Grafana dashboard."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_PATH = ROOT / "observability" / "dashboards" / "game-lab-overview.json"


class GrafanaDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))

    def test_dashboard_has_expected_identity_and_panels(self) -> None:
        self.assertEqual(self.dashboard["uid"], "game-lab-overview")
        self.assertEqual(self.dashboard["title"], "Game Lab Overview")
        panels = self.dashboard["panels"]
        self.assertEqual(
            {panel["title"] for panel in panels},
            {
                "Requests per second by API route",
                "95th percentile response time",
                "Server error rate (5xx)",
            },
        )
        self.assertEqual(len({panel["id"] for panel in panels}), len(panels))

    def test_panels_use_the_verified_api_metric_and_prometheus(self) -> None:
        panels = self.dashboard["panels"]
        queries = " ".join(
            target["expr"]
            for panel in panels
            for target in panel.get("targets", [])
        )
        self.assertIn('job="game-lab-api"', queries)
        self.assertIn("http_server_duration_milliseconds_count", queries)
        self.assertIn("http_server_duration_milliseconds_bucket", queries)
        self.assertIn("http_status_code", queries)
        self.assertTrue(all(panel.get("datasource") == "Prometheus" for panel in panels))


if __name__ == "__main__":
    unittest.main()
