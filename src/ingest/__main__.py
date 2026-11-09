"""CLI used in the live demo. No network. No cloud.

Examples:
    python -m ingest demo --mode before --url https://news.example/timeout
    python -m ingest demo --mode after --url https://news.example/timeout
    python -m ingest jobs --mode after --url https://news.example/ok
    python -m ingest pipeline --mode before
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from ingest.catalog import EMPTY_TITLE_URL, MISSING_URL, OK_URL, TIMEOUT_URL


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ingest")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run ingest on one URL")
    _add_common(demo)

    jobs = sub.add_parser("jobs", help="run a job through start/finish")
    _add_common(jobs)

    pipeline = sub.add_parser("pipeline", help="show enrichment side effects")
    pipeline.add_argument("--mode", choices=("before", "after"), default="after")

    args = parser.parse_args(argv)
    if args.command == "demo":
        return _demo(args.mode, args.url)
    if args.command == "jobs":
        return _jobs(args.mode, args.url)
    return _pipeline(args.mode)


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mode", choices=("before", "after"), default="after")
    parser.add_argument(
        "--url",
        default=OK_URL,
        help=f"one of {OK_URL}, {MISSING_URL}, {EMPTY_TITLE_URL}, {TIMEOUT_URL}",
    )


def _demo(mode: str, url: str) -> int:
    if mode == "before":
        from ingest.before.errors import ingest

        try:
            result = ingest(url)
        except ValueError as exc:
            print(f"raised: {exc}")
            return 2
        print("returned:", result)
        if result is None:
            print("note: None means missing OR timeout. The caller cannot tell.")
        return 0 if result is not None else 1

    from ingest.after.errors import NotFound, Retryable, ValidationFailed
    from ingest.after.ingest import ingest
    from ingest.after.result import Err, Ok

    result = ingest(url)
    match result:
        case Ok(article):
            print(f"ok: {article.title}")
            return 0
        case Err(NotFound(missing_url)):
            print(f"not_found: {missing_url}")
            return 1
        case Err(ValidationFailed(fields)):
            print(f"validation_failed: {fields}")
            return 2
        case Err(Retryable(reason)):
            print(f"retryable: {reason}")
            return 3
        case Err(error):
            print(f"err: {error}")
            return 1


def _jobs(mode: str, url: str) -> int:
    if mode == "before":
        from ingest.before.errors import ingest
        from ingest.before.jobs import Job

        job = Job(job_id="job-1", url=url)
        job.start()
        try:
            payload = ingest(url)
        except ValueError as exc:
            job.fail(str(exc))
        else:
            # The bug: we still "complete" on None.
            job.complete(payload)
        print(_job_before_view(job))
        return 0

    from ingest.after.ingest import ingest
    from ingest.after.jobs import Pending, finish, start
    from ingest.after.types import JobId, Url

    pending = Pending(job_id=JobId("job-1"), url=Url(url))
    processing = start(pending)
    finished = finish(processing, ingest(url))
    print(type(finished).__name__, finished)
    return 0


def _pipeline(mode: str) -> int:
    first = {
        "url": OK_URL,
        "title": "City council approves downtown bike lanes",
        "body": "The council voted 8-1 to add protected bike lanes on Main Street.",
        "source": "example-news",
    }
    second = {
        "url": "https://news.example/other",
        "title": "Weather outlook",
        "body": "Sunshine through Thursday.",
        "source": "example-news",
    }
    if mode == "before":
        from ingest.before.pipeline import SHARED_TOPICS, enrich

        print("shared topics before:", list(SHARED_TOPICS))
        enrich(first)
        enrich(second)
        print("first topics:", first["topics"])
        print("second topics:", second["topics"])
        print("shared topics after:", list(SHARED_TOPICS))
        print("note: second article inherited transportation from the first run.")
        return 0

    from ingest.after.pipeline import Article, enrich

    a = enrich(
        Article(
            url=first["url"],
            title=first["title"],
            body=first["body"],
            source=first["source"],
        )
    )
    b = enrich(
        Article(
            url=second["url"],
            title=second["title"],
            body=second["body"],
            source=second["source"],
        )
    )
    print("first topics:", a.topics)
    print("second topics:", b.topics)
    return 0


def _job_before_view(job: Any) -> str:
    return json.dumps(
        {
            "job_id": job.job_id,
            "url": job.url,
            "status": job.status,
            "result": job.result,
            "error": job.error,
        },
        default=str,
    )


if __name__ == "__main__":
    raise SystemExit(main())
