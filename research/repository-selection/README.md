# Medical diagnostics game repository selection

**Checkpoint:** Stages 0–2 complete (requirements, normalized inventory, desk triage and integration-feasibility screen). **Stage 3 and later have not started. No foundation or portfolio has been selected.**

**Snapshot date:** 20 November 2026 (Europe/Copenhagen). This is a selection record, not implementation work.

## Authority and scope

- The user's request authorizes work through Stage 2, asks for provisional assumptions and approval points, requires rights/security precautions, and explicitly stops work after the Stage 2 review.
- [Repository selection plan v2.2](../source-inputs/medical_diagnostics_repository_selection_plan_2026-11-20_v2.2.md) is the process rubric: gates, evidence grades, inventory fields, role-based triage, and Stage 2 exit criteria. It does not authorize skipping the user's stop point.
- [Canonical repository inventory v1.1](../source-inputs/medical_diagnostics_game_canonical_repositories_and_research_2026-11-19_v1.1.md) is the source inventory and prior-research ledger. Its claims are not treated as fresh tests, legal clearance, or instructions to install or execute projects.
- [Source-input manifest](../source-inputs/MANIFEST.md) records snapshot provenance and SHA-256 hashes. The two repository-relative files are byte-for-byte frozen inputs; `.gitattributes` disables line-ending conversion for them so their hashes remain stable on Windows checkouts. Corrections belong in this checkpoint's working research records.

## Files

- [Requirements and provisional assumptions](00-requirements.md)
- [Normalized inventory](01-normalized-inventory.md)
- [Stage 2 shortlist and feasibility cards](02-stage2-triage.md)
- [Evidence, source pins, commands and safety boundary](03-evidence-and-reproducibility.md)
- [Experiment register](04-experiment-register.md)

## What was and was not done

Read-only inspection covered the two supplied Markdown documents, current pinned GitHub/GitLab refs, and selected upstream README, package, tree, and source files for shortlist candidates. Remote-ref commands and HTTP GET requests were used only to identify versions and inspect text. No candidate repository was cloned into the workspace. No third-party install, build, test, application, container, script, model, or dataset was executed or downloaded. No clinical artifact was validated.

The next possible work is Stage 3's T0 pre-execution screen and role-specific test contracts, after the user reviews this checkpoint and approves that stage. No candidate is approved for execution, adoption, or release by appearing in the comparison pool.

## Evidence notation

- **A-source:** local scope label for a pinned upstream path, source text, license file, or reuse seam inspected. It supports only the named source-level claim; it is not a separate v2.2 evidence grade and does not establish behavior or rights for all assets.
- **B, C, D:** retain the v2.2 meanings: upstream primary claim; secondary evidence; and inference/unresolved claim. Record source and date. D-grade effort and integration statements remain hypotheses until measured.
- **eligible:** eligible for the specifically named next-stage screen based on Stage 2 evidence. Here, Stage 3 T0 eligibility is conditional on user review and approval; it does not authorize candidate execution.
- **conditional:** the named future-scope requirement or blocker must be resolved before T0 eligibility.
- **shortlist:** membership in the Stage 2 comparison pool only; it conveys no eligibility, execution approval, adoption decision, or release readiness.
- **not-tested:** no relevant behavior was run. Source inspection and upstream claims do not change that status.

Earlier informal labels are normalized as follows: `viable to inspect only` becomes `eligible` for a named T0 screen or `conditional` when a scope gate remains; `viable to test` is not used as a status. Execution remains not authorized until T0 is complete and any required user approval is recorded.

Each file keeps rights, privacy, integration, clinical validity, and evidence confidence separate. A public URL or MIT/Apache code grant does not clear bundled case text, datasets, recordings, models, dependencies, or generated outputs.

## Stage exit audit

| Stage | Desk exit evidence | Status and limits |
|---|---|---|
| **0 — Requirements and benchmark skeleton** | [Requirements card](00-requirements.md) records audience, learning objective, first-slice actions, platform, release modes, scope exclusions, quality/accessibility floor, effort model, intended-purpose assumption, and one compact fictional ECG case with a provisional hidden answer. | **Complete with assumptions pending approval.** The rhythm skeleton and vitals are illustrative and need clinical review before teaching use. |
| **1 — Inventory normalization** | [Inventory](01-normalized-inventory.md) contains 96 GitHub + 7 GitLab + 6 Hugging Face code/model + 2 dataset + 1 Orthanc Mercurial entries, with roles, relevance, provisional surface, rights/privacy flags, relationships, evidence grade/date and disposition. Supplemental references are separate. | **Desk normalization complete.** Non-shortlisted evidence remains the supplied 19 November audit; reuse surfaces can be inferred or explicitly unknown. |
| **2 — Triage and feasibility** | [Triage cards](02-stage2-triage.md) identify 11 repository capability candidates plus a custom-core comparator, two watchlist leads, and GH-11 as a ruled-out reference. Candidate cards include expected benefit, boundary, effort range, uncertainty, blockers, and a proposed falsifying experiment. | **Desk screen complete.** Open Sim Lab, GTAgentClinic, and GH-04 are eligible for Stage 3 T0 only after this checkpoint is reviewed and approved. Other repository candidates are conditional on their named scope. All behavior remains `not-tested`; no foundation or portfolio is selected. |

**Not established:** T0/T1/T2 clearance, executable behavior, build success, complete dependency or resource licenses, clinical validity, learning outcomes, accessibility behavior, deployment cost, or adoption/release readiness. The user requested review before any later stage, so none has begun.
