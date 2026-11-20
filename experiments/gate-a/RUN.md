# Gate A run record

- Baseline commit: `764074a1520973a990539000f17cdb1a0ff8d2d1`
- Python: `Python 3.11.4`
- Command (from repository root): `python -m unittest discover -s experiments/gate-a -v`
- Result: **PASS**, 27 tests; A01–A11 all passed.
- Mode: offline, synthetic Fixture-A data, SQLite authority, deterministic worker and Luna stubs. No clinical assets, live model access, candidate code, or live consent were used.

| Scenario | Outcome | Coverage summary |
|---|---|---|
| A01 | PASS | One successful publication, retry stability, independent plays, and missing-evidence rejection. |
| A02 | PASS | Retry and target-scoped idempotency, stale revisions, authorization, and concurrent duplicates. |
| A03 | PASS | Partitioned clock advances, transition-before-capture ordering, and inclusive trace `[1, 2, 2]`. |
| A04 | PASS | Bound worker candidates, cancellation cutoff, delayed results, and release timing. |
| A05 | PASS | Atomic `processing_blocked` retry and terminal worker/validation failures without measurements. |
| A06 | PASS | Fresh-process continuation, pinned dependencies, pending work, and `restore_blocked`. |
| A07 | PASS | Role-filtered projection, metadata and assets; release, accessible text, and stored interpretation aid. |
| A08 | PASS | Submission cutoff, six debrief dimensions, evidence versions, aid record, immutable review/skip, and closed C. |
| A09 | PASS | Missing-media fallback, unsupported and unavailable capability, limited subset, invalid units, and storage rollback. |
| A10 | PASS | Luna-only dialogue, denied/unavailable/error outcomes, retry after recovery, saved utterances, and explanation outage. |
| A11 | PASS | Same-time release at submission plus collecting/processing closeout and late-work rejection. |

The fixture clock limit is `2**31 - 1` milliseconds. This is an experiment-local boundary used to verify overflow rejection; it is not a production clock decision.
