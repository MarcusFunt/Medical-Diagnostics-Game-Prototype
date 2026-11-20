# Stage 0 — Requirements card

**Status:** provisional assumptions for repository comparison; approvals remain open. This card defines the comparison slice only. It does not choose a case, foundation, or final product architecture.

## Provisional target

| Decision area | Working assumption for Stages 0–2 | Why this is a reasonable comparison baseline | Approval needed? |
|---|---|---|---|
| Intended audience | Health-profession learners with basic anatomy and physiology; start with early medical/paramedic learners. | A simple, observable diagnostic-reasoning objective is needed before comparing tools. | **Yes.** Confirm learner level and prior knowledge. |
| Learning objective | The learner chooses a useful first investigation, distinguishes an observed finding from an interpretation, submits a leading diagnosis, and explains the evidence and an important alternative. | This measures investigation and reasoning rather than lucky diagnosis alone. | **Yes.** Confirm whether prioritization, test stewardship, or treatment should be primary. |
| Inquiry and feedback style | Allow the learner to choose history questions, a focused examination, and whether/when to request the ECG; show explicit uncertainty or unavailable-result states. Debrief actions and evidence after the submitted diagnosis. | Preserves meaningful investigation choices while keeping the selection case small and comparable. | **Yes.** Confirm how open-ended inquiry and formative feedback should feel. |
| First playable | A fictional encounter with concise history/examination, one 12-lead ECG investigation, diagnosis submission, and a debrief tied to the learner's actions and the presented evidence. | ECG provides a bounded, inspectable investigation and evidence-based debrief fixture for comparing every route; this scope assumption is independent of any candidate repository. | **Yes.** Confirm ECG as the first modality and whether imaging or multiple tests must be in the first slice. |
| Treatment | Treatment is part of the longer product goal, but excluded from this first-slice comparison unless approved. No treatment-response claims are assumed. | Treatment introduces a second physiology/state-model requirement and may change the best foundation. | **Yes.** This exclusion affects whether a physiology engine is worth early integration. |
| Patient dialogue | Authored/scripted answers and examination findings for the first slice; no external or generative model required. | Keeps case truth deterministic and reduces privacy, latency, cost, and prompt-injection work while testing the game loop. | **Yes.** Confirm whether free-text/LLM conversation is essential in the first playable. |
| Platform | Browser, desktop-first, local-only/offline for selection spikes; no account, cloud service, real patient data, or multiplayer. | Fits static browser modules and avoids hosting assumptions during selection. | **Yes.** Confirm browser vs desktop/engine and mobile support. |
| Release mode | Treat the current work as a private selection prototype. Public source distribution, public hosting, classroom release, and commercial use remain undecided. | Avoids silently assuming a license or deployment target. Candidate rights still need to support any later intended use. | **Yes.** Choose intended release mode before adoption decisions. |
| Intended purpose | Educational practice only; outputs do not inform the care of a real person. This is a working product assumption, not a medical-device or regulatory classification. For later screening, use the [EU MDR 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/oj/eng), [MDCG 2019-11 rev.1 (June 2025)](https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=mdcg_2019_11_en.pdf), and [MDCG 2025-4 (June 2025)](https://health.ec.europa.eu/document/download/ec9b0f40-7f82-43a7-b833-ebd45b772eae_en?filename=mdcg_2025-4_en.pdf). | Keeps the comparison within a simulated-learning context while leaving the intended-purpose screen visible. | **Yes** if real-patient use or medical decision claims are contemplated; obtain qualified regulatory advice then. |
| Case/artifacts | Fictional authored case; generated or explicitly cleared ECG only. No patient records or candidate-bundled clinical media. | Keeps selection experiments reproducible and avoids unresolved real-data/privacy rights. | No, unless the project requires real recordings. |
| Clinical quality | Educational simulation only. One case must have coherent authorized facts, an interpretable result, a held-back answer key, and an action/evidence-based debrief. A qualified clinical reviewer must check a case before it is used as teaching content. | A source's UI polish, scenario count, tests, or claims do not establish clinical validity. | **Yes.** Name the reviewer and acceptable fidelity/validation floor before Stage 5. |
| Accessibility | Use WCAG 2.2 AA as the provisional public-web target; keyboard access and text/number alternatives for waveform interpretation are part of the quality floor. | Repositories vary widely in canvas, motion, small traces, focus handling, and semantic labeling. | Confirm target devices; otherwise keep WCAG 2.2 AA as the default. |
| AI and operating burden | No paid inference in the first slice. Prefer local deterministic behavior; if AI is later approved, measure model size, latency, cost, and network behavior separately. | AI is optional to the first comparison and must not become an authority for case truth. | **Yes** if AI dialogue is wanted in the first playable. |
| Team/runtime capacity | Languages, available maintainers, deployment capacity, and monthly operating budget are unknown. For comparison, prefer a small local browser runtime with no paid service; do not assume the team can maintain native C++ or a multi-service platform. | Avoids treating a theoretically reusable but operationally expensive system as low effort. | **Yes.** Confirm available languages, tooling, maintainers, and operating budget before advancing candidates. |
| Effort accounting | Use low / likely / high qualitative estimates with low confidence until runnable spikes exist; include adaptation, integration, missing features, content, verification, deployment and maintenance. | Avoid fabricated person-hour precision. | No; estimates will be updated after experiments. |

## Quality floor for the comparison

These are **provisional, observable acceptance criteria** for comparing routes later; none has been implemented or checked yet.

| ID | Criterion for the eventual first playable | Evidence expected at the later comparison stage |
|---|---|---|
| QF-01 | One trusted case-state component is the only source of truth for patient state, action history, objective findings, result release, and the answer key. | Trace a full playthrough and show each displayed fact maps to that authority; before debrief, the answer key is absent from client bundles, learner-facing payloads, and ordinary logs. |
| QF-02 | Each learner-visible question, exam finding, order, result status, diagnosis, and debrief item has an explicit authorization and case-time rule. | Table-test the sequence, including no ECG, limited ECG, and released ECG; viewing or pausing the artifact does not advance case time. |
| QF-03 | The first playable supports focused history and exam, an optional ECG order, result review, diagnosis entry, and action/evidence-based debrief in one encounter. | Complete the same required action path for each candidate route; record any missing or substituted action. |
| QF-04 | The ECG appears as an inspectable 12-lead artifact with labeled leads and its calibration/measurement context; the debrief distinguishes the observation from its interpretation. | Review the artifact and text/measurement equivalent; a qualified reviewer assesses clinical interpretation before teaching use. |
| QF-05 | The learner can submit one leading diagnosis and cite at least one supporting observation; the debrief points to at least one relevant action, one finding, and one uncertainty or important alternative. | Inspect the submitted response and debrief against the authored case rubric; no claim of learning effectiveness is implied. |
| QF-06 | The primary workflow is keyboard-operable, has visible focus and semantic labels, does not rely on color alone, and provides a text or numeric alternative for a small/fast waveform. | Keyboard-only pass through the same encounter and accessibility review against WCAG 2.2 AA if the public-web assumption is retained. |
| QF-07 | Selection-stage assets are synthetic or explicitly cleared, and candidate experiments use no real patient records or credentials. | Resource manifest and environment/network record for every later experiment. |

## Compact benchmark skeleton (not a selected clinical case)

- **ID:** `BENCH-ECG-SKELETON-01`.
- **Presentation:** fictional 58-year-old with two hours of palpitations and mild lightheadedness; no chest pain, syncope, or shortness of breath at rest. These details are invented placeholders, not a reviewed case.
- **Starting information:** awake and conversant; a fictional irregular pulse around 126/min, blood pressure 124/78 mmHg, and oxygen saturation 98% on room air. Values, examination, differential, and any exclusions require clinical review before use.
- **Learner actions:** focused history → pulse/perfusion examination → decide whether and when to order a 12-lead ECG → inspect the tracing → enter a leading rhythm diagnosis and supporting evidence.
- **Evidence:** a synthetic, calibration-labelled 12-lead tracing with irregular R–R intervals and no discernible regular P waves. The guideline describes atrial fibrillation on surface ECG using those broad features; an ECG remains the evidence in this game, and patient symptoms alone do not establish the rhythm. [2024 ESC atrial fibrillation guideline](https://academic.oup.com/eurheartj/article/45/36/3314/7738779).
- **Possible outcomes:** (1) timely, interpretable trace with the described rhythm; (2) technically limited trace that remains inconclusive and may be repeated; or (3) no ECG, so the rhythm stays unconfirmed. The case authority controls availability and timing.
- **Provisional hidden answer:** atrial fibrillation documented on ECG, with stable initial presentation. Do not infer the cause, duration classification, stroke risk, or treatment from this skeleton. Keep the answer key in the trusted case authority and reveal it only at debrief.
- **Debrief points:** separate observation (irregular R–R, no regular P waves) from interpretation (atrial fibrillation); explain why ECG documentation matters; identify uncertainty or one rhythm alternative; assess whether the test choice and timing matched the question.
- **Action sequence:** history → examination → order/skip ECG → result becomes available → inspect → submit diagnosis and rationale → debrief. No medication or treatment step is in this slice.
- **Out of this slice unless approved:** treatment, deterioration modeling, CT/MRI, echo, labs, longitudinal chart, AI dialogue, multiplayer, public hosting, and real clinical data.

The 2024 guideline is a research reference only. Do not copy its text, figures, or tables into the game without checking its terms. This skeleton is a provisional comparison fixture, not clinical advice or a validated educational case; it needs qualified clinical review before any teaching use. It does not grant permission to use any candidate repository's example cases or assets.

## Decisions to resolve before Stage 3/5

1. Audience and learning level.
2. Whether ECG is the first investigation, or an actual echo/radiology modality is essential in the first playable.
3. Whether treatment and physiologic response belong in the first slice.
4. Whether free-text or AI-driven patient dialogue is essential immediately.
5. Browser/offline target vs desktop/engine, and whether mobile matters.
6. Intended distribution and use (private, classroom, public source, hosted, commercial).
7. Confirm the educational-only intended purpose; identify any real-person use or medical decision claim.
8. Clinical reviewer and required review depth.

These answers can change which foundation is lowest-work. No Stage 3 execution or foundation decision should be based on the assumptions as if approved.
