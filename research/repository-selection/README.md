# Medical diagnostics game repository selection

**Checkpoint:** Stages 0–2 complete (requirements, normalized inventory, desk triage and integration-feasibility screen). **Stage 3 and later have not started. No foundation or portfolio has been selected.**

**Snapshot date:** 20 November 2026 (Europe/Copenhagen). This is a selection record, not implementation work.

## Authority and scope

- The user's request authorizes work through Stage 2, asks for provisional assumptions and approval points, requires rights/security precautions, and explicitly stops work after the Stage 2 review.
- `medical_diagnostics_repository_selection_plan_2026-11-20_v2.2.md` is the process rubric: gates, evidence grades, inventory fields, role-based triage, and Stage 2 exit criteria. It does not authorize skipping the user's stop point.
- `medical_diagnostics_game_canonical_repositories_and_research_2026-11-19_v1.1.md` is the source inventory and prior-research ledger. Its claims are not treated as fresh tests, legal clearance, or instructions to install or execute projects.
- The source documents are at `C:\Users\marcu\Downloads\medical_diagnostics_game_selection_v2.2_and_canonical_reference\`.

## Files

- [Requirements and provisional assumptions](00-requirements.md)
- [Normalized inventory](01-normalized-inventory.md)
- [Stage 2 shortlist and feasibility cards](02-stage2-triage.md)
- [Evidence, source pins, commands and safety boundary](03-evidence-and-reproducibility.md)
- [Experiment register](04-experiment-register.md)

## What was and was not done

Read-only inspection covered the two supplied Markdown documents, current pinned GitHub/GitLab refs, and selected upstream README, package, tree, and source files for shortlist candidates. Remote-ref commands and HTTP GET requests were used only to identify versions and inspect text. No candidate repository was cloned into the workspace. No third-party install, build, test, application, container, script, model, or dataset was executed or downloaded. No clinical artifact was validated.

The next required work, if approved after review, is Stage 3's T0 pre-execution screen and role-specific test contracts. A repository marked `viable to inspect` or `shortlist` below is not thereby `viable to test`, `viable to adopt`, or `viable to release`.

## Evidence notation

- **A-source:** pinned upstream text/tree/license/source path was directly inspected. This supports source identity and the described seam, not runtime behavior.
- **B:** upstream README or project documentation claim; not reproduced.
- **C:** claim or correction retained from the supplied canonical v1.1 audit (19 November 2026), not refreshed against every current source.
- **D / inference:** integration, effort, privacy, clinical, or product conclusion that needs an experiment, owner confirmation, or qualified review.

Each file keeps rights, privacy, integration, clinical validity, and evidence confidence separate. A public URL or MIT/Apache code grant does not clear bundled case text, datasets, recordings, models, dependencies, or generated outputs.

## Stage exit audit

| Stage | Desk exit evidence | Status and limits |
|---|---|---|
| **0 — Requirements and benchmark skeleton** | [Requirements card](00-requirements.md) records audience, learning objective, first-slice actions, platform, release modes, scope exclusions, quality/accessibility floor, effort model, intended-purpose assumption, and one compact fictional ECG case with a provisional hidden answer. | **Complete with assumptions pending approval.** The rhythm skeleton and vitals are illustrative and need clinical review before teaching use. |
| **1 — Inventory normalization** | [Inventory](01-normalized-inventory.md) contains 96 GitHub + 7 GitLab + 6 Hugging Face code/model + 2 dataset + 1 Orthanc Mercurial entries, with roles, relevance, provisional surface, rights/privacy flags, relationships, evidence grade/date and disposition. Supplemental references are separate. | **Desk normalization complete.** Non-shortlisted evidence remains the supplied 19 November audit; reuse surfaces can be inferred or explicitly unknown. |
| **2 — Triage and feasibility** | [Triage cards](02-stage2-triage.md) identify 11 repository capability candidates plus a custom-core comparator, and two watchlist leads. Each shortlisted role includes expected benefit, boundary, effort range, uncertainty, blockers, and a proposed falsifying experiment. | **Desk screen complete.** All repository candidates are viable to inspect only. None is viable to test before Stage 3 T0; no foundation or portfolio is selected. |

**Not established:** T0/T1/T2 clearance, executable behavior, build success, complete dependency or resource licenses, clinical validity, learning outcomes, accessibility behavior, deployment cost, or adoption/release readiness. The user requested review before any later stage, so none has begun.
