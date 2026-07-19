# Scripts Overview — `agentic_training_loop`

*(Regenerated 2026-07-13 by the initialize workflow.)*

> **Drift note (2026-07-13 14:47, Execution ID 4):** `README.md` (write-readme skill output: goal → pipeline → component tables → verified commands → code examples → Notes) and `README.html` (self-contained rendering) now exist at the repo root. Concurrent changes outside that execution: the three run logs under *Root documents* are no longer in the working tree. The root discovery wrapper and recovery checker added in the same working tree are documented below.

> **Drift note (2026-07-18 22:16, Function Update ID 6):** New Python package **`agentic_robot/`** — the deterministic control-plane reference implementation, installed as the `agentic-robot` console script (`pyproject.toml` `[project.scripts]`). Modules: `objective.py` (`load_objective`, `validate_objective`, `command_preflight`, `objective_digest` — validates against `objective.schema.json` + the [command preflight]); `scoring.py` (`parse_metric`, `compare`, `acceptance_report`/`acceptance_passed` for the metric vector); `state.py` (`load_snapshots`, `migrate` — versioned decoded-state loader, single migration seam); `ledger.py` (`atomic_write` prepare→write→fsync→rename, `append_event`/`read_events` on `events.jsonl`, `render_events_markdown` — never writes `LOOP_LOG.md`; a `crash_hook` boundary lets tests inject crashes); `cli.py` (`main`/`build_parser` — verbs `validate|init|status|replay|report|resume`, all read-only or scaffolding, none execute commands). Root **`objective.schema.json`** is the machine-checkable Draft-2020-12 mirror (`additionalProperties: true`) of the prose objective contract, with optional `acceptance` metric-vector and `acceptance_eval` holdout blocks. Infra: `pyproject.toml` (deps PyYAML+jsonschema; dev extras pytest/hypothesis/ruff/mypy; pytest `testpaths=["tests"]`), `.github/workflows/ci.yml` (compile/ruff/mypy/pytest matrix Py 3.10–3.12), `recovery/__init__.py` (package marker), and root docs `LICENSE`/`CONTRIBUTING.md`/`SECURITY.md`/`CITATION.cff`/`COMPATIBILITY.md`. New tests under `tests/`: `test_objective_and_scoring.py`, `test_ledger_crash.py`, `test_cli_integration.py`, `test_replay_properties.py`, `test_schemas_and_skills.py` — all pass with `python3 -m pytest -q` (42 total incl. the pre-existing recovery suite).

> **Drift note (2026-07-19 16:31, Function Update ID 8):** Skills library now **26 skills**. Added `conditioning-on-advantage` (candidate/mutating — RECAP-style advantage-conditioned RL for **flow-matching** policies; trains with the stock flow-matching loss plus a binarized "Advantage: positive/negative" text token from a separately-fit distributional value model, serves the positive bucket at inference; arXiv 2511.14759, paper-only, no reference implementation) and `synthesizing-skills-from-rollouts` (candidate/reversible — read-only cross-round ledger mining, ≥5 rounds, max 3 proposals per invocation, registers nothing). `reinforcing-with-rl` now carries a policy-class-keyed recipe table (SimpleVLA-RL / RIPT-VLA / RLinf-VLA / piRL / VLA-RFT / ConRFT / HIL-SERL) with an explicit note that only the LeRobot-native row is Executor work and every external row is Implementer work via `writing-new-scripts`/`preparing-runtime`. `researching-online` gained sweep mode. `continuing-training`, `curating-dataset`, `tuning-action-horizon`, and `measuring-the-gate` were restructured into backend-independent contract + reference-backend layers with all verbatim commands and traps preserved; `measuring-the-gate` also gained a cited caution that LIBERO is one of the weaker benchmarks on statistical-significance grounds (arXiv 2606.04233). The *Skills table* below remains stale (~17 rows); `skills/index.md` is authoritative.

> **Drift note (2026-07-19 15:28, Function Update ID 7):** Skills library now **24 skills**. Added `reinforcing-with-rl` (candidate/mutating — RL fine-tune vs. an env reward to escape the demo distribution; drives LeRobot `.[hilserl]` learner/actor or SimpleVLA-RL/RLinf-VLA/RIPT-VLA) and `harvesting-rollouts` (candidate/mutating — autonomous rollout data + reward logging via `lerobot-rollout --strategy.type=sentry`; no-reward → record + label). `robot_agentic_training_flow.md` added a held-out **[acceptance gate]** (part of the [exit condition], resolved only at Step 4; durable `acceptance_result` field + exit-report line; `exit_status: ACCEPTANCE_FAILED` outcome), a **[measurement integrity]** gate (eval-script sha256 pin + worker-tampering scan → `ERROR`), and backend-agnostic framing. The *Skills table* below predates these and several earlier skills (it lists ~17); `skills/index.md` is the authoritative 24-skill list.

Scope: every file in the repo except `.git/` and the installed `.github/HarnessFlow/` pack internals (HarnessFlow tooling, documented in the pack itself). The repo's main content is markdown/YAML specification an agent reads and follows; training/evaluation commands run in a separate LeRobot repository. The repo also contains the stdlib-only recovery checker/test suite and the vendored `skills/original/skill-creator/` offline tooling. Because `.github/` is an external, gitignored folder (absent on a fresh clone), the pack files the flow reads at runtime are **vendored under `context/`** (`_lib/`, `philosophy/`, `agents/`, `repo_info/`, and the two review skills), and Pack Path Resolution is context-first — the package is self-contained without the pack.

---

## Root documents

### `SKILL.md`
**Purpose:** a deliberately thin Agent Skills discovery entry point. It contains no independent loop protocol and delegates exclusively to `robot_agentic_training_flow.md`, preventing the stale wrapper and authoritative flow from diverging.

### `robot_agentic_training_flow.md`
**Purpose:** the flow's single source of truth — a controller-style train→evaluate→improve loop for a robot policy in an external LeRobot repo: a context-lean main agent binds an immutable external objective, then each round spawns subagents to analyze, execute skills, create new skills, debug, and research, while the main agent alone decides the action set, parses the metric, scores, logs the ledger, and exits only when the external exit condition holds.

**Structure:** frontmatter → controller framing → `[inputs]`/`[state]`/`[gates]`/`[outputs]` definition tables (every concept is a bracketed `[term]`) → 10 Invariants → Protocol: a durable round-transaction/recovery section, then Steps 0 (Bind: schema validation against objective.example.yaml + command preflight) → 1 (Baseline — three phases: 1a preflight probe / 1b initialize / 1c trained-policy baseline) → 2 (Sanity gate) → 3 (Round loop, substeps a–j: Verify/Read/Analyze/Decide/Execute/Measure/Score/Register/Log/Record) → 4 (Exit, Devils-Advocate-verified with an exit-revalidation branch) → the `LOOP_LOG.md` ledger schema (header + commit-key-marked round entry template). Dispatch state now includes frozen execution leases and verified phase-transition edges layered on the existing wait generations.

**Reads/writes:** read (never edited — Invariant 6) by the controller and every subagent. At runtime it writes `[run_dir]/LOOP_LOG.md`, `[run_dir]/ROUND_IN_PROGRESS.md` (+ stable `.lock` sidecars), and reads/writes `skills/index.md` + `skills/<name>/SKILL.md` (the repo-root [skills library] — explicitly distinct from the pack's `.github/HarnessFlow/skills/`). Step 3(j) additionally appends one advisory row per round to the repo-root `LoopRefineRewards/<run_id>.md` — the second in-repo growing artifact, write-only and never read back into loop state.

### `recovery/round_state.schema.json`
**Purpose:** Draft 2020-12 structural schema for normalized, already-decoded schema-version-1 round state. It types the canonical core fields, known phases, wait/measurement maps, committed cleanup, and prepared ledger block while allowing forward-compatible additional evidence. It does not define or migrate the on-disk Markdown/YAML encoding used by legacy records.

### `recovery/replay_checker.py`
**Purpose:** pure, dependency-free consistency checks. `check_replay(states)` validates decoded snapshots and transitions: phase sequencing, round initialization, monotonic generation high-water marks/nonreuse, reciprocal measurement/wait ownership, immutable wait identity, and interrupted active-to-completed movement. `recover_partial_append(ledger, prepared)` verifies byte offsets and sha256 digests, accepts an exact complete block idempotently, and repairs only an anchored nonempty strict final prefix (case 3 of the flow's four-case ledger protocol). It performs no file I/O, parsing, or migration.

### `tests/test_recovery.py`
**Purpose:** focused stdlib `unittest` coverage for the full `READY_TO_SCORE` → `ROUND_ADVANCED` chain, valid and stale round initialization, generation/binding failures, interrupted waits, every nonempty byte cut of a UTF-8 prepared ledger block, schema/checker agreement, and thin-wrapper conformance. Run from this repo with `python -m unittest discover -s tests -v`.

### `objective.example.yaml`
**Purpose:** template for the external, operator-owned objective spec bound at Step 0. The agent reads it and never writes it; its metric + exit condition are the sole definition of success.

**Schema:** `run_dir` (pinned output dir); `metric_path` (dotted path into `eval_info.json`, e.g. `overall.pc_success` — note `lerobot-eval` writes `overall.<key>`, not `aggregated.<key>`); `comparison` (`>=` `>` `<=` `<`; the latter two mean lower-is-better); `target`; `eval_command` (multi-line verbatim block templated with `{checkpoint}`/`{eval_dir}`; contract: must write `{eval_dir}/eval_info.json`; validated by the command preflight — first token `uv`/`python`/allow-listed, no `;`/backticks/`$( )`/`&`, no redirection outside the run dir); `stagnation_rounds`; optional `min_delta` (replaces the noise band; steer deterministic no-per-episode evals here), `workdir`, `allowed_executables`, `preflight_eval_command` (reduced-cost round-0 probe, same measurement code path). This file is the canonical objective schema Step 0 validates against. Comments carry statistical guidance (Wilson-interval noise at n=50, fixed-seed paired-comparison advice) and a commented real-robot variant using a reward-model scorer instead of `lerobot-eval`.

**Reads/writes:** read-only by the controller at Step 0 (sha256-digested for the [integrity check]). Real runs use an operator copy outside the repo (e.g. `/home/hangyu/umi_vla/objectives/*.yaml`).

### `robot_agentic_training_flow_request_template.md`
**Purpose:** a fill-in prompt that launches the standalone flow (invoked directly by name — not a pack request-classification category, so it deliberately has no `mode:` and is not swept by the pack's `sync_gui_templates.py`). Header block (`agent type`, `subagent_model`, `subagent_effort`, `simplify`, `code_review`) + a "read and follow `robot_agentic_training_flow.md`" imperative + hard constraints, then three operator sections: **Requirements** (a preflight checklist the controller does NOT parse — hardware/runtime/data/storage), **Objective** (carries only the `objective path` plus the field schema of `objective.example.yaml`; per Invariant 1 the objective's *values* are never inlined into the prompt — the operator authors and saves that YAML themselves), and optional **Starting state**. Copy-paste fallback for the GUI below.

### `robot_agentic_training_flow_gui.html`
**Purpose:** a self-contained, dependency-free static "request builder" for the flow, mirroring the design of the pack's `.github/HarnessFlow/harness_gui.html` (same CSS-variable light/dark theme, segmented radio controls, live preview, copy/download helpers) but single-template. Left panel sets the flow headers; right panel takes typed Requirements + Objective fields (comparison dropdown, numeric target/stagnation, `eval_command`/`preflight_eval_command` textareas prefilled with `objective.example.yaml`'s PushT/ACT example, optional fields). Emits two live previews with copy/download: the request **prompt** (carries only the objective *path* — Invariant-1-safe) and a generated **`objective.yaml`** the operator saves and then references by path. YAML is hand-generated offline (`yamlScalar` single-quote-doubling; `yamlBlock` literal-`|` with a uniform 2-space indent that is valid regardless of user indentation; `yamlNum` emits YAML-numeric forms incl. normalized exponentials). Pure client-side; opens via `file://`, writes nothing on disk.

### `run_record.md` *(untracked)*
Historical record of one real execution (SmolVLA on LIBERO, `libero_smolvla_001`): autonomous-mode assumptions, scout findings, dependency installs, errors ERR-1..5 with fixes, a round-by-round timeline (baseline 46.0 → confirmed exit 88.0 `overall.pc_success` in 4 rounds), and closing improvement suggestions for the flow — (A) round flexibility, (B) reliability, (C) keep-as-is. Written by the agent that ran it (per Invariant 6, suggestions live here, never in the flow file); read by humans/future revisions, not consumed programmatically.

### `suggestions.md` *(untracked)*
Problem/suggestion report from an earlier PushT run of the predecessor `train-robot-loop` skill (which mutated/was deleted mid-run — recorded as finding A2). Structure: TL;DR validated train/eval commands → A skill/spec problems (A1–A5) → B SmolVLA↔PushT compatibility (B1–B3: embodiment feature mismatch, dead language conditioning at eval, target above demonstrated ceiling) → C environment blockers table (C1–C7) → D loop-mechanics traps (resume-vs-fresh, scheduler-decay stall, exit-code hygiene) → E what worked → F recommended next actions. Lessons-learned artifact, not consumed programmatically.

### `exec_suggestions.md` *(untracked)*
Running errors-and-bumps log for the LIBERO ≥70 exec-workflow run. Fixed entry format `Where/Symptom/Cause/Fix/Suggestion`, appended newest-at-bottom. Entries: mid-session flow-spec drift; `uv pip` targeting the wrong interpreter; `egl-probe` build failure under cmake≥4; tqdm `\r` defeating line-based monitors; harness reaping background Bash tasks (even `sleep` timers); an eval task killed externally mid-run; fixed-seed determinism voiding the confirmation-eval mechanism; `n_action_steps` as the highest-leverage zero-cost knob; `--policy.scheduler_decay_steps` silently ignored on resume; LIBERO's interactive first-import prompt. Several findings are reflected as `Watch out`/`Evidence` content in the skills below.

---

## `skills/` — the flow's [skills library]

### `skills/index.md`
The library index — "a menu, not a fence." Declares the Agent Skills conventions (dir per skill, `SKILL.md` frontmatter `name`==dirname + `description`, `lifecycle`/`safety` nested under `metadata:` — the validator allowlist has no top-level slots for them, body <500 lines). Provides: a **verdict→skill routing table** (PROGRESS→exploit; NO PROGRESS below stagnation→cheapest levers first; at stagnation→must switch strategy class; REGRESSION→diagnose then revert; ERROR→fix the measurement, never the policy); the **skills table** (purpose/origin/lifecycle for all 17 skills); **Creating a new skill** — the mandatory round-time minimal form (~20-line SKILL.md: Prerequisites/Do/Mutates/Validation/Rollback/Watch out/Evidence + one index row; skill-creator's full eval loop is forbidden mid-round); and **Curating the library** (promote on evidence, never delete — deprecate, merge near-duplicates). Read by the controller at Step 0.5 and every Step 3b; written at Step 3h under the library transaction: controller-held `flock` on the stable `skills/LIBRARY.lock`, re-read + semantic dup detection under the lock, atomic temp+rename index replace (concurrent loop instances share the library live).

### Skills table

| Skill | Trigger / when-to-use | What it does | Depends on | Lifecycle |
|---|---|---|---|---|
| **continuing-training** | Default exploit after PROGRESS; round-0 fresh training; any round adding steps. | Fresh: `lerobot-train --dataset.repo_id=… --policy.type=… --output_dir=<train_dir>`. Resume: resolve saved config plus exact overrides with LeRobot's parser, read checkpoint optimizer/scheduler state, persist `resume_preflight.json`, then run `--resume=true --steps=<strictly greater>` and numerically gate the first logged LR at that log's actual step. | `lerobot-train` CLI | **validated** — documents auto-scaling, horizon clamp, and the resume no-op of `--policy.scheduler_decay_steps` (use top-level `--scheduler.num_decay_steps`). |
| **measuring-the-gate** | Every round, Step 3f + Step 1 baseline — mandatory feedback signal, never a hand-rolled variant. | Runs the objective's `eval_command` verbatim; contract is writing `{eval_dir}/eval_info.json`; worker reports exit status + path, controller parses the number (Invariant 3). | `lerobot-eval` or any contract-satisfying command | **validated** (by construction) |
| **diagnosing-qualitatively** | Metric regressed/flat and nobody can say why. Produces a *finding*, not a metric change (delta 0 by construction). | `lerobot-rollout`, `lerobot-replay`, reading `<eval_dir>/videos/`. | `lerobot-rollout`/`lerobot-replay` CLIs | **validated** — round-3 evidence: found the no-retry open-loop failure mode that redirected the run to `tuning-action-horizon`. |
| **tuning-action-horizon** | Chunked-action policy (`chunk_size >> 1`) underperforms and training is expensive. | Edit `<checkpoint>/pretrained_model/config.json` `n_action_steps` (e.g. 50→10, ≤ chunk_size; weights untouched), re-run `eval_command` verbatim. | checkpoint config only | **validated** — two independent wins: 64.0→85.0 and 52.0→88.0 on LIBERO, both exit-clearing. ~5× more policy calls at horizon 10. |
| **tuning-inference-chunking** | — deprecated. | Duplicate of `tuning-action-horizon` (registered concurrently by two loop instances; merged per curation rule). Kept so old ledgers resolve. | successor skill | **deprecated** |
| **tuning-hyperparameters** | Training converged but short of target, or wrong policy class for the task. | Re-parameterizes `continuing-training` (`--policy.type`/batch/LR/steps); a policy-type switch means a fresh `<train_dir>` lineage. | `continuing-training`; LeRobot `AGENT_GUIDE.md` §6–7 | candidate |
| **curating-dataset** | Suspect the data, not the model — cheaper than training. | `lerobot-dataset-viz` (view), `lerobot-edit-dataset --operation.type=delete_episodes\|split\|merge\|remove_feature\|modify_tasks\|convert_image_to_video`, `augment_dataset_quantile_stats.py`. Trap: `lerobot-info` silently ignores `--repo-id`. | `lerobot-dataset-viz`/`lerobot-edit-dataset` | candidate |
| **collecting-data** | Underfit / states absent from data / small dataset — a strategy-class switch. | `lerobot-record --resume=true --dataset.num_episodes=<K>` appends K teleop episodes; validate via `meta/info.json`. | `lerobot-record`; robot hardware | candidate |
| **annotating-data** | Multi-stage or language-conditioned task; wrong reward/success labels. | `lerobot-annotate`; snapshot labels first; spot-check against video (mutation is irreversible). | `lerobot-annotate` | candidate |
| **researching-online** | Stagnation gate fired — the canonical plateau escape. | Web/paper/GitHub/HF search via the Online Researcher agent; cites every URL; returns a testable hypothesis, never a blind config paste. | Online Researcher agent; web tools | candidate |
| **writing-new-scripts** | Needed behavior exists nowhere (confirmed via index scan + `lerobot-* --help`). | Write the script (augmentation, curriculum, reward shaping, custom eval); place under run dir unless reusable; register afterwards if reusable. | — (feeds `scoring-with-reward-model` as its wrapper) | candidate |
| **checking-hardware** | Real-robot degradation with no software change; erratic identical-round evals. | `lerobot-calibrate`, `lerobot-find-cameras`, `lerobot-find-port`; save pre-calibration state; re-verify with a reference move. | those CLIs; physical hardware | candidate |
| **scoring-with-reward-model** | Real-hardware objective — no gym env, no `lerobot-eval`. | Score recorded episodes with `src/lerobot/rewards/` models (`robometer`/`topreward`/`sarm`/`reward_classifier` via `get_reward_model_class`), wrapped in a script that writes `eval_info.json` in the standard shape. | `src/lerobot/rewards/`; `writing-new-scripts` | candidate |
| **reverting-to-champion** | Confirmed REGRESSION (beyond noise band) or damaged `last` — never a within-noise dip. | Take the champion from the [round brief] (canonical durable `score_state`; the derived `[run_dir]/CHAMPION` pointer — line1 path, line2 metric, line3 round — is a cross-check only); quarantine step-dirs newer than champion (lerobot `save_checkpoint` uses `exist_ok=True` — would silently overwrite); repoint `checkpoints/last` as a relative symlink (matching `update_last_checkpoint()`); re-validate by re-running `eval_command` and requiring the champion metric to reproduce within the band. Resume `--steps` must exceed the *champion's* step count. | lerobot checkpoint/symlink conventions | candidate (from source inspection, not yet exercised) |
| **installing-libero-headless** | `env.type=libero` needed and `import libero` fails. | `CMAKE_POLICY_VERSION_MINIMUM=3.5 uv pip install --python .venv/bin/python egl_probe==1.0.2 hf-egl-probe==1.0.2`, then `hf-libero>=0.1.4,<0.2.0`, then drain the first-import prompt (`echo n \| python -c "import libero.libero"`), then EGL smoke test. | `uv pip`; hf-libero/robosuite/bddl; MUJOCO_GL=egl | candidate |
| **detaching-gpu-jobs** | Training/eval outlives a harness-tracked shell task (reaped ~18–25 min observed). | `setsid bash -c '<vars> <cmd> > <log> 2>&1; echo $? > <name>.exit' &`; record generation-owned identity (pid, ps-read pgid, /proc starttime, cmd sha256, exit sentinel, wait generation); persistent Monitor (60–120 s) on artifact + sentinel + `kill -0 $PID`; arm a second time-driven wake; cleanup = identity-verified `kill -- -PGID` from the controller, never bare `kill $PID`. Normalize logs with `tr '\r' '\n'`; steps ≥1000 print as "5K". | harness Monitor/ScheduleWakeup | candidate |
| **preparing-runtime** | Any dependency install, download, cache fill, or preprocessing step that may be slow/noisy/restarted. | Explicit cwd/interpreter/env; noninteractive and progress-off controls; resumable pinned cache/staging; hard log cap; disk/cache growth checks; atomic generation/lease-bound terminal envelope. | uv/pip/Hugging Face tooling plus task-specific commands | candidate |
| **skill-creator** | Creating/editing/optimizing skills themselves (vendored, Apache-2.0, anthropics/skills). | Full offline lifecycle: interview → SKILL.md → parallel with/without-skill test runs → assertions → grading → `aggregate_benchmark.py` → analyst → `generate_review.py` viewer → iterate → optional description optimization (`run_loop.py`) → `package_skill.py`. **Local vendoring note overrides upstream:** during a round use only its writing conventions; never start the eval loop mid-round. 3 scripts shell out to the `claude` CLI (Claude-Code-specific). | `claude -p` CLI (3 scripts); `pyyaml` (quick_validate); else stdlib | **validated** (upstream-tested; vendored body never edited) |

The index's `Origin` column cites option ids `O1`–`O11` from the retired `OPTIONS.md` registry (deleted during the PushT run — see `suggestions.md` A2); kept so old ledgers stay readable.

---

## `skills/original/skill-creator/` internals

- **`agents/analyzer.md` / `comparator.md` / `grader.md`** — subagent prompts for the offline eval loop: grade assertions against outputs; blind A/B comparison between skill versions; analyze why one version won (non-discriminating assertions, flaky evals, time/token tradeoffs).
- **`references/schemas.md`** — JSON schemas for `evals/evals.json`, `grading.json`, `benchmark.json`.
- **`assets/eval_review.html`** — template with `__EVAL_DATA_PLACEHOLDER__`/`__SKILL_NAME_PLACEHOLDER__`/`__SKILL_DESCRIPTION_PLACEHOLDER__`, used to human-review the 20 trigger-eval queries before `run_loop.py`.
- **`eval-viewer/viewer.html`** — static template consumed by `generate_review.py` via a `/*__EMBEDDED_DATA__*/` placeholder.

### Python scripts (function-by-function)

**`scripts/__init__.py`** — empty (0 bytes); makes `scripts/` a package for the `from scripts.xxx import yyy` imports below.

**`scripts/utils.py`**
- `parse_skill_md(skill_path) -> (name, description, content)` — parses SKILL.md YAML frontmatter without PyYAML (manual `---` scanning, handles block scalars `>`, `|`, `>-`, `|-`); raises `ValueError` on missing delimiters. Imported by `improve_description.py` and `run_eval.py`.

**`scripts/quick_validate.py`** *(depends: PyYAML)*
- `validate_skill(skill_path) -> (bool, message)` — checks SKILL.md exists, frontmatter parses, only allowed keys (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`), name kebab-case ≤64 chars, description ≤1024 chars no angle brackets, compatibility ≤500 chars.
- `main()` — CLI `python quick_validate.py <skill_dir>`, exit 0/1. Imported by `package_skill.py`.

**`scripts/package_skill.py`** *(depends: quick_validate; stdlib zipfile/fnmatch)*
- `should_exclude(rel_path)` — exclusion rules (`__pycache__`, `node_modules`, `*.pyc`, `.DS_Store` anywhere; `evals/` at skill root only).
- `package_skill(skill_path, output_dir=None)` — validates via `validate_skill` then zips the skill dir into `<skill_name>.skill`.
- `main()` — CLI `skill-folder [output-directory]`.

**`scripts/aggregate_benchmark.py`** *(stdlib only)*
- `calculate_stats(values)` — mean/sample-stddev/min/max, 4-decimal rounding.
- `load_run_results(benchmark_dir)` — discovers `eval-N/{with_skill,without_skill}/run-N/grading.json` (plus a legacy `runs/` layout and `timing.json` fallback); returns config→per-run results; warns rather than fails on malformed files.
- `aggregate_results(results)` — per-config stats over pass_rate/time/tokens + a delta between the first two configs.
- `generate_benchmark(benchmark_dir, skill_name, skill_path)` — full `benchmark.json` shape (metadata, runs, run_summary, empty notes for the analyst).
- `generate_markdown(benchmark)` — renders `benchmark.md` comparison table.
- `main()` — argparse CLI; writes both output files.

**`scripts/generate_report.py`** *(stdlib only; imported by run_loop.py)*
- `generate_html(data, auto_refresh=False, skill_name="")` — standalone HTML report of a description-optimization run: summary block, per-iteration rows with ✓/✗ cells per train/test trigger query (inline helpers `aggregate_runs`, `score_class`); handles legacy and new history shapes.
- `main()` — CLI (JSON in / HTML out, stdin/stdout supported).

**`scripts/improve_description.py`** *(depends: utils.parse_skill_md, `claude` CLI)*
- `_call_claude(prompt, model, timeout=300)` — runs `claude -p --output-format text` with the prompt on stdin; strips `CLAUDECODE` from child env to allow nesting; RuntimeError on non-zero exit.
- `improve_description(...) -> str` — builds a prompt from failed/false-trigger queries + prior attempts + full skill content; parses `<new_description>` tags; one retry pass if >1024 chars; optional transcript logging.
- `main()` — CLI; prints JSON with new description + appended history. Called by `run_loop.py`.

**`scripts/run_eval.py`** *(depends: utils.parse_skill_md, `claude` CLI; ProcessPoolExecutor)*
- `find_project_root()` — walks up to the nearest `.claude/` dir (mirrors Claude Code's discovery).
- `run_single_query(query, skill_name, skill_description, timeout, project_root, model=None) -> bool` — the trigger-test primitive: writes a temp slash-command file into `.claude/commands/` whose description mirrors the skill's; runs `claude -p <query> --output-format stream-json`; stream-parses NDJSON to detect a `Skill`/`Read` invocation of the temp command's unique name; always cleans up.
- `run_eval(...) -> dict` — parallel runs (`runs_per_query` × queries), per-query trigger rate vs. threshold, returns results + summary.
- `main()` — argparse CLI. Imported by `run_loop.py`.

**`scripts/run_loop.py`** *(orchestrator: run_eval + improve_description + generate_report + utils)*
- `split_eval_set(eval_set, holdout, seed=42)` — stratified (by `should_trigger`) train/test split.
- `run_loop(...) -> dict` — the optimization loop: eval train+test together, split results back, record history (test scores blinded from the improver), live HTML report option, early exit when all train queries pass, else propose a new description and iterate to `max_iterations`; selects best iteration by test (or train) score.
- `main()` — argparse CLI (`--model` required; `--report auto|none|path`; `--results-dir` writes `results.json`/`report.html`/`logs/`).

**`eval-viewer/generate_review.py`** *(stdlib only; standalone — no `scripts/` imports, no `claude` CLI)*
- `get_mime_type(path)` — MIME override table + `mimetypes` fallback.
- `find_runs(workspace)` / `_find_runs_recursive(...)` — find every dir containing `outputs/` (skipping `node_modules`/`.git`/`__pycache__`/`skill`/`inputs`).
- `build_run(root, run_dir)` — one run's display dict: prompt (from `eval_metadata.json` or `transcript.md`), stable `run_id`, embedded outputs, sibling `grading.json`.
- `embed_file(path)` — text inline; images/PDF as base64 data-URIs; xlsx/other as base64 downloads.
- `load_previous_iteration(workspace)` — prior iteration's `feedback.json` + outputs for cross-iteration review.
- `generate_html(runs, skill_name, previous, benchmark)` — fills `viewer.html`'s `/*__EMBEDDED_DATA__*/` placeholder.
- `_kill_port(port)` — `lsof -ti` + `os.kill`, best-effort.
- `ReviewHandler(BaseHTTPRequestHandler)` — `GET /` regenerates the page per request (fresh workspace scan); `GET/POST /api/feedback` reads/writes `feedback.json`; request logging suppressed.
- `main()` — argparse CLI (`workspace`, `--port` default 3117, `--static` for a standalone HTML file in headless environments; else serves on 127.0.0.1 and opens a browser).

---

## `context/RoboticKnowledges/` — reference library (no executable code)

Added 2026-07-19 (Function Update ID 9). Eleven Markdown files, **zero scripts, zero imports, zero test surface** — listed here only so future readers do not go looking for entry points.

### `knowledge_index.md`
Index of the ten categories, the sourcing/verification policy (what `award: not verified`, `precursor (…)`, and an empty year-slot each mean), aggregated known limitations, and a staleness note.

### `<category>/README.md` ×10
`ros`, `hardware`, `reinforcement-learning`, `imitation-learning`, `diffusion-and-flow-matching`, `vla`, `classic-control-and-planning`, `kernel-methods`, `mechanical-engineering`, `agentic-ai`. The six paper categories share one entry format — title / one-sentence contribution / one-sentence results — across 11 year-slots (2014–2024), 3×2025 and 5×2026, each ending in `## Coverage notes` and `## Sources`.

**Not a runtime dependency.** `robot_agentic_training_flow.md` never reads this tree, so it has no bearing on a loop execution. Contrast `skills/`, which the controller re-reads every round.

---

## Cross-cutting observations

1. The root docs are historical artifacts of **at least two separate loop executions** (PushT via the retired `train-robot-loop` skill; LIBERO ×2 via the current flow), whose overlapping evidence is mostly-but-not-fully reconciled in the skills library (`tuning-action-horizon` vs. deprecated `tuning-inference-chunking`; duplicate scheduler-clamp findings).
2. All `lerobot-*` commands live in the external LeRobot repo. Locally executable code is limited to the pure recovery checker/tests and skill-creator's offline tooling (three of whose scripts additionally require the `claude` CLI).
3. `.github/HarnessFlow/` is the installed orchestration pack (agents, contract, workflows, its own pack-internal skills) — separate from the flow's `skills/` library.
