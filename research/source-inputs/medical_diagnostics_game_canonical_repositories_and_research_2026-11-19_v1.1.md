# MEDICAL DIAGNOSTICS GAME — CANONICAL OPEN-SOURCE SIMULATION & REPOSITORY RESEARCH

**Master consolidation • 19 November 2026 • Version 1.1 • Markdown reference**

> **Scope is precise:** the medical diagnostic-reasoning game in which a player interviews/examines a patient, requests investigations, reads actual ECG/echo/medical images and physiological signals, treats the patient, and is evaluated on clinical reasoning. The unrelated Godot 4 / FastAPI / PostgreSQL design and the unrelated historical diplomacy/negotiation game are **not part of this document**. No technology decision or development plan is imported from those other projects.
>
> **Document purpose:** preserve *all technically relevant inventory and investigations recovered so far*, including direct repository links, detailed descriptions, licensing/provenance limitations, architecture/security findings, and next tests. Historical audit facts are preserved with explicit corrections; a public repo or dataset is never presumed reusable just because it can be downloaded.

## How to use this canonical document

- **Part I** — product goals, evidence tiers, discoveries recovered from other chats, and corrected decisions.
- **Part II** — the complete **96-GitHub-entry index** (the original 53 and the additional 43).
- **Part III** — detailed **original 53 repository dossiers**, preserving the longer original source audit, later corrections, and new source-level implementation notes.
- **Part IV** — detailed **43 newly discovered GitHub repository dossiers** with newly merged architecture, features, workflow and source verification detail.
- **Part V** — official **GitLab/Hugging Face/Mercurial** repositories, models, datasets, mirrors, licensing distinctions, external-host evidence, and the 16 detailed non-GitHub dossiers.
- **Part VI** — **further repositories, clinical content sources, and leads recovered from previous project conversations** and earlier source reports; each is classified separately so that the original inventory count remains honest.
- **Part VII** — proposed technical integration contracts, medical/AI safety boundaries, proof-of-concept tests, and the 10-experiment technical acceptance matrix (recommendations, *not previously implemented code*).
- **Part VIII** — full **historical Rohy source, licensing, regression, and security forensics**.
- **Part IX** — consolidated correction ledger, shortlist, practical adoption decisions, due diligence and source links.

### Coverage and count integrity

The previous multi-host audit counted **112 tracked primary-host entries**, not 112 separate reusable games: **96 GitHub entries + 7 GitLab entries + 6 Hugging Face code/model entries + 2 Hugging Face dataset entries + 1 canonical Orthanc Mercurial source repository**. The present document preserves all of those and adds a *separately counted supplementary appendix* of further leads recovered from past project discussions and earlier reports, including clinical datasets and related repositories. It does **not** double-count a GitHub/HF code-and-weights pair, a read-only mirror, or the Epicurrents subrepositories as independent full games.

**Evidence hierarchy**: (A) directly inspected upstream LICENSE/source or exact commit; (B) upstream README/project page; (C) earlier audit or prior project conversation; (D) hypothesis requiring installation, tests, or owner confirmation. A/B may still be stale, and neither proves clinical validity. Exact dates, release numbers, commit counts, test counts and feature catalogs are snapshots or claims, *not continuous live monitoring*.



**Added detailed-source audit labels:** **R** = upstream repository README directly fetched during the later audit; **P** = earlier research or insufficient direct README retrieval; **H** = official host documentation; **I** = integration inference. These are separate from the broader A–D evidence hierarchy above. A README is evidence of a maintainer's description, not proof that a feature works as described. No 112-way runnable benchmark was completed.

**Version 1.1 changelog (19 November 2026):** integrated 96 detailed upstream-source supplements directly into the corresponding canonical dossiers; added 16 structured non-GitHub profiles, source/mirror/weight relationships, expanded 10-experiment acceptance matrix, source-level flags and the deep-read priorities. Existing license corrections, extra projects recovered from prior chats, Rohy history/security forensics and the unrelated-project scope exclusion remain in force. The 112-primary-entry base count has not changed.

**What was not performed in this consolidation:** no installation of all candidates; no execution of their test suites; no original clinical validation; no full transitive software bill of materials; no provenance verification of every image/recording/model; and no claim that private project conversations were exhaustively exported verbatim. Searchable relevant past-project context was consulted, and findings supported by that context were cross-linked to repository URLs where possible.

---

# PART I — GAME GOAL, CORE FINDINGS AND PRIOR RESEARCH

## A. Player experience and requirements established across project conversations

This is a clinical *reasoning and investigation* game rather than a simulator that merely shows a final diagnosis or text report. A credible encounter has at least the following dimensions:

1. **Patient encounter:** ask natural-language questions, examine the patient, account for incomplete/incorrect recollection and disclosure, and distinguish subjective patient reports from objective evidence.
2. **Diagnostic workup:** order appropriate laboratory panels, bedside measurements, 12-lead ECG, continuous ECG monitoring, echo/point-of-care ultrasound, X-ray, CT, MRI, optionally EEG/EMG, pathology and specialist consultations. Some tests have material acquisition delays and different interpretations at different time points.
3. **Actual inspectable results:** interact with waveform strips, calipers, lead selection, cine loops, DICOM slices/volumes, window/level, zoom, annotations, and comparative repeat tests—not only an LLM's paragraph claiming a result.
4. **Dynamically consistent patient state:** a single medical condition and timeline must produce compatible vitals, perfusion, rhythm, labs, images and treatment responses. Avoid one independent model per instrument generating mutually contradictory 'truth'.
5. **Reasoning and treatment:** maintain a differential, use time- and risk-aware investigations and interventions, respond to complications, reach a diagnosis, and receive a debrief that distinguishes process from lucky guessing.
6. **Reusability:** use free/openly licensed code as a base or module where genuinely permitted; inspect interesting unlicensed/restricted applications as inspiration only. A modular combination is attractive, but no foundation has been selected without a controlled integration benchmark.

### Key invariants

- **Authoritative state stays server-side or inside another trusted authority boundary.** Do not transmit concealed diagnoses, solution keys, unreleased laboratory values or hidden NPC knowledge to the learner client.
- **A generated response is not evidence.** AI dialog can express authorized facts, but may not invent laboratory results, pathology, recorded investigations or treatment events that the case engine has not authorized.
- **One clinical clock and event log** for orders, specimen collection, test reporting, therapy administration, and repeat studies.
- **Primary electrocardiographic rhythm is not synonymous with effective perfusion.** ECG, blood pressure, pulse oximetry and echo must agree on when circulation exists.
- **Rights are per resource.** Software code, clinical text, study recordings, scanned images, video, datasets, model weights, anatomy, audio and proprietary dependencies may all have different legal conditions.
- **Medical plausibility and educational fitness must be checked independently** of graphical polish, UI feature counts, source-code license and reported CI tests.

## B. Most consequential discoveries

The baseline shortlist contained Patient Monitor Engine, 12-Lead Generator, Infirmary Integrated, Open Sim Lab, Virtual Standardized Patient, OHIF/Cornerstone3D, Epicurrents and Open Vent Sim. The expanded research newly elevated **GTAgentClinic** (full 3D encounter), **EchoSim** (MIT procedural echo), **SimEHR** (realistic chart and orders), **PatientsWithPersonality** (selective patient disclosure), **NeuroKit2** and **WFDB** (signals), **BioGears / Kitware Pulse** (whole-body physiology), **Orthanc** (DICOM server), and stronger case-asset and model provenance checks.

From separate earlier conversations, missing or underrepresented categories emerged: **Synthea** for synthetic longitudinal records, **MedCaseReasoning** for structured diagnostic case skeletons, **MultiCaRe** for multimodal case/image discovery, **PMC-Patients**, **PMC Open Access**, **MIMIC-IV / MIMIC-IV-ED demo datasets** for realistic chart/timeline fixtures, and **Patient-Simulator / OLab4** as additional virtual-patient references. These are recorded later as supplementary items, not silently added to the original 96 count.

### Recommended immediate shortlist (unvalidated, for technical spikes)

| System goal | Candidate | Why it leads | Main gate |
|---|---|---|---|
| Focused case engine / debrief | [Open Sim Lab](https://github.com/clay-good/opensimlab) | Typed clinical actions, evolving scenarios, replay/debrief | Case truth and module embedding |
| Full 3D encounter alternative | [GTAgentClinic](https://github.com/eth-medical-ai-lab/GTAgentClinic) | Rich ED/OSCE room, staff, orders, EHR | Complexity and unvalidated clinical cases |
| Historic workflow donor | [Rohy before OyonR](https://github.com/mohsaqr/rohySimulator/tree/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd) | Authoring, orders, consultation, examinations | Hidden-answer leakage and mixed rights |
| LLM patient interviews | [Virtual Standardized Patient](https://github.com/igembitsky/virtual-standardized-patient) | Separate case facts and expressive dialogue | Case-content rights and disclosure tests |
| Monitor / physiological traces | [Patient Monitor Engine](https://github.com/samhv-dev/patient-monitor-engine) | Browser multisignal patient monitor | Coherence and model validity |
| Twelve-lead ECG | [12-Lead Generator](https://github.com/arpitre/12-Lead-Generator) | Compact MIT ECG teaching module | Pathology morphology/measurement accuracy |
| Interactive echo | [EchoSim](https://github.com/peterdoubell/Echosim) | 3D heart, B-mode, Doppler and calipers | External medical accuracy and remote state control |
| DICOM radiology | [OHIF Viewer](https://github.com/OHIF/Viewers) | High-quality imaging workstation | DICOM data acquisition and rights |
| Hospital chart / orders | [SimEHR](https://github.com/HealthRex/SimEHR) | Case state, orders, results and audits | Preview maturity; integration interface |
| EEG / EMG | [Epicurrents](https://github.com/epicurrents) | Multichannel workstation family | Format compatibility; build complexity |
| Advanced physiology | [Kitware Pulse](https://gitlab.kitware.com/physiology/engine) | State/action/time physiological engine | Native bridge, scope and validation |
| Clinical fixture data | [Synthea](https://github.com/synthetichealth/synthea) | Synthetic encounter/lab/medication exports | Offline generator, not real-time disease engine |

### Deep-source technical synthesis (19 November 2026)

The highest-yield code and concepts are not simply the longest projects. For a genuinely playable diagnostic investigation, the useful divisions are: **(1) one authoritative patient/case timeline, (2) a controllable clinical dialogue and examination API, (3) an order/result EHR, (4) independent instrument workstations, and (5) replayable evaluation**. GTAgentClinic already demonstrates a large slice of that combination. SimuPatient shows a particularly clean boundary between case truth and generative text; AetioMed shows an outline-first authoring strategy and blinded test planning; SimEHR shows one canonical chart viewed through multiple clinical screens. EchoSim provides a genuine permissively licensed interactive echo research system, not merely a cine viewer.

The external physiology options are significant but must be used selectively. Kitware's own [Pulse validation summary](https://pulse.kitware.com/_about_pulse.html) includes both strong and weak comparisons across subsystems (particularly renal-related outputs); model complexity is not equivalent to universal clinical correctness. Patient Monitor Engine remains more suitable than a native physiology platform for an early responsive browser monitor. Dynamic signal generation, true patient-specific scan realism, and independent clinical evaluation remain distinct problems.

## C. Critical corrections before any reuse decision

1. **Medkit** is not simply 'no license found': its README states private hackathon code without a redistribution grant. Treat implementation copying as prohibited absent permission.
2. **paultman/patientSimulator** was labeled license-unverified in the 96 entry catalog, but its upstream GitHub repository visibly includes a root **MIT LICENSE** and an explicit MIT statement. The historical catalog entry must be corrected; third-party clinical-content rights are still separate.
3. **biosimkit**: MIT was stated in a README in the detailed 53-repo audit, while the later abbreviated 96-row table inaccurately collapsed it to 'no license'. Keep **MIT claimed; exact full grant still needs review**.
4. **ION_Simula**: a related publication claims GPL, whereas a definitive root grant/version was not retrieved. Keep **GPL claimed / exact version unverified**, not categorical 'no license'.
5. **Rohy**: current Carm Research v1.4 limits integration and derivative use. Historic root MIT on 8 May 2026 is a useful candidate only for first-party covered material; it is **not** an all-MIT, all-assets-cleared repo.
6. **Open Sim Lab**: 256 refers to **scenarios/lessons across specialties**, not 256 kinds of laboratory test. Its debrief reportedly does not assign a single overall score; preserve that distinction.
7. **GTAgentClinic**: original cases are CC BY 4.0, not CC BY-NC; README documentation described **0.3.0, 111 cases, and WebGL2 fallback**, contradicting an earlier report saying 0.4, WebGPU-only or 7,500 commits. These are snapshot claims requiring future refresh, not universal facts.
8. **DWV** is GPL-3.0, not MIT. **SonoForge** is GPL-3.0. License obligations cannot be decided merely by saying a project is in a separate process, but neither does an API link automatically relicense all unrelated client code.
9. **PyMUST**: GitHub `LICENSE` cites LGPL-2.1 whereas package metadata cites LGPL-3.0. Author intent and distribution need clarification.
10. **Kitware Pulse** is a **historical fork** of BioGears 6.1.1, not an official GitHub mirror or identical engine. The canonical maintained engine source is on GitLab.
11. **Orthanc** is primarily a DICOM server, not a viewer. Its canonical source is Mercurial and maintainer GitHub copies are mirrors. It should not be a prerequisite just to display packaged scans.
12. **OLab4** does exist, but its README explicitly says this historical repository is archived and should not be used. Older OpenLabyrinth is still relevant for authoring patterns, not as an unexamined production base.
13. **MultiCaRe** has incompatible public licensing labels across GitHub, Hugging Face and Zenodo/underlying materials. Only article-/asset-level provenance can establish permission. **PMC-Patients** declares CC BY-NC-SA for its assembled dataset. Do not call all freely downloadable clinical datasets unrestricted open content.
14. **'All data synthetic' is false** across the ecosystem: many packages incorporate published clinical examples, MIMIC-derived material, scans, research videos and other source-specific rights.
15. **Counts/CI and graphical fidelity do not prove medical validity.** GTAgentClinic's cases, Open Sim Lab scenarios and EchoSim educational measurements all need independent review.

## D. Evidence updates checked during this consolidation

The following upstream pages were rechecked for a small set of high-impact decisions, in addition to the two user-provided files:

- [paultman/patientSimulator](https://github.com/paultman/patientSimulator): root `LICENSE` (MIT), limited voice/text patient-interview POC, and a transcript evaluation endpoint. Earlier 'license unverified' label is superseded.
- [Synthea](https://github.com/synthetichealth/synthea): Apache-2.0, Java synthetic population/EHR generator; not a drop-in bedside physiology service.
- [shivanand-vn/Patient-Simulator](https://github.com/shivanand-vn/Patient-Simulator): a real additional virtual-patient codebase, but the current exact permission grant is not established here.
- [OLab4](https://github.com/olab/OLab4): archived GPL-3.0 project; do not use its README demo Docker instructions for internet-facing deployment (hardcoded credentials and explicit author warning).
- [MedCaseReasoning](https://github.com/kevinwu23/Stanford-MedCaseReasoning) and [dataset](https://huggingface.co/datasets/zou-lab/MedCaseReasoning): repository describes 14,489 cases and distinct code/dataset rights; seek each original article's provenance.
- [MultiCaRe](https://github.com/mauro-nievoff/MultiCaRe_Dataset), [HF dataset](https://huggingface.co/datasets/mauro-nievoff/MultiCaRe_Dataset), and [Zenodo record](https://zenodo.org/records/10079370): distribution-layer license labels differ, and upstream article rights govern content reuse.
- [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/): individual license requirements, not a global blanket relicense.
- [MIMIC-IV demo](https://physionet.org/content/mimic-iv-demo/2.2/) and [ED demo](https://physionet.org/content/mimic-iv-ed-demo/2.2/): openly accessible 100-patient examples, distinct from credentialed restricted full MIMIC releases.
- [PMC-Patients](https://github.com/zhao-zy15/PMC-Patients): 167k extracted patient summaries and CC BY-NC-SA assembled-dataset terms.

---

# PART II — FULL 96-REPOSITORY GITHUB INDEX

The original index numbers are stable. A source title is linked to its canonical GitHub location. The license/decision statements below are **screening findings**; detailed sections and corrections take precedence when different sources disagree. Where multiple subrepositories implement one stack (e.g. Epicurrents), the numeric rows are components, not independent products.

| # | Repository | License / permission assessment | Priority in earlier audit | Function and caveat |
|---:|---|---|---|---|
| 1 | [samhv-dev/patient-monitor-engine](https://github.com/samhv-dev/patient-monitor-engine) | MIT | Core | Physiology-coupled multi-channel patient monitor; strong first integration candidate |
| 2 | [tanjera/infirmary-integrated](https://github.com/tanjera/infirmary-integrated) | Apache-2.0 | Backup | Mature device/training suite, cardiac monitor, defibrillator, EHR and fetal monitor; C# integration effort |
| 3 | [pafolol/vitalis](https://github.com/pafolol/vitalis) | No license found | Study | Unusually complete 3D patient, interventions and mechanistic physiology; request permission before copying |
| 4 | [arpitre/12-Lead-Generator](https://github.com/arpitre/12-Lead-Generator) | MIT | Core | Comprehensive blind-mode 12-lead ECG generator with interpretations and lead-pathology controls |
| 5 | [LaiCxm/biosimkit](https://github.com/LaiCxm/biosimkit) | MIT claimed in README; full grant needs confirmation | Study | Synchronized ECG/EEG/PPG/ABP/respiration synthesis; useful algorithms but no reuse grant found |
| 6 | [riccardo-budai/ION_Simula](https://github.com/riccardo-budai/ION_Simula) | GPL claimed in publication; exact code license unverified | Defer | Intraoperative neurophysiology niche; narrower than initial diagnostic gameplay |
| 7 | [robchiral/AnaSim](https://github.com/robchiral/AnaSim) | Custom noncommercial | Defer | Anesthesia PK/PD and machine simulator, restricted for commercial integration |
| 8 | [fedebarra/open-vent-sim](https://github.com/fedebarra/open-vent-sim) | MIT | Optional | Ventilator/lung mechanics, gas exchange and dynamic interventions |
| 9 | [Nicholas-Amsler/lung-iq](https://github.com/Nicholas-Amsler/lung-iq) | MIT | Defer | Narrow waveform-focused ventilation tool; overlap with Open Vent Sim |
| 10 | [bowowbox/vent-teach](https://github.com/bowowbox/vent-teach) | No license found | Defer | Ventilation pedagogy; license blocker |
| 11 | [seanwkelley/ecg-simulator](https://github.com/seanwkelley/ecg-simulator) | MIT | Backup | Feature-rich rhythm recognition and 12-lead teaching; overlaps lead generator |
| 12 | [zhenyuanzhou/cardiosim-lab](https://github.com/zhenyuanzhou/cardiosim-lab) | CC BY-NC 4.0 | Study | Interesting causal cardiac electrophysiology, not a commercially reusable game engine |
| 13 | [SeraKah-1/cardiac-3d-ecg-simulator](https://github.com/SeraKah-1/cardiac-3d-ecg-simulator) | MIT | Backup | Interactive 3D electrophysiology and clinical ECG training; evaluate clinical accuracy independently |
| 14 | [infocusp/ecg-atlas](https://github.com/infocusp/ecg-atlas) | MIT code; separate assets | Backup | Electrode-position and ECG visualization; asset/recording licenses differ |
| 15 | [aschanken/EKGSim](https://github.com/aschanken/EKGSim) | No license found | Defer | Paramedic rhythm teaching UI, no reuse permission found |
| 16 | [goga-lanchava/ecg-simulator](https://github.com/goga-lanchava/ecg-simulator) | No license found | Defer | Multi-channel cardiac monitor with artifact and measured numerics; no reuse grant found |
| 17 | [efavirenz/MI-ECG-learning-simulator](https://github.com/efavirenz/MI-ECG-learning-simulator) | No license found | Defer | Very detailed MI/lead-placement teaching; no license found |
| 18 | [douyang/echodemo](https://github.com/douyang/echodemo) | No license found | Study | Most compelling interactive echo probe, views, wall motion and Doppler; must obtain reuse permission |
| 19 | [gowthamaanp/simpsonef](https://github.com/gowthamaanp/simpsonef) | MIT code; CC BY-NC models | Optional | EF analysis of recorded echo; model checkpoints noncommercial and research terms |
| 20 | [hoodlm/affordable-medical-ultrasound-training-simulator](https://github.com/hoodlm/affordable-medical-ultrasound-training-simulator) | MIT | Defer | Old Unity ultrasound training prototype; outdated toolchain and limited pathology |
| 21 | [yunhaoli24/OTC-Flow](https://github.com/yunhaoli24/OTC-Flow) | MIT code; verify models/data | R&D | CT-to-TEE research image synthesis, not plug-and-play dynamic diagnostic echo |
| 22 | [ahastava/moculus](https://github.com/ahastava/moculus) | No license found | Study | Diffusion-driven lung ultrasound training with interactive probe; license and data rights block straightforward reuse |
| 23 | [asclepius/edus2](https://github.com/asclepius/edus2) | GPL-3.0 | Defer | Older emergency ultrasound simulator with GPL copyleft obligations |
| 24 | [jiff3/ar-ultrasound-slice-simulator](https://github.com/jiff3/ar-ultrasound-slice-simulator) | No license found | Defer | Useful virtual-probe geometry prototype; no reuse grant |
| 25 | [osamamalik/TEESimulator](https://github.com/osamamalik/TEESimulator) | No license found | Defer | Older Arduino/C++ TEE positioning prototype rather than a modern echo workstation |
| 26 | [OHIF/Viewers](https://github.com/OHIF/Viewers) | MIT | Core | Browser-based clinical DICOM/PACS workstation, CT/MRI investigation viewing |
| 27 | [cornerstonejs/cornerstone3D](https://github.com/cornerstonejs/cornerstone3D) | MIT | Core dependency | Modular rendering library underpinning OHIF; use with OHIF unless bespoke viewer needed |
| 28 | [Kitware/VolView](https://github.com/Kitware/VolView) | Apache-2.0 | Optional | Strong browser 3D DICOM volume rendering; alternative/add-on to OHIF |
| 29 | [Slicer/Slicer](https://github.com/Slicer/Slicer) | 3D Slicer custom BSD-style terms; read actual License.txt | Defer | Powerful heavy desktop research platform; avoid embedding whole application for a lightweight game |
| 30 | [openseadragon/openseadragon](https://github.com/openseadragon/openseadragon) | BSD-3-Clause | Optional | Zoomable giant images and digital pathology rendering foundation |
| 31 | [pathologysmile/wsi-viewer](https://github.com/pathologysmile/wsi-viewer) | MIT | Optional | Whole-slide pathology and NIfTI viewer; later diagnostic module |
| 32 | [eegdb/eeg-simulator](https://github.com/eegdb/eeg-simulator) | MIT | Optional | Synthetic real-time EEG with anatomy/electrode and artifact controls; runtime or pre-generation |
| 33 | [dbrang/Neuron-to-EEG-Demo](https://github.com/dbrang/Neuron-to-EEG-Demo) | MIT | Defer | Great EEG teaching visualization, less useful as clinical diagnostic workstation |
| 34 | [mne-tools/mne-python](https://github.com/mne-tools/mne-python) | BSD-3-Clause | R&D | Scientific EEG/MEG processing ecosystem, Python backend research option |
| 35 | [epicurrents/core](https://github.com/epicurrents/core) | Apache-2.0 | Core family | Signal infrastructure underlying EEG/EMG workstation |
| 36 | [epicurrents/eeg-module](https://github.com/epicurrents/eeg-module) | Apache-2.0 | Core family | EEG montages, annotations, spectrograms and study interpretation |
| 37 | [epicurrents/emg-module](https://github.com/epicurrents/emg-module) | Apache-2.0 | Optional family | Electromyography traces and audio functionality |
| 38 | [epicurrents/edf-reader](https://github.com/epicurrents/edf-reader) | Apache-2.0 | Core family | EDF/BDF waveform file import/export |
| 39 | [epicurrents/dicom-reader](https://github.com/epicurrents/dicom-reader) | Apache-2.0 | Optional family | DICOM waveform import (not image DICOM viewer) |
| 40 | [epicurrents/interface](https://github.com/epicurrents/interface) | Apache-2.0 | Core family | Visual shell for Epicurrents neurophysiological workstation |
| 41 | [epicurrents/builder](https://github.com/epicurrents/builder) | Apache-2.0 | Core family | Assembles embeddable Epicurrents editions; start here |
| 42 | [mrmehar229/virtual-patient](https://github.com/mrmehar229/virtual-patient) | No license found | Defer | AI case interview and assessment prototype; restricted source reuse |
| 43 | [yusra-kk/clinical-case-practice-ai](https://github.com/yusra-kk/clinical-case-practice-ai) | No license found | Defer | Small clinical interaction prototype, limited cases and no reuse permission |
| 44 | [igembitsky/virtual-standardized-patient](https://github.com/igembitsky/virtual-standardized-patient) | MIT code; CC BY cases | Core | AI simulated patient interview, examinations and clinician-authored grading; good reusable interaction patterns |
| 45 | [clay-good/opensimlab](https://github.com/clay-good/opensimlab) | MIT code; scenarios individually licensed | Core | Large offline collection of dynamic clinical scenarios and debrief workflows |
| 46 | [SamuelSchmidgall/AgentClinic](https://github.com/SamuelSchmidgall/AgentClinic) | MIT | Optional | Patient-doctor-agent benchmark, multimodal cases, evaluation; useful for automated testing |
| 47 | [ZJUMAI/EvoPatient](https://github.com/ZJUMAI/EvoPatient) | Apache-2.0 text in LICENSES | Optional | Research multi-agent standardized patients and consultations; confirm license scope |
| 48 | [DylanTombs/Multi-Agent-Hospital-Sim](https://github.com/DylanTombs/Multi-Agent-Hospital-Sim) | MIT | Defer | Hospital triage and resource scheduling game, less focused on physician diagnostic decisions |
| 49 | [josephmasson26/DiagnoseMe](https://github.com/josephmasson26/DiagnoseMe) | MIT | Defer | Simpler patient chatbot proof of concept, less depth than top choices |
| 50 | [olab/Open-Labyrinth](https://github.com/olab/Open-Labyrinth) | GPL-3.0 asserted; verify repo license | Study | Longstanding virtual-patient branching authoring; old PHP stack and copyleft if reused |
| 51 | [bedriyan/medkit-app](https://github.com/bedriyan/medkit-app) | Explicit no-redistribution grant in README | Study | Voice-first ER and outpatient patient agents, testing and grading; no license found |
| 52 | [MAXNORM8650/MedAgentSim](https://github.com/MAXNORM8650/MedAgentSim) | CC BY-NC-SA 4.0 | Study | Research multi-agent diagnostic interaction and evaluation; noncommercial and share-alike |
| 53 | [mohsaqr/rohySimulator](https://github.com/mohsaqr/rohySimulator) | Current Carm Research v1.4; historic MIT first-party core has exclusions | Study | Extremely broad clinical encounter + ECG/PACS/WSI, but explicit permission required for integration and modifications |
| 54 | [eth-medical-ai-lab/GTAgentClinic](https://github.com/eth-medical-ai-lab/GTAgentClinic) | Apache-2.0 code; CC BY 4.0 cases | Core contender | 3D ED/OSCE game: dialogue, EHR, tests, dynamic time and debrief; compare as a possible complete base. Clinical validation pending. |
| 55 | [peterdoubell/Echosim](https://github.com/peterdoubell/Echosim) | MIT | Core echo candidate | Browser 3D heart, ultrasound-like B-mode, Doppler, EF/calipers, 12-lead ECG and blinded questions; external clinical validation pending. |
| 56 | [BioGearsEngine/core](https://github.com/BioGearsEngine/core) | Apache-2.0 (README/organization) | R&D physiology | Whole-body C++ physiology for coherent responses and interventions; complex build and bridge, validate specific outputs. |
| 57 | [ihkarise/wisecases](https://github.com/ihkarise/wisecases) | MIT | Optional case editor | Offline progressive case clues, authoring/import tools and reasoning feedback; more quiz-like than an unrestricted workup. |
| 58 | [mo374z/PatientsWithPersonality](https://github.com/mo374z/PatientsWithPersonality) | MIT | Core dialogue research | Patient persona and selective disclosure framework; ideal source of ideas for realistic history-taking and difficult interviews. |
| 59 | [Sahandfer/PatientHub](https://github.com/Sahandfer/PatientHub) | MIT | Optional dialogue research | Modular patient/client agents and evaluations; strong architecture reference, mental-health emphasis, not a full game. |
| 60 | [MAGIC-AI4Med/DiagGym](https://github.com/MAGIC-AI4Med/DiagGym) | CC BY-SA notice; nonstandard for software, verify | Research / permission check | Multi-turn diagnostic tool calls and conditional test-result generation; experimental world model, guard against fabricated contradictory results. |
| 61 | [HealthRex/SimEHR](https://github.com/HealthRex/SimEHR) | Apache-2.0 code; CC BY 4.0 synthetic charts | High-priority EHR | Interactive chart review, orders, medications, notes, flowsheets and audit API; excellent EHR candidate, still a preview. |
| 62 | [janthoXO/AetioMed](https://github.com/janthoXO/AetioMed) | No root LICENSE confirmed | Study / permission check | Blueprint-first synthetic cases with hidden diagnosis and blinded workup agent; potentially useful authoring pipeline. |
| 63 | [dek924/PatientSim](https://github.com/dek924/PatientSim) | No root LICENSE confirmed; data rights separate | Study / permission check | Research-grade patient personas and dialogue grounded in clinical datasets; check rights before code/data reuse. |
| 64 | [MadGAA-Lab/OSCE-Project](https://github.com/MadGAA-Lab/OSCE-Project) | MIT-like permission text in LICENSE | Optional evaluation | Adversarial standardized-patient consultations and clinical evaluation; small specialty case set. |
| 65 | [ArneshBanerjee/open-residencyrl](https://github.com/ArneshBanerjee/open-residencyrl) | Apache-2.0 | R&D evaluation | Simulated longitudinal encounters, history interviews and structured rewards; RL harness, not a finished game. |
| 66 | [Chelsea-19/Simu_Patient](https://github.com/Chelsea-19/Simu_Patient) | MIT | Optional case logic | Application-controlled case truth, allowed tests and encounter state; good patterns for safe AI patient boundaries. |
| 67 | [paultman/patientSimulator](https://github.com/paultman/patientSimulator) | MIT — verified in repository LICENSE during 19 November consolidation | Study | Speech/realtime virtual patient proof of concept; useful voice UX reference; API and permissions need checking. |
| 68 | [drewhirschi/virtual-patient](https://github.com/drewhirschi/virtual-patient) | No LICENSE verified | Defer | Gemini-powered patient interview demo with authored case records; overlaps stronger dialogue engines. |
| 69 | [MegaWiz-Dev-Team/vitals](https://github.com/MegaWiz-Dev-Team/vitals) | AGPL-3.0 | Study / defer | Deterministic emergency simulation and audit/replay; unusual Solana/blockchain architecture increases integration cost. |
| 70 | [tipcode-cpu/echocardiography-simulator](https://github.com/tipcode-cpu/echocardiography-simulator) | No root LICENSE confirmed | Study / permission check | Small dependency-free browser tutorials for echocardiography concepts; no evidenced source-reuse grant. |
| 71 | [sawaz/simpocus](https://github.com/sawaz/simpocus) | No root LICENSE confirmed | Defer | Tiny low-fidelity POCUS prototype mapping probe/tags to images; modest utility and license uncertainty. |
| 72 | [tomzzzhang/Cardiology-app](https://github.com/tomzzzhang/Cardiology-app) | AGPL-3.0 | R&D / copyleft review | Heart/echo-focused interactive application; large codebase and AGPL network obligations demand consideration. |
| 73 | [neuropsychology/NeuroKit](https://github.com/neuropsychology/NeuroKit) | MIT | High-priority signal utility | Python synthetic 12-lead ECG, PPG, respiration, EDA, EMG and processing; not a pathology-validated case simulator. |
| 74 | [MIT-LCP/wfdb-python](https://github.com/MIT-LCP/wfdb-python) | MIT | High-priority data utility | Load and process physiological waveform databases; useful for real ECG/ICU recordings and annotations. |
| 75 | [creatis-ULTIM/PyMUST](https://github.com/creatis-ULTIM/PyMUST) | LGPL-2.1 LICENSE; setup.py says LGPL-3 (conflict!) | R&D / license check | Simulated ultrasound RF/IQ, transducers and beamforming; not an interactive echo game; clarify conflicting license notices. |
| 76 | [unioslo/USTB](https://github.com/unioslo/USTB) | MIT | Optional ultrasound research | MATLAB/Python ultrasound beamforming toolbox; offline generation and imaging research rather than ready UI. |
| 77 | [ingle/ultrasound-simulation](https://github.com/ingle/ultrasound-simulation) | Modified MIT per README; verify text | R&D | Older frequency-domain medical B-mode ultrasound generation; check source provenance and modifications. |
| 78 | [CeBiDa/ECG-Format-Converter](https://github.com/CeBiDa/ECG-Format-Converter) | MIT (LICENSE.md) | Optional ECG interoperability | Convert ECG/WFDB/CSV/DICOM-waveform/HL7 XML formats for investigation assets. |
| 79 | [lavrentiy/meridian](https://github.com/lavrentiy/meridian) | MIT | Optional imaging alternative | Small offline browser DICOM MPR/3D viewer; consider for compact imaging screen, check clinical fidelity. |
| 80 | [thulefog/circinus](https://github.com/thulefog/circinus) | MIT claimed in README; root LICENSE not seen | Optional imaging alternative | Web DICOM/NIfTI MPR and 3D volume visualization; independently verify license distribution. |
| 81 | [rii-mango/Papaya](https://github.com/rii-mango/Papaya) | BSD-style project terms; no clinical-use claim | Optional legacy viewer | Browser NIfTI/DICOM viewer; lighter than OHIF, older technical architecture. |
| 82 | [ivmartel/dwv](https://github.com/ivmartel/dwv) | GPL-3.0 (license.txt) | Optional / copyleft review | Embeddable DICOM Web Viewer with imaging tools; GPL obligations for distributed derivatives. |
| 83 | [ImagingDataCommons/slim](https://github.com/ImagingDataCommons/slim) | Apache-2.0 | Optional pathology viewer | DICOM whole-slide digital pathology viewer and annotations; complement OpenSeadragon. |
| 84 | [tanjera/infirmary-integrated-ehr](https://github.com/tanjera/infirmary-integrated-ehr) | License not verified in root | Study / verify | Separate inpatient EHR simulator companion to Infirmary Integrated; check rights separately from parent project. |
| 85 | [google/simhospital](https://github.com/google/simhospital) | Apache-2.0; archived | Defer | Synthetic hospital/EHR message-flow simulator; useful integration research but archived. |
| 86 | [Alp-creator/medphys-lab](https://github.com/Alp-creator/medphys-lab) | MIT | Optional imaging pedagogy | Unity medical physics game with X-ray/CT/MRI/PET lessons; teaching mechanics more than patient-case reading. |
| 87 | [micaalle/CT-VR-App](https://github.com/micaalle/CT-VR-App) | No root LICENSE confirmed | Study | VR medical CT anatomy navigation project; no reliable grant for copying source/assets found. |
| 88 | [AdvancedModularManikin/physiology-manager](https://github.com/AdvancedModularManikin/physiology-manager) | CC BY 4.0 LICENSE.md; unusual for code | R&D / license check | Physiology orchestration around BioGears; heavy native framework and licensing follow-up. |
| 89 | [areatu/SonoForge](https://github.com/areatu/SonoForge) | GPL-3.0 | Optional / copyleft review | Desktop echocardiography measurements, reporting and DICOM analysis; not a procedural echo simulator. |
| 90 | [Heigvd/mimms](https://github.com/Heigvd/mimms) | No root LICENSE confirmed | Study | Major-incident medical simulation/game model; event/time/severity ideas, license requires inspection. |
| 91 | [Heigvd/Wegas](https://github.com/Heigvd/Wegas) | MIT per README; check license file | Optional authoring platform | Generic serious-game authoring platform used in medical incident research; larger Java/web stack. |
| 92 | [anddegilevich/CPRSimulator](https://github.com/anddegilevich/CPRSimulator) | CC0-1.0 per GitHub | Optional training game | Unity CPR/defibrillation training game; focused intervention practice rather than diagnostics. |
| 93 | [02developer/yapper](https://github.com/02developer/yapper) | BSD-style custom terms in LICENSE | Optional communication UX | Interview/communication training game; useful interactions, substantial non-code assets. |
| 94 | [pydicom/pydicom](https://github.com/pydicom/pydicom) | MIT for most code; exceptions in LICENSE | Core DICOM backend utility | Python DICOM reading/writing and metadata, for organizing and delivering real study assets. |
| 95 | [sadc-lab/pulse_reliability_atlas](https://github.com/sadc-lab/pulse_reliability_atlas) | Apache-2.0 | R&D validation | Reproducible sensitivity/failure-mode audit for Pulse Physiology Engine; helps test realism boundaries. |
| 96 | [OHIF/ohif-core](https://github.com/OHIF/ohif-core) | MIT; archived | Legacy dependency / defer | Reusable functions from earlier OHIF architecture; current OHIF/Cornerstone preferred. |

# PART III — FULL DETAILED REVIEWS OF THE ORIGINAL 53 REPOSITORIES

**Source provenance:** the following 53 original technical dossiers are retained from `medical_simulation_github_repositories_expanded_v4.md` so that name, creator, capabilities, quality signals, reuse rationale and original license statements do not disappear in consolidation. Where conflicts exist, **Part I corrections and Part IX correction ledger override the historical field**. The review covers source/README evidence, not independently executed clinical or functional tests.

## III-A. Whole-body physiology, monitors and respiratory devices

### 1. [samhv-dev/patient-monitor-engine](https://github.com/samhv-dev/patient-monitor-engine)
- **Creator/maintainer:** `samhv-dev` and contributors.
- **What it does:** A TypeScript educational monitor combining 3/5/12-lead ECG, ABP/CVP/PAP, NIBP, SpO₂/pleth, EtCO₂, breathing and temperature. Manual and modeled modes, coupled cardiac/lung/organ physiology, drug responses, scenarios, instructor controls and ventilator components.
- **Code quality:** **Promising–strong.** A pnpm monorepo with type checking, unit/E2E tests, model audits, documentation and packaging scripts. Its own README acknowledges some inadequate test targets and that `1.0.0-rc.5` is a prerelease; do not confuse extensive tests with validated physiology.
- **Reuse for the game:** **Very high.** Best single candidate for bedside monitors, synchronized findings and treatment-driven vitals. Prefer isolating the physiology as a service or module and maintaining one authoritative patient state.
- **License:** **MIT — verified** ([LICENSE](https://github.com/samhv-dev/patient-monitor-engine/blob/main/LICENSE)). Retain copyright/license notices. Clinical validity remains unproven.


#### Added detailed-source dossier — 01

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: 3/5/12-lead ECG, invasives (ABP/CVP/PAP/ICP), pleth, gas exchange/capnography, monitors, alarms, scenarios, and device behavior. Separates headless physiology, visual monitor skins and manual/model-driven state. Reported prerelease 1.0.0-rc.5.
- **Additional integration/limitations:** Use first for live monitor; establish a unit-tested adapter that subscribes to a canonical case clock. Tests must link electrical rhythm to perfusion, not equate QRS activity with pulse. The source explicitly says not clinically validated.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/samhv-dev/patient-monitor-engine); [README](https://github.com/samhv-dev/patient-monitor-engine#readme); review the pinned license/notice before importing.

### 2. [tanjera/infirmary-integrated](https://github.com/tanjera/infirmary-integrated)
- **Creator:** **Ibi Keller** (`tanjera`).
- **What it does:** A training suite with cardiac monitoring, defibrillation, 12-lead ECG, IABP, fetal monitoring and simulated EHR/medication administration records, plus scenario-authoring tools.
- **Code quality:** **Promising–strong as a device simulator.** Substantial feature depth and long development history; integration complexity and differences between app/release licensing merit investigation. Not a drop-in lightweight game component.
- **Reuse:** **Very high for clinical-device UI and workflows; medium for direct integration** because its architecture may not match a new web-based game.
- **License:** **Apache-2.0 — verified** ([License.md](https://github.com/tanjera/infirmary-integrated/blob/master/License.md)). Check bundled dependencies, graphics, and any separate binary-release EULA before redistribution.


#### Added detailed-source dossier — 02

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** Prior audit: C#/.NET device simulation covering cardiac monitor, 12-lead ECG, defibrillation, intra-aortic balloon pump, fetal monitoring and chart functions, with educator-controlled scenarios.
- **Additional integration/limitations:** Good functional reference if real device control matters. README.md was inaccessible at the queried canonical path in this pass; avoid making stronger statements about its internal architecture until the correct entry point is inspected.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/tanjera/infirmary-integrated); README at the default path not confirmed; review the pinned license/notice before importing.

### 3. [pafolol/vitalis](https://github.com/pafolol/vitalis)
- **Creator:** `pafolol` (GitHub repository owner).
- **What it does:** Ambitious 3D emergency-room simulator with seeded patients, a 10 Hz continuous physiological engine, multi-organ pathologies, drugs/PK-PD, examination, ECG, radiology, POCUS, treatment and post-case debriefing.
- **Code quality:** **Promising but unverified.** TypeScript app with lint/typecheck, Vitest and Playwright scripts; sweeping physiology features are self-described, and clinical validation is explicitly absent. The project identifies known missing pathologies and approximations.
- **Reuse:** **Exceptionally high design fit; legally blocked for copying at present.** Study the interface boundaries and gameplay loop independently. Body/anatomy assets have **different** licenses (CC0, CC BY, and potentially share-alike provenance).
- **License:** **No application-code license found** in common root locations or README. Do **not** assume the asset-license section licenses application code; obtain an explicit grant before adapting it.


#### Added detailed-source dossier — 03

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: seed-generated 3D patients, a 10-Hz worker-driven physiological engine, pharmacology, composition of illness modules, examination/auscultation and interventions including airway management and defibrillation.
- **Additional integration/limitations:** Strong design reference for case progression and a procedural patient, but no identified reusable source license. The repository itself states the physiology lacks clinical validation.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/pafolol/vitalis); [README](https://github.com/pafolol/vitalis#readme); review the pinned license/notice before importing.

### 4. [arpitre/12-Lead-Generator](https://github.com/arpitre/12-Lead-Generator)
- **Creator:** `arpitre` and listed contributors.
- **What it does:** Dependency-free browser 12-lead ECG generator with about 85 case presets, selectable rhythm/ischemia/conduction findings, artifacts, blind testing mode and interpretation explanations.
- **Code quality:** **Promising.** Modular static web assets and a deliberately low-complexity deployment. Morphologies are teaching-grade approximations, not validated electrophysiology.
- **Reuse:** **Very high.** One of the easiest ways to create a playable ECG workstation where the diagnosis is not revealed until after interpretation.
- **License:** **MIT — verified** ([LICENSE](https://github.com/arpitre/12-Lead-Generator/blob/main/LICENSE)).


#### Added detailed-source dossier — 04

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: 85 teaching presets, composable conduction/rhythm/ischemia findings, PTB-XL calibration support, actual computed ECG measurements and an instructor-facing blind mode.
- **Additional integration/limitations:** One of the strongest formal ECG choices because the player can examine a generated tracing before seeing the interpretation. Cross-check consistency against live monitor state.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/arpitre/12-Lead-Generator); [README](https://github.com/arpitre/12-Lead-Generator#readme); review the pinned license/notice before importing.

### 5. [LaiCxm/biosimkit](https://github.com/LaiCxm/biosimkit)
- **Creator:** `LaiCxm`.
- **What it does:** Python-oriented multimodal signal synthesis: ECG, EEG, PPG, ABP and respiration, with pathologies and noise, exposed through a configurable virtual patient interface.
- **Code quality:** **Prototype–promising.** Clear signal-generator API, useful for controlled experiments; its README notes that many channels are independently generated and time-truncated, so real physiological coupling is limited.
- **Reuse:** **High as signal prototyping/test-data generator; medium as primary game physiology.** Prefer a consistent master timeline and clinical-state rules above it.
- **License:** **MIT stated in README, but no full root license file located.** Treat as **README-only / obtain confirmation** before redistribution; a bare `MIT` statement is less robust than an explicit full grant.

**Canonical correction:** A README MIT declaration was reported; an explicit full-root grant was not independently retrieved. It must not be flattened to “no license found” or to “fully cleared MIT” without a commit-pinned review.


#### Added detailed-source dossier — 05

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: synchronized programmable ECG, EEG, PPG, arterial pressure and respiration, custom ECG shaping and noise injection for signal-processing tests.
- **Additional integration/limitations:** Use as an offline synthesis reference, not the main physiology model; independent signal recipes can look convincing yet violate multi-organ causal relationships. No root license found.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/LaiCxm/biosimkit); [README](https://github.com/LaiCxm/biosimkit#readme); review the pinned license/notice before importing.
- **Reconciled license alert:** The newer detailed audit’s “no license found” does not replace the earlier **MIT-claimed-in-README** finding. Full root grant and scope remain unverified.

### 6. [riccardo-budai/ION_Simula](https://github.com/riccardo-budai/ION_Simula)
- **Creators:** **Riccardo Budai** and research collaborators, including **Rosmary Blanco**, as reported in the associated ION-Sim publication.
- **What it does:** Intraoperative neurophysiological-monitoring simulator used for training with electrophysiological traces and intraoperative alert scenarios. Its published paper describes an open-source IONM framework.
- **Code quality:** **Unclear–research prototype.** Repository is accessible, but no conventional root README/license was retrievable via the checks performed; a research paper is not a substitute for a code audit.
- **Reuse:** **Medium for specialized evoked-potential/operating-room scenarios; low for the core general diagnostics game.**
- **License:** **GNU GPL asserted by the associated paper, but no corresponding root license file verified.** Seek clarification about exact GPL version and repository-file coverage before copying. [Publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC13406592/).

**Canonical correction:** The published-paper GPL claim is a positive clue, not sufficient proof of a specific root code license/version.


#### Added detailed-source dossier — 06

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** Prior audit: niche intraoperative neurophysiology EEG/EMG/evoked-potential training and anomaly injection. It is closer to surgical monitoring than general medical diagnosis.
- **Additional integration/limitations:** Could support nerve monitoring mini-games, but first implement ordinary EEG interpretation with Epicurrents. README fetch was not successful, so details and root license remain prior-audit only.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/riccardo-budai/ION_Simula); README at the default path not confirmed; review the pinned license/notice before importing.
- **Reconciled license alert:** The detailed audit’s root-license uncertainty must be read alongside the ION-Sim publication’s GPL assertion; exact GPL version/file coverage is not established.

### 7. [robchiral/AnaSim](https://github.com/robchiral/AnaSim)
- **Creator:** **Robert Chen**.
- **What it does:** Python anesthesia simulator joining monitor, ventilation, cardiorespiratory physiology and pharmacokinetic/pharmacodynamic drug response, with adult comorbidities and procedural scenarios.
- **Code quality:** **Promising.** Documented package, installable command, CI and structured modeling; educational assumptions need validation.
- **Reuse:** **High functionality; legally conditional.** Very valuable as a modeling reference or for permitted noncommercial educational deployment, **not** an unrestricted component in a distributed game.
- **License:** **Custom `AnaSim noncommercial license 1.0` — verified** ([LICENSE](https://github.com/robchiral/AnaSim/blob/main/LICENSE)). Personal study and specified nonprofit instruction are permitted; commercial/institutional uses and most external hosting require a written license. Modified copies may be shared for permitted uses with obligations; check earlier versions and third-party provenance.


#### Added detailed-source dossier — 07

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: adult anesthesia simulator combining patient factors, pharmacokinetics/dynamics, ventilatory modes, hemodynamics, monitors and headless operation.
- **Additional integration/limitations:** Educational reference for drug and anesthesia responses. Its noncommercial source/license conditions make unrestricted integration unsuitable.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/robchiral/AnaSim); [README](https://github.com/robchiral/AnaSim#readme); review the pinned license/notice before importing.

### 8. [fedebarra/open-vent-sim](https://github.com/fedebarra/open-vent-sim)
- **Creator:** **Federico Lorenzo Barra** and contributors.
- **What it does:** ICU ventilator, anesthesia workstation and high-flow oxygen educational simulator. Calculates pressure/flow/volume loops, patient effort/asynchrony and gas exchange, with an instructor-facing session system.
- **Code quality:** **Promising–strong.** Detailed mechanics, documentation, versioned releases and related peer-reviewed publication; not independent proof of every modeled intervention.
- **Reuse:** **High** for ventilation cases, blood gas interpretation and ICU settings; perhaps excessive for the game’s first general-medicine release.
- **License:** **MIT — verified** ([LICENSE](https://github.com/fedebarra/open-vent-sim/blob/main/LICENSE)).


#### Added detailed-source dossier — 08

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: an equation-of-motion ventilator with auto-PEEP, trigger/cycling effects, pressure–flow–volume traces, modeled blood gases, three device modes and an instructor console.
- **Additional integration/limitations:** Best respiratory training proof-of-concept; test it with realistic gas exchange and patient effort cases before importing. Version 3.4.1 is author-reported as of mid-November 2026.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/fedebarra/open-vent-sim); [README](https://github.com/fedebarra/open-vent-sim#readme); review the pinned license/notice before importing.

### 9. [Nicholas-Amsler/lung-iq](https://github.com/Nicholas-Amsler/lung-iq)
- **Creator:** **Nicholas Amsler**.
- **What it does:** Ventilator waveform and respiratory training application covering pediatric/adult parameter settings, ARDS/COPD/pneumothorax patterns, challenges and training paths.
- **Code quality:** **Prototype–promising.** Extensive feature claims, but even the introductory screenshot is a placeholder; clinical/guideline accuracy and test coverage require audit.
- **Reuse:** **Medium–high** for a respiratory interpretation/learning module, less compelling than Open Vent Sim as the underlying model.
- **License:** **MIT — verified** ([LICENSE](https://github.com/Nicholas-Amsler/lung-iq/blob/main/LICENSE)).


#### Added detailed-source dossier — 09

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: real-time waveforms for adult, pediatric and extremely premature simulated patients with demographic and lung-protective parameter constraints.
- **Additional integration/limitations:** Optional pediatric/ARDS teaching extension; compare its equation and waveform behavior against Open Vent Sim rather than duplicating both.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Nicholas-Amsler/lung-iq); [README](https://github.com/Nicholas-Amsler/lung-iq#readme); review the pinned license/notice before importing.

### 10. [bowowbox/vent-teach](https://github.com/bowowbox/vent-teach)
- **Creator:** `bowowbox`.
- **What it does:** Interactive React/TypeScript teaching app for respiratory mechanics, ventilator asynchrony and instructor/learner sessions. Uses a single-compartment equation-of-motion simulation and a custom 60-fps Canvas waveform display.
- **Code quality:** **Promising educational prototype.** Coherent stated architecture and model-driven rather than hand-drawn asynchronies; relies on Firebase for paired sessions.
- **Reuse:** **Medium–high concept fit**, particularly for teaching recognition and correction of dyssynchrony.
- **License:** **No license found.** README calls it an open teaching resource but does **not** grant reusable software rights. Treat code as **not cleared**.


#### Added detailed-source dossier — 10

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: one-compartment mechanics producing six ventilator dyssynchrony cases, interactive settings, a learn/sandbox/challenge loop and optional two-device instructor sessions.
- **Additional integration/limitations:** A useful training mini-game: learners fix the underlying asynchrony instead of merely reading a label. No root software LICENSE was independently established.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/bowowbox/vent-teach); [README](https://github.com/bowowbox/vent-teach#readme); review the pinned license/notice before importing.

## III-B. ECG and cardiac simulation

### 11. [seanwkelley/ecg-simulator](https://github.com/seanwkelley/ecg-simulator)
- **Creator:** **Sean Kelley**.
- **What it does:** React ECG rhythm trainer covering numerous rhythm families, lead-specific 12-lead appearances, ischemic territories, metabolic changes, pacemaker patterns, heart sounds and clinical interpretation notes. The README inconsistently describes **39** vs **42** rhythms, so verify the actual catalog.
- **Code quality:** **Promising prototype.** Rich simulated phenotypes with relatively little app infrastructure: much UI lives in one large React component, which hurts maintainability and unit-level reuse.
- **Reuse:** **High** as a rhythm-pattern library and teaching reference; refactor waveform logic away from UI before integrating.
- **License:** **MIT — verified** ([LICENSE](https://github.com/seanwkelley/ecg-simulator/blob/main/LICENSE)).


#### Added detailed-source dossier — 11

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: single React ECG renderer with 12-lead and rhythm catalog, clinical ST morphology, paced rhythms, shock classification and audio. Its own overview says 39 while feature list says 42 rhythms.
- **Additional integration/limitations:** Good compact alternative to the 12-Lead Generator; inspect the actual implemented catalog and clinical morphology before choosing.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/seanwkelley/ecg-simulator); [README](https://github.com/seanwkelley/ecg-simulator#readme); review the pinned license/notice before importing.

### 12. [zhenyuanzhou/cardiosim-lab](https://github.com/zhenyuanzhou/cardiosim-lab)
- **Creator:** `zhenyuanzhou` (Zhenyuan Zhou).
- **What it does:** Causal teaching simulator connecting cellular action potentials, 3D cardiac activation and projected 12-lead ECG. Includes scenario comparison, activation visualization and measurements.
- **Code quality:** **Promising–strong engineering signals.** TypeScript, Vitest, Playwright and an explicit validation script; README reports 104 physiology/unit tests and 21 browser tests. Educational model is not clinically validated.
- **Reuse:** **High technically for 3D cardiac teaching, but restricted for commercial scenarios.** Better for studying a model-driven approach than serving as the default production ECG engine.
- **License:** **CC BY-NC 4.0 — verified** ([LICENSE](https://github.com/zhenyuanzhou/cardiosim-lab/blob/main/LICENSE)); `package.json` also declares `CC-BY-NC-4.0`. Commercial reuse prohibited; CC licenses are also not ideal software licenses. Check interpretation for any intended distribution.


#### Added detailed-source dossier — 12

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: linked cellular action potentials, 3D conduction, torso lead vectors and deterministic real-time 12-lead tracings with A/B comparisons.
- **Additional integration/limitations:** Interesting causal heart-electricity reference but not a freely integrable commercial component because it uses a noncommercial Creative Commons license.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/zhenyuanzhou/cardiosim-lab); [README](https://github.com/zhenyuanzhou/cardiosim-lab#readme); review the pinned license/notice before importing.

### 13. [SeraKah-1/cardiac-3d-ecg-simulator](https://github.com/SeraKah-1/cardiac-3d-ecg-simulator)
- **Creator:** `SeraKah-1`.
- **What it does:** React/Three.js 3D cardiac electrophysiology and ECG visualization with bilingual curriculum, interpretive exercises and extensive claimed numerical test coverage.
- **Code quality:** **Promising, with verification needed.** Ambitious architecture and declared tests, but claims such as **15,925 tests passed** are repository-provided and were **not independently run**. Distinguish graphics/teaching plausibility from genuine electrophysiological fidelity.
- **Reuse:** **High for an explorable 3D heart and ECG lessons; medium for integration** owing to complexity and curricular scope.
- **License:** **MIT — verified** ([LICENSE](https://github.com/SeraKah-1/cardiac-3d-ecg-simulator/blob/main/LICENSE)). Audit any third-party curriculum excerpts, images and audiovisual material independently.


#### Added detailed-source dossier — 13

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: 3D volume-conductor-based teaching application, clinical ECG practice, 21 cases/100 digital-caliper exercises as documented, dual-language UI and extensive claimed tests.
- **Additional integration/limitations:** Evaluate whether its caliper, grading and lead tools are superior to the smaller 12-Lead Generator. Clinical-calibration claims should be independently tested.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/SeraKah-1/cardiac-3d-ecg-simulator); [README](https://github.com/SeraKah-1/cardiac-3d-ecg-simulator#readme); review the pinned license/notice before importing.

### 14. [infocusp/ecg-atlas](https://github.com/infocusp/ecg-atlas)
- **Creator:** `infocusp` and ECG Atlas contributors.
- **What it does:** Interactive ECG exploration through anatomical electrode placement, two-/three-/12-lead views, recordings and crafted waveforms, beating-heart visualizations and contextual education.
- **Code quality:** **Promising.** The project has unusually explicit provenance and asset-license documentation, and distinguishes measured recordings from synthetic teaching examples.
- **Reuse:** **High** for patient electrode placement and 12-lead collection gameplay, especially as a complement to an independently synchronized monitor.
- **License:** **MIT for original app code — verified** ([LICENSE](https://github.com/infocusp/ecg-atlas/blob/main/LICENSE)); **anatomy assets CC BY 4.0, decoder Apache-2.0, ECG excerpts CC BY 4.0 or ODC-By 1.0** per README. Read [asset inventory](https://github.com/infocusp/ecg-atlas/blob/main/public/ATTRIBUTION.md) and each signal's manifest before copying data.


#### Added detailed-source dossier — 14

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: free electrode placement, normal/AF/VF recorded examples, teaching strips and paired heart/ECG visualizations.
- **Additional integration/limitations:** Best instructional electrode-placement reference. The app code is MIT but anatomy and recorded signals have separate licenses.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/infocusp/ecg-atlas); [README](https://github.com/infocusp/ecg-atlas#readme); review the pinned license/notice before importing.

### 15. [aschanken/EKGSim](https://github.com/aschanken/EKGSim)
- **Creator:** `aschanken`.
- **What it does:** Browser-based ACLS rhythm and intervention trainer. Two ECG channels, calibrated graph-paper sweep, live HR/NIBP/SpO₂, alarms, variable rhythms, audio and quiz mode.
- **Code quality:** **Promising, focused prototype.** Self-contained JS Canvas rendering and reasonable UI constraints; README admits the lead projection uses a coefficient table, not a cardiac dipole model.
- **Reuse:** **High for design inspiration; source copying blocked.** Particularly good bedside-monitor appearance and teaching interactions.
- **License:** **No license found** in common root files or README. Obtain permission before incorporation.


#### Added detailed-source dossier — 15

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: 18 ACLS dysrhythmias, calibrated monitor paper, QRS-derived heart rate, patient status and rhythm-plus-intervention assessment.
- **Additional integration/limitations:** Borrow the two-stage quiz mechanism, but avoid code reuse without a clearly identified license.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/aschanken/EKGSim); [README](https://github.com/aschanken/EKGSim#readme); review the pinned license/notice before importing.

### 16. [goga-lanchava/ecg-simulator](https://github.com/goga-lanchava/ecg-simulator)
- **Creator:** `goga-lanchava`.
- **What it does:** Python/PyQt6 and pyqtgraph synthetic patient monitor with ECG, ABP, pleth and respiration; 19 arrhythmias, CPR/defibrillation and alarms. Readouts are computed from generated traces rather than copied from sliders.
- **Code quality:** **Promising prototype.** Conceptually strong waveforms-to-numerics coupling and desktop packaging. Requires refactoring for web deployment and explicit independent medical-model validation.
- **Reuse:** **High design value, medium technical portability; legally blocked** without a license. The waveform-driven vital-sign principle is worth replicating independently.
- **License:** **No license found** in common root files or README.


#### Added detailed-source dossier — 16

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: four synchronized ECG/pleth/arterial/respiratory lanes, 19 rhythms, six breathing patterns, CPR, defibrillation, artifact and scenario script controls.
- **Additional integration/limitations:** An alternative dedicated desktop monitor; lacks a verified reuse license. The synthetic physiologic coupling may still inform regression tests.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/goga-lanchava/ecg-simulator); [README](https://github.com/goga-lanchava/ecg-simulator#readme); review the pinned license/notice before importing.

### 17. [efavirenz/MI-ECG-learning-simulator](https://github.com/efavirenz/MI-ECG-learning-simulator)
- **Creator:** `efavirenz`.
- **What it does:** Interactive 12-lead ECG electrode-positioning and myocardial infarction localization trainer, including right/posterior leads, teaching thresholds and synthetic cases.
- **Code quality:** **Promising educational prototype.** Rich explanatory text and structured learning objectives; clinical thresholds and guideline interpretations should be reviewed before use.
- **Reuse:** **Medium–high conceptually**, especially bedside acquisition and MI interpretation; less useful as a general physiological engine.
- **License:** **No license found** in common root files or README. Educational disclaimers do not authorize copying.


#### Added detailed-source dossier — 17

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: electrode landmarks, supplementary posterior/right-sided leads, myocardial territory localization, STEMI mimics and calibrated educational ECG views.
- **Additional integration/limitations:** Good advanced ECG teaching reference; does not automatically belong in the first release, and its license was not verified.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/efavirenz/MI-ECG-learning-simulator); [README](https://github.com/efavirenz/MI-ECG-learning-simulator#readme); review the pinned license/notice before importing.

## III-C. Echocardiography and ultrasound simulation

### 18. [douyang/echodemo](https://github.com/douyang/echodemo)
- **Creator:** `douyang`.
- **What it does:** *The Heart by Ultrasound*, an unusually rich interactive echo curriculum: transducer views, ultrasound physics, Doppler, simulated imaging, EF, hemodynamics, valve disease and pathology. Includes a 3D heart and freely manipulated probe.
- **Code quality:** **Promising–strong educational presentation.** Detailed guideline references and consistent instructional structure; generated images and measurements are illustrative rather than clinically validated.
- **Reuse:** **Extremely high as the echo experience to emulate; legally blocked for code/asset copying** until licensed. One of the highest-priority authors to contact.
- **License:** **No license found** in root files or README. The public educational website does not imply permission to embed the implementation.


#### Added detailed-source dossier — 18

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: interactive echo curriculum with 35 TTE views, Doppler, valve anatomy, pathologies and simulated views from a common virtual heart.
- **Additional integration/limitations:** Use for interaction design and teaching pathway concepts. Public source without a reuse license is not a code library.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/douyang/echodemo); [README](https://github.com/douyang/echodemo#readme); review the pinned license/notice before importing.

### 19. [gowthamaanp/simpsonef](https://github.com/gowthamaanp/simpsonef)
- **Creators:** **Gowthamaan Palani** and **Ganapathy Krishnamurthi**, per copyright notice.
- **What it does:** Research model that traces echo chamber boundaries on existing A4C/A2C video, identifies end-diastole/end-systole and computes LV ejection fraction using Simpson's rule, with explainable overlays.
- **Code quality:** **Promising research-grade.** Documented architecture, published numerical evaluation and model checkpoints; model accuracy depends on domain-specific datasets and image acquisition style.
- **Reuse:** **Medium–high for a quantitative echo-reading tool**, but **not an echo-image generator**. Could score a learner’s manual EF estimate against an actual echo clip if dataset rights permit.
- **License:** **MIT for repository code — verified** ([LICENSE](https://github.com/gowthamaanp/simpsonef/blob/main/LICENSE)). Review model weight, EchoNet/CAMUS and input-video terms separately.


#### Added detailed-source dossier — 19

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: AI-predicted LV cavity tracings, ED/ES timing, Simpson's disks and interpretable EF calculations using echo clips.
- **Additional integration/limitations:** Could enable manual/assisted measurement in recorded studies. Code license and model/data rights differ; only adopt permitted assets.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/gowthamaanp/simpsonef); [README](https://github.com/gowthamaanp/simpsonef#readme); review the pinned license/notice before importing.

### 20. [hoodlm/affordable-medical-ultrasound-training-simulator](https://github.com/hoodlm/affordable-medical-ultrasound-training-simulator)
- **Creator:** **Logan M. Hood**, associated with a University of South Carolina 2013–2014 research project.
- **What it does:** Older Unity 3D augmented-reality ultrasound teaching prototype with anatomical assets and physical-simulator integration.
- **Code quality:** **Legacy.** Research proof of concept with old Unity/assets workflow; large model files need manual reassembly. Expect significant update and porting work.
- **Reuse:** **Medium as a design/asset-processing reference; low as a foundation for a modern web game**.
- **License:** **MIT — verified** ([LICENSE.txt](https://github.com/hoodlm/affordable-medical-ultrasound-training-simulator/blob/master/LICENSE.txt)). **Verify provenance of large 3D body asset separately**; repository code permission does not automatically settle all asset rights.


#### Added detailed-source dossier — 20

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: early university VR/AR ultrasound training research prototype published under MIT.
- **Additional integration/limitations:** An old acquisition interaction reference, but dated build systems and uncertain asset applicability make it low priority.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/hoodlm/affordable-medical-ultrasound-training-simulator); [README](https://github.com/hoodlm/affordable-medical-ultrasound-training-simulator#readme); review the pinned license/notice before importing.

### 21. [yunhaoli24/OTC-Flow](https://github.com/yunhaoli24/OTC-Flow)
- **Creators:** **Yunhao Li** and coauthors at Hong Kong Polytechnic University, University of Hong Kong and collaborating institutes.
- **What it does:** Research system synthesizing transesophageal echocardiography-like images conditioned on CT, using learned cross-modality translation/flow matching and anatomical constraints.
- **Code quality:** **Promising research-grade.** Detailed method and manuscript; usable output depends on trained models, CT data, runtime and available checkpoints.
- **Reuse:** **Medium for advanced ultrasound rendering R&D**, low for a fast plug-and-play echo workstation. Potentially valuable later for synthetic teaching cases.
- **License:** **MIT for released code — verified** ([LICENSE](https://github.com/yunhaoli24/OTC-Flow/blob/main/LICENSE)). Independently inspect model and training-data rights and clinical applicability.


#### Added detailed-source dossier — 21

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: MICCAI 2026 CT-conditioned transesophageal ultrasound synthesis pipeline, with official Hugging Face checkpoint companion.
- **Additional integration/limitations:** Advanced research only: image plausibility and clinical anatomy cannot be assumed from model output. Code MIT, weights/datasets require separate verification.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/yunhaoli24/OTC-Flow); [README](https://github.com/yunhaoli24/OTC-Flow#readme); review the pinned license/notice before importing.

### 22. [ahastava/moculus](https://github.com/ahastava/moculus)
- **Creator:** `ahastava`.
- **What it does:** MoCoLUS, a lung-POCUS training environment with web/BLE probe controls and diffusion-model-generated B/M-mode images across claimed pathology classes; Docker/CPU cache paths are described.
- **Code quality:** **Promising experimental/research prototype.** Rich architecture/deployment documentation and infrastructure, but complex model and dataset dependencies; repository includes developer-local deployment assumptions that require cleanup before sharing.
- **Reuse:** **Medium–high concept fit for lung ultrasound, but source reuse not cleared**. Also consider whether simulated images can satisfy cases without pretrained model availability.
- **License:** **No license found** in common root files/README; clinical training datasets and checkpoints may have independent restrictions.


#### Added detailed-source dossier — 22

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: lung ultrasound teaching with interactive chest zones, probe IMU/BLE option, diffusion-generated B/M-mode frames and cached CPU playback.
- **Additional integration/limitations:** Potential future POCUS acquisition system; the model's source datasets and application license are not cleared for reuse.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ahastava/moculus); [README](https://github.com/ahastava/moculus#readme); review the pinned license/notice before importing.

### 23. [asclepius/edus2](https://github.com/asclepius/edus2)
- **Creator:** `asclepius` contributors.
- **What it does:** Emergency Department Ultrasound Simulator, coupling an RFID-enabled pretend transducer to anatomy-specific prerecorded clips in a physical mannequin setting. Uses Python, X11 and mplayer.
- **Code quality:** **Legacy.** Functional historical teaching pattern, but outdated desktop/hardware assumptions and limited reuse portability.
- **Reuse:** **Low for direct integration, medium for interaction ideas**: physical placement selects a corresponding ultrasound clip.
- **License:** **GPL-3.0 — verified** ([COPYING](https://github.com/asclepius/edus2/blob/master/COPYING)); distributed derivatives may need GPL-compatible licensing and source distribution.


#### Added detailed-source dossier — 23

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** Prior audit: older GPL-3 EDUS2 interactive ultrasound training package using probe/tag-to-video mapping.
- **Additional integration/limitations:** Useful acquisition mechanics, but no default README was fetched and integration would bring a dated system plus copyleft obligations.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/asclepius/edus2); README at the default path not confirmed; review the pinned license/notice before importing.

### 24. [jiff3/ar-ultrasound-slice-simulator](https://github.com/jiff3/ar-ultrasound-slice-simulator)
- **Creator:** `jiff3`.
- **What it does:** Browser-based React/Three.js phantom, freely moving virtual transducer and procedural synthetic B-mode slice tied to transducer plane, position and orientation.
- **Code quality:** **Promising small prototype.** Good separation of probe geometry, synthetic anatomy and rendering; README describes Vitest tests, but the repo is small/early and not a true tissue-acoustics simulator.
- **Reuse:** **Very high concept fit for acquisition gameplay**; not yet a source-cleared module. The plane-to-image linkage is an important design reference.
- **License:** **No license found** in common root files/README. Request a license before copying the slice renderer.


#### Added detailed-source dossier — 24

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: React/Three.js spatial probe and procedurally generated virtual B-mode slice displayed in its 3D acquisition plane.
- **Additional integration/limitations:** Excellent simple geometry demonstration, but a coarse phantom is not equivalent to clinically interpretable pathology-specific ultrasound. License not found.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/jiff3/ar-ultrasound-slice-simulator); [README](https://github.com/jiff3/ar-ultrasound-slice-simulator#readme); review the pinned license/notice before importing.

### 25. [osamamalik/TEESimulator](https://github.com/osamamalik/TEESimulator)
- **Creator:** **Osama Malik**, as identified in the project README.
- **What it does:** Student project for training transesophageal probe movement using an Arduino/mouse sensor, serial bridge and VTK visualization of patient CT slices.
- **Code quality:** **Legacy/student proof of concept.** Platform-specific Xcode/VTK and hardware assumptions; README describes a concept and demonstration rather than a portable modular simulation engine.
- **Reuse:** **Low–medium as a historical transducer-tracking reference**, low for direct modern deployment.
- **License:** **No license found** in common root files/README; the phrase “open source” in the objective is not an express reuse license.


#### Added detailed-source dossier — 25

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** Prior audit: Arduino-linked transesophageal probe position tracking with CT anatomical visualization rather than realistic live B-mode output.
- **Additional integration/limitations:** Hardware-centric research reference; require license and build review before importing code.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/osamamalik/TEESimulator); README at the default path not confirmed; review the pinned license/notice before importing.

## III-D. CT, MRI, radiology and pathology

### 26. [OHIF/Viewers](https://github.com/OHIF/Viewers)
- **Creator/maintainer:** **Open Health Imaging Foundation (OHIF)** and its contributors.
- **What it does:** Full web PACS/DICOM viewer with study/series navigation, image stacks, multiplanar and advanced workflows, measurements, segmentation and extensible display modes, using DICOMweb data sources.
- **Code quality:** **Strong.** Mature, documented multi-package production-grade system. Large dependency surface and deployment/configuration complexity are the main integration costs.
- **Reuse:** **Very high for the diagnostic imaging station**, especially CT/MRI and radiology reporting. Can be a separate workstation/panel rather than embedded into every game screen.
- **License:** **MIT — verified** ([LICENSE](https://github.com/OHIF/Viewers/blob/master/LICENSE)); retain notices and review bundled packages/data.


#### Added detailed-source dossier — 26

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: current OHIF full DICOMweb browser workstation, extensions, mode configuration and radiology-focused UI.
- **Additional integration/limitations:** Primary scan viewer for CT/MRI/X-ray studies. Prefer it over writing windowing/MPR/measurement implementations from scratch.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/OHIF/Viewers); [README](https://github.com/OHIF/Viewers#readme); review the pinned license/notice before importing.

### 27. [cornerstonejs/cornerstone3D](https://github.com/cornerstonejs/cornerstone3D)
- **Creator/maintainer:** **Cornerstone and the OHIF community**.
- **What it does:** Lower-level JavaScript medical-image visualization stack powering apps such as OHIF. Supports efficient DICOM decoding, image/volume rendering, interactions and medical imaging tool APIs.
- **Code quality:** **Strong.** Well-documented modular TypeScript ecosystem with testing and downstream OHIF integration checks, although backend format/codec complexity is nontrivial.
- **Reuse:** **Very high if developing a custom radiology interface**, whereas OHIF is faster when a complete workstation is wanted. Do not duplicate both stacks unnecessarily.
- **License:** **MIT — verified** ([LICENSE](https://github.com/cornerstonejs/cornerstone3D/blob/main/LICENSE)); verify branch path if the default changes.


#### Added detailed-source dossier — 27

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: high-performance Cornerstone3D JavaScript image/volume loaders, WebGL/WebAssembly rendering and customizable metadata/interaction modules.
- **Additional integration/limitations:** Underlying OHIF dependency; import directly only to build a smaller custom game imaging panel.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/cornerstonejs/cornerstone3D); [README](https://github.com/cornerstonejs/cornerstone3D#readme); review the pinned license/notice before importing.

### 28. [Kitware/VolView](https://github.com/Kitware/VolView)
- **Creator/maintainer:** **Kitware**.
- **What it does:** Browser radiological volume viewer with local DICOM import, 2D slicing, interactive cinematic 3D volume rendering, windowing, measurements and annotations.
- **Code quality:** **Strong.** Backed by an established imaging-technology organization, documented application workflow and specialized rendering expertise; different scope from a full PACS system.
- **Reuse:** **High** for visually impressive CT/MRI volume interpretation, standalone radiology lesson or 3D reconstruction panel.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/Kitware/VolView/blob/main/LICENSE)); inspect dependencies and bundled rendering assets.


#### Added detailed-source dossier — 28

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: browser-first volumetric DICOM rendering, drag-and-drop studies and cinematic 3D visualization.
- **Additional integration/limitations:** Useful alternative for impressive volumetric exploration; not necessarily better than OHIF for clinical workflow and longitudinal cases.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Kitware/VolView); [README](https://github.com/Kitware/VolView#readme); review the pinned license/notice before importing.

### 29. [Slicer/Slicer](https://github.com/Slicer/Slicer)
- **Creator/maintainer:** **3D Slicer community**, historically linked to **Brigham and Women's Hospital** and multi-institutional research teams.
- **What it does:** Extensive cross-platform medical-image visualization, segmentation, registration, quantitative analysis and research platform, especially for volumetric imaging.
- **Code quality:** **Strong and mature.** Significant research usage and community testing; heavyweight native desktop architecture rather than a browser-first game component.
- **Reuse:** **Medium for direct embedding, high as reference or external tool** for preparing teaching assets, cases and segmented image datasets.
- **License:** **3D Slicer custom BSD-style agreement — verified** ([License.txt](https://github.com/Slicer/Slicer/blob/main/License.txt)). **Not simply standard BSD-3-Clause**; includes specific attribution, redistribution and modified-version terms. Read the agreement carefully.

**Canonical correction:** License is **custom BSD-style**, not automatically stock BSD-3-Clause. Preserve the actual original terms.


#### Added detailed-source dossier — 29

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: prominent research desktop 3D medical image processing application with segmentation, registration and extensions.
- **Additional integration/limitations:** Heavyweight reference for advanced MRI/CT, not a practical dependency for a small browser game. Its license file and extensions require review.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Slicer/Slicer); [README](https://github.com/Slicer/Slicer#readme); review the pinned license/notice before importing.
- **Reconciled license alert:** The earlier inspected 3D Slicer License.txt contains custom BSD-style terms. Do not collapse the legal status to either ordinary BSD-3-Clause or an unsupported generic “mixed” label.

### 30. [openseadragon/openseadragon](https://github.com/openseadragon/openseadragon)
- **Creator/maintainer:** **OpenSeadragon contributors**, with **Ian Gilman** among the principal creators/maintainers.
- **What it does:** Pure-JavaScript viewer for deep-zoom images and multiresolution tiling. Not medical-specific, but very suitable for enormous histology/pathology slides.
- **Code quality:** **Strong.** Established, reusable JavaScript library with documentation, examples and widely understood coordinate/zoom operations.
- **Reuse:** **Very high** as the microscopy interaction layer. Add medical measurements, specimen metadata and diagnosis overlays separately.
- **License:** **New BSD / BSD-3-Clause-style — verified** ([LICENSE.txt](https://github.com/openseadragon/openseadragon/blob/master/LICENSE.txt)); preserve full notices and disclaimers.


#### Added detailed-source dossier — 30

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: BSD-licensed pure-JS deep zoom viewer for enormous images, not a DICOM-aware pathology workflow by itself.
- **Additional integration/limitations:** Foundation for tiled histology, if no clinical PACS requirements are needed; use separately licensed slide assets.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/openseadragon/openseadragon); [README](https://github.com/openseadragon/openseadragon#readme); review the pinned license/notice before importing.

### 31. [pathologysmile/wsi-viewer](https://github.com/pathologysmile/wsi-viewer)
- **Creator/maintainer:** `pathologysmile`; copyright identifies **Kather Lab at EKFZ / TU Dresden**.
- **What it does:** Browser pathology whole-slide and NIfTI image viewer, using OpenSeadragon for tissue slides plus FastAPI, Vue, VTK.js, Docker and caching infrastructure for large data.
- **Code quality:** **Promising.** Clear deployment architecture and well-defined imaging features; its production-readiness claim was not operationally audited.
- **Reuse:** **High** if the game needs a realistic pathology/histology workstation in addition to a DICOM radiology viewer.
- **License:** **MIT — verified** ([LICENSE](https://github.com/pathologysmile/wsi-viewer/blob/main/LICENSE)); clinical slide files need separate rights.


#### Added detailed-source dossier — 31

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: FastAPI/Vue/OpenSeadragon pathology application with NIfTI/VTK visualizations and Docker support.
- **Additional integration/limitations:** An integrated low-cost whole-slide viewer; compare against DICOM-centric Slim according to the intended pathology data format.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/pathologysmile/wsi-viewer); [README](https://github.com/pathologysmile/wsi-viewer#readme); review the pinned license/notice before importing.

## III-E. EEG, EMG and neurophysiology

### 32. [eegdb/eeg-simulator](https://github.com/eegdb/eeg-simulator)
- **Creator/maintainer:** `eegdb` / **EEG Simulator Team**.
- **What it does:** Desktop Python/PyQt6 + MNE simulator. Configure cortical dipole/patch sources, electrode montage, coupling and noise; display time traces, FFTs and scalp topograms; export EDF/FIF or stream LSL.
- **Code quality:** **Promising.** Proper separation of forward models, signal generation, visualization and export, backed by MNE; needs computational-performance and realism testing.
- **Reuse:** **High for synthetic EEG experiments; medium for direct game integration** because of desktop/Python dependencies. Generated EDF could be passed to a web EEG viewer.
- **License:** **MIT — verified** ([LICENSE](https://github.com/eegdb/eeg-simulator/blob/main/LICENSE)). Check MNE and bundled anatomical data separately.


#### Added detailed-source dossier — 32

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: PyQt/MNE EEG source and electrode selection, synthetic cortical activity, live signal views, topography and spectral analysis.
- **Additional integration/limitations:** Useful offline EEG fixture generator, but clinical ictal patterns require independent review and/or real recordings.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/eegdb/eeg-simulator); [README](https://github.com/eegdb/eeg-simulator#readme); review the pinned license/notice before importing.

### 33. [dbrang/Neuron-to-EEG-Demo](https://github.com/dbrang/Neuron-to-EEG-Demo)
- **Creator:** `dbrang`.
- **What it does:** Browser teaching demo showing how neuronal conductances, recurrent populations, extracellular fields and rhythms lead to scalp EEG signals, with step-through and waveform exploration.
- **Code quality:** **Promising teaching prototype.** Zero dependencies and coherent pedagogical model; simplified circuit rather than a full multi-channel clinical EEG recording generator.
- **Reuse:** **Medium** for educational neurophysiology explainers, **low** for a full EEG diagnostic workstation.
- **License:** **MIT — verified** ([LICENSE](https://github.com/dbrang/Neuron-to-EEG-Demo/blob/main/LICENSE)).


#### Added detailed-source dossier — 33

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: single-file interactive demonstration connecting neuron/synapse currents and population rhythms to scalp EEG.
- **Additional integration/limitations:** Best pedagogical mini-lesson, not a complete diagnostic EEG workstation.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/dbrang/Neuron-to-EEG-Demo); [README](https://github.com/dbrang/Neuron-to-EEG-Demo#readme); review the pinned license/notice before importing.

### 34. [mne-tools/mne-python](https://github.com/mne-tools/mne-python)
- **Creator/maintainer:** **MNE-Python open-source research community**.
- **What it does:** Widely used scientific Python toolkit for analyzing EEG/MEG and related electrophysiology: filtering, artifacts, source estimation, visualization, epoching, montages and statistical processing.
- **Code quality:** **Strong.** Established research software, extensive docs and test culture. Powerful but much more general-purpose than a video-game subsystem.
- **Reuse:** **High as offline processing, dataset preparation and synthetic/real EEG verification; medium as a runtime dependency**. Keep heavy processing in a separate pipeline/service.
- **License:** **BSD-3-Clause-style — verified** ([LICENSE.txt](https://github.com/mne-tools/mne-python/blob/main/LICENSE.txt)); check optional datasets and dependencies.

**Epicurrents is a coordinated set of seven repositories, not seven independent EEG games.** The foundation is `core`; importers translate files to studies; modality modules represent EEG/EMG; `interface` renders them; `builder` assembles deployable editions. Combining these packages is substantially more useful than treating each as a standalone recommendation.


#### Added detailed-source dossier — 34

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** Prior audit: BSD-licensed research-grade Python EEG/MEG analysis and processing ecosystem.
- **Additional integration/limitations:** Useful offline EEG preprocessing, montage generation and reference checking; default README could not be retrieved in this pass.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/mne-tools/mne-python); README at the default path not confirmed; review the pinned license/notice before importing.

### 35. [epicurrents/core](https://github.com/epicurrents/core)
- **Creator/maintainer:** **Epicurrents maintainers and contributors**.
- **What it does:** Shared TypeScript runtime, study/module/reader abstractions, signal caches, workers, montages and state model for the Epicurrents biosignal viewer.
- **Code quality:** **Promising–strong.** Modular API, architectural documentation (`AGENTS.md`), type checking, unit tests and explicit worker/cache lifecycle.
- **Reuse:** **High** if adopting the Epicurrents EEG/EMG ecosystem; otherwise an unnecessary core dependency.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/core/blob/main/LICENSE)).


#### Added detailed-source dossier — 35

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: Epicurrents' headless runtime, worker protocol, state management, biosignal montages and modality/service registration.
- **Additional integration/limitations:** Core of the EEG/EMG workstation family, not a standalone viewing application.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/core); [README](https://github.com/epicurrents/core#readme); review the pinned license/notice before importing.

### 36. [epicurrents/eeg-module](https://github.com/epicurrents/eeg-module)
- **Creator/maintainer:** **Epicurrents contributors**.
- **What it does:** EEG domain objects, channel montages, annotations, time-synced video, spectrograms and scalp topography, built on `core` and file-reader packages.
- **Code quality:** **Promising–strong.** Clear responsibilities and public interfaces; integration requires the rest of the family.
- **Reuse:** **Very high** for a realistic EEG interpretation station with electrode/montage controls.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/eeg-module/blob/main/LICENSE)).


#### Added detailed-source dossier — 36

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: `EegRecording`, EEG setups, montage registration, annotations, trends and worker-based signal representation.
- **Additional integration/limitations:** Use for real multichannel EEG interpretation; combine with a reader and interface/builder.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/eeg-module); [README](https://github.com/epicurrents/eeg-module#readme); review the pinned license/notice before importing.

### 37. [epicurrents/emg-module](https://github.com/epicurrents/emg-module)
- **Creator/maintainer:** **Epicurrents contributors**.
- **What it does:** EMG waveform resources, cascade/montage presentation, study importing and audio playback of muscle signals, integrated into Epicurrents.
- **Code quality:** **Promising.** Explicit modality interface and lifecycle; this is analysis/playback infrastructure, not an EMG synthesis engine.
- **Reuse:** **Medium–high** for specialized neuropathy/EMG cases; lower first-version priority than EEG and ECG.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/emg-module/blob/main/LICENSE)).


#### Added detailed-source dossier — 37

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: EMG reader/recording, synchronized waveform audio, event annotations and modality-specific caching.
- **Additional integration/limitations:** Optional nerve/muscle interpretation panel. It is a companion module, not another independent full simulator.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/emg-module); [README](https://github.com/epicurrents/emg-module#readme); review the pinned license/notice before importing.

### 38. [epicurrents/edf-reader](https://github.com/epicurrents/edf-reader)
- **Creator/maintainer:** **Epicurrents contributors**.
- **What it does:** EDF/BDF/EDF+ physiological signal decoding and de-identified export; supports multichannel physiological datasets and file-based studies.
- **Code quality:** **Promising–strong.** Documentation explains sample widths, calibration, memory and worker behavior, suggesting good attention to correctness boundaries.
- **Reuse:** **High** for loading real/synthetic EEG, sleep and electrophysiology files into the game.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/edf-reader/blob/main/LICENSE)).


#### Added detailed-source dossier — 38

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: EDF/BDF import/export, decoding of signal channels and annotations, including EDF+D interruption handling.
- **Additional integration/limitations:** Important for real EEG studies; preserve calibrated units and reading discontinuities.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/edf-reader); [README](https://github.com/epicurrents/edf-reader#readme); review the pinned license/notice before importing.

### 39. [epicurrents/dicom-reader](https://github.com/epicurrents/dicom-reader)
- **Creator/maintainer:** **Epicurrents contributors**.
- **What it does:** Imports *DICOM waveform objects* (EEG, ECG, EMG etc.) into Epicurrents, using dcmjs for container parsing and its own calibration/deinterleaving logic.
- **Code quality:** **Promising.** Well-defined sample interpretations and explicit unsupported representations. README states only the **first multiplex group** is read, a relevant limitation.
- **Reuse:** **Medium–high** if supporting DICOM ECG/EEG files. **Not** a replacement for Cornerstone/OHIF radiology image reading.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/dicom-reader/blob/main/LICENSE)); dcmjs licensing is separate.


#### Added detailed-source dossier — 39

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: DICOM waveform IOD reader for EEG/ECG/EMG using dcmjs for container parsing.
- **Additional integration/limitations:** Complements OHIF's image viewing; not a CT/MRI renderer. Useful in a unified investigation asset pipeline.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/dicom-reader); [README](https://github.com/epicurrents/dicom-reader#readme); review the pinned license/notice before importing.

### 40. [epicurrents/interface](https://github.com/epicurrents/interface)
- **Creator/maintainer:** **Epicurrents contributors**.
- **What it does:** Vue/Vite front end for EEG/EMG and other Epicurrents study modules, with modular registration and standalone build support.
- **Code quality:** **Promising–strong.** Documented module exports, type checking and unit tests. Requires integration with the same core state and package versions.
- **Reuse:** **High if embedding a full biosignal viewer; medium if designing a completely custom UI**.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/interface/blob/main/LICENSE)).


#### Added detailed-source dossier — 40

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: Vue/Vite UI that registers Epicurrents modality packages and builds as a reusable module.
- **Additional integration/limitations:** Modular EEG interface to embed inside the game. Keep patient selection and investigation authorization in the host application.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/interface); [README](https://github.com/epicurrents/interface#readme); review the pinned license/notice before importing.

### 41. [epicurrents/builder](https://github.com/epicurrents/builder)
- **Creator/maintainer:** **Epicurrents contributors**.
- **What it does:** Node build orchestration for assembling independently versioned Epicurrents packages into standalone web apps and embeddable editions, including optional OHIF integration.
- **Code quality:** **Promising.** Explicit build profiles, dependency order and release process; it is infrastructure, not a waveform generator.
- **Reuse:** **Medium–high if using the full Epicurrents ecosystem**. You probably do not need it if embedding a small subset with your own application build.
- **License:** **Apache-2.0 — verified** ([LICENSE](https://github.com/epicurrents/builder/blob/main/LICENSE)).


#### Added detailed-source dossier — 41

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: Node-based builder producing modality-specific Epicurrents editions and embeddable application libraries.
- **Additional integration/limitations:** Start from its EEG edition rather than hand-assembling several packages; additional modules such as NCS and ONNX services exist in the wider family.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/epicurrents/builder); [README](https://github.com/epicurrents/builder#readme); review the pinned license/notice before importing.

## III-F. Medical diagnostic games and virtual patients

### 42. [mrmehar229/virtual-patient](https://github.com/mrmehar229/virtual-patient)
- **Creator:** `mrmehar229`.
- **What it does:** AI clinical reasoning web game: generate fictional patients, interview them, select investigations, submit diagnoses and receive an OSCE-style evaluation of the reasoning process.
- **Code quality:** **Prototype.** Clear product scope and role separation for patient/examiner; README contains a placeholder deployment link, and fixed test ordering is less capable than a complete hospital workflow.
- **Reuse:** **High design relevance, but not cleared for code copying.** Relevant for question-answer gating, test selection and end-of-case grading; ensure generated cases/results cannot contradict authoritative case state.
- **License:** **No license found** in common root files or README. Permission required to reuse implementation.


#### Added detailed-source dossier — 42

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: AI patient role, ordering investigations, differential/final diagnosis and examiner-style feedback in a web app.
- **Additional integration/limitations:** Mechanically close to the game, but no identified source license. Preserve the concept, not the code.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/mrmehar229/virtual-patient); [README](https://github.com/mrmehar229/virtual-patient#readme); review the pinned license/notice before importing.

### 43. [yusra-kk/clinical-case-practice-ai](https://github.com/yusra-kk/clinical-case-practice-ai)
- **Creator:** `yusra-kk`.
- **What it does:** Clinical reasoning simulator with four predefined patient cases, free-text interview, requested physical examination/testing and AI examiner feedback. Uses Gemini to play patient and examiner roles.
- **Code quality:** **Prototype.** Accessible and focused reference for keeping a hidden case in context; single-model prompting alone is not enough to guarantee medically consistent disclosure.
- **Reuse:** **High for game-loop inspiration; medium as architecture**. The small scripted case set makes it easier to see which state should be deterministic.
- **License:** **No license found** in common root files or README.


#### Added detailed-source dossier — 43

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: four authored cases, AI patient/examiner separation and deliberate disclosure of findings only when asked.
- **Additional integration/limitations:** Good pedagogical interaction design, but without an identified source license direct integration is restricted.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/yusra-kk/clinical-case-practice-ai); [README](https://github.com/yusra-kk/clinical-case-practice-ai#readme); review the pinned license/notice before importing.

### 44. [igembitsky/virtual-standardized-patient](https://github.com/igembitsky/virtual-standardized-patient)
- **Creator:** **Igor Gembitsky**.
- **What it does:** Local/offline-compatible simulated OSCE consultations. AI models handle patient dialogue, while clinician-authored case data determines the real findings, scenario clock and scoring. README reports eight cases adapted from published MedEdPORTAL educational materials.
- **Code quality:** **Promising–strong.** Clear boundary between LLM speech and deterministic clinical truth, documented developer workflow and visible CI/security automation. Live benchmark claims were not independently rerun.
- **Reuse:** **Very high.** One of the best architectural references for the game's **patient-facing conversation vs hidden-case authority** split; especially useful if local models are desired.
- **License:** **MIT for code — verified** ([LICENSE](https://github.com/igembitsky/virtual-standardized-patient/blob/main/LICENSE)). **Audit the source cases, adaptations, images and MedEdPORTAL terms separately**; a software MIT license does not automatically relicense published teaching cases.


#### Added detailed-source dossier — 44

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: offline Qwen/Ollama patient simulation with authored OSCE cases, clinician-delimited examination findings and grading.
- **Additional integration/limitations:** One of the best foundations for interview/medical-examination AI, particularly to avoid paid inference while prototyping.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/igembitsky/virtual-standardized-patient); [README](https://github.com/igembitsky/virtual-standardized-patient#readme); review the pinned license/notice before importing.

### 45. [clay-good/opensimlab](https://github.com/clay-good/opensimlab)
- **Creator:** **Clay Good**.
- **What it does:** Browser-native, offline-capable clinical simulation platform with bounded, closed-loop interventions, claimed 256 scenarios across 16 specialties, teaching examples, tutor, physiologic changes and debriefing.
- **Code quality:** **Promising–strong engineering signals.** `package.json` has TypeScript, Vitest, build gates, catalog verification, asset-license checking and quality scripts; still a new and ambitious project whose case/physiology accuracy must be independently checked.
- **Reuse:** **Very high for an overall diagnostic-game loop**, scenario registry, time progression, intervention evaluation and feedback. A realistic path is to adopt selected gameplay concepts/components rather than blindly fork the entire 256-scenario app.
- **License:** **MIT — verified** ([LICENSE](https://github.com/clay-good/opensimlab/blob/main/LICENSE)). Individual scenario content and third-party assets still need review.

**Clinical-correctness caveat:** the 256 count refers to registered scenarios across 16 specialties and is not evidence of 256 distinct laboratory assays. Check which are genuinely dynamic and which are authored lesson shells. No clinician sign-off was verified.


#### Added detailed-source dossier — 45

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: 256 clinical lessons across 16 specialties, case progression, modeled physiology, repeatable worked examples, reference-run debriefs and offline deployment.
- **Additional integration/limitations:** Good clinical scenario kernel, but does not deliver a full free-form hospital EHR. Its own documentation states unreviewed clinical content and no overall debrief score.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/clay-good/opensimlab); [README](https://github.com/clay-good/opensimlab#readme); review the pinned license/notice before importing.

### 46. [SamuelSchmidgall/AgentClinic](https://github.com/SamuelSchmidgall/AgentClinic)
- **Creators:** **Samuel Schmidgall** and research collaborators (including Rojin Ziaei, Carl Harris and others).
- **What it does:** Research benchmark for AI doctor–patient diagnostic encounters. Doctor, patient and evaluation roles, multimodal/vision possibilities, configurable model backends and curated case sources (MedQA, NEJM, restricted MIMIC-IV).
- **Code quality:** **Promising research benchmark; less suitable as a production game backend.** Good scientific framing and reproducibility intent, but codebase focuses on agent evaluation rather than persistence, game design or polished UI.
- **Reuse:** **High for evaluation methods and scripted patient-agent interactions; medium for core product code**. Strong inspiration for measuring diagnostic reasoning without confusing patient simulator and grading agent.
- **License:** **MIT for code — verified** ([LICENSE.txt](https://github.com/SamuelSchmidgall/AgentClinic/blob/main/LICENSE.txt)). **MIMIC-IV, NEJM and other case corpora have distinct access and redistribution restrictions**.


#### Added detailed-source dossier — 46

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: benchmark patient/doctor/measurement agents and multi-turn diagnosis with MedQA, NEJM and restricted MIMIC-IV case families.
- **Additional integration/limitations:** Useful automated agent benchmarking and test-ordering behavior; protect against ungrounded measurement-agent answers.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/SamuelSchmidgall/AgentClinic); [README](https://github.com/SamuelSchmidgall/AgentClinic#readme); review the pinned license/notice before importing.

### 47. [ZJUMAI/EvoPatient](https://github.com/ZJUMAI/EvoPatient)
- **Creators:** **ZJUMAI research team** and authors of *LLMs Can Simulate Standardized Patients via Agent Coevolution*.
- **What it does:** Research framework for evolving/improving patient agents through multi-agent doctor interactions, profile generation, retrieval, evaluation and simulations with specialist roles.
- **Code quality:** **Promising research prototype.** Structured agent architecture, paper and clear descriptions; likely integration and dataset requirements. Claims of high realism and fidelity need independent evaluation.
- **Reuse:** **Medium–high for patient-agent evaluation and behavior generation**, less compelling than the deterministic clinical-state design of Virtual Standardized Patient for game correctness.
- **License:** **Apache-2.0 stated in README, but no full root license file located.** **README-only / clarify exact grant and materials covered** before redistribution. [README](https://github.com/ZJUMAI/EvoPatient).


#### Added detailed-source dossier — 47

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: coevolving multi-agent patient/doctor setup, patient histories, specialists and RAG support.
- **Additional integration/limitations:** More research harness than player-facing game. Verify exact distribution license scope before importing any case data.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ZJUMAI/EvoPatient); [README](https://github.com/ZJUMAI/EvoPatient#readme); review the pinned license/notice before importing.

### 48. [DylanTombs/Multi-Agent-Hospital-Sim](https://github.com/DylanTombs/Multi-Agent-Hospital-Sim)
- **Creator:** **Dylan Tombs**.
- **What it does:** Hackathon-style live hospital AI-agent environment with patients, doctors, triage, staffing/beds, surge scenarios, movement on a map, metrics and LLM-generated explanations. React/TypeScript + FastAPI/WebSockets.
- **Code quality:** **Promising hackathon prototype.** A good visualization and agent/event separation for a demonstration, but not a medically validated, production-grade hospital simulation.
- **Reuse:** **Medium**: useful for multiple simultaneous patients, shifts, queueing and visible clinical staff, but the diagnostic game likely needs rich *one-patient* reasoning before large-scale hospital management.
- **License:** **MIT — verified** ([LICENSE](https://github.com/DylanTombs/Multi-Agent-Hospital-Sim/blob/main/LICENSE)).


#### Added detailed-source dossier — 48

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: Python/FastAPI plus React hospital floor simulation with patient and doctor agents, triage, resource counts and traffic.
- **Additional integration/limitations:** Useful for shift triage background events rather than the actual clinical investigation workstation.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/DylanTombs/Multi-Agent-Hospital-Sim); [README](https://github.com/DylanTombs/Multi-Agent-Hospital-Sim#readme); review the pinned license/notice before importing.

### 49. [josephmasson26/DiagnoseMe](https://github.com/josephmasson26/DiagnoseMe)
- **Creators:** Repository owner `josephmasson26`; the included copyright names **Namkhang Le**, and the README points to an earlier `NamkhangNLe/DiagnoseMe` project. Treat as a likely derivative; confirm contributors/provenance before crediting ownership.
- **What it does:** Earlier hackathon patient-chatbot application with Flask/OpenAI backend and Electron/JavaScript front end for diagnostic interview practice.
- **Code quality:** **Prototype/legacy.** Straightforward architecture but dated model/API assumptions, manual key setup and limited visible medical-state and test-ordering logic.
- **Reuse:** **Low–medium**: useful as an early AI-patient interface example; not competitive with the better modern case-authoritative systems.
- **License:** **MIT — verified** ([LICENSE](https://github.com/josephmasson26/DiagnoseMe/blob/main/LICENSE)), copyright **Namkhang Le**; retain attribution and check origin of borrowed material.


#### Added detailed-source dossier — 49

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: older hackathon patient-chat application using Flask, Electron and OpenAI-generated responses.
- **Additional integration/limitations:** Simple conversation UX reference; substantial overlap with better structured patient agents.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/josephmasson26/DiagnoseMe); [README](https://github.com/josephmasson26/DiagnoseMe#readme); review the pinned license/notice before importing.

### 50. [olab/Open-Labyrinth](https://github.com/olab/Open-Labyrinth)
- **Creator/maintainer:** **OpenLabyrinth / OLab project contributors**.
- **What it does:** Web authoring and playing of branching virtual-patient cases, with long-running medical education history. PHP/MySQL traditional web-server architecture.
- **Code quality:** **Legacy but established.** README describes version 3.3 as stable yet acknowledges installation fragility. V3 is no longer actively developed; the project points to [OLab4](https://github.com/olab/OLab4).
- **Reuse:** **High for branching case-authoring concepts; low–medium for direct reuse** due to older PHP platform and copyleft terms. Examine the maintained OLab4 separately if pursuing this direction.
- **License:** **GPL-3.0 stated in README and repository description.** No root GPL file was retrieved in the common-name check, but the project explicitly declares GPL-3; **confirm the exact file coverage** before integrating with a differently licensed game.


#### Added detailed-source dossier — 50

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: classic GPL virtual-patient editor/browser system running on PHP/Apache/MySQL.
- **Additional integration/limitations:** Long-standing branching authoring concepts; old deployment stack and copyleft complicate direct adoption.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/olab/Open-Labyrinth); [README](https://github.com/olab/Open-Labyrinth#readme); review the pinned license/notice before importing.

### 51. [bedriyan/medkit-app](https://github.com/bedriyan/medkit-app)
- **Creator:** `bedriyan`, described as a medical-doctor-turned-software-engineer and hackathon author.
- **What it does:** Voice-first emergency department/polyclinic simulator with AI patients, real-time speech, timed orders, exams and an attending grader; React/TypeScript + FastAPI, LiveKit and multiple paid speech/model services.
- **Code quality:** **Promising hackathon prototype.** Thoughtful client/server key separation, guided grading and test scripts, but built in three days and has external service dependencies. Not independently hardened.
- **Reuse:** **High product inspiration; no permission to copy code.** Relevant for voice turns, investigation turnaround, physician feedback and ER workflow.
- **License:** **Explicitly restricted**, README says **“Private — hackathon submission. Not licensed for redistribution.”** No permissive code license. [README](https://github.com/bedriyan/medkit-app).

**Canonical correction:** Explicit README no-redistribution instruction. Inspiration and evaluation do not give a code-import grant.


#### Added detailed-source dossier — 51

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: LiveKit-based voice ER/polyclinic simulation, multiple roles, triage, time delays, testing and an attending model with guideline registry.
- **Additional integration/limitations:** Strong voice/OSCE design reference but custom source rights not established, and hosted voice/model services impose costs.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/bedriyan/medkit-app); [README](https://github.com/bedriyan/medkit-app#readme); review the pinned license/notice before importing.
- **Reconciled license alert:** “No LICENSE found” in the later profile must **not** override the earlier audit: the Medkit README explicitly says private/not licensed for redistribution. Treat current code as restricted for source transplantation.

### 52. [MAXNORM8650/MedAgentSim](https://github.com/MAXNORM8650/MedAgentSim)
- **Creator/maintainer:** `MAXNORM8650` and research collaborators; associated with a MICCAI 2025 paper.
- **What it does:** Research simulated hospital/doctor–patient agent system for multi-turn clinical encounters, patient state, requested examinations, diagnostic decision-making and self-evolving multi-agent evaluation.
- **Code quality:** **Promising research-grade, not production-ready by default.** Paper and dataset offer evaluation value; integration, hallucination control and reproducibility would require a dedicated audit.
- **Reuse:** **Medium–high for research inspiration and agent benchmark design; license-constrained for product code**.
- **License:** **CC BY-NC-SA 4.0 — verified** ([LICENSE.txt](https://github.com/MAXNORM8650/MedAgentSim/blob/master/LICENSE.txt)). Noncommercial and share-alike restrictions; this is not a permissively licensed software component.


#### Added detailed-source dossier — 52

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: research multi-agent doctor/patient/measurement interactions, self-improvement and experience replay.
- **Additional integration/limitations:** Research/benchmark reference with CC BY-NC-SA restrictions; not a permissive library.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/MAXNORM8650/MedAgentSim); [README](https://github.com/MAXNORM8650/MedAgentSim#readme); review the pinned license/notice before importing.

### 53. [mohsaqr/rohySimulator](https://github.com/mohsaqr/rohySimulator)
- **Creator:** **Professor Mohammed Saqr** and contributors.
- **What it does:** Broad AI virtual-patient platform: clinical chat and multiple roles, dynamic vitals, ECG, investigations, medications, imaging/PACS, microscopy, 3D rooms, debriefing, analytics and optional multimodal interaction.
- **Code quality:** **Ambitious and promising, but not independently proven.** One of the closest overall feature matches to the proposed game; several integrated subsystems increase review, deployment and security complexity.
- **Reuse:** **Very high as a conceptual product reference; current source reuse requires written approval.** However, the historical **v2.9.12 root was MIT**: a focused license/provenance audit may identify older stand-alone MIT-licensed components worth extracting. The vendored `OyonR/` at that same tag was **already Carm-restricted**. Avoid copying newer implementation under the outdated site-wide MIT claim.
- **License:** **Current:** Custom `Carm Research License v1.4` — verified ([LICENSE](https://github.com/mohsaqr/rohySimulator/blob/main/LICENSE)). Research/education running and sharing is permitted within restrictions, but integration requires written permission. **Historical:** [v2.9.12](https://github.com/mohsaqr/rohySimulator/tree/v2.9.12) root LICENSE and package.json declared MIT, **while OyonR/LICENSE in the same tag was Carm**. [Relicensed at v2.9.14 on July 31, 2026](https://github.com/mohsaqr/rohySimulator/commit/84a35664f33e48871714e94427c66369d5317713). Official website still incorrectly advertises current work as MIT. The history offers a possible limited reuse pathway for proven older MIT-covered files only, not a blanket permission for the entire historic tree.

---

**Canonical correction:** The historically MIT first-party Rohy core and current Carm-restricted code must never be intermixed without a license review. Part VIII provides the full forensic timeline and security findings.


#### Added detailed-source dossier — 53

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Additional implementation findings:** README directly inspected: broad AI-patient, monitoring, investigations, 12-lead ECG, imaging/pathology, 3D bedside and educational debrief platform.
- **Additional integration/limitations:** Functionally closest all-in-one reference, but Carm Research license explicitly restricts repurposing and embedding without permission.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/mohsaqr/rohySimulator); [README](https://github.com/mohsaqr/rohySimulator#readme); review the pinned license/notice before importing.

# PART IV — ADDITIONAL 43 GITHUB REPOSITORIES (#54–96): DETAILED SCREENING

The entries below preserve every item newly found in the 96-repository expansion. These detailed screenings use the linked repository evidence and tables from the existing multihost audit; **integration notes are engineering hypotheses, not successful installs, API certifications or clinical validation**. Every entry links to the canonical repository.

## 54. [eth-medical-ai-lab/GTAgentClinic](https://github.com/eth-medical-ai-lab/GTAgentClinic)

**Recorded license/rights:** Apache-2.0 code; CC BY 4.0 cases.  **Screening decision:** Core contender.

**Capabilities and reuse:** 3D ED/OSCE game: dialogue, EHR, tests, dynamic time and debrief; compare as a possible complete base. Clinical validation pending.

**Engineering interpretation / investigation:** Compare the ED scene/action loop with Open Sim Lab by replaying the same case. Inspect the boundary between browser, NPC prompts, EHR, hidden case truth and scoring; read the case-content CC BY attribution requirements separately from Apache-licensed application code. The initial collection of cases has not received independent expert validation.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 54

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** A Node/browser-first 3D emergency-department simulation with first-, third-person and top-down control, agent-facing REST/MCP interfaces and an AgentChart electronic record. Browser graphics prefer WebGPU but document a WebGL2 fallback.
- **Features and medical behavior:** The current README describes 111 playable cases, with patient/family/nurse/consultant roles, order sets, investigation turnarounds, physiological drift, treatment effects and timed debriefs. An optional AI doctor can use the same clinical action surface as a human.
- **Potential integration (inference):** Run one neurological/endocrine multi-test case; examine how each lab and ECG derives from a hidden case state. Extract order/result and AI-agent interfaces only if the game remains maintainable without its 3D shell.
- **Validation and reuse constraints:** Apache-2.0 code and original assets; clinical cases are CC BY 4.0 with required attribution. Clinical validation is explicitly incomplete. Counts, tests and visual realism come from the README, not an independent run.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/eth-medical-ai-lab/GTAgentClinic); [README](https://github.com/eth-medical-ai-lab/GTAgentClinic#readme); review the pinned license/notice before importing.

## 55. [peterdoubell/Echosim](https://github.com/peterdoubell/Echosim)

**Recorded license/rights:** MIT.  **Screening decision:** Core echo candidate.

**Capabilities and reuse:** Browser 3D heart, ultrasound-like B-mode, Doppler, EF/calipers, 12-lead ECG and blinded questions; external clinical validation pending.

**Engineering interpretation / investigation:** Test whether clinical case settings can remotely specify rhythm, valve lesions, left ventricular function and pathology while retaining independent, blinded image acquisition. Assess probe angle/view changes, Doppler and caliper units. A 3D scene capable of making ultrasound-like images is not evidence of real anatomy or validated measurements.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 55

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Static-site JavaScript/three.js 3D heart with a signed-distance-field anatomical representation, a lumped closed-loop circulation, synthetic B-mode renderer and a synchronized 12-lead ECG.
- **Features and medical behavior:** Includes moving probe/standard echo views, Doppler, calculated EF and dimensions, calipers, structured reports, pathology controls, blind clinical questions and a BSE-oriented learning pathway. The repository supplies targeted verification scripts and a documented anatomy audit.
- **Potential integration (inference):** Use as an isolated examination workstation controlled by the game's hidden pathology/time state; block diagnostic settings and reports until the player earns or requests them. Compare synthetic loops with licensed real echo clips.
- **Validation and reuse constraints:** MIT code. Self-reported reference-range and automated checks do not establish clinical validity; the author explicitly calls for external expert assessment and validation of image/anatomical accuracy.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/peterdoubell/Echosim); [README](https://github.com/peterdoubell/Echosim#readme); review the pinned license/notice before importing.

## 56. [BioGearsEngine/core](https://github.com/BioGearsEngine/core)

**Recorded license/rights:** Apache-2.0 (README/organization).  **Screening decision:** R&D physiology.

**Capabilities and reuse:** Whole-body C++ physiology for coherent responses and interventions; complex build and bridge, validate specific outputs.

**Engineering interpretation / investigation:** Check build reproducibility, case-state serialization, validated model ranges, time-stepping, treatment/actions and bindings to the chosen web runtime. Compare with Kitware Pulse against an identical shock or pulmonary illness scenario. Do not assume the physiology engine provides correct image synthesis or arbitrary lab diagnoses.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 56

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Native C++ cross-platform physiology engine with compartment/circuit-based models, APIs for patient state and intervention progression, and supporting build toolchains. The README describes January 2025 BioGears 8.2.0 release notes.
- **Features and medical behavior:** Aims to model interdependent systems rather than output independent fake monitor traces. The ecosystem includes physiological assessments, clinical conditions, intervention actions and training-technology integrations.
- **Potential integration (inference):** Evaluate a small standalone service simulating shock, fluid response and blood gases; feed a browser monitor from serialized outputs. Compare explicitly against Kitware Pulse, a separately developed BioGears-derived fork.
- **Validation and reuse constraints:** Apache-2.0 is stated in its README, although the root path LICENSE was not returned in this pass. Native build, imperfect model coverage and domain validation are major costs. Do not assume all lab analytes are accurate in all disease regimes.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/BioGearsEngine/core); [README](https://github.com/BioGearsEngine/core#readme); review the pinned license/notice before importing.

## 57. [ihkarise/wisecases](https://github.com/ihkarise/wisecases)

**Recorded license/rights:** MIT.  **Screening decision:** Optional case editor.

**Capabilities and reuse:** Offline progressive case clues, authoring/import tools and reasoning feedback; more quiz-like than an unrestricted workup.

**Engineering interpretation / investigation:** Good case authoring/progressive clue ideas; assess versioning, how hidden facts are withheld, support for optional tests and whether case content is serializable independent of UI. Quiz-like guided flows may not support open-ended investigation without substantial changes.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 57

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** A lightweight browser progressive-clue application with a case schema, case-authoring studio and CSV/Excel/JSON ingestion. Offline-friendly deployments and Google Sheets data mode are documented.
- **Features and medical behavior:** The player submits differential hypotheses in stages; incorrect attempts trigger educational explanations, scoring/lives and additional evidence. The repository also documents automated logic and browser tests.
- **Potential integration (inference):** Borrow the case editor, import validation and explainable debrief concepts. Use authored pathways as the case-editor front end, not the only permitted investigation path in a free-form game.
- **Validation and reuse constraints:** MIT license verified in LICENSE. Its staged clue/quiz mechanics are narrower than the requested unrestricted ordering and evolving physiological state.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ihkarise/wisecases); [README](https://github.com/ihkarise/wisecases#readme); review the pinned license/notice before importing.

## 58. [mo374z/PatientsWithPersonality](https://github.com/mo374z/PatientsWithPersonality)

**Recorded license/rights:** MIT.  **Screening decision:** Core dialogue research.

**Capabilities and reuse:** Patient persona and selective disclosure framework; ideal source of ideas for realistic history-taking and difficult interviews.

**Engineering interpretation / investigation:** Focus on knowledge vs personality: case facts must be fixed; personality controls style, uncertainty, resistance, memory and disclosure, not truth. Evaluate repeated and adversarial patient questions and transcript replay, and measure whether the framework supports explicit per-fact permissions.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 58

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Python experimental patient-simulation framework with a shared comparison interface for several patient agent designs. Separates initialization of a latent patient role from per-turn disclosure and response generation.
- **Features and medical behavior:** Query-conditioned disclosure gates avoid volunteering the complete history; the model selects only fields that match the clinician's actual question. The framework studies controlled personality variation and similarity to human disclosure patterns.
- **Potential integration (inference):** Particularly suitable for the AI patient's 'knowable facts' filter: keep case truth server-side, select permitted facts from intent, then use a local/hosted LLM to phrase the answer. Add explicit memory and uncertainty controls.
- **Validation and reuse constraints:** MIT software license verified. Original studies and evaluation datasets have separate rules; a good benchmark result is not proof of accurate portrayal for psychiatric/neuroendocrine cases.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/mo374z/PatientsWithPersonality); [README](https://github.com/mo374z/PatientsWithPersonality#readme); review the pinned license/notice before importing.

## 59. [Sahandfer/PatientHub](https://github.com/Sahandfer/PatientHub)

**Recorded license/rights:** MIT.  **Screening decision:** Optional dialogue research.

**Capabilities and reuse:** Modular patient/client agents and evaluations; strong architecture reference, mental-health emphasis, not a full game.

**Engineering interpretation / investigation:** Consider for validating multi-agent interaction and quality of simulated patient behavior, especially if specialist or family agents will exist. Its mental-health emphasis makes it a secondary research source for medical workup rather than an investigation system.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 59

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Python CLI/research toolkit with configurable simulated clients, therapists, NPCs, evaluators, YAML prompts and saved sessions. Supports OpenAI-compatible endpoints and reusable agent scaffolds.
- **Features and medical behavior:** Provides commands to simulate conversations, create agents, evaluate recorded interactions and adapt patient characters. A documented emphasis is mental-health client behavior rather than medical examinations.
- **Potential integration (inference):** Useful for dialogue evaluation and realistic psychiatric interviews; less useful as the primary game engine. Port its conversation evaluation patterns, not the entire CLI and therapist abstraction.
- **Validation and reuse constraints:** MIT license verified. Models/API credentials and any research data are external. Clinical consistency and hallucination containment still require case-engine policy.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Sahandfer/PatientHub); [README](https://github.com/Sahandfer/PatientHub#readme); review the pinned license/notice before importing.

## 60. [MAGIC-AI4Med/DiagGym](https://github.com/MAGIC-AI4Med/DiagGym)

**Recorded license/rights:** CC BY-SA notice; nonstandard for software, verify.  **Screening decision:** Research / permission check.

**Capabilities and reuse:** Multi-turn diagnostic tool calls and conditional test-result generation; experimental world model, guard against fabricated contradictory results.

**Engineering interpretation / investigation:** Useful research on next-test selection and result prediction, but a generative tool-result model should not be installed as the authority of labs or imaging. Investigate the meaning of the CC BY-SA software notice before any redistribution; protect against arbitrary invented results and hidden-diagnosis leakage.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 60

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Research framework for reinforcement-learning diagnostic agents and a conditional examination-result world model. The README links external Hugging Face DiagGym/DiagAgent checkpoints and DiagBench benchmark data.
- **Features and medical behavior:** An agent chooses which additional exam to request from evolving case context, obtains synthetic findings, repeats, and decides when evidence is sufficient. The paper describes rubric-based multi-step evaluation.
- **Potential integration (inference):** Study as a benchmark for investigation selection, stop criteria and information gain. Run controlled contradictory-request tests before considering it for producing in-game evidence.
- **Validation and reuse constraints:** Root LICENSE is a terse CC BY-SA-style notice rather than a conventional software permission text; license scope requires expert inspection. The generator can hallucinate medically wrong or contradictory test results and should never become authoritative case truth.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/MAGIC-AI4Med/DiagGym); [README](https://github.com/MAGIC-AI4Med/DiagGym#readme); review the pinned license/notice before importing.

## 61. [HealthRex/SimEHR](https://github.com/HealthRex/SimEHR)

**Recorded license/rights:** Apache-2.0 code; CC BY 4.0 synthetic charts.  **Screening decision:** High-priority EHR.

**Capabilities and reuse:** Interactive chart review, orders, medications, notes, flowsheets and audit API; excellent EHR candidate, still a preview.

**Engineering interpretation / investigation:** Trial its `loadCase`, `getState`, `getAuditLog` and `resetState` application API. Measure the work needed to adapt arbitrary clinical case records, order timelines, duplicate test results, lab trending, notes and user navigation. Its sample preview is not proof it handles the game’s entire test catalog.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 61

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Browser EHR application with a canonical patient JSON model, separate episode/action state, an audit log and a documented `window.SimEHR` API. Built to let computer-use agents manipulate real UI controls.
- **Features and medical behavior:** The README describes chart review, vital-sign trends, laboratory/imaging/cardiology studies, clinician notes, medication orders with dose/route/frequency, patient messages, scheduling and a demonstrated chart task.
- **Potential integration (inference):** High-value candidate for the game's EHR and ordering interface. Implement an adapter translating game orders and released results into its chart schema, then verify chart panels cannot reveal uncollected or future findings.
- **Validation and reuse constraints:** Apache-2.0 root license verified; synthetic chart content is separately attributed in the prior audit. EHR UI and audit model are promising but clinical workflow correctness and accessibility have not been tested here.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/HealthRex/SimEHR); [README](https://github.com/HealthRex/SimEHR#readme); review the pinned license/notice before importing.

## 62. [janthoXO/AetioMed](https://github.com/janthoXO/AetioMed)

**Recorded license/rights:** No root LICENSE confirmed.  **Screening decision:** Study / permission check.

**Capabilities and reuse:** Blueprint-first synthetic cases with hidden diagnosis and blinded workup agent; potentially useful authoring pipeline.

**Engineering interpretation / investigation:** The blueprint-first and hidden-diagnosis authoring approach is valuable. Without a confirmed grant this stays a reference. Validate source-case provenance, schema stability and whether generation changes results when given identical inputs.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 62

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** TypeScript/Node self-hosted backend using LangGraph/LangChain with Ollama, Gemini and OpenAI-compatible inference. Outputs schema-constrained structured patient, presentation, anamnesis and procedure bundles via a REST API.
- **Features and medical behavior:** Uses an outline-first clinical blueprint, explicit consistency checks and a diagnostic-workup agent blinded to the actual diagnosis. The plan stage can introduce plausible alternatives and sequential investigations.
- **Potential integration (inference):** Promising *offline case authoring pipeline*, not a runtime patient simulator: export candidate cases for human review, freeze accepted truth and convert into the game schema. Its blinded investigator can generate training paths, not dictate actual player options.
- **Validation and reuse constraints:** No root LICENSE was found in checked path, so copying source is conditional. Plausible LLM-generated medical content is not necessarily correct, and local models need systematic validation.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/janthoXO/AetioMed); [README](https://github.com/janthoXO/AetioMed#readme); review the pinned license/notice before importing.

## 63. [dek924/PatientSim](https://github.com/dek924/PatientSim)

**Recorded license/rights:** No root LICENSE confirmed; data rights separate.  **Screening decision:** Study / permission check.

**Capabilities and reuse:** Research-grade patient personas and dialogue grounded in clinical datasets; check rights before code/data reuse.

**Engineering interpretation / investigation:** Compare patient-grounded dialogue to a deterministic case contract. Research dataset consent, provenance and redistribution. Use only as an architectural or evaluation study until software and content license rights are established.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 63

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Persona-driven medical consultation simulator distributed as Python experiment code, a package and a public Hugging Face demonstration. Research cases were derived using MIMIC-ED/MIMIC-IV clinical profiles.
- **Features and medical behavior:** Distinct persona controls include personality, language proficiency, recall and another conversational/cognitive dimension. The authors provide dialog-level and sentence-level evaluations of patient interactions.
- **Potential integration (inference):** Study persona diversity and difficult-history simulation; compare against PatientsWithPersonality. A real patient profile and a fictional public demo have different provenance and permissions.
- **Validation and reuse constraints:** No root LICENSE was identified in this review. MIMIC/PhysioNet data require credentialed access and carry strict use rules; the README says hosted model deployment constraints depend on that data provenance.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/dek924/PatientSim); [README](https://github.com/dek924/PatientSim#readme); review the pinned license/notice before importing.

## 64. [MadGAA-Lab/OSCE-Project](https://github.com/MadGAA-Lab/OSCE-Project)

**Recorded license/rights:** MIT-like permission text in LICENSE.  **Screening decision:** Optional evaluation.

**Capabilities and reuse:** Adversarial standardized-patient consultations and clinical evaluation; small specialty case set.

**Engineering interpretation / investigation:** Its adversarial standardized-patient evaluation ideas may expose overly compliant or answer-leaking simulated patients. Verify the exact original license text and how evaluation cases/ratings can be reproduced for the game’s rubric.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 64

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** AgentBeats/A2A evaluation environment for standardized-patient conversations, with adversarial role-driven patient agents and separate evaluated doctor agents.
- **Features and medical behavior:** The README describes 64 constructed patient persona configurations across MBTI labels, conditions and gender, communication/persuasion rubrics, safety evaluation and hidden patient persona information.
- **Potential integration (inference):** Use to stress-test whether the game's AI patient resists leading questions, leaks hidden details, unfairly changes its story, or responds safely to poor clinical communication.
- **Validation and reuse constraints:** Root LICENSE contains permissive MIT-like terms, but verify exact copyright text and any AgentBeats dependencies. Its medical scenarios focus on conversational evaluation rather than full labs/imaging or physiological engines.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/MadGAA-Lab/OSCE-Project); [README](https://github.com/MadGAA-Lab/OSCE-Project#readme); review the pinned license/notice before importing.

## 65. [ArneshBanerjee/open-residencyrl](https://github.com/ArneshBanerjee/open-residencyrl)

**Recorded license/rights:** Apache-2.0.  **Screening decision:** R&D evaluation.

**Capabilities and reuse:** Simulated longitudinal encounters, history interviews and structured rewards; RL harness, not a finished game.

**Engineering interpretation / investigation:** A longitudinal encounter/reward framework may help assess investigation quality rather than merely final-answer correctness. It is not a front-end game. Check how actions, progress and scoring are specified and whether reward signals align with clinically sensible behavior.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 65

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Open reimplementation of a published ResidencyRL training method, with deterministic mock, Ollama and OpenAI-compatible backends; text encounters are treated as episodes and evaluated through structured rubrics.
- **Features and medical behavior:** Scenarios are built from sampled demographics, behavioral traits, presenting complaints and complexity; the agent interviews, records SOAP/differential/plan, and is evaluated on the full trajectory. A mock backend allows reproducibility without API credits.
- **Potential integration (inference):** Reuse episode and reward design to test a game AI tutor or diagnostic bot; not an immediate game base. A useful experiment is whether an autonomous test-ordering agent operates within the same knowledge constraints as the player.
- **Validation and reuse constraints:** Apache-2.0 verified. It is an independent implementation of a method whose authors did not supply code, and its game-world fidelity is narrower than hospital investigations. Ensure grader does not learn hidden answers prematurely.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ArneshBanerjee/open-residencyrl); [README](https://github.com/ArneshBanerjee/open-residencyrl#readme); review the pinned license/notice before importing.

## 66. [Chelsea-19/Simu_Patient](https://github.com/Chelsea-19/Simu_Patient)

**Recorded license/rights:** MIT.  **Screening decision:** Optional case logic.

**Capabilities and reuse:** Application-controlled case truth, allowed tests and encounter state; good patterns for safe AI patient boundaries.

**Engineering interpretation / investigation:** Inspect how clinician-authored truth determines permitted tests and generated responses. This is a useful design comparison for authorization/knowledge-scope tests. Assess whether it handles timeline, repeat tests and treatment progression adequately.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 66

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Streamlit OSCE agent with YAML-authored cases, encounter-state machine, bounded clinical tools, explicit safety supervision and an action trace. It reserves ground truth for application state instead of the model.
- **Features and medical behavior:** Tools mediate examination and investigation findings, while the assistant controls only patient wording or bounded language actions. An authored safety rule can block an unsafe case completion, and the trace supports targeted remediation.
- **Potential integration (inference):** One of the most directly reusable patterns for our design: use explicit authorization for `order_test`, `view_result`, `examine` and `finish`; log exactly which facts the player was allowed to know at each turn.
- **Validation and reuse constraints:** MIT root license verified. The displayed chest-pain workflow is a demonstration, not proof of broad disease coverage or clinically validated safety rules.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Chelsea-19/Simu_Patient); [README](https://github.com/Chelsea-19/Simu_Patient#readme); review the pinned license/notice before importing.

## 67. [paultman/patientSimulator](https://github.com/paultman/patientSimulator)

**Recorded license/rights:** No LICENSE verified.  **Screening decision:** Study.

**Capabilities and reuse:** Speech/realtime virtual patient proof of concept; useful voice UX reference; API and permissions need checking.

**Engineering interpretation / investigation:** **New check in this consolidation:** the upstream repository has a root MIT LICENSE and explicit MIT text in README. It is primarily a narrow voice/text patient interview POC, including transient loss of consciousness cases and TF-IDF/keyword transcript scoring. Useful interview UX; not a complete workup engine.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 67

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Virtual-patient interview application with a condition database and an AI conversation layer; initial clinical focus is transient loss of consciousness, including cardiac/orthostatic/reflex syncope and non-syncopal mimics.
- **Features and medical behavior:** Supports randomized diagnosis selection, voice/text patient conversation and an evaluation rubric. The report distinguishes patient-knowledge limitations from the underlying chosen condition.
- **Potential integration (inference):** Useful for testing the exact neuro/psychiatric/endocrine overlap that motivated this game, particularly a syncope-versus-seizure tutorial. It is not a comprehensive investigations engine.
- **Validation and reuse constraints:** The README has a license section but a root license grant was not confirmed; inspect its exact terms. OpenAI service costs and generated-response consistency remain implementation considerations.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/paultman/patientSimulator); [README](https://github.com/paultman/patientSimulator#readme); review the pinned license/notice before importing.
- **Reconciled license alert:** The detailed source file repeats an older “no root LICENSE verified” finding; the earlier canonical consolidation separately identified an upstream MIT root LICENSE and README statement. Preserve the earlier positive finding, but pin the exact commit and inspect the grant/other assets before code import.

## 68. [drewhirschi/virtual-patient](https://github.com/drewhirschi/virtual-patient)

**Recorded license/rights:** No LICENSE verified.  **Screening decision:** Defer.

**Capabilities and reuse:** Gemini-powered patient interview demo with authored case records; overlaps stronger dialogue engines.

**Engineering interpretation / investigation:** A small LLM interview demonstration. Compare only its authoring and transcript handling if simpler candidates are wanted; there is no license-cleared code-import basis established in the previous audit.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 68

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Next.js 15/React/TypeScript patient-interview frontend with pre-authored patient data and Gemini-based conversation, styled with shadcn/Radix and Tailwind.
- **Features and medical behavior:** It uses a patient selector, responsive chat pane, case details and API-key-backed conversational roleplay. The README shows a small set of example patients, including parkinsonism and memory-loss presentations.
- **Potential integration (inference):** Low-effort UX reference for simple encounter layout and free-text patient questions; prefer more stateful patient engines for hiding test results and longitudinal behavior.
- **Validation and reuse constraints:** No root LICENSE confirmed in this review. Hosted Gemini use and small fixed case library are limitations.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/drewhirschi/virtual-patient); [README](https://github.com/drewhirschi/virtual-patient#readme); review the pinned license/notice before importing.

## 69. [MegaWiz-Dev-Team/vitals](https://github.com/MegaWiz-Dev-Team/vitals)

**Recorded license/rights:** AGPL-3.0.  **Screening decision:** Study / defer.

**Capabilities and reuse:** Deterministic emergency simulation and audit/replay; unusual Solana/blockchain architecture increases integration cost.

**Engineering interpretation / investigation:** Interesting event, audit and deterministic patient actions, but the AGPL terms and blockchain/storage design are disproportionate to the medical gameplay benefit. Potential study reference rather than direct reuse.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 69

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Rust deterministic emergency-case simulation/game tied to a Solana anchoring protocol and replayable audit events. README separates the publicly released Vitals code from private Embla infrastructure.
- **Features and medical behavior:** Cases advance over simulated time, actions are replayable and scoring/progression can be independently recomputed from an event trace. Opt-in blockchain anchoring is a distinctive feature, not necessary for medicine.
- **Potential integration (inference):** Borrow event-sourcing and reproducible case replays, not the chain-specific system. Its deterministic verification concept could make grading and regression testing robust.
- **Validation and reuse constraints:** AGPL-3.0-or-later plus separate commercial licensing reported by the README; additional private services limit independent reproducibility. Avoid importing its blockchain architecture.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/MegaWiz-Dev-Team/vitals); [README](https://github.com/MegaWiz-Dev-Team/vitals#readme); review the pinned license/notice before importing.

## 70. [tipcode-cpu/echocardiography-simulator](https://github.com/tipcode-cpu/echocardiography-simulator)

**Recorded license/rights:** No root LICENSE confirmed.  **Screening decision:** Study / permission check.

**Capabilities and reuse:** Small dependency-free browser tutorials for echocardiography concepts; no evidenced source-reuse grant.

**Engineering interpretation / investigation:** Small lightweight echo lessons are useful for teaching explanations and browser UI comparisons. Lack of confirmed code grant and limited evidence of pathology-rich procedural simulation block immediate adoption.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 70

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Six single-file HTML learning simulators, each running in a browser with no build step or runtime library. The repository describes itself as an English edition of an earlier Korean `echo-sim` tutorial project.
- **Features and medical behavior:** Topics include Doppler Nyquist/aliasing, PISA regurgitant quantification, image frame-rate tradeoffs, aortic stenosis grading, LVOT-derived cardiac output and diastolic assessment.
- **Potential integration (inference):** Good small examples for *manual echo interpretation tools* that accompany EchoSim or real cine clips. A player can adjust Doppler angle or trace measurements to understand how results are derived.
- **Validation and reuse constraints:** No root LICENSE found. The measured values and educational classifications are simplifications; permission is required before importing code.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/tipcode-cpu/echocardiography-simulator); [README](https://github.com/tipcode-cpu/echocardiography-simulator#readme); review the pinned license/notice before importing.

## 71. [sawaz/simpocus](https://github.com/sawaz/simpocus)

**Recorded license/rights:** No root LICENSE confirmed.  **Screening decision:** Defer.

**Capabilities and reuse:** Tiny low-fidelity POCUS prototype mapping probe/tags to images; modest utility and license uncertainty.

**Engineering interpretation / investigation:** A tagged phantom-to-probe image selector is a relevant cheap fallback for ultrasound learning but does not establish physiological image generation. Confirm whether code/license and case-image assets are reusable before doing more than studying behavior.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 71

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Low-fidelity Python/wx ultrasound teaching prototype explicitly based on EDUS2 scenario files; supports externally placed tags and an instructor remote controller.
- **Features and medical behavior:** Links ultrasound clips to scanned tags, allows replacement of the clip during a scenario and shows operator interaction on an instructor screen. This provides a physical-acquisition metaphor rather than synthetic ultrasound physics.
- **Potential integration (inference):** Relevant if the game later implements hand-guided POCUS; otherwise recorded image navigation within a browser viewer is faster and more portable.
- **Validation and reuse constraints:** Very small, older repository; no root LICENSE verified. EDUS2 scenario/asset licenses also matter.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/sawaz/simpocus); [README](https://github.com/sawaz/simpocus#readme); review the pinned license/notice before importing.

## 72. [tomzzzhang/Cardiology-app](https://github.com/tomzzzhang/Cardiology-app)

**Recorded license/rights:** AGPL-3.0.  **Screening decision:** R&D / copyleft review.

**Capabilities and reuse:** Heart/echo-focused interactive application; large codebase and AGPL network obligations demand consideration.

**Engineering interpretation / investigation:** AGPL web-application obligations require explicit review for networked deployment. Examine echo and cardiology controls in isolation before considering the substantial application integration cost.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 72

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Browser 3D educational cardiac anatomy tool using a content-pack model with saved probe poses, a 3D cut plane and matching illustrative echo wedges. The README explicitly labels its clinical content as draft/unvetted.
- **Features and medical behavior:** The prototype focuses on normal anatomy and pediatric trainee navigation between 3D position and 2D echo; its probe-relative plane and sweep design are more important than its limited pathology catalog.
- **Potential integration (inference):** Inspect the anatomy-independent pack schema if we want to distribute configurable echo studies. EchoSim currently offers a broader interactive physiological and pathology story.
- **Validation and reuse constraints:** AGPL-3.0 license verified. Root README says normal-heart technical slice is implemented but further view rail and sweeps are planned; do not claim complete pediatric pathology coverage.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/tomzzzhang/Cardiology-app); [README](https://github.com/tomzzzhang/Cardiology-app#readme); review the pinned license/notice before importing.

## 73. [neuropsychology/NeuroKit](https://github.com/neuropsychology/NeuroKit)

**Recorded license/rights:** MIT.  **Screening decision:** High-priority signal utility.

**Capabilities and reuse:** Python synthetic 12-lead ECG, PPG, respiration, EDA, EMG and processing; not a pathology-validated case simulator.

**Engineering interpretation / investigation:** Strong scientific offline signal test fixture utility for EKG/PPG/RSP/EDA/EMG. Validate supported channels carefully: a mathematically generated waveform is not by itself a verified clinical pathology. Use deterministic seeds and import into front-end signal viewers.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 73

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Scientific Python package for generating and analyzing physiological signals, especially ECG, respiratory effort, EDA, EMG and PPG. Does not require a 3D patient or interactive game engine.
- **Features and medical behavior:** Provides algorithms for simulation, cleaning, feature detection and physiological signal analysis; useful for deterministic seed-based offline signal assets and automated measurement checks.
- **Potential integration (inference):** Use behind an asset-build pipeline: generate candidate signals, export sampling rate/channel units, manually review morphology, and package only approved recordings. Do not infer a specific disease diagnosis from generic signal appearance.
- **Validation and reuse constraints:** MIT root LICENSE checked. MATLAB-like/synthetic morphology is not clinically validated against every condition, and Python dependencies are not a direct replacement for web live monitoring.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/neuropsychology/NeuroKit); README at the default path not confirmed; review the pinned license/notice before importing.

## 74. [MIT-LCP/wfdb-python](https://github.com/MIT-LCP/wfdb-python)

**Recorded license/rights:** MIT.  **Screening decision:** High-priority data utility.

**Capabilities and reuse:** Load and process physiological waveform databases; useful for real ECG/ICU recordings and annotations.

**Engineering interpretation / investigation:** High-value real-waveform import and signal records with sampling frequency and annotation metadata. Keep patient IDs and identifiers out of game packages; require data-specific rights and de-identification review.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 74

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** MIT PhysioNet-oriented Python library for physiological WaveForm DataBase (`WFDB`) files, metadata and annotations; provides established interfaces to read, write and display research signals.
- **Features and medical behavior:** Supports multi-channel recordings, physiologic signal header data and record annotations. Useful for bringing known signals from PhysioNet into a game with provenance and sampling units intact.
- **Potential integration (inference):** Use in offline ingestion jobs for ECG, arterial pressure or respiratory signals. Keep raw files and metadata separate from the display adapter so waveforms can be rechecked without regeneration.
- **Validation and reuse constraints:** MIT LICENSE verified. Library rights do not grant rights to any externally sourced ECG/ICU patient recordings, which may require separate attribution or credentialed access.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/MIT-LCP/wfdb-python); [README](https://github.com/MIT-LCP/wfdb-python#readme); review the pinned license/notice before importing.

## 75. [creatis-ULTIM/PyMUST](https://github.com/creatis-ULTIM/PyMUST)

**Recorded license/rights:** LGPL-2.1 LICENSE; setup.py says LGPL-3 (conflict!).  **Screening decision:** R&D / license check.

**Capabilities and reuse:** Simulated ultrasound RF/IQ, transducers and beamforming; not an interactive echo game; clarify conflicting license notices.

**Engineering interpretation / investigation:** Probe geometry, RF/IQ simulation and beamforming research for future ultrasound fidelity. The LGPL-2.1/3.0 metadata conflict must be resolved; generating arbitrary clinically believable echocardiograms is not guaranteed by ultrasound physics tooling alone.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 75

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Python port of the MATLAB MUST toolkit for synthetic ultrasound RF data, beamforming, Doppler and reconstruction; uses scientific numerical Python and examples/notebooks.
- **Features and medical behavior:** The authors document RF-to-IQ conversion, delay-and-sum beamforming, B-mode formation and Doppler processing, with references to SIMUS publications. It is a research library, not a playable echo workstation.
- **Potential integration (inference):** Good future tool if we want physics-derived synthetic B-mode artifacts from known 3D anatomy. Benchmark against real echo and ensure interactive performance before embedding in the game.
- **Validation and reuse constraints:** Root LICENSE says LGPL-2.1 while packaging metadata has been reported as LGPL-3; resolve version discrepancy. README warns of ongoing development and differences from MATLAB numerical results.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/creatis-ULTIM/PyMUST); [README](https://github.com/creatis-ULTIM/PyMUST#readme); review the pinned license/notice before importing.

## 76. [unioslo/USTB](https://github.com/unioslo/USTB)

**Recorded license/rights:** MIT.  **Screening decision:** Optional ultrasound research.

**Capabilities and reuse:** MATLAB/Python ultrasound beamforming toolbox; offline generation and imaging research rather than ready UI.

**Engineering interpretation / investigation:** Scientific ultrasound beamforming research and image reconstruction reference. Check MATLAB/Python dependencies, current sample datasets and numerical validation; likely best used offline rather than as a live browser dependency.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 76

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Research MATLAB UltraSound ToolBox for beamforming, processing and visualization of ultrasound data from multiple academic groups.
- **Features and medical behavior:** Offers a generalized beamforming framework, research demos and documentation on different processing methods. Its README explicitly identifies an official Bitbucket mirror of the GitHub source.
- **Potential integration (inference):** Useful for precomputing ultrasound reference images, benchmarking synthetic reconstruction and acquiring methods ideas. Not a game frontend or arbitrary pathology generator.
- **Validation and reuse constraints:** MIT LICENSE verified; datasets, specific beamformers and published methods have separate citation requirements. **Official alternate host:** https://bitbucket.org/ustb/ustb.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/unioslo/USTB); [README](https://github.com/unioslo/USTB#readme); review the pinned license/notice before importing.

## 77. [ingle/ultrasound-simulation](https://github.com/ingle/ultrasound-simulation)

**Recorded license/rights:** Modified MIT per README; verify text.  **Screening decision:** R&D.

**Capabilities and reuse:** Older frequency-domain medical B-mode ultrasound generation; check source provenance and modifications.

**Engineering interpretation / investigation:** A legacy frequency-domain B-mode simulation. Evaluate whether its outputs add learning value beyond EchoSim or licensed recorded clips, and clarify the stated modified MIT terms before copying.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 77

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Older numerical ultrasound simulator focused on B-mode generation from acoustic scatterer/reflection assumptions. Prior audit identifies modified MIT-like distribution language.
- **Features and medical behavior:** It is a specialized signal/image synthesis proof of concept rather than a contemporary patient-specific ultrasound simulator or echo teaching workstation.
- **Potential integration (inference):** Only worth revisiting if EchoSim or PyMUST leaves a clearly defined gap in frequency-domain image formation. A project-specific build and visual test is required.
- **Validation and reuse constraints:** README.md was not found through the default path in this verification pass; confirm source description, actual license, dependencies and reproducibility before adoption.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ingle/ultrasound-simulation); README at the default path not confirmed; review the pinned license/notice before importing.

## 78. [CeBiDa/ECG-Format-Converter](https://github.com/CeBiDa/ECG-Format-Converter)

**Recorded license/rights:** MIT (LICENSE.md).  **Screening decision:** Optional ECG interoperability.

**Capabilities and reuse:** Convert ECG/WFDB/CSV/DICOM-waveform/HL7 XML formats for investigation assets.

**Engineering interpretation / investigation:** Potential standardized ingestion bridge between multiple ECG file formats and 12-lead study storage. Test preservation of units, lead labeling, sample rates, start times and any manufacturer-specific metadata.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 78

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Python package and cross-platform GUI for reading, transforming and exporting 12-lead ECGs across multiple formats, including CSV, WFDB, MATLAB, DICOM waveforms and HL7 aECG.
- **Features and medical behavior:** The optional pipeline includes filters, resampling, pacemaker spikes, limb-lead derivation, waveform visualization and metadata summaries. It can export aligned investigations for a consistent game viewer.
- **Potential integration (inference):** Excellent build-time ingestion tool to normalize real/licensed ECGs and reduce manual cleanup. Preserve original traces; derived leads and filtering must be labeled rather than mistaken for raw acquisition.
- **Validation and reuse constraints:** MIT LICENSE.md verified. External recordings and any third-party codecs have separate rights. Anonymization must be audited before using real clinical data; filters can erase meaningful morphology.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/CeBiDa/ECG-Format-Converter); [README](https://github.com/CeBiDa/ECG-Format-Converter#readme); review the pinned license/notice before importing.

## 79. [lavrentiy/meridian](https://github.com/lavrentiy/meridian)

**Recorded license/rights:** MIT.  **Screening decision:** Optional imaging alternative.

**Capabilities and reuse:** Small offline browser DICOM MPR/3D viewer; consider for compact imaging screen, check clinical fidelity.

**Engineering interpretation / investigation:** Compact viewer alternative when loading bundled DICOM studies locally is more important than full OHIF PACS workflow. Check MPR orientation, transfer-syntax support, pixel scaling and packaging tests with actual cases.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 79

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Local-first DICOM browser workstation using client-side parsing and WebGL2 rendering, with no application backend. The README documents linked acquired slices, MPR, volume view and explicit image-provenance labels.
- **Features and medical behavior:** Supports measurement rulers, window/level presets, crosshair navigation, local file opening and several dataset layouts. Labels distinguish acquired frames from reconstructed and rendered images.
- **Potential integration (inference):** Strong lightweight challenger to full OHIF for a single-player radiology case, especially if we ship approved DICOM studies bundled with the game.
- **Validation and reuse constraints:** MIT LICENSE verified. The maintainer flags educational/non-clinical use. Test difficult DICOM transfer syntaxes, oblique series and phone performance before substituting for OHIF.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/lavrentiy/meridian); [README](https://github.com/lavrentiy/meridian#readme); review the pinned license/notice before importing.

## 80. [thulefog/circinus](https://github.com/thulefog/circinus)

**Recorded license/rights:** MIT claimed in README; root LICENSE not seen.  **Screening decision:** Optional imaging alternative.

**Capabilities and reuse:** Web DICOM/NIfTI MPR and 3D volume visualization; independently verify license distribution.

**Engineering interpretation / investigation:** Browser DICOM/NIfTI MPR and volume imaging is attractive, but its MIT claim is from README and root grant needs inspection. Compare compatibility and developer effort against OHIF, VolView and Meridian.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 80

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Browser dataset navigator built on Cornerstone3D with NIfTI parsing and patient/study/series navigation. The README describes client-side Web Worker loading and GPU volume rendering.
- **Features and medical behavior:** Offers orthogonal MPR, interactive 3D volume rendering, metadata panels and windowing. Positioned as a neuro/thoracic research viewing proof of concept.
- **Potential integration (inference):** Worth comparing with Meridian for compact neurological MRI support; advantage is NIfTI alongside DICOM, and dependency on established Cornerstone primitives.
- **Validation and reuse constraints:** README contains an MIT claim but a root LICENSE was not found. Explicitly described as a concept proof; verify actual notices and supported codecs before copying source.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/thulefog/circinus); [README](https://github.com/thulefog/circinus#readme); review the pinned license/notice before importing.

## 81. [rii-mango/Papaya](https://github.com/rii-mango/Papaya)

**Recorded license/rights:** BSD-style project terms; no clinical-use claim.  **Screening decision:** Optional legacy viewer.

**Capabilities and reuse:** Browser NIfTI/DICOM viewer; lighter than OHIF, older technical architecture.

**Engineering interpretation / investigation:** Legacy light imaging viewer, useful for NIfTI or simplified studies. Compare supported file codecs, orientation and measurement tools against modern Cornerstone3D; verify the exact BSD-style legal terms.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 81

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Mature pure-JavaScript research image viewer for DICOM/NIfTI, overlays, atlases, surface meshes and DTI; configurable for static/offline deployment.
- **Features and medical behavior:** Its architecture predates current Cornerstone3D but can support compact MRI/neuroimaging experiences without a full PACS application.
- **Potential integration (inference):** Use as a fallback for simple NIfTI visualizations or embedded educational views, not as the first choice for a modern full clinical PACS.
- **Validation and reuse constraints:** BSD-style terms verified at root (including non-clinical-use disclaimer). Review older browser dependencies, compressed syntax compatibility and maintenance before integration.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/rii-mango/Papaya); [README](https://github.com/rii-mango/Papaya#readme); review the pinned license/notice before importing.

## 82. [ivmartel/dwv](https://github.com/ivmartel/dwv)

**Recorded license/rights:** GPL-3.0 (license.txt).  **Screening decision:** Optional / copyleft review.

**Capabilities and reuse:** Embeddable DICOM Web Viewer with imaging tools; GPL obligations for distributed derivatives.

**Engineering interpretation / investigation:** Correction: GPL-3.0, not the MIT erroneously claimed in an earlier broad report. Embedding or distributing derivatives needs copyleft review; possible architectural alternative only if its compact UI is materially beneficial.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 82

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** HTML5 DICOM Web Viewer with a long-established JavaScript codebase and medical image viewing tools; intended to embed DICOM rendering in web applications.
- **Features and medical behavior:** Provides alternative image navigation/windowing strategies to OHIF and Cornerstone, and helps compare the total weight of medical image libraries.
- **Potential integration (inference):** Evaluate only when the chosen browser stack needs a simpler DICOM-oriented toolset; no reason to duplicate fully installed OHIF in the first game build.
- **Validation and reuse constraints:** Root `license.txt` explicitly contains GPL-3.0 (contrary to a prior report's MIT claim); evaluate distribution/coupling obligations. The missing root README.md in API lookup does not invalidate the repository.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ivmartel/dwv); README at the default path not confirmed; review the pinned license/notice before importing.

## 83. [ImagingDataCommons/slim](https://github.com/ImagingDataCommons/slim)

**Recorded license/rights:** Apache-2.0.  **Screening decision:** Optional pathology viewer.

**Capabilities and reuse:** DICOM whole-slide digital pathology viewer and annotations; complement OpenSeadragon.

**Engineering interpretation / investigation:** Useful whole-slide DICOM pathology and annotations, rather than ordinary CT/MRI. Could pair with OpenSeadragon if pathology becomes a playable discipline. Investigate color/profile, pyramid/tiles and specimen metadata support.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 83

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Client-side web microscopy application built on DICOM microscopy viewer libraries, connected to standard DICOMweb services. Designed for interoperable whole-slide pathology analysis.
- **Features and medical behavior:** Supports whole-slide navigation, high-resolution tiled imagery, image-derived annotations, stain channels and outputs in standard DICOM representations.
- **Potential integration (inference):** Ideal later pathology workstation where players zoom across a biopsy, identify regions and formulate findings without a prewritten report. Run against appropriately licensed slides and a read-only DICOMweb backend.
- **Validation and reuse constraints:** Apache-2.0 verified; much more infrastructure required than OpenSeadragon alone. Model-derived tissue annotations and real slides require their own attribution and privacy checks.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/ImagingDataCommons/slim); [README](https://github.com/ImagingDataCommons/slim#readme); review the pinned license/notice before importing.

## 84. [tanjera/infirmary-integrated-ehr](https://github.com/tanjera/infirmary-integrated-ehr)

**Recorded license/rights:** License not verified in root.  **Screening decision:** Study / verify.

**Capabilities and reuse:** Separate inpatient EHR simulator companion to Infirmary Integrated; check rights separately from parent project.

**Engineering interpretation / investigation:** A separate EHR companion to Infirmary Integrated, not automatically the same code license. Inspect root grant independently and compare with SimEHR before attempting cross-platform UI transplantation.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 84

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Companion repository associated with Infirmary Integrated's inpatient record UI. Potentially useful for reviewing chart workflow and how simulated devices feed longitudinal notes.
- **Features and medical behavior:** The prior audit establishes its separate repository identity, but the default README.md and root license file were not accessible in this verification pass; avoid claiming a current runnable architecture.
- **Potential integration (inference):** Treat this as a research lead while SimEHR and GTAgentClinic offer more clearly documented EHR APIs. Before adoption inspect the actual branch, source tree and deployment instructions.
- **Validation and reuse constraints:** **Evidence limited**: repository exists, but a README/license fetch failed at the common paths. Its parent project's Apache license does not automatically grant rights to this distinct repository.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/tanjera/infirmary-integrated-ehr); README at the default path not confirmed; review the pinned license/notice before importing.

## 85. [google/simhospital](https://github.com/google/simhospital)

**Recorded license/rights:** Apache-2.0; archived.  **Screening decision:** Defer.

**Capabilities and reuse:** Synthetic hospital/EHR message-flow simulator; useful integration research but archived.

**Engineering interpretation / investigation:** Archived synthetic hospital/EHR messaging is relevant for data/schema realism or interface simulations, but an archived research system should not be selected as a new dependency without a strong and specific use case.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 85

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Google's archived Simulated Hospital generates realistic but artificial HL7v2 event streams to exercise hospital integration and clinical-message ingestion.
- **Features and medical behavior:** Clinical pathways model admission, investigation orders and resulting messages, emitted to console, text, or a network MLLP endpoint. Not an interactive doctor roleplaying game.
- **Potential integration (inference):** Useful for integration tests if our backend needs interoperable order/result messaging, or to stress the correctness of event timestamps and patient identifiers.
- **Validation and reuse constraints:** Apache-2.0 verified, but GitHub marks the project archived. HL7 event validity does not imply medically plausible diagnosis or biochemical values.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/google/simhospital); [README](https://github.com/google/simhospital#readme); review the pinned license/notice before importing.

## 86. [Alp-creator/medphys-lab](https://github.com/Alp-creator/medphys-lab)

**Recorded license/rights:** MIT.  **Screening decision:** Optional imaging pedagogy.

**Capabilities and reuse:** Unity medical physics game with X-ray/CT/MRI/PET lessons; teaching mechanics more than patient-case reading.

**Engineering interpretation / investigation:** Illustrates medical physics concepts in an interactive game. It should not be confused with a complete case-linked radiology viewer, and any instructional image assets need separate evaluation.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 86

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Unity 6 educational medical-physics game, with a navigable teaching center, 36 lessons and interactive labs covering CT, MRI, X-ray, PET/nuclear medicine, radiotherapy and radiation protection.
- **Features and medical behavior:** Offers physics-informed demonstrations, NIST-related material and an educational case queue; desktop Windows and Android binaries are described by the README.
- **Potential integration (inference):** Use imaging teaching controls as inspiration, such as showing how CT contrast/windowing or MRI acquisition parameters alter images. Not a patient DICOM interpretation workstation.
- **Validation and reuse constraints:** MIT verified. Author-stated physical benchmarks are not a complete clinical modality validation, and porting Unity interactions into a web-based game would cost time.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Alp-creator/medphys-lab); [README](https://github.com/Alp-creator/medphys-lab#readme); review the pinned license/notice before importing.

## 87. [micaalle/CT-VR-App](https://github.com/micaalle/CT-VR-App)

**Recorded license/rights:** No root LICENSE confirmed.  **Screening decision:** Study.

**Capabilities and reuse:** VR medical CT anatomy navigation project; no reliable grant for copying source/assets found.

**Engineering interpretation / investigation:** Useful CT anatomy and VR ideas but code/asset grant unclear. If true 3D radiology teaching becomes central, use this as a conceptual comparator rather than core production code.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 87

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Unity 6/OpenXR VR education project for identifying anatomy and implants in 3D models derived from CT, with backend and 3D segmentation tools.
- **Features and medical behavior:** The project used UCF medical CT data, but the README clearly says all patient data was removed from the public repository because the university owns it.
- **Potential integration (inference):** Conceptual reference for a 3D anatomy mode and interactive implanted-device identification; not a source of redistributable CT cases.
- **Validation and reuse constraints:** No root LICENSE verified and original CT source data intentionally unavailable. Do not infer rights to copy any assets or reconstruct the absent dataset.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/micaalle/CT-VR-App); [README](https://github.com/micaalle/CT-VR-App#readme); review the pinned license/notice before importing.

## 88. [AdvancedModularManikin/physiology-manager](https://github.com/AdvancedModularManikin/physiology-manager)

**Recorded license/rights:** CC BY 4.0 LICENSE.md; unusual for code.  **Screening decision:** R&D / license check.

**Capabilities and reuse:** Physiology orchestration around BioGears; heavy native framework and licensing follow-up.

**Engineering interpretation / investigation:** Model orchestration could inform BioGears/Pulse adapters. Creative Commons license treatment of actual software needs legal review and native dependency burden is high.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 88

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Modular physiology-manager service from the MoHSES/Advanced Modular Manikin framework. The README explicitly depends on BioGears 8.1.0+ and a MoHSES standard library using FastRTPS/FastCDR.
- **Features and medical behavior:** Its role is control/orchestration of a separate physiology engine, not independent medical modeling; native dependencies and middleware provide hardware/simulator integration.
- **Potential integration (inference):** Research adapter patterns if connecting BioGears to other game services, but a custom small HTTP/IPC bridge may be much easier for the first web prototype.
- **Validation and reuse constraints:** LICENSE.md uses CC BY 4.0 for code, which is unusual; verify contributor and transitive project terms before adoption. No runtime/clinical validation was performed.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/AdvancedModularManikin/physiology-manager); [README](https://github.com/AdvancedModularManikin/physiology-manager#readme); review the pinned license/notice before importing.

## 89. [areatu/SonoForge](https://github.com/areatu/SonoForge)

**Recorded license/rights:** GPL-3.0.  **Screening decision:** Optional / copyleft review.

**Capabilities and reuse:** Desktop echocardiography measurements, reporting and DICOM analysis; not a procedural echo simulator.

**Engineering interpretation / investigation:** Strong differentiation: it measures/reports existing echo, it does not synthesize echocardiographic pathology. GPL-3.0 distribution review required. Potentially valuable for designing player measurement exercises.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 89

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Python 3.11+ offline-friendly echocardiography measurement and reporting workstation with DICOM viewing, Doppler/vascular tools and a portable presentation edition.
- **Features and medical behavior:** Provides area/length/caliper measurement, EF-related workflows, DICOM study comparison, reporting templates, export to PDF/CSV/JSON and configurable reference tables. Recent README outlines multiple image-analysis and visualization improvements.
- **Potential integration (inference):** Useful for designing a serious interpretive report, potentially as a reference for manually measuring a provided echo. It is not an interactive ultrasound-from-3D pathology generator.
- **Validation and reuse constraints:** GPL-3.0 confirmed at root. Data rights and segmenter/model weights must be audited separately; desktop Python stack increases integration cost.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/areatu/SonoForge); [README](https://github.com/areatu/SonoForge#readme); review the pinned license/notice before importing.

## 90. [Heigvd/mimms](https://github.com/Heigvd/mimms)

**Recorded license/rights:** No root LICENSE confirmed.  **Screening decision:** Study.

**Capabilities and reuse:** Major-incident medical simulation/game model; event/time/severity ideas, license requires inspection.

**Engineering interpretation / investigation:** Mass-casualty triage/incident time mechanics are a possible later addition; outside the focused one-patient reasoning loop. Lack of verified license is a firm no-copy gate.

**Stop condition:** Do not import code, model weights, copied data, or embedded recordings into a distributable game until the exact file-level license, upstream rights and dependency obligations have been resolved at a pinned commit.


### Added detailed-source dossier — 90

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** MIMMS is a major-incident medical management serious-game scenario package for the Wegas authoring platform, with separate common scripts, base scenario and model assets.
- **Features and medical behavior:** The README focuses on visibility rights, scenario packaging, page scripts, shared variables and reproducible patches of active simulation models.
- **Potential integration (inference):** Not a diagnosis simulator, but a useful reference for scenario composition, hidden/public variable permissions and event-driven mass-casualty management.
- **Validation and reuse constraints:** No root LICENSE confirmed; verify game assets, diagrams, maps and Wegas-specific dependencies. Reuse patterns only unless permission is established.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Heigvd/mimms); [README](https://github.com/Heigvd/mimms#readme); review the pinned license/notice before importing.

## 91. [Heigvd/Wegas](https://github.com/Heigvd/Wegas)

**Recorded license/rights:** MIT per README; check license file.  **Screening decision:** Optional authoring platform.

**Capabilities and reuse:** Generic serious-game authoring platform used in medical incident research; larger Java/web stack.

**Engineering interpretation / investigation:** General-purpose serious-game authoring is an option if extensive branching courses are desired. Large Java/web stack versus a focused game core; exact source license and long-term maintenance need review.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 91

**Deep-source verification note (19 November 2026):** **P — prior audit or limited direct README evidence**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Wegas is a larger Java/web serious-game platform, including narrative/game authoring. The audit identifies it as the authoring environment associated with MIMMS.
- **Features and medical behavior:** It is designed for multiple cases/roles and persistent game models rather than for displaying clinical signals. Could inform a scenario editor's variable visibility and deployment conventions.
- **Potential integration (inference):** A broad platform might be excessive compared with a bespoke JSON/YAML scenario system. Review only if authoring and education-management needs become complex.
- **Validation and reuse constraints:** No default README.md/root LICENSE could be retrieved in this pass, so the prior audit's MIT assertion remains **unverified**; do not import code until rights are confirmed.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/Heigvd/Wegas); README at the default path not confirmed; review the pinned license/notice before importing.

## 92. [anddegilevich/CPRSimulator](https://github.com/anddegilevich/CPRSimulator)

**Recorded license/rights:** CC0-1.0 per GitHub.  **Screening decision:** Optional training game.

**Capabilities and reuse:** Unity CPR/defibrillation training game; focused intervention practice rather than diagnostics.

**Engineering interpretation / investigation:** CPR/defibrillation practice could become a case-specific minigame. It is not a diagnostic case foundation, and the CC0 status should be confirmed for each third-party animation or sound asset.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 92

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Unity VR CPR teaching application built around a virtual cardiac-arrest scenario, physical compression practice and an assessment/quiz mode.
- **Features and medical behavior:** Focuses on compression depth, rhythm and sequence of CPR actions rather than differentiating etiologies through laboratory and imaging investigations.
- **Potential integration (inference):** Later resuscitation mini-game reference; independently calculate physiological consequences before coupling action results into the game's clinical engine.
- **Validation and reuse constraints:** Prior audit reported CC0, but the root file is a Creative Commons legal text; verify exact CC version and any separate Unity store/VR assets. Not a validated treatment trainer.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/anddegilevich/CPRSimulator); [README](https://github.com/anddegilevich/CPRSimulator#readme); review the pinned license/notice before importing.

## 93. [02developer/yapper](https://github.com/02developer/yapper)

**Recorded license/rights:** BSD-style custom terms in LICENSE.  **Screening decision:** Optional communication UX.

**Capabilities and reuse:** Interview/communication training game; useful interactions, substantial non-code assets.

**Engineering interpretation / investigation:** Clinical communication training as supplementary interview UX. Review unusual BSD-style custom license terms and third-party media before transplanting interaction patterns.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 93

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Java desktop patient-interview game with intentionally game-like pixel-art visuals and time-limited conversations, designed for medical and nursing students.
- **Features and medical behavior:** Includes a patient actor driven by a small language model, case background notes and session timers. The README also describes a distributable JAR.
- **Potential integration (inference):** Useful inspiration for low-friction player engagement, time pressure, and a conversational approach instead of traditional static forms. Limited as a realistic hospital investigation engine.
- **Validation and reuse constraints:** Root LICENSE is a customized BSD-style notice, not automatically equivalent to standard BSD-3-Clause; read exact obligations, asset copyrights and trained model rules before reuse.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/02developer/yapper); [README](https://github.com/02developer/yapper#readme); review the pinned license/notice before importing.

## 94. [pydicom/pydicom](https://github.com/pydicom/pydicom)

**Recorded license/rights:** MIT for most code; exceptions in LICENSE.  **Screening decision:** Core DICOM backend utility.

**Capabilities and reuse:** Python DICOM reading/writing and metadata, for organizing and delivering real study assets.

**Engineering interpretation / investigation:** Canonical Python DICOM preprocessing library for indexing de-identified studies, deleting identifiers, generating manifests and validating study metadata. It will not render DICOM by itself.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 94

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** General-purpose pure Python DICOM dataset parser and writer, with optional NumPy and compression backends. Supports DICOM metadata editing and pixel data access.
- **Features and medical behavior:** Essential for building synthetic or de-identified study bundles, validating scan IDs, anonymizing metadata carefully and preparing browser-viewer feeds.
- **Potential integration (inference):** Use on an offline ingestion service that produces a DICOM manifest and internal case-to-study mapping. Keep original copies, verify modality/study associations and test pixel data before shipping assets.
- **Validation and reuse constraints:** Core MIT license verified with component exceptions documented in LICENSE; **not a medical image viewer**. Proper DICOM de-identification is more complex than simply deleting names.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/pydicom/pydicom); [README](https://github.com/pydicom/pydicom#readme); review the pinned license/notice before importing.

## 95. [sadc-lab/pulse_reliability_atlas](https://github.com/sadc-lab/pulse_reliability_atlas)

**Recorded license/rights:** Apache-2.0.  **Screening decision:** R&D validation.

**Capabilities and reuse:** Reproducible sensitivity/failure-mode audit for Pulse Physiology Engine; helps test realism boundaries.

**Engineering interpretation / investigation:** Useful reproducible fault/sensitivity atlas for Kitware Pulse model reliability. Investigate whether its benchmarks cover physiological states required by the game and whether failure modes can become regression tests.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 95

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Research-grade reproducibility and sensitivity audit for Kitware Pulse physiology, with pinned engine version, parameter sweeps, error classification and generated validation figures.
- **Features and medical behavior:** The README describes a 1,280-run systematic sweep and an atlas identifying where modeled behavior satisfies its criteria and where solvers or physiological outputs fail. Version-specific results are emphasized.
- **Potential integration (inference):** A critical safety/evidence companion if we ever use Pulse for generating shock, renal or respiratory case results; use it to select supported parameter regimes and write our own regression tests.
- **Validation and reuse constraints:** Apache-2.0 verified. Claims are limited to Pulse v4.3.1 (and noted equivalent build), not all current Pulse versions or all diagnoses. Avoid interpreting benchmark agreement as universal validity.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/sadc-lab/pulse_reliability_atlas); [README](https://github.com/sadc-lab/pulse_reliability_atlas#readme); review the pinned license/notice before importing.

## 96. [OHIF/ohif-core](https://github.com/OHIF/ohif-core)

**Recorded license/rights:** MIT; archived.  **Screening decision:** Legacy dependency / defer.

**Capabilities and reuse:** Reusable functions from earlier OHIF architecture; current OHIF/Cornerstone preferred.

**Engineering interpretation / investigation:** Legacy archived OHIF module package. Favor maintained OHIF Viewers/Cornerstone3D; avoid importing an obsolete core without a specific compatibility requirement.

**Before adoption:** Pin a revision; run documented tests and a minimal end-to-end proof; audit third-party assets and medically important edge cases. The license alone does not certify correctness.


### Added detailed-source dossier — 96

**Deep-source verification note (19 November 2026):** **R — README examined this revision**. This records source review, not a successful installation, clinical validation or complete license audit.

- **Implementation and architecture:** Older OHIF core JavaScript library containing common viewer services such as hotkeys, DICOMweb helpers, hanging protocols, study/measurement state and plugin-oriented utilities.
- **Features and medical behavior:** Its README explicitly states the repository is archived and points to the monorepo path `OHIF/Viewers/platform/core` as the active continuation.
- **Potential integration (inference):** Use as a historical architecture reference only; take current components from OHIF/Viewers or Cornerstone3D rather than pinning this archived package.
- **Validation and reuse constraints:** MIT. Importing duplicate legacy code introduces unnecessary version drift and dependency risk.
- **Direct repository/README evidence:** [repository and source tree](https://github.com/OHIF/ohif-core); [README](https://github.com/OHIF/ohif-core#readme); review the pinned license/notice before importing.

# PART V — NON-GITHUB PRIMARY SOURCES, MODEL REPOSITORIES, DATASETS AND MIRRORS

This part transcribes the research and source/relationship ledger of the multihost verified audit. Project relationships matter: different platform URLs are not necessarily different software. Hugging Face weights, Spaces, datasets and checkpoints are separated from executable simulator code. The original `96 GitHub + 7 GitLab + 6 HF code/model + 2 HF datasets + 1 Mercurial` count is preserved exactly.

**Method.** Searched for canonical upstream projects, genuine alternate mirrors, and new non-GitHub codebases. Included licenses only when grounded in project/readme/LICENSE statements or identified metadata. Where direct browsing was blocked, the uncertainty remains explicit. Research checked 19 Nov 2026; do not infer a repo's newest commit from an indexed search date.

### A. GitLab — FOSS candidates and relevant simulation code

| ID | Canonical repository | License evidence | Relationship | Usefulness for our diagnostic game | Decision |
|---|---|---|---|---|---|
| GL-01 | **[Kitware Pulse Physiology Engine](https://gitlab.kitware.com/physiology/engine)** · [official Pulse docs](https://pulse.kitware.com/_docs.html) · [integration architecture](https://pulse.kitware.com/_about_pulse.html) | **Apache-2.0**, stated in official engine docs | **Canonical GitLab upstream**; specifically **forked from BioGears 6.1.1**, subsequently developed independently. Thus a *derived project*, not a synchronizing mirror of GitHub #BioGears. Unverified GitHub copies are not official mirrors. | Whole-body patient state, physiological actions, time advancement, vitals/assessments, scenario execution; C++ with multiple language bindings. **Highest-priority non-GitHub find** | **High-priority R&D**. The [official FAQ](https://pulse.kitware.com/_f_a_q.html) says the historical CodeSynthesis XSD GPL/FLOSS-exception complication was addressed by replacing it with BSD-licensed Protocol Buffers. Verify dependencies for the exact build; do not present the old constraint as automatically applying to current Pulse. |
| GL-02 | **[PyUS](https://gitlab.com/pyus/pyus)** | **BSD-3-Clause** shown by GitLab project license classification | Separate GitLab project; no established relation to a GitHub original in the 96 | GPU-accelerated ultrasound imaging/reconstruction tooling; *not* a ready clinical echo case simulator | **Optional / ultrasound R&D**. Reuse source only after checking the pinned dependency graph. |
| GL-03 | **[T1D Exercise RL](https://gitlab.com/csb.ethz/t1d-exercise-rl)** | **BSD-3-Clause** explicitly stated by project README and GitLab license classification | Independent research repository | Mechanistic glucose response to exercise and treatment control; could support an endocrine-specific diabetes simulation | **Optional / specific case R&D**, limited number of commits and specialized scope. |
| GL-04 | **[BETSE](https://gitlab.com/betse/betse)** | **BSD-2-Clause** stated in project README | Independent bioelectric tissue simulation | Bioelectric/ionic tissue research; *not* an ECG or ICU waveform engine | **Defer**, source archived and not well aligned to gameplay. |
| GL-05 | **[BETSEE](https://gitlab.com/betse/betsee)** | **BSD-2-Clause** indicated in GitLab license classification | GUI companion to BETSE, not another physiology engine | Interactive visualization for BETSE simulations | **Defer**, archived GUI. |

**GitLab entries that are FOSS-looking but need a definitive code/license review before importing:**

| ID | Repository | Evidence and unresolved issue | Decision |
|---|---|---|---|
| GL-06 | [OpenViBE meta](https://gitlab.inria.fr/openvibe/meta) | Open EEG/BCI acquisition and signal-processing platform. Independent software metadata labels this GitLab project **AGPL-3.0**; an older website refers to LGPL for older versions. The canonical forge blocks automatic inspection, so **license by version and all sub-repos require confirmation**. Sources: [research reference](https://www.nature.com/articles/s41597-023-02445-z), [repository metadata](https://data.code.gouv.fr/hosts/gitlab.inria.fr/repositories/openvibe%2Fmeta). | **Potentially FOSS/copyleft; not license-cleared for this game yet.** Interesting EEG workstation or preprocessing reference, but Epicurrents remains easier to embed. |
| GL-07 | [CLAsim — software-only](https://gitlab.com/openconnectedmed/clasim/clasim_software_only) | GitLab page lists **Educational Community License v2.0** while the README says “all files Apache 2.0.” **Both are OSI-style open-source licenses**, but a conflict in the project's authoritative terms must be resolved before copying. Very old Ubuntu/Pulse integration. | **Conditional/open-source license discrepancy.** A promising real closed-loop patient-monitor ↔ infusion-pump ↔ Pulse example, but too old for early integration. |

For GL-06 and GL-07, this is an identification of potentially free/open-source upstreams, **not** permission to treat their code as cleared for unrestricted integration.

### B. Hugging Face — distinguish software source from model/asset repositories

**Source-bearing application (actual inspectable Python code):**

| ID | Hugging Face repository | Type and license evidence | Value / restriction |
|---|---|---|---|
| HF-01 | **[ECGDiagnosticSystem Space](https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/tree/main)** · [README](https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/blob/main/README.md) | Code-bearing Gradio Space with `app.py`, preprocessing/inference/visualization scripts and model weights. **MIT declared in repo metadata and README**, but a root `LICENSE` file was not visible in the browsed file tree. | ECG analysis UI with 12-lead interpretation, lead ranking, explainer overlays and report exports. **Conditional adoption**: obtain/confirm complete MIT notice and model-weight/data provenance before copying. Its model predictions are not medical ground truth. |

**Openly licensed model/weight repositories — not standalone FOSS medical simulators:**

| ID | Repository | Public license metadata | Parent/mirror role | Potential use and limitations |
|---|---|---|---|---|
| HF-02 | **[lealaxy/OTC-Flow](https://huggingface.co/lealaxy/OTC-Flow)** | **MIT** model card | **Model/checkpoint counterpart to GitHub #21** [yunhaoli24/OTC-Flow](https://github.com/yunhaoli24/OTC-Flow); *not* another independent project | CT-conditioned transesophageal ultrasound synthesis research; high compute/medical validation burden. Verify original datasets and any checkpoint-specific restrictions. |
| HF-03 | [yang-ai-lab/SensorGen](https://huggingface.co/yang-ai-lab/SensorGen) | **MIT** model card | Independent generative biosignal model | Text-to-ECG and blood-pressure signal translation; multi-GB weights. Most relevant to *future* on-demand synthetic signals; check waveform morphology and actual clinical realism. |
| HF-04 | [PULSE-ECG/PULSE-7B](https://huggingface.co/PULSE-ECG/PULSE-7B) | **Apache-2.0** model card | ECG-interpretation model. **Unrelated to Kitware Pulse Physiology Engine** despite same word in name | Can help evaluate how informative a displayed ECG is; never use as independent authority for case truth. Heavy 7B multimodal model. |
| HF-05 | [wanglab/ecg-fm](https://huggingface.co/wanglab/ecg-fm) | **MIT** model metadata | ECG foundation model weights | Representation/extraction for real ECG study matching or evaluation; no synthetic ECG workstation included. |
| HF-06 | [PKUDigitalHealth/ECG-R1-8B-RL](https://huggingface.co/PKUDigitalHealth/ECG-R1-8B-RL) | **Apache-2.0** model metadata | Multimodal ECG reasoning model family; check upstream [ECG-R1 code](https://github.com/PKUDigitalHealth/ECG-R1) if integrating | Possible benchmark or tutor, not diagnostic truth. Training data, inference infrastructure and applicable license chain need checking. |

**Important rights distinction:** a Hugging Face model repo with a permissive metadata tag can still require independent checks for architecture source, converted weights, base model license, training material and redistributed examples. This appendix catalogs these as **freely accessible, permissively tagged model assets**, not as fully proven open-source software stacks or validated medical devices.

**Open-data references on Hugging Face — separate from software count:**

| ID | Repository | License metadata | Appropriate use |
|---|---|---|---|
| HF-D1 | [AymanAmeen/SimEIT-dataset](https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset) | **Apache-2.0** metadata | Synthetic electrical-impedance tomography measurements and conductivity maps; research/prototyping for future respiratory/volumetric investigations. Not a ready-to-play simulator. |
| HF-D2 | [PULSE-ECG/ECGInstruct](https://huggingface.co/datasets/PULSE-ECG/ECGInstruct) | **Apache-2.0** metadata | ECG interpretation/training examples. Check underlying ECG/image sources and attribution before redistributing inside the game. |

### C. Other code hosts / false-positive mirror handling

| Candidate | Finding | Disposition |
|---|---|---|
| [SourceForge OpenVCT](https://sourceforge.net/p/openvct/wiki/Home/) | Genuine source-control-hosted *virtual clinical trial / imaging-simulation* project with an SVN repository, not a patient diagnostics game. Its exact current software LICENSE was **not** established from the inspected project wiki. | **Not counted as a cleared FOSS candidate**. Obtain authoritative source-license text first. |
| [GitLab altairLab probe-tissue simulation](https://gitlab.com/altairLab/probe-tissue-simulation) | SOFA ultrasound probe–tissue interaction. Direct public repository visible; no reliable code-license verification in this pass. | **Excluded pending license proof.** |
| [GitLab SimuPro](https://gitlab.com/tylerleedixon-group/simupro) | Promising paramedic ECG/physiology training description, but no reproducible license evidence in inspected results. | **Excluded pending license proof** — do not copy merely because public. |
| [GitLab Sirael T1D subjects](https://gitlab.com/sirael_metabolic_simulator/diabetes-type-1-subjects) | Patient parameter source for endocrine models; no code/data license verified. | **Excluded pending rights verification**. |
| [GitHub unofficial Pulse mirror](https://github.com/cnsuhao/engine1) | A GitHub project linking the Kitware GitLab source, but no evidence it is the official or current mirror. | **Do not replace the Kitware GitLab canonical source** or count as a distinct engine. |
| **Codeberg / other GitLab mirrors of all 96** | Searches did not establish trustworthy, licensed one-to-one mirrors for the 96 GitHub original repos. Codeberg blocked automated crawling. | **No guessed mirror URLs added**. Canonical GitHub URLs remain unchanged. |
| [Ahus-AIM/EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow), [EchoXFlow-Demo](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow-Demo) | Particularly interesting synchronized echo/ECG/flow sources, but explicitly **CC BY-NC-SA 4.0**. | **Excluded from reusable corpus** under the strict open-source/open-content requirement despite research value. |
| [nsrek/ECGLight](https://huggingface.co/nsrek/ECGLight) | ECG digitization source/model with *noncommercial research-only* terms. | **Excluded**. |

**No claims are made that repositories on GitLab or Hugging Face with the same topic are forks/mirrors unless their upstream relationship was identifiable.** Within the original 96, HF-02 is the direct checkpoint companion to GitHub #21 OTC-Flow. Additional HF-to-GitHub code counterparts were verified for projects *outside* the original 96; see the pairing ledger below. Pulse is a BioGears-derived fork, not a mirrored copy.

### C2. Verified cross-platform source, mirror, checkpoint, and dataset relationships

The following table links **the same project's code, a maintainer-described mirror, or its associated weights/datasets across hosting platforms**. These are *relationships*, **not** extra independent simulators. A checkpoint on Hugging Face is almost never a source-code mirror.

| Project or relationship | Upstream code / canonical source | Other host / counterpart | Relationship established | Integration relevance |
|---|---|---|---|---|
| **OTC-Flow** (already GitHub #21) | [GitHub source](https://github.com/yunhaoli24/OTC-Flow) | [Hugging Face weights](https://huggingface.co/lealaxy/OTC-Flow) | Official model card explicitly links the GitHub implementation | Echo / CT-to-TEE image generation research |
| **SensorGen** (new external companion) | [GitHub source](https://github.com/yang-ai-lab/SensorGen) | [Hugging Face weights](https://huggingface.co/yang-ai-lab/SensorGen) | HF model card points to the project code | Future biosignal synthesis and validation, not ready pathological ECG realism |
| **PULSE-7B ECG model** (not Kitware Pulse) | [GitHub ECG model code](https://github.com/AIMedLab/PULSE) | [Hugging Face model](https://huggingface.co/PULSE-ECG/PULSE-7B), [training set](https://huggingface.co/datasets/PULSE-ECG/ECGInstruct), [evaluation set](https://huggingface.co/datasets/PULSE-ECG/ECGBench) | Model card explicitly links GitHub and both datasets | ECG image-reading research and an optional tutor evaluation set |
| **ECG-FM** | [GitHub source](https://github.com/bowang-lab/ECG-FM) | [Hugging Face pretrained weights](https://huggingface.co/wanglab/ecg-fm) | Model card explicitly states the HF repository is **weights-only** and links GitHub | Offline ECG feature extraction; not an ECG waveform game |
| **ECG-R1** | [GitHub source](https://github.com/PKUDigitalHealth/ECG-R1) | [Hugging Face model](https://huggingface.co/PKUDigitalHealth/ECG-R1-8B-RL), [supporting data](https://huggingface.co/datasets/PKUDigitalHealth/ECG-Protocol-Guided-Grounding-CoT) | HF model card directly identifies the source | ECG reasoning research; may leak answers if used as game truth |
| **SimEIT** | [Hugging Face synthetic EIT dataset](https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset) | [Hugging Face Space demo](https://huggingface.co/spaces/AymanAmeen/SimEIT-demo) | Space names the dataset; **the Space's own code license not independently checked** | Research into reconstructed respiratory imaging and demo UI |
| **Orthanc** (NEW canonical off-GitHub codebase) | **[Official Mercurial upstream](https://orthanc.uclouvain.be/hg/orthanc/)** | [Maintainer's GitHub mirror](https://github.com/jodogne/OrthancMirror); [additional read-only GitHub mirror](https://github.com/orthanc-mirrors/orthanc) | Main upstream is Mercurial. `jodogne/OrthancMirror` self-identifies as a mirror; secondary mirror says read-only. **Mirrors need independent freshness checks** | DICOMweb/PACS server backend, not necessary if a small game just loads packaged DICOM files |
| **BioGears → Kitware Pulse** | [BioGears GitHub source](https://github.com/BioGearsEngine/core) | [Kitware Pulse official GitLab source](https://gitlab.kitware.com/physiology/engine) | **Historical fork**, specifically BioGears 6.1.1, documented by Kitware; **NOT a synchronous mirror** | Compare engines independently, and prefer the maintained/correctly licensed one after a runtime study |

**Orthanc license and provenance:** the canonical Mercurial repository's [CITATION.cff](https://orthanc.uclouvain.be/hg/orthanc/file/tip/CITATION.cff) states **GPL-3.0-or-later**. Its maintainer-provided GitHub mirror is useful for browsing, but GitHub availability does not change the GPL obligations. Orthanc has a distinct license and role from OHIF: it is a DICOM server, whereas OHIF is a medical image viewer. The upstream's source index and release history were confirmed in November 2026.

**Pulse fork and historical dependency caveat:** the [official FAQ](https://pulse.kitware.com/_f_a_q.html) states that Pulse started as a fork of BioGears 6.1.1 and explains that an older CodeSynthesis licensing problem was later addressed with Protocol Buffers. Exact pinned code and third-party licenses still require inspection; do not claim all current Pulse modifications are automatically GPL-constrained.

**Dataset usability caveat:** the [SimEIT dataset](https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset) currently exposes a schema/casting failure in Hugging Face's online dataset viewer. That is **a preview/import issue**, not evidence that the actual underlying files are corrupted. Validate actual files and schema before use.

**Mirror credibility rule:** only tag an address as an official mirror when it explicitly identifies its upstream or is linked by the maintainer. Codeberg was inaccessible to automated inspection here, so the absence of confirmed mirrors is **not proof that none exist**.


### C3. Newly detailed upstream–mirror–model relationships (not additional primary entries)

The later source review specifically identifies the following companion resources. The upstream–mirror relationship must be verified independently from the license of a checkpoint, dataset or source repository. These links do **not** inflate the 112-entry primary inventory.

- **USTB official mirror**: the maintainers' [GitHub README](https://github.com/unioslo/USTB) explicitly lists **[Bitbucket USTB](https://bitbucket.org/ustb/ustb)** as a parallel official source. This is a verified mirror relationship, not a 113th simulator.
- **PatientSim**: its [GitHub README](https://github.com/dek924/PatientSim) identifies a public [Hugging Face demonstration](https://huggingface.co/spaces/dek924/PatientSim) and a credentialed [PhysioNet persona dataset](https://physionet.org/content/persona-patientsim/1.0.0/). A public demo does not clear the underlying MIMIC-derived case material for redistribution.
- **DiagGym**: its [GitHub README](https://github.com/MAGIC-AI4Med/DiagGym) links [DiagGym weights](https://huggingface.co/Henrychur/DiagGym), [DiagAgent-14B](https://huggingface.co/Henrychur/DiagAgent-14B), and [DiagBench](https://huggingface.co/datasets/Henrychur/DiagBench). These are companion model/dataset repositories, not copies of the GitHub implementation. Their own licenses/data conditions require verification.
- **Epicurrents**: the verified [builder README](https://github.com/epicurrents/builder) documents a wider modular package family (NCS, DICOM/EDF/WAV readers, ONNX/Pyodide computation services) beyond the six previously enumerated repositories. These are **related packages discovered**, but are not silently counted as additional primary sources.
- **OHIF**: the archived [ohif-core](https://github.com/OHIF/ohif-core) points directly to its maintained successor inside [OHIF/Viewers/platform/core](https://github.com/OHIF/Viewers/tree/master/platform/core), rather than being an independent library to adopt.

### D. Priority changes in the actual medical-game build

1. **Investigate Kitware Pulse beside BioGears**, not simply as an unrelated extra physiology engine. Test the same authored sepsis/shock or pulmonary scenario, using identical interventions/time points; compare reproducibility, implementation/API friction, clinical plausible ranges and performance. See official [Pulse time-step/action interface](https://pulse.kitware.com/_docs.html).
2. **Keep Patient Monitor Engine + 12-Lead Generator for the first ECG/monitor screen.** Pulse is a whole-body physiological engine, not an immediate replacement for a refined browser cardiac display.
3. **Explore PyUS for an advanced ultrasound backend only if EchoSim/recorded cine loops fail the learning goal.** Physics-based reconstruction by itself does not yield arbitrary pathology-specific echocardiography.
4. **Treat SensorGen as an experiment, not a drop-in pathology generator.** In particular, independently check whether target myocardial infarction, electrolyte abnormalities, rhythm changes and serial ECG changes are medically plausible and mutually consistent.
5. **Do not import noncommercial echo datasets/models or unlicensed GitLab demos** into the game's packaged assets. License-pinned clinical media provenance is a first-class requirement.
6. **Keep a per-resource ledger**: URL; canonical/mirror/companion relationship; version/commit; OSI software license versus weights/data/content terms; third-party asset obligations; training/clinical validation; locally tested status; integration priority.

### E. Evidence anchors for the non-GitHub additions

- Kitware documentation: [Pulse license, current releases and interfaces](https://pulse.kitware.com/_docs.html); [engine capabilities and integrations](https://pulse.kitware.com/_about_pulse.html); [third-party licensing caveat](https://pulse.kitware.com/_f_a_q.html).
- Direct GitLab project pages and declared licenses: [PyUS](https://gitlab.com/pyus/pyus), [T1D Exercise RL](https://gitlab.com/csb.ethz/t1d-exercise-rl), [BETSE](https://gitlab.com/betse/betse), [BETSEE](https://gitlab.com/betse/betsee), [CLAsim](https://gitlab.com/openconnectedmed/clasim/clasim_software_only). [OpenViBE external repo metadata](https://data.code.gouv.fr/hosts/gitlab.inria.fr/repositories/openvibe%2Fmeta) is **secondary** evidence because the official server blocks crawling.
- Hugging Face source-bearing Space: [ECGDiagnosticSystem source files](https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/tree/main) and [README license declaration](https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/blob/main/README.md).
- Hugging Face permissively tagged model cards: [OTC-Flow](https://huggingface.co/lealaxy/OTC-Flow), [SensorGen](https://huggingface.co/yang-ai-lab/SensorGen), [PULSE-7B](https://huggingface.co/PULSE-ECG/PULSE-7B), [ECG-FM](https://huggingface.co/wanglab/ecg-fm), [ECG-R1](https://huggingface.co/PKUDigitalHealth/ECG-R1-8B-RL).
- Open-data licensing and noncommercial exclusions: [SimEIT](https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset), [ECGInstruct](https://huggingface.co/datasets/PULSE-ECG/ECGInstruct), [EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow), [ECGLight restrictions](https://huggingface.co/nsrek/ECGLight).

---


### F. Deeper source-by-source dossiers — all 16 non-GitHub primary entries

The later uploaded audit provides structured profiles for the seven GitLab repositories, six Hugging Face applications/weight repositories, two Hugging Face datasets, and Orthanc's Mercurial upstream. These elaborate on Part V's compact canonical inventory **without adding sixteen new projects to the counts**. Reuse terms and claims in these snapshots remain subject to the precise caveats established earlier. The “potential use” fields are engineering proposals rather than documented integration APIs.

These sixteen entries retain the prior cross-host **count of 112** while offering the same architectural / functional / integration / uncertainty structure as GitHub #54–96. A Hugging Face weight card is not equivalent to executable game code. The label *GitLab* does not automatically mean a repository is official, maintained or licensed.

#### GL-01. [Kitware Pulse Physiology Engine](https://gitlab.kitware.com/physiology/engine)

**Host/type:** GitLab code  |  **License/status:** Apache-2.0 — official Kitware documentation

**Implementation and architecture.** Native C++ physiology SDK with cross-language integration approaches, a common patient data model, lumped cardiovascular/respiratory/renal and pharmacological models, and a scenario driver.

**Relevant capabilities and behavior.** Each patient is a stateful engine instance advanced in simulation time. Actions, conditions and assessments can produce connected vitals, blood chemistry, CBC/CMP and arterial blood gas responses. Published validation tables make strengths and weak domains more inspectable than generic simulator claims.

**Potential use in our game (design inference).** Highest-value non-GitHub candidate for eventually replacing ad-hoc physiology formulas. Compare one identical patient/action scenario with BioGears; keep a lightweight monitor renderer and a separate case truth adapter.

**Legal, validation and deployment limits.** Official documentation reports Apache-2.0 and identifies Pulse as a substantially extended BioGears fork. Validity is **domain-specific**: Kitware's own reference table includes poor renal and renal-solute matches. A 20-ms model step does not establish real-time browser integration. Sources: https://pulse.kitware.com/_about_pulse.html and https://pulse.kitware.com/_docs.html.

**Primary evidence:** [https://gitlab.kitware.com/physiology/engine](https://gitlab.kitware.com/physiology/engine).

#### GL-02. [PyUS](https://gitlab.com/pyus/pyus)

**Host/type:** GitLab code  |  **License/status:** BSD-3-Clause — GitLab project classification

**Implementation and architecture.** Python GPU-accelerated ultrasound imaging/reconstruction package, distinct from full echo patient simulation.

**Relevant capabilities and behavior.** Provides a research path toward faster signal processing and image formation where synthetic B-mode/Doppler-like outputs are needed.

**Potential use in our game (design inference).** Compare narrowly against PyMUST and USTB on one simulated probe/phantom input. The game should treat its output as an authored/verified image asset, not on-the-fly clinical fact.

**Legal, validation and deployment limits.** GitLab license label reports BSD-3-Clause. Pin a commit and inspect dependencies, test data and platform/GPU requirements. It has no independently verified full pathology or clinical-training claim.

**Primary evidence:** [https://gitlab.com/pyus/pyus](https://gitlab.com/pyus/pyus).

#### GL-03. [T1D Exercise RL](https://gitlab.com/csb.ethz/t1d-exercise-rl)

**Host/type:** GitLab code  |  **License/status:** BSD-3-Clause — prior project readme/forge license evidence

**Implementation and architecture.** Research reinforcement-learning setup for insulin dosing and glucose regulation with exercise effects in virtual type-1 diabetic subjects.

**Relevant capabilities and behavior.** Uses dynamic endocrine/insulin response models and controllable interventions; companion research on model-predictive control is linked from project docs.

**Potential use in our game (design inference).** Possible specialized endocrine scenario component, particularly when exercise or nutrition changes glucose trajectories. Run it as a separate narrowly bounded simulator.

**Legal, validation and deployment limits.** Not a general laboratory generator or clinical dosing system. Modeling population and license of patient parameters require separate inspection. Research README: https://gitlab.com/csb.ethz/t1d-exercise-rl.

**Primary evidence:** [https://gitlab.com/csb.ethz/t1d-exercise-rl](https://gitlab.com/csb.ethz/t1d-exercise-rl).

#### GL-04. [BETSE](https://gitlab.com/betse/betse)

**Host/type:** GitLab code  |  **License/status:** BSD-2-Clause — project documentation

**Implementation and architecture.** Bioelectric tissue and ion/electrodiffusion simulation research engine, not a simulated electrocardiograph.

**Relevant capabilities and behavior.** Its scale is cellular/tissue bioelectric phenomena and numerical visualization, rather than patient vitals or hospital tests.

**Potential use in our game (design inference).** Defer; consider only for a specific electrophysiological education project or tissue modeling question.

**Legal, validation and deployment limits.** Previously marked archived; no complete runtime evaluation. Neither 'electrical' in its description nor open code implies clinical ECG accuracy.

**Primary evidence:** [https://gitlab.com/betse/betse](https://gitlab.com/betse/betse).

#### GL-05. [BETSEE](https://gitlab.com/betse/betsee)

**Host/type:** GitLab code  |  **License/status:** BSD-2-Clause — forge classification

**Implementation and architecture.** Graphical front end and visualization companion to BETSE, not a separate medical disease or physiology engine.

**Relevant capabilities and behavior.** Helps configure and display underlying biological electrical simulation runs.

**Potential use in our game (design inference).** Defer. If BETSE is ever needed, count the GUI as one linked component rather than an independent medical test simulator.

**Legal, validation and deployment limits.** Previously marked archived. Exact source/packaging/version compatibility not re-tested.

**Primary evidence:** [https://gitlab.com/betse/betsee](https://gitlab.com/betse/betsee).

#### GL-06. [OpenViBE meta](https://gitlab.inria.fr/openvibe/meta)

**Host/type:** GitLab code  |  **License/status:** Conflicting AGPL-3.0 / older LGPL information — conditional

**Implementation and architecture.** EEG/brain-computer-interface platform coordinating acquisition, real-time processing, visualization and training scenarios across component packages.

**Relevant capabilities and behavior.** Useful for complex EEG filters, stimulus paradigms and signal pipelines, but its scope extends far beyond our passive clinical EEG viewing requirements.

**Potential use in our game (design inference).** Study only if Epicurrents plus offline EEG preparation cannot support a needed modality or measurement. Decide whether a separate process avoids unnecessary code coupling.

**Legal, validation and deployment limits.** Canonical forge access is restricted to the available browser in this pass; exact licensing by package and version was not established. Do not inherit a single AGPL tag as proof for the whole suite.

**Primary evidence:** [https://gitlab.inria.fr/openvibe/meta](https://gitlab.inria.fr/openvibe/meta).

#### GL-07. [CLAsim software-only](https://gitlab.com/openconnectedmed/clasim/clasim_software_only)

**Host/type:** GitLab code  |  **License/status:** GitLab labels Educational Community License v2.0; README reportedly Apache-2.0

**Implementation and architecture.** Medical device/control-algorithm co-simulation environment joining virtual patients, modeled equipment and feedback controllers; older work with Pulse-related interactions.

**Relevant capabilities and behavior.** Its software-only approach can demonstrate closed-loop coupling, for example a measured patient signal driving an actuator or infusion-control algorithm.

**Potential use in our game (design inference).** Interesting integration architecture reference for the relationship between physiology, sensor outputs and treatments; low priority as a dependency.

**Legal, validation and deployment limits.** GitLab page confirms a 2019-era project. Resolve conflicting license statements; independently evaluate dependency and clinical assumptions before using.

**Primary evidence:** [https://gitlab.com/openconnectedmed/clasim/clasim_software_only](https://gitlab.com/openconnectedmed/clasim/clasim_software_only).

#### HF-01. [ECGDiagnosticSystem Space](https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/tree/main)

**Host/type:** Hugging Face source application  |  **License/status:** MIT declared in model/Space metadata; root notice not confirmed

**Implementation and architecture.** Gradio Python source application using a multi-label ECG model, lead-importance computation, waveform preprocessing and explanation/visualization utilities.

**Relevant capabilities and behavior.** The source includes an app entry point, preprocessing modules, model code, lead ranking and plotting for 12-lead traces. The app describes a CNN + bidirectional LSTM + attention pipeline trained with PTB-XL-derived ECG data.

**Potential use in our game (design inference).** Could act as an offline *second opinion* for QA of bundled ECG exercises or inspire a report viewer. Do not let an AI prediction rewrite the case diagnosis or certify correctness.

**Legal, validation and deployment limits.** Root LICENSE and weights provenance need confirmation; model discrimination is not shown to be reliable across the full set of pathologies expected in the game. App source and metadata are inspectable at its linked Space.

**Primary evidence:** [https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/tree/main](https://huggingface.co/spaces/orocktk-agbor/ECGDiagnosticSystem/tree/main).

#### HF-02. [OTC-Flow weights](https://huggingface.co/lealaxy/OTC-Flow)

**Host/type:** Hugging Face model weights  |  **License/status:** MIT model-card tag; verify every dependency and source data

**Implementation and architecture.** Checkpoint counterpart to GitHub #21 OTC-Flow, implementing research-stage CT-conditioned transesophageal echo image synthesis.

**Relevant capabilities and behavior.** Generative output depends on CT source data and the trained image model, rather than producing a measurement-valid procedural echo automatically.

**Potential use in our game (design inference).** Potential future R&D for authored echo loop assets; not independent code and not a dynamic patient physiology engine.

**Legal, validation and deployment limits.** Model tags do not grant rights to third-party clinical CT/TEE material. Use GitHub code plus the HF weight card as a paired dependency record.

**Primary evidence:** [https://huggingface.co/lealaxy/OTC-Flow](https://huggingface.co/lealaxy/OTC-Flow).

#### HF-03. [SensorGen weights](https://huggingface.co/yang-ai-lab/SensorGen)

**Host/type:** Hugging Face model weights  |  **License/status:** MIT model-card metadata

**Implementation and architecture.** Large physiological signal generation checkpoints for translating descriptions or contexts into ECG and blood-pressure-related time series; project source is linked on GitHub.

**Relevant capabilities and behavior.** The cards distinguish model checkpoints from the Python code and identify task-specific weights such as text-to-ECG. It may support realistic waveform augmentation after careful benchmarking.

**Potential use in our game (design inference).** Prototype only: generate a known rhythm/pathology, use independent measurements and check clinical plausibility, reproducibility, lead relationships, amplitude and sampling metadata.

**Legal, validation and deployment limits.** Independent from the 96-entry GitHub inventory, but not a second simulator solely because its code is on GitHub. The HF checkpoint and GitHub source are a paired project. Memory/GPU needs may be substantial.

**Primary evidence:** [https://huggingface.co/yang-ai-lab/SensorGen](https://huggingface.co/yang-ai-lab/SensorGen).

#### HF-04. [PULSE-7B ECG model](https://huggingface.co/PULSE-ECG/PULSE-7B)

**Host/type:** Hugging Face model weights  |  **License/status:** Apache-2.0 model card

**Implementation and architecture.** A multimodal 7-billion-parameter model for reading printed and digital ECG images; linked to AIMedLab/PULSE code, ECGInstruct training data and ECGBench evaluation data.

**Relevant capabilities and behavior.** It is an *interpreter*, not a heart model or waveform source. Model documentation discusses ECG image interpretation and examples across benchmark tasks.

**Potential use in our game (design inference).** Useful for independent rubric comparisons or optional AI tutor wording after the player has reached a conclusion; should not supply test results or be trusted as clinical ground truth.

**Legal, validation and deployment limits.** Distinct from Kitware's Pulse Physiology Engine. A permissive card tag does not clear every training image, conversion or fine-tuned base-model right.

**Primary evidence:** [https://huggingface.co/PULSE-ECG/PULSE-7B](https://huggingface.co/PULSE-ECG/PULSE-7B).

#### HF-05. [ECG-FM weights](https://huggingface.co/wanglab/ecg-fm)

**Host/type:** Hugging Face model weights  |  **License/status:** MIT model metadata

**Implementation and architecture.** Weights-only ECG representation/foundation model companion to GitHub bowang-lab/ECG-FM.

**Relevant capabilities and behavior.** Encodes electrocardiographic morphology into features suitable for retrieval, downstream analysis and potential signal similarity comparisons.

**Potential use in our game (design inference).** Potential offline tool to select compatible real ECG examples for authored cases, or cluster quality-control failures in synthetic ECG assets.

**Legal, validation and deployment limits.** Not a waveform simulator, not a player-facing clinical app, and not an independent validation authority. Check pretrained training-domain mismatch and weights-only status.

**Primary evidence:** [https://huggingface.co/wanglab/ecg-fm](https://huggingface.co/wanglab/ecg-fm).

#### HF-06. [ECG-R1-8B-RL weights](https://huggingface.co/PKUDigitalHealth/ECG-R1-8B-RL)

**Host/type:** Hugging Face model weights  |  **License/status:** Apache-2.0 model metadata

**Implementation and architecture.** Multimodal ECG reasoning model checkpoint linked to GitHub PKUDigitalHealth/ECG-R1 implementation.

**Relevant capabilities and behavior.** Focuses on reasoning over ECG inputs and producing clinical interpretations rather than dynamically simulating electrical activity.

**Potential use in our game (design inference).** Possible research comparison with PULSE-7B ECG on a held-out, clinically checked case corpus; useful as a tutor only if false-positive/error behavior is bounded.

**Legal, validation and deployment limits.** Weights, code, original recordings and underlying base models require distinct license checks. Inference memory is high for an interactive local player experience.

**Primary evidence:** [https://huggingface.co/PKUDigitalHealth/ECG-R1-8B-RL](https://huggingface.co/PKUDigitalHealth/ECG-R1-8B-RL).

#### HF-D1. [SimEIT dataset](https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset)

**Host/type:** Hugging Face data  |  **License/status:** Apache-2.0 dataset metadata

**Implementation and architecture.** Synthetic electrical-impedance tomography conductivity maps and simulated measurements rather than software source.

**Relevant capabilities and behavior.** Potential input material for an advanced respiratory functional-imaging lesson where the player interprets ventilation redistribution or reconstructed slices.

**Potential use in our game (design inference).** Do not package as a physiology engine. Confirm labels, resolution, source terms and that any generated displays are not presented as clinical patient imaging.

**Legal, validation and deployment limits.** Dataset-card license is a starting point, not a substitute for inspecting its upstream generated data, referenced source dependencies and applicable attribution.

**Primary evidence:** [https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset](https://huggingface.co/datasets/AymanAmeen/SimEIT-dataset).

#### HF-D2. [ECGInstruct dataset](https://huggingface.co/datasets/PULSE-ECG/ECGInstruct)

**Host/type:** Hugging Face data  |  **License/status:** Apache-2.0 dataset metadata

**Implementation and architecture.** ECG instruction and image-interpretation examples associated with the PULSE-7B research pipeline.

**Relevant capabilities and behavior.** Can help generate standardized *questions and rubric categories* about existing ECG images, or compare automatic interpretation models.

**Potential use in our game (design inference).** Treat as evaluation/training content, not a substitute for properly licensed clinical ECG cases; manually review any example incorporated into a learner-facing scenario.

**Legal, validation and deployment limits.** Check original ECG source provenance, copyright and potential patient data restrictions before redistribution; model-generated annotations may include mistakes.

**Primary evidence:** [https://huggingface.co/datasets/PULSE-ECG/ECGInstruct](https://huggingface.co/datasets/PULSE-ECG/ECGInstruct).

#### OTHER-01. [Orthanc — canonical Mercurial source](https://orthanc.uclouvain.be/hg/orthanc/)

**Host/type:** Mercurial source archive  |  **License/status:** GPL family / additional Orthanc component terms — verify exact release

**Implementation and architecture.** Production-grade DICOM server and imaging archive with an official Mercurial upstream and read-only GitHub mirror `jodogne/OrthancMirror`.

**Relevant capabilities and behavior.** Offers DICOM storage/index, access APIs and PACS/DICOMweb capabilities through appropriate components/plugins. Unlike an image viewer, it operates the underlying study repository.

**Potential use in our game (design inference).** Add only when many licensed DICOM studies, server-based sharing, permissions and retrieval justify a dedicated archive. For one-player bundled cases, static assets or a small DICOMweb-compatible service may be simpler.

**Legal, validation and deployment limits.** Canonical Mercurial ≠ identical/current GitHub snapshot without checking a revision. Orthanc components/plugins can have distinct GPL/AGPL/proprietary terms; an external server's license obligations require a deployment-specific review.

**Primary evidence:** [https://orthanc.uclouvain.be/hg/orthanc/](https://orthanc.uclouvain.be/hg/orthanc/).

---

# PART VI — OTHER PROJECT-CONVERSATION DISCOVERIES NOT IN THE TWO UPLOADED FILES

These were encountered in earlier relevant project conversations or the older *Open-Source Medical Simulation Games and Modules* report but were not present as independent entries in the 96-GitHub master table, or were mentioned only indirectly. **Supplementary entries are not retrospectively included in the 112 tracked primary-host count.** Only evidence available in this consolidation is asserted; uncertainty remains explicit. The excluded, unrelated project architecture is not presented here.

## VI-A. Additional clinical simulation and case-authoring source repositories

### S1. Synthea — synthetic patient population simulator

- **Repository:** [synthetichealth/synthea](https://github.com/synthetichealth/synthea)
- **Type:** Synthetic longitudinal EHR and patient-population generator (Java); **Apache-2.0** code.
- **Recoverable capabilities:** seedable generation, clinical state-machine modules, conditional/distributed event transitions, observations, encounters, medication, procedures, patient histories and multiple health-record export formats (including FHIR and CSV formats as supported by configuration).
- **Use in this game:** generate fictional charts, consistent demographics, realistic-looking encounter sequences, medication histories, lab ordering examples, fixtures and EHR stress-test data. Use **offline** or in authoring/test pipelines. Do not mistake the population generator for a real-time bedside cardiac electrophysiology or arbitrary pathology-specific image generator.
- **Earlier research detail:** an October 2026 source review reported roughly 242 JSON simulation modules and configurable seeded state machines. This module count is an earlier snapshot, not a current independently reproduced count.
- **Validation tasks:** validate JSON/FHIR semantic coherence, date formats, reference ranges, synthetic–real-data separation and whether any sampled values violate the intended case path. Favor deterministic seeds for automated fixture regeneration. License source: project repo and root `LICENSE`.

### S2. Patient-Simulator — shivanand-vn (distinct from paultman)

- **Repository:** [shivanand-vn/Patient-Simulator](https://github.com/shivanand-vn/Patient-Simulator)
- **Type:** AI-driven virtual patient, patient personas, scenario versions, sessions, interventions and evaluations. Repository describes a web/native wrapper with frontend, Python API and database; this is **an external candidate**, not the target game architecture.
- **Earlier project review:** includes clinical truth/personas, investigations and treatments, real-time updates and dynamic vitals; at the time of the earlier review, many treatment effects were numerical state changes and requested results lacked realistic waiting/collection stages. The LLM still required strict authority boundaries.
- **License:** **Unconfirmed** in available review. Public access alone is not a grant.
- **Decision:** architecture reference only. Test whether its case-state model separates patient knowledge, secret ground truth and externally verifiable test results before any direct reuse request.

### S3. OLab4 — legacy successor to OpenLabyrinth

- **Repository:** [olab/OLab4](https://github.com/olab/OLab4)
- **Type:** historically GPL-3.0 educational scenario authoring platform derived from earlier OpenLabyrinth concepts.
- **Important freshly checked finding:** repository README literally states **this repository is no longer active and only exists for archival purposes; do not use** (dated 6 October 2022). Its sample Docker instructions include hard-coded demo passwords and explicit warnings against any public-facing use.
- **Decision:** archival research, **not a new base game**. Main canonical 96 index already includes [olab/Open-Labyrinth](https://github.com/olab/Open-Labyrinth), a different v3 codebase.

### S4. TUM-style Virtual Patient System — timbruckdorfer

- **Repository:** [timbruckdorfer/virtual-patient-system](https://github.com/timbruckdorfer/virtual-patient-system)
- **Earlier report:** student anamnesis training with German-language examples, GPT-assisted interviews, session tracking and analytics; the earlier report classified usage as academic/noncommercial.
- **Current rights status:** no complete authoritative license was reverified in this consolidation; **conditionally restricted**. Useful as a clinical interview UX comparison, not prioritized above MIT Virtual Standardized Patient.
- **Evidence discipline:** do not conflate free access to its demonstration with license to redistribute source or patient cases.

### S5. Quickcardboard ECG Studio / LiveHeart reference

- **Repository:** [quickcardboard/ecgstudio](https://github.com/quickcardboard/ecgstudio)
- **Type:** interactive 3D heart and 12-lead electrocardiography lesson application. Repository describes CT-derived four-chamber heart geometry, controllable activation abnormalities, ischemia and changes to the resulting leads.
- **Earlier report:** regarded as proprietary/all-rights-reserved or at least not freely reusable; **an authoritative software grant was not established in this pass**. Therefore classify as **study only** pending its actual license.
- **Engineering value:** compare heart conduction-to-lead rendering, spatial orientation and interactive pathology changes against `cardiosim-lab`, `cardiac-3d-ecg-simulator` and `12-Lead-Generator`. Do not equate interactive morphology with clinically correct 12-lead diagnosis.

### S6. EKG Maker — arzaluz-chris

- **Repository:** [arzaluz-chris/EKG-Maker](https://github.com/arzaluz-chris/EKG-Maker)
- **Earlier report:** simple HTML/JS waveform construction site; no code reuse license had been verified. It overlaps more capable waveform generators.
- **Decision:** very low priority / uncertain provenance. URL originated in the earlier comparative report and was not independently fetched in this consolidation.

### S7. 12-lead ECG viewer — humanurozcelik

- **Repository:** [humanurozcelik/12-lead-ecg-viewer](https://github.com/humanurozcelik/12-lead-ecg-viewer)
- **Earlier report:** Python-oriented GUI for interpreting/displaying simulated 12-lead results; no verified permission grant. Narrow viewer rather than disease simulator.
- **Decision:** defer; URL originated in the earlier comparative report, not independently installed/verified.

### S8. Additional smaller patient-conversation candidate — Artificial-intelligence-patient-simulator

- **Repository:** [umiiwarraich1122/Artificial-intelligence-patient-simulator](https://github.com/umiiwarraich1122/Artificial-intelligence-patient-simulator)
- **What public repository describes:** Flask/HTML/CSS/OpenAI-assisted fictional patient dialogue and adaptive case interviews for clinical learning.
- **Assessment:** introductory conversation prototype and possible baseline to demonstrate a data-bound dialog adapter. License/asset provenance and testing were not audited. Not a priority over the more mature conversation projects already indexed.

### S9. Other patient communication prototype — MaksymPetyak

- **Repository:** [MaksymPetyak/patient-simulator](https://github.com/MaksymPetyak/patient-simulator)
- **What public repository describes:** patient communication practice with emotional conversations including delivering distressing news. This is a consultation/communication exercise, not a fully featured diagnostic orders, imaging and physiology engine.
- **Decision:** reference only; full grant and case content rights not audited. Distinct from shivanand-vn and paultman repositories.

### S10. OpenLabyrinth family relationship

- **Original indexed repository:** [olab/Open-Labyrinth](https://github.com/olab/Open-Labyrinth) (**already #50**).
- **Additional historic variation:** older chats sometimes described `OpenLabyrinth/Open-Labyrinth` or `openspur/OpenLabyrinth`. These were **not confirmed canonical independent current upstreams** during this consolidation. The indexed `olab` repository, its README and OLab4 historical successor are the references to preserve; do not inflate independent codebase counts with alternate names.

## VI-B. Case data, reproducible diagnosis assets and medical literature sources

### D1. MedCaseReasoning — cases plus provenance/reasoning scaffolding

- **Code/documentation repository:** [kevinwu23/Stanford-MedCaseReasoning](https://github.com/kevinwu23/Stanford-MedCaseReasoning) (README also names a historically styled `kevinwu23/MedCaseReasoning` clone URL; confirm canonical repository and redirects before scripting).
- **Dataset:** [zou-lab/MedCaseReasoning on Hugging Face](https://huggingface.co/datasets/zou-lab/MedCaseReasoning).
- **Claimed scale in repository README:** **14,489 clinician-authored cases**, described as 13,092 training and 897 test, across 30+ specialties. **Internal numeric inconsistency:** 13,092 + 897 = 13,989, not 14,489; do not claim the split reconciles without inspecting actual dataset. The total count and split must be independently checked in files/data card.
- **Fields:** `case_prompt`, `diagnostic_reasoning`, `final_diagnosis`, and manuscript/PMC extraction routines according to README.
- **Rights:** code MIT per README; dataset CC BY 4.0 per GitHub README, while HF dataset metadata and source-article rights still require examination. Model checkpoints separate.
- **Game use:** a high-volume *authoring source* for differential diagnoses, initial presentations, hidden diagnoses, reasoning rubrics and candidate case metadata. It is **not** automatically a validated interactive game or a collection of free-to-republish figures. Convert source narrative to an authored event timeline and verify causal assumptions.
- **Critical safety:** the reference diagnosis/reasoning should remain outside learner-visible prompts, API responses and client bundle until debrief.

### D2. MultiCaRe — multimodal published cases and medical figures

- **Repository:** [mauro-nievoff/MultiCaRe_Dataset](https://github.com/mauro-nievoff/MultiCaRe_Dataset).
- **Hugging Face:** [mauro-nievoff/MultiCaRe_Dataset](https://huggingface.co/datasets/mauro-nievoff/MultiCaRe_Dataset).
- **Zenodo dataset:** [MultiCaRe record](https://zenodo.org/records/10079370) (resolve record/version-specific actual rights before import).
- **Earlier reports:** roughly 98k+ case snippets and 139k+ related medical figures in some advertised versions; different versions may have different figures or counts. The important capability is linking source clinical narratives and image metadata.
- **Rights conflict:** GitHub README describes CC0/open source; Hugging Face metadata marks CC BY 4.0; an earlier Zenodo record displayed CC BY-NC-SA. There is **no justified blanket license declaration** covering every published article, figure and derivative. The original content license, article ID, authors, restrictions, version and transformation chain must be recorded for each candidate game asset.
- **Decision:** major **discovery/indexing** source, with per-case clearance and expert curation, not an unrestricted asset warehouse.

### D3. PMC Open Access Subset and Europe PMC

- **Primary source:** [NCBI PubMed Central Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/).
- **Related:** [Europe PMC](https://europepmc.org/).
- **Function:** original source articles, figures, reference diagnoses, clinical narratives, metadata, rights and citation provenance; supports reconstruction of the real source to resolve ambiguity from dataset aggregators.
- **Restriction:** 'readable through PMC' does not mean a work is in the OA subset; even items in the subset may carry different Creative Commons conditions. Some figures have rights separate from surrounding article text. Favor a per-figure license ID and exact source URL.
- **Game use:** select articles with permitted commercial redistribution and strong clinical teaching value; author fictionalized, clearly differentiated cases and record what aspects were drawn from literature.

### D4. PMC-Patients dataset

- **Repository:** [zhao-zy15/PMC-Patients](https://github.com/zhao-zy15/PMC-Patients).
- **Site:** [PMC-Patients homepage](https://pmc-patients.github.io/).
- **Reported scale:** ~167,000 case-report-derived patient summaries, with article and similar-patient retrieval relations.
- **Rights:** assembled dataset README declares **CC BY-NC-SA 4.0**. Even if public download is possible, it is **not** an unrestricted commercially reusable corpus.
- **Value:** research on case retrieval, comparing diagnoses and finding similar presentations. **Keep outside any permissive/commercial package** absent alternative rights or permission. Its code/data may have different legal terms.

### D5. MIMIC-IV and MIMIC-IV-ED public demos

- **Clinical demo:** [MIMIC-IV Clinical Database Demo](https://physionet.org/content/mimic-iv-demo/2.2/).
- **Emergency-department demo:** [MIMIC-IV-ED Demo](https://physionet.org/content/mimic-iv-ed-demo/2.2/).
- **Official character:** deidentified 100-patient demonstrations from a larger restricted clinical dataset; database fields include encounters, triage, vitals, medications, diagnoses and laboratory examples where the respective release supplies them.
- **Difference from full MIMIC:** credentialing, DUA, sharing restrictions and distinct source access rules apply to full MIMIC, notes, CXR, and other associated datasets. **Never package full restricted real patient records** into the game merely because they are useful for realism. The freely accessible demos have their own explicit database license and citation terms.
- **Best use:** model believable test/result formats, trends, arrival/collection/report times, chart navigation, emergency-department flows and SQL-style realistic schemas—not necessarily as player-facing real patient encounters.

### D6. PhysioNet waveform ecosystem

- **Catalog:** [PhysioNet databases](https://physionet.org/about/database/).
- **Supporting code already indexed:** [WFDB Python](https://github.com/MIT-LCP/wfdb-python) at #74, plus ECG format conversion #78.
- **Use:** reference ECGs, multiparameter signals, annotations and time alignment in medically meaningful formats. Rights are **dataset-specific**, and some PhysioNet collections require credentialed access or a data-use agreement.
- **Engineering use:** offline transform a properly licensed real recording into a medically faithful ECG study, with exact sample rate, units, lead names, filter settings, acquisition time and provenance.

### D7. Synthea fixtures (relation to S1)

See [Synthea S1](#s1-synthea--synthetic-patient-population-simulator). Synthea should fill gaps in **synthetic longitudinal EHR fixtures** and generated medication histories; it does not substitute for pathology-validated 12-lead ECG, ultrasound or real DICOM imaging.

### D8. Research-only additional dataset leads from earlier conversations

- **CUPCase** (research publication earlier recorded as [arXiv:2503.06204](https://arxiv.org/abs/2503.06204)): an earlier project chat mentioned roughly **3,562** extracted case reports. Dataset license and distributions were **not** independently checked here.
- **PMOA-TTS** (earlier recorded [arXiv:2505.20323](https://arxiv.org/abs/2505.20323)): an earlier project chat mentioned **124,699** OA case reports / structured temporal content. Treat both counts and repository/corpus rights as unverified until official source inspection.
- **Medical article examples** from older project browsing: `PMC4863315`, `PMC12475988`, `PMC12607131` and others were example source IDs, **not separate redistributable repositories**.
- **Radiopaedia, journal case reports and other teaching cases:** often highly instructive but not automatically reusable in a new game. The original license of every text, image, video, and annotation matters.

## VI-C. Summary of older report leads and false positives

The earlier broad 'Games and Modules' report also mentioned quickcardboard ECG Studio, EKG Maker, a standalone 12-lead ECG viewer, the TUM-style virtual patient site, and lightweight narrative/minigame ideas. The most important corrected conclusions are: **DWV is GPL rather than MIT; GTAgentClinic case content is CC BY rather than NC; Open Sim Lab has 256 scenarios rather than 256 laboratory assays; WebGL2 fallback exists; Infirmary Integrated is a C# desktop suite, not a demonstrated Unity engine**. Older project-specific framework proposals unrelated to this game's architecture have deliberately **not** been imported into this inventory.

---

# PART VII — INTEGRATION DESIGN, MEDICAL COHERENCE, AUTHORIZATION AND VALIDATION

This part is an **engineering synthesis** of all retrieved research, designed to turn repository discovery into a working demonstration. It does not claim any of these contracts has already been implemented.

## VII-A. Architecture: authoritative clinical state plus interchangeable investigation workstations

**Do not merge six complete 'patients' into one game.** Each candidate base already has its own internal state, time progression, prompts or scoring, and each physiologic instrument may have a different simplified physiology. The game should have **one source of clinical truth**. Individual modules should accept explicit, typed state and return either a displayed artifact or a verified observation. A third-party simulator that cannot be controlled by external state must run in a bounded adapter, be replaced with curated media, or be omitted from a specific case.

Recommended logical layers (not a mandate for programming language, process model or database):

1. **Case definitions / assets**: source-linked authoring, diagnoses, disease mechanisms, examinations, tests, expected results, normal ranges, clinical media and licensing ledger.
2. **Private case authority**: hidden diagnosis and constraints; patient physiology; scenario clock; clinical event log; treatment state; truth/provenance; permitted results and NPC knowledge.
3. **Action and order engine**: validated game actions (`ask_patient`, `examine`, `order_test`, `collect_specimen`, `review_result`, `administer_drug`, `consult`, `submit_differential`, `final_diagnosis`).
4. **Projection / acquisition layer**: releases only information discoverable by the specified learner or NPC at the recorded time. Handles acquisition, result availability, acquisition artifacts and serial comparisons.
5. **Modality adapters**: Patient Monitor Engine, 12-Lead Generator, EchoSim, OHIF/Cornerstone3D, SimEHR, Epicurrents, Open Vent Sim, pathology and optional physiology.
6. **AI presentation layer**: LLM controls *wording and behavior within authorized facts*. System prompts and tools are assembled by trusted code; the browser cannot rewrite hidden case prompts or invoke any tool with unconstrained credentials.
7. **Evaluator/debrief**: scores meaningful reasoning/actions using event traces, constraints, clinical references, known uncertainties and expert-reviewed rubrics.

### Who owns truth?

| Variable / artifact | Authority | Presentation / generation options | Common failure if poorly integrated |
|---|---|---|---|
| Hidden diagnosis, cause, disease progression | Case engine, authored reference | Not visible to player until feedback permits | Source answer leaks into client/prompt |
| Patient report, memory and personality | Case knowledge + dialogue policy | Virtual Standardized Patient / PatientsWithPersonality | AI reveals facts it should not know |
| Rhythm and ECG pathological state | Case authority; validated ECG model | Monitor Engine / 12-Lead Generator / licensed real data | ECG says one rhythm; pulse another |
| Mechanical circulation, pressure, saturation | Shared physiology or authored measurements | Monitor Engine / Pulse / curated recordings | Electrical ECG rhythm mistaken for perfusion |
| Echo heart anatomy, EF, valve lesion | Authored pathology + validated signal/view mapping | EchoSim or licensed cine | Fake echo looks normal during severe dysfunction |
| CT/MRI/X-ray series and radiologist report | Curated study provenance and case time | OHIF/Cornerstone/VolView | DICOM presented without corresponding diagnosis |
| EEG / EMG and annotations | Curated/simulated study and reference | Epicurrents / MNE / EDF assets | Electrode/format/sampling mismatch |
| Labs, units and timing | Case authority + verified reference set | SimEHR and case lab UI | Impossible test value or instant results |
| Drug administration and interventions | Action/event log + physiology rules | Device UI / EHR / monitor | 'Ordered' conflated with 'given' |
| Player evaluation | Hidden authored rubric + event history | Debrief/grading UI or AI explanation | LLM invents grading criteria after outcome |

### Suggested *illustrative* case-result contract (not previously shipped)

```json
{
  "case_id": "example_case_001",
  "session_id": "opaque_session_id",
  "sim_time_seconds": 840,
  "actor": "learner",
  "available_actions": ["order_test", "review_result", "examine"],
  "test_result": {
    "order_id": "ord_012",
    "test_code": "ECG_12_LEAD",
    "status": "resulted",
    "ordered_at_seconds": 360,
    "acquired_at_seconds": 660,
    "reported_at_seconds": 720,
    "observations": [{"code": "HEART_RATE", "value": 108, "unit": "beats/min"}],
    "artifact": {
      "kind": "ecg_waveform",
      "asset_ref": "study/001/ecg/trace-01",
      "provenance_ref": "license-ledger/asset-0001"
    }
  }
}
```

A player-facing response must **not** contain `true_diagnosis`, hidden lesion definitions, secret case prompt, unreleased test findings or hidden evaluator rubric. Those fields belong in privileged author/admin or controlled debrief data, never in a client-bundled JSON file. Even a permissive but sensitive study could require signed retrieval and access logging.

## VII-B. Acquisition and time semantics

An investigation is more than a button that reveals a static text string. Distinguish **ordered → accepted → specimen/image acquired → processing → validated → released → viewed**, with explicit timestamps. A sample might be rejected; a machine could be unavailable; a result might be delayed or repeated; and a treatment given between samples can alter later measurements. Calendar-independent **simulation time** should be monotonic and replayable; wall time can drive UI animations without altering clinical truth.

Use deterministic replay where possible: same case seed + same sequenced interventions should yield the same authored observations, except for explicitly modeled stochastic effects with seeded randomness. Keep assessment inputs separate from presentational/agent output logs.

## VII-C. ECG investigation design

The player may need three different screens, which should not be confused:

1. **Continuous telemetry/bedside ECG:** timed traces, heart rate and alarms, alongside pleth, pressure, capnography and respiration. Candidate: Patient Monitor Engine; Infirmary Integrated as device-interaction reference.
2. **Diagnostic 12-lead ECG:** proper limb/precordial lead labeling, paper speed, gain, intervals, lead placement, repeat studies and interpretation. Candidate: 12-Lead Generator; ECG Atlas for electrode placement and measured/synthetic provenance; WFDB and PhysioNet for recorded examples.
3. **Electrophysiology teaching view:** explanatory conduction/activation and mathematical models. Candidates: MIT 3D heart simulator, restricted CardioSim Lab, and conditional ECG Studio. This is *optional* and not the core diagnostic instrument.

Test one clinically plausible ischemia/conduction/electrolyte scenario in synchronized telemetry and 12-lead output. Verify P/QRS/T morphology, PR/QRS/QT intervals, sampling, gain and temporal onset. Compare machine-derived numerics with underlying traces. A heart-rate number must not come from an independent slider if the waveform contradicts it.

## VII-D. Echocardiography and ultrasound design

**EchoSim is the primary legally plausible interactive procedural base** because it is MIT and provides a coherent 3D heart, synthetic B-mode output, Doppler, hemodynamic links, ECG and calipers. It is a **teaching simulator with incomplete external clinical validation**, not a clinically certified tissue ultrasound engine.

Separate at least four tasks:

- **Acquisition:** virtual probe pose, standard views, imaging plane, gain/depth/focus, Doppler mode and patient-position constraints.
- **Display:** ultrasound-like speckle, image geometry, cine timeline and measurement overlays.
- **Pathology:** authoritatively defined chamber size/function, valve disease, wall-motion abnormalities, pericardial fluid or hemodynamic lesions.
- **Interpretation:** player measurements, report writing and clinical comparison to history/ECG/labs, with blinded case truth.

Test whether changing an external valve/pathology setting affects the ultrasound view, derived measurement and corresponding case physiology together. If realistic pathology synthesis is unsupported, use **licensed real cine loops** in the interpretation pathway instead of producing plausible-but-wrong images. PyMUST, USTB, PyUS and OTC-Flow are research candidates, not default replacements.

## VII-E. CT/MRI imaging, radiology and pathology

OHIF + Cornerstone3D is the main browser-native DICOM workstation family; choose **OHIF when its full clinical UI is wanted** and **Cornerstone3D alone for a narrow custom interface**. Avoid importing both as if independent renderer engines. Offer window/level, navigation through image series, MPR/orientation, measurement annotations and report-entry controls appropriate to each study. A game needs real or convincingly valid images—not just an image-viewer dependency.

**VolView** adds an appealing volume-rendering comparison. **Meridian / Circinus / Papaya** offer lighter options with different maintenance and license verification requirements. **Orthanc** is an optional server when storage, query/retrieve and DICOMweb ingestion become necessary. **pydicom** is a preprocessing/metadata tool, not a UI. **IDC Slim / OpenSeadragon** solve digital pathology/whole slides, not radiology CT/MR stacks. The model should distinguish all of these tasks.

Keep an asset manifest with study instance identifiers, modality, body region, diagnosis relevance, orientation, acquisition phase, timestamp, slice count, format, source link, licence type, required attribution and editorial approval. Do not render an MRI just because a patient requested one; a valid corresponding study must exist or the game must report its unavailability.

## VII-F. EEG, EMG, invasive/respiratory and complex ICU investigations

Epicurrents provides the principal web electrophysiology *viewer/workstation family*. MNE and EEG Simulator are offline computation/data-generation support; EDF/DICOM waveform readers are data importers. Preserve montage, channel scaling, acquisition clock, filtering, artifact and reference electrode definitions. For EMG, audio can be useful but each source recording needs rights.

Open Vent Sim is a strong candidate for ventilator modes/pressure–volume–flow visualization. Full-system ICU integration should await a narrower validated scenario. BioGears and Kitware Pulse are rich research engines for gas exchange and drug effects but have substantial native interfaces and model limitations; neither guarantees all physiological organ systems or clinically correct imaging.

## VII-G. Patient AI, tool authorization, outcome and grading

An AI patient can be reluctant, inaccurate about self-reported history, emotional, confused or forgetful, while the **objective case facts remain stable**. Split `case_truth`, `patient_known_facts`, `patient_persona`, `clinician_observable_data` and `answer_key`. The AI must not independently authorize a test, release a result, administer a drug, change time, or assign final clinical truth. Let models explain already-approved observations rather than invent observations.

Security and game-integrity checks:

- An authenticated learner may retrieve allowed active-case metadata, but **never** hidden diagnosis, complete scenario configuration, correct treatment sequence or private grader rubric through normal APIs.
- Any patient/persona system message is created in a trusted execution context, not concatenated from arbitrary learner-controlled text.
- AI tool calls are allow-listed per role/session/phase; `order_test` requires a known catalog item and affordability/timing rules; results come from the canonical case, not from a general chat reply.
- A nurse, consultant, family member and simulated patient have **different knowledge**. The assistant/LLM must not automatically see all information just because the server knows it.
- Every action is logged, auditable and replayable. Validation and clinical scoring can be repeated from the event trace without the same language-model wording.
- A user may enter text designed to reveal spoilers or rewrite instructions; tests should prove that such requests do not reveal the answer or alter the case.

For grading, preserve ordered tests and interpretation, sensitivity to red flags, adverse treatment decisions, delays, differential quality, justification and final diagnosis as distinct dimensions. A fixed total score is not necessary; an evidence-backed multidimensional debrief is safer than a single arbitrarily generated grade.

## VII-H. Minimal technically meaningful benchmark

### Common authored case (same source of truth)

Use one moderate-complexity emergency diagnostic case with symptoms that can point to multiple disorders, an evolving course, discordant subjective history, serial vitals, 12-lead ECG, an echo or imaging study, at least two laboratory collection times and an intervention. An acute dyspnea + cardiac differential is a useful example *only when the chosen source material and output models support all requested observations*.

### Spike A — foundation game comparison

- **A:** Open Sim Lab
- **B:** GTAgentClinic
- **C (limited historical donor):** Rohy May 8 MIT-covered first-party workflows, after removal of unauthorized dependencies/assets

Evaluate: can the same case load? how are hidden facts stored? how do clinician actions advance time? do orders have distinct collection/report times? can an NPC leak diagnosis? can the application produce deterministic replay? how much of the UI can be embedded? what existing code must be rewritten? what is test/documentation coverage? how many dependencies are unmaintained or restricted?

### Spike B — diagnostic instrument compatibility

- Patient Monitor Engine + 12-Lead Generator + one properly licensed WFDB recording
- EchoSim independent blinded study with a known case pathology
- OHIF with one licensed anonymized DICOM study
- SimEHR case order/result/notes flow

Demonstrate that `case_id`, `sim_time`, disease state and result provenance remain consistent between all screens. Judge with objective automated assertions rather than aesthetics alone.

### Spike C — medical cross-modality consistency

Use a test matrix with columns `case state | ECG waveform | arterial pulse | SpO2 | ABG | echo | labs | interventions | expected discrepancies`. Specify acceptable tolerances and forbid impossible contradictions. Repeat at t0, after first test, after treatment and at debrief. Distinguish signal artifacts from true disease changes.

### Spike D — licenses and source reproducibility

For every directly imported file, record upstream repository, commit SHA, path, full license text/NOTICE, author, source asset, dependent libraries/models, local modifications and distribution purpose. Run clean-checkout tests and a third-party dependency vulnerability review. Any unresolved license puts a hard stop on copying that file.


### Expanded ten-experiment technical adoption matrix (detailed-source audit)

The following is the **full additional testing matrix** from the latest uploaded research. It supplements, rather than replaces, the general spike definitions above. Each experiment tests a potential implementation dependency or medical validity failure. No test below is claimed to have been run.

| Experiment | Repositories to compare | Implementation probe | Pass/fail criterion |
|---|---|---|---|
| Patient-case foundation | GTAgentClinic, Open Sim Lab, Simu_Patient (SimuPatient in source) | Same blinded neuro/endocrine case; history questions, repeated labs, deterioration and post-case reconstruction | Case facts never contradict; temporal and permission gates work; evaluator never sees unavailable tests |
| EHR | SimEHR and GTAgentClinic EHR | Create synthetic CBC, CMP, medication order, pending MRI and follow-up result for one patient | Patient ID/unit/timestamp correct, no leakage of unreleased findings, full audit log |
| ECG | Patient Monitor Engine, 12-Lead Generator, NeuroKit2, WFDB | Capture sinus, hyperkalemia and rhythm abnormality in pre-/post-treatment states; compare to independent approved real cases | Consistent 12-lead morphology, timing, artifact flags and perfusion/ECG separation |
| Echo | EchoSim, real cine clips in OHIF, optional SonoForge | Review normal LV and a clinical abnormality; compare EF, Doppler, wall motion and blind-mode acquisition | Measurement units and geometry coherent; experts can recognize intended pattern; no viewer settings leak diagnosis |
| Ultrasound physics | PyMUST, USTB, PyUS | Same known synthetic phantom/scatterer geometry through beamforming and display | Numerical/test-case agreement and acceptable runtime; no unwarranted claim of disease-specific realism |
| MRI/CT | OHIF, Meridian, Circinus, VolView | Same de-identified DICOM CT/MRI study with nonaxial planes, VOI LUT, pixel spacing and measurements | Correct orientations, physical measurements and windowing; reliable loading across supported codecs |
| Neurophysiology | Epicurrents, EEG Simulator, WFDB/EDF | EDF/EDF+D montage, annotations and seizure/artifact case | Correct units/time discontinuities and montage behavior; relevant pathology not fabricated by random noise |
| Physiology | Kitware Pulse, BioGears, Patient Monitor Engine | Identical modeled adult shock/respiratory intervention sequence with repeat vitals and blood gases | Stable numerical traces in validated parameter domains; explicit detection of unsupported states |
| Dialogue | PatientsWithPersonality, PatientHub, PatientSim, Simu_Patient (SimuPatient in source) | Hidden diagnosis, suggestive question, misunderstanding, memory challenge and repeat patient request | No hidden fact leakage or impossible certainty; stable patient memory and auditable disclosure |
| Case generation | AetioMed, DiagGym | Generate 20 draft cases, run blinded investigation, compare against checked authored truth | No contradictions, hallucinated normal tests or unaudited medical claims; no unlicensed case data |

These tests are **proposed acceptance criteria**, not work claimed to have been executed in this report.

## VII-I. Risks and mitigation register

| Risk | Example | Mitigation / gate |
|---|---|---|
| Hidden answers leak to client | Historical Rohy GET /cases exposes full config | Default-deny projections and browser/network tests |
| Prompt manipulation | Client appends own system prompt | Server-owned persona assembly and role authorization |
| Physiological contradiction | Monitor VF but normal arterial pressure | Shared state, cross-module tests and curated fallbacks |
| Visually plausible but medically false echo | Wrong valve anatomy or EF | Expert comparison and real cine as needed |
| License contamination | Restricted pathology image shipped in MIT code | File/asset-level rights ledger with commit/source ID |
| False clinical license assurance | HF card says MIT, base weights not audited | Inspect base model, training sources and checkpoint terms |
| Overcomplex first version | Native whole-body engine added prematurely | First prove one narrow end-to-end playable case |
| Legacy/archived dependency | OLab4 hardcoded demo secrets | Research only, do not deploy; choose maintained modules |
| Non-reproducible grading | LLM reinterprets answer key | Authored rubric and event-history scoring |
| Device UI looks right but inputs wrong | ECG caliper scale mismatch | Numeric tests, calibration and expert review |
| Wrong artifact delivered for an order | MRI result without MRI media | Type-checked study manifests and no-fabrication policy |
| Privacy issues | Clinical real-world samples repackaged | Licensing, data-use and de-identification gate |

## VII-J. Suggested incremental delivery sequence

**Stage 0 — choose a clinical truth design** and one appropriately licensed source case; create the private/public visibility boundary, timeline and logging, before lifting game UIs wholesale.

**Stage 1 — one end-to-end patient:** history, exam, vitals, a few preauthored labs, an ECG and differential/debrief. Use a target base only after a side-by-side spike.

**Stage 2 — serious reading workstations:** DICOM imaging via OHIF, echo via EchoSim or real clips, SimEHR chart/orders, waveform ingestion through WFDB and test ordering with realistic turnaround times.

**Stage 3 — advanced case dynamics:** ICU ventilation, EEG, pathology, consultations, more extensive physiology and medically reviewed intervention responses. Defer the heaviest native engines until their value is demonstrated.

**Stage 4 — source content scaling:** license-validated clinical media library, Synthea fixtures, PMC/MedCaseReasoning/MultiCaRe discovery tools, standardized case authoring and educational quality control.

This sequence is a **dependency-based roadmap**, not a calendar promise. Earlier reports' 3–24-month schedules were unsupported without a benchmark of the team, scope and technology choices.

---

# PART VIII — COMPLETE ROHY HISTORICAL CODE, LICENSING AND SECURITY FORENSICS

The following retains the substantive detailed Rohy investigation in the uploaded 704-line audit, including commit history, comparison counts, vendor-code rights, confirmed structural weaknesses and safe extraction gates. **A historical MIT root license is not permission to copy current Carm-restricted source.**

### Decision in brief

**The best identifiable pre-Oyon revision is commit [`d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd`](https://github.com/mohsaqr/rohySimulator/tree/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd), committed 8 May 2026 at 17:56:53 UTC.** It declares package version `1.0.0`, has an MIT root `LICENSE`, and its Git tree has **no `OyonR/`**. This is a **historical commit, not an official release**: the first published GitHub release `v1.0.0` is dated 10 May 2026, after OyonR had been added.

This commit is an **MIT-licensed application-code baseline**, **not** proof that every file or dependency in the checkout is MIT. The repository contains separately licensed reference data and third-party avatar/audio assets. For adaptation and redistribution, check individual files and omit anything without an appropriate grant. **No unmodified full-repository snapshot was certified 100% MIT-only.**

### Evidence for the cutoff

- [`d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd`](https://github.com/mohsaqr/rohySimulator/commit/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd): final parent of the first OyonR-vendoring commit. Historical root `LICENSE` is MIT, and `package.json` says `"license": "MIT"`.
- [`7093edc1d349e94882a960c5fa3c865f13598b66`](https://github.com/mohsaqr/rohySimulator/commit/7093edc1d349e94882a960c5fa3c865f13598b66): **9 May 2026**, "Unified learning analytics, data grid viewers, Oyon capture engine". Adds `OyonR/`, including `OyonR/LICENSE` under Carm terms. The presence of an MIT *root* license after this commit is not sufficient to give MIT rights to the vendored addon.
- [`v2.9.12`](https://github.com/mohsaqr/rohySimulator/tree/v2.9.12): published 30 July 2026; an example of the misleading transitional period. The root `LICENSE` still declared MIT, but `OyonR/LICENSE` already declared Carm.
- [`84a35664f33e48871714e94427c66369d5317713`](https://github.com/mohsaqr/rohySimulator/commit/84a35664f33e48871714e94427c66369d5317713): **31 July 2026**, replaces the MIT root license with Carm Research License v1.4, expressly mentioning its conflict with OyonR.
- [`5460de92f53330a4b704c44bc35597ec293fadbe`](https://github.com/mohsaqr/rohySimulator/commit/5460de92f53330a4b704c44bc35597ec293fadbe): current `main` inspected 19 November; committed 14 November 2026; `package.json` version `3.1.5`. Latest published GitHub *release* retrieved was `v3.1.3` (2 November 2026).

### Licensing issues in the May 8 checkout

1. **CALIPER pediatric ranges** — `server/data/lab_pediatric_ranges.json` directly declares `"license": "CC BY-NC-SA"`. Keep it excluded from a permissive-only derivative, replace with independently licensed reference intervals, or obtain proper permission.
2. **External sequence-analytics dependency** — `package.json` references `"dynajs": "file:../dynajs"`. The historical `mohsaqr/dynajs` snapshot at [`96c1d82` (4 April 2026)](https://github.com/mohsaqr/dynajs/tree/96c1d82c4ba4b5a3b8ffc7b59ac8c093c0596660) declares MIT in `package.json` and its README; it does not have a standalone LICENSE file at that commit. Current `dynajs/main` instead has the Carm Research License. **Do not install current dynajs/main as if it were MIT**. Pin the original historical dependency, and retain evidence of its historical grant (or replace that analytics library).
3. **3D head models** — the May `public/avatars/heads/manifest.json` identifies two MIT sources: [Microsoft RocketBox](https://github.com/microsoft/Microsoft-Rocketbox) and [met4citizen/TalkingHead](https://github.com/met4citizen/TalkingHead). Both upstream projects currently have MIT `LICENSE` files, but verify each derived asset's provenance, preserve credits/notices, and be careful with downstream textures/conversions.
4. **Auscultation recordings and other media** — `public/sounds/normal-heart.mp3` and `normal-lung.mp3` were committed, but no per-asset license/provenance was located. The later licensing commit explicitly identified unclear auscultation-audio provenance. Exclude/relicense until cleared.
5. **General** — MIT licenses Rohy's own covered material, not automatically everything downloaded or vendored into it. Review other sample case images, model checkpoints, external service SDKs, dependencies and data before republishing.

### Capability comparison: last pre-Oyon MIT code vs current Rohy

| Capability | May 8 2026 pre-Oyon revision | November 14 2026 main (`3.1.5`) | Effect on your diagnostic game |
|---|---|---|---|
| AI patient interviews | Yes: text, streaming, configurable local/cloud LLMs | Yes: expanded | **Small gap** |
| Multi-agent consultation | Five roles including patient, nurse, consultant, family, discussant | Expanded roles and workflows | **Small–medium gap** |
| Live vitals + scenarios | Seven monitored vital parameters, five base ECG rhythms, nine modifiers, timeline interpolation | Expanded monitoring and case state | **Moderate gap** |
| Treatments | 33 default interventions with time-dependent effects and custom medication authoring | Expanded interventions/workflows | **Small–medium gap**, but educational model still requires validation |
| Labs, orders, reporting | README advertises 225 test entries, 32 panels, 74 radiology investigations, report and media attachment | Expanded, including specialist workstations | **Small gap for ordering; large for interpreting real imagery** |
| Physical examination | Body-map 67 named regions; techniques and findings | Expanded and integrated | **Small–medium gap** |
| ECG diagnosis | ECG monitor and rhythm generator; no separate dedicated 12-lead ECG reading plugin | Dedicated `cardoyon` 12-lead workstation with calipers, paper speeds, filters, lead-linked notes | **Large gap** |
| CT/MRI viewer | Orders, reports, and upload/display of attached media | DICOM PACS reading room (`radoyon`) with stacks, windowing, cine, measurements | **Large gap** |
| Echo | Echo is in radiology study catalog / can attach results | No dedicated real-time procedural echo system established in review | **Both need external echo module** |
| Pathology | No dedicated WSI/microscopy workstation | `pathoyon` whole-slide reading and reporting | **Large gap if pathology central** |
| 3D | Talking-head avatars and viseme lipsync | Adds 3D bedside room via separate `rohy-3d-patient-room` package | **Medium gap**, less critical than diagnostic workflows |
| Cases and instructor authoring | 12-step wizard; 16 prebuilt scenarios and JSON import/export | Courses, cohorts, lessons and additional authoring workflows | **Medium gap** |
| Analytics / education | TNA and detailed event log, questionnaires | Multimodal/affect/gaze analytics, expanded event stream and cohort dashboards | **Medium–large gap** for institutional research; less relevant to single-player game |
| Languages | No equivalent comprehensive i18n framework confirmed | Eight interface languages | **Medium gap** if multilingual release desired |
| Test/deployment infrastructure | Vitest, Playwright, CI, auth, audit, observability | Much broader suites, plugin checks, fuzzing, documentation, deploy checks | **Large quality/operations gap**, not simply feature count |

**Important:** The May README **claims** 695 passing tests; those tests were not executed as part of this remote inspection. The presence of tests and CI scripts does not prove clinical accuracy or production security.

### Objective repository growth

Both trees were enumerated via GitHub's recursive Git Tree API, excluding directory entries:

| Git-tree metric | May 8 revision | Nov 14 `main` |
|---|---:|---:|
| All tracked files | **512** | **3,481** |
| Files inside `src/` | **212** | **1,196** |
| Files inside `server/` | **61** | **197** |
| Files inside `tests/` | **69** | **400** |
| Tracked migration `.sql` files | **10** | **77** |
| Commits after May 8 | — | **625** (GitHub compare reports ahead=625, behind=0) |
| Separate dedicated PACS/ECG/pathology components | No | Yes; vendored specialist plugins |

File counts are **not** quality or functionality scores. The old version also had large monolithic files (`src/components/settings/ConfigPanel.jsx` around 290 KB and `src/components/monitor/PatientMonitor.jsx` around 119 KB); current `main` still includes large central components. Reusing the project wholesale will incur substantial refactoring.

The separate latest ECG/PACS/pathology workstations in Rohy are explicitly stamped as vendored from `cardoyon`, `radoyon` and `pathoyon` (`.vendor.json`). The upstream repositories were not publicly retrievable at the inspected GitHub paths, so **do not assume their code has an MIT grant**. Instead, consider independently licensed alternatives: OHIF / Cornerstone3D for DICOM, OpenSeadragon or another approved viewer for pathology, and MIT ECG projects from the existing repository audit.

### Recommendation

**Worth using? Yes, selectively — not as an untouched drop-in platform.** The 8 May version is already a meaningful end-to-end clinical encounter foundation: case authoring, dialogue/agents, examinations, test ordering, time-dependent interventions, ECG monitor, debrief, and analytics. For a reusable open-source project, its historical MIT grant is significantly more attractive than current Rohy's custom license.

**What to copy first after attribution and dependency checks:** authoritative clinical action/event records; case and scenario data models; order/treatment flows; patient/exam UI; AI patient/consultant prompt boundaries; debrief and seed-case scaffolding. Refactor large React components and independently validate medical simulation assumptions.

**What to replace rather than backport from current Carm code:** the dedicated 12-lead ECG room, DICOM reading workstation, pathology reader, 3D room, and later platform internals. Use separately licensed modules and a documented adapter contract. Taking general design ideas is different from copying a restricted implementation.

**Reasons not to adopt it as your main game wholesale:** older security patches, large UI monoliths, historical dependencies that need pinning, mixed data/media licenses, and likely work to isolate simulation state from presentation. The old version's 695 passing tests are README claims rather than re-run evidence.

**Decision:** **Strong candidate as an MIT-covered clinical workflow donor; moderate candidate as a direct fork of the entire game.** Prioritize the clinical consultation + action/state model. If you mostly need modern imaging, detailed ECG, echo, or pathology, combining independent permissive modules is more practical than trying to modernize the entire 8 May fork.

**Verification boundary:** This is a review of GitHub commit history, tree metadata, documentation, package manifests and selected source files. No full source checkout/test run, binary license forensic analysis, or legal opinion was performed. Obtain written permission or use a verified replacement for uncertain files.


---

## Rohy follow-up: recovered compare, clinical integrity and refined decision — 19 November 2026

### A. What failed in the large comparison response

The GitHub compare endpoint returned `ahead_by: 625` for [`d5f14e6` → `5460de9`](https://github.com/mohsaqr/rohySimulator/compare/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd...5460de92f53330a4b704c44bc35597ec293fadbe), but its per-file list is capped at 300 changed files. The surfaced response was interrupted/truncated while listing the `OyonR/` changes. **Do not interpret the first 300 changed-file entries as a complete diff.** To recover, both exact revision trees were independently enumerated through GitHub's recursive Git Tree API; neither tree was flagged as truncated.

| Verified measure | MIT-era candidate — May 8, `d5f14e6` | Current inspected — Nov 14, `5460de9` |
|---|---:|---:|
| Git-tracked files (blobs) | 512 | 3,481 |
| Frontend `src/` | 212 | 1,196 |
| Backend `server/` | 61 | 197 |
| `tests/` | 69 | 400 |
| SQL migrations | 10 | 77 |
| OyonR addon files | 0 | 848 |
| `website/` files | 0 | 361 |
| `docs/` files | 0 | 153 |
| Commits after base | — | 625 |

**First-party code continuity:** Among the 145 tracked files under the May version's `src/components/`, `src/services/`, and `src/hooks/`, 23 were byte-for-byte unchanged at the November revision, 109 retained the same path but changed, and 13 no longer existed at that path. This is a file-level measure only; renamed files are counted as missing at the old path, not necessarily deleted functionality. The current code genuinely differs from the old one even where the feature names are the same.

### B. Newly verified, high-impact flaw in the May 8 design: learner-visible case answers

This is the **most important engineering finding** beyond the feature list. The May version is **not secure against a curious player inspecting network requests or modifying their own browser**.

**Original code evidence (exact historical commit):**

1. [`server/routes/cases-routes.js` lines 128–193](https://github.com/mohsaqr/rohySimulator/blob/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd/server/routes/cases-routes.js#L128-L193) — `GET /cases` and `GET /cases/:id` use `SELECT *` and return all case fields, including parsed `config` and `scenario`, to authenticated learners. Visibility `is_available` is not field-level secrecy.
2. [`src/components/chat/ChatInterface.jsx` around lines 487–533](https://github.com/mohsaqr/rohySimulator/blob/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd/src/components/chat/ChatInterface.jsx#L487-L533) — the browser assembles the patient prompt from the full case configuration and medical-record content described as hidden.
3. [`src/utils/casePromptContext.js` around lines 258–279](https://github.com/mohsaqr/rohySimulator/blob/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd/src/utils/casePromptContext.js#L258-L279) — full case context includes an explicit `Expected diagnosis` field for discussant/debrief contexts.
4. [`server/routes/proxy-routes.js` lines 158–159 and 475–480](https://github.com/mohsaqr/rohySimulator/blob/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd/server/routes/proxy-routes.js#L475-L480) — the LLM proxy accepts a client-supplied `system_prompt` and appends it to its own system prompt template. A learner could manipulate the client-provided context. This is a game-integrity weakness even if infrastructure-level usage controls still apply.

**Current code's documented repair:**

- [`server/services/caseProjection.js`](https://github.com/mohsaqr/rohySimulator/blob/5460de92f53330a4b704c44bc35597ec293fadbe/server/services/caseProjection.js) — role-specific, allow-listed case projections intended to omit title, expected diagnosis, prompt and answer-key fields from ordinary learner responses; added plugin-document handling.
- [`server/services/patientPersona.js`](https://github.com/mohsaqr/rohySimulator/blob/5460de92f53330a4b704c44bc35597ec293fadbe/server/services/patientPersona.js) — the patient system prompt is assembled server-side from the session's saved case snapshot. Its opening comment explicitly describes why the old browser-built design exposed answers and permitted prompt manipulation.
- [`server/routes/proxy-routes.js` around lines 474–500 and 1059–1082](https://github.com/mohsaqr/rohySimulator/blob/5460de92f53330a4b704c44bc35597ec293fadbe/server/routes/proxy-routes.js#L1059-L1082) — server-resolved patient/discussant prompts take priority; client-supplied persona prompt is dropped. Do not copy this code into an MIT-only fork: it was written after the applicable relicensing boundary and is under the current project's license.

**Implication:** The old code is a promising **workflow and UI donor**, but it should **not** be used unchanged as the authoritative game server. Implement separate, new server-side case-authority logic: (a) hidden case answer key in server-only storage, (b) learner response schemas with default-deny field projection, (c) server-generated prompts and verified agent knowledge scopes, (d) logged action/order/test state, (e) tests proving the API never leaks hidden diagnosis, (f) deterministic clinical state and results independent of the LLM's creative output.

The newer design is evidence of what needed fixing, but its presence does not establish perfect security or clinical correctness.

### C. A stricter reading of “the latest genuinely MIT version”

The **last pre-Oyon root-MIT source revision** we identified is still **May 8, 2026**, commit [`d5f14e6`](https://github.com/mohsaqr/rohySimulator/tree/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd). However, **there is no basis to call the *whole checkout* exclusively MIT**:

- [`server/data/lab_pediatric_ranges.json`](https://github.com/mohsaqr/rohySimulator/blob/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd/server/data/lab_pediatric_ranges.json) is explicitly marked `CC BY-NC-SA` (the file appeared in commit [`3b505b0`, May 6](https://github.com/mohsaqr/rohySimulator/commit/3b505b089ab36a2927676a0b4dcf8aedf41da989)). Remove from the permissive-only derivative and substitute separately cleared data.
- `public/sounds/normal-heart.mp3` and `normal-lung.mp3` have no verified source license. The heart sound was already committed by January 11, 2026; simply selecting an earlier date does not resolve its provenance. Replace with independently licensed audio.
- The talking-avatar manifest names Microsoft's RocketBox and `met4citizen/TalkingHead`; the *upstream repositories' root MIT licenses* were verified, but individual derived GLBs and their textures should still be mapped to original assets and notices before copying or selling a derivative.
- Historical [`mohsaqr/dynajs` at `96c1d82`](https://github.com/mohsaqr/dynajs/tree/96c1d82c4ba4b5a3b8ffc7b59ac8c093c0596660) declared MIT in `package.json` and README, though no standalone LICENSE was found. Current `dynajs` is Carm-licensed. Prefer replacing the analytics dependency or obtaining clear historical reuse documentation rather than silently installing latest.
- The May snapshot's images, seeds, data, audio, dependencies and voice/model licenses have *not* been completely forensically audited.

Accordingly, the precise defensible conclusion is **“last identifiable pre-restriction MIT-covered first-party core, subject to exclusions”**, not “last definitely all-MIT repository archive.” There may be later, individually MIT-covered contributions, but no entire post-May 9 repository tree is confirmed to be uniformly MIT.

### D. Additional maintainability findings from selected historical source

- `src/components/monitor/PatientMonitor.jsx` is approximately 122 KB at the May revision and combines ECG waveform generation, monitor visualization, alarms, settings, patient record state and treatment interactions. Extract pure waveforms and physiology into separately tested modules rather than lifting the whole UI component.
- `src/components/settings/ConfigPanel.jsx` is approximately 290 KB. The first-party authoring UI is not a small independently embeddable package.
- The May `server/routes/cases-routes.js`, `agents-routes.js`, `orders-routes.js` and `proxy-routes.js` share a very large import/helper prelude. They may have been mechanically split from a larger router; transplanting route files wholesale brings substantial coupling. Validate individual routes; do not infer modularity from directory organization.
- The monitor waveform generator uses a fixed 250 Hz stepping model and hand-parameterized morphology; `server/data/treatment_effects.json` represents many interventions with scripted effects on HR, BP, RR and SpO2. This can be useful for an educational game but should not be described as clinically validated physiological simulation.
- The May README advertises 695 passing tests, the repository has Vitest and Playwright configuration, and the Git tree has 69 files under `tests/`. **No historical tests, build or deployment were executed in this audit.** There may be dependency installation issues, especially the required sibling `../dynajs` checkout.

### E. Which parts to reuse and which to rebuild

| Component | Recommended action | Reason |
|---|---|---|
| Case authoring UI / case model | **Extract and refactor** | Mature feature scope, but the data schema must split public findings from hidden answer keys |
| Investigation catalogues and order UI | **Reuse with data audit** | Already useful and extensive, but exclude the noncommercial pediatric dataset and verify data provenance |
| Patient, nurse, consultant and debrief UI | **Reuse interaction patterns** | Valuable workflow; prompts/agent knowledge scopes must be built server-side instead |
| Treatment list and time progression | **Reuse scaffolding, validate science** | Existing trigger model, but scalar HR/BP effects are a simplified teaching model |
| Old ECG monitor | **Consider as an initial UI demo** | Lacks the current 12-lead clinical interpretation workstation; use dedicated MIT ECG/signal code for serious study reading |
| PACS / pathology / echo | **Bring in independently licensed modules** | Dedicated workstations arrived later in restricted/vendor code or do not exist at needed fidelity |
| User authentication, session trust, hidden case prompts | **Rebuild the trust boundary** | Historical case payload/prompt are controlled or accessible in the learner browser |
| Old `dynajs`, audio, avatar GLBs | **Pin/replace/audit** | Historical or mixed provenance; do not assume the current versions carry MIT rights |
| Current 3.1.5 private/restricted plugin internals | **Do not copy** | Subsequent Carm license and third-party vendor licensing |

**Decision for the game:** The old May 8 version is still a compelling source for clinical-workflow modules, especially if speed of building a prototype matters. It is **not** my first choice as the intact main application: a hidden-diagnosis game needs a clean authority boundary, and the old UI/backend architecture would require meaningful surgery. Prefer a compositional architecture with a separate trusted case engine (developed anew or from a clearly MIT-licensed alternative), selectively adapted legacy Rohy workflows, and independently licensed ECG/imaging/echo modules. A direct fork only makes sense if you accept the cost of restructuring the back end, cleaning data/media licensing, and replacing the prompt and disclosure trust model.

### F. Minimal extraction checklist

1. Preserve the May revision's MIT copyright and include the license for every reused first-party file.
2. Maintain a `THIRD_PARTY_NOTICES.md` mapping every copied dataset/asset to its originating license; quarantine unknown provenance rather than assuming it is MIT.
3. Exclude CALIPER pediatric ranges and unresolved heart/lung audio. Independently inspect and clear the talking-head GLBs or replace them.
4. Do not resolve `file:../dynajs` from current `main`; choose a verified historical revision or build a replacement analytics adapter.
5. Split authoring-only, hidden-case and assessment fields from fields a learner may receive; use server-generated redacted views.
6. Build LLM prompts on the server from server-controlled session snapshots; accept only bounded, authorized client actions, not arbitrary system prompts.
7. Add adversarial tests: student `GET /cases` cannot reveal expected diagnosis, test values or secrets; forged client prompts cannot change patient identity or case diagnosis; specialist responses reveal only their authorized findings.
8. Verify the full old test/build pipeline, then benchmark one end-to-end case with dynamic vitals, labs, imaging, medication actions and final debrief.

**Scope and certainty:** Source-inspection and Git metadata audit, not a legal opinion or an executed test-suite result. Original license grants remain subject to third-party rights; historical MIT material is not automatically relicensed by a later proprietary root license, but that principle does not cure unlicensed bundled assets.

# PART IX — FINAL RECONCILIATION, ADOPTION DECISIONS AND RESEARCH LEDGER

### 1. New priority: a believable electronic health record

The earlier recommendations emphasized physical signals, but **SimEHR** supplies a realistic clinical workflow beyond a collection of popup laboratory values: orders and medications, notes, results, imaging studies, trend charts and audit events. It is a different kind of fidelity, and for a diagnostic reasoning game it may matter more than 3D hospital rendering. Its repository documents an application API (`loadCase`, `getState`, `getAuditLog`, `resetState`); inspect those endpoints for a lightweight embedding adapter.

### 2. New priority: high-quality patient conversation without knowledge leakage

**PatientsWithPersonality**, **PatientHub**, **Simu_Patient** and the earlier Virtual Standardized Patient suggest separating: (i) immutable case truth, (ii) information the patient knows, (iii) how it is communicated, and (iv) objective exam or test results. A patient may be misleading from anxiety, confusion or poor recall, but the model should never freely overwrite factual study results.

### 3. Signal generation is not diagnostic truth

**NeuroKit2** is useful for generating smooth, parameterized ECG/PPG/RSP/EDA/EMG and building unit tests. **WFDB** and **ECG-Format-Converter** bring real recordings into standardized acquisition formats. A synthetic 12-lead baseline does not automatically model STEMI localization, hyperkalemia or complex conduction abnormalities accurately. For disease-specific interpretation, pair a tested generator or recorded asset with case-authored abnormalities and provenance.

### 4. Echocardiography is still the highest medical-validation challenge

**EchoSim** changes the licensing picture materially, but a synthetic ultrasound-rendered anatomical scene is not the same as independently validated pathology. **PyMUST**, **USTB** and other RF/beamforming projects are physics research pipelines, not a drop-in echo training game. A pragmatic design is EchoSim for guided procedural exploration, with legally reusable real cine loops for high-fidelity interpretation.

### 5. New research field: diagnosis as a sequential information-acquisition problem

**DiagGym** and **open-residencyrl** offer ideas for evaluation beyond a single final diagnosis: did the user request the right investigation, at the right time, and update the differential reasonably? But a generative test-result model should be sandboxed against authored ground truth, with a refusal or explicit unavailable state for impossible/unlisted studies.

## Verification status and technical debt

- **Verified directly via GitHub file retrieval:** prominent licenses including GTAgentClinic (Apache), EchoSim (MIT), WiseCases (MIT), PatientsWithPersonality (MIT), PatientHub (MIT), SimEHR (Apache), Chelsea-19/Simu_Patient (MIT), open-residencyrl (Apache), NeuroKit2 (MIT), WFDB (MIT), USTB (MIT), CeBiDa (MIT), Meridian (MIT), Slim (Apache), SonoForge (GPL), DWV (GPL), PyMUST (conflicting LGPL notices), MegaWiz vitals (AGPL), and the Pulse reliability atlas (Apache).
- **Verified from official repository README/metadata rather than an inspected LICENSE text:** BioGears Apache-2.0, Circinus MIT claim, Wegas MIT claim, CPRSimulator CC0 claim, and Papaya's BSD-style distribution terms. Inspect at a pinned commit before redistribution.
- **Still requiring clarification:** AetioMed, PatientSim, the small echo/tutorial prototypes, CT-VR-App, separate Infirmary EHR, and several older studies; source visibility does not confer a reuse license. The DiagGym license notice is unusually terse for software and needs direct author clarification; PyMUST's version conflict must also be resolved.
- **Not undertaken:** running full games, checking UI functionality across hardware, reproducing scientific validation, testing 96 builds or auditing all transitive licenses. README test counts remain developer claims, not verified pass results.

## Practical next decisions

1. **Base-game A/B test:** GTAgentClinic vs Open Sim Lab using one identical authored patient/case and an explicit integration scorecard.
2. **Echo proof of concept:** load EchoSim inside an isolated view; ensure the diagnosis and pathologies can be set from authoritative case data and not exposed through controls when hidden.
3. **EHR proof of concept:** compare SimEHR's ordering/results UI against GTAgentClinic's built-in EHR, including exam timestamps and result release times.
4. **Waveform proof of concept:** Patient Monitor Engine + 12-Lead Generator + one real, appropriately licensed WFDB recording. Check synchronization and ECG/perfusion separation.
5. **Consolidated licensing ledger:** repository, pinned commit, license, third-party assets, models, clinical case text, attribution, planned modifications and distribution mode.

### Key GitHub source documents (new work)

- [GTAgentClinic README](https://github.com/eth-medical-ai-lab/GTAgentClinic#readme) and [LICENSE](https://github.com/eth-medical-ai-lab/GTAgentClinic/blob/main/LICENSE)
- [EchoSim README](https://github.com/peterdoubell/Echosim#readme) and [LICENSE](https://github.com/peterdoubell/Echosim/blob/main/LICENSE)
- [BioGears core README](https://github.com/BioGearsEngine/core#readme)
- [SimEHR README](https://github.com/HealthRex/SimEHR#readme)
- [NeuroKit2 repository and signal simulators](https://github.com/neuropsychology/NeuroKit)
- [DiagGym README and license notice](https://github.com/MAGIC-AI4Med/DiagGym)
- [PyMUST license text](https://github.com/creatis-ULTIM/PyMUST/blob/main/LICENSE) and [package metadata](https://github.com/creatis-ULTIM/PyMUST/blob/main/setup.py)
- [GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)


## IX-0. Detailed audit's adoption ordering and reproducibility boundary

This later ranking is a snapshot from the newly uploaded *multihost_detailed* report. It is preserved as a supplemental decision record; the older canonical correction ledger continues to govern contested license findings.

**Build soon (permissive code / strong fit):** GTAgentClinic or Open Sim Lab (A/B test rather than merger), SimuPatient (state-guard patterns), SimEHR (chart/order UI), Patient Monitor Engine (live monitor), 12-Lead Generator (formal ECG), OHIF/Cornerstone3D (radiology), EchoSim (echo; external validation remains essential), PatientsWithPersonality (history disclosure), Epicurrents (EEG), plus pydicom/WFDB for asset preparation.

**Test as a second wave:** Open Vent Sim, NeuroKit2, WiseCases authoring, Meridian, Slim, SonoForge (copyleft considerations), PatientHub and AetioMed (licensing permission required), PyMUST/USTB/PyUS for offline ultrasound assets, and Kitware Pulse/BioGears for full physiology.

**Inspiration only / blocked:** Rohy, Vitalis, The Heart by Ultrasound and several unlicensed patient demos; CC BY-NC/noncommercial model systems, restrictive AnaSim versions and unverified asset packages should not be copied into a freely redistributable game without permission.

**Explicitly not independent simulator duplicates:** USTB Bitbucket mirror, OHIF archived core, individual Epicurrents subpackages, OTC-Flow Hugging Face weights, PULSE-7B model vs Kitware Pulse engine, and Orthanc's Mercurial/GitHub read-only mirror.

### Detailed source audit: remaining reproducibility limits

The source base remains the original uploaded research reports and the multi-host inventory, expanded with directly fetched GitHub READMEs and selected LICENSE files, official Pulse documentation, targeted GitLab/Hugging Face resource pages, and links carried in each source profile. A filename, a license badge and a GitHub screenshot are not sufficient evidence that a simulation feature was run or that its generated measurements are medically correct. The source-level flags differentiate directly reviewed text from prior-research descriptions, and integration suggestions are explicitly labeled as design inferences.

**Not completed in this revision:** running 112 builds, code-level audits of every dependency, clinical validation studies, full dependency/license trees, patient-media redistribution checks, formal threat modeling, and benchmarked performance. Those are costly tasks and should be prioritized for the shortlist instead of distributed across every repository.

**Canonical inventory counts remain unchanged:** 96 GitHub primary entries + 7 GitLab + 6 Hugging Face code/model + 2 Hugging Face datasets + 1 Mercurial = **112 primary tracked entries**. Newly identified mirrors and companion projects have not been added as new primary simulator counts. This report intentionally preserves the preceding audit verbatim for source provenance and historical comparison.

## IX-A. Conflict-resolution / source precedence rules

**Never silently delete earlier evidence.** When a new finding changes an earlier verdict, record the old statement, evidence checked and the updated decision. The following ledger is binding for this version:

| Topic | Earlier unsupported or incomplete claim | Current canonical position |
|---|---|---|
| Medkit | No license found | README explicitly no redistribution; inspiration only |
| paultman patientSimulator (#67) | No root LICENSE verified | MIT root LICENSE now identified; still a small interview POC |
| biosimkit (#5) | No license | README MIT assertion; exact scope not fully verified |
| ION_Simula (#6) | No license | Paper states GPL; actual version and repository grant pending |
| Open Sim Lab | 256 lab tests; conventional total score | 256 *scenarios*; check debrief process and scoring independently |
| GTAgentClinic | Current v0.4, WebGPU mandatory, case content NC | Earlier inspected README 0.3.0, WebGL2 fallback, CC BY 4.0 cases; counts snapshot-dependent |
| Infirmary Integrated | Unity engine | C#/.NET solution; no demonstrated Unity foundation |
| DWV | MIT | GPL-3.0 original license |
| Slicer | ordinary BSD3 | Custom BSD-style license terms |
| Rohy | historical site-wide MIT implies all versions reusable | Current Carm 1.4; historical May 8 first-party MIT core with explicit excluded assets/deps |
| Rohy older safety | Good direct fork | Learner-visible hidden-case config and client prompt control must be redesigned |
| Echo | No permissively licensed procedural candidate | MIT EchoSim exists, but clinical validation pending |
| Pulse / BioGears | independent unrelated engines | Kitware Pulse forks BioGears 6.1.1 and is separately maintained on GitLab |
| Orthanc | an imaging viewer; GPL infects any client | DICOM server; actual obligations depend on specific distribution/derivative architecture |
| PyMUST | single known LGPL grant | LGPL 2.1 vs 3.0 declarations conflict; clarify |
| Clinical datasets | freely downloadable means open assets | Rights per source article, dataset revision, media and intended distribution |
| OLab4 | current successor ready to fork | GPL archival code; README says explicitly do not use |
| MultiCaRe | CC0 everywhere | License metadata conflict across GitHub/HF/Zenodo; item-level permissions required |
| PMC-Patients | Open access implies reusable for any game | Assembled dataset CC BY-NC-SA; not permissive |

## IX-B. Shortlist by actual purpose, not repository popularity

### First end-to-end prototype comparison

1. [Open Sim Lab](https://github.com/clay-good/opensimlab) — case progression, gameplay loop, clinician action/time state; license MIT code (scenario assets separate).
2. [GTAgentClinic](https://github.com/eth-medical-ai-lab/GTAgentClinic) — richer hospital/3D/NPC/EHR interaction; Apache-2.0 code and CC BY 4.0 cases, medical validation required.
3. [Historical Rohy clinical workflows](https://github.com/mohsaqr/rohySimulator/tree/d5f14e6e9b19e9db268125a0a2f3aa63cdb5adbd) — selected UI/authoring/order concepts only after security and material-rights audit.
4. [Virtual Standardized Patient](https://github.com/igembitsky/virtual-standardized-patient) — dialogue-to-private-case separation and offline clinician interaction.

### Best-first modality experiments

1. [Patient Monitor Engine](https://github.com/samhv-dev/patient-monitor-engine) — live vitals and waveform dashboard.
2. [12-Lead Generator](https://github.com/arpitre/12-Lead-Generator) — 12-lead ECG interpretation and teaching controls.
3. [EchoSim](https://github.com/peterdoubell/Echosim) — interactive acquisition and measurements; cross-validate with source clips.
4. [OHIF Viewer](https://github.com/OHIF/Viewers) + [Cornerstone3D](https://github.com/cornerstonejs/cornerstone3D) — radiology interpretation.
5. [SimEHR](https://github.com/HealthRex/SimEHR) — orders, reports and notes.
6. [Epicurrents](https://github.com/epicurrents/builder) — EEG/EMG after the cardiac/imaging spine is stable.

### Later add-ons / R&D

- [Kitware Pulse](https://gitlab.kitware.com/physiology/engine) and [BioGears](https://github.com/BioGearsEngine/core): systemic physiology when scientifically justified.
- [Open Vent Sim](https://github.com/fedebarra/open-vent-sim): ventilation and intensive care.
- [Synthea](https://github.com/synthetichealth/synthea): realistic synthetic chart fixtures.
- [MedCaseReasoning](https://huggingface.co/datasets/zou-lab/MedCaseReasoning), [MultiCaRe](https://github.com/mauro-nievoff/MultiCaRe_Dataset) and [PMC OA](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/): research/content discovery, pending rights and clinical review.
- [PyMUST](https://github.com/creatis-ULTIM/PyMUST), [PyUS](https://gitlab.com/pyus/pyus), [OTC-Flow](https://github.com/yunhaoli24/OTC-Flow): advanced ultrasound/synthetic signals research only.

## IX-C. Source and provenance manifest conventions

Maintain a structured record for each adopted resource with at least:

| Property | Why it is required |
|---|---|
| `canonical_project` | Distinguishes upstream from fork/companion/mirror |
| `source_url` / `commit_sha` | Reproducible source of source code |
| `path` / `asset_id` | Exact copied file, recording, case or model |
| `resource_type` | Code vs dataset vs clinical figure vs weights vs notes |
| `license_spdx` and complete grant | Legal reproduction/derivative rights and notices |
| `attribution` / `NOTICE` | Required credit and legal distribution terms |
| `source_article_id` / `study_id` | Clinical provenance and correction of aggregate-dataset confusion |
| `privacy/deid` | No unauthorized or identifying clinical data |
| `clinical_validation_state` | Independent medical review status and limitations |
| `build_test_state` | Actual locally executed test/install evidence |
| `api_adapter_owner` | Who maintains interface and upgrades |
| `integration_priority` and `decision` | Next steps and auditable go/no-go |

## IX-D. Interpretation of 'free/open source'

MIT / Apache-2.0 / BSD: usually reasonable permission to modify with notices, subject to third-party material. GPL/LGPL/AGPL: real open-source licenses, not a blanket ban; their obligations depend on the specific work, linking, modification, packaging and network deployment. CC BY for media/cases: permits reuse under attribution/terms, but is not a substitute for software licensing. CC BY-NC and CC BY-NC-SA: exclude from unrestricted commercial re-distribution. Missing license: no implied reuse grant. 'Research only' and Carm restrictions: respect the text of the grant; obtain written approval for copying/integration when required. Dataset badges, model cards and repository READMEs are evidence, but not proof that all underlying content has consistent rights.

## IX-E. What the evidence still cannot answer

- Which foundation (Open Sim Lab or GTAgentClinic) is demonstrably easier to modify and connect to the full instrument stack under identical controlled conditions?
- Can EchoSim reliably accept externally authored pathology without exposing hidden answers or producing misleading findings?
- Can the Patient Monitor Engine and 12-Lead Generator use a common rhythm/cardiovascular state and maintain appropriate units/timing?
- Does SimEHR load arbitrary synthetic patients/cases, and can it remain subordinate to another game's authoritative clinical history?
- Which actual pathology-rich, legally reusable DICOM/ultrasound/EEG datasets are cleared and medically reviewed for redistribution into game builds?
- What exact known limitations and numerical validation ranges are covered by Pulse and BioGears for our intended scenarios?
- Are all third-party licenses, checksums and security advisories acceptable at a known tested commit?

These are **not claims of missing software**. They are high-value test questions. Answer them with one repeatable clinical case and real code/runtime spikes before selecting a primary fork.

## IX-F. Complete source-document and cross-chat basis

**User-provided primary documents in this consolidation:**

1. `medical_diagnostics_repository_audit_multihost_verified_2026-11-19.md` — 96 GitHub discovery inventory; GitLab/HF/Mercurial verification; source ledger; corrections and R&D priorities.
2. `medical_simulation_github_repositories_expanded_v4.md` — detailed original 53 license and reuse reviews; historical May 8 Rohy source and later-restricted code, explicit source-level UI/security findings.
3. `medical_diagnostics_repository_audit_multihost_detailed_2026-11-19.md` — full later source-by-source review of the same 112 primary entries, 96 GitHub detailed supplements, 16 cross-host dossiers, cross-platform links and experiment matrix; source classifications R/P/H/I are retained in the merged dossiers.

**Additional recovered prior-source material:** earlier document *Open-Source Medical Simulation Games and Modules*; earlier two-report reconciliation and relevant medical game research conversations. These supplied supplemental TUM/ECG Studio/older patient tools and earlier case-data research. Not every conversation was available as a raw export, so any otherwise unsupported claim is qualified as 'earlier report', 'earlier conversation', or 'unverified'. The unrelated Godot/FastAPI/PostgreSQL architecture has been consciously excluded.

**Direct upstream reference URLs for re-checking:** all 96 original canonical links in Part II; seven GitLab URLs, six Hugging Face code/model URLs, two HF datasets, Orthanc upstream and pairing ledger in Part V; added source repos and clinical datasets in Part VI. This file is designed to remain useful without any ephemeral chat citation IDs.

---

# CONCLUSION

The research has reached a useful **technology-discovery stopping point**. There are multiple legally plausible high-value components, and more repositories are not the principal bottleneck. The real engineering challenge is **integrating them under one authoritative case truth, a reproducible timeline and a safe hidden-information boundary**, while preserving clinical accuracy and rights for every educational asset. Begin with one high-quality clinical case and side-by-side spikes, then import only modules whose *state control, medical realism and license* have been demonstrated.

**Document status:** consolidated source/research ledger; not a release-approved SBOM, medical validation, software license legal opinion, executed benchmark or production architecture specification. All candidate systems require further direct inspection before source transplantation.

