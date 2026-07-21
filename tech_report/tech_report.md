# AgenticRobotics: An LLM-Controller Loop for Autonomous, Statistically-Gated, Crash-Safe Robot-Policy Improvement

*Technical report — draft materials.* Authored from the repository's own sources
(`README.md`, `robot_agentic_training_flow.md`, `objective.example.yaml`, the `skills/`
library) using the **ResearchStudio** methodology. Every quantitative claim is traced to
its in-repo provenance; where the repository does not ship the underlying run artifact,
the claim is reported as *the project's reported result*, not as an independently
reproduced measurement — consistent with the system's own Invariant 3 ("progress is
measured, never asserted").

---

## Abstract

Robot-policy learning is bottlenecked by its **outer** loop — deciding which lever to
pull next, when to collect data, and when to switch strategy — not by any single training
run, which is already automated. **AgenticRobotics** closes that gap with a context-lean
**LLM controller** that binds an external, immutable objective and then drives a pluggable
training backend (LeRobot / SmolVLA / LIBERO is the reference) through repeated
*train → evaluate → improve* rounds until a measured target holds, with **no iteration cap
and no "good enough."** The design rests on four principles: (i) *controller, not doer* —
the main agent spends context only on decisions and delegates all token-heavy work to
stateless, time-boxed, watchdog-killed workers; (ii) *measured, never asserted* — the
controller itself parses the metric from `eval_info.json` and gates promotion on an
Agresti–Caffo noise band with a 1.5× margin, confirmation evals, and paired tests; (iii)
*crash-safe by construction* — commit-keyed side effects, generation-scoped waits,
execution leases, and phase-transition handshakes let a killed session recover without
repeating or losing work; and (iv) a *compounding skills library* — every reusable
behavior is registered under a `flock`-shared open-standard library that makes the loop
smarter each run. We report two autonomous SmolVLA-on-LIBERO runs that reached **85.0** and
**88.0** `overall.pc_success` from champion baselines of **53.0** and **46.0**, one of them
via a 30-minute zero-training inference-config change. We are explicit about the system's
assumptions (an operator-authored objective; a resumable trainer + an `eval_info.json`-writing
eval command) and its limitations (small-n evaluation noise; run ledgers not shipped in the
public checkout; documentation-count drift; a missing `objective.schema.json`).

**Contributions.**
1. A controller/worker architecture that makes the robot-policy *outer* loop autonomous while keeping every measurement decision in the strong controller.
2. A statistically-disciplined promotion rule (noise band + margin + confirmation + paired McNemar/bootstrap) that resists eval-noise false positives, plus an optional locked acceptance holdout that resists adaptive-holdout reuse bias.
3. A durable round-transaction and recovery protocol (10 invariants; a 6-phase commit sequence; a pure, zero-I/O replay checker) that makes long unbounded runs crash-safe.
4. A live, evidence-tiered **skills library** (Agent Skills open standard) shared across concurrent runs, that compounds across runs and records negative results as first-class outcomes.

---

## 1. Introduction

**The outer loop is the bottleneck.** Given a dataset and a policy class, running one
training job is a solved, automated act. What remains manual is the *decision cycle* around
it: which hyperparameter or inference-config to change, whether to collect or relabel data,
when a plateau means "tune more" versus "switch strategy entirely," and when to stop. That
labor is what AgenticRobotics automates. An LLM **controller** owns the full cycle from
objective to exit condition, with crash recovery and statistical rigor built in, so a human
sets a target once and the system iterates unattended.

**The SOTA-discovery sub-problem.** Applying state-of-the-art methods is itself a research
bottleneck, and the 2026 tooling landscape makes it worse: Papers With Code was sunset by
Meta in July 2025 (its 9,327 leaderboards and 79,817 paper→code links frozen), and
ungrounded LLMs hallucinate 78–90% of citations on recent literature, so only
retrieval-grounded systems are reliable. AgenticRobotics integrates a **retrieval-grounded
Online Researcher** worker that queries grounded academic search mid-loop, so the controller
can incorporate published methods without the operator manually tracking the literature.
*(These framing claims originate in the project's README and its cited sources; we
independently re-verified each against primary sources — see §7.)*

**Why not a generic self-improving agent or an AutoML sweep?** Published self-improving-agent
patterns grow a side library and leave their program fixed — AgenticRobotics adopts that
discipline (Invariant 6) but couples it to something most such systems lack: *statistically
gated, crash-safe robot evaluation*. Versus a fixed AutoML/hyperparameter sweep, the action
space here is open — supervised, inference-time-config, data, and RL levers, plus
**self-authored new skills** — and actions are ranked by *gain per GPU-hour*, not a fixed grid.

---

## 2. System Design

### 2.1 Architecture: a controller and its workers

```text
 objective.yaml  (operator-authored, OUTSIDE the repo, immutable — Invariant 1)
        |
        v
   +----------------------  LLM CONTROLLER (main agent)  ----------------------+
   |  binds objective · decides each round's action set · PARSES the metric    |
   |  itself · scores · writes the ledger · decides halt/exit                  |
   +--------------------------------------------------------------------------+
        |  delegates all token-heavy work (compact results only)
        v
   Focus Analyst · Free Analyst · Online Researcher   (analyze / research)
   Executor · Implementer · QA Engineer · Bug Reproducer   (run skills / build / debug)
   Devils Advocate   (independent exit re-verification)
        |
        v
   Pluggable backend:  resumable trainer  +  eval_command -> eval_info.json
   (reference: LeRobot / SmolVLA / LIBERO; also PushT/ACT)
```

The controller is a strong model with a deliberately limited context window; it stays in the
main loop and spends context only on decisions. Everything else — analyzing eval outputs,
executing skills, writing scripts, debugging crashed evals, searching the literature — is
delegated to **stateless, time-boxed** workers that each return a *compact result*, never a
transcript. Workers are watchdog-killed on overrun (default 1 h; long work estimated
explicitly and killed at 2× the estimate); a kill is "a statement about the execution, never
about the policy."

### 2.2 Backend independence

The loop drives whatever the objective points at. The backend contract is exactly two things:
(1) a **resumable training step** that writes a checkpoint, and (2) an **`eval_command`** that
writes `{eval_dir}/eval_info.json` containing the objective's `metric_path`. LeRobot/SmolVLA/
LIBERO is the reference and validation backend, not the only target; any other library,
simulator, reward-model scorer, or real rig is supported by supplying its own equivalents.
Everything else — the controller/worker split, the gates, scoring, durability, the skills
library — is backend-independent.

### 2.3 The ten invariants (what every round must preserve)

1. The objective is **external and immutable** — read, never edited, never relaxed.
2. The **exit condition is the only exit** — not a plateau, a timer, or a feasibility judgment; when an acceptance gate is defined, the exit condition is the *conjunction* of the selection target and that locked gate.
3. **Progress is measured, never asserted** — the controller parses the metric from `eval_info.json` itself.
4. **Every round is logged before the next begins.**
5. The **skills library is a menu, not a fence** — you may always author a new skill; register what is reusable.
6. **This program is never modified at runtime** — only the outputs grow.
7. A **wake is generation-scoped and at-most-once.**
8. **Round side effects are commit-keyed** (scoring, ledger append, cleanup, advance each at most once per key).
9. **Placement never changes success semantics** — device IDs and process placement live only in execution leases.
10. **Transitions are derived from verified work** — a `*_COMPLETE` marker comes only from a verified terminal wait plus its artifacts.

### 2.4 Gates

The run passes through a fixed set of pass/fail checks: a **command preflight** (validates the
objective's raw eval-command text — allowed executables, only `{checkpoint}`/`{eval_dir}`
placeholders, no shell metacharacters or out-of-run-dir redirection — before *every* dispatch);
**measurement integrity** (the eval process actually ran, `eval_info.json` belongs to the
recorded dir/checkpoint, any repo-local eval script's sha256 is unchanged, and the worker
shows no eval-tampering signal); an **integrity check** (the objective's sha256 is unchanged);
a **sanity gate** (the objective is reachable at all); the **improvement rule** and
**stagnation gate** (below); and an optional **acceptance gate** (a locked holdout, read only
at exit).

### 2.5 The skills library

A growing menu of skills following the [Agent Skills](https://agentskills.io) open standard,
one directory per skill (`SKILL.md` with `name`/`description` + `lifecycle`/`evidence_tier`/
`safety` metadata), indexed by a router `skills/index.md`. As of this writing the library holds
**26 skill directories** — 11 under `original/`, 15 under `iterated/`. Of the 25 loop skills
carrying an evidence tier, **6 are `validated`, 18 `candidate`, and 1 `deprecated`** (a
measured-negative result kept for the record); the 26th directory is the vendored
`skill-creator` offline tooling, which carries no tier. Skills advance an **evidence ladder**
(`candidate → reproduced → cross-seed → cross-task → cross-embodiment`) that gates unattended
action selection. The library is shared **live** across concurrent loop instances: every
library write happens inside a `flock` transaction on a stable `LIBRARY.lock` sidecar, with
re-read + semantic-duplicate detection before an atomic index replacement.

### 2.6 Control-plane package (operator tooling, not the loop)

`agentic_robot/` is a small deterministic Python package (`validate` / `init` / `status` /
`replay` / `report` / `resume`) plus a pure `recovery/` module. It implements testable
control-plane primitives — objective validation, sha256 digesting, atomic/crash-safe writes,
a JSONL event ledger, metric scoring, replay checking — and by design **does not run the
training loop** (that is the LLM controller's job).

---

## 3. Method

### 3.1 The round loop (Steps 0–4)

- **Step 0 — Bind.** Validate the objective against the canonical schema, run the command preflight, sha256-digest the objective, scaffold `run_dir` with its locks and durable `ROUND_IN_PROGRESS.md`, and read the skills index.
- **Step 1 — Baseline (round 0, three phases).** A preflight probe (catches degenerate objectives before the big GPU spend), an initialize-training phase, and a trained-policy baseline eval that seeds the first champion. All body work runs in Executor workers; the controller allocates, verifies, parses, and logs.
- **Step 2 — Sanity gate.** Re-judge, on the real baseline `eval_info.json`, three reachability checks: degenerate success-signal (e.g., an env that reports `pc_success == 0.0` forever), already-satisfied, and metric-missing. Halt rather than loop on an unsatisfiable objective.
- **Step 3 — Round loop (repeat until exit).** Ten sub-steps: **(a)** verify the objective digest; **(b)** re-read the skills index; **(c)** *analyze* via three parallel workers (Focus Analyst, Free Analyst, Online Researcher); **(d)** *decide* the action set (controller-only; rank by gain-per-GPU-hour, prefer a zero-training lever when comparable, fix data first when the diagnosis points at data, and switch strategy class on stagnation); **(e)** *execute* via workers; **(f)** *measure* — the controller re-runs the preflight, dispatches the eval verbatim, and **parses the metric itself**; **(g)** *score* (below); **(h)** *register* new reusable skills under the library transaction; **(i)** *log* one byte-exact round entry; **(j)** *record* one advisory refine-signal row.
- **Step 4 — Exit.** Only when the exit condition holds. A **Devils Advocate** worker independently re-reads the final `eval_info.json`, re-derives `metric_best` from committed ledger blocks, and confirms the target; on disagreement the controller runs a controller-only `REMEASURE_ONLY` round. When an acceptance gate is defined, the locked holdout is run here — read *only* here, never for action selection — and the exit is the conjunction of both.

### 3.2 Scoring and statistics (the "measured, never asserted" core)

For each successful measurement the controller judges the delta *before persisting anything*:

- **Beyond the noise band with margin** (`|delta| ≥ 1.5 ×` band, or `≥ 1.5 × min_delta` when set) → the improvement rule passes outright.
- **Directionally improving but under that margin** → run *one* confirmation eval on the same checkpoint, then either **pool** the two evals (if per-episode results differ) and re-test against the narrower band, or — if the confirmation is identical, i.e. the eval is deterministic — switch to a **paired test** against the champion's stored per-episode outcomes: **McNemar** (with an exact-binomial small-sample fallback and a continuity-corrected χ² otherwise) for binary success, or a **paired bootstrap** (≥10⁴ resamples, 95% CI excludes 0) for non-binary metrics.
- **Not directionally improving** → `REGRESSION` (beyond band, wrong direction) or `NO PROGRESS` (within band).

The noise band is the Agresti–Caffo two-sample 95% half-width computed by the controller from
the two evals' own episode counts; an operator-supplied `min_delta` replaces it. A per-round
margin bounds one comparison's false-promotion rate; the **acceptance gate** is the separate
guard against the *cumulative* upward bias of reusing one selection eval to pick the champion
every round. The **stagnation gate** is an action-selection interrupt, never a termination
condition: after `stagnation_rounds` non-improving rounds the next action set *must* switch
strategy class.

### 3.3 Durability and recovery

A single canonical `ROUND_IN_PROGRESS.md`, serialized under a stable never-renamed sidecar
lock and atomically replaced (write-temp → flush → rename → flush-parent-dir), holds the entire
in-flight transaction: score state, monotonic wait/measurement generation high-water marks,
active/completed waits, execution leases, phase transitions, measurement attempts, log inputs,
prepared score/ledger commits, and the last completed-round tombstone. Round side effects are
**commit-keyed** and progress through a strict 6-phase sequence
(`READY_TO_SCORE → SCORE_APPLIED → REGISTRATION_COMMITTED → CLEANUP_COMPLETE → LEDGER_COMMITTED →
ROUND_ADVANCED`); recovery *completes* the first missing phase rather than repeating a committed
one. Every delegation follows a generation-scoped wait protocol (arm two wake triggers through
two mechanisms before yielding; a wake atomically claims exactly one generation — Invariant 7),
every dispatch takes an **execution lease** (a fencing-token'd placement record), and every
multi-operation chain derives a **phase transition** (`TRAIN_COMPLETE → EVAL_LAUNCHED →
EVAL_COMPLETE`) only from verified work. The ledger append itself is byte-exact and idempotent,
with a pure `recovery/replay_checker.py` (zero file I/O) that validates decoded snapshots and
repairs a torn append anchored by prefix + block sha256, refusing to guess on mismatch.

---

## 4. Evaluation

**What is measured.** The system's own success metric is the objective's `metric_path`
(reference: `overall.pc_success`, percent) read from `eval_info.json`, gated as in §3.2.

**Reported autonomous runs.** Two SmolVLA-on-LIBERO campaigns reached the following, fully
autonomously after the objective was set:

| Run id | Champion baseline | Final | Decisive lever | Provenance |
|---|---|---|---|---|
| `smolvla_libero_70_001` | 53.0 | **85.0** | `tuning-action-horizon` round: 64.0→85.0, Δ+32 vs champion, band ±12.1, n=100 fixed seeds — cleared the 70% target in one **30-min** round | `skills/iterated/tuning-action-horizon/SKILL.md` (Evidence) |
| `libero_smolvla_001` (2026-07-11) | 46.0 | **88.0** | inference action-horizon cut 50→10 on the 80k checkpoint: 52.0→88.0, Δ+42 vs champion, band ±11.8, n=100 fixed seeds, every `libero_object` task ≥7/10 | `skills/iterated/tuning-action-horizon/SKILL.md` (Evidence) |

The headline finding is not merely the numbers but *how* they were obtained: a **30-minute,
zero-training inference-config probe** produced a decisive win that a preceding multi-hour
training extension did not — exactly the "prefer a zero-training lever of comparable expected
gain" rule the controller applies at Step 3(d).

**Negative results are first-class.** The same skill's evidence records that the lever
*saturates*: going below horizon 10 **hurts** (10→5 gave 48.0→43.0, −5.0, and 44.0→33.0,
−11 pp in a controlled A/B; 39/100 episodes flipped, evidencing that n=100 eval is itself
noisy). One library skill (`unfreezing-the-vlm`) is marked `deprecated` — a measured-negative
result kept for the record. Retaining negatives is a design choice: they are what let the
"measured, never asserted" discipline steer future rounds away from spent levers.

**Provenance honesty.** This repository checkout does **not** ship the per-run `LOOP_LOG.md`
or `eval_info.json` artifacts (they live under each run's external `run_dir`); the numbers
above are drawn from the skills library's in-repo **Evidence** records, which are the closest
available provenance. They should be read as *the project's reported results*, reproducible
only against the external run directories — not as measurements this report independently
re-ran. This framing is deliberate: a report that asserted these numbers as independently
verified would violate the very invariant (3) the system is built on.

---

## 5. Related Work

**Vision-language-action policies and benchmarks.** SmolVLA is a 0.45B-parameter VLA trained
on a single GPU that reports strong LIBERO success at low inference cost, the reference policy
here (arXiv [2506.01844](https://arxiv.org/abs/2506.01844)). LeRobot is Hugging Face's
open-source robot-learning framework supplying the reference `lerobot-train` / `lerobot-eval`
CLIs ([release notes](https://huggingface.co/blog/lerobot-release-v040)). LIBERO is a lifelong
robot-learning benchmark (130 tasks across 4 suites; NeurIPS 2023 D&B; arXiv
[2306.03310](https://arxiv.org/abs/2306.03310)). LIBERO-PRO (arXiv
[2510.03827](https://arxiv.org/abs/2510.03827)) shows standard-LIBERO scores collapse under
perturbations — the motivation for the system's locked acceptance holdout.

**Evaluation rigor.** The promotion machinery instantiates classical two-sample/paired testing
under a controlled false-promotion margin; the acceptance-holdout design follows the
adaptive-data-analysis / holdout-reuse literature (Dwork et al., arXiv
[1506.02629](https://arxiv.org/abs/1506.02629); also *Science* 2015).

**Grounded scientific search.** The Online Researcher worker follows the retrieval-grounded
paradigm (OpenScholar, Nature DOI [10.1038/s41586-025-10072-4](https://www.nature.com/articles/s41586-025-10072-4);
preprint arXiv [2411.14199](https://arxiv.org/abs/2411.14199); PaperQA2; FutureHouse) precisely
to avoid the 78–90% ungrounded-citation hallucination rate.

**Self-improving and self-optimizing LLM agents.** The controller-loop framing relates to
test-time self-improving agents (arXiv [2510.07841](https://arxiv.org/abs/2510.07841)) and
iterative self-optimization over large search spaces (OPT-BENCH, arXiv
[2605.08904](https://arxiv.org/abs/2605.08904)); AgenticRobotics differs by keeping the program
fixed (Invariant 6) and coupling improvement to *gated, crash-safe robot evaluation*. The
report claims no head-to-head comparison against these systems — none is available in the
source material, and the source documents name no competing agentic *training-loop* framework.

---

## 6. Limitations and Threats to Validity

1. **Small-n evaluation noise.** Reference evals use n=50–100 episodes, yielding wide bands (≈±12–16 pp); a controlled A/B flipped 39/100 episodes on identical weights. The loop mitigates this (fixed seeds, paired tests, confirmation evals, a locked holdout) but cannot eliminate it — some rounds are honestly *inconclusive*.
2. **Reproducibility gap in this checkout.** The public repo does not include run ledgers or `eval_info.json`; the reported 85/88 results are traceable only to in-repo skill Evidence records, not to shippable measurement artifacts.
3. **Documentation-count drift.** The skill count is stated inconsistently across the repo: the README says "24 skills (16 candidate)," the maintained overviews say "22," and the actual tree holds **26** (6 validated / 18 candidate / 1 deprecated by frontmatter). The library index and the per-skill frontmatter also disagree by one `validated` entry. These are documentation-hygiene defects, not loop defects, but they undercut at-a-glance trust and should be reconciled to a single generated source of truth.
4. **A missing schema.** `objective.schema.json` was deleted (commit `ce1b7c8`) yet is still imported by `agentic_robot/objective.py` and the `validate` CLI path, so two schema tests fail and `agentic-robot validate` errors — a control-plane defect independent of the loop.
5. **Selection-eval overfitting.** Without the (optional) acceptance gate enabled, repeatedly optimizing one selection eval biases the champion upward; the loop's own docs recommend enabling the locked holdout for any long/unbounded campaign, but it is off by default.
6. **Human-in-the-loop residue.** The operator still authors the objective and provisions the backend, dataset, and compute; "autonomous" refers to the improvement loop, not to task specification or infrastructure.

---

## 7. Conclusion

AgenticRobotics demonstrates that the *outer* loop of robot-policy improvement — the part that
was still manual — can be made autonomous without surrendering measurement rigor or
crash-safety. The design's leverage comes from a strict separation of concerns (a decision-only
controller over disposable workers), a promotion rule that treats eval noise as the adversary
it is, a durability protocol that survives arbitrary kills, and a compounding skills library
that turns each run's lessons — including its failures — into reusable, evidence-tiered levers.
The reported single-GPU SmolVLA-on-LIBERO runs (53→85 and 46→88 `pc_success`, one via a
30-minute zero-training probe) illustrate the payoff of ranking actions by gain-per-GPU-hour.
The most valuable next steps are the four directions in the companion `idea_cards.md` —
holdout-aware anti-overfitting, learning the action-selection policy from the refine-signal
ledger, compiling grounded research into candidate skills, and sequential eval-episode
allocation — and closing the documentation and schema defects in §6.

---

## References (verified against primary sources)

- SmolVLA — arXiv [2506.01844](https://arxiv.org/abs/2506.01844)
- LeRobot v0.4.0 — https://huggingface.co/blog/lerobot-release-v040
- LIBERO — arXiv [2306.03310](https://arxiv.org/abs/2306.03310)
- LIBERO-PRO — arXiv [2510.03827](https://arxiv.org/abs/2510.03827)
- Dwork et al., adaptive holdout reuse — arXiv [1506.02629](https://arxiv.org/abs/1506.02629)
- OpenScholar — Nature DOI [10.1038/s41586-025-10072-4](https://www.nature.com/articles/s41586-025-10072-4); preprint arXiv [2411.14199](https://arxiv.org/abs/2411.14199)
- Self-improving LLM agents at test time — arXiv [2510.07841](https://arxiv.org/abs/2510.07841)
- OPT-BENCH (iterative self-optimization) — arXiv [2605.08904](https://arxiv.org/abs/2605.08904) *(recent, arXiv-only; positioning reference)*
- Agent Skills open standard — https://agentskills.io
- ResearchStudio (methodology used to produce these materials) — arXiv [2607.04439](https://arxiv.org/abs/2607.04439) (Idea) · [2607.04438](https://arxiv.org/abs/2607.04438) (Reel)
- Systems-paper writing guidance — Levin & Redell, [*How (and How Not) to Write a Good Systems Paper*](https://www.usenix.org/conferences/author-resources/how-and-how-not-write-good-systems-paper); Irene Zhang, [*Hints on how to write an SOSP paper*](https://irenezhang.net/blog/2021/06/05/hints.html)

*In-repo provenance:* `README.md`, `robot_agentic_training_flow.md`, `objective.example.yaml`,
`skills/index.md`, `skills/iterated/tuning-action-horizon/SKILL.md`.


https://claude.ai/public/artifacts/a2caec56-3449-472e-a53e-d63fbdb67231