# Gate A run record

- Baseline commit: `764074a1520973a990539000f17cdb1a0ff8d2d1`
- Python: `Python 3.11.4`
- Command (from repository root): `python -m unittest discover -s experiments/gate-a -v`
- Result: **PASS**, 39 tests; A01–A11 all passed.
- Mode: offline, synthetic Fixture-A data, SQLite authority, deterministic worker and Luna stubs. No clinical assets, live model access, candidate code, or live consent were used.

| Scenario | Outcome | Coverage summary |
|---|---|---|
| A01 | PASS | One successful publication, retry stability, independent plays, and missing-evidence rejection. |
| A02 | PASS | Retry and target-scoped idempotency, stale revisions, authorization, concurrent duplicates, and typed malformed/storage failures. |
| A03 | PASS | Partitioned clock advances, literal transition/capture/trace event order, inclusive trace `[1, 2, 2]`, and immediate boundary drains. |
| A04 | PASS | Bound worker candidates, cancellation cutoff, delayed results, and release timing. |
| A05 | PASS | Atomic `processing_blocked` retry, stale-candidate isolation, and terminal worker/validation failures without measurements. |
| A06 | PASS | Fresh-process continuation, pinned dependencies, pending work, and tamper-detected `restore_blocked` across state, acquisition, order, and ordinal data. |
| A07 | PASS | Role-filtered projection, metadata and assets; authority-only release, accessible text, and stored interpretation aid. |
| A08 | PASS | Submission cutoff, evidence-qualified six-dimension debrief, evidence versions, aid record, subprocess closeout, immutable review/skip, and closed C. |
| A09 | PASS | Registry-bound supported/unsupported/unavailable capability, missing-media fallback, limited subset, invalid units, and storage rollback. |
| A10 | PASS | Luna-only dialogue, unsafe text rejection, denied/unavailable/error outcomes, retry after recovery, saved utterances, and explanation outage. |
| A11 | PASS | Same-time release at submission plus collecting/processing closeout, subprocess late-candidate/release probes, and late-work rejection. |

The fixture clock limit is `2**31 - 1` milliseconds. This is an experiment-local boundary used to verify overflow rejection; it is not a production clock decision.
