# Engineering slice execution record — 22 November 2026

**Baseline:** 7e0938d on docs/resolve-repository-review-findings, in isolated worktree feat/first-playable-vertical-slice-20261122. Existing research modifications remain in the original worktree.

**Environment:** Marcus_Computer, Windows; Python 3.11.4, Node 24.15.0. No Synthea, Pulse, or other candidate application was executed.

## Verified checks

| Test/check | Observed result |
|---|---|
| Gate A full unittest suite | **39 passed**, 0 failures |
| Playable-slice backend unittest suite | **3 passed**, 0 failures |
| SIWC smoke and server contract Node tests | **7 passed**, 0 failures |
| Local API bootstrap | Fixture-A auto-created in catalog, Luna disconnected |
| Local API new playthrough | committed; session indexed persistently |
| HTTP order T | committed |
| HTTP advance +9 seconds | committed, time 9000 ms, T released after internal authority action |
| HTTP asset T | available, samples [1, 2, 2] |
| Cross-origin POST attempt | blocked |
| Static HTML, JS, CSS GET | all returned HTTP 200 |
| UI browser automation or visual inspection | **Not tested** |
| Live OAuth consent and Luna inference through new app | **Not tested**, requires user action |
| Clinical validity, real ECG, scan/image rights | **Not tested**, not claimed |

Python tests included withholding, release rules, inspectable trace, debrief and immutable submission, review and session persistence, absence of Luna, forged model text, session separation and hidden-key exclusion.

Node tests included PKCE, ID-token signature and claims, Luna model selection, SSE completion, restricted model input, output enforcement and refresh rotation/denial. These are offline unit checks; they do not prove actual live app OAuth.

## Boundaries

- Artificial scalar and three-sample waveform, not medical measurements
- Gate A SQLite authority and deterministic worker remain test doubles
- T result authorized by internal service at 9 seconds, not by browser-controlled privilege
- No live candidate-module integration or qualified clinical validation
- Local-only HTTP server at 127.0.0.1:8787
- No API key and no conventional usage-based API billing

## Still required

1. User-initiated Luna sign-in, allowed history question, adversarial question, consent denial, refresh and reauthentication tests.
2. Browser automation and visual/accessibility review; browser network inspection for accidental hidden-answer disclosure.
3. Architecture route review before adopting this experiment as a production foundation.
