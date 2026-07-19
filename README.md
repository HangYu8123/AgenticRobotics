# Robot Agentic Training Loop

An agent-executable specification for a self-improving robot-policy training loop: train → evaluate → improve until an external target is met.

This repository is not a conventional software project — the "program" is [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md), a strict, step-numbered control-flow spec that an LLM coding agent (Claude Code, Codex, or VS Code Copilot) reads and executes against an external [LeRobot](https://github.com/huggingface/lerobot) checkout. The loop binds an immutable, operator-owned objective (a metric target such as `overall.pc_success >= 80.0`), then runs rounds of train/tune/diagnose/measure until that exit condition holds, accumulating everything it learns into a reusable, self-growing [skills library](skills/index.md). It produces an improved policy checkpoint, an append-only run ledger, and new skills for the next run. The only conventional code in the repo is a small crash-recovery checker module (`recovery/`, exercised by `tests/test_recovery.py`) and the vendored offline skill tooling.

## Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [Components](#components)
  - [1. The flow specification](#1-the-flow-specification)
  - [2. The skills library (`skills/`)](#2-the-skills-library-skills)
  - [3. Offline skill tooling (`skills/original/skill-creator/`)](#3-offline-skill-tooling-skillsoriginalskill-creator)
  - [4. Orchestration pack and entry points](#4-orchestration-pack-and-entry-points)
- [Usage](#usage)
  - [Running the loop](#running-the-loop)
  - [Control-plane CLI (`agentic-robot`)](#control-plane-cli-agentic-robot)
  - [External commands the skills drive](#external-commands-the-skills-drive)
  - [Offline skill tooling commands](#offline-skill-tooling-commands)
- [Code examples](#code-examples)
- [Notes](#notes)

## Pipeline Overview

The flow casts the main agent as a **controller, not a doer**: it spends its context only on decisions — binding the objective, choosing each round's action set, parsing the metric itself, scoring, writing the ledger, deciding halts and exit. All token-heavy work (running commands, reading logs and videos, writing scripts, researching, debugging) is delegated to stateless, time-boxed subagents that return compact results.

```text
objective.yaml (operator-owned, immutable)
      |
      v
Step 0  Bind        — validate objective against the canonical schema, run the
      |               command preflight, sha256-digest it, create run_dir +
      |               ledger + durable round record
      v
Step 1  Baseline    — 1a preflight probe / 1b initialize / 1c trained-policy
      |               baseline (round 0 metric, first champion)
      v
Step 2  Sanity gate — objective reachable? degenerate signal? already met?
      |
      v
Step 3  Round loop  — (a) Verify  (b) Read skills index  (c) Analyze
      |               (d) Decide action set  (e) Execute skills via workers
      |               (f) Measure: run eval_command verbatim -> eval_info.json
      |               (g) Score against the noise band  (h) Register new skills
      |               (i) Log the round entry            ... repeat until exit
      v
Step 4  Exit        — exit condition holds; a Devils Advocate subagent
                      re-verifies independently before the exit report
```

Ten invariants govern every round — most importantly: the objective is external and immutable (1), the exit condition is the only exit (2), progress is measured from `eval_info.json` by the controller itself, never asserted by a worker (3), and the flow file is never modified at runtime — only the outputs grow (6). Rounds are crash-safe: side effects are commit-keyed, waits are generation-scoped, and dispatches carry execution leases, so a killed session recovers by completing partially committed phases instead of repeating them.

**Run outputs** (all under the objective's `run_dir`, outside this repo): `LOOP_LOG.md` (append-only ledger, one entry per round), `ROUND_IN_PROGRESS.md` (durable round transaction and recovery record), `CHAMPION` (derived best-checkpoint pointer), and per-attempt eval directories `round_<n>/eval_g<m>` (fresh per measurement generation; never reused). One more output lives in this repo: `skills/` grows with every reusable behavior a run discovers.

## Components

### 1. The flow specification

The program, its parameter contract, and the recovery checkers it calls. **Input:** an operator-filled objective YAML. **Output:** run ledger, durable round record, champion pointer, and library growth.

| File | Key functionality | Key input / output | Key parameters |
|---|---|---|---|
| [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md) | The complete controller loop: `[term]` definitions, 10 invariants, a durable round-transaction/recovery protocol, and Steps 0–4 with a per-step dataflow line. | Reads the objective and `skills/index.md`; writes `LOOP_LOG.md`, `ROUND_IN_PROGRESS.md`, `CHAMPION`, and new skills. | None of its own — the run is parameterized entirely by the objective (Invariant 1). |
| [`objective.example.yaml`](objective.example.yaml) | Canonical schema for the operator-owned objective, validated at Step 0 and never edited by the agent. | Copied outside the repo and filled in by the operator; read-only bound (sha256-digested) at Step 0. | `run_dir`, `metric_path`, `comparison`, `target`, `eval_command` (with `{checkpoint}`/`{eval_dir}` placeholders), `stagnation_rounds`; optional `min_delta`, `workdir`, `allowed_executables`, `preflight_eval_command`. |
| [`recovery/replay_checker.py`](recovery/replay_checker.py) | Pure structural checkers the flow's recovery protocol calls on schema-backed round records: `check_replay` (cross-snapshot consistency before replacement/replay) and `recover_partial_append` (byte-exact repair of a partially appended ledger block). | Decoded round-record mappings / prepared ledger bytes → a pass verdict or a halt. | Gates only records carrying `schema_version: 1`; covered by `tests/test_recovery.py`. |
| [`recovery/round_state.schema.json`](recovery/round_state.schema.json) | Machine-readable shape of the decoded round-record logical mapping — it never prescribes, parses, or migrates `ROUND_IN_PROGRESS.md`'s on-disk encoding. | A decoded round-record mapping → schema validity. | Optional `schema_version: 1` marker on new records. |

### 2. The skills library (`skills/`)

The flow's growing menu of known-good procedures, following the [Agent Skills](https://agentskills.io) open standard (one directory per skill, `SKILL.md` with `name`/`description` frontmatter, `lifecycle`/`safety` nested under `metadata:`). **Input:** the controller's round brief. **Output:** executed procedures plus new/updated skill entries registered under a `flock`-serialized library transaction (`skills/LIBRARY.lock`), because concurrent loop instances share the library live.

The index routes by last round's verdict: PROGRESS → exploit (train more, tune); NO PROGRESS below the stagnation limit → cheapest levers first; at the limit → **switch strategy class** (diagnose, collect data, research); REGRESSION → diagnose, then revert to champion; ERROR → fix the measurement, never the policy. Lifecycle is `candidate` (documented, not yet evidenced in a logged round) → `validated` (survived a real round) → `deprecated` (kept for the record).

| Skill | Key functionality | Key input / output | Key parameters | Lifecycle |
|---|---|---|---|---|
| [`continuing-training`](skills/original/continuing-training/SKILL.md) | Starts a fresh `lerobot-train` run or resumes into the run's persistent `train_dir`, with a mandatory parser-resolved `resume_preflight.json` and an early runtime learning-rate gate on every resume. | Round brief (fresh/resume directive) + dataset id or `checkpoints/last` → new step checkpoints and a moved `last` symlink. | `--dataset.repo_id`, `--policy.type`, `--output_dir`, `--resume=true`, `--steps` (must exceed the checkpoint's total), top-level `--scheduler.num_decay_steps` for clamped resumes (`--policy.scheduler_decay_steps` is a no-op on resume). | validated |
| [`measuring-the-gate`](skills/original/measuring-the-gate/SKILL.md) | Runs the objective's `eval_command` verbatim — the mandatory feedback signal, never a hand-rolled variant. | `{checkpoint}` → `{eval_dir}/eval_info.json` containing the objective's `metric_path`, parsed by the controller itself. | None of its own — note the stock `lerobot-eval` aggregate lives at `overall.<key>`, not `aggregated.<key>`. | validated |
| [`collecting-data`](skills/original/collecting-data/SKILL.md) | Records additional teleoperated episodes when states are absent from the data — a strategy-class switch. | Robot hardware + existing dataset → K appended episodes, checked via `meta/info.json`. | `lerobot-record --resume=true --dataset.num_episodes=<K>`. | candidate |
| [`curating-dataset`](skills/original/curating-dataset/SKILL.md) | Inspects, cleans, augments, or restricts training to the evaluated suite. | Dataset repo → an edited/visualized dataset, or a non-destructive suite-filtered training lineage. | `lerobot-edit-dataset`; `lerobot-dataset-viz`; quoted `--dataset.episodes=[...]` on `continuing-training`. | validated |
| [`diagnosing-qualitatively`](skills/original/diagnosing-qualitatively/SKILL.md) | Watches rollouts, replays, and eval videos to see *how* the policy fails — produces a finding, not a metric change. | Eval videos / checkpoint → a failure-mode diagnosis steering the next round. | `lerobot-rollout`, `lerobot-replay`, `<eval_dir>/videos/`. | validated |
| [`researching-online`](skills/original/researching-online/SKILL.md) | Searches papers, docs, and issues to escape a plateau, returning a testable hypothesis with cited URLs. | A stagnation verdict → a hypothesis for the next action set. | Web search/fetch tools via the Online Researcher agent. | candidate |
| [`writing-new-scripts`](skills/original/writing-new-scripts/SKILL.md) | Writes a script for behavior the external repo lacks (augmentation, curriculum, custom eval). | A confirmed capability gap → a script under the run dir (registered here only if reusable). | — | candidate |
| [`checking-hardware`](skills/original/checking-hardware/SKILL.md) | Calibrates and checks cameras/ports when real-robot performance degrades with no software change. | Physical rig → calibration state re-verified with a reference move. | `lerobot-calibrate`, `lerobot-find-cameras`, `lerobot-find-port`. | candidate |
| [`scoring-with-reward-model`](skills/original/scoring-with-reward-model/SKILL.md) | Scores recorded real-robot episodes with a reward model when no gym env (and no `lerobot-eval`) exists. | Recorded episodes → `eval_info.json` in the standard contract shape. | Reward model choice: `robometer` \| `topreward` \| `sarm` \| `reward_classifier` (from LeRobot `src/lerobot/rewards/`). | candidate |
| [`reverting-to-champion`](skills/iterated/reverting-to-champion/SKILL.md) | Branches training back from the champion checkpoint after a **confirmed** regression (beyond the noise band). | Champion from the run's durable `score_state` (cross-checked against `CHAMPION`) → repointed `checkpoints/last`, quarantined newer step dirs, reproduction re-validated by eval. | Resume `--steps` must exceed the champion's step count. | candidate |
| [`skill-creator`](skills/original/skill-creator/SKILL.md) | Vendored Anthropic tooling for authoring and evaluating skills themselves — offline/operator-attended only, never mid-round. | A skill idea or draft → a validated, packaged, optionally benchmark-optimized skill. | See [offline tooling](#3-offline-skill-tooling-skillsoriginalskill-creator) below. | validated |
| [`preparing-runtime`](skills/iterated/preparing-runtime/SKILL.md) | Generic contract for installs/downloads/preprocessing: noninteractive, resumable, bounded-output, with durable exit evidence. | A slow/noisy setup step → a completed, evidence-backed runtime preparation. | Explicit interpreter/env, progress-off controls, hard log cap, disk/cache growth checks. | candidate |
| [`installing-libero-headless`](skills/iterated/installing-libero-headless/SKILL.md) | Installs LeRobot's LIBERO sim env (`hf-libero`) into the repo venv on a headless box. | A venv where `import libero` fails → a working EGL-rendering LIBERO install. | `CMAKE_POLICY_VERSION_MINIMUM=3.5`, `egl_probe==1.0.2` pin, first-import prompt drain, `MUJOCO_GL=egl`. | candidate |
| [`tuning-action-horizon`](skills/iterated/tuning-action-horizon/SKILL.md) | Shrinks a chunked VLA checkpoint's inference horizon for closed-loop control — a zero-cost config edit, no retraining. | Checkpoint `config.json` → a re-evaluated checkpoint (two exit-clearing wins on LIBERO: 64→85 and 52→88). | `n_action_steps` (e.g. 50→10, must stay ≤ `chunk_size`; ~5× more policy calls at horizon 10). | validated |

### 3. Offline skill tooling (`skills/original/skill-creator/`)

Vendored from [`anthropics/skills`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) (Apache-2.0) with a local preamble; strictly offline — a live round may use its writing conventions but never its eval loop. **Input:** a skill directory. **Output:** validation verdicts, `.skill` packages, benchmark reports.

| Script | Key functionality | Key input / output | Key parameters |
|---|---|---|---|
| `scripts/quick_validate.py` | Validates a `SKILL.md`'s frontmatter against the Agent Skills allowlist (name/description limits, allowed keys). | Skill directory → exit 0/1 plus a message. | One positional arg: the skill directory (requires PyYAML). |
| `scripts/package_skill.py` | Validates and zips a skill directory into a distributable `<name>.skill` archive. | Skill directory → `<name>.skill` zip. | Positional `skill-folder [output-directory]`; run as `python3 -m scripts.package_skill` (its `scripts.*` import fails as a direct script path). |
| `scripts/run_eval.py` | Trigger-testing: measures whether queries actually activate a skill by stream-parsing `claude -p` runs. | Eval queries + skill → per-query trigger rates. | `runs_per_query`, threshold; requires the `claude` CLI. |
| `scripts/run_loop.py` | Orchestrates the description-optimization loop (eval → improve description → re-eval) with a live HTML report. | A skill + eval set → best-scoring description and `results.json`/`report.html`. | `--model` (required), `--report auto\|none\|path`, `--results-dir`. |
| `scripts/improve_description.py` | Proposes an improved skill description from failed/false-trigger queries via `claude -p`. | Failure lists + skill content → a new `<new_description>` candidate. | `--model`, `--eval-results`, `--skill-path` (all required), optional `--history`/`--verbose`; requires the `claude` CLI. |
| `scripts/aggregate_benchmark.py` | Aggregates with-skill vs. without-skill grading runs into comparison stats. | `eval-N/*/run-N/grading.json` trees → `benchmark.json` + `benchmark.md`. | Benchmark dir, skill name/path. |
| `scripts/generate_report.py` | Renders an optimization-run history as a standalone HTML report. | History JSON → HTML (stdin/stdout supported). | Positional `input` (`-` for stdin), `-o/--output` (default stdout), `--skill-name`. |
| `scripts/utils.py` | Parses `SKILL.md` YAML frontmatter without PyYAML. | Skill directory `Path` → `(name, description, content)`. | — |
| `eval-viewer/generate_review.py` | Serves (or statically generates) a human review page for benchmark run outputs. | A workspace of run outputs → a browsable review page with feedback capture. | `workspace`, `--port` (default 3117), `--static` for headless use. |

### 4. Orchestration pack and entry points

Tool-facing scaffolding around the flow; not part of the loop itself. **Input:** a filled-in request-template prompt. **Output:** a routed pack workflow.

| File / Directory | Key functionality | Key input / output | Key parameters |
|---|---|---|---|
| `CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md` | Per-tool entry points that route filled-in `request_template/` prompts to pack workflows (anything else gets a normal answer). | A templated request → a classified, mode-selected workflow run. | `mode: fast\|general\|skill`, `simplify`/`code_review` headers. |
| `.github/HarnessFlow/` | The installed HarnessFlow orchestration pack: workflow contract, safety/stay-active rules, agent roster, and the repo's `repo_info/` context docs. | Workflow/agent definitions consumed by the orchestrating agent. | — (its internal `skills/` directory is pack tooling — **not** this repo's skills library). |

## Usage

### Running the loop

**The loop itself is executed by an LLM agent, not a CLI** — choosing experiments and interpreting failures is the controller's job. A small `agentic-robot` CLI ships alongside it for the *deterministic control-plane* only (validation, status, replay); it never runs training or eval (see [Control-plane CLI](#control-plane-cli-agentic-robot) below). The one required argument is a path to an objective spec:

```bash
# 1. Copy the objective template somewhere OUTSIDE this repo and fill it in
#    (the agent reads it and never writes it):
cp objective.example.yaml ~/objectives/my_task.yaml
```

Then open your agent (Claude Code, Codex CLI, or VS Code Copilot) at this repo root and instruct it with a prompt such as:

```text
Read and follow robot_agentic_training_flow.md with the objective at
~/objectives/my_task.yaml.
```

The loop runs until the objective's exit condition holds — there is no iteration cap and no "good enough" (Invariant 2). To enforce objective immutability at the harness level rather than by instruction, deny writes to the objective path (e.g. a Claude Code `settings.json` permission rule).

### Control-plane CLI (`agentic-robot`)

An optional, installable reference implementation of the loop's **deterministic control-plane operations** — objective validation, evidence hashing, atomic writes, an append-only JSONL event ledger, metric-vector scoring, and recovery/replay. It does **not** run the loop; the LLM controller does. Install and use:

```bash
pip install -e ".[dev]"          # from this repo root

agentic-robot validate obj.yaml  # validate an objective against objective.schema.json + command preflight
agentic-robot init obj.yaml      # scaffold a new objective from objective.example.yaml
agentic-robot status RUN_DIR     # summarize a run's LOOP_LOG.md (read-only)
agentic-robot replay RUN_DIR     # replay-check exported decoded state snapshots (read-only)
agentic-robot report RUN_DIR     # render the JSONL event ledger to stdout
agentic-robot resume RUN_DIR     # describe a run's deterministic resume point (read-only)
```

`objective.schema.json` is the machine-checkable mirror of the prose objective contract (`objective.example.yaml` stays the canonical human schema). The CLI verbs are read-only or scaffolding — the loop's transaction semantics live in the flow spec and `recovery/`.

### External commands the skills drive

Every training/eval command runs in the **external LeRobot repo** (the objective's `workdir`), prefixed `uv run`. The two commands at the core of most rounds, as documented in the skills:

```bash
# Fresh training run (round 0 only, or a deliberate restart) — from continuing-training
uv run lerobot-train \
  --dataset.repo_id=<user/dataset> \
  --policy.type=<act|diffusion|smolvla|pi0|...> \
  --output_dir=<train_dir> \
  --job_name=<name> --steps=<N> --batch_size=<B> \
  --policy.device=cuda --save_freq=<N/4>

# Resume (the normal path on rounds 1+) — --steps MUST exceed the checkpoint's
# total or this trains nothing while exiting 0
uv run lerobot-train \
  --config_path=<train_dir>/checkpoints/last/pretrained_model/train_config.json \
  --resume=true \
  --steps=<strictly greater than before>

# Measurement — the objective's eval_command, run verbatim every round
# (objective.example.yaml's default form; the loop substitutes
#  {checkpoint} -> <train_dir>/checkpoints/last/pretrained_model and
#  {eval_dir} -> <run_dir>/round_<n>/eval_g<m>; the aggregate metric
#  lands at overall.<key> in eval_info.json)
uv run lerobot-eval \
  --policy.path={checkpoint} \
  --env.type=pusht \
  --eval.n_episodes=50 \
  --eval.batch_size=10 \
  --policy.device=cuda \
  --output_dir={eval_dir}
```

### Offline skill tooling commands

Run from `skills/original/skill-creator/` (operator-attended, never during a live round):

```bash
cd skills/skill-creator

# Validate a skill's frontmatter (exit 0 = valid; requires PyYAML)
python3 scripts/quick_validate.py ../measuring-the-gate

# Package a skill into a distributable zip (module form is required —
# the script imports through the scripts package)
python3 -m scripts.package_skill ../tuning-action-horizon
```

## Code examples

The spec and skills are plain markdown; the importable Python is the vendored skill-creator tooling below, plus the `recovery/` replay checkers the flow's recovery protocol calls. From the repo root (verified against the vendored source; `validate_skill` needs PyYAML):

```python
import sys
from pathlib import Path
sys.path.insert(0, "skills/skill-creator")

# Validate a skill directory against the Agent Skills frontmatter rules
from scripts.quick_validate import validate_skill
ok, message = validate_skill("skills/measuring-the-gate")
print(ok, message)  # True Skill is valid!

# Parse a SKILL.md's frontmatter (takes the skill DIRECTORY as a Path)
from scripts.utils import parse_skill_md
name, description, content = parse_skill_md(Path("skills/measuring-the-gate"))
```

A minimal objective (see [`objective.example.yaml`](objective.example.yaml) for the fully commented schema, statistical guidance, and a real-robot reward-model variant):

```yaml
run_dir: outputs/train_loop/pusht_act_001
metric_path: overall.pc_success   # dotted path into eval_info.json
comparison: ">="
target: 80.0
eval_command: |
  uv run lerobot-eval \
    --policy.path={checkpoint} \
    --env.type=pusht \
    --eval.n_episodes=50 \
    --eval.batch_size=10 \
    --policy.device=cuda \
    --output_dir={eval_dir}
stagnation_rounds: 2
```

## Notes

- **Key advantages:**
  - The controller/worker split keeps the main agent's context lean across arbitrarily long runs; workers are stateless, time-boxed, and watchdog-killed on overrun.
  - Progress is *measured, never asserted* (Invariant 3), and judged against a statistically honest bar: an Agresti–Caffo two-sample noise band, confirmation evals, and paired per-episode tests (McNemar / paired bootstrap) when the eval proves deterministic.
  - Rounds are crash-safe by construction: commit-keyed side effects, generation-scoped waits, execution leases, and phase-transition handshakes let a killed session recover without repeating or losing work.
  - The skills library compounds across runs *and* across concurrent loop instances on the same machine (shared live under a `flock` transaction), following the platform-neutral Agent Skills standard.
  - The design is validated: two real SmolVLA-on-LIBERO runs exited at 85.0 and 88.0 `overall.pc_success` from baselines of 53.0 and 46.0 (see `context/repo_info/update_logs.md`, Executions 2–3).
- **Known issues:**
  - 10 of the 18 skills are lifecycle `candidate` — documented but not yet evidenced in a logged round; prefer `validated` skills when several fit.
  - An untracked `SKILL.md` at the repo root (named `train-robot-loop`, after the retired predecessor skill) is a thin Agent-Skills discovery wrapper that redirects to `robot_agentic_training_flow.md`; it is not tracked in git.
  - Historical run logs referenced by older ledger entries and docs (`run_record.md`, `suggestions.md`, `exec_suggestions.md`) are no longer in the working tree.
  - The default execution-lease registry coordinates concurrent runs for a single OS user; multi-user GPU hosts must configure a securely permissioned host-shared coordinator via `ROBOT_TRAINING_LEASE_REGISTRY`.
  - The vendored `skill-creator` body slightly exceeds the library's own 500-line SKILL.md convention (upstream-owned; never edited locally).
- **Future improvements** *(aspirational)*:
  - Promote the candidate skills to `validated` as logged rounds exercise them (flow Step 3h, evidence-driven).
  - Automated hyperparameter search (Optuna/Hyperband) behind the Step 3(d) selection rubric — considered and explicitly deferred.
  - Hardening of the host-shared execution-lease coordinator for multi-user GPU machines.
- **References:**
  - [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md) — the flow itself; [`skills/index.md`](skills/index.md) — the library index and curation rules.
  - [Agent Skills open standard](https://agentskills.io) — the skill format this library follows.
  - [`anthropics/skills`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — upstream source of the vendored `skill-creator` (Apache-2.0).
  - [Hugging Face LeRobot](https://github.com/huggingface/lerobot) — the external repo whose `lerobot-*` CLIs the skills drive.
  - `context/repo_info/` — the pack-maintained codebase/scripts overviews and update logs for this repo.
