import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.pull_deploy import (
    BUILD_WORKFLOW,
    DeployError,
    VALIDATE_WORKFLOW,
    latest_validated_candidate,
    load_state,
    reconcile,
    save_state,
)


SHA_A = "a" * 40
SHA_B = "b" * 40


def run(path, sha, *, number, event="push", branch="main", status="completed", conclusion="success"):
    return {
        "id": number + 1000,
        "path": path,
        "head_sha": sha,
        "head_branch": branch,
        "event": event,
        "run_number": number,
        "status": status,
        "conclusion": conclusion,
    }


class PullDeploySelectionTests(unittest.TestCase):
    def test_selects_newest_main_commit_when_build_and_validation_pass(self):
        runs = [
            run(BUILD_WORKFLOW, SHA_B, number=11),
            run(VALIDATE_WORKFLOW, SHA_B, number=12),
            run(BUILD_WORKFLOW, SHA_A, number=10),
            run(VALIDATE_WORKFLOW, SHA_A, number=11),
        ]

        candidate, reason = latest_validated_candidate(runs)

        self.assertEqual(candidate.sha, SHA_B)
        self.assertEqual(candidate.run_id, 1011)
        self.assertEqual(reason, "")

    def test_waits_for_latest_build_instead_of_falling_back_to_old_success(self):
        runs = [
            run(BUILD_WORKFLOW, SHA_B, number=11, status="in_progress", conclusion=None),
            run(VALIDATE_WORKFLOW, SHA_B, number=12, status="in_progress", conclusion=None),
            run(BUILD_WORKFLOW, SHA_A, number=10),
            run(VALIDATE_WORKFLOW, SHA_A, number=11),
        ]

        candidate, reason = latest_validated_candidate(runs)

        self.assertIsNone(candidate)
        self.assertIn("still in_progress", reason)

    def test_failed_build_blocks_deployment(self):
        runs = [
            run(BUILD_WORKFLOW, SHA_B, number=11, conclusion="failure"),
            run(VALIDATE_WORKFLOW, SHA_B, number=12),
        ]

        candidate, reason = latest_validated_candidate(runs)

        self.assertIsNone(candidate)
        self.assertIn("ended with failure", reason)

    def test_failed_full_validation_blocks_deployment(self):
        runs = [
            run(BUILD_WORKFLOW, SHA_B, number=11),
            run(VALIDATE_WORKFLOW, SHA_B, number=12, conclusion="failure"),
        ]

        candidate, reason = latest_validated_candidate(runs)

        self.assertIsNone(candidate)
        self.assertIn("Full validation", reason)

    def test_waits_when_full_validation_has_not_started(self):
        candidate, reason = latest_validated_candidate([run(BUILD_WORKFLOW, SHA_B, number=11)])

        self.assertIsNone(candidate)
        self.assertIn("has not appeared", reason)

    def test_ignores_pull_request_and_non_main_runs(self):
        runs = [
            run(BUILD_WORKFLOW, SHA_B, number=99, event="pull_request"),
            run(BUILD_WORKFLOW, SHA_B, number=98, branch="feature/test"),
        ]

        candidate, reason = latest_validated_candidate(runs)

        self.assertIsNone(candidate)
        self.assertIn("No main-branch", reason)

    def test_rejects_non_full_commit_sha(self):
        candidate, reason = latest_validated_candidate(
            [run(BUILD_WORKFLOW, "abc1234", number=11)]
        )

        self.assertIsNone(candidate)
        self.assertIn("full commit SHA", reason)

    def test_missing_state_establishes_baseline_without_deploying(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            state = root / "state.json"
            runs = [
                run(BUILD_WORKFLOW, SHA_A, number=11),
                run(VALIDATE_WORKFLOW, SHA_A, number=12),
            ]
            with (
                patch.dict(
                    "os.environ",
                    {
                        "GAME_LAB_DEPLOY_REPO_DIR": str(repo),
                        "GAME_LAB_BASE_URL": "https://games.example.com",
                        "GAME_LAB_PULL_DEPLOY_STATE_FILE": str(state),
                    },
                    clear=False,
                ),
                patch("scripts.pull_deploy.github_json", return_value={"workflow_runs": runs}),
                patch("scripts.pull_deploy.fetch_main", return_value=SHA_B),
                patch("scripts.pull_deploy.is_ancestor", return_value=True),
                patch("scripts.pull_deploy.deployed_version", return_value="5c03e0e"),
                patch("scripts.pull_deploy.deploy") as deploy,
            ):
                self.assertEqual(reconcile(), 0)

            deploy.assert_not_called()
            self.assertEqual(load_state(state), SHA_A)

    def test_state_is_written_atomically_as_private_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "nested" / "state.json"
            save_state(state, SHA_A)

            self.assertEqual(json.loads(state.read_text()), {"tracked_sha": SHA_A})
            self.assertEqual(state.stat().st_mode & 0o777, 0o600)

    def test_corrupt_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "state.json"
            state.write_text('{"tracked_sha":"short"}')

            with self.assertRaises(DeployError):
                load_state(state)


if __name__ == "__main__":
    unittest.main()
