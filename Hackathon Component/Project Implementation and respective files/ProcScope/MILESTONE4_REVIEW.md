# ProcScope v1.0.2 — Integrated Release-Candidate Review

## Integrated features

- Live `/proc` snapshot collector and interactive parent-child Explorer.
- Hierarchy search, expansion/collapse, selected-process details, and follow-family highlighting for ancestors and descendants.
- Explorer organization views for process groups, sessions, thread IDs, and cgroup paths where available.
- Snapshot-derived Timeline plus optional best-effort Linux process connector event mode.
- Five allow-listed C Process Lab experiments: zombie, orphan re-parenting, pipeline, threads, and fork/exec.
- Reports with redacted JSON/CSV export, in-session snapshot comparison, and collection diagnostics.
- Localhost binding and Host-header/Origin checks.
- Verification helper compares parent relationships against `ps` and sampled immediate-parent ancestry against `pstree` where available.

## Release-candidate fixes

- Corrected the pipeline experiment's write handling so it checks for write errors and handles partial/interrupted writes.
- Verified strict GCC compilation with `-std=c11 -O2 -Wall -Wextra -Werror -pthread` in the development environment.
- Added process group ID, session ID, terminal ID, per-process thread IDs, and cgroup paths to collector records.
- Added organization views and follow-family highlighting to the Explorer.
- Strengthened `pstree` verification from PID coverage alone to sampled ancestry-chain parent comparisons.
- Fixed the Lab duration display to use the API's `duration` field.
- Applied readable dark-theme colors to the Reports comparison panel and statistic labels.
- Clarified Timeline wording to distinguish inferred snapshot observations from observed kernel events.
- Updated documentation to match the delivered feature set and limitations.

## Validation reported for the development environment

- `./run_tests.sh`: 23 tests passed.
- Python compilation and JavaScript syntax checks passed.
- Strict GCC compilation passed.
- The five Lab experiments were started and stopped through the Lab manager in the reported development run.
- HTTP smoke tests covered the main page, static assets, health, snapshot, timeline, Lab, Reports, and invalid Host handling.
- A tree verification run reported 0 parent mismatches in the compared `ps` relationships and 0 mismatches in the sampled `pstree` ancestry relationships for that run.

## Known limitations and remaining acceptance work

- These results are from the development environment; they do not establish acceptance on the recipient's Ubuntu machine.
- Real-browser end-to-end review and a full click-through of Explorer, Timeline, Lab, and Reports remain required on the presentation machine.
- Snapshot collection is best-effort and not atomic; process churn can cause transient verification differences.
- Optional CN_PROC event collection depends on kernel support and permissions and may lose events. It is not a complete audit log.
- Process-group, session, thread, and cgroup views organize collected metadata; they are not replacements for full Linux administration tools.
- Lab experiments run with the current user's privileges and are educational demonstrations, not a security sandbox.
