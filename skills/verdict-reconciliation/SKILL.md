---
name: verdict-reconciliation
description: Reconcile an ambiguous Advent of Code submission response against saved page evidence and extract accepted-answer codes from saved HTML.
---

# Verdict reconciliation

Use when a submission POST returns an ambiguous response such as "You don't
seem to be solving the right level. Did you already complete it?" or any other
response that is not an explicit right/wrong answer, and when reviewing an
attempt whose acceptance was reconciled from an authenticated day page.

## Trigger

- The submitter or reviewer needs a stable verdict from saved AoC HTML.
- A POST response is not an explicit acceptance or rejection.
- The reviewer must confirm that a submitted answer matches an accepted part.

## Inputs

- Saved AoC response HTML (from the answer POST) and/or the authenticated day
  page HTML that shows accepted answers.
- The submitted answer, when reconciling.

## Procedure

1. Save the exact HTML response from the submission POST (or the authenticated
   day page) to a file. Preserve the verbatim wording as evidence.
2. Classify it deterministically:

   ```bash
   python3 scripts/aoc_verdict_extract.py --file /tmp/aoc-verdict.html
   ```

   The script reads only the file or stdin, never the network, and prints one
   JSON object with `verdict`, `article`, and `acceptedAnswers`. Verdicts:
   `accepted`, `rejected`, `rejected_too_high`, `rejected_too_low`,
   `already_completed_or_wrong_level`, `rate_limited`, `auth_required`,
   `completed_day`, `unknown`.
3. `already_completed_or_wrong_level`, login pages, network failures, and
   unrecognized responses require reconciliation, never blind acceptance or
   blind rejection. Fetch the authenticated day page, save it, and run the
   helper with `--answer` to check whether the submitted answer matches an
   accepted code:

   ```bash
   python3 scripts/aoc_verdict_extract.py --file /tmp/day1.html --answer 1129
   ```

   A matching accepted code plus a complete-parts page is authoritative
   historical acceptance for that part. A day page that shows the
   `day-success` "Both parts of this puzzle are complete" marker is classified
   `completed_day` even though that marker sits outside the article, so the
   authoritative page is never reported as `unknown`. Absence of a code is not
   rejection.
4. On a completed day page the accepted codes appear in document order — part
   1's answer first, part 2's second — so the helper also reports `matchedPart`
   (1-based) when `--answer` matches. Attribute the match to the part under
   review: `matchedPart: 1` for a part-1 attempt, `matchedPart: 2` for part 2.
   `reconciled: true` alone is not enough when both parts are complete, because
   a submitted answer could collide with the other part's accepted code.
5. Record the verdict, the verbatim response wording, the `acceptedAnswers`
   codes, the `matchedPart`, and the reconciliation result on the issue.
   Rate-limit responses require a wait before any retry; do not loop on them.

## Evidence and validation

- Fixtures in `skills/verdict-reconciliation/fixtures/` cover accepted,
  rejected, too-high/too-low, wrong-level, rate-limited, auth-required, and a
  complete day page. `tests/test_verdict_extract.py` asserts each classification
  and the reconciliation match/mismatch behavior; run `uv run --locked pytest`.
- The script is stdlib-only and deterministic: same HTML in, same JSON out.

## Stopping conditions

Stop after recording the verdict and reconciliation evidence. Do not invent an
answer, retry a POST on an ambiguous response, or start any other part. Report
the disposition on the review issue and stop.
