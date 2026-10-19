"""ProcScope Milestone 1: Linux /proc snapshot collector.

This module is deliberately read-only. It does not send signals or launch processes.
It uses only the Python standard library and is intended for Linux systems with /proc.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable
import os
import time


@dataclass(frozen=True, order=True)
class ProcessIdentity:
    """Identity stable enough to distinguish PID reuse within a boot."""
    boot_id: str
    pid: int
    start_time_ticks: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessRecord:
    identity: ProcessIdentity
    pid: int
    ppid: int
    name: str
    state: str
    state_description: str
    user_ticks: int | None = None
    system_ticks: int | None = None
    thread_count: int | None = None
    rss_bytes: int | None = None
    executable: str | None = None
    command_line: list[str] | None = None
    collection_warnings: list[str] = field(default_factory=list)
    process_group_id: int | None = None
    session_id: int | None = None
    terminal_id: int | None = None
    thread_ids: list[int] = field(default_factory=list)
    cgroups: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["identity"] = self.identity.as_dict()
        return result


@dataclass
class ProcessSnapshot:
    boot_id: str
    captured_at_unix: float
    duration_seconds: float
    processes: dict[int, ProcessRecord]
    children_by_pid: dict[int, list[int]]
    roots: list[int]
    warnings: list[str]
    skipped_processes: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "boot_id": self.boot_id,
            "captured_at_unix": self.captured_at_unix,
            "duration_seconds": self.duration_seconds,
            "processes": {str(pid): record.as_dict() for pid, record in self.processes.items()},
            "children_by_pid": {str(pid): children for pid, children in self.children_by_pid.items()},
            "roots": self.roots,
            "warnings": self.warnings,
            "skipped_processes": self.skipped_processes,
        }


STATE_DESCRIPTIONS = {
    "R": "Running or runnable",
    "S": "Sleeping (interruptible)",
    "D": "Waiting in uninterruptible sleep",
    "Z": "Zombie (finished, awaiting parent cleanup)",
    "T": "Stopped or traced",
    "t": "Tracing stop",
    "X": "Dead",
    "x": "Dead",
    "K": "Wakekill",
    "W": "Waking",
    "P": "Parked",
    "I": "Idle kernel thread",
}


class ProcCollectorError(RuntimeError):
    """Raised when a valid baseline snapshot cannot be collected."""


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def _parse_stat(stat_text: str) -> dict[str, Any]:
    """Parse /proc/PID/stat safely, including comm values containing spaces or ')'.

    Linux format: pid (comm) state ... . The final ')' before state is used because
    the comm field may itself contain parentheses.
    """
    left = stat_text.find("(")
    right = stat_text.rfind(")")
    if left <= 0 or right <= left or right + 2 > len(stat_text):
        raise ValueError("Malformed /proc stat record")
    try:
        pid = int(stat_text[:left].strip())
    except ValueError as exc:
        raise ValueError("Invalid PID in /proc stat record") from exc
    comm = stat_text[left + 1:right]
    rest = stat_text[right + 1:].strip().split()
    # rest[0] is field 3 (state), so field N is rest[N - 3].
    if len(rest) <= 21:
        raise ValueError("Incomplete /proc stat record")
    try:
        state = rest[0]
        ppid = int(rest[1])               # field 4
        process_group_id = int(rest[2])   # field 5
        session_id = int(rest[3])         # field 6
        terminal_id = int(rest[4])        # field 7 (device number; 0 means no controlling terminal)
        user_ticks = int(rest[11])        # field 14
        system_ticks = int(rest[12])      # field 15
        thread_count = int(rest[17])      # field 20
        start_time_ticks = int(rest[19])  # field 22
        rss_pages = int(rest[21])         # field 24
    except (ValueError, IndexError) as exc:
        raise ValueError("Invalid numeric field in /proc stat record") from exc
    return {
        "pid": pid,
        "name": comm,
        "state": state,
        "ppid": ppid,
        "process_group_id": process_group_id,
        "session_id": session_id,
        "terminal_id": terminal_id,
        "user_ticks": user_ticks,
        "system_ticks": system_ticks,
        "thread_count": thread_count,
        "start_time_ticks": start_time_ticks,
        "rss_pages": rss_pages,
    }


def _parse_status_rss(status_text: str) -> int | None:
    for line in status_text.splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    # Linux reports VmRSS in kB (KiB in practice).
                    return int(parts[1]) * 1024
                except ValueError:
                    return None
    return None


class ProcCollector:
    """Collect a best-effort, race-aware snapshot from a Linux procfs mount.

    proc_root is injectable so parsing and race conditions can be tested with fixtures.
    """
    def __init__(self, proc_root: str | os.PathLike[str] = "/proc") -> None:
        self.proc_root = Path(proc_root)

    def _boot_id(self) -> str:
        path = self.proc_root / "sys/kernel/random/boot_id"
        try:
            boot_id = _read_text(path)
        except OSError as exc:
            raise ProcCollectorError(f"Cannot read Linux boot ID at {path}: {exc}") from exc
        if not boot_id:
            raise ProcCollectorError("Linux boot ID is empty; cannot establish process identity")
        return boot_id

    def _read_process(self, pid_dir: Path, boot_id: str) -> ProcessRecord:
        stat = _parse_stat(_read_text(pid_dir / "stat"))
        pid = stat["pid"]
        if pid_dir.name != str(pid):
            raise ValueError("PID directory and stat PID do not match")
        warnings: list[str] = []
        rss_bytes: int | None = None
        try:
            rss_bytes = _parse_status_rss(_read_text(pid_dir / "status"))
        except OSError:
            warnings.append("Memory details unavailable during collection")

        executable: str | None = None
        try:
            executable = os.readlink(pid_dir / "exe")
        except OSError:
            warnings.append("Executable path unavailable or access restricted")

        command_line: list[str] | None = None
        try:
            raw_cmdline = (pid_dir / "cmdline").read_bytes()
            command_line = [part.decode("utf-8", errors="replace") for part in raw_cmdline.split(b"\0") if part]
        except OSError:
            warnings.append("Command line unavailable or access restricted")

        thread_ids: list[int] = []
        try:
            task_dir = pid_dir / "task"
            thread_ids = sorted(int(item.name) for item in task_dir.iterdir() if item.name.isdigit())
        except OSError:
            warnings.append("Thread IDs unavailable or access restricted")

        cgroups: list[str] = []
        try:
            for line in _read_text(pid_dir / "cgroup").splitlines():
                parts = line.split(":", 2)
                if len(parts) == 3:
                    cgroups.append(f"hierarchy {parts[0]} ({parts[1] or 'unified'}): {parts[2]}")
        except OSError:
            warnings.append("Cgroup information unavailable or access restricted")

        identity = ProcessIdentity(boot_id, pid, stat["start_time_ticks"])
        state = stat["state"]
        return ProcessRecord(
            identity=identity,
            pid=pid,
            ppid=stat["ppid"],
            name=stat["name"],
            state=state,
            state_description=STATE_DESCRIPTIONS.get(state, "Unknown process state"),
            user_ticks=stat["user_ticks"],
            system_ticks=stat["system_ticks"],
            thread_count=stat["thread_count"],
            rss_bytes=rss_bytes,
            executable=executable,
            command_line=command_line,
            collection_warnings=warnings,
            process_group_id=stat["process_group_id"],
            session_id=stat["session_id"],
            terminal_id=stat["terminal_id"],
            thread_ids=thread_ids,
            cgroups=cgroups,
        )

    def collect(self) -> ProcessSnapshot:
        start = time.monotonic()
        captured_at = time.time()
        boot_id = self._boot_id()
        processes: dict[int, ProcessRecord] = {}
        warnings: list[str] = []
        skipped = 0
        try:
            entries: Iterable[Path] = list(self.proc_root.iterdir())
        except OSError as exc:
            raise ProcCollectorError(f"Cannot enumerate procfs at {self.proc_root}: {exc}") from exc

        for entry in entries:
            if not entry.name.isdigit() or not entry.is_dir():
                continue
            try:
                record = self._read_process(entry, boot_id)
                processes[record.pid] = record
            except (OSError, ValueError, ProcCollectorError):
                # Processes can exit or change while /proc is being read. Skip that
                # record and report the count instead of failing the entire snapshot.
                skipped += 1

        children: dict[int, list[int]] = {pid: [] for pid in processes}
        roots: list[int] = []
        for pid, record in processes.items():
            if record.ppid in processes and record.ppid != pid:
                children[record.ppid].append(pid)
            else:
                # Includes kernel/init roots and parents that disappeared during scan.
                roots.append(pid)
        for child_list in children.values():
            child_list.sort()
        roots.sort()
        if skipped:
            warnings.append(f"{skipped} process entr{'y' if skipped == 1 else 'ies'} could not be read; processes may have changed during collection or access may be restricted.")
        if not processes:
            warnings.append("No process records were collected. Verify that procfs is mounted and readable.")

        return ProcessSnapshot(
            boot_id=boot_id,
            captured_at_unix=captured_at,
            duration_seconds=time.monotonic() - start,
            processes=processes,
            children_by_pid=children,
            roots=roots,
            warnings=warnings,
            skipped_processes=skipped,
        )


if __name__ == "__main__":
    import json
    try:
        snapshot = ProcCollector().collect()
    except ProcCollectorError as exc:
        raise SystemExit(f"ProcScope collector error: {exc}")
    print(json.dumps(snapshot.as_dict(), indent=2))
