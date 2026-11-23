# Stages 5–7 Execution Record

**Date:** 22 November 2026  
**Baseline:** `feat/first-playable-vertical-slice-20261122` at `5dac76e`  
**Status:** Stage 5 selected; Stage 6 software viewer implemented; Stage 7 candidate case package prepared, with clinical review still required before educational release.

## Stage 5 — One trusted owner for clinical state

**Decision:** Keep Gate A's Python `SQLiteAuthority` as the single near-term authority for this prototype. It remains the behavior reference and owns playthrough state, clinical time, orders, release, artifact access, diagnosis submission, and debrief. The selected browser slice continues to send commands through its Node/Python adapter.

The Node `local_sessions` table only maps saved playthrough IDs to case IDs. It does not own encounter time, hidden truth, release state, or grading. The `release_due` adapter reads the authority's current state and submits a release command back to that authority; it does not advance a second clock. Viewers only receive artifacts after the authority grants released-asset access.

This is a prototype decision, not a production architecture selection. The SQLite/Python implementation has not been selected for the final product.

**Player boundary change:** the browser-facing adapter now refuses to send Fixture-A's answer-bearing interpretation assessment to Luna and removes answer-bearing assessment/result fields from player projections. The synthetic case returns a safe “no clinical interpretation” status. The reference diagnosis remains available to the authority for the post-submission debrief.

## Stage 6 — Bounded evidence viewer

The pinned [12-Lead Generator source at `0db754d`](https://github.com/arpitre/12-Lead-Generator/tree/0db754d5a30e826d7662d1ba76961e088a315a91) was inspected at source level. It includes a calibrated SVG renderer, but its delivered static app also bundles case construction, interpretation/explanation logic, and a client-side blind/reveal state. The browser page is not a protected answer boundary.

**Ruling:** use a small game-owned SVG viewer for the first software proof. This avoids embedding the generator's full client state or making its answer controls part of the player shell. No 12-Lead Generator code or case data was vendored. The viewer receives its display payload only through the released artifact returned by Gate A.

The trace order now carries a deterministic, 12-channel **display-only** fixture. The viewer renders a 10-second grid at 25 mm/s and 10 mm per fixture-mV, with lead labels and an accessible text equivalent. The sample shapes and channel relationships are arbitrary software output; it is explicitly labeled **not an ECG, not patient data, and not medical evidence**. The scale values follow the technical display convention in the [ACC/AHA electrocardiography statement](https://www.ahajournals.org/doi/pdf/10.1161/circ.104.25.3169); this does not validate the generated signal.

This replaces the old stretched three-point graph for new Fixture-A runs. Older saved runs without the display payload retain a clearly labeled legacy sample plot. The authority still owns evidence eligibility and release; the browser only draws the released result.

## Stage 7 — Source-backed case package

A separate [AF-ECG case candidate](../../experiments/playable-slice/case-data/af-ecg-candidate-2026-11-22.json) now records the proposed presentation, question disclosures, timeline, investigation values, reference concept, citations, and release conditions outside the UI.

The clinical reference concept is atrial fibrillation, grounded at the source level in the [2024 ESC atrial fibrillation guideline](https://academic.oup.com/eurheartj/article/45/36/3314/7738779). The candidate is still marked `draft_not_playable`: patient-specific facts are fictional proposals, no clinical ECG asset is attached, and no qualified ECG clinician has reviewed the case. It is not served by the local app, is not in the case catalog, and must not be used for teaching or described as clinically validated until the listed review gate passes.

**Completion boundary:** the case-data structure and source dossier are prepared. Clinical teaching use remains gated on qualified review and an approved rights-cleared or clinically reviewed ECG artifact. The active software/UX fixture remains Fixture-A.

## Changed files

- `experiments/gate-a/authority.py` — validates the preview payload shape; stores it with the result; returns it only as a released artifact; adds nonclinical accessible text.
- `experiments/gate-a/workers.py` — creates the deterministic display-only signal.
- `experiments/playable-slice/backend.py` — blocks answer-bearing explanation context from reaching Luna and sanitizes player-facing projections/receipts.
- `experiments/playable-slice/app.js`, `app.css`, and `index.html` — render the released preview with an accessible SVG and explicit nonclinical labels.
- `experiments/playable-slice/README.md` — records the current fixture and boundary.
- `experiments/playable-slice/case-data/af-ecg-candidate-2026-11-22.json` — source-backed, non-playable case candidate.

No application tests were added or run in this turn.

