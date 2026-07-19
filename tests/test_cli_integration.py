"""End-to-end CLI + control-plane integration using FAKE train/eval commands.

No real LeRobot is involved: a tiny fake eval command writes an eval_info.json in
the documented shape, and the deterministic scoring/validation/replay path is
driven over a synthesized run directory.
"""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from agentic_robot import cli, ledger, scoring, state


def _write_objective(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """
            run_dir: outputs/run
            metric_path: overall.pc_success
            comparison: ">="
            target: 80.0
            eval_command: |
              uv run lerobot-eval --policy.path={checkpoint} --output_dir={eval_dir}
            stagnation_rounds: 2
            acceptance:
              success_rate: {comparison: ">=", target: 0.80}
              unsafe_success_rate: {comparison: "<=", target: 0.00}
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


class FakeEvalCommandTests(unittest.TestCase):
    def test_fake_eval_writes_parseable_metric(self):
        with tempfile.TemporaryDirectory() as d:
            eval_dir = Path(d) / "eval"
            eval_dir.mkdir()
            fake = Path(d) / "fake_eval.py"
            fake.write_text(
                "import json,sys,pathlib;"
                "p=pathlib.Path(sys.argv[1]);"
                "p.write_text(json.dumps({'overall':{'pc_success':83.5}}))",
                encoding="utf-8",
            )
            out = eval_dir / "eval_info.json"
            subprocess.run([sys.executable, str(fake), str(out)], check=True)
            eval_info = json.loads(out.read_text())
            value = scoring.parse_metric(eval_info, "overall.pc_success")
            self.assertTrue(scoring.compare(value, ">=", 80.0))


class CliVerbTests(unittest.TestCase):
    def test_validate_ok_and_bad(self):
        with tempfile.TemporaryDirectory() as d:
            good = Path(d) / "obj.yaml"
            _write_objective(good)
            self.assertEqual(cli.main(["validate", str(good)]), 0)

            bad = Path(d) / "bad.yaml"
            bad.write_text("run_dir: x\n", encoding="utf-8")
            self.assertEqual(cli.main(["validate", str(bad)]), 1)

    def test_init_scaffolds_then_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "new.yaml"
            self.assertEqual(cli.main(["init", str(dest)]), 0)
            self.assertTrue(dest.exists())
            self.assertEqual(cli.main(["init", str(dest)]), 1)

    def test_status_report_resume_over_synth_run(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d) / "run"
            run.mkdir()
            (run / "LOOP_LOG.md").write_text(
                "# LOOP_LOG\n<!-- ROUND_ENTRY_BEGIN commit_key=a -->\nMetric: 83.5\n"
                "<!-- ROUND_ENTRY_END commit_key=a -->\n",
                encoding="utf-8",
            )
            (run / "CONTINUATION.json").write_text(
                json.dumps(
                    {
                        "run_id": "r" * 8,
                        "status": "IN_PROGRESS",
                        "current_round": 1,
                        "pending_action": "resume phase READY_TO_SCORE of round 1",
                        "reentry_prompt": "Follow robot_agentic_training_flow.md with objective X.",
                    }
                ),
                encoding="utf-8",
            )
            ledger.append_event(run / ledger.EVENTS_FILENAME, {"event": "round_scored", "round": 1})

            self.assertEqual(cli.main(["status", str(run)]), 0)
            self.assertEqual(cli.main(["report", str(run)]), 0)
            self.assertEqual(cli.main(["resume", str(run)]), 0)

    def test_replay_over_exported_snapshots(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d) / "run"
            run.mkdir()
            snap = {
                "schema_version": 1,
                "status": "IN_PROGRESS",
                "current_round": 1,
                "next_round": 2,
                "objective_digest": "digest",
                "score_state": {"metric_best": 50.0},
                "generation_high_water": 0,
                "measurement_generation_high_water": 0,
                "active_waits": {},
                "completed_waits": {},
                "execution_leases": {},
                "phase_transitions": {},
                "measurement_attempts": {},
                "round_log_inputs": {"phase": "ROUND_START"},
            }
            (run / state.SNAPSHOTS_FILENAME).write_text(json.dumps(snap) + "\n", encoding="utf-8")
            self.assertEqual(cli.main(["replay", str(run)]), 0)

    def test_status_missing_log_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(cli.main(["status", d]), 1)


if __name__ == "__main__":
    unittest.main()
