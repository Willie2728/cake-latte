#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("flywheel.py")


class FlywheelCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "campaign"
        self.cli(
            "init",
            "--workspace", str(self.workspace),
            "--business", "Wilkerson Collective Inc.",
            "--offer", "Test Product",
            "--landing-url", "https://example.com/app",
            "--target-mrr", "5000",
            "--arpu", "50",
            "--target-days", "90",
        )
        config_path = self.workspace / "campaign.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["audience"] = {
            "primary": "service business owners",
            "problem": "leads receive inconsistent follow-up",
            "desired_outcome": "recover more qualified opportunities",
        }
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def cli(self, *args: str, expected: int = 0) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, msg=result.stderr or result.stdout)
        source = result.stdout if expected == 0 else result.stderr
        return json.loads(source)

    def content_batch(self) -> Path:
        path = self.root / "content.json"
        path.write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "platform": "tiktok",
                            "format": "short_video",
                            "audience": "service business owners",
                            "problem": "missed follow-up",
                            "hypothesis": "specific workflow proof beats broad AI claims",
                            "experiment_cell": "specificity-v1",
                            "hook": "Your leads are not cold. Your follow-up is.",
                            "body": ["problem", "workflow", "next step"],
                            "caption": "A practical workflow demonstration.",
                            "cta": "See the workflow",
                            "media": [{"id": "media-1", "path": "https://cdn.example.com/video.mp4"}],
                            "disclosure": "AI-assisted demonstration",
                            "rights_confirmed": True,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_end_to_end_control_plane(self) -> None:
        model = self.cli("model-target", "--workspace", str(self.workspace))
        self.assertEqual(model["target_active_customers"], 100)
        self.assertGreater(model["modeled_new_customers_per_month"], 0)
        schedule = self.cli("schedule-spec", "--workspace", str(self.workspace))
        self.assertEqual(len(schedule["jobs"]), 7)
        self.assertEqual(schedule["jobs"][0]["openclaw_command"][0:3], ["openclaw", "cron", "create"])

        batch = self.content_batch()
        queued = self.cli("enqueue", "--workspace", str(self.workspace), "--input", str(batch))
        self.assertEqual(len(queued["inserted"]), 1)
        content_id = queued["inserted"][0]["content_id"]
        self.assertIn("utm_content=", queued["inserted"][0]["destination_url"])

        duplicate = self.cli("enqueue", "--workspace", str(self.workspace), "--input", str(batch))
        self.assertEqual(len(duplicate["rejected"]), 1)

        approved = self.cli(
            "approve", "--workspace", str(self.workspace), "--content-id", content_id, "--approved-by", "owner"
        )
        self.assertEqual(approved["state"], "approved")

        payload = self.cli(
            "postiz-payload",
            "--workspace", str(self.workspace),
            "--content-id", content_id,
            "--integration-id", "integration-1",
        )
        self.assertEqual(payload["posts"][0]["settings"]["__type"], "tiktok")
        self.assertEqual(payload["posts"][0]["settings"]["privacy_level"], "SELF_ONLY")

        blotato_payload = self.cli(
            "blotato-payload",
            "--workspace", str(self.workspace),
            "--content-id", content_id,
            "--account-id", "account-1",
        )
        self.assertEqual(blotato_payload["post"]["accountId"], "account-1")
        self.assertEqual(blotato_payload["post"]["target"]["targetType"], "tiktok")
        self.assertEqual(blotato_payload["post"]["target"]["privacyLevel"], "SELF_ONLY")
        self.assertTrue(blotato_payload["post"]["target"]["isAiGenerated"])

        metrics_path = self.root / "metrics.json"
        metrics_path.write_text(
            json.dumps(
                {
                    "snapshots": [
                        {
                            "content_id": content_id,
                            "platform": "tiktok",
                            "captured_at": "2026-08-04T06:00:00Z",
                            "impressions": 10000,
                            "views": 9000,
                            "average_watch_pct": 0.62,
                            "completion_rate": 0.4,
                            "shares": 180,
                            "saves": 140,
                            "comments": 40,
                            "profile_visits": 350,
                            "link_clicks": 180,
                            "signups": 30,
                            "trials": 10,
                            "purchases": 4,
                            "new_mrr": 200,
                            "content_cost": 10,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.cli("ingest-metrics", "--workspace", str(self.workspace), "--input", str(metrics_path))
        scores = self.cli("score", "--workspace", str(self.workspace))
        self.assertEqual(scores["scores"][0]["depth"], "revenue")
        self.assertGreater(scores["scores"][0]["contribution_per_1k_impressions"], 0)

        report = self.cli("report", "--workspace", str(self.workspace))
        self.assertEqual(report["economics"]["attributed_new_mrr"], 200)
        self.assertEqual(report["economics"]["target_gap"], 4800)

    def test_risky_content_is_blocked(self) -> None:
        batch = self.content_batch()
        payload = json.loads(batch.read_text(encoding="utf-8"))
        payload["items"][0]["hook"] = "Guaranteed income with no effort required"
        batch.write_text(json.dumps(payload), encoding="utf-8")
        queued = self.cli("enqueue", "--workspace", str(self.workspace), "--input", str(batch))
        self.assertEqual(queued["inserted"][0]["status"], "blocked")
        self.assertTrue(queued["inserted"][0]["risks"])
        content_id = queued["inserted"][0]["content_id"]
        error = self.cli(
            "approve", "--workspace", str(self.workspace), "--content-id", content_id, "--approved-by", "owner", expected=2
        )
        self.assertIn("Cannot approve blocked content", error["error"])


if __name__ == "__main__":
    unittest.main()
