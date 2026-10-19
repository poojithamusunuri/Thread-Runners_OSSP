# ProcScope Architecture

## Overview

ProcScope is a local Linux process-exploration application. A Python standard-library HTTP server provides the API and serves a plain HTML/CSS/JavaScript frontend. The Explorer's primary data source is Linux `/proc`; optional kernel process-event collection supplements, but never replaces, snapshot collection.

## Data flow

1. The browser requests a process snapshot from the local Python server.
2. `ProcCollector` enumerates numeric directories in `/proc`, parses `/proc/PID/stat`, and reads optional status, executable, command-line, thread, session, process-group, and cgroup details where available.
3. Each process is identified using `(boot_id, pid, start_time_ticks)` to reduce confusion caused by PID reuse within a boot.
4. The collector builds parent-child relationships and visible roots. If a parent is absent from the snapshot, it does not fabricate a parent record.
5. The Explorer renders the hierarchy, supports search and selection, and can highlight the selected process's visible ancestors and descendants.
6. `TimelineTracker` compares successive snapshots and stores bounded in-memory observations labelled as inferred.
7. `EventCollector` is opt-in. When Linux CN_PROC is supported and permission is available, it can add best-effort kernel-reported fork/exec/exit observations. It does not replace snapshots and may be unavailable or lose events.
8. Reports provide redacted JSON/CSV exports, in-session snapshot comparison, and collection diagnostics.

## Main modules

- `server.py` — local HTTP server, routes, request validation, and static file serving.
- `proc_collector.py` — `/proc` snapshot collection, parsing, identity, and relationship building.
- `timeline_tracker.py` — snapshot-difference lifecycle observations.
- `event_collector.py` — optional best-effort Linux CN_PROC listener.
- `lab_manager.py` and `lab/lab_experiments.c` — allow-listed educational C experiments and tracked cleanup.
- `static/index.html`, `static/style.css`, `static/app.js` — no-build frontend.
- `verify_tree.py` — independent best-effort comparison with `ps` and sampled `pstree` ancestry.
- `tests/` — automated tests for collector, timeline, event collector, and Lab manager.

## Safety boundaries

- The server binds to `127.0.0.1` by default and validates Host/Origin information for relevant requests.
- Lab requests select from a fixed experiment allow-list; arbitrary browser-provided shell commands are not executed.
- Lab subprocesses run as the current user in tracked process groups with bounded experiment duration/active-run limits.
- Server shutdown requests cleanup of tracked Lab process groups and stops optional event collection.
- Process inspection is read-only; there is no general-purpose process-kill interface.
- Report redaction is enabled by default for command-line arguments and executable paths.

## Verification approach

`verify_tree.py` collects a ProcScope snapshot and independently queries `ps -e -o pid=,ppid=`. It compares PPIDs for PIDs shared by the two observations. If `pstree` is available, it samples up to 50 shared PIDs and compares the selected PID's immediate parent in an ancestry-chain output. These checks run sequentially, so they are best-effort comparisons, not one atomic snapshot or a formal proof of correctness.

## Known limitations

- `/proc` snapshots are not atomic; processes can change while the collector reads them.
- CPU tick values are raw counters, not normalized CPU percentages.
- Access to some fields may be restricted.
- Optional CN_PROC support depends on kernel configuration and permissions; events may be lost and the event buffer is bounded.
- Timeline history and snapshot-comparison state are held in memory and reset when the server restarts; comparison history may also reset on page reload.
- Organization views use available metadata and do not replace full process, service, container, or cgroup management tools.
- Browser-based validation and acceptance testing must be completed on the target Ubuntu machine before claiming full presentation-machine acceptance.
