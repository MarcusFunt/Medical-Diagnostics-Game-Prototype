# Medical Diagnostics Game — Repository Selection and Verification Plan

**Version:** 2.2 (revised selection plan)  
**Prepared:** 20 November 2026  
**Status:** Plan only. No repository has been newly shortlisted, cloned, installed, benchmarked, integrated, scored, or selected as part of this revision.  
**Project baseline:** A new Medical Diagnostics Game, starting from zero. There is no existing game application, runtime, or application compatibility baseline.  
**Primary input:** *Medical Diagnostics Game — Repository Selection and Verification Plan*, v2.1 (19 November 2026).  
**Inventory of record:** *Medical diagnostics game canonical repositories and research*, v1.1 (19 November 2026), subject to subsequent verified corrections.

> **Purpose:** Select the repository foundation and/or reusable components that can produce the best first playable medical diagnostic reasoning game with the **least total custom work**, without sacrificing non-negotiable clinical integrity, rights, privacy, security, and user experience. This is a plan for choosing and verifying software, **not** a plan to build the finished game and **not** an adoption decision.

## Executive decision

The evaluation must compare **complete routes from zero**, not candidate repositories against a nonexistent application:

1. **Adapt an existing game/encounter foundation**, using additional modules only where justified.
2. **Adopt a case/encounter engine**, and add carefully selected dialogue, EHR, investigation, and visualization modules.
3. **Write only a small authoritative case core**, reusing high-value modules for patient interaction and medical investigations.
4. **Implement a minimal first slice mostly from scratch**, if repository reuse offers no net advantage.
5. **Adopt nothing yet**, if no route can satisfy the essential quality and rights conditions.

The winner is the route that meets the agreed first-playable quality floor at the lowest credible **total work and risk**, with the best extensibility where additional effort is justified. Do not equate more existing features, more repositories, fewer new lines of code, or higher GitHub popularity with lower total work.

Selection proceeds **cheap evidence first, expensive evidence only when decision-changing**. Evaluate a module against its own promised capability; evaluate a *portfolio* against the complete clinical encounter. Screen safety and licensing before executing untrusted code, but reserve exhaustive audit for plausible adoption candidates. Preserve unknowns explicitly.

The canonical inventory reportedly tracks **112 primary-host entries**, plus supplementary leads. These represent different kinds of artifacts—not 112 competing games. Maintain and annotate that inventory instead of producing 112 new dossiers. This count is inherited from canonical v1.1; it is not independently re-audited by this revision.

## 1. Non-negotiable principles and project boundaries

### 1.1 Intended product

The target is a **diagnostic reasoning and investigation game**, not an operational clinical decision-support tool. A first playable encounter should let a learner, to the extent relevant for that case:

- Receive a coherent presentation and interact with a patient, companion, or clinical information source.
- Ask follow-up questions and perform selected examination or history-taking actions.
- Order investigations and inspect their results, including at least one meaningful clinical artifact if the case requires one.
- Build or revise a differential diagnosis, submit a final diagnosis, and receive a debrief tied to actions and evidence.

A complete first slice **does not need every specialty, modality, treatment mechanic, multiplayer mode, or production operation**. Treatment is mandatory only if chosen in the first-slice requirements. The first case is a representative benchmark, not a commitment to a specific final game architecture.

### 1.2 Clinical-truth and information boundaries

Each solution route must satisfy these **behavioral invariants**, whether natively or through trusted adapters:

1. **One authoritative clinical truth:** A trusted component owns case state, patient status, timeline, available actions, objective findings, diagnosis/answer key, and release rules. The authoritative component may be adapted from an existing foundation or newly written.
2. **One authoritative clinical clock:** Questions, examination, orders, acquisitions, treatments (if applicable), reports, and repeat observations follow one coherent simulation timeline. Renderer playback controls must not silently advance or rewind clinical state.
3. **No invented objective findings:** Generative dialogue may paraphrase or express **authorized facts**, but must not fabricate ECGs, labs, imaging, examinations, treatment responses, or timestamps as canonical observations.
4. **Bounded disclosure:** Learners and patient-facing dialogue receive only information their roles are authorized to know at that point. Hidden diagnosis and unreleased results must not leak through client bundles, API payloads, normal logs, ordinary user-visible model context, or browser assets.
5. **Role-specific privileged processing:** A *trusted server-side* adjudicator or debrief mechanism may receive the answer key when genuinely necessary, under a separate privilege boundary. A patient-dialogue model must not. “No hidden facts in model context” applies to untrusted or unauthorized model roles, not every possible trusted server process.
6. **Consistent multimodal evidence:** Results and artifacts must agree with case truth or explicitly document the clinically justified discrepancy, uncertainty, or limitation. Electrical rhythm is not equivalent to effective perfusion.
7. **Auditable decision history:** The system must preserve enough ordered actions and released evidence to reconstruct and explain the learner's decisions. Implementation details (event sourcing, schema shape, storage technology) remain negotiable.

Do **not** require every upstream library to implement the game's internal contract directly. A bounded adapter may translate library events and data into the authoritative clinical model. A visualization module may maintain rendering, playback, selection, or viewport state without becoming a second source of clinical truth.

### 1.3 Explicit non-goals of selection

- No redesign or implementation of the complete game during repository selection.
- No cloning/testing the full inventory.
- No production deployment, real patient data collection, medical-device certification, or educational efficacy claims.
- No adoption solely because a repository looks sophisticated, has many stars, or claims medically realistic output.
- No assumption that a current project implementation, stack, or frontend exists.
- No assumption that all modules must use the same programming language or event architecture internally.

## 2. Evaluation units: repositories, capabilities, and solution routes

A central correction from v2.1 is to keep these units distinct:

| Unit | Definition | What is tested | What is **not** required |
| --- | --- | --- | --- |
| **Repository / package** | Pinned source, dependencies and associated resources | Identity, rights, maintenance, security, actual usable surface | An entire game by itself |
| **Capability / module** | A reusable function such as ECG generation, patient dialogue, case state, ordering, or DICOM viewing | **Role-specific** functionality, quality, interface, effort to reuse | Complete patient-to-diagnosis encounter |
| **Foundation** | A candidate capable of owning substantial case/game behavior | Case authority, extensibility, encounter loop, debrief integration | Every conceivable medical modality |
| **Portfolio / route** | Foundation and/or custom core plus selected modules and adapters | **End-to-end** first playable encounter and total effort | A fixed number of repositories |
| **Reference implementation** | Source used for design lessons but not adopted | Specific algorithms, patterns, test fixtures, UX ideas | Direct integration or redistribution |

A repository may fill several roles. A model and its weights, datasets and viewers, forks and upstream projects, or mutually dependent companion repositories must not be miscounted as independent game engines. Do not reject a valuable imaging viewer for lacking patient dialogue, or count a monitor simulator as a complete encounter engine.

**Complexity measure:** Limit the number and difficulty of *new, fragile integration boundaries* rather than imposing a universal ceiling of three modules. Record a reason whenever another dependency adds long-term risk.

## 3. Evidence, decisions, and provenance

### 3.1 Evidence grades

- **A — Directly reproduced or inspected:** Pinned source path/commit; exact license; executed behavior, result or artifact; command and environment recorded. State exactly what was inspected or reproduced.
- **B — Upstream primary claim:** Maintainer documentation, release notes, source README, official API reference; version/date recorded.
- **C — Secondary evidence:** Prior audits, independent publication, third-party evaluation; source/date recorded.
- **D — Inference, unsupported claim, or unresolved:** Clearly label the assumption and its consequence.

Direct source inspection is **not** proof of successful installation; a passing test is **not** clinical validation; a declared code license is **not** clearance for all bundled medical images or data. Track freshness separately from evidence grade.

### 3.2 Status dimensions

Keep distinct statuses for: scope fit; reuse mechanism; rights/resources; privacy and data use; technical readiness; security and supply chain; case authority; clinical credibility; educational usefulness; accessibility; maintainability; and confidence. Do not average a prohibited license or hidden-answer leak into a favorable overall score.

Use the same outcome vocabulary throughout:

- `eligible` — sufficient evidence and no blocking issue for the **next specified evaluation stage**.
- `conditional` — potentially viable, with a stated condition and owner; no silent promotion to adoption.
- `hold-rights`, `hold-privacy`, `hold-security`, `hold-technical`, `hold-clinical` — blocked until specific evidence or mitigation exists.
- `reference-only` — valuable ideas, but direct adoption is not justified or permitted.
- `drop` — irrelevant, dominated, infeasible or fundamentally incompatible.
- `not-tested` — no behavioral result; never treat as pass.

Eligibility for local testing **does not equal** legal clearance for redistribution or a public release. Admission to each stage has a separate evidence threshold.

## 4. Bounded funnel and stage outputs

Counts are **planning budgets, not quotas or hard exclusions**. Reallocate based on roles and the expected information value of additional tests. The evaluator must explain any budget extension. Where feasible, prioritize a few credible alternatives per critical architectural role.

| Stage | Objective | Typical bounded work | Required output / exit decision |
| --- | --- | --- | --- |
| **0** | Define the product and benchmark skeleton | One short requirements brief | Scope, non-negotiables, unknowns, measurable quality floor |
| **1** | Normalize the canonical inventory | Annotate all relevant entries; no duplicate dossiers | Role map, dependencies/forks, dispositions |
| **2** | Desk triage and feasibility screening | Roughly 8–15 high-value role candidates; expand only to preserve an important alternative | Candidate cards, actual reuse seam, first blockers, cheapest falsifying test |
| **3** | Minimum pre-execution checks + role-specific evaluation plan | Roughly 4–8 plausible runnable contenders across roles | Permission/security screen; pinned targets; role-specific test contracts |
| **4** | Isolated capability checks | Usually up to 4 major experiments, plus cheap module checks where decisive | Reproducible module/foundation results and observed setup/integration effort |
| **5** | Compare viable solution portfolios | Typically up to 2 repository-based routes plus a minimal custom control | Same-scope vertical-slice evidence; second-case extensibility probe |
| **6** | Adoption-depth diligence and comparative decision | Preferred portfolio plus credible runner-up where necessary | Clinical, rights, privacy, security, accessibility, operations and effort evidence |
| **7** | Record the architectural decision | One selected route, or no adoption | ADR, portfolio, gaps, owner/action plan, deferred list |

At the end of every stage ask: **“Which available next test could change the leading choice, and what does it cost?”** Stop investigating a candidate when the answer is “none.” Do not fill quotas. Do not conceal incomplete tests merely to move forward.

## 5. Stage 0 — Target product, benchmark skeleton, and decision variables

### 5.1 Requirements card

Before evaluating implementation approaches, define:

- **Audience and prerequisites:** learner type, expected medical knowledge, educational aim and intended depth.
- **First-playable actions:** indispensable versus optional history, examination, orders, result review, differential, diagnosis, debrief, and treatment.
- **Learning objective:** a behavior that can be observed during a playthrough rather than a generic promise that “the game teaches diagnosis.”
- **Platform and deployment:** browser, desktop, local-only, hosted, offline, authentication, expected device capability; keep undecided constraints as alternatives.
- **Game experience:** freedom of inquiry, feedback style, responsiveness, clarity of uncertainties, and what makes investigation engaging.
- **Available skills and operating burden:** tooling, languages, maintainers, expected hosting/AI cost, AI-assisted development where relevant.
- **Release modes:** private evaluation, classroom/internal demonstration, public source distribution, hosted public access, commercial use if considered, redistribution of assets and models. Treat unknown modes as unresolved rather than automatically prohibited or allowed.
- **Non-goals and scope exclusions:** modalities, advanced physiology, multiplayer, content scale and production features not needed for the first slice.

Make the first-slice scope **candidate-independent**. Do not pick the clinical case merely because one repository ships a compelling demo.

### 5.2 Define a quality floor, not a feature maximalist wishlist

A first playable must be able to: (a) keep case facts coherent; (b) disclose findings only when appropriate; (c) support meaningful investigative choices; (d) present a clinically interpretable result when called for; (e) accept a diagnosis; and (f) produce an evidence-and-action-based debrief. It must be runnable with synthetic/cleared content and use an accessible primary interaction path.

Minimum integrity and security rules are mandatory from the first runnable experiment. Features such as comprehensive longitudinal EHR, production-grade collaborative play, every error/retry mechanic, and every imaging or electrophysiological modality are **future-facing** unless deliberately included in the chosen slice.

### 5.3 Prepare the benchmark in two versions

**Benchmark skeleton (now):** A fictional presentation, key subjective and objective facts, key actions, one primary investigation modality, possible outcomes, hidden answer, expected debrief points, and a short action sequence. This should fit on a compact case card.

**Fully specified benchmark (before Stage 5):** Expand the same case with complete timeline, authorized disclosures, selected orders and acquisition/report/release time, units, references, uncertainty, intentional noise or limitations, artifact files or generators, known error/unavailable cases, explicit answer-key boundary, clinically referenced interpretations, and scripted tests. Do not use real patient records or candidate-bundled records without rights and privacy clearance.

Create a **small modality-neutral extensibility probe**: can this architecture later add a second investigation category without rewriting the trusted case core? Do not require the new modality to be fully implemented during selection.

### 5.4 Intended-purpose and accessibility screen

This is a Denmark/EU-based educational project. Record the claimed intended purpose and whether outputs inform any real person's healthcare. Review [Regulation (EU) 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/oj), [MDCG 2019-11 rev. 1 (June 2025)](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en), and [MDCG 2025-4](https://health.ec.europa.eu/latest-updates/mdcg-2025-4-guidance-safe-making-available-medical-device-software-mdsw-apps-online-platforms-june-2025-06-16_en) when relevant. This is a screening exercise, **not** a declaration that the game is or is not a medical device. Escalate to qualified regulatory advice if actual-patient use or medical decision claims enter scope.

For a public web game, use [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/) as the default accessibility target unless an explicit alternative is justified. Include keyboard operation, focus indication, semantic labeling, legible units, non-color-only cues, alternatives to interpreting small or fast waveforms, and controllable motion. Stopping a display must not alter authoritative simulation time unexpectedly.

**Stage 0 exit:** A requirements card with measurable first-slice requirements, scope exclusions, quality floor, release modes, intended-use risks, effort accounting, benchmark skeleton, and marked unknowns.

## 6. Stage 1 — Normalize the canonical inventory

Keep canonical IDs, verified upstream links, corrections, source dates and relationships from v1.1. Avoid recreating the 112 detailed entries. Assign a **primary role** and optional secondary roles:

- Game/encounter foundation and case-authoring environment.
- Authoritative patient/case state or clinical event engine.
- Patient dialogue and conversational interface.
- EHR, ordering, result-release, clinician workflow and debrief.
- ECG, monitor and physiology/waveform generation.
- Echo/ultrasound and interactive measurements.
- DICOM/radiology, other imaging, pathology viewers.
- EEG/EMG and other biosignals.
- Physiology, intervention and treatment-response models.
- Case/data generation, synthetic records, simulation assets and model weights.
- Reference-only algorithms, UI patterns or test fixtures.

Track forks, mirrors, inactive archives, upstream versions, companion repos, embedded libraries and data/model pairs. One large repository may contain multiple distinct reusable capabilities; represent those as child capability records rather than counting the whole repository as an indivisible solution.

**Inventory row (minimum):** `canonical_id`, name/URL, canonical upstream, role(s), capability, first-slice relevance, fork/dependency links, surface for reuse, rights flag, privacy flag, evidence grade/date, disposition, one-sentence reason, and deeper record link if shortlisted.

**Stage 1 exit:** Searchable role/disposition matrix and a shortlist pool with no untracked duplicate projects.

## 7. Stage 2 — Fast triage and integration-feasibility screen

### 7.1 Desk triage questions

For each plausible role candidate, answer **before deep review**:

1. Which precise first-slice function would it replace or provide?
2. Is it a library/API, embeddable view, service, standalone desktop program, complete game, dataset, model, or code example?
3. What is the exact integration seam? Link to API, source file, extension point, export format, IPC bridge, or documented fork requirement.
4. Can the game retain authoritative clinical truth? If native state differs, can a bounded adapter map it without contradictions or leaks?
5. Is its runtime/UI plausibly usable in one of the currently acceptable target platforms?
6. Which user-facing features are genuinely present? Which are unverified claims or require substantial rewriting?
7. What setup, adaptation, content, clinical verification, deployment and future upgrade work remains?
8. What is the smallest implementation or inspection test that could disprove its fit?
9. Is there a clearly simpler same-role library or small custom solution?
10. Are there obvious license, provenance, patient-data, telemetry, secret, or security blockers?

### 7.2 Reuse classification

Assign one of:

- `direct-use`: import/embed/serve its capability with minimal configuration.
- `adapter-use`: keep upstream largely intact behind a small, defined interface.
- `fork-and-modify`: significant source modifications expected; quantify and explain.
- `extract`: a useful subcomponent or algorithm can be isolated; rights and coupling must permit it.
- `reference-only`: reuse ideas, tests, or design patterns; no adoption assumed.
- `no-fit`: does not provide enough value for the intended slice.

Avoid an unsupported assertion of “easy integration”: state the real call boundary and required data transformations. Prefer small, demonstrated seams to theoretical compatibility.

### 7.3 Role-based shortlist budget

Aim for approximately **8–15 promising capability/foundation candidates**, not an artificial uniform quota. Maintain credible alternatives for the central engine and the one required first-slice investigation. Other categories can receive a light screen or be deferred. A promising combination may have more than three repositories if each boundary is simple and the total integration burden is acceptable.

Use a `0/1/2` preliminary relevance flag *only* to prioritize experiments (`0` not relevant; `1` potentially useful; `2` directly satisfies a required capability). Pair with evidence grade and estimated integration difficulty. **Do not rank by stars, commit counts, downloads, styling or test counts alone.**

**Stage 2 exit:** Shortlist cards showing concrete reuse value, integration route, uncertainty, initial blockers, cheapest decisive experiment and obvious alternatives.

## 8. Stage 3 — Minimum gates before execution and role-specific test contracts

### 8.1 Tiered diligence model

Diligence occurs in three escalating tiers:

| Tier | Applied when | Minimum checks | Cannot establish |
| --- | --- | --- | --- |
| **T0 — Pre-execution screen** | Before any untrusted clone/install/build/run | Upstream identity, pinned ref, obvious license/data restrictions, scripts, external calls, default secrets, privileges, network and user-data requirements | Adoption clearance or clinical correctness |
| **T1 — Runnable capability check** | When candidate could change a decision | Targeted permission review, isolated environment, reproducible build/test, scoped security and role-specific verification, basic provenance of test assets | Public distribution rights for all bundled resources or effectiveness of learning |
| **T2 — Adoption-depth review** | Before selecting a component for intended release/use | Resource-level license and privacy provenance, dependency inventory/SBOM, security review, clinical/educational/accessibility evidence proportional to impact, maintenance plan | Permanent compliance if use/release changes |

**Never** postpone T0 screening in order to save time. **Never** demand a full T2 review of an eliminated candidate. No unresolved resource is included in a release/adoption portfolio.

### 8.2 Licenses and resources

Inspect separately: code; snippets; cases; clinical text; waveforms; scan/DICOM assets; images/video/audio/fonts; training datasets and data-use agreements; model code and weights; dependencies, containers and binaries; and any generated outputs for which terms apply. Record holder, exact grant and obligations, path/version, license compatibility, attribution requirements, modifications, hosting and redistribution permissions.

Public source visibility without an appropriate license does **not** grant general reuse or redistribution. GitHub's detected license does not clear embedded scans, assets, weights or dependencies. Distinguish permissible **inspection** from permission to execute, modify, distribute or host. If the rights path is unclear, classify `hold-rights` or `reference-only`, seek permission where practical, and do not silently incorporate the resource.

### 8.3 Privacy and data-use authority

Use synthetic case and test content. For any real clinical data candidate, establish source/controller, lawful authority, agreements, identifiers including DICOM metadata, processing/transformation, access and retention rules, onward-sharing restrictions and evidence supporting anonymization. Pseudonymization does not automatically put the data outside GDPR. The EDPB's [Guidelines 02/2026 on Anonymisation](https://www.edpb.europa.eu/documents/guideline/guidelines-022026-on-anonymisation_en) page currently supplies **v1 and records the public consultation as closed**; do not label it a final post-consultation revision without rechecking.

### 8.4 Pre-execution security

Review installation scripts and build hooks, dependencies, containers, services, exposed ports, network calls, upload behavior, analytics/telemetry, secret storage, default credentials and required privileges. Pin versions and record hashes if relevant. Use disposable environments with no credentials or patient data; block outbound access by default, permitting only documented endpoints under explicit exceptions. Do not run arbitrary install scripts in a personal machine's privileged session.

### 8.5 Define **role-specific** test contracts

Each candidate is judged against promised capability plus the stated integration boundary—not an entire game loop:

| Role | Essential capability checks |
| --- | --- |
| **Game/case foundation** | Case authoring, authorized disclosure, case authority, learner actions, reset/replay or equivalent audit, result timing, debrief extensibility, player experience |
| **Dialogue/AI** | Truth-bound answers, consistent history, disclosure limits, hallucination/injection checks, approved tool calls, latency and cost, separation of patient and adjudicator roles |
| **EHR/orders** | Order lifecycle, identifiers, status/time/units, duplicate/repeat behavior, canceled or delayed results, case authority mapping |
| **ECG/monitor** | Signal semantics and sampling, units/calibration, lead labeling, relevant rhythm plausibility, perfusion distinction, noise/artifacts, inspection accessibility |
| **Echo/ultrasound** | View and orientation, measurement calibration where applicable, Doppler/caliper behavior, playback versus clinical time, patient/case alignment |
| **Imaging/DICOM** | Series/study loading and navigation, pixel representation, window/level, metadata/privacy, measurement interaction, reliable study reference mapping |
| **Physiology/treatment model** | Supported domain, time-step/units, numerical behavior, reproducibility, reference comparisons, coupling with authoritative case state |
| **Datasets/models/assets** | Origin, version, rights, privacy, limitations, quality, transformations, licensing of derivatives, contamination, suitable intended use |

**Stage 3 exit:** A small set of pinned, screen-eligible candidates with exact capability tests, environments, data and allowed network exceptions. Candidates with unresolved rights or safety requirements remain on hold instead of being called eligible.

## 9. Stage 4 — Isolated runnable capability checks

### 9.1 Experiment procedure

For each screen-eligible candidate:

1. Record repo URL, upstream identity, pinned commit/release, access date, environment/toolchain and test fixture.
2. Verify the inspected source and resources correspond to the build to be run.
3. Inspect setup and dependency scripts before execution; document any necessary outbound connectivity.
4. Build and launch in an isolated checkout or container/VM suited to the project; keep credentials absent.
5. Run relevant native tests. Record commands, exit codes, skipped tests, warnings and configuration.
6. Exercise the defined **role-specific** function with synthetic or cleared inputs. Record numerical/visual output and evidence.
7. Check the real integration seam: a function call, API request, exported result, test adapter or minimal embeddable view. Avoid relying only on screenshots of a standalone demo.
8. Measure active human/agent engineering effort for setup, debugging and adapter development separately.
9. Capture logs, small non-sensitive output artifacts, traces, hashes and reproducibility instructions.
10. Mark each claim `pass`, `partial`, `fail`, `not tested`, or `not applicable`, with limitations.

A suggested budget is **about two active engineering hours** for a first pass per substantial candidate, with **one further two-hour investigation** only if the problem is understood and the result could change the decision. This is a *resource allocation heuristic*, not a technical quality criterion. Cheap inspections or pre-existing, reproducible tests need not consume the full budget; more time can be justified for disproportionately valuable options.

Classify failures as upstream defect, docs/setup gap, local environment mismatch, missing external service, rights/data barrier, evaluator error, and out-of-scope behavior. A successful locally patched build is a **modified result**, not an upstream pass. Preserve both upstream baseline and patch delta.

### 9.2 Targeted adversarial checks

Apply relevant tests, not the same full set to every category:

- **Authority boundaries:** unauthorized mutations, stale versions, duplicate actions, delayed/out-of-order updates, answer-key leakage.
- **LLM components:** direct/indirect prompt injection from dialogue, documents, retrieved notes, tool outputs, and media metadata; attempts to invent results or exceed tool authority.
- **Results/workflow:** unreleased, missing, delayed, repeated or canceled orders; mismatched units and unknown artifact IDs.
- **Medical display:** correct labels/scales/time base, reference interpretations, clinically meaningful measurement and readable/keyboard-accessible interactions.
- **Persistence:** restart/replay/save-resume if the chosen first-slice scope requires it, or explicit description of missing capability.
- **Integration:** schema mismatch, network exposure, upload handling, unexpected dependence on untrusted external services.

An inconclusive clinical check is not a clinical pass. A smooth UI demo is not proof of correct physiology.

**Stage 4 exit:** Comparable *role-specific* evidence, observed integration friction and a justified list of candidates to assemble into portfolio hypotheses. Do not compare a DICOM viewer and a full game with one aggregate “pass count.”

## 10. Stage 5 — Construct and compare complete solution routes

### 10.1 Design portfolio hypotheses

Construct at most a few distinct routes, normally:

- **Route A: Existing complete foundation.** Adopt/adapt a game/encounter solution if it provides strong native workflows and preserves clinical truth.
- **Route B: Case engine plus modules.** Reuse a strong case/session engine, with necessary interaction, investigation and rendering modules.
- **Route C: Minimal custom case core plus reused modules.** Implement only the authoritative orchestration needed by the benchmark; attach high-value reuse components.
- **Route D: Minimal mostly custom control.** Implement the same thin first-slice behavior without a large adopted foundation, still allowing separately validated simple libraries when appropriate.

Routes C and D may coincide if no suitable high-value components exist; document that rather than build redundant controls. Limit to **two promising repository-based routes and one small custom control** for a typical comparison. Do not build the complete game in this stage. A route can use five small compatible modules and still be preferable to one tightly coupled monolith; compare *integration boundaries* and total effort.

### 10.2 Boundary and integration map

For each route produce a compact dependency/authority diagram and an interface table containing:

- Clinical authority and who owns the case/session state.
- Actor/action flow, what actions may alter state, and how authorization is enforced.
- Source of each result/artifact and release/visibility rule.
- Where generated language is permitted and what facts/tools it may access.
- Interface types (function, API, event, file, iframe/view integration), versions and adapters.
- Clock mapping, units, resource identity, replay/idempotency behavior where needed.
- Main deployment process, secrets, external dependencies, latency/cost and maintenance owner.

**Behavioral contract required:** correct state authority, ordered timing, legal disclosure, referentially valid findings, auditable choices, no fabricated objective results, and clinically coherent results. **Implementation format flexible:** internal identifiers, messaging patterns, databases, schemas, event sourcing, queues, and module language. Translate with adapters whenever the trusted behavior is maintained without invasive changes.

A recommended *adapter-level vocabulary*, not a mandatory upstream interface, includes: opaque case/session ID, version, actor, requested action, optional event ID and idempotency key, authoritative simulation timestamp, structured observation with units and provenance, visibility/release time, artifact reference, validation errors, and public versus trusted data classification.

### 10.3 Complete benchmark and first playable comparison

Before running route-level comparisons, finalize the same synthetic benchmark case independently from the candidate implementations. It must define the player-visible scenario; scripted questions and allowed answers; examination actions; one primary investigative modality and artifact; expected timing/availability; clinically defensible expected results; differential/final answer evaluation; debrief; and selected negative paths.

The same case, same action sequence, same permitted scope and **same acceptance tests** apply to every complete route. If a route cannot implement the case, record the incompatibility instead of silently replacing the benchmark with its built-in showcase.

**Mandatory first-slice acceptance criteria:**

1. A player can follow a coherent presentation-to-diagnosis loop, including the required interaction and investigations.
2. The trusted case authority determines all canonical facts and observation releases.
3. Patient dialogue cannot access/disclose hidden answers or invent canonical objective results.
4. Findings and artifacts have clinically interpretable values, units, timing and provenance; required cross-modal findings are coherent.
5. Required player actions are recorded sufficiently to reconstruct the debrief and explain what evidence was available at each decision.
6. The player can inspect the required artifact with usable controls and an accessible alternative to inaccessible visual-only interpretation.
7. The final diagnosis and debrief work against the case answer key and actual learner action/evidence history, with uncertainty where relevant.
8. The slice runs from a pinned, documented environment using synthetic or cleared resources and without obvious critical access-control/secret exposures.
9. Mandatory first-slice features are demonstrated, not merely promised in an upstream README.

**Conditional criteria:** Treatment, full longitudinal records, advanced save/resume, multiuser access, concurrency, additional modalities, extensive authoring UI, and production operations are mandatory **only when Stage 0 selected them**. Otherwise list them as gaps and estimate future implementation cost; do not fail a minimalist first playable for missing optional features.

### 10.4 Second-case and second-modality extensibility probes

Perform a limited probe on each plausible route:

- **Second-case probe:** Introduce a small but meaningfully different synthetic case (different diagnosis, findings or ordering pattern). Determine what is configurable, what must be coded, what must be clinically authored, and which components need changes. If constructing an entire second case is too expensive, document a source-level trace and implement one meaningful variation with actual evidence.
- **Second-modality probe:** Trace how a new investigation category would be added: case definitions, order, artifact reference, view, timing, permissions and debrief. Implement only a thin skeleton or adapter test unless it would change the decision.
- Record whether adding cases means writing declarative content, editing GUI forms, modifying backend code, duplicating applications or forking third-party components.

These probes are **selection evidence** and estimates, not a requirement to build two polished cases or two full investigation suites.

### 10.5 Player experience / learning review

Have an evaluator attempt an unguided short playthrough and record: clarity of the patient presentation, relevance of available questions, interaction latency, meaningful investigative freedom, discoverability of results, artifact readability, uncertainty handling, differential submission, debrief specificity, and accessibility barriers. Do not claim educational effectiveness from a short playthrough; it is a usability and educational *plausibility* check.

**Stage 5 exit:** Side-by-side end-to-end demonstrations or documented failures, integration diagrams, first-case work estimates, second-case/modality extensibility evidence, and early UX findings.

## 11. Stage 6 — Adoption-level gates and verification

Only a route that could realistically win should receive exhaustive review. Conduct additional checks on its selected code and resources and, where the decision is close, on the most credible runner-up.

### Gate A — Intended-use rights and provenance

Confirm all adopted code, images, cases, recordings, scans, waveforms, model weights and datasets can be used **in the chosen release mode**, including modification, public source publication, hosting and commercial use if applicable. Verify attribution, notice, share-alike, copyleft, patent and dependency obligations with qualified assistance where necessary. Scope unresolved assets **out** of the release, replace them, obtain permission, or hold adoption.

### Gate B — Privacy and data control

No real patient data in tests or release unless explicitly authorized, assessed and appropriately governed. Verify relevant data provenance and any anonymization claim, including DICOM and archive metadata. Treat privacy, copyright, contractual use restrictions and database rights as separate tracks.

### Gate C — Clinical truth and secure isolation

Review actual enforcement paths for answer-key isolation, authorized actions, source-of-truth consistency, simulation time and result release. Test both API and client paths, not just UI behavior. For AI functions, authorization must be external to the model, tool calls must be allowlisted and validated, and the tool/result pipeline must resist prompt injection and excessive agency. Trusted adjudication and patient dialogue require different privileges.

### Gate D — Cybersecurity and maintainability

Record dependencies and known risks, build reproducibility, defaults/secrets, vulnerability triage, exposure paths, patch cadence, upstream viability, CI and upgrade effort. Use [OpenSSF Scorecard](https://openssf.org/projects/scorecard/) as one signal, **not** as a security verdict. Use [NIST SSDF](https://csrc.nist.gov/Projects/ssdf/publications) as a vocabulary: as checked 20 November 2026, SP 800-218 v1.1 is final and SP 800-218 Rev. 1 / SSDF 1.2 is draft. Maintain a workable regression and update owner plan.

### Gate E — Clinical credibility proportional to reliance

For each *clinically consequential* generator, model, viewer and case artifact record intended context of use, known inputs, units, numerical/reference expectations, uncertainty, validation limitations and reviewer expertise. Check underlying numbers and representations as well as rendered appearance. Risk-informed methodologies such as [FDA computational-model credibility guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/assessing-credibility-computational-modeling-and-simulation-medical-device-submissions) and [ASME V&V 40](https://www.asme.org/codes-standards/find-codes-standards/assessing-credibility-of-computational-modeling-through-verification-and-validation-application-to-medical-devices) may inform appropriate evidence without implying device regulation. A display/viewer is not required to validate an entire differential diagnosis; a physiology generator must be justified for the physiological claims being made. Mark illustrative-only results as such.

### Gate F — Educational design, accessibility and usability

Check alignment with the learning objective, debrief accuracy, learner agency, limitations of feedback, accessible controls and alternative representations. Independent educator/clinical review is valuable before making effectiveness claims. Reference healthcare simulation standards and assessment-validity guidance; do not translate a technically successful benchmark into a demonstrated learning outcome.

### Gate G — Deployment, operating burden and continuation

Verify that the chosen environment is plausible for development and first release: supported runtimes, required hardware, network dependencies, AI costs/latency, scale assumptions, failure recovery and reproducible onboarding. Identify who maintains every adopted dependency, adapter, case asset and clinical reference. A route with excellent code but an unsupported, very expensive deployment may lose on total work or operational risk.

For each gate, report `pass`, `pass-with-conditions`, `fail`, `unresolved`, or `not-applicable`, plus the *exact release mode* and evidence. **A blocking unresolved gate is not a pass.** A condition may be accepted for a private selection prototype if clearly scoped, but not silently carried into a public adoption decision.

## 12. Cost, quality, and decision method

### 12.1 Compare the same scope and count all work

Estimate the complete work to reach a comparable first playable:

`E_initial = E_setup + E_adaptation + E_integration + E_missing_features + E_content + E_verification + E_deployment`

Report separately:

- **Measured engineering effort** during selection, distinguishing active effort from elapsed build/download time and automated execution.
- **Remaining engineering effort** as low / likely / high estimates and a confidence grade, with explanation of assumptions.
- **Marginal second-case effort** split into case authoring, software changes and clinical review.
- **Marginal second-modality effort** split into adapter, backend/order model, UI, reference content and verification.
- **Expected ongoing maintenance** (e.g. hours/month or release cadence) and critical third-party dependencies.
- **Operating cost and performance** (hosting, model inference, asset storage, memory/CPU/GPU requirements, latency) under the stated scale assumptions.
- **Risk and rework exposure** (low/medium/high, concrete failure mechanisms, contingency).

Avoid fictional precision. Where the project is too immature for numerical hours, show the evidence needed to narrow the range; do not insert fabricated benchmark measurements. A full-featured foundation with costly adaptations may be dominated by a modest library plus an uncomplicated case engine.

### 12.2 Quality assessment

First enforce non-compensatory gates. Then compare survivors on these distinct quality axes:

1. First-slice clinical and case-state integrity.
2. Accuracy/credibility of the actual chosen investigations.
3. Player usability and investigative freedom.
4. Educational/debrief quality (plausibility, not proven learning effectiveness).
5. Additional-case authoring and modality extensibility.
6. Reliability, security, accessibility and operational sustainability.
7. Evidence confidence and likelihood of significant rework.

If scores aid communication, use anchored `0–5` ratings with definitions for each axis (e.g., `0 = absent/unusable`, `1 = speculative`, `2 = partial demo`, `3 = demonstrated minimum`, `4 = strong reproducible implementation`, `5 = strong externally reviewed evidence`). Do **not** sum scores into an authoritative winner or treat all quality dimensions as interchangeable. Evidence confidence remains an independent dimension.

### 12.3 Decision rules

1. Exclude routes that fail essential rights, privacy, security, trusted-case-state or required clinical quality gates.
2. Eliminate routes strictly dominated by another route with equal-or-better credible quality, lower work and no greater unacceptable risk.
3. For plausible non-dominated routes, compare first-case cost, second-case cost, quality, maintenance, uncertainty and integration risk in plain terms.
4. If quality and effort trade off, identify the lowest-work viable route, the higher-quality route and the reasoned best balance. Name the additional work needed for incremental quality.
5. Prefer simple, reproducible reuse boundaries and low future authoring cost over large superficial feature lists.
6. If evidence is too weak to choose, define the **single cheapest experiment** that would resolve the uncertainty; stop if further testing has low decision value.
7. Recommend `no adoption yet` if none reaches the quality floor or intended-use rights.

Do **not** claim that an aggregate MCDA score or preset weights objectively identify the best project. Optional sensitivity tables can expose tradeoffs, but the [UK Green Book (2026)](https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026) advises against using multi-criteria analysis as the decision method; its supplementary MCDA documents should not be presented as a mandate or definitive ranking authority.

## 13. Records and reusable templates

### 13.1 Candidate capability card (one per serious lead)

```yaml
candidate_id: CANONICAL-ID-or-child-capability
upstream: https://example.invalid/upstream
pin: COMMIT_OR_RELEASE
role: ECG / imaging / foundation / ...
capability_to_reuse: SPECIFIC_FUNCTION
reusable_surface: library | API | plugin | embed | fork | extraction
first_slice_relevance: 0 | 1 | 2
integration_boundary: HOW_INPUTS_AND_OUTPUTS_CROSS
case_truth_owner: WHO
remaining_work: [adapt, integrate, author, validate, deploy]
rights_status: eligible | hold-rights | unknown
privacy_status: synthetic-only | hold-privacy | ...
security_screen: passed-for-test | blocked | not-tested
evidence: [GRADE, SOURCE, DATE, PATH_OR_COMMAND]
cheapest_falsifying_test: PRECISE_ACTION
status: eligible | conditional | reference-only | hold-* | drop
reason: ONE_SENTENCE
```

`example.invalid` is a placeholder only; never treat it as a discovered repository.

### 13.2 Experiment record

Store: candidate/capability ID; pinned version; scope and role-specific claims; machine/OS/toolchain/container; environment configuration; test resources and licenses; exact commands, exit codes, output paths/hashes; allowed network endpoints; failures and classification; measured active effort; patch delta; verdict by claim; reviewer/date; and remaining decision uncertainty.

### 13.3 Portfolio comparison record

For each complete route: inventory of foundation, core, modules and adapters; clinical authority diagram; dependency/runtime diagram; integration contracts; first-slice acceptance matrix; benchmark evidence; second-case and second-modality probe; UX/accessibility review; first/second-case effort ranges; maintenance and operating costs; rights/security/clinical gate statuses; confidence; fallback; and known future-rewrite risks.

### 13.4 Software SBOM and security record

For adopted/tested builds as appropriate, record source version, direct/transitive dependencies, package URLs, hashes where available, license detection and unknowns, dependency relationships, tool/coverage limitations, vulnerabilities and analysis date, toolchain/build image and binary-to-source traceability. SPDX or CycloneDX are acceptable. An automatically generated SBOM is **not** proof of completeness, license compliance or trustworthy provenance.

### 13.5 Clinical/resource provenance manifest

For each case, scan, study, waveform, model, dataset or medical learning asset record: resource ID/path/hash; source/author/version; acquisition/access date; license, permission or agreement; privacy classification and evidence; transformations/derivatives; generator/model version; modality and units; temporal context; what the learner may see and when; expected interpretation; uncertainty and limitations; clinical reviewer/comments/date; and learning objective. Maintain this separately from the software SBOM.

### 13.6 Architectural Decision Record (ADR)

The final ADR must capture: target product and non-goals; compared routes; rejected/deferred candidates; exact selected components and pins; interface/authority diagrams; first-slice and extensibility tests; quality gates; work and maintenance ranges; evidence confidence; unresolved issues and release blockers; rights/security/clinical records; owners; upgrade strategy; fallback if upstream disappears; and triggers for reconsideration. A `no-adoption` conclusion is a valid ADR.

## 14. Stopping, escalation, and release boundaries

Stop or defer a candidate when:

- It cannot materially contribute to the first slice or enable an important low-cost future capability.
- Its permission/data path is unavailable or infeasible for the intended use.
- It demands an irreconcilable second source of clinical truth or leaks unreleased answers.
- The actual reusable seam is nonexistent, brittle, or far more expensive than a simple substitute.
- The critical claimed behavior cannot be reproduced within a justified time budget.
- Its clinical output cannot be justified for the role it would play.
- Security, operations or maintenance risk exceeds available capacity.
- A better option achieves at least the same relevant quality at less credible work and risk.
- Further experiments cannot plausibly change the selection decision.

Reopen a deferred candidate only after a material change in first-slice requirements, upstream version, rights, evidence, target platform, price/effort, clinical requirements or module availability.

**Distinguish decisions explicitly:**

- `viable to inspect`: enough information to research safely.
- `viable to test`: isolated evaluation is legally and operationally acceptable after T0.
- `viable to prototype`: role-specific behavior and integration have enough evidence for a disposable spike.
- `viable to adopt`: use-mode rights, clinical/truth boundaries, security and other specified adoption gates are satisfied.
- `viable to release`: intended distribution, assets, accessibility, privacy, security and relevant regulatory checks have been completed for that release.

None of these automatically implies the next.

## 15. Deliverables and acceptance checklist

1. **Requirements card:** first-slice loop, audience, quality floor, learning objective, environment choices, intended release/use, non-goals and unresolved assumptions.
2. **Compact synthetic benchmark skeleton**, followed later by the fully specified, independent clinical case and expected outputs.
3. **Canonical inventory disposition view**, preserving source IDs and fork/dependency relationships rather than reproducing full dossiers.
4. **Role-based shortlist and capability cards**, including actual integration seams and cheapest falsifying tests.
5. **Pre-execution screening records** for everything run.
6. **Reproducible capability tests** for decision-relevant foundations/modules, with role-specific findings and active effort.
7. **Portfolio architectures**, with clinical authority and adapter/interface diagrams.
8. **Comparable first-playable vertical-slice results**, including test matrix, selected clinical artifacts, security boundaries and debrief.
9. **Second-case and second-modality extensibility evidence**, with estimated marginal effort.
10. **Rights/privacy/security and clinical/resource records**, including relevant SBOM and provenance material for adoption candidates.
11. **Quality-versus-total-effort comparison**, covering initial, future-case, operational and maintenance costs and confidence.
12. **Final ADR** selecting a route or recording justified non-adoption, with rejected/deferred options and reconsideration triggers.

**Completion condition:** The final decision identifies a realistic, evidence-backed route to the best attainable first playable within the available resources—or candidly explains why none has yet been demonstrated. It must not mistake shortlisting, a green CI badge, a demo video, a validated medical asset, or a nice UI for a complete adoption decision.

## 16. Research and standards references

These references inform the evaluation procedure; they do not individually certify any repository or establish legal status of the game. Checked or contextualized on 20 November 2026 where noted. Refresh versions before future execution.

### Project sources

- *Medical diagnostics game canonical repositories and research*, v1.1 (19 November 2026): inventory, source corrections, integration invariants, and candidate leads. [Original Library link](https://chatgpt.com/library?file_id=libfile_167f5635892481919756d56d18fc39d4&account_id=personal).
- *Medical Diagnostics Game — Repository Selection and Verification Plan*, v2.1 (19 November 2026): immediate source for this revision.
- *Original repository selection plan* (19 November 2026): [Original Library link](https://chatgpt.com/library?file_id=libfile_f9e6e66169248191b28f1dbcaf970d8f&account_id=personal).

### Licensing, source integrity, and security

- [GitHub licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) and [GitHub licenses API](https://docs.github.com/en/rest/licenses/licenses).
- [SPDX 3.0.1](https://spdx.github.io/spdx-spec/v3.0.1/) and [REUSE 3.3](https://reuse.software/spec-3.3/): software licensing and file-level notices.
- [CycloneDX](https://cyclonedx.org/) and [GitHub SBOM export](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/export-dependencies-as-sbom).
- [OpenSSF Scorecard](https://openssf.org/projects/scorecard/) and [NIST SSDF publications](https://csrc.nist.gov/Projects/ssdf/publications) (final v1.1, draft v1.2 as of this revision).
- [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) and [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/).

### Clinical, education, EU/EEA, and accessibility

- [FDA assessing credibility of computational modeling and simulation](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/assessing-credibility-computational-modeling-and-simulation-medical-device-submissions) and [ASME V&V 40](https://www.asme.org/codes-standards/find-codes-standards/assessing-credibility-of-computational-modeling-through-verification-and-validation-application-to-medical-devices).
- [INACSL Healthcare Simulation Standards of Best Practice](https://www.inacsl.org/healthcare-simulation-standards-of-best-practice-) and [Cook et al., assessment validity primer](https://pubmed.ncbi.nlm.nih.gov/29450000/).
- [EU MDR 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/oj), [MDCG qualification/classification guidance](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en), and [MDCG 2025-4](https://health.ec.europa.eu/latest-updates/mdcg-2025-4-guidance-safe-making-available-medical-device-software-mdsw-apps-online-platforms-june-2025-06-16_en).
- [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) and [EDPB Guidelines 02/2026 on Anonymisation](https://www.edpb.europa.eu/documents/guideline/guidelines-022026-on-anonymisation_en) (v1; public consultation closed at time of check).
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/).
- [UK Green Book (2026)](https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026) and its [supplementary MCDA guidance](https://www.gov.uk/government/publications/green-book-supplementary-guidance-use-of-multi-criteria-decision-analysis). The 2026 Green Book advises **against MCA as the final decision method**; here any optional multi-axis scoring is explanatory, not dispositive.

## 17. Changes from v2.1

1. **Corrected the evaluation unit:** individual modules get role-specific checks; only complete portfolios get the shared end-to-end clinical case.
2. **Added early integration-feasibility screening**, actual reusable seams, cheapest falsifying experiments and role-based shortlist budgets.
3. **Moved exhaustive diligence to adoption**, while retaining mandatory pre-execution safety/rights/privacy screening and intermediate runnable checks.
4. **Replaced rigid interface requirements with behavioral invariants** that can be met via adapters or a qualified adopted foundation.
5. **Specified trusted answer-key access by role**, distinguishing patient-facing LLM prompts from trusted server-side adjudication.
6. **Split benchmark authoring into a skeleton and complete case**, preventing premature clinical content work.
7. **Added second-case and second-modality extensibility probes**, plus explicit case-authoring ergonomics.
8. **Aligned acceptance tests with the agreed first slice**, avoiding mandatory treatment, full persistence or production operations when out of scope.
9. **Replaced raw module-count limits with integration-complexity accounting** and clarified flexible workload caps.
10. **Made initial engineering, content, second-case, second-modality, ongoing maintenance and operational cost separately visible**, with ranges and confidence.
11. **Added learner experience and usability checks**, without claiming measured educational efficacy.
12. **Clarified standards citations** for EDPB v1/consultation status, NIST SSDF draft/final status and the 2026 Green Book's caution against MCA in final decisions.
13. **Corrected the duplicated funnel table header** and standardized evidence/status/gate terminology.

**Final instruction to the future executor:** Do not start implementing the game before there is an evidence-backed portfolio choice. Do not extend the research indefinitely once the marginal experiment cannot alter that choice. Keep rejected alternatives available for reconsideration and clearly separate what was read, what was run, what was clinically checked and what is still unknown.
