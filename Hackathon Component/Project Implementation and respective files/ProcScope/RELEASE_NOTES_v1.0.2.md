# ProcScope v1.0.2 — Release Notes

## UI corrections

- Fixed Process Lab duration labels to use the `duration` field returned by the Lab API.
- Applied explicit dark-theme colors to the Reports comparison panel and statistic labels.
- Clarified the Timeline introduction: snapshot-derived entries are inferred; kernel-event entries are labelled observed when event mode receives those events.

## Included release-candidate functionality

- Interactive live process tree, search, process details, organization views, and follow-family highlighting.
- Snapshot-based Timeline and optional best-effort CN_PROC event collection.
- Five guided C Process Lab experiments.
- Redacted JSON/CSV exports, in-session snapshot comparison, and collector diagnostics.
- Automated tests and `ps` / sampled `pstree` verification helper.

## Validation status

The recorded development-environment run reports 23 automated tests passed, successful Python and JavaScript syntax checks, strict GCC compilation, Lab integration checks, HTTP smoke tests, and best-effort tree cross-checks.

Real-browser click-through and acceptance testing on the recipient's Ubuntu machine remain required. Optional event mode depends on kernel support and permissions and may be unavailable or lose events. See `VALIDATION_REPORT.md` for details.
