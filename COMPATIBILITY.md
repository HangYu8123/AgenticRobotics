# Compatibility

## LeRobot

Every training/eval command in this repo's skills runs against an **external**
[LeRobot](https://github.com/huggingface/lerobot) repo (the objective's `workdir`),
prefixed `uv run`. LeRobot moves quickly, so the skills pin to a known-good release.

**Supported / tested-against release: `v0.6.0`** (released 2026-07-06).

| LeRobot | Status | Notes |
|---|---|---|
| `v0.6.0` | ✅ supported | Current pin. `env_eval_freq` (renamed from `eval_freq`), reward-model API under `src/lerobot/rewards/`, deployment CLI. |
| `v0.5.x` | ⚠️ best-effort | Pre-`v0.6.0` config/flag names differ; skills referencing `env_eval_freq` or the rewards factory may need the old names. |
| `< v0.5` | ❌ untested | Not validated against this flow. |

> **Breaking change in v0.6.0:** `pip install lerobot` no longer bundles dataset/
> training dependencies by default — install the extra, e.g. `pip install
> "lerobot[training]"` (or the `uv` equivalent), in the external LeRobot repo.

This is a **documented** pin, not an executed CI matrix: LeRobot requires GPU and
heavy dependencies that this repo's CI (which tests only the deterministic
control-plane) does not install. When bumping the pin, run the loop against the new
release manually and update the table above with what changed.

## Python

The `agentic_robot` control-plane package and `recovery` core target **Python
3.10–3.12** (CI matrix). Runtime dependencies: `PyYAML`, `jsonschema` (see
`pyproject.toml`); dev extras add `pytest`, `hypothesis`, `ruff`, `mypy`.

## External evaluation harnesses (referenced, not vendored)

The optional acceptance gate (`acceptance_eval` in `objective.example.yaml`) points
at an operator-run harness rather than vendoring one:

- **LIBERO-PRO** — perturbation suites (object/state/instruction/environment).
  Paper: <https://arxiv.org/abs/2510.03827>.
- **vla-eval** — container-isolated model×benchmark matrix (Apache-2.0, GPU/Docker).
  Repo: <https://github.com/allenai/vla-evaluation-harness>.
