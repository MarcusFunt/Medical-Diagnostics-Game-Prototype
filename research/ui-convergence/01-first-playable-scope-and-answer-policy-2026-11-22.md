# Stage 4 Decision — First Playable Scope and Answer Reveal

**Decision date:** 22 November 2026  
**Status:** Stage 4 decision recorded for the selected playable-slice baseline  
**Baseline:** `D:\projects\Medical-Diagnostics-Game-Playable-Slice`, branch `feat/first-playable-vertical-slice-20261122`, commit `5dac76e`  
**Purpose:** Bound the first engineering proof and define what interpretation may disclose before diagnosis submission.

## Decision

The first playable remains a small, diagnosis-focused software slice. Before the player submits a diagnosis, result interpretations must not name, rank, endorse, or otherwise reveal the case's scored target diagnosis. There is no scored-hint mode in this slice.

The player may request an optional explanation after evidence is released. It may explain the observation and its units, point out visible features, and describe evidence quality, uncertainty, and limitations. It may not expose the hidden answer, the case-specific diagnosis labels or scoring rubric, or an equivalent clue that uniquely identifies the answer. After the authority commits the player's diagnosis, the debrief may reveal the reference diagnosis and rubric.

This resolves the answer-reveal choice in step 4 of the development direction. It is a first-slice policy; it does not amend the approved product vision.

## First-playable scope

The proof contains:

- One learner/player role and one synthetic case: Fixture-A.
- A bounded patient interview.
- Two artificial investigations from the current fixture: A, a numeric observation, and T, an invented three-sample signal.
- At least one inspectable artifact: T's plot and accessible text equivalent.
- A ranked differential, leading diagnosis, and submission.
- A post-submission debrief.

The current A/T labels, values, units, diagnoses, and scoring rules are software fixtures. They are not clinical evidence or a validated medical case.

The proof does not include a treatment loop, navigable 3D environment, multiplayer, a broad case library, or a claim of clinically grounded physiology. Those limits describe this prototype's acceptance scope only. The confirmed product direction remains a broader, extensible diagnosis-only educational simulation.

## Why this answer policy

The approved Product Vision and Requirements v1.0 requires that the hidden diagnosis not be revealed before the end of a playthrough, while allowing optional validated interpretations. A finding-level explanation satisfies both constraints for this proof: it helps the player inspect released evidence without giving away the scored diagnosis.

The recorded live test showed that the current Luna explanation says the trace “supports DX-A,” which is the fixture's correct target. That is a concrete answer leak, even though the response followed the reference assessment it was given. Making that response an explicit scored hint would require a new hint interaction, visible scoring consequences, and rules for how hints affect the separate score dimensions. None is required for this proof, and the approved product spec does not define such a penalty.

## Pre-submission disclosure contract

**Allowed:** explain released observations; their displayed units and timing; visible signal features; reference-supported, finding-level meaning; and technical quality, uncertainty, or limitations. It may say that a result is nonspecific or insufficient by itself.

**Disallowed:** the hidden target label or a synonym; a case-specific diagnosis list, ranking, endorsement, or “supports diagnosis X” assertion; the hidden differential or scoring rubric; unreleased evidence; private case fields; or a combination of clues that uniquely identifies the target.

The contract applies to every player-facing surface, including interpretation text, interview responses, API projections, error messages, reload/reopen flows, and model context. Diagnosis-bearing reference content must not be sent to a pre-submission explanation model. If a safe finding-level explanation cannot be produced, the explanation should be marked unavailable; the released artifact remains inspectable.

Once diagnosis submission is committed by the case authority, the debrief may reveal the reference diagnosis, scoring criteria, and feedback. Failed or uncommitted submissions do not unlock the answer.

## Handoff criteria for implementation

The next implementation work should satisfy these observable checks:

1. Before submission, released artifacts remain inspectable, and optional explanations can describe only player-released, finding-level evidence and its limitations.
2. The explanation request receives a player-safe evidence projection. It does not receive the target diagnosis, case scoring key, private truth, or unreleased results.
3. The authority or trusted server validates the disclosure boundary before committing or returning model text. A prompt instruction alone is not the control.
4. Unavailable or nonconforming explanations fail closed with a clear status and no diagnosis-bearing fallback. They do not block artifact viewing or diagnosis submission.
5. No bootstrap, action response, interpretation response, reload, or reopen reveals the answer before a committed submission. After submission, the debrief reveals the answer and feedback.
6. Requesting a safe interpretation does not incur a score penalty; this slice has no scored-hint mechanic.

## Source basis

- Development direction, step 4: lock first-playable scope and answer-reveal rule.
- Approved `Medical_Diagnostics_Game_Product_Vision_and_Requirements_v1.0_2026-11-20.md`, sections 3, 5.2, and 5.3: diagnosis-only scope, optional validated interpretation, and keeping hidden diagnosis undisclosed before the end of a playthrough.
- `experiments/playable-slice/LUNA-LIVE-TEST-2026-11-22.md`, L06 and “Finding”: the pre-submission explanation disclosed the correct synthetic target DX-A.
- `experiments/playable-slice/README.md`: Fixture-A and its A/T evidence are artificial engineering fixtures, not medical evidence.

No application code or tests were changed as part of this Stage 4 decision.


