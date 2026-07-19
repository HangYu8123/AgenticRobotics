import tempfile
import unittest
from pathlib import Path

from agentic_robot import ledger


class _CrashAt(Exception):
    pass


class AtomicWriteCrashTests(unittest.TestCase):
    def test_crash_at_every_boundary_leaves_file_fully_old_or_new(self):
        for boundary in ("prepare", "write", "fsync", "rename"):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as d:
                target = Path(d) / "record.json"
                target.write_bytes(b"OLD")

                def hook(b, want=boundary):
                    if b == want:
                        raise _CrashAt(b)

                with self.assertRaises(_CrashAt):
                    ledger.atomic_write(target, b"NEW", crash_hook=hook)

                # Before the rename the target is untouched; at/after it, fully new.
                content = target.read_bytes()
                self.assertIn(content, (b"OLD", b"NEW"), f"torn file at {boundary}: {content!r}")
                if boundary in ("prepare", "write", "fsync"):
                    self.assertEqual(content, b"OLD")
                else:
                    self.assertEqual(content, b"NEW")

    def test_successful_write_replaces_content_and_leaves_no_tmp(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "record.json"
            ledger.atomic_write(target, b"first")
            ledger.atomic_write(target, b"second")
            self.assertEqual(target.read_bytes(), b"second")
            self.assertFalse((Path(d) / "record.json.tmp").exists())


class EventLedgerTests(unittest.TestCase):
    def test_append_and_read_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ledger.EVENTS_FILENAME
            ledger.append_event(path, {"event": "round_scored", "round": 1, "metric": 83.5})
            ledger.append_event(path, {"event": "round_scored", "round": 2, "metric": 84.0})
            events = ledger.read_events(path)
            self.assertEqual([e["round"] for e in events], [1, 2])

    def test_crash_before_append_keeps_prior_lines_intact(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ledger.EVENTS_FILENAME
            ledger.append_event(path, {"event": "a", "round": 1})

            def hook(b):
                if b == "prepare":
                    raise _CrashAt(b)

            with self.assertRaises(_CrashAt):
                ledger.append_event(path, {"event": "b", "round": 2}, crash_hook=hook)
            # The second line was never written; the first stays readable/parseable.
            events = ledger.read_events(path)
            self.assertEqual(events, [{"event": "a", "round": 1}])

    def test_render_markdown_mentions_events(self):
        md = ledger.render_events_markdown([{"event": "exit", "round": 3, "verdict": "PASS"}])
        self.assertIn("exit", md)
        self.assertIn("round 3", md)
        self.assertIn("verdict: PASS", md)


if __name__ == "__main__":
    unittest.main()
