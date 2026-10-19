import unittest
from lab_manager import ALLOWED, LAB, LabError

class LabManagerTests(unittest.TestCase):
    def test_only_allowlisted_experiments_are_available(self):
        self.assertEqual(set(ALLOWED), {"zombie", "orphan", "pipeline", "threads", "fork-exec"})
        with self.assertRaises(LabError):
            LAB.start("arbitrary-command")

    def test_experiment_metadata_is_explanatory(self):
        for item in ALLOWED.values():
            self.assertTrue(item["title"])
            self.assertTrue(item["summary"])
            self.assertTrue(item["expected"])
            self.assertGreater(item["duration"], 0)

    def test_start_and_stop_zombie_experiment(self):
        run = LAB.start("zombie")
        self.assertEqual(run["experiment"], "zombie")
        self.assertEqual(run["status"], "running")
        stopped = LAB.stop(run["id"])
        self.assertEqual(stopped["status"], "stopped")

    def test_status_includes_run_history(self):
        payload = LAB.status()
        self.assertIn("runs", payload)
        self.assertIn("max_active", payload)
        self.assertLessEqual(payload["max_active"], 4)

if __name__ == "__main__":
    unittest.main()
