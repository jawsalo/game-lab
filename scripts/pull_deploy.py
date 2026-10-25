#!/usr/bin/env python3
"""Pull and deploy the newest fully validated Game Lab main-branch image build.

This runs on the VPS. It reads public GitHub Actions metadata and never needs a
GitHub token. The first successful check establishes a baseline without
deploying, so installing the timer cannot unexpectedly roll production.
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPOSITORY = "jawsalo/game-lab"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY}"
BUILD_WORKFLOW = ".github/workflows/build-images.yml"
VALIDATE_WORKFLOW = ".github/workflows/validate.yml"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
LOG = logging.getLogger("game-lab-pull-deploy")


@dataclass(frozen=True)
class Candidate:
    sha: str
    run_id: int


class DeployError(RuntimeError):
    """Raised when the deployment must stop safely."""


def github_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "game-lab-pull-deployer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            value = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise DeployError(f"Could not read GitHub Actions status: {exc}") from exc
    if not isinstance(value, dict):
        raise DeployError("GitHub returned an unexpected response.")
    return value


def latest_validated_candidate(runs: list[dict[str, Any]]) -> tuple[Candidate | None, str]:
    """Return the newest main push with both image publishing and validation green."""
    build_runs = [
        run
        for run in runs
        if run.get("path") == BUILD_WORKFLOW
        and run.get("event") == "push"
        and run.get("head_branch") == "main"
    ]
    if not build_runs:
        return None, "No main-branch image build has run yet."

    build = max(build_runs, key=lambda run: int(run.get("run_number", 0)))
    sha = str(build.get("head_sha", ""))
    if not FULL_SHA.fullmatch(sha):
        return None, "Latest image build did not contain a full commit SHA."
    if build.get("status") != "completed":
        return None, f"Image build for {sha[:7]} is still {build.get('status', 'pending')}."
    if build.get("conclusion") != "success":
        return None, f"Image build for {sha[:7]} ended with {build.get('conclusion')}."

    validate_runs = [
        run
        for run in runs
        if run.get("path") == VALIDATE_WORKFLOW
        and run.get("event") == "push"
        and run.get("head_branch") == "main"
        and run.get("head_sha") == sha
    ]
    if not validate_runs:
        return None, f"Full validation for {sha[:7]} has not appeared yet."
    validation = max(validate_runs, key=lambda run: int(run.get("run_number", 0)))
    if validation.get("status") != "completed":
        return None, f"Full validation for {sha[:7]} is still {validation.get('status', 'pending')}."
    if validation.get("conclusion") != "success":
        return None, f"Full validation for {sha[:7]} ended with {validation.get('conclusion')}."

    return Candidate(sha=sha, run_id=int(build.get("id", 0))), ""


def run(command: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, check=check)


def fetch_main(repo_dir: Path) -> str:
    run(["git", "-C", str(repo_dir), "fetch", "--quiet", "origin", "main"])
    result = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "FETCH_HEAD"],
        check=True,
        text=True,
        capture_output=True,
    )
    sha = result.stdout.strip()
    if not FULL_SHA.fullmatch(sha):
        raise DeployError("git fetch did not return a full main-branch commit SHA.")
    return sha


def is_ancestor(repo_dir: Path, older: str, newer: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(repo_dir), "merge-base", "--is-ancestor", older, newer],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def deployed_version(namespace: str) -> str:
    result = subprocess.run(
        ["kubectl", "-n", namespace, "get", "deployment/game-lab-api", "-o", "json"],
        check=True,
        text=True,
        capture_output=True,
    )
    try:
        deployment = json.loads(result.stdout)
        api = next(
            container
            for container in deployment["spec"]["template"]["spec"]["containers"]
            if container.get("name") == "api"
        )
        return next(
            env["value"]
            for env in api.get("env", [])
            if env.get("name") == "APP_VERSION"
        )
    except (KeyError, StopIteration, TypeError, json.JSONDecodeError) as exc:
        raise DeployError("Could not read the running API version from Kubernetes.") from exc


def load_state(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        sha = value["tracked_sha"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise DeployError(f"Deployment state at {path} is unreadable; refusing to deploy.") from exc
    if not isinstance(sha, str) or not FULL_SHA.fullmatch(sha):
        raise DeployError(f"Deployment state at {path} contains an invalid commit SHA.")
    return sha


def save_state(path: Path, sha: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".deploy-state-", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            os.chmod(temporary_path, 0o600)
            json.dump({"tracked_sha": sha}, temporary)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def is_https_origin(value: str) -> bool:
    try:
        parsed = urllib.parse.urlsplit(value)
        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.path in {"", "/"}
            and not parsed.query
            and not parsed.fragment
            and parsed.username is None
            and parsed.password is None
            and (parsed.port is None or 1 <= parsed.port <= 65535)
        )
    except ValueError:
        return False


def deploy(repo_dir: Path, sha: str, base_url: str, namespace: str) -> None:
    with tempfile.TemporaryDirectory(prefix="game-lab-deploy-") as temporary:
        source = Path(temporary) / "source"
        run(["git", "-C", str(repo_dir), "worktree", "add", "--detach", str(source), sha])
        try:
            run(["bash", "scripts/deploy.sh", f"sha-{sha[:7]}", base_url], cwd=source)
        finally:
            run(
                ["git", "-C", str(repo_dir), "worktree", "remove", "--force", str(source)],
                check=False,
            )
    actual = deployed_version(namespace)
    if actual != sha[:7]:
        raise DeployError(
            f"Deployment command completed, but Kubernetes reports API version {actual!r}; "
            f"expected {sha[:7]}. State was not advanced."
        )


def reconcile() -> int:
    repo_dir = Path(os.environ.get("GAME_LAB_DEPLOY_REPO_DIR", Path(__file__).resolve().parents[1])).resolve()
    base_url = os.environ.get("GAME_LAB_BASE_URL", "").rstrip("/")
    namespace = os.environ.get("GAME_LAB_NAMESPACE", "game-lab")
    state_file = Path(
        os.environ.get(
            "GAME_LAB_PULL_DEPLOY_STATE_FILE",
            Path.home() / ".local/state/game-lab-pull-deploy/state.json",
        )
    )
    if not is_https_origin(base_url):
        raise DeployError("GAME_LAB_BASE_URL must be an HTTPS origin without a path.")
    if not repo_dir.is_dir():
        raise DeployError(f"Deployment checkout does not exist: {repo_dir}")

    lock_path = state_file.parent / "deployer.lock"
    lock_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with lock_path.open("a", encoding="utf-8") as lock:
        os.chmod(lock_path, 0o600)
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            LOG.info("A deployment check is already running; skipping this timer tick.")
            return 0

        runs = github_json(f"{API_ROOT}/actions/runs?branch=main&event=push&per_page=100").get(
            "workflow_runs", []
        )
        candidate, reason = latest_validated_candidate(runs)
        if candidate is None:
            LOG.info("No deployment: %s", reason)
            return 0

        main_sha = fetch_main(repo_dir)
        if not is_ancestor(repo_dir, candidate.sha, main_sha):
            raise DeployError(
                f"Validated commit {candidate.sha[:7]} is not an ancestor of current main {main_sha[:7]}."
            )

        tracked_sha = load_state(state_file)
        if tracked_sha is None:
            live = deployed_version(namespace)
            save_state(state_file, candidate.sha)
            LOG.info(
                "Initialized deployment baseline at %s (live API reports %s); no rollout on first run.",
                candidate.sha[:7],
                live,
            )
            return 0

        if candidate.sha == tracked_sha:
            LOG.info("No new validated main build; current candidate remains %s.", candidate.sha[:7])
            return 0
        if not is_ancestor(repo_dir, tracked_sha, candidate.sha):
            raise DeployError(
                f"Candidate {candidate.sha[:7]} is not newer than tracked commit {tracked_sha[:7]}; "
                "refusing a rollback caused by rewritten history."
            )

        live = deployed_version(namespace)
        if live == candidate.sha[:7]:
            save_state(state_file, candidate.sha)
            LOG.info("Kubernetes already runs %s; advanced deployment state.", candidate.sha[:7])
            return 0

        LOG.info(
            "Deploying validated commit %s (image build run %s); live API version is %s.",
            candidate.sha[:7],
            candidate.run_id,
            live,
        )
        deploy(repo_dir, candidate.sha, base_url, namespace)
        save_state(state_file, candidate.sha)
        LOG.info("Deployment and smoke tests passed for %s.", candidate.sha[:7])
        return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        return reconcile()
    except (DeployError, OSError, subprocess.CalledProcessError) as exc:
        LOG.error("Pull deployment failed safely: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
