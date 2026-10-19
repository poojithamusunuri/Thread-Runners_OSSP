"""Best-effort lifecycle observations derived from successive /proc snapshots.

These records are inferences from snapshots, not kernel-confirmed lifecycle events.
"""
from __future__ import annotations
from collections import deque
from datetime import datetime, timezone
from typing import Any

MAX_EVENTS = 500

class TimelineTracker:
    def __init__(self, max_events: int = MAX_EVENTS) -> None:
        self.events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self.previous: dict[str, Any] | None = None
        self.sequence = 0

    @staticmethod
    def _identity(record: dict[str, Any]) -> str:
        identity = record.get("identity") or {}
        return f"{identity.get('boot_id', '')}:{record.get('pid')}:{identity.get('start_time_ticks', '')}"

    def _add(self, timestamp: float, kind: str, title: str, detail: str,
             pid: int | None, source: str, confidence: str = "inferred") -> None:
        self.sequence += 1
        self.events.append({
            "id": self.sequence,
            "timestamp": timestamp,
            "kind": kind,
            "title": title,
            "detail": detail,
            "pid": pid,
            "source": source,
            "confidence": confidence,
        })

    def observe(self, snapshot: dict[str, Any]) -> None:
        now = float(snapshot.get("captured_at_unix") or datetime.now(timezone.utc).timestamp())
        current = snapshot.get("processes") or {}
        if self.previous is None or self.previous.get("boot_id") != snapshot.get("boot_id"):
            reason = "Initial baseline snapshot established." if self.previous is None else "System boot identity changed; a new baseline was established."
            self._add(now, "baseline", "Snapshot baseline established", reason, None, "snapshot", "observed")
            self.previous = snapshot
            return

        previous = self.previous.get("processes") or {}
        old_by_identity = {self._identity(r): r for r in previous.values()}
        new_by_identity = {self._identity(r): r for r in current.values()}

        # A PID may be reused. Compare stable identities, not PID alone.
        old_pids = {int(r["pid"]): r for r in previous.values()}
        new_pids = {int(r["pid"]): r for r in current.values()}
        for pid in sorted(set(old_pids) & set(new_pids)):
            if self._identity(old_pids[pid]) != self._identity(new_pids[pid]):
                self._add(now, "pid-reuse", "PID identity changed", f"PID {pid} now refers to a different process identity. This is inferred from start-time identity.", pid, "snapshot comparison")

        for key, record in new_by_identity.items():
            if key not in old_by_identity:
                pid = int(record["pid"])
                if pid in old_pids and self._identity(old_pids[pid]) != key:
                    title = "New process identity observed"
                    detail = f"PID {pid} appears with a different start-time identity than the previous snapshot."
                else:
                    title = "Process first seen"
                    detail = f"{record.get('name') or 'Process'} (PID {pid}) was present in this snapshot but not the previous one. Its exact start time was not observed."
                self._add(now, "appeared", title, detail, pid, "snapshot comparison")

        for key, record in old_by_identity.items():
            if key not in new_by_identity:
                pid = int(record["pid"])
                title = "Process no longer visible"
                detail = f"{record.get('name') or 'Process'} (PID {pid}) was absent from the latest snapshot. It may have exited or become unreadable; an exit event was not directly observed."
                self._add(now, "disappeared", title, detail, pid, "snapshot comparison")

        for key in set(old_by_identity) & set(new_by_identity):
            before, after = old_by_identity[key], new_by_identity[key]
            pid = int(after["pid"])
            if before.get("state") != after.get("state"):
                self._add(now, "state", "Process state changed", f"PID {pid}: {before.get('state', '?')} → {after.get('state', '?')}. Observed by comparing snapshots.", pid, "snapshot comparison")
            if before.get("ppid") != after.get("ppid"):
                self._add(now, "parent", "Parent relationship changed", f"PID {pid}: parent PID {before.get('ppid')} → {after.get('ppid')}. Observed by comparing snapshots.", pid, "snapshot comparison")

        self.previous = snapshot

    def as_dict(self) -> dict[str, Any]:
        events = list(self.events)
        return {
            "events": list(reversed(events)),
            "event_count": len(events),
            "max_events": self.events.maxlen,
            "collection_mode": "snapshot comparison",
            "limitations": [
                "Timeline entries are inferred from successive /proc snapshots, except for baseline records.",
                "A process may start and exit between snapshots without appearing in the timeline.",
                "A process absent from a snapshot may have exited or may have become unreadable.",
                "The timeline is held in memory and is cleared when the server restarts.",
            ],
        }
