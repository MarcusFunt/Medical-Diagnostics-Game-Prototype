# Medical Diagnostics Game — First Playable Engineering Slice

**Status:** engineering-only local preview, 22 November 2026. This is not a clinically credible game case, a selected production architecture, an ECG simulator, or medical software.

This branch adds a browser workspace driven by the **already tested Gate A SQLite Case Authority**, not a second clinical-state implementation. It explicitly uses synthetic Fixture-A values and its fictional `DX-A` / `DX-B` scoring rubric. The case is automatically registered in the local library. Every "new play" starts a separate, persistent session. The game remains diagnosis-only with no treatment or 3D environment.

## Run on Marcus_Computer

From `D:\projects\Medical-Diagnostics-Game-Playable-Slice\experiments\playable-slice`:

```powershell
node server.mjs
```

Then open **http://127.0.0.1:8787** on the *same computer*. Requires Python 3.11+ and Node 24+. No npm or pip dependencies are required. The server binds to `127.0.0.1`, serves its own static UI, and does not expose a LAN service.

The local SQLite store defaults to `%LOCALAPPDATA%\MedicalDiagnosticsGame\playable-slice.sqlite3`. The OAuth host/client registration file is `playable-slice-auth-client.json` in the same user-local directory. **No OAuth token is saved to disk or delivered to browser JavaScript.** The browser receives only a per-server-run local request nonce; refresh/access/ID tokens remain in Node memory and are discarded when the process exits (and refreshed/revoked when possible while it runs). Full secure persistence across restarts is not implemented.

Click **Sign in with ChatGPT** in the app to authorize. The required model is **`gpt-6-luna`**; no API key or alternative model is used. The server verifies OpenID signature/claims, consent scopes, listable model access, and exchanges authorization/rotating refresh tokens. Denied, unavailable, malformed, or non-grounded dialogue outputs cause an explicit blocked command, not a canned fallback. New-turn dialogue calls use `store:false`, `stream:true`, the HTTP Responses endpoint, and complete-event checking. The local web app requires a new interactive consent verification; **this implementation has not been proven to complete a live Luna turn yet**. Fixture-A explanation requests are not sent to Luna because the authority's internal reference assessment contains its answer key.

## The demonstrated encounter

1. Create a new playthrough from the auto-published **Fixture-A** library case, or reopen a prior session.
2. Optionally sign in and ask the patient about prior episodes. The trusted Case Authority supplies only its allowlisted subjective-history fact to the inference layer. This synthetic test recognizes only one exactly grounded answer or a precisely constrained uncertainty answer. It deliberately does not support free-ranging clinical history generation yet.
3. Order **A** (numeric observation) and/or **T** (invented three-sample signal plus a deterministic display-only 12-channel preview). Neither is a medical finding or ECG. Advance the authoritative clock. Acquisition happens around 5s, computation at 6s and eligibility at 8s; A automatically releases at 8s. T receives an internal-only demo authorization once the game clock reaches 9s. The browser cannot submit a privileged release command.
4. Inspect T through a game-owned SVG viewer with lead labels, a text alternative, and display grid spacing of 25 mm/s and 10 mm per fixture-mV. The trace shapes and lead relationships are arbitrary software output, not patient data or a medically valid ECG. The fixture has no player-safe clinical interpretation; the authority returns an unavailable status instead of exposing the internal answer-bearing assessment.
5. Submit a leading fictional label and differential. The authority creates a six-dimension debrief, closes pending work, freezes the clinical time, and prompts for a case-quality review. Review submission and skipping are persisted separately from grading.

All actions, observations, reference assessments, scoring, and access control are delegated to `../gate-a/authority.py`; the UI gets only role-filtered projections and released artifacts.

## Design boundaries

- **Trusted backend:** `backend.py` is a per-command JSON-lines adapter to Gate A. It commits through `SQLiteAuthority` and persists a local session index. A deterministic worker test double produces the synthetic trace from the declared fixture state; this does not generalize to medical evidence.
- **Model bridge:** when Gate A asks for Luna, Python emits an internal `model_request` over its child-process pipe. The app bridge passes only the bounded subjective-history dialogue request; it refuses the synthetic Fixture-A explanation request because its reference assessment includes the hidden answer. The player projection removes answer-bearing result fields and replaces internal assessments with a safe unavailable status. Structured dialogue output must match the fixture allowlist or Gate A refuses the command; no model output becomes objective case truth. Network latency does not advance simulated time.
- **Browser boundary:** static application without external libraries, CSP, strict local host/Origin and request-nonce checks, text-escaped rendering, no directly loaded hidden-case JSON, and no client-accessible privileged release route.
- **Persistence:** the entire test authority is stored in local SQLite, separately from synthetic patient/session index. Reopening does not regenerate results. Local single-user trust only; no multi-account authorization or cross-user access separation is claimed.
- **Time & provisional policies:** T's release at 9s is an application-specific demo service rule atop Gate A's trusted manual-release capability; it is not a clinical laboratory policy.

## Test commands

```powershell
# From the project worktree root:
python -m unittest discover -s experiments/gate-a -v
python -m unittest discover -s experiments/playable-slice -p test_backend.py -v
cd experiments/playable-slice
node --test siwc-smoke.test.mjs server.test.mjs
```

The backend tests cover creation/catalog, repeatable state, withholding until release, inspectable trace, debrief/review/reopen, fake diagnosis rejection, unavailable Luna, and local session separation. The copied and unmodified SIWC smoke module supplies independent PKCE/JWT/SSE unit tests; browser-side auth is not yet integration-tested. A separate HTTP smoke confirms GET pages/CSS/JS, POST create/order/advance/release and rejection of a cross-origin POST.

**Not tested or completed:** a live authenticated Luna conversation through this new app; persistence/renewal of an actual refresh-token across restarts; robustness under multiple OS accounts; full browser accessibility/automation; a clinically reviewed ECG asset; activation of the AF-ECG candidate (pending review); case generation with variation or Synthea; Pulse adapter; clinical accuracy; rights-cleared media; production packaging; native UI; security audit; or portability to other computers.

The new source tree is deliberately isolated on `feat/first-playable-vertical-slice-20261122`, created from the review branch at commit `7e0938d`. Original research files and original worktree working-tree changes were not modified. Do not merge this into `main` without deciding whether Gate A should become the production authority or remain a comparison fixture.
