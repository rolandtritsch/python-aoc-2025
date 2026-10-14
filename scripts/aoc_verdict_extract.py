#!/usr/bin/env python3
"""Classify a saved Advent of Code answer page and extract accepted-answer codes.

AoC submission responses and day pages are saved as HTML (e.g. the submitter's
`aoc-verdict.html`). This read-only helper turns that saved page into a stable
verdict classification and pulls out every ``Your puzzle answer was <code>N``
accepted-answer code, so an ambiguous "already completed / wrong level"
response can be reconciled against the authenticated day page without guessing.
A day page that marks the whole day complete (the ``day-success`` "Both parts
of this puzzle are complete" marker) is reported as ``completed_day`` even
though that marker sits outside the article. Only the Python standard library
is used.

Examples
--------
Classify a saved POST response::

    python3 scripts/aoc_verdict_extract.py --file /tmp/aoc-verdict.html

Reconcile an ambiguous response against a saved day page::

    python3 scripts/aoc_verdict_extract.py --file day1.html --answer 1129

The ``--answer`` flag reports whether that answer appears among the page's
accepted-answer codes, which is the reconciliation signal for an already
completed part. On a day page the codes appear in document order, part 1's
accepted answer before part 2's, so ``matchedPart`` (1-based) attributes the
match to a specific part; this is what distinguishes a genuine part-1 match
from a cross-part collision (e.g. a submitted part-2 answer on a completed
day). Exit status is always 0 for a parsed page; callers decide what
an ``unknown`` or ``auth_required`` verdict means for the cycle.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ACCEPTED_ANSWER = re.compile(
    r"Your\s+puzzle\s+answer\s+was\s*<code>\s*(\d+)\s*</code>", re.IGNORECASE
)

DAY_COMPLETED = re.compile(
    r"class\s*=\s*\"day-success\"|both\s+parts\s+of\s+this\s+puzzle\s+are\s+complete",
    re.IGNORECASE,
)


class ArticleParser(HTMLParser):
    """Collect the text inside the first ``<article>`` element."""

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article":
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "article" and self.depth:
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.parts.append(data)

    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def classify(article_text: str) -> str:
    """Return a stable verdict key from the article text.

    Known AoC response wordings map to ``accepted``, ``rejected`` (with
    ``_too_high``/``_too_low`` detail), ``already_completed_or_wrong_level``,
    ``rate_limited``, ``auth_required``, or ``unknown``. Order matters: the
    completed-level wording never appears with a right-answer wording.
    """
    low = article_text.lower()
    if "that's the right answer" in low:
        return "accepted"
    if "that's not the right answer" in low or "your answer is too" in low:
        if "too high" in low:
            return "rejected_too_high"
        if "too low" in low:
            return "rejected_too_low"
        return "rejected"
    if (
        "don't seem to be solving the right level" in low
        or "did you already complete it" in low
    ):
        return "already_completed_or_wrong_level"
    if "posting too frequently" in low or "have to wait" in low:
        return "rate_limited"
    if "log in" in low or "login" in low or "identify yourself" in low:
        return "auth_required"
    return "unknown"


def day_completed(page: str) -> bool:
    """Return whether a saved page marks its whole day as completed.

    AoC marks a completed day outside the article with a ``day-success``
    paragraph whose text includes "Both parts of this puzzle are complete".
    These markers appear only on the authenticated day page, never on a
    submission POST response.
    """
    return DAY_COMPLETED.search(page) is not None


def extract(page: str) -> dict[str, object]:
    """Return verdict, article text, and accepted-answer codes from saved HTML."""
    parser = ArticleParser()
    parser.feed(page)
    article = parser.text()
    accepted = [int(value) for value in ACCEPTED_ANSWER.findall(page)]
    verdict = classify(article)
    if verdict == "unknown" and day_completed(page):
        verdict = "completed_day"
    return {
        "verdict": verdict,
        "article": article,
        "acceptedAnswers": accepted,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Classify a saved AoC answer page and extract accepted-answer codes."
        )
    )
    parser.add_argument("--file", type=Path, help="saved HTML page; stdin if omitted")
    parser.add_argument(
        "--answer", type=int, help="answer to reconcile against accepted codes"
    )
    args = parser.parse_args(argv)
    if args.file:
        page = args.file.read_text(encoding="utf-8")
    else:
        page = sys.stdin.read()
    result = extract(page)
    if args.answer is not None:
        result["answer"] = args.answer
        matched = [
            index
            for index, code in enumerate(result["acceptedAnswers"])
            if code == args.answer
        ]
        result["reconciled"] = bool(matched)
        if matched:
            result["matchedPart"] = matched[0] + 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
