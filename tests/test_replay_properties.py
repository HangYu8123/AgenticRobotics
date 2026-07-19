"""Property-based tests for replay idempotence and generation non-reuse.

Skipped automatically when hypothesis is not installed, so default `unittest`
discovery still passes; CI installs the dev extras and runs them.
"""

import copy
import unittest

from recovery.replay_checker import check_replay

try:
    from hypothesis import given, settings
    from hypothesis import strategies as st

    HAS_HYPOTHESIS = True
except ImportError:  # pragma: no cover - exercised only without the dev extra
    HAS_HYPOTHESIS = False


def _executing_state(round_no, metric_best, high_water):
    return {
        "schema_version": 1,
        "status": "IN_PROGRESS",
        "current_round": round_no,
        "next_round": round_no + 1,
        "objective_digest": "digest",
        "score_state": {"metric_best": metric_best},
        "generation_high_water": high_water,
        "measurement_generation_high_water": 0,
        "active_waits": {},
        "completed_waits": {},
        "execution_leases": {},
        "phase_transitions": {},
        "measurement_attempts": {},
        "round_log_inputs": {"phase": "EXECUTING"},
    }


@unittest.skipUnless(HAS_HYPOTHESIS, "hypothesis not installed")
class ReplayPropertyTests(unittest.TestCase):
    @settings(max_examples=200, deadline=None)
    @given(
        round_no=st.integers(min_value=0, max_value=1000),
        metric_best=st.floats(allow_nan=False, allow_infinity=False, width=32),
        high_water=st.integers(min_value=0, max_value=50),
    )
    def test_check_replay_is_pure_and_idempotent(self, round_no, metric_best, high_water):
        state = _executing_state(round_no, metric_best, high_water)
        original = copy.deepcopy(state)
        check_replay([state])
        check_replay([state])  # idempotent: a second pass behaves identically
        self.assertEqual(state, original)  # pure: never mutates its input

    @settings(max_examples=200, deadline=None)
    @given(
        high_water=st.integers(min_value=1, max_value=50),
        reused=st.data(),
    )
    def test_reusing_a_wait_generation_is_rejected(self, high_water, reused):
        g = reused.draw(st.integers(min_value=1, max_value=high_water))
        before = _executing_state(1, 50.0, high_water)
        after = copy.deepcopy(before)
        after["active_waits"][str(g)] = {"status": "PREPARED", "owner": "train:x"}
        with self.assertRaisesRegex(ValueError, "reused"):
            check_replay([before, after])

    @settings(max_examples=100, deadline=None)
    @given(high_water=st.integers(min_value=0, max_value=50))
    def test_fresh_generation_above_high_water_is_accepted(self, high_water):
        before = _executing_state(1, 50.0, high_water)
        g = high_water + 1
        after = copy.deepcopy(before)
        after["generation_high_water"] = g
        after["active_waits"][str(g)] = {"status": "PREPARED", "owner": "train:x"}
        check_replay([before, after])  # must not raise


if __name__ == "__main__":
    unittest.main()
