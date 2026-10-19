# ProcScope v1.0 — Frozen Project Specification

**Status:** Original specification frozen for implementation; retained as a historical design record  
**Current release candidate:** v1.0.2  
**Target:** Ubuntu Linux  
**Project title:** Linux Process Tree Visualizer  
**Product name:** ProcScope

## Problem statement

Linux systems run many processes, and processes can create child processes. Understanding their parent-child relationships and how they change over time can require several command-line tools and operating-system knowledge. ProcScope displays the live process hierarchy in an interactive interface, provides process details, records lifecycle observations, and offers guided experiments that explain core operating-system concepts.

## Objective

Provide a continuously updated visual representation of running Linux processes and their parent-child relationships, while preserving technical accuracy and making the information accessible to beginners.

## Frozen product decisions

- The Process Explorer and live process tree are the home screen.
- Four primary sections: Explorer, Timeline, Lab, Reports.
- Frontend: plain HTML, CSS, and JavaScript; no frontend build step.
- Backend: Python, using the standard library wherever practical.
- Baseline collector: read-only Linux `/proc` snapshots.
- Optional collector: Linux process lifecycle event collection, only where supported and permitted.
- Process identity: boot ID + PID + process start time in clock ticks.
- Process Lab: guided C experiments with explanations and cleanup.
- Verification script: compare ProcScope's observed relationships against `ps` and `pstree` where available.
- Server binds to localhost by default; core inspection is read-only.
- Build and review one milestone at a time.

## Must ship

- Live process tree with expandable/collapsible branches.
- Search, process selection, and process detail view.
- PID, PPID, process state, and available resource measurements.
- Robust `/proc` parsing and safe identity handling for PID reuse.
- Snapshot collection that continues when individual processes disappear or are inaccessible.
- Basic activity timeline with a distinction between directly observed events and snapshot-inferred changes.
- Verification script, automated tests, setup instructions, user guide, and architecture documentation.

## Should ship

- Optional process-event collector with clear support, permission, and event-loss diagnostics.
- Guided C experiments: zombie process, orphan re-parenting, pipeline/process groups, multithreading, and fork/exec.
- Process groups, sessions, threads, and cgroup views where available.
- Snapshot comparison and JSON export with sensitive command-line redaction.

## Optional after core validation

- Timeline replay, richer historical analysis, additional filters, and extra visualizations.

## Milestones

1. **Process collector:** `/proc` parsing, stable process identity, parent-child relationship building, and tests.
2. **Explorer:** plain-JavaScript live tree UI and comparison against system tools.
3. **Timeline:** live updates, event/inference labels, and diagnostics.
4. **Process Lab:** controlled C experiments, explanations, and cleanup.
5. **Validation and delivery:** Ubuntu integration testing, documentation, report template, and final ZIP.

## Accuracy and safety requirements

- Snapshot collection is best-effort; processes may change while a snapshot is being collected.
- A process whose parent is absent from a snapshot must not cause a fabricated parent record.
- Event mode must never claim perfect or lossless capture.
- Unavailable data must not be presented as zero.
- The main tool must work without the Process Lab or optional event mode.
- Never execute arbitrary shell commands supplied by the browser.
- Lab actions must be restricted to processes started and tracked by ProcScope, with cleanup behavior tested.
- Command lines may contain secrets; exports must support redaction.

## Differentiation from `pstree` and `htop`

ProcScope does not claim to replace or universally outperform existing tools. Its distinct contribution is the combination of an interactive live hierarchy, transparent observed-versus-inferred lifecycle information, careful PID-reuse handling, repeatable verification against system tools, and a guided Process Lab.

## Implementation status in v1.0.2

The current release candidate includes the four primary sections, baseline `/proc` snapshots, optional best-effort CN_PROC event mode, organization views for process groups/sessions/threads/cgroups where available, family highlighting, five C Lab experiments, redacted JSON/CSV reports, snapshot comparison, and a `ps`/sampled-`pstree` verification helper.

The specification remains named v1.0 because it records the original frozen design. Release-specific changes and actual validation results are recorded in `RELEASE_NOTES_v1.0.2.md` and `VALIDATION_REPORT.md`. The recipient-machine and real-browser acceptance checks remain outstanding as described in the validation report.
