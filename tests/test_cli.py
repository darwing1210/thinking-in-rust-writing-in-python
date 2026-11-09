from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    env_pythonpath = str(SRC)
    return subprocess.run(
        [sys.executable, "-m", "ingest", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "PYTHONPATH": env_pythonpath},
        check=False,
    )


def test_before_timeout_prints_none() -> None:
    proc = _run(["demo", "--mode", "before", "--url", "https://news.example/timeout"])
    assert "None" in proc.stdout
    assert "missing OR timeout" in proc.stdout


def test_after_timeout_is_retryable() -> None:
    proc = _run(["demo", "--mode", "after", "--url", "https://news.example/timeout"])
    assert proc.stdout.startswith("retryable:")
    assert proc.returncode == 3


def test_after_ok() -> None:
    proc = _run(["demo", "--mode", "after", "--url", "https://news.example/ok"])
    assert proc.stdout.startswith("ok:")
    assert proc.returncode == 0


def test_before_job_can_complete_with_null_result() -> None:
    proc = _run(["jobs", "--mode", "before", "--url", "https://news.example/missing"])
    payload = json.loads(proc.stdout)
    assert payload["status"] == "completed"
    assert payload["result"] is None


def test_after_job_fails_on_missing() -> None:
    proc = _run(["jobs", "--mode", "after", "--url", "https://news.example/missing"])
    assert proc.stdout.startswith("Failed")


def test_before_pipeline_leaks_topics() -> None:
    proc = _run(["pipeline", "--mode", "before"])
    assert "inherited transportation" in proc.stdout


def test_after_pipeline_isolates_topics() -> None:
    proc = _run(["pipeline", "--mode", "after"])
    assert "transportation" in proc.stdout
    assert proc.stdout.count("transportation") == 1
