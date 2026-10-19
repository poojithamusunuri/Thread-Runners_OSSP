#!/usr/bin/env python3
"""Compare a ProcScope snapshot with independent ps and pstree observations.

This is a best-effort cross-check, not a proof of a perfectly simultaneous snapshot.
Processes can start or exit between each command.
"""
from __future__ import annotations
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from proc_collector import ProcCollector, ProcCollectorError  # noqa: E402


def run_command(args: list[str], timeout: float = 10) -> str | None:
    try:
        result = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout)
        return result.stdout
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"[WARN] Could not run {' '.join(args)}: {exc}")
        return None


def main() -> int:
    if not Path("/proc").is_dir():
        print("ERROR: /proc is unavailable. Run this tool on Linux.", file=sys.stderr)
        return 2
    try:
        snapshot = ProcCollector().collect()
    except ProcCollectorError as exc:
        print(f"ERROR: ProcScope collector failed: {exc}", file=sys.stderr)
        return 2

    proc_map = snapshot.processes
    ps_text = run_command(["ps", "-e", "-o", "pid=,ppid="])
    if ps_text is None:
        print("ERROR: ps is required for relationship verification.", file=sys.stderr)
        return 2
    ps_map: dict[int, int] = {}
    for line in ps_text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            try:
                ps_map[int(parts[0])] = int(parts[1])
            except ValueError:
                continue

    shared = set(proc_map) & set(ps_map)
    compared = 0
    mismatches: list[tuple[int, int, int]] = []
    for pid in sorted(shared):
        collector_ppid = proc_map[pid].ppid
        ps_ppid = ps_map[pid]
        # Ignore self-parent oddities and only compare the parent relation.
        compared += 1
        if collector_ppid != ps_ppid:
            mismatches.append((pid, collector_ppid, ps_ppid))

    print("ProcScope process-tree verification")
    print("===================================")
    print(f"ProcScope snapshot records: {len(proc_map)}")
    print(f"ps records:                 {len(ps_map)}")
    print(f"PIDs present in both:       {len(shared)}")
    print(f"Parent relationships compared: {compared}")
    print(f"Parent mismatches:          {len(mismatches)}")
    if mismatches:
        print("\nMismatches (PID: ProcScope PPID vs ps PPID):")
        for pid, ours, theirs in mismatches[:20]:
            print(f"  {pid}: {ours} vs {theirs}")
        if len(mismatches) > 20:
            print(f"  … and {len(mismatches) - 20} more")
        print("NOTE: process changes between commands can cause transient mismatches.")

    pstree_available = shutil.which("pstree") is not None
    pstree_mismatches: list[tuple[int, int, int | None]] = []
    pstree_compared = 0
    pstree_skipped = 0
    if not pstree_available:
        print("\n[INFO] pstree is not installed; install the psmisc package for structural verification.")
    else:
        # Query ancestry chains for a deterministic sample. `pstree -s -p -T PID`
        # prints the selected process and its ancestors (and may include descendants);
        # the selected PID's preceding token provides a sampled parent cross-check.
        candidates = sorted(shared)
        sample_size = min(50, len(candidates))
        if sample_size and len(candidates) > sample_size:
            indices = sorted({round(i * (len(candidates) - 1) / (sample_size - 1)) for i in range(sample_size)}) if sample_size > 1 else [0]
            candidates = [candidates[i] for i in indices]
        for pid in candidates:
            tree_text = run_command(["pstree", "-s", "-p", "-T", str(pid)], timeout=3)
            if tree_text is None:
                pstree_skipped += 1
                continue
            ancestry = [int(value) for value in re.findall(r"\((\d+)\)", tree_text)]
            # pstree may include the selected process's descendants after its
            # ancestry chain. Locate the selected PID and compare its preceding
            # PID rather than assuming the selected process is the final token.
            try:
                target_index = ancestry.index(pid)
            except ValueError:
                pstree_skipped += 1
                continue
            # A selected root has no preceding PID; do not infer a mismatch.
            if target_index == 0:
                pstree_skipped += 1
                continue
            pstree_parent = ancestry[target_index - 1]
            collector_parent = proc_map[pid].ppid
            pstree_compared += 1
            if collector_parent != pstree_parent:
                pstree_mismatches.append((pid, collector_parent, pstree_parent))
        print(f"pstree ancestry relationships compared: {pstree_compared}")
        print(f"pstree parent mismatches:               {len(pstree_mismatches)}")
        print(f"pstree observations skipped/raced:       {pstree_skipped}")
        if pstree_mismatches:
            print("\nMismatches (PID: ProcScope PPID vs pstree parent):")
            for pid, ours, theirs in pstree_mismatches[:20]:
                print(f"  {pid}: {ours} vs {theirs}")
            if len(pstree_mismatches) > 20:
                print(f"  … and {len(pstree_mismatches) - 20} more")
        print("pstree check compares sampled immediate-parent relationships via ancestry chains; process churn can cause transient mismatches.")

    print(f"\nSnapshot skipped records: {snapshot.skipped_processes}")
    print("Interpretation: compare is best-effort because these tools cannot take one atomic snapshot.")
    # A mismatch is evidence to inspect, but can be caused by process churn.
    # Exit non-zero only for a large persistent-looking mismatch rate.
    mismatch_rate = len(mismatches) / compared if compared else 0.0
    pstree_rate = len(pstree_mismatches) / pstree_compared if pstree_compared else 0.0
    if compared == 0 or mismatch_rate > 0.10 or (pstree_compared and pstree_rate > 0.10):
        print("RESULT: REVIEW REQUIRED — inspect mismatches and repeat on a quiet system.")
        return 1
    print("RESULT: BASIC CROSS-CHECK PASSED — no large parent mismatch rate detected against available tools.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
