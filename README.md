# AgenticRobotics — Self-Improving Robot Policy Training

An LLM-agent-driven agentic training loop that autonomously trains, evaluates, and improves robot policies until a measurable target is met. No human-in-the-loop iteration, no manual hyperparameter sweeps — the agent decides what to try, measures the result, and keeps going.

## Intuitions

**Robot learning is bottlenecked by the outer loop, not the inner one.** Training a policy is automated; deciding *what to train next* — which hyperparameters to change, whether to collect more data, when to switch strategy entirely — is still manual labor. AgenticRobotics closes that gap: an LLM controller owns the full decision cycle, from objective to exit condition, with crash recovery and statistical rigor built in.

### The SOTA Discovery Problem (and How We Address It)

Finding and applying state-of-the-art methods is itself a research bottleneck. The landscape in 2026:

- **Papers With Code is dead.** Meta sunset it on July 24-25, 2025 (9,327 benchmark leaderboards, 79,817 paper-to-code links, frozen). Community replacements are only partial.
- **LLMs hallucinate citations.** GPT-4o hallucinates 78-90% of citations on recent literature (OpenScholar, Nature, Feb 2026, DOI 10.1038/s41586-025-10072-4). Only retrieval-grounded systems (OpenScholar, PaperQA2, FutureHouse agents) are reliable.
- **Deep Research products converged** but each has a strength: OpenAI (most comprehensive), Gemini (fastest, best Scholar integration), Perplexity (best citations/recency), Claude (best synthesis).
- **A 2026 academic wave targets SOTA discovery explicitly:** AutoSurvey, SurveyForge, DeepSurvey (survey generation) and AutoSOTA (auto-discovers improved models) — research artifacts, not yet turnkey.

AgenticRobotics integrates an **online researcher subagent** that queries grounded academic search (Semantic Scholar, arXiv) to find relevant techniques mid-loop, so the controller can incorporate new methods without the operator manually tracking the literature. The best 2026 stack for this is a two-layer approach: an agentic discovery engine grounded in academic corpora (FutureHouse Falcon, OpenScholar, PaperQA2) paired with a recency layer (alphaXiv, arXiv monitors). Our researcher skill plugs into this architecture.

## Validated Results

Two real SmolVLA-on-LIBERO runs reached **85.0** and **88.0** `overall.pc_success` from baselines of **53.0** and **46.0** — fully autonomous, no human intervention after the objective was set.

## Key Design Principles

| Principle | How |
|---|---|
| **Controller, not doer** | The main agent spends context only on decisions. All heavy work (training, eval, research) runs in stateless, time-boxed, watchdog-killed subagents. |
| **Measured, never asserted** | Progress is parsed from `eval_info.json` by the controller itself, judged against an Agresti-Caffo noise band with confirmation evals and paired statistical tests (McNemar / paired bootstrap). |
| **Crash-safe by construction** | Commit-keyed side effects, generation-scoped waits, execution leases, and phase-transition handshakes. A killed session recovers without repeating or losing work. |
| **Compounding skills library** | 24 skills (7 validated, 16 candidate, 1 deprecated) following the [Agent Skills](https://agentskills.io) open standard, shared live across concurrent loop instances under `flock` transactions. Spans supervised, inference-time-config, data, and RL levers. |
| **Grounded research, not hallucination** | The online researcher subagent uses retrieval-grounded academic search, avoiding the 78-90% citation hallucination rate of ungrounded LLMs. |

## Pipeline

```text
objective.yaml (operator-owned, immutable)
      |
      v
Step 0  Bind        — validate, preflight, sha256-digest, scaffold run_dir
      v
Step 1  Baseline    — preflight probe, initialize, trained-policy baseline (round 0)
      v
Step 2  Sanity gate — reachable? degenerate? already met?
      v
Step 3  Round loop  — Verify -> Read skills -> Analyze -> Decide actions
      |               -> Execute via workers -> Measure (eval_info.json)
      |               -> Score against noise band -> Register new skills
      |               -> Log round -> Record refine signal ... repeat
      v
Step 4  Exit        — exit condition holds; Devil's Advocate re-verifies
```

Ten invariants govern every round. Most importantly: the objective is external and immutable (1), the exit condition is the only exit (2), and progress is measured by the controller from `eval_info.json`, never asserted by a worker (3).

## Quick Start

The loop is executed by an LLM agent, not a CLI.

```bash
# 1. Copy and fill in an objective (the agent reads it, never writes it)
cp objective.example.yaml ~/objectives/my_task.yaml
```

Then open your agent at this repo root:

```text
Read and follow robot_agentic_training_flow.md with the objective at
~/objectives/my_task.yaml.
```

The loop runs until the objective's exit condition holds — no iteration cap, no "good enough."

### Control-plane CLI (`agentic-robot`)

An optional reference implementation of deterministic control-plane operations — validation, hashing, atomic writes, JSONL event ledger, metric scoring, recovery/replay. It does **not** run the loop.

```bash
pip install -e ".[dev]"

agentic-robot validate obj.yaml   # validate objective
agentic-robot init obj.yaml       # scaffold from template
agentic-robot status RUN_DIR      # summarize run
agentic-robot replay RUN_DIR      # replay-check state snapshots
agentic-robot report RUN_DIR      # render event ledger
agentic-robot resume RUN_DIR      # describe resume point
```

### External Commands

Training and eval run in the external LeRobot repo (the objective's `workdir`), prefixed `uv run`:

```bash
# Training (round 0)
uv run lerobot-train \
  --dataset.repo_id=<user/dataset> \
  --policy.type=<act|diffusion|smolvla|pi0|...> \
  --output_dir=<train_dir> --steps=<N> --batch_size=<B> \
  --policy.device=cuda --save_freq=<N/4>

# Resume (rounds 1+) — --steps MUST exceed the checkpoint's total
uv run lerobot-train \
  --config_path=<train_dir>/checkpoints/last/pretrained_model/train_config.json \
  --resume=true --steps=<strictly greater than before>

# Measurement — the objective's eval_command, run verbatim every round
uv run lerobot-eval \
  --policy.path={checkpoint} --env.type=pusht \
  --eval.n_episodes=50 --eval.batch_size=10 \
  --policy.device=cuda --output_dir={eval_dir}
```

## Components

| Component | Description |
|---|---|
| [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md) | The complete controller loop: definitions, 10 invariants, recovery protocol, Steps 0-4. |
| [`objective.example.yaml`](objective.example.yaml) | Canonical objective schema, validated at Step 0, never edited by the agent. |
| [`skills/index.md`](skills/index.md) | The skills library index and curation rules. |
| [`recovery/`](recovery/) | Replay checkers and round-state schema for crash recovery. |
| [`agentic-robot` CLI](pyproject.toml) | Deterministic control-plane operations. |

## Code Examples

```python
import sys
from pathlib import Path
sys.path.insert(0, "skills/skill-creator")

from scripts.quick_validate import validate_skill
ok, message = validate_skill("skills/measuring-the-gate")
print(ok, message)  # True Skill is valid!

from scripts.utils import parse_skill_md
name, description, content = parse_skill_md(Path("skills/measuring-the-gate"))
```

Minimal objective:

```yaml
run_dir: outputs/train_loop/pusht_act_001
metric_path: overall.pc_success
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

## References

- [`robot_agentic_training_flow.md`](robot_agentic_training_flow.md) — the flow spec
- [`skills/index.md`](skills/index.md) — skill library index
- [Agent Skills open standard](https://agentskills.io) — the skill format
- [Hugging Face LeRobot](https://github.com/huggingface/lerobot) — external training/eval CLIs
- [OpenScholar](https://doi.org/10.1038/s41586-025-10072-4) — retrieval-grounded academic search (Nature, Feb 2026)
- [FutureHouse Falcon](https://www.futurehouse.org/) — benchmarked superhuman on literature search
- [PaperQA2](https://github.com/Future-House/paper-qa) — open-source retrieval-grounded research agent
