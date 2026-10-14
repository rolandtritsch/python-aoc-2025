"""Verdict extraction and reconciliation helper behavior."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "aoc_verdict_extract.py"
FIXTURES = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "verdict-reconciliation"
    / "fixtures"
)


def extract(fixture: str, answer: int | None = None) -> dict[str, object]:
    """Run the extractor on a saved-page fixture and return its JSON result."""
    args = [sys.executable, str(SCRIPT), "--file", str(FIXTURES / fixture)]
    if answer is not None:
        args.extend(["--answer", str(answer)])
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_extract_accepts_accepted_page() -> None:
    result = extract("accepted.html")
    assert result["verdict"] == "accepted"


def test_extract_rejects_wrong_answer() -> None:
    assert extract("rejected.html")["verdict"] == "rejected"


def test_extract_reports_too_high() -> None:
    assert extract("rejected_too_high.html")["verdict"] == "rejected_too_high"


def test_extract_reports_too_low() -> None:
    assert extract("rejected_too_low.html")["verdict"] == "rejected_too_low"


def test_extract_marks_wrong_level_as_ambiguous() -> None:
    result = extract("wrong_level.html")
    assert result["verdict"] == "already_completed_or_wrong_level"


def test_extract_rate_limited() -> None:
    assert extract("rate_limited.html")["verdict"] == "rate_limited"


def test_extract_auth_required() -> None:
    assert extract("auth_required.html")["verdict"] == "auth_required"


def test_extract_unknown_page() -> None:
    result = extract("accepted.html")
    assert isinstance(result["article"], str)
    assert result["article"]


def test_extract_day_page_answers() -> None:
    result = extract("day_page_complete.html")
    assert result["acceptedAnswers"] == [1129, 6638]


def test_extract_completed_day_page() -> None:
    result = extract("day_page_complete.html")
    assert result["verdict"] == "completed_day"


def test_reconcile_matching_answer() -> None:
    result = extract("day_page_complete.html", answer=1129)
    assert result["reconciled"] is True


def test_reconcile_nonmatching_answer() -> None:
    result = extract("day_page_complete.html", answer=9999)
    assert result["reconciled"] is False
