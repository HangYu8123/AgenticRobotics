# Robot Agentic Training Loop

An agent-executable specification for a self-improving robot-policy training loop: train, evaluate, improve — repeat until an external metric target is met.

**Designed for:** [Claude Code](https://claude.ai/code), [Codex CLI](https://github.com/openai/codex), and [VS Code Copilot](https://code.visualstudio.com/docs/copilot/overview) — LLM coding agents that read [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md) and execute it as a step-numbered control-flow program against an external policy-training backend. [LeRobot](https://github.com/huggingface/lerobot) is the reference and validation backend, **not the only target** — the loop is backend-agnostic (any backend that offers a resumable trainer and an eval command writing `eval_info.json` works; see the flow's *Backend independence* note).

The agent binds an immutable, operator-owned objective (e.g. `overall.pc_success >= 80.0`), then runs rounds of train/tune/diagnose/measure until that exit condition holds. Everything it learns accumulates into a reusable, self-growing [skills library](skills/index.md). The only conventional code is a crash-recovery checker (`recovery/`) and vendored offline skill tooling.

## Highlights

- **Controller/worker architecture.** The main agent spends context only on decisions; all token-heavy work (training, evaluation, log reading, scripting, research) is delegated to stateless, time-boxed subagents that return compact results. Overrunning workers are watchdog-killed.
- **Measured, never asserted.** Progress is parsed from `eval_info.json` by the controller itself (Invariant 3), judged against an Agresti-Caffo two-sample noise band with confirmation evals and paired per-episode tests (McNemar / paired bootstrap) when eval proves deterministic. At exit, an optional operator-defined **acceptance gate** (a locked holdout metric vector, part of the exit condition) plus a **measurement-integrity** monitor guard against evaluator overfitting and worker eval-tampering.
- **Crash-safe by construction.** Commit-keyed side effects, generation-scoped waits, execution leases, and phase-transition handshakes let a killed session recover without repeating or losing work.
- **Compounding skills library.** 24 skills (7 validated, 16 candidate, 1 deprecated) following the [Agent Skills](https://agentskills.io) open standard, shared live across concurrent loop instances on the same machine under a `flock` transaction. The menu spans supervised, inference-time-config, data, and RL levers — including RL fine-tuning to escape the demonstration distribution and autonomous rollout harvesting for self-generated data.
- **Validated results.** Two real SmolVLA-on-LIBERO runs exited at 85.0 and 88.0 `overall.pc_success` from baselines of 53.0 and 46.0 (see `context/repo_info/update_logs.md`, Executions 2-3).

## Quick Start

**The loop is executed by an LLM agent, not a CLI.** A small `agentic-robot` CLI ships alongside for deterministic control-plane operations only (validation, status, replay); see [Control-plane CLI](#control-plane-cli-agentic-robot) below. The one required input is a path to an objective spec:

```bash
# 1. Copy the objective template somewhere OUTSIDE this repo and fill it in
#    (the agent reads it and never writes it):
cp objective.example.yaml ~/objectives/my_task.yaml
```

Then open your agent at this repo root and instruct it:

```text
Read and follow robot_agentic_training_flow.md with the objective at
~/objectives/my_task.yaml.
```

The loop runs until the objective's exit condition holds — no iteration cap, no "good enough" (Invariant 2). To enforce objective immutability at the harness level, deny writes to the objective path (e.g. a Claude Code `settings.json` permission rule).

## Table of Contents

- [Highlights](#highlights)
- [Quick Start](#quick-start)
- [Pipeline Overview](#pipeline-overview)
- [Components](#components)
  - [1. The flow specification](#1-the-flow-specification)
  - [2. The skills library](#2-the-skills-library)
  - [3. Offline skill tooling](#3-offline-skill-tooling)
  - [4. Orchestration pack and entry points](#4-orchestration-pack-and-entry-points)
- [Usage](#usage)
  - [Control-plane CLI (`agentic-robot`)](#control-plane-cli-agentic-robot)
  - [External commands the skills drive](#external-commands-the-skills-drive)
  - [Offline skill tooling commands](#offline-skill-tooling-commands)
- [Code examples](#code-examples)
- [Notes](#notes)

## Pipeline Overview

The flow casts the main agent as a **controller, not a doer**: it spends its context only on decisions — binding the objective, choosing each round's action set, parsing the metric itself, scoring, writing the ledger, deciding halts and exit. All token-heavy work is delegated to stateless, time-boxed subagents.

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
      |               (i) Log the round entry  (j) Record the refine signal
      |                                                  ... repeat until exit
      v
Step 4  Exit        — exit condition holds; a Devils Advocate subagent
                      re-verifies independently before the exit report
```

Ten invariants govern every round — most importantly: the objective is external and immutable (1), the exit condition is the only exit (2), progress is measured from `eval_info.json` by the controller itself, never asserted by a worker (3), and the flow file is never modified at runtime — only the outputs grow (6). Rounds are crash-safe: side effects are commit-keyed, waits are generation-scoped, and dispatches carry execution leases, so a killed session recovers by completing partially committed phases instead of repeating them.

**Run outputs** (all under the objective's `run_dir`, outside this repo): `LOOP_LOG.md` (append-only ledger, one entry per round), `ROUND_IN_PROGRESS.md` (durable round transaction and recovery record), `CHAMPION` (derived best-checkpoint pointer), and per-attempt eval directories `round_<n>/eval_g<m>` (fresh per measurement generation; never reused). Two outputs live in this repo: `skills/` grows with every reusable behavior a run discovers, and `LoopRefineRewards/<run_id>.md` collects one advisory row per round — which advisor the controller actually used, and whether the round moved the metric — read offline to refine the loop program itself.

## Components

### 1. The flow specification

The program, its parameter contract, and the recovery checkers it calls. **Input:** an operator-filled objective YAML. **Output:** run ledger, durable round record, champion pointer, and library growth.

| File | Key functionality | Key input / output | Key parameters |
|---|---|---|---|
| [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md) | The complete controller loop: `[term]` definitions, 10 invariants, a durable round-transaction/recovery protocol, and Steps 0-4 with a per-step dataflow line. | Reads the objective and `skills/index.md`; writes `LOOP_LOG.md`, `ROUND_IN_PROGRESS.md`, `CHAMPION`, `LoopRefineRewards/<run_id>.md`, and new skills. | None of its own — the run is parameterized entirely by the objective (Invariant 1). |
| [`objective.example.yaml`](objective.example.yaml) | Canonical schema for the operator-owned objective, validated at Step 0 and never edited by the agent. | Copied outside the repo and filled in by the operator; read-only bound (sha256-digested) at Step 0. | `run_dir`, `metric_path`, `comparison`, `target`, `eval_command` (with `{checkpoint}`/`{eval_dir}` placeholders), `stagnation_rounds`; optional `min_delta`, `workdir`, `allowed_executables`, `preflight_eval_command`. |
| [`recovery/replay_checker.py`](recovery/replay_checker.py) | Pure structural checkers the flow's recovery protocol calls on schema-backed round records: `check_replay` (cross-snapshot consistency) and `recover_partial_append` (byte-exact repair of a torn ledger block). | Decoded round-record mappings / prepared ledger bytes -> a pass verdict or a halt. | Gates only records carrying `schema_version: 1`; covered by `tests/test_recovery.py`. |
| [`recovery/round_state.schema.json`](recovery/round_state.schema.json) | Machine-readable shape of the decoded round-record logical mapping — it never prescribes, parses, or migrates `ROUND_IN_PROGRESS.md`'s on-disk encoding. | A decoded round-record mapping -> schema validity. | Optional `schema_version: 1` marker on new records. |

### 2. The skills library

The flow's growing menu of known-good procedures, following the [Agent Skills](https://agentskills.io) open standard (one directory per skill, `SKILL.md` with `name`/`description` frontmatter, `lifecycle`/`safety` nested under `metadata:`). **Input:** the controller's round brief. **Output:** executed procedures plus new/updated skill entries registered under a `flock`-serialized library transaction (`skills/LIBRARY.lock`), because concurrent loop instances share the library live.

The [index](skills/index.md) routes by last round's verdict: PROGRESS -> exploit (train more, tune); NO PROGRESS below the stagnation limit -> cheapest levers first; at the limit -> **switch strategy class** (diagnose, collect data, research); REGRESSION -> diagnose, then revert to champion; ERROR -> fix the measurement, never the policy. Lifecycle is `candidate` (documented, not yet evidenced in a logged round) -> `validated` (survived a real round) -> `deprecated` (kept for the record).

**24 skills** (11 under `original/`, 13 under `iterated/`):

| Skill | Key functionality | Key input / output | Key parameters | Lifecycle |
|---|---|---|---|---|
| [`continuing-training`](skills/original/continuing-training/SKILL.md) | Starts a fresh `lerobot-train` run or resumes into the run's persistent `train_dir`, with a mandatory parser-resolved `resume_preflight.json` and an early runtime learning-rate gate on every resume. | Round brief (fresh/resume directive) + dataset id or `checkpoints/last` -> new step checkpoints and a moved `last` symlink. | `--dataset.repo_id`, `--policy.type`, `--output_dir`, `--resume=true`, `--steps` (must exceed the checkpoint's total), top-level `--scheduler.num_decay_steps` for clamped resumes. | validated |
| [`measuring-the-gate`](skills/original/measuring-the-gate/SKILL.md) | Runs the objective's `eval_command` verbatim — the mandatory feedback signal, never a hand-rolled variant. | `{checkpoint}` -> `{eval_dir}/eval_info.json` containing the objective's `metric_path`, parsed by the controller itself. | None of its own — note the stock `lerobot-eval` aggregate lives at `overall.<key>`, not `aggregated.<key>`. | validated |
| [`curating-dataset`](skills/original/curating-dataset/SKILL.md) | Inspects, cleans, augments, or restricts training to the evaluated suite. | Dataset repo -> an edited/visualized dataset, or a non-destructive suite-filtered training lineage. | `lerobot-edit-dataset`; `lerobot-dataset-viz`; quoted `--dataset.episodes=[...]` on `continuing-training`. | validated |
| [`diagnosing-qualitatively`](skills/original/diagnosing-qualitatively/SKILL.md) | Watches rollouts, replays, and eval videos to see *how* the policy fails — produces a finding, not a metric change. | Eval videos / checkpoint -> a failure-mode diagnosis steering the next round. | `lerobot-rollout`, `lerobot-replay`, `<eval_dir>/videos/`. | validated |
| [`tuning-action-horizon`](skills/iterated/tuning-action-horizon/SKILL.md) | Shrinks a chunked VLA checkpoint's inference horizon for closed-loop control — a zero-cost config edit, no retraining. | Checkpoint `config.json` -> a re-evaluated checkpoint (two exit-clearing wins on LIBERO: 64->85 and 52->88). | `n_action_steps` (e.g. 50->10, must stay <= `chunk_size`; ~5x more policy calls at horizon 10). | validated |
| [`rebalancing-stage-2`](skills/iterated/rebalancing-stage-2/SKILL.md) | Clones each multi-stage demo from its first "place" event onward to give the post-place state extra training weight, for policies that complete sub-goal 1 but fail to start sub-goal 2. | Multi-stage dataset -> rebalanced dataset with duplicated stage-2 segments. | Dataset manipulation via LeRobot dataset tools. | validated |
| [`skill-creator`](skills/original/skill-creator/SKILL.md) | Vendored Anthropic tooling for authoring and evaluating skills themselves — offline/operator-attended only, never mid-round. | A skill idea or draft -> a validated, packaged, optionally benchmark-optimized skill. | See [offline tooling](#3-offline-skill-tooling) below. | validated |
| [`collecting-data`](skills/original/collecting-data/SKILL.md) | Records additional teleoperated episodes when states are absent from the data — a strategy-class switch. | Robot hardware + existing dataset -> K appended episodes, checked via `meta/info.json`. | `lerobot-record --resume=true --dataset.num_episodes=<K>`. | candidate |
| [`annotating-data`](skills/original/annotating-data/SKILL.md) | Annotates or re-labels dataset episodes with `lerobot-annotate` for multi-stage or language-conditioned tasks when reward/success labels are suspected wrong or missing. | Dataset with suspect labels -> re-annotated dataset. | `lerobot-annotate`. | candidate |
| [`researching-online`](skills/original/researching-online/SKILL.md) | Searches papers, docs, and issues to escape a plateau, returning a testable hypothesis with cited URLs. | A stagnation verdict -> a hypothesis for the next action set. | Web search/fetch tools via the Online Researcher agent. | candidate |
| [`writing-new-scripts`](skills/original/writing-new-scripts/SKILL.md) | Writes a script for behavior the external repo lacks (augmentation, curriculum, custom eval). | A confirmed capability gap -> a script under the run dir (registered here only if reusable). | — | candidate |
| [`checking-hardware`](skills/original/checking-hardware/SKILL.md) | Calibrates and checks cameras/ports when real-robot performance degrades with no software change. | Physical rig -> calibration state re-verified with a reference move. | `lerobot-calibrate`, `lerobot-find-cameras`, `lerobot-find-port`. | candidate |
| [`scoring-with-reward-model`](skills/original/scoring-with-reward-model/SKILL.md) | Scores recorded real-robot episodes with a reward model when no gym env (and no `lerobot-eval`) exists. | Recorded episodes -> `eval_info.json` in the standard contract shape. | Reward model choice: `robometer` \| `topreward` \| `sarm` \| `reward_classifier` (from LeRobot `src/lerobot/rewards/`). | candidate |
| [`reverting-to-champion`](skills/iterated/reverting-to-champion/SKILL.md) | Branches training back from the champion checkpoint after a **confirmed** regression (beyond the noise band). | Champion from the run's durable `score_state` -> repointed `checkpoints/last`, quarantined newer step dirs, reproduction re-validated by eval. | Resume `--steps` must exceed the champion's step count. | candidate |
| [`preparing-runtime`](skills/iterated/preparing-runtime/SKILL.md) | Generic contract for installs/downloads/preprocessing: noninteractive, resumable, bounded-output, with durable exit evidence. | A slow/noisy setup step -> a completed, evidence-backed runtime preparation. | Explicit interpreter/env, progress-off controls, hard log cap, disk/cache growth checks. | candidate |
| [`installing-libero-headless`](skills/iterated/installing-libero-headless/SKILL.md) | Installs LeRobot's LIBERO sim env (`hf-libero`) into the repo venv on a headless box. | A venv where `import libero` fails -> a working EGL-rendering LIBERO install. | `CMAKE_POLICY_VERSION_MINIMUM=3.5`, `egl_probe==1.0.2` pin, `MUJOCO_GL=egl`. | candidate |
| [`correcting-subtask-stalls`](skills/iterated/correcting-subtask-stalls/SKILL.md) | Test-time interventions for the completed-first-stage-then-stalls sequencing failure, used when qualitative diagnosis shows stalls dominating and stage-2 rebalance is already exploited. | Qualitative diagnosis of sequencing failure -> test-time corrective interventions. | — | candidate |
| [`detaching-gpu-jobs`](skills/iterated/detaching-gpu-jobs/SKILL.md) | Dispatches multi-hour GPU jobs detached from harness task management (exit sentinel, artifact watch, scheduled wake) so they survive task reaping. | A long-running GPU command -> a detached job with monitoring. | Exit sentinel path, artifact watch, scheduled wake interval. | candidate |
| [`evicting-hf-dataset-caches`](skills/iterated/evicting-hf-dataset-caches/SKILL.md) | Frees disk by deleting regenerable HuggingFace dataset builder caches that no live process holds, before touching source data. | Disk pressure -> freed cache space. | — | candidate |
| [`rebasing-on-a-stronger-checkpoint`](skills/iterated/rebasing-on-a-stronger-checkpoint/SKILL.md) | Evaluates a published checkpoint of the same policy class under the objective's own gate and adopts it as the training lineage's base if it beats the champion. | Published checkpoint -> evaluated candidate, adopted if it beats the current champion. | Checkpoint source, policy class match. | candidate |
| [`souping-task-vectors`](skills/iterated/souping-task-vectors/SKILL.md) | Interpolates a regressed-but-informative fine-tune back toward the champion to keep its task gains while canceling its forgetting. | Regressed checkpoint + champion -> interpolated checkpoint. | Interpolation weight. | candidate |
| [`unfreezing-the-vlm`](skills/iterated/unfreezing-the-vlm/SKILL.md) | Makes a VLA's frozen vision-language backbone trainable instead of training only the action expert, reserved for genuine perception/grounding deficits (measured not to help sequencing failures). | Frozen VLA -> unfrozen training config. | Backbone layer selection. | deprecated |
| [`harvesting-rollouts`](skills/iterated/harvesting-rollouts/SKILL.md) | Autonomously rolls out the current policy to self-generate new trajectories and log their env rewards into the dataset (data flywheel); records + flags for labeling when no env reward exists. | Checkpoint + env -> appended dataset episodes with rewards/labels. | `lerobot-rollout --strategy.type=sentry`; reward feature per LeRobotDataset schema. | candidate |
| [`reinforcing-with-rl`](skills/iterated/reinforcing-with-rl/SKILL.md) | RL-fine-tunes the policy against an env reward to improve beyond the demonstration distribution (new-behavior discovery) when supervised/config levers have stalled. | Checkpoint + reward/env -> RL-fine-tuned checkpoint lineage. | LeRobot `.[hilserl]` learner/actor; or SimpleVLA-RL / RLinf-VLA / RIPT-VLA (sim GRPO/PPO). | candidate |

### 3. Offline skill tooling

Vendored from [`anthropics/skills`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) (Apache-2.0) with a local preamble; strictly offline — a live round may use its writing conventions but never its eval loop. **Input:** a skill directory. **Output:** validation verdicts, `.skill` packages, benchmark reports.

| Script | Key functionality | Key input / output | Key parameters |
|---|---|---|---|
| `scripts/quick_validate.py` | Validates a `SKILL.md`'s frontmatter against the Agent Skills allowlist (name/description limits, allowed keys). | Skill directory -> exit 0/1 plus a message. | One positional arg: the skill directory (requires PyYAML). |
| `scripts/package_skill.py` | Validates and zips a skill directory into a distributable `<name>.skill` archive. | Skill directory -> `<name>.skill` zip. | Positional `skill-folder [output-directory]`; run as `python3 -m scripts.package_skill`. |
| `scripts/run_eval.py` | Trigger-testing: measures whether queries actually activate a skill by stream-parsing `claude -p` runs. | Eval queries + skill -> per-query trigger rates. | `runs_per_query`, threshold; requires the `claude` CLI. |
| `scripts/run_loop.py` | Orchestrates the description-optimization loop (eval -> improve description -> re-eval) with a live HTML report. | A skill + eval set -> best-scoring description and `results.json`/`report.html`. | `--model` (required), `--report auto\|none\|path`, `--results-dir`. |
| `scripts/improve_description.py` | Proposes an improved skill description from failed/false-trigger queries via `claude -p`. | Failure lists + skill content -> a new `<new_description>` candidate. | `--model`, `--eval-results`, `--skill-path` (all required); requires the `claude` CLI. |
| `scripts/aggregate_benchmark.py` | Aggregates with-skill vs. without-skill grading runs into comparison stats. | `eval-N/*/run-N/grading.json` trees -> `benchmark.json` + `benchmark.md`. | Benchmark dir, skill name/path. |
| `scripts/generate_report.py` | Renders an optimization-run history as a standalone HTML report. | History JSON -> HTML (stdin/stdout supported). | Positional `input` (`-` for stdin), `-o/--output` (default stdout), `--skill-name`. |
| `scripts/utils.py` | Parses `SKILL.md` YAML frontmatter without PyYAML. | Skill directory `Path` -> `(name, description, content)`. | — |
| `eval-viewer/generate_review.py` | Serves (or statically generates) a human review page for benchmark run outputs. | A workspace of run outputs -> a browsable review page with feedback capture. | `workspace`, `--port` (default 3117), `--static` for headless use. |

### 4. Orchestration pack and entry points

Tool-facing scaffolding around the flow; not part of the loop itself. **Input:** a filled-in request-template prompt. **Output:** a routed pack workflow.

| File / Directory | Key functionality | Key input / output | Key parameters |
|---|---|---|---|
| `CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md` | Per-tool entry points that route filled-in `request_template/` prompts to pack workflows (anything else gets a normal answer). | A templated request -> a classified, mode-selected workflow run. | `mode: fast\|general\|skill`, `simplify`/`code_review` headers. |
| `.github/HarnessFlow/` | The installed HarnessFlow orchestration pack: workflow contract, safety/stay-active rules, agent roster, and the repo's `repo_info/` context docs. | Workflow/agent definitions consumed by the orchestrating agent. | — (its internal `skills/` directory is pack tooling — **not** this repo's skills library). |

## Usage

### Control-plane CLI (`agentic-robot`)

An optional, installable reference implementation of the loop's **deterministic control-plane operations** — objective validation, evidence hashing, atomic writes, an append-only JSONL event ledger, metric-vector scoring, and recovery/replay. It does **not** run the loop; the LLM controller does.

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

Every training/eval command runs in the **external LeRobot repo** (the objective's `workdir`), prefixed `uv run`. The two commands at the core of most rounds:

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
# (the loop substitutes {checkpoint} and {eval_dir}; the aggregate metric
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

- **Known issues:**
  - 16 of the 24 skills are lifecycle `candidate` — documented but not yet evidenced in a logged round; prefer `validated` skills when several fit.
  - A `SKILL.md` at the repo root (named `train-robot-loop`, after the retired predecessor skill) is a thin Agent-Skills discovery wrapper that redirects to `robot_agentic_training_flow.md`.
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
