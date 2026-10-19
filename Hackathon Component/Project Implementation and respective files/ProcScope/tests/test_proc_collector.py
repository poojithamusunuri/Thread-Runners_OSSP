import json
import os
from pathlib import Path
import tempfile
import unittest

from proc_collector import ProcCollector, ProcCollectorError, ProcessIdentity, _parse_stat


def make_stat(pid, comm, state, ppid, start_time, user_ticks=10, system_ticks=5, threads=1, rss_pages=4, pgid=0, sid=0, tty=0):
    # /proc stat fields after comm start at field 3. Fill through field 24.
    fields = ["0"] * 22
    fields[0] = state                 # field 3
    fields[1] = str(ppid)             # field 4
    fields[2] = str(pgid)             # field 5
    fields[3] = str(sid)              # field 6
    fields[4] = str(tty)              # field 7
    fields[11] = str(user_ticks)      # field 14
    fields[12] = str(system_ticks)    # field 15
    fields[17] = str(threads)         # field 20
    fields[19] = str(start_time)      # field 22
    fields[21] = str(rss_pages)       # field 24
    return f"{pid} ({comm}) " + " ".join(fields)


class ParseStatTests(unittest.TestCase):
    def test_parses_comm_with_spaces_and_parentheses(self):
        parsed = _parse_stat(make_stat(123, "worker (blue) process", "S", 1, 9876))
        self.assertEqual(parsed["pid"], 123)
        self.assertEqual(parsed["name"], "worker (blue) process")
        self.assertEqual(parsed["ppid"], 1)
        self.assertEqual(parsed["start_time_ticks"], 9876)
        self.assertEqual(parsed["state"], "S")
        self.assertEqual(parsed["process_group_id"], 0)
        self.assertEqual(parsed["session_id"], 0)

    def test_rejects_incomplete_record(self):
        with self.assertRaises(ValueError):
            _parse_stat("123 (broken) S 1 2")


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "sys/kernel/random").mkdir(parents=True)
        (self.root / "sys/kernel/random/boot_id").write_text("boot-test-001\n")
        self.add_process(1, "init", "S", 0, 100, rss_kib=32)
        self.add_process(20, "parent", "S", 1, 200, rss_kib=64)
        self.add_process(21, "child", "R", 20, 210, rss_kib=96)

    def tearDown(self):
        self.temp.cleanup()

    def add_process(self, pid, name, state, ppid, start, rss_kib=10):
        directory = self.root / str(pid)
        directory.mkdir(exist_ok=True)
        (directory / "stat").write_text(make_stat(pid, name, state, ppid, start))
        (directory / "status").write_text(f"Name:\t{name}\nVmRSS:\t{rss_kib} kB\n")
        (directory / "cmdline").write_bytes(f"{name}\0--demo\0".encode())
        # A fake symlink is enough to validate the executable field.
        try:
            (directory / "exe").symlink_to(f"/usr/bin/{name}")
        except FileExistsError:
            pass
        task = directory / "task"
        task.mkdir(exist_ok=True)
        (task / str(pid)).mkdir(exist_ok=True)
        (directory / "cgroup").write_text("0::/user.slice/test.scope\n")

    def test_collects_parent_child_tree_and_identity(self):
        snapshot = ProcCollector(self.root).collect()
        self.assertEqual(snapshot.boot_id, "boot-test-001")
        self.assertEqual(set(snapshot.processes), {1, 20, 21})
        self.assertEqual(snapshot.children_by_pid[20], [21])
        self.assertIn(1, snapshot.roots)
        self.assertEqual(snapshot.processes[21].rss_bytes, 96 * 1024)
        self.assertEqual(snapshot.processes[21].identity, ProcessIdentity("boot-test-001", 21, 210))
        self.assertEqual(snapshot.processes[21].thread_ids, [21])
        self.assertEqual(snapshot.processes[21].cgroups, ["hierarchy 0 (unified): /user.slice/test.scope"])

    def test_parent_missing_process_becomes_root_with_no_fabricated_parent(self):
        self.add_process(22, "late-child", "S", 999, 220)
        snapshot = ProcCollector(self.root).collect()
        self.assertIn(22, snapshot.roots)
        self.assertNotIn(22, snapshot.children_by_pid.get(999, []))

    def test_collects_process_group_session_and_terminal_fields(self):
        directory = self.root / "21"
        (directory / "stat").write_text(make_stat(21, "child", "R", 20, 210, pgid=19, sid=18, tty=7))
        record = ProcCollector(self.root).collect().processes[21]
        self.assertEqual(record.process_group_id, 19)
        self.assertEqual(record.session_id, 18)
        self.assertEqual(record.terminal_id, 7)

    def test_json_serialization_is_safe(self):
        data = ProcCollector(self.root).collect().as_dict()
        encoded = json.dumps(data)
        self.assertIn('"boot_id": "boot-test-001"', encoded)
        self.assertIn('"start_time_ticks": 210', encoded)

    def test_missing_boot_id_is_fatal(self):
        (self.root / "sys/kernel/random/boot_id").unlink()
        with self.assertRaises(ProcCollectorError):
            ProcCollector(self.root).collect()

    def test_skips_non_numeric_proc_entries(self):
        (self.root / "self").mkdir()
        snapshot = ProcCollector(self.root).collect()
        self.assertEqual(set(snapshot.processes), {1, 20, 21})

    def test_disappearing_process_does_not_break_snapshot(self):
        (self.root / "22").mkdir()
        # Missing stat simulates a process disappearing during collection.
        snapshot = ProcCollector(self.root).collect()
        self.assertEqual(set(snapshot.processes), {1, 20, 21})
        self.assertGreaterEqual(snapshot.skipped_processes, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
