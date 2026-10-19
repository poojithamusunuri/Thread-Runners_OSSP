import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from timeline_tracker import TimelineTracker


def record(pid, name, ppid=1, state="S", start=100, boot="boot-a"):
    return {"pid": pid, "name": name, "ppid": ppid, "state": state,
            "identity": {"boot_id": boot, "pid": pid, "start_time_ticks": start}}


def snapshot(processes, captured=1000.0, boot="boot-a"):
    return {"boot_id": boot, "captured_at_unix": captured,
            "processes": {str(p["pid"]): p for p in processes}}


class TimelineTrackerTests(unittest.TestCase):
    def test_initial_snapshot_only_creates_baseline(self):
        tracker = TimelineTracker()
        tracker.observe(snapshot([record(1, "init")]))
        events = tracker.as_dict()["events"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "baseline")
        self.assertEqual(events[0]["confidence"], "observed")

    def test_new_process_is_labeled_as_snapshot_inference(self):
        tracker = TimelineTracker()
        tracker.observe(snapshot([record(1, "init")], 1000))
        tracker.observe(snapshot([record(1, "init"), record(2, "worker")], 1002))
        event = next(e for e in tracker.as_dict()["events"] if e["kind"] == "appeared")
        self.assertEqual(event["pid"], 2)
        self.assertEqual(event["source"], "snapshot comparison")
        self.assertEqual(event["confidence"], "inferred")

    def test_disappearance_does_not_claim_confirmed_exit(self):
        tracker = TimelineTracker()
        tracker.observe(snapshot([record(1, "init"), record(2, "worker")], 1000))
        tracker.observe(snapshot([record(1, "init")], 1002))
        event = next(e for e in tracker.as_dict()["events"] if e["kind"] == "disappeared")
        self.assertIn("may have exited or become unreadable", event["detail"])

    def test_state_and_parent_changes_are_recorded(self):
        tracker = TimelineTracker()
        tracker.observe(snapshot([record(1, "init"), record(2, "worker", ppid=1, state="S")], 1000))
        tracker.observe(snapshot([record(1, "init"), record(2, "worker", ppid=3, state="R")], 1002))
        kinds = {e["kind"] for e in tracker.as_dict()["events"]}
        self.assertIn("state", kinds)
        self.assertIn("parent", kinds)

    def test_pid_reuse_detected_using_start_time(self):
        tracker = TimelineTracker()
        tracker.observe(snapshot([record(1, "init"), record(2, "old", start=100)], 1000))
        tracker.observe(snapshot([record(1, "init"), record(2, "new", start=900)], 1002))
        kinds = [e["kind"] for e in tracker.as_dict()["events"]]
        self.assertIn("pid-reuse", kinds)

    def test_boot_change_establishes_new_baseline(self):
        tracker = TimelineTracker()
        tracker.observe(snapshot([record(1, "init")], 1000, "boot-a"))
        tracker.observe(snapshot([record(1, "init", boot="boot-b")], 2000, "boot-b"))
        baselines = [e for e in tracker.as_dict()["events"] if e["kind"] == "baseline"]
        self.assertEqual(len(baselines), 2)

    def test_event_history_is_bounded(self):
        tracker = TimelineTracker(max_events=3)
        tracker.observe(snapshot([record(1, "init")], 1000))
        for i in range(5):
            tracker._add(1001 + i, "state", "test", "test", i, "test")
        self.assertEqual(tracker.as_dict()["event_count"], 3)


if __name__ == "__main__":
    unittest.main()
