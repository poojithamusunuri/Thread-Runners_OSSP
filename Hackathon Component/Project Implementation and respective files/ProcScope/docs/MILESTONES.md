# ProcScope Development Milestones

This document summarizes the implementation milestones for the v1.0.2 release candidate. The original feature priorities are preserved in `../SPECIFICATION_v1.0.md`; this file records the delivered implementation and remaining acceptance work.

## Milestone 1 — Process collector

**Implemented.** Reads Linux `/proc`, parses process stat/status information, identifies processes using boot ID + PID + start time, builds parent-child relationships, and handles per-process read failures without failing the entire snapshot.

## Milestone 2 — Process Explorer

**Implemented.** Provides a live tree, search, expansion/collapse, process selection/details, organization views for process groups/sessions/threads/cgroups where available, and follow-family highlighting.

## Milestone 3 — Activity Timeline

**Implemented.** Tracks snapshot-derived lifecycle observations and labels them as inferred. Optional event mode can add kernel-reported observations when available; collection availability and limitations must remain visible.

## Milestone 4 — Process Lab

**Implemented.** Provides five controlled C experiments: zombie, orphan re-parenting, pipeline, threads, and fork/exec. Lab actions are allow-listed and cleanup is tracked. The Lab is educational and is not a security sandbox.

## Milestone 5 — Reports and release validation

**Release-candidate implementation completed; target acceptance still required.** Includes redacted JSON/CSV export, in-session snapshot comparison, collector diagnostics, automated tests, and a verification helper that compares ProcScope relationships with `ps` and sampled `pstree` ancestry.

## Remaining acceptance checks

- Run `./run_tests.sh` on the target Ubuntu machine.
- Run `python3 verify_tree.py` and review both tool comparisons and skipped/raced observations.
- Open the app in a real browser and click through Explorer, Timeline, each Lab experiment, and Reports exports.
- Verify cleanup of Lab processes and stop the server cleanly.
- Update any presentation evidence with the results from that actual run.

See `../VALIDATION_REPORT.md` for the environment-specific results currently recorded and their limitations.
