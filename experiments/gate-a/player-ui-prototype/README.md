# Fixture-A player UI prototype

This is a clearly labeled, local browser exercise for the first three development steps and a bounded step-4 recovery slice in **Player UI/UX Plan v0.4**. It uses the repository's Gate A `Fixture-A` through the public `GateAPort` operations implemented by `SQLiteAuthority`.

It is a software and interaction prototype. It contains no real patient data, clinical assets, live provider connection, or medically grounded claims. The deterministic worker and Luna doubles stay local. No dependency installation is required.

## Run locally

From the repository root in PowerShell:

```powershell
python experiments/gate-a/player-ui-prototype/server.py --port 0
```

Open the loopback URL printed in the terminal. Stop the server with `Ctrl+C`.

The server binds only to loopback. SQLite state and attempt metadata live outside the repository in `%TEMP%\medical-diagnostics-game-player-ui-prototype` by default. Pass `--data-dir <path>` to use a separate local data folder, or `--port <port>` if 8765 is occupied. Restarting the server preserves the authority database and attempts in the selected data folder.

## Walkthrough path

1. Select **Publish fixture** on Home, then start Fixture-A.
2. In Encounter, try the blocked dialogue state. Open **Help** and switch the local Luna double to **Available** if you want to see a committed reply.
3. In Investigations, review A, T, and C, place the orders, then advance clinical time by 9 seconds.
4. Open **Synthetic authority controls** at the bottom and authorize the fixture's manual release for T. A and T are now released; C remains ordered.
5. Open A and T from the worklist. Cite both into reasoning, then return to Diagnosis and rank the opaque fixture labels.
6. Review the exact submission and per-item closeout preview. Submit; A and T stay in history and C closes in its ordered state.
7. Use Help to simulate a debrief outage before submission if you want to exercise the independent feedback path. The frozen submission remains visible, and feedback or Skip still works.
8. In the synthetic authority drawer after submission, attempt a 1-second wait. It should be rejected with no clock change.
9. To exercise order recovery, open Help and choose **Lose response before commit** or **Lose response after commit**. Place an order. The unresolved banner offers one status check and a retry using the original command identity. A reload performs one read-only status check. The local simulation never hides whether it is running.

You can add B before placing the order to compare two compatible point studies. Fixture-A schedules A and B at the same clinical time, so the viewer labels that as a same-time comparison rather than a prior trend. The fixture cannot demonstrate a distinct earlier measurement; see [WALKTHROUGH.md](WALKTHROUGH.md).

## Scope and limits

- Authority-backed: case publication, independent playthroughs, orders, clinical time, result release and access, artifact opening, final submission, frozen debrief, and independent feedback.
- Browser-only: screen selection, unsent text, ranking draft, and walkthrough settings. Drafts are kept per attempt in browser local storage. Stale-tab edits show a conflict with explicit restore or save choices.
- Test-build controls: select simulated dialogue availability, release T as the fixture authority, simulate debrief rendering failure, simulate one lost order response before or after commit, and probe a post-submission wait. They are not player controls in a live product.
- Recovery slice: unresolved order requests keep their original ID, revision, and payload in local storage. The UI checks the current projection once, then offers a same-intent retry. This does not implement durable worker recovery, command reconciliation for every mutation, or trusted-store outage handling.
- Not implemented: generation through Luna, live sign-in, real tests, clinical measurements, treatment, or a release-ready application.

## Verification notes

The source of truth for clinical time, command effects, released evidence, submissions, and debrief is the Gate A authority. The browser does not invent case facts or infer hidden findings. The UI makes one fixture-authorized T release call because Fixture-A configures that result for manual release.

See [step-4/5 readiness notes](STEP4-5-READINESS.md) for the recorded GUI recovery/accessibility checks and the live-slice prerequisites that remain open.
