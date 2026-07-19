agent type: claude
subagent_model: inherit
subagent_effort: high
simplify: false
code_review: false

Read and follow **robot_agentic_training_flow.md** — the standalone *Robot Agentic Training Flow*, invoked directly by name (not through the pack's request-classification table) — in its entirety, then run its controller loop (Steps 0–4) against the objective below until its exit condition holds.

Hard constraints, in priority order (hardest first) —
1. Read the entire flow file before doing anything else, and follow its Steps 0–4 in order.
2. The [objective] is external and operator-owned (Invariant 1): read it from the `objective path` below and **never invent, edit, "fix", relax, or write it** — I authored that YAML myself. If the path is missing or the objective fails the flow's Step-0 validation or a gate, halt and say so; do not adapt it.
3. Create every subagent per the `subagent_model` header — the default `inherit` keeps subagents on the main agent's model with **no downgrade**; a specific model id overrides it for all subagents. `subagent_effort` sets the subagent reasoning tier per `_lib/workflow_contract.md` §Subagent Launch Contract.
4. Resolve the flow file for your platform (it lives at the repo root): Claude Code / Codex → `robot_agentic_training_flow.md`; VS Code Copilot → `@/robot_agentic_training_flow.md`.

`simplify` / `code_review` are the flow's opt-in post-run review headers — `false` skips (the default), `true` runs Claude Code's native `/simplify` · `/code-review`, `local` runs the pack's vendored `skills/code-simplification` · `skills/code-review-and-quality` (portable to every platform). They run only if a round edited repo source files (new scripts/skills). See `_lib/review_skills.md`.

## Requirements (operator preflight — confirm before running; NOT read by the controller)

The environment the flow's train/eval commands assume is already in place. This is a checklist for you, the operator, and context for the agent — the controller does not parse it, and it is separate from the objective's own `workdir`.

requirements:
  - hardware: <e.g. 1× CUDA GPU (≥24 GB), or "real robot + host machine">
  - runtime: <e.g. LeRobot repo cloned & installed; `uv` available; matching CUDA toolkit>
  - data: <e.g. dataset recorded/downloaded at <root>; teleop device present if collecting>
  - storage / other: <e.g. disk for checkpoints & eval videos; network access for HuggingFace>

## Objective (the only definition of success — flow Invariant 1; I own this file)

objective path: <absolute path to the objective YAML I filled in from `objective.example.yaml`>

- I filled that YAML from the `objective.example.yaml` schema and **saved it myself** at the path above (the request builder's "Download objective.yaml" produces it). The flow reads it from that path and never writes it.
- Schema of the fields inside that file (fill them into the file, not here) — **required:** `run_dir`, `metric_path`, `comparison` (one of `>=` `>` `<=` `<`), `target` (number), `eval_command` (`{checkpoint}`/`{eval_dir}` placeholders; first token `uv`/`python`/an `allowed_executables` entry; no `;`, backticks, `$()`, or background `&`; must write `{eval_dir}/eval_info.json` containing `metric_path`), `stagnation_rounds`. **Optional:** `min_delta`, `preflight_eval_command`, `workdir`, `allowed_executables`.

## Starting state (optional — defaults to none; round 0 creates the train_dir)

starting state: <existing train_dir / checkpoint / dataset notes, or leave blank>
