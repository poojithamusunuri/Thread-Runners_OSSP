# ProcScope v1.0.2 — Linux Process Tree Visualizer

ProcScope is a local, educational Linux process explorer. Its home screen is the live parent-child process tree. It also provides an activity timeline, a guided C Process Lab, and snapshot reports.

## Requirements

- Linux with `/proc` mounted (Ubuntu is the target platform)
- Python 3.10 or newer
- `cc`, `gcc`, or `clang` for Process Lab experiments only
- `pstree` from the `psmisc` package for the additional structural cross-check
- No Python packages, Node.js, frontend build step, internet connection, or root access for baseline operation

## Start ProcScope

1. Extract the project archive on the Linux machine.
2. Open a terminal in the extracted `ProcScope` directory.
3. Run:

   ```sh
   ./run.sh
   ```

4. Open <http://127.0.0.1:8765> in a browser on the same machine.
5. Stop the server with `Ctrl+C`. ProcScope attempts to clean up active Lab experiments during shutdown.

The server binds to `127.0.0.1` only. Do not expose it to a network unless you have reviewed the security implications.

## Main sections

- **Explorer:** live process tree, search, process selection, available process details, organization views for process groups, sessions, threads, and cgroups, plus **Follow family** highlighting in hierarchy mode.
- **Timeline:** baseline and lifecycle observations. Snapshot-derived changes are labelled inferred; optional process-connector events are labelled observed when received.
- **Lab:** five allow-listed C experiments: zombie, orphan re-parenting, pipeline, threads, and fork/exec.
- **Reports:** redacted JSON/CSV exports, in-session snapshot comparison, and collection diagnostics. Event mode is optional; if unavailable, snapshots continue normally.

## Tests and verification

Run the automated tests:

```sh
./run_tests.sh
```

Run the independent tree cross-check:

```sh
python3 verify_tree.py
```

The verifier compares parent PIDs with `ps -e -o pid=,ppid=` and samples immediate-parent relationships from `pstree` ancestry output when `pstree` is installed. Commands run sequentially, not against one atomic system snapshot, so process churn can create transient differences. Review the counts and warnings rather than interpreting one run as mathematical proof.

## Data and privacy

Data is read locally from `/proc`. Timeline history and snapshot-comparison state are held in memory and reset when the server restarts. Reports redact command-line arguments and executable paths by default; inspect exports before sharing them. Process names, IDs, parent IDs, resource values, and timing remain in reports.

## Collection modes and limitations

- **Snapshot baseline:** periodically reads `/proc`. It works independently of optional event collection, but it is best-effort and not atomic. Very short-lived processes can be missed.
- **Optional event mode:** attempts Linux `NETLINK_CONNECTOR` / `CN_PROC` subscription when explicitly started from Reports. Support and permissions depend on the kernel and system configuration. Events may be unavailable or lost; this is not a complete audit log.
- A process missing from a snapshot may have exited or been inaccessible. Missing records are not fabricated.
- Process identity uses boot ID + PID + process start time to reduce confusion from PID reuse.
- Process-group ID, session ID, terminal device number, thread IDs, and cgroup paths are collected where available. Some details may be unavailable because of access restrictions or system configuration.
- CPU tick values are raw counters, not normalized CPU percentages. Memory details can be unavailable.
- The Lab is educational, not a security sandbox. Experiments run with the current user's privileges and should not be used on production-critical systems.
- ProcScope does not claim to replace `pstree` or `htop`; it combines an interactive hierarchy, transparent lifecycle observations, verification helpers, and guided experiments.

## Project layout

- `server.py` — local HTTP server and API
- `proc_collector.py` — Linux `/proc` snapshot collector
- `timeline_tracker.py` — snapshot-based lifecycle tracker
- `event_collector.py` — optional best-effort CN_PROC listener
- `lab_manager.py`, `lab/lab_experiments.c` — controlled Process Lab
- `static/` — plain HTML, CSS, and JavaScript frontend
- `verify_tree.py` — comparison against `ps` and sampled `pstree` ancestry
- `tests/` — automated tests
- `docs/ARCHITECTURE.md` — system architecture
- `docs/MILESTONES.md` — milestone summary
- `SPECIFICATION_v1.0.md` — frozen original product specification
- `RELEASE_NOTES_v1.0.2.md` — release-candidate fixes
- `VALIDATION_REPORT.md` — validation performed and remaining acceptance checks
