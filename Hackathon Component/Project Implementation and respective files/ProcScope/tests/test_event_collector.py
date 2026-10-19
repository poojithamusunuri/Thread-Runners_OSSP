import struct
import unittest
from event_collector import EventCollector, CN_IDX_PROC, CN_VAL_PROC

class EventCollectorTests(unittest.TestCase):
    def test_decodes_fork_event_as_observed(self):
        payload = struct.pack("=IIII", 12, 12, 34, 34)
        proc_event = struct.pack("=IIQ", 1, 0, 123456789) + payload
        cn = struct.pack("=IIIIHH", CN_IDX_PROC, CN_VAL_PROC, 1, 0, len(proc_event), 0) + proc_event
        msg = struct.pack("=IHHII", 16 + len(cn), 3, 0, 1, 100) + cn
        result = EventCollector()._decode(msg)
        self.assertEqual(result["kind"], "fork")
        self.assertEqual(result["pid"], 34)
        self.assertEqual(result["ppid"], 12)
        self.assertEqual(result["confidence"], "observed")

    def test_ignores_short_or_invalid_messages(self):
        collector = EventCollector()
        self.assertIsNone(collector._decode(b"short"))
        self.assertIsNone(collector._decode(b"\0" * 80))

    def test_default_status_is_not_claimed_available(self):
        status = EventCollector().status()
        self.assertEqual(status["status"], "stopped")
        self.assertEqual(status["event_count"], 0)
        self.assertTrue(status["limitations"])

if __name__ == "__main__": unittest.main()
