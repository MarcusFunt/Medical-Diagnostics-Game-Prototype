# Player UI walkthrough — synthetic first slice

**Status:** local prototype design and interaction notes; bounded step-4 recovery added<br>
**Authority:** Gate A `Fixture-A`, SQLite authority, deterministic worker and Luna doubles<br>
**Purpose:** exercise the first three development steps and a bounded recovery slice from step 4 in Player UI/UX Plan v0.4. This is an invented software fixture, not clinically grounded content.

## Walkthrough

| Screen | Player sees | Action and effect | Recovery or blocked state |
|---|---|---|---|
| Home and Library | Local-only mode, published `Fixture-A` version, recent attempts, and Continue when an attempt is active | Publish the synthetic fixture, then start an independent attempt at 00:00 | If dialogue is unavailable, case browsing and non-dialogue actions remain available. No live sign-in is offered by this non-live build. |
| Encounter | Patient alias, verified chart summary, patient-reported dialogue, and a test composer | Ask about remembered episodes; only a committed, fixture-grounded response appears in the transcript | If the Luna double is unavailable, retain the draft, show `New dialogue unavailable`, and keep the clock unchanged. Route to Chart or Investigations. |
| Investigation order | Empty worklist, supported fixture catalog, selected order tray, and exact order review | Place A (point), T (trace), and C (point) together at 00:00; placing an order does not advance time | Duplicate or unavailable items retain their receipt status. Pending results show separately from released results. |
| Worklist and time | A, T, and C status rows and the clinical clock | Advance the synthetic clock by 9 seconds. A releases automatically; T remains pending authorized release; C is still ordered | A withheld result has no learner-visible result metadata or artifact. The only clock control is an explicit committed wait. |
| Study viewer | Released result value, units, acquisition and release times, a plotted trace when available, and a text equivalent | Open A or T, optionally compare compatible point results in this same attempt, and cite into general reasoning or a selected hypothesis | If no compatible earlier measurement exists, say so. A same-time comparison is not described as a trend or prior value. Return to the worklist with the originating selection. |
| Diagnosis draft | Ranked DX-A / DX-B hypotheses and editable reasoning draft with inserted evidence citations | Rank the leading diagnosis and review the generated draft | Draft citations remain editable. The result viewer does not submit reasoning by itself. |
| Submission review | Exact leading diagnosis, ordered differential, reasoning text, evidence cutoff, and per-order closeout preview | Confirm the reviewed snapshot to submit | Submission requires a deliberate confirmation. At 9 seconds, A and T stay released; C closes while still ordered, before its 11-second capture. |
| Completed attempt and Debrief | Frozen submission immediately, followed by fixture feedback when available | Inspect the fixture rubric and optionally submit or skip case feedback | If debrief rendering is unavailable, keep the frozen submission visible and allow feedback or Skip independently. The clinical clock and orders remain closed. |
| Lost order response | Recovery panel names the unresolved order and offers **Check status** and **Retry same order** | Check the authority projection once, then retry the same saved command identity and payload if still unresolved | The request identity and order payload survive reload. A late response after commit is recovered from the projection without placing the order twice. |
| Draft conflict in two tabs | The newer saved revision and local edits stay separate | Choose **Use newer saved draft** or **Keep my draft and save it** | Clinical mutations pause until the player resolves the conflict. A stale tab cannot silently overwrite a newer draft. |

## Action notes

- Navigation, result viewing, evidence citation, and feedback have zero clinical duration. Only the authority `wait` command advances the clock.
- Orders, waits, diagnosis submission, and feedback are committed to the active attempt through the Gate A port. Browser drafts and screen selection are presentation state.
- Results and assets are read through the authority's attempt-scoped access methods. A withheld result does not enter the learner projection.
- The local walkthrough has synthetic controls for dialogue availability, manual T release, one-shot lost order responses, debrief outage, and a post-submission wait. They exercise the local harness; they are not player-facing live-service controls.
- The order response control can drop a response before commit or after commit. A pre-commit loss remains unresolved through reload and can be retried with the original identity. A post-commit loss resolves through a read-only projection check.
- The fixture has one acquisition time for A and B, so it cannot demonstrate a *prior* compatible measurement or a trend. The viewer can compare compatible same-time point readings if both were ordered, and labels that comparison accurately. A later fixture should add a distinct earlier point if the walkthrough must validate the plan's prior-measurement path.
- The prototype persists pending order requests and browser drafts. It does not implement terminal worker reconciliation, trusted-store outage handling, or recovery controls for every command type.

## Screen flow

```text
Home / Library
  → Generate local Fixture-A → Start Attempt 1
  → Encounter (dialogue available or blocked)
  → Review orders → Place A + T + C
  → Advance clinical time to 00:09
  → Fixture authority releases T → Open released study
  → Cite evidence → Rank DX-A / DX-B
  → Review exact submission + mixed-panel closeout → Confirm
  → Frozen completed attempt → Debrief or debrief-outage fallback → Feedback / Skip
```

## Remaining beyond this recovery slice

Live Sign in with ChatGPT and inference, clinically reviewed patient details or artifact claims, production security, broad investigation catalog, terminal recovery for abandoned workers, full cross-window command arbitration, complete accessibility acceptance, and release readiness.
