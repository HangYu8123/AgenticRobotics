import copy
import hashlib
import json
import unittest
from pathlib import Path

from recovery.replay_checker import check_replay, recover_partial_append


COMMIT_KEY = "a" * 64


def _ready_state():
    return {
        "schema_version": 1,
        "status": "IN_PROGRESS",
        "current_round": 1,
        "next_round": 2,
        "objective_digest": "objective-digest",
        "score_state": {"metric_best": 50.0},
        "generation_high_water": 2,
        "measurement_generation_high_water": 1,
        "active_waits": {},
        "completed_waits": {
            "2": {
                "status": "CLAIMED",
                "owner": "measure:1",
                "launch_key": "round-1-measure-1",
                "event_trigger_key": "event-2",
                "fallback_trigger_key": "fallback-2",
                "outcome": "SUCCESS",
                "verification": "exit and artifact",
            }
        },
        "execution_leases": {},
        "phase_transitions": {},
        "measurement_attempts": {
            "1": {
                "wait_generation": 2,
                "checkpoint": "/checkpoint/1",
                "eval_dir": "/eval/1",
                "command": "evaluate",
                "outcome": "SUCCESS",
            }
        },
        "round_log_inputs": {"phase": "READY_TO_SCORE"},
        "score_applied": None,
        "registration_committed": None,
        "cleanup": None,
        "prepared_ledger_block": None,
        "ledger_committed": None,
        "round_advanced": None,
    }


class ReplayCheckerTests(unittest.TestCase):
    def test_ready_to_score_replays_to_round_advanced(self):
        states = [_ready_state()]

        score = copy.deepcopy(states[-1])
        score["round_log_inputs"]["phase"] = "SCORE_APPLIED"
        score["score_applied"] = COMMIT_KEY
        states.append(score)

        registration = copy.deepcopy(states[-1])
        registration["round_log_inputs"]["phase"] = "REGISTRATION_COMMITTED"
        registration["registration_committed"] = COMMIT_KEY
        states.append(registration)

        cleanup = copy.deepcopy(states[-1])
        cleanup["round_log_inputs"]["phase"] = "CLEANUP_COMPLETE"
        cleanup["cleanup"] = {"commit_key": COMMIT_KEY, "complete": True}
        states.append(cleanup)

        ledger = copy.deepcopy(states[-1])
        ledger["round_log_inputs"]["phase"] = "LEDGER_COMMITTED"
        ledger["ledger_committed"] = COMMIT_KEY
        states.append(ledger)

        advanced = copy.deepcopy(states[-1])
        advanced["round_log_inputs"]["phase"] = "ROUND_ADVANCED"
        advanced["round_advanced"] = COMMIT_KEY
        advanced["status"] = "COMPLETED"
        states.append(advanced)

        original = copy.deepcopy(states)
        check_replay(states)
        check_replay(states)
        self.assertEqual(states, original)
        self.assertEqual(states[-1]["next_round"], states[-1]["current_round"] + 1)

        skipped = [states[0], states[2]]
        with self.assertRaisesRegex(ValueError, "invalid commit phase transition"):
            check_replay(skipped)

        next_round = copy.deepcopy(advanced)
        next_round.update(
            {
                "status": "IN_PROGRESS",
                "current_round": 2,
                "next_round": 3,
                "active_waits": {},
                "completed_waits": {},
                "execution_leases": {},
                "phase_transitions": {},
                "measurement_attempts": {},
                "score_applied": None,
                "registration_committed": None,
                "cleanup": None,
                "prepared_ledger_block": None,
                "ledger_committed": None,
                "round_advanced": None,
            }
        )
        next_round["round_log_inputs"] = {"phase": "ROUND_START"}
        check_replay([advanced, next_round])

        remeasure = copy.deepcopy(next_round)
        remeasure["round_log_inputs"] = {"phase": "REMEASURE_ONLY"}
        check_replay([advanced, remeasure])

        stale = copy.deepcopy(next_round)
        stale["completed_waits"] = copy.deepcopy(advanced["completed_waits"])
        stale["measurement_attempts"] = copy.deepcopy(advanced["measurement_attempts"])
        with self.assertRaisesRegex(ValueError, "must clear completed_waits"):
            check_replay([advanced, stale])

        for field in ("execution_leases", "phase_transitions"):
            stale_map = copy.deepcopy(next_round)
            stale_map[field] = {"stale": {}}
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, f"must clear {field}"
            ):
                check_replay([advanced, stale_map])

    def test_partial_ledger_append_recovery_at_byte_boundary(self):
        prefix = "ledger header — λ\n".encode("utf-8")
        block_text = "<!-- BEGIN -->\nmetric: 88 🚀\n<!-- END -->\n"
        block = block_text.encode("utf-8")
        prepared = {
            "block": block_text,
            "block_sha256": hashlib.sha256(block).hexdigest(),
            "byte_length": len(block),
            "pre_append_offset": len(prefix),
            "pre_append_prefix_sha256": hashlib.sha256(prefix).hexdigest(),
        }

        for cut in range(1, len(block)):
            with self.subTest(cut=cut):
                repaired = recover_partial_append(prefix + block[:cut], prepared)
                self.assertEqual(repaired, prefix + block)
                self.assertEqual(recover_partial_append(repaired, prepared), repaired)

        with self.assertRaisesRegex(ValueError, "strict prefix"):
            recover_partial_append(prefix + block[:5] + b"conflict", prepared)
        with self.assertRaisesRegex(ValueError, "non-empty partial"):
            recover_partial_append(prefix, prepared)

    def test_interrupted_wait_moves_atomically_without_new_generation(self):
        before = _ready_state()
        before["round_log_inputs"]["phase"] = "EXECUTING"
        before["generation_high_water"] = 5
        before["measurement_generation_high_water"] = 3
        before["completed_waits"] = {}
        before["active_waits"] = {
            "5": {
                "status": "WAITING",
                "owner": "measure:3",
                "launch_key": "round-1-measure-3",
                "event_trigger_key": "event-5",
                "fallback_trigger_key": "fallback-5",
            }
        }
        before["measurement_attempts"] = {
            "3": {
                "wait_generation": 5,
                "checkpoint": "/checkpoint/3",
                "eval_dir": "/eval/3",
                "command": "evaluate",
                "outcome": "PREPARED",
            }
        }

        after = copy.deepcopy(before)
        completed = after["active_waits"].pop("5")
        completed.update(
            {"status": "CLAIMED", "outcome": "SUCCESS", "verification": "exit and artifact"}
        )
        after["completed_waits"]["5"] = completed
        after["measurement_attempts"]["3"]["outcome"] = "SUCCESS"

        check_replay([before, after])
        self.assertEqual(after["generation_high_water"], 5)
        self.assertEqual(after["measurement_generation_high_water"], 3)

        changed_identity = copy.deepcopy(after)
        changed_identity["completed_waits"]["5"]["launch_key"] = "different"
        with self.assertRaisesRegex(ValueError, "immutable field launch_key"):
            check_replay([before, changed_identity])

        regressed = copy.deepcopy(before)
        regressed["active_waits"]["5"]["status"] = "PREPARED"
        with self.assertRaisesRegex(ValueError, "status regressed"):
            check_replay([before, regressed])

    def test_rejects_decreasing_high_water_and_broken_binding(self):
        state = _ready_state()
        before = copy.deepcopy(state)
        before["round_log_inputs"]["phase"] = "EXECUTING"
        before["active_waits"] = {}
        before["completed_waits"] = {}
        before["measurement_attempts"] = {}
        before["generation_high_water"] = 5
        before["measurement_generation_high_water"] = 4
        after = copy.deepcopy(before)
        after["generation_high_water"] = 4
        with self.assertRaisesRegex(ValueError, "generation_high_water decreased"):
            check_replay([before, after])

        after = copy.deepcopy(before)
        after["measurement_generation_high_water"] = 3
        with self.assertRaisesRegex(ValueError, "measurement_generation_high_water decreased"):
            check_replay([before, after])

        reused = copy.deepcopy(before)
        reused["active_waits"]["5"] = {"status": "PREPARED", "owner": "train:round1"}
        with self.assertRaisesRegex(ValueError, "wait generation 5 was reused"):
            check_replay([before, reused])

        reused_measurement = copy.deepcopy(before)
        reused_measurement["generation_high_water"] = 6
        reused_measurement["active_waits"]["6"] = {
            "status": "PREPARED",
            "owner": "measure:4",
        }
        reused_measurement["measurement_attempts"]["4"] = {"wait_generation": 6}
        with self.assertRaisesRegex(ValueError, "measurement generation 4 was reused"):
            check_replay([before, reused_measurement])

        broken = copy.deepcopy(state)
        broken["completed_waits"]["2"]["owner"] = "measure:9"
        with self.assertRaisesRegex(ValueError, "does not reciprocally own"):
            check_replay([broken])

        bypass = copy.deepcopy(state)
        bypass["current_round"] = 2
        bypass["next_round"] = 3
        bypass["round_log_inputs"]["phase"] = "EXECUTING"
        with self.assertRaisesRegex(ValueError, "new round must start from ROUND_ADVANCED"):
            check_replay([state, bypass])

        unknown = copy.deepcopy(state)
        unknown["round_log_inputs"]["phase"] = "SOMETHING_ELSE"
        with self.assertRaisesRegex(ValueError, "unknown round_log_inputs.phase"):
            check_replay([unknown])

        bad_outcome = copy.deepcopy(state)
        bad_outcome["measurement_attempts"]["1"]["outcome"] = 42
        with self.assertRaisesRegex(ValueError, "outcome must be a string"):
            check_replay([bad_outcome])

        invalid_evidence = (
            ("outcome", None),
            ("outcome", ""),
            ("verification", None),
            ("verification", ""),
            ("verification", {}),
        )
        for field, value in invalid_evidence:
            missing_evidence = copy.deepcopy(state)
            missing_evidence["completed_waits"]["2"][field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(
                ValueError, "non-empty"
            ):
                check_replay([missing_evidence])

    def test_run_id_persists_across_replacements(self):
        before = _ready_state()
        before["run_id"] = "r" * 64

        after = copy.deepcopy(before)
        after["round_log_inputs"]["phase"] = "SCORE_APPLIED"
        after["score_applied"] = COMMIT_KEY
        check_replay([before, after])

        changed = copy.deepcopy(after)
        changed["run_id"] = "x" * 64
        with self.assertRaisesRegex(ValueError, "run_id changed or was dropped"):
            check_replay([before, changed])

        dropped = copy.deepcopy(after)
        del dropped["run_id"]
        with self.assertRaisesRegex(ValueError, "run_id changed or was dropped"):
            check_replay([before, dropped])

        legacy = _ready_state()  # predates [run identity]: no run_id
        gains = copy.deepcopy(legacy)
        gains["run_id"] = "r" * 64
        check_replay([legacy, gains])

        advanced = copy.deepcopy(after)
        advanced["round_log_inputs"] = {"phase": "ROUND_ADVANCED"}
        advanced["registration_committed"] = COMMIT_KEY
        advanced["cleanup"] = {"commit_key": COMMIT_KEY, "complete": True}
        advanced["ledger_committed"] = COMMIT_KEY
        advanced["round_advanced"] = COMMIT_KEY
        advanced["status"] = "COMPLETED"

        next_round = copy.deepcopy(advanced)
        next_round.update(
            {
                "status": "IN_PROGRESS",
                "current_round": 2,
                "next_round": 3,
                "completed_waits": {},
                "measurement_attempts": {},
                "score_applied": None,
                "registration_committed": None,
                "cleanup": None,
                "ledger_committed": None,
                "round_advanced": None,
            }
        )
        next_round["round_log_inputs"] = {"phase": "ROUND_START"}
        check_replay([advanced, next_round])

        dropped_at_init = copy.deepcopy(next_round)
        del dropped_at_init["run_id"]
        with self.assertRaisesRegex(ValueError, "run_id changed or was dropped"):
            check_replay([advanced, dropped_at_init])

        empty = _ready_state()
        empty["run_id"] = ""
        with self.assertRaisesRegex(ValueError, "run_id must be a non-empty string"):
            check_replay([empty])

    def test_schema_and_thin_wrapper_conformance(self):
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "recovery" / "round_state.schema.json").read_text())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertTrue(schema["additionalProperties"])
        self.assertIn("schema_version", schema["required"])

        missing_version = _ready_state()
        missing_version.pop("schema_version")
        with self.assertRaisesRegex(ValueError, "schema_version must be 1"):
            check_replay([missing_version])

        bad_cleanup = _ready_state()
        bad_cleanup["cleanup"] = {"complete": False}
        with self.assertRaisesRegex(ValueError, "cleanup.commit_key"):
            check_replay([bad_cleanup])

        bad_prepared = _ready_state()
        bad_prepared["prepared_ledger_block"] = {"block": "incomplete"}
        with self.assertRaisesRegex(ValueError, "prepared.byte_length"):
            check_replay([bad_prepared])

        wrapper = (root / "SKILL.md").read_text()
        self.assertIn("robot_agentic_training_flow.md", wrapper)
        self.assertNotIn("OPTIONS.md", wrapper)
        self.assertLessEqual(len(wrapper.splitlines()), 12)


if __name__ == "__main__":
    unittest.main()
