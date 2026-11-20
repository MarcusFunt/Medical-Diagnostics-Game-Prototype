# Evidence, version pins and reproducibility

**Snapshot:** 20 November 2026, Europe/Copenhagen. Pins below are immutable commit identifiers observed at the upstream default branch during this screen. Branch heads can move; the commit link is the reproducible source reference. A pin does not imply a release tag or runtime verification.

## Read-only commands used

The following patterns query public remote refs only. They do not clone, install, build, or execute candidate code. The actual ref names and SHAs are recorded in [the Stage 2 cards](02-stage2-triage.md).

```powershell
$checks = @(
  @{url='https://github.com/clay-good/opensimlab.git'; ref='refs/heads/main'},
  @{url='https://github.com/eth-medical-ai-lab/GTAgentClinic.git'; ref='refs/heads/main'},
  @{url='https://github.com/igembitsky/virtual-standardized-patient.git'; ref='refs/heads/main'},
  @{url='https://github.com/Chelsea-19/Simu_Patient.git'; ref='refs/heads/main'},
  @{url='https://github.com/samhv-dev/patient-monitor-engine.git'; ref='refs/heads/main'},
  @{url='https://github.com/arpitre/12-Lead-Generator.git'; ref='refs/heads/claude/ekg-generator-students-gbjl22'},
  @{url='https://github.com/peterdoubell/Echosim.git'; ref='refs/heads/main'},
  @{url='https://github.com/HealthRex/SimEHR.git'; ref='refs/heads/main'},
  @{url='https://github.com/OHIF/Viewers.git'; ref='refs/heads/master'},
  @{url='https://github.com/neuropsychology/NeuroKit.git'; ref='refs/heads/master'},
  @{url='https://github.com/MIT-LCP/wfdb-python.git'; ref='refs/heads/main'},
  @{url='https://github.com/synthetichealth/synthea.git'; ref='refs/heads/master'}
)
foreach ($check in $checks) { git ls-remote $check.url $check.ref }
git ls-remote --symref https://gitlab.kitware.com/physiology/engine.git HEAD
```

Pinned README/source links in the candidate cards point directly to `blob/<commit>/...` or `tree/<commit>`. The source text was fetched by HTTP GET for inspection only. No candidate source was saved to this workspace or run.

## Source pin register

| Candidate | Observed ref | Pin | Pin link |
|---|---|---|---|
| Open Sim Lab | `main` | `4f3162d33b7f3cc10addf13009e2f258cd3541de` | [commit](https://github.com/clay-good/opensimlab/commit/4f3162d33b7f3cc10addf13009e2f258cd3541de) |
| GTAgentClinic | `main` | `df2560dd3b8f6d1f9a720a5d7547fbe7b4926e8a` | [commit](https://github.com/eth-medical-ai-lab/GTAgentClinic/commit/df2560dd3b8f6d1f9a720a5d7547fbe7b4926e8a) |
| Virtual Standardized Patient | `main` | `b1ed2b9be30d039a4ecf117f230e829bc4fb944e` | [commit](https://github.com/igembitsky/virtual-standardized-patient/commit/b1ed2b9be30d039a4ecf117f230e829bc4fb944e) |
| Simu_Patient | `main` | `e2f0312488b50785f5a57ae4489b231f4e69b495` | [commit](https://github.com/Chelsea-19/Simu_Patient/commit/e2f0312488b50785f5a57ae4489b231f4e69b495) |
| Patient Monitor Engine | `main` | `aa79eb072654b4e0db2a38939a933803729e373d` | [commit](https://github.com/samhv-dev/patient-monitor-engine/commit/aa79eb072654b4e0db2a38939a933803729e373d) |
| 12-Lead Generator | `claude/ekg-generator-students-gbjl22` (upstream default branch at snapshot) | `0db754d5a30e826d7662d1ba76961e088a315a91` | [commit](https://github.com/arpitre/12-Lead-Generator/commit/0db754d5a30e826d7662d1ba76961e088a315a91) |
| EchoSim | `main` | `ffa68354e3f7adb589fd398cdaa223a6f5a9d7f0` | [commit](https://github.com/peterdoubell/Echosim/commit/ffa68354e3f7adb589fd398cdaa223a6f5a9d7f0) |
| SimEHR | `main` | `f6358d8a547620421c291f299cfe5d6d2fb8333b` | [commit](https://github.com/HealthRex/SimEHR/commit/f6358d8a547620421c291f299cfe5d6d2fb8333b) |
| OHIF Viewers | `master` | `eaa45b8db99c824ca6aa5764965dff576581d44c` | [commit](https://github.com/OHIF/Viewers/commit/eaa45b8db99c824ca6aa5764965dff576581d44c) |
| NeuroKit | `master` | `f49ad489fd291d99b22df5dac3ad13951ab9cdef` | [commit](https://github.com/neuropsychology/NeuroKit/commit/f49ad489fd291d99b22df5dac3ad13951ab9cdef) |
| WFDB Python | `main` | `cc9f94fcc8bc938c6fb6cb40fb61c85b33e9404e` | [commit](https://github.com/MIT-LCP/wfdb-python/commit/cc9f94fcc8bc938c6fb6cb40fb61c85b33e9404e) |
| Synthea (supplemental lead) | `master` | `bd8a52ba0a54ad8c6a1004b74787a14d8c25dbcc` | [commit](https://github.com/synthetichealth/synthea/commit/bd8a52ba0a54ad8c6a1004b74787a14d8c25dbcc) |
| Kitware Pulse | `stable` | `5e29e5b13710a08cec90874be7d36ecb192ebcda` | [commit](https://gitlab.kitware.com/physiology/engine/-/commit/5e29e5b13710a08cec90874be7d36ecb192ebcda) |

The 12-Lead Generator's default branch name is unusual and its branch head was last changed before the snapshot date. This is not itself a security finding, but it increases the value of reviewing the branch's authorship and history during T0. Do not silently substitute a different branch or release.

## Fresh ref confirmation at the Stage 2 checkpoint

On 20 November 2026, the read-only commands above were re-run for the 12 listed GitHub refs and for Kitware Pulse's symbolic `HEAD`. Every GitHub ref returned the same full SHA recorded in the pin register; Pulse `HEAD` resolved to `refs/heads/stable` and returned its recorded SHA. No ref drift was observed. This confirms current branch identity only; it does not inspect dependencies, clear rights, or demonstrate behavior.

## Reproducibility boundary

Re-run the metadata-only command below to see today's branch head; if it differs, retain the recorded pin rather than changing it silently:

```powershell
git ls-remote https://github.com/<owner>/<repo>.git refs/heads/<observed-branch>
```

Before any future checkout, first complete the plan's T0 screen: verify upstream identity, pinned file licenses and bundled resources, install/build hooks, dependencies, network behavior, exposed services, default credentials, secrets, required privileges and data uploads. Only after the Stage 2 review should any source be fetched into a disposable, credential-free environment with outbound access blocked by default. The fetch/install/build/test commands are therefore deliberately not recorded as commands to execute now.

## Uncertainty and evidence ledger

- **Freshness:** pinned source names and SHAs are refreshed for the Stage 2 shortlist; the full 112-entry canonical inventory remains the 19 November 2026 audit snapshot.
- **What a pin proves:** a stable identity for a source tree. It does not prove quality, safe installation, license clearance of dependencies/assets, medical accuracy, or integration success.
- **GitHub API:** metadata inspection hit an unauthenticated API rate limit after initial calls. All listed GitHub default-branch SHAs were subsequently confirmed with `git ls-remote`; commit timestamps for every candidate are intentionally omitted.
- **License scope:** root code notices were inspected for the principal browser candidates where available. Data, scenario, media, dependency, model, and derivative-output rights remain separate. Stage 3 must record file-level rights for any candidate actually tested.
- **Security:** no T0 review was performed. `not-tested` remains the status for executable behavior.
- **Clinical:** no case, waveform, image, model, physiological output, or debrief was clinically validated.

## Recommended Stage 3 commands (not run)

For each candidate that survives review, record the exact ref and environment before fetching. Do not use upstream install instructions until their hooks and dependencies have been screened. After T0, a suitable isolated workflow can capture, without executing implicitly:

```powershell
git init <disposable-candidate-dir>
git -C <disposable-candidate-dir> fetch --no-tags https://github.com/<owner>/<repo>.git <full-commit-sha>
git -C <disposable-candidate-dir> checkout --detach FETCH_HEAD
git -C <disposable-candidate-dir> status --short --branch
```

Those are templates only. Container, package-manager and test commands must be selected per candidate after reviewing its pinned scripts and permitted network needs.
