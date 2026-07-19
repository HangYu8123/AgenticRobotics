# Contributing

Thanks for helping improve `robot_agentic_training_flow`. This repo is a
**spec-driven controller plus a skills library** — most of it is markdown the
LLM controller executes, and a small deterministic **control-plane** package
(`agentic_robot/`) plus its recovery core (`recovery/`). Contributions fall into
one of those two lanes; keep them separate in a change.

## Ground rules

- **The flow spec is authoritative.** `robot_agentic_training_flow.md`,
  `objective.example.yaml`, and `skills/index.md` define behavior. Code in
  `agentic_robot/`/`recovery/` must *mirror* the spec, never quietly diverge from
  it. If code and spec disagree, that is a bug in one of them — say which.
- **Control-plane only.** `agentic_robot/` implements deterministic operations
  (objective validation, hashing, atomic writes, scoring, replay). It does **not**
  run training/eval — that is the LLM controller's job.
- **Surgical changes.** Touch only what the change requires. Don't reformat or
  "improve" adjacent code.
- **Evidence over assertion.** New behavior lands with a test that exercises it.

## Development setup

```bash
python -m pip install -e ".[dev]"   # installs pytest, hypothesis, ruff, mypy
```

## The gate (run before opening a PR)

CI (`.github/workflows/ci.yml`) runs these on Python 3.10–3.12; run them locally:

```bash
python -m compileall agentic_robot recovery tests
ruff check agentic_robot
mypy agentic_robot
pytest -q
```

Default test discovery runs the recovery tests plus the schema, skill, ledger,
scoring, CLI-integration, and property-based suites. All must pass.

## Adding a skill

Follow **Creating a new skill** in `skills/index.md`: the round-time minimal
`SKILL.md` shape, one index row, and registration under `skills/LIBRARY.lock`.
Record evidence honestly and promote `metadata.evidence_tier` only on replicated
evidence (see *Evidence tiers* in the index).

## Reporting security issues

See [`SECURITY.md`](SECURITY.md) — do not open a public issue for vulnerabilities.
