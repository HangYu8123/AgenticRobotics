# Codebase Overview — `agentic_training_loop`

*(Regenerated 2026-07-13 by the initialize workflow.)*

> **Drift note (2026-07-13 14:47, exec workflow Execution ID 4):** `README.md` and `README.html` now exist at the repo root (written by the pack's `write-readme` skill; the HTML is a self-contained light/dark rendering regenerable via python-markdown). Also changed since this overview was regenerated, by concurrent work outside that execution: the three run logs (`run_record.md`, `suggestions.md`, `exec_suggestions.md`) are **no longer in the working tree** (mentions below are historical); the root `SKILL.md` is now a 10-line Agent-Skills discovery wrapper redirecting to the flow file (untracked); and `recovery/` (`replay_checker.py`, `round_state.schema.json`) plus `tests/test_recovery.py` were added and are documented below.

> **Drift note (2026-07-18 22:16, Function Update ID 6):** Added a small **deterministic control-plane reference implementation** — package `agentic_robot/` (`objective.py` schema+preflight validation, `scoring.py` metric-vector scoring, `state.py` versioned decoded-state loader with a single migration seam, `ledger.py` crash-safe atomic writes + append-only `events.jsonl` + markdown render, `cli.py` exposing the `agentic-robot` console script with read-only/scaffold verbs `validate|init|status|replay|report|resume`) and the root `objective.schema.json` (JSON-Schema **mirror** of the prose objective contract; `objective.example.yaml` stays canonical). The CLI never runs training/eval and never writes `LOOP_LOG.md`. Project/CI infra added: `pyproject.toml` (console entry point + pinned dev extras; default test discovery runs `tests/`), `.github/workflows/ci.yml` (compile/ruff/mypy/pytest on Py 3.10–3.12; lint+type scoped to `agentic_robot/`), and `.gitignore` narrowed to ignore only `.github/HarnessFlow/` so project-owned `.github/` is tracked. New tests: `test_objective_and_scoring.py`, `test_ledger_crash.py` (crash injection at prepare/write/fsync/rename), `test_cli_integration.py` (fake train/eval), `test_replay_properties.py` (hypothesis idempotence + generation-non-reuse, auto-skipped without hypothesis), `test_schemas_and_skills.py` (schema validity + skill-frontmatter + internal links). Docs added: `LICENSE` (Apache-2.0), `CONTRIBUTING.md`, `SECURITY.md`, `CITATION.cff`, `COMPATIBILITY.md` (LeRobot **v0.6.0** pin + matrix). `objective.example.yaml` gained a commented three-eval-layer + `acceptance:` metric-vector block (smoke=`preflight_eval_command`, selection=`eval_command`, acceptance=new locked holdout; LIBERO-PRO/vla-eval referenced, not integrated); `skills/index.md` gained an *Evidence tiers* section (candidate→reproduced→cross-seed→cross-task→cross-embodiment) with an unattended-selection rule. Note: `skills/` has since been reorganized into `skills/original/` and `skills/iterated/` by concurrent work.

## 1. What this repo is

`agentic_training_loop` is **not a traditional software project** — it has no application or build system. It is an **agent-executable specification for a self-improving robot-VLA (vision-language-action) training loop**: a controller-style train → evaluate → improve cycle that an LLM coding agent (Claude Code, Codex, or VS Code Copilot) runs against an external robot-learning repo (in practice the sibling `lerobot` checkout at `/home/hangyu/umi_vla/lerobot`). A small stdlib-only recovery checker and focused unit suite now make the most critical durable-state transitions executable.

The "code" here is:

- **Markdown protocol files** — `robot_agentic_training_flow.md` is the actual program: a strict, step-numbered control-flow spec with a `[term]` glossary (Definitions), ten Invariants, six gates (incl. a [command preflight] on the objective's command text), and a durable-transaction recovery protocol for crash-safe rounds.
- **Markdown skills** (`skills/*/SKILL.md`) — reusable procedures that worker subagents read and execute, following the [Agent Skills](https://agentskills.io) open standard (one directory per skill, frontmatter `name`/`description`, body < 500 lines).
- A small amount of **Python utility code**: `recovery/replay_checker.py` provides pure decoded-state replay checks and byte-exact partial-append repair; `tests/test_recovery.py` exercises those contracts. The separate `skills/original/skill-creator/scripts/` tree is vendored offline tooling (Apache-2.0, from `anthropics/skills`) for authoring/evaluating skills.

Everything else (the actual `lerobot-train` / `lerobot-eval` commands, datasets, checkpoints, run dirs) lives **outside** this repo, in whatever external repo the flow's objective points at. This repo supplies only the orchestration logic, the parameterization contract, and the accumulating "menu" of known-good procedures.

Three side files record real executions of the spec: `run_record.md`, `suggestions.md`, and `exec_suggestions.md` are logs from actual runs (SmolVLA on PushT and on LIBERO). Per Invariant 6 the flow file is never edited *at runtime*; lessons accumulate in these side files and are folded into the spec in offline revisions (visible in git history — e.g. the 2026-07-12 "time-boxed delegation watchdog + durable round recovery" commit).

The repo also carries its own installed **HarnessFlow orchestration pack** at `.github/HarnessFlow/` — entry points (`CLAUDE.md`/`AGENTS.md`/`copilot-instructions.md`), the workflow-contract/philosophy layer, and generic agent definitions (Executor, Implementer, Focus/Free Analyst, Online Researcher, QA Engineer, Bug Reproducer, Devils Advocate, …) that the flow reuses as its subagent roster. Its internals are standard HarnessFlow scaffolding, documented in the pack's own files rather than here. Because `.github/` is gitignored (an external dev folder, absent on a fresh clone), the specific pack files the flow reads at runtime — `_lib/`, `philosophy/`, `agents/`, `repo_info/`, and the two review skills (`code-simplification`, `code-review-and-quality`) — are **vendored under `context/`** at the repo root, and Pack Path Resolution is **context-first**, so the package runs self-contained without the pack.

**Git status note:** this folder is tracked inside the enclosing `umi_vla` git repo. The spec, objective template, and most skills are committed; the run logs (`run_record.md`, `suggestions.md`, `exec_suggestions.md`) and the newest run-registered skills (`detaching-gpu-jobs`, `installing-libero-headless`, `reverting-to-champion`, `tuning-action-horizon`, `tuning-inference-chunking`) are currently untracked working-tree additions.

## 2. Pipeline / control flow

### The controller loop (`robot_agentic_training_flow.md`)

The flow casts the **main agent as a controller, not a doer**: it spends its limited context only on decisions — binding the objective, choosing each round's action set, parsing the metric itself, scoring, writing the ledger, deciding halts/exit. All token-heavy work (running commands, reading logs/videos, writing scripts, researching, debugging) is delegated to stateless subagents that return a compact result, never a transcript.

**Input: the objective YAML** (template `objective.example.yaml`; operator-owned, immutable — Invariant 1). It parameterizes:

- `run_dir` — where `LOOP_LOG.md` and per-round artifacts accumulate.
- `metric_path` / `comparison` / `target` — the exit condition (dotted path into `eval_info.json`, e.g. `overall.pc_success >= 80.0`).
- `eval_command` — the verbatim measurement command run every round; its only contract is to write `{eval_dir}/eval_info.json` containing `metric_path`. It is validated (never edited) by a command preflight: placeholders `{checkpoint}`/`{eval_dir}` only, first token `uv`/`python`/allow-listed, no `;`/backticks/`$( )`/`&`, no redirection outside the run dir.
- `stagnation_rounds` — non-improving rounds tolerated before the loop must switch strategy class.
- Optional: `min_delta` (replaces the computed noise band; required in practice for deterministic evals whose output lacks per-episode results), `workdir`, `allowed_executables`, `preflight_eval_command` (reduced-cost round-0 probe on the same measurement code path). `objective.example.yaml` is the canonical schema; Step 0 validates the objective against it and runs the command preflight before anything is dispatched.
- A commented **real-robot variant** shows scoring recorded episodes with a reward model instead of a gym env (`skills/original/scoring-with-reward-model/SKILL.md`).

**The loop's five standard parts (plus one flow-specific):**

| Part | Realization here |
|---|---|
| Program (fixed) | `robot_agentic_training_flow.md` — never rewritten at runtime |
| Artifact (improved) | the policy checkpoint (`<train_dir>/checkpoints/last/pretrained_model`) |
| Feedback signal | `eval_command` → `[metric]`, judged by the gates |
| Run ledger | `[run_dir]/LOOP_LOG.md`, append-only, one commit-keyed entry per round |
| Termination | the `[exit condition]` alone — no iteration cap, no "good enough" |
| Skills library (6th part) | `skills/` at the repo root — a menu that grows every round |

**Steps:** Step 0 **Bind** (read objective, sha256 digest it, create run dir + ledger + durable round record) → Step 1 **Baseline** (Executor measures round 0; or trains an initial policy first) → Step 2 **Sanity gate** (objective reachable? degenerate always-zero success signal? already satisfied? metric path resolves?) → Step 3 **Round loop** → Step 4 **Exit** (Devils Advocate independently re-verifies before the exit report is written).

**Round mechanics (Step 3, repeated until the exit condition holds):**

1. **(a) Verify** — re-digest the objective (integrity gate; halt on change).
2. **(b) Read** — re-read `skills/index.md` (it may have grown, including from concurrent sibling loop instances).
3. **(c) Analyze** — a Focus/Free Analyst subagent reads the heavy artifacts and returns a compact round analysis (skippable when the next move is obvious).
4. **(d) Decide** — the controller alone assembles the round's **action set** (one or more skills, and/or new skills). Bundling moves faster but forfeits per-skill attribution.
5. **(e) Execute** — workers per action-set member: Executor (run a skill), Implementer (new script/skill), Online Researcher, QA Engineer/Bug Reproducer (only on `ERROR`). Every delegation is time-boxed (`[time budget]`, watchdog-killed at 2× estimate).
6. **(f) Measure** — Executor runs `eval_command` verbatim into a fresh `eval_g<m>` dir; the controller itself parses `metric_path` from `eval_info.json` (Invariant 3 — a subagent's claimed number is never the metric). A crashed eval is verdict `ERROR` — a statement about the measurement, never the policy; it never touches the stagnation counter.
7. **(g) Score** — noise-aware improvement rule: a direction-aware delta must clear the [noise band] (Agresti–Caffo two-sample 95% half-width; operator `min_delta` replaces it) or survive the confirmation protocol — one confirmation eval with pooled re-test, switching to a paired per-episode test (McNemar exact/χ², or paired bootstrap for non-binary metrics) when the confirmation proves the eval deterministic. Updates `metric_best` / best checkpoint / stagnation counter plus the advisory `best_observed`, via a commit-keyed, idempotent score snapshot; a promotion transactionally regenerates the derived `[run_dir]/CHAMPION` pointer.
8. **(h) Register** — **reusable** procedures and reusable failure lessons are registered into `skills/` (round-time minimal form) — Invariant 5; failed one-offs stay in the ledger. Library writes are a controller-held transaction under `skills/LIBRARY.lock` (flock; re-read index under lock, semantic dup detection, atomic temp+rename index replace) because concurrent loop instances share the library live.
9. **(i) Log** — cleanup is aggregated, then the round entry is rendered from durable state only and appended to `LOOP_LOG.md` under lock with a four-case idempotent append protocol.

**Gates:** integrity check (objective unchanged) → sanity gate (once, Step 2) → improvement rule → stagnation gate (at `stagnation_rounds` non-improving rounds the next action set **must** switch strategy class) → exit condition (the only exit; independently re-verified, with a controller-only remeasurement round on disagreement).

**Durability:** the flow defines a heavyweight crash-recovery protocol — `[run_dir]/ROUND_IN_PROGRESS.md` (atomically replaced, serialized by stable `.lock` sidecars), monotonic **wait generations** and **measurement generations**, and **commit keys** (sha256 of canonical scoring inputs) so scoring, registration, ledger append, and round advance each happen at most once per key. `recovery/round_state.schema.json` now defines the normalized decoded mapping for schema-backed records, while the pure checker validates generation monotonicity/nonreuse, reciprocal measurement/wait ownership, wait movement, the commit-phase chain, clean round initialization, and the byte-anchored partial-ledger-append case. It deliberately does not parse or migrate legacy Markdown/YAML encodings. Each dispatch also has a frozen **execution lease** (run-local recovery snapshot plus a configurable cross-run resource registry), and operation chains use thin **phase-transition edges** derived from verified waits (`TRAIN_COMPLETE → EVAL_LAUNCHED → EVAL_COMPLETE`, generalized to setup/download/preprocess/publish). Wakes are generation-scoped and at-most-once (Invariant 7); recovery completes partially committed phases rather than repeating them (Invariant 8).

### How the side logs fit in

- **`run_record.md`** — narrative log of the LIBERO run (`libero_smolvla_001`): assumptions, dependency installs, errors ERR-1..5 with fixes, a round-by-round timeline ending in a confirmed exit (46.0 → 88.0 `pc_success` in 4 rounds), and structured improvement suggestions for the flow (paired statistics for deterministic evals, inference-time config changes as a first-class strategy class, mandatory controller-side artifact watcher, …).
- **`suggestions.md`** — problems/suggestions from the earlier PushT run: SmolVLA↔PushT embodiment mismatch, `uv run` re-sync breakage in a blocked-network env, torchcodec/pyav, async-env eval flag, resume-vs-fresh and scheduler-decay traps.
- **`exec_suggestions.md`** — flat timestamped bump log (`Where/Symptom/Cause/Fix/Suggestion` per entry): tqdm `\r` defeating line-based monitors, harness reaping background tasks (motivating `detaching-gpu-jobs`), fixed-seed determinism voiding the confirmation-eval mechanism, `--policy.scheduler_decay_steps` no-op on resume.

These are the offline feedback channel by which the operator hardens the flow and skills between runs; the flow file itself is only revised offline (git history confirms this cadence).

## 3. Pipeline diagram

```
 operator                                                external repo (e.g. lerobot)
 ┌────────────────────┐
 │ objective.yaml      │  (filled-in copy of objective.example.yaml)
 │  run_dir            │
 │  metric_path/target │
 │  eval_command       │
 │  stagnation_rounds  │
 └─────────┬───────────┘
           │  Step 0: Bind — read + sha256-digest objective; create run_dir,
           │  LOOP_LOG.md header, ROUND_IN_PROGRESS.md + lock sidecars
           ▼
 ┌──────────────────── robot_agentic_training_flow.md (controller) ────────────────────┐
 │  prereqs: context/_lib/{workflow_contract,safety_rules,stay_active,                  │
 │  approval_gate}.md + context/philosophy/philosophy.instructions.md                   │
 │                                                                                      │
 │  Step 1  Baseline ──▶ Executor runs eval_command (round 0; trains first if needed)   │
 │  Step 2  Sanity gate ─▶ reachable? degenerate signal? already met? metric resolves?  │
 │                                                                                      │
 │  ┌── Step 3  Round loop (until exit condition) ────────────────────────────────┐     │
 │  │ (a) Verify   — re-digest objective (integrity gate)                         │     │
 │  │ (b) Read     — re-read skills/index.md  ◀───────────────┐                   │     │
 │  │ (c) Analyze  — Focus/Free Analyst → [round analysis]    │   skills/         │     │
 │  │ (d) Decide   — controller picks [action set]  ──────────┤   ([skills        │     │
 │  │ (e) Execute  — workers, time-boxed:                     │    library])      │     │
 │  │      Executor → continuing-training, tuning-*,          │                   │     │
 │  │                 curating-dataset, collecting-data, …    │                   │     │
 │  │      Implementer → writing-new-scripts, new SKILL.md    │                   │     │
 │  │      Online Researcher → researching-online             │                   │     │
 │  │      QA Eng / Bug Reproducer → fix crashed eval (ERROR) │                   │     │
 │  │ (f) Measure  — Executor runs eval_command verbatim →    │                   │     │
 │  │                eval_info.json; CONTROLLER parses metric │                   │     │
 │  │ (g) Score    — improvement rule + stagnation gate →     │                   │     │
 │  │                metric_best / best checkpoint (commit-keyed snapshot)        │     │
 │  │ (h) Register — new behaviors → skills/ ─────────────────┘                   │     │
 │  │ (i) Log      — round entry appended to LOOP_LOG.md (idempotent, locked)     │     │
 │  └──────────────────────────────────────────────────────────────────────────────┘     │
 │                                                                                      │
 │  Step 4  Exit — exit condition holds ─▶ Devils Advocate re-verifies independently    │
 │           (disagreement → controller-only remeasurement round) ─▶ exit report        │
 └──────────────────────────────────────────────────────────────────────────────────────┘
           │ writes                                          ▲ reads/writes
           ▼                                                 │
 run_dir/LOOP_LOG.md (append-only ledger)     run_dir/ROUND_IN_PROGRESS.md (+ .lock sidecars)
 run_dir/CHAMPION (derived best-checkpoint pointer, regenerated from durable score_state)
 skills/index.md + skills/<name>/SKILL.md (grows every round; shared across loop instances)

 Offline feedback (never edits the flow at runtime — Invariant 6):
   run_record.md, suggestions.md, exec_suggestions.md
     → offline revisions of robot_agentic_training_flow.md / objective.example.yaml / skills/
```

## 4. Directory structure

```
agentic_training_loop/
├── CLAUDE.md, AGENTS.md, .github/copilot-instructions.md
│     Tool entry points (copies from the pack). Routing here is simplified vs. the
│     parent umi_vla repo: only a filled-in request_template/ prompt runs a workflow;
│     anything else gets a normal answer.
├── robot_agentic_training_flow.md    # the program (see §2)
├── SKILL.md                          # thin Agent Skills discovery wrapper; delegates to flow
├── objective.example.yaml            # operator-facing parameter template
├── robot_agentic_training_flow_request_template.md   # fill-in prompt that launches the flow
├── robot_agentic_training_flow_gui.html              # offline request builder (mirrors the pack's harness_gui.html)
├── recovery/
│   ├── round_state.schema.json       # decoded schema-backed round-state contract
│   └── replay_checker.py             # pure replay and partial-append checks
├── tests/test_recovery.py            # focused stdlib unittest recovery suite
├── run_record.md                     # LIBERO run narrative log (untracked)
├── suggestions.md                    # PushT run problems/suggestions (untracked)
├── exec_suggestions.md               # timestamped bump log (untracked)
├── skills/                           # the flow's OWN [skills library]
│   ├── index.md                      # master index: skill table (purpose/origin/
│   │                                 # lifecycle), verdict→skill routing, new-skill
│   │                                 # template, curation rules
│   ├── continuing-training/          # validated — start/resume training; 3 scheduler traps
│   ├── measuring-the-gate/           # validated — run eval_command verbatim
│   ├── diagnosing-qualitatively/     # validated — watch rollouts/videos for failure modes
│   ├── tuning-action-horizon/        # validated — shrink n_action_steps, zero-cost lever
│   ├── tuning-inference-chunking/    # deprecated — duplicate, merged into the above
│   ├── tuning-hyperparameters/       # candidate — policy type/batch/LR/steps
│   ├── curating-dataset/             # candidate — inspect/clean/augment dataset
│   ├── collecting-data/              # candidate — record more episodes
│   ├── annotating-data/              # candidate — (re-)label episodes
│   ├── researching-online/           # candidate — papers/docs/issues to escape plateaus
│   ├── writing-new-scripts/          # candidate — behaviors the external repo lacks
│   ├── checking-hardware/            # candidate — cameras/ports calibration
│   ├── scoring-with-reward-model/    # candidate — real-robot scoring without a gym env
│   ├── reverting-to-champion/        # candidate — branch back from CHAMPION after regression
│   ├── installing-libero-headless/   # candidate — hf-libero install on a headless box
│   ├── detaching-gpu-jobs/           # candidate — setsid/nohup detach vs. harness reaping
│   ├── preparing-runtime/            # candidate — generic bounded/resumable setup contract
│   └── skill-creator/                # vendored (Apache-2.0, anthropics/skills):
│       ├── SKILL.md, agents/, references/, assets/
│       ├── scripts/*.py              # offline skill eval loop (run_loop, run_eval, …)
│       └── eval-viewer/              # benchmark review HTML generator
├── context/                         # VENDORED runtime deps — self-contained, shipped:
│                                     # _lib/, philosophy/, agents/, repo_info/, and
│                                     # skills/{code-simplification,code-review-and-quality};
│                                     # mirrors of the pack files the flow reads at runtime
└── .github/HarnessFlow/              # dev-only HarnessFlow pack — GITIGNORED, absent on clone
                                      # (workflow/, agents/, _lib/, philosophy/, repo_info/,
                                      # request_template/, pack-internal skills/ ≠ library, GUI)
```

> **Two `skills/` directories exist — never confuse them.** The flow's [skills library] is `skills/` at the repo root. `.github/HarnessFlow/skills/` is HarnessFlow pack tooling (code review, PR breakdown, …).

## 5. Key conventions

- **Detached GPU jobs** (`detaching-gpu-jobs`): long training/eval commands run `setsid nohup … &` with PID tracking, watched by a persistent Monitor (60–120 s) on the expected artifact + `kill -0 $PID`, plus a second time-driven wake — because the harness reaps plain background tasks (~18–25 min observed), even `sleep` timers. Normalize tqdm logs with `tr '\r' '\n'` before grepping; step counts ≥1000 print as "5K"/"12.5K".
- **Champion / revert** (`reverting-to-champion` + `[run_dir]/CHAMPION`): a pointer file (path/metric/round) is rewritten on every promotion. On a **confirmed** regression (beyond the noise band, never a within-noise dip), quarantine step-dirs newer than the champion (lerobot's `save_checkpoint` would silently overwrite them), repoint the `last` symlink, and re-validate by re-running `eval_command`. The current flow spec tracks `[best checkpoint]` in its durable record; the `CHAMPION` file is the skills-library convention layered on top.
- **Gate measurement** (`measuring-the-gate`, Invariant 3): eval command always verbatim from the objective; the controller parses the metric from `eval_info.json` itself. `lerobot-eval` writes aggregates under `overall.<key>` (not `aggregated.`).
- **Fresh vs. resume + scheduler traps** (`continuing-training`): fresh/resume is dictated by the controller's round brief, never the worker's choice. Before every resume, the worker resolves the effective config through LeRobot's own parser, reads training/scheduler state, persists `resume_preflight.json`, predicts LR at the actual early logged step, and aborts on mismatch. Three documented scheduler traps remain: auto-scaling on short runs, horizon clamping, and the resume no-op of `--policy.scheduler_decay_steps` (use top-level `--scheduler.num_decay_steps`).
- **Generic runtime preparation** (`preparing-runtime`): dependency installs, downloads, cache fills, and preprocessing use an explicit interpreter/environment, noninteractive/progress controls, resumable caches, a hard log-byte cap, disk/cache growth and stall checks, and a generation/lease-bound terminal result envelope. Task skills retain installer-specific recipes (for example LIBERO's prompt and CMake workaround).
- **Skill lifecycle** (`skills/index.md`): frontmatter `lifecycle: candidate | validated | deprecated` and `safety: reversible | mutating | irreversible`. Promote on measured evidence only; never delete a failed skill — deprecate it; merge near-duplicates into the earlier one (done once: `tuning-inference-chunking` → `tuning-action-horizon`). New skills use the mandatory ~20-line round-time minimal form; skill-creator's full eval loop is offline/operator-attended only.
- **Stagnation forces a strategy-class switch**: the index's verdict table is advisory except the stagnation gate's on-fail action — at `stagnation_rounds` non-improving rounds, stop tuning and go get new information (diagnose, collect data, research).
- **Real-robot scoring** (`scoring-with-reward-model`): with no gym env, `eval_command` is a script scoring recorded episodes with a reward model (`robometer | topreward | sarm | reward_classifier`) that still writes `eval_info.json` in the same shape — the metric contract is env-agnostic.
- **Cross-instance sharing**: multiple loop instances on one machine share `skills/` live (observed win: a sibling's `n_action_steps` evidence redirected a round); registration must re-read the index immediately before writing and grep for existing behaviors to avoid duplicate skills — concurrent index writes are otherwise unguarded (see known issues).

## 6. Open questions

1. Whether `run_record.md` / `suggestions.md` / `exec_suggestions.md` are perpetual append-only journals or per-run scratch files is not stated; both existing run logs describe themselves as tied to one specific run.
2. Which of the run logs' improvement suggestions have already been folded into the current flow revision is not tracked anywhere explicit; the 2026-07-12 commit message ("time-boxed delegation watchdog + durable round recovery") indicates at least the reliability class (B.7) has landed.
