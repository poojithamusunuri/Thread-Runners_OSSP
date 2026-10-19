# ProcScope v1.0.2 — Validation Report

## Scope

This report records checks reported for the corrected v1.0.2 release candidate in the available Linux development environment. It is not a claim that the recipient's Ubuntu machine or the final presentation browser has been fully acceptance-tested.

## Checks reported in the development environment

- **Automated tests:** 23 passed using `./run_tests.sh`.
- **Python compilation:** passed for the server, collector, timeline, Lab manager, event collector, and verification script.
- **Frontend syntax:** `node --check static/app.js` passed when Node.js was available; Node is not required at runtime.
- **Strict GCC compilation:** passed with `gcc -std=c11 -O2 -Wall -Wextra -Werror -pthread`.
- **Lab integration:** all five allow-listed experiments were reported as started and stopped through the Lab manager; follow-up process checks found no known Lab process left running.
- **HTTP smoke tests:** the main page, static assets, health, snapshot, timeline, Lab, Reports, and event status endpoints returned successful responses. An unexpected Host header was rejected.
- **Tree verification:** the recorded run reported zero parent mismatches against `ps` for the compared relationships and zero mismatches for sampled `pstree` ancestry relationships. The sample size and skipped/raced observations are reported by the verifier for each run.

## How to reproduce

From the project directory on Linux:

```sh
./run_tests.sh
python3 verify_tree.py
```

For the interactive acceptance test:

```sh
./run.sh
```

Then open <http://127.0.0.1:8765> locally and test Explorer search/tree/follow-family, Timeline labels, all five Lab experiments and cleanup, and Reports exports/comparison.

## Interpretation and limitations

- Development-environment results do not establish that the recipient's Ubuntu installation has been tested.
- A full real-browser click-through and target-machine acceptance run remain required.
- Snapshot collection is best-effort and not atomic. Processes may start or exit between ProcScope, `ps`, and `pstree` observations.
- Optional kernel event subscription depends on kernel support and permissions; event mode may be unavailable and may lose events. Snapshot mode remains the baseline.
- The verifier is a practical cross-check, not a formal proof of correctness.
- Lab experiments run with the current user's permissions and are educational demonstrations, not a security sandbox.

## Feature status

The v1.0.2 release candidate includes Explorer, Timeline, Lab, Reports, plain HTML/CSS/JavaScript, a Python standard-library server, organization views for process groups/sessions/threads/cgroups where available, family highlighting, five C Lab experiments, optional event mode, redacted JSON/CSV reports, in-session snapshot comparison, and `ps`/sampled-`pstree` verification.
