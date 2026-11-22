# UI/UX plan steps 4–5 readiness record

**Date:** 22 November 2026 (Europe/Copenhagen)<br>
**Fixture:** Gate A `Fixture-A` v1, local SQLite authority, deterministic worker and Luna doubles<br>
**Status:** Bounded step-4 recovery checks recorded; full synthetic acceptance remains open. Step 5 is blocked on a clinically reviewed live case and artifact decision.

This record follows the supplied Player UI/UX Plan v0.4. The plan is the requested work scope; its proposed live and clinical checks do not authorize clinical claims or change the repository's separate approval gates.

## Step 4 — recovery and accessibility slice

| Scenario | Result | Observed evidence |
|---|---|---|
| Gate A authority retries, fresh-process continuation, and late work | **PASS** | `python -m unittest discover -s experiments/gate-a -v` ran 39 tests; all passed. Coverage includes same-key command replay, concurrent duplicate commands, fresh-process resume, frozen closeout, and late-result rejection. |
| Local server restart and drafts | **PASS** | Stopped and restarted the prototype against the same isolated `%TEMP%\meddx-step4-qa` data directory. The active attempt, question draft, selected order, and reasoning draft returned at the same attempt identity and clinical time. |
| Same-intent order retry, before commit | **PASS** | Simulated a lost response before commit. The request remained visibly unresolved through reload; one automatic read-only projection check did not resend it. Retrying reused the saved command identity and payload and committed the selected order batch once at 00:00. |
| Lost response, after commit | **PASS** | Simulated a response loss after the authority committed. **Check status** found the committed order batch in the projection and cleared recovery without a second placement. |
| Authority idempotency receipt | **PASS** | Repeated an identical order command with one `command_id`; both receipts were `committed`, the second was marked `replayed`, both referenced revision 1, and the projection contained one order. |
| Draft conflict across two tabs | **PASS** | Reproduced stale-tab overwrite before the change. The revised UI now adopts a newer draft when the other tab has no local edits; when both tabs have edits it preserves the local copy, exposes both restore/save choices, and blocks clinical mutations until resolution. Both choices were exercised. |
| Keyboard path through waveform, reasoning, and submission | **PASS — scoped walkthrough** | Used keyboard focus and Enter to advance time, open the synthetic T study, cite its result, return with focus on the original study button, reorder DX-B, type reasoning, review the exact snapshot, and submit. The completion page retained the submitted text. |
| Waveform visual and text access | **PASS — synthetic fixture** | T exposed an SVG image with a text description and a separate text equivalent: samples `1, 2, 2` at offsets `0, 1, 2 ms`. Opening, citing, and returning left clinical time at 00:18. |
| Reflow spot checks | **PASS — completed screen only** | With browser emulation at 1280×720 and 1024×768, the completed screen had no document-level horizontal overflow. These checks did not cover the full workflow at each size. |
| 200% zoom, screen reader, full §13 acceptance | **NOT RUN** | The desktop browser viewport was emulated; a browser zoom and screen-reader pass were not completed. Several §13 checks exceed this prototype's implemented scope. |

The order-recovery UI persists only `order_tests` command identity, expected revision, and payload. It covers the before-commit and after-commit response-loss paths above. Durable worker termination, trusted-store outage, generation/dialogue/submission recovery, and full cross-window command serialization remain unimplemented. Therefore this record does **not** declare the synthetic GUI milestone accepted.

## Step 5 — live-slice readiness

| Prerequisite | Result | Evidence or remaining decision |
|---|---|---|
| SIWC and required model | **NOT RUN in prototype work** | This prototype uses deterministic local doubles only. No SIWC request ran during these checks. Model authorization and availability for a future live slice must be confirmed for its approved case and artifact decision. |
| Live case | **BLOCKED — no approved case** | The repository's T1 records explicitly defer a clinically grounded route comparison pending the Gate B case/reference packet and qualified reviewer approval. The Synthea output reviewed so far is a software-only historical-input probe, not an approved playable case. |
| Supported artifact and claim evidence | **BLOCKED — no clinically validated artifact** | The Pulse probe demonstrated a build/runtime seam only; it did not compare outputs with a clinical reference or validate an artifact for learner interpretation. No clinical waveform, image, or measurement was selected or attached to the prototype. |
| Authority adoption for production integration | **OPEN** | Record the adopted Case Authority revision and resolve the plan's remaining clinical values before production integration. Gate A's synthetic behavior contract is not evidence of medical validity. |

No medically grounded demonstration is ready. To unblock step 5, the owner and a qualified clinical reviewer need to select a bounded case, reference source, artifact format, provenance/rights, supported measurements, and evidence-level acceptance criteria. The live case and artifact decision is deliberately left open rather than inferred from the software-only Synthea/Pulse results.

## Run record

- UI source and recovery controls: [`app.js`](app.js), [`server.py`](server.py), [`index.html`](index.html), [`styles.css`](styles.css).
- Manual prototype data remained in a temporary folder outside the repository.
- No real-patient content, clinical asset, or live model request was used in these checks.
