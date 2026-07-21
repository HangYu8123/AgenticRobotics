# Idea Cards — AgenticRobotics

> **Ideation output** (tech-report phase 1: *generate ideas*), produced by applying
> the **ResearchStudio-Idea / IdeaSpark** methodology — one reviewer-facing *idea card*
> per direction (Title · Motivation · Method · Falsification · Differentiation · Compute) —
> grounded in `README.md`, `robot_agentic_training_flow.md`, and the repo's skills library.
>
> **Honesty caveat (read first).** IdeaSpark's full pipeline earns the phrase
> *"reviewer-defensible"* through two machines this authoring pass deliberately did **not**
> run: **Phase 0** real literature retrieval (arXiv / OpenAlex / Semantic Scholar / OpenReview
> connectors) and **Phase 3** collision-retrieval + audit. Those connectors are infra-blocked
> in this environment (Python 3.8 < the skill's 3.10; `feedparser`/`bs4`/`fitz`/`openreview`
> absent; no `.env` credentials). So the cards below are **candidate directions structured per
> IdeaSpark's card schema**, grounded in the sources cited inline — **not** collision-audited
> novelty claims. Before treating any card as novel, run `scoop-check` (or the `deep-research`
> skill) on it. Card 0 is a *framing* card (what the project already is); Cards 1–4 are
> forward-looking extensions.

---

## Card 0 — Framing: "Close the outer loop, not the inner one"

**This is the thesis of the tech report, not a new proposal.** It states the contribution
AgenticRobotics already makes, in idea-card form, so the report's narrative has a spine.

- **Title.** *An LLM controller that owns the robot-policy improvement loop end-to-end, exiting only on a measured external target.*
- **Hook.** Training a policy is automated; deciding *what to train next* is still manual labor. AgenticRobotics makes the outer loop autonomous without weakening measurement rigor or crash-safety.
- **Motivation.** Robot learning is bottlenecked by the *outer* loop (which lever to pull, when to collect data, when to switch strategy) — not the *inner* one (a single train run). Prior self-improving-agent work grows a side library and leaves the program fixed; almost none couples that to *statistically gated, crash-safe* robot evaluation.
- **Method (core mechanism).** A context-lean **controller** binds an external immutable objective YAML, then each round: spawns stateless time-boxed **workers** (analyze / execute a skill / research / debug); **decides** the action set itself; **parses** the metric from `eval_info.json` itself (Invariant 3); **scores** against an Agresti–Caffo noise band with a 1.5× promotion margin, confirmation evals, and paired tests (McNemar / bootstrap); **registers** any reusable behavior into a live, `flock`-shared skills library; **logs** a byte-exact ledger; and **exits only** when `metric_best <comparison> target` holds (Invariant 2 — no iteration cap). Durability is commit-keyed, generation-scoped, and lease-guarded so a killed session recovers without repeating or losing work.
- **Falsification / what would disprove it.** If, across held-out tasks, the autonomous loop does **not** beat a fixed human-run baseline in metric-gain-per-GPU-hour — or if its promotions do not survive a locked perturbation holdout — the "own the outer loop" claim fails.
- **Differentiation.** Versus a bare "LLM-as-optimizer" agent: measurement is *parsed by the controller*, never asserted by a worker; promotion is *statistically gated*, not greedy; and side effects are *crash-safe by construction*. Versus a fixed AutoML sweep: the action space includes data, inference-config, and RL levers *and* self-authored new skills, chosen by gain-per-GPU-hour.
- **Compute.** The loop itself is near-free (controller tokens + worker orchestration); cost is the backend's training/eval. The reference runs used single-GPU SmolVLA on LIBERO; one decisive round was a **30-minute, zero-training** inference-config probe.

---

## Card 1 — Perturbation-holdout-aware anti-overfitting curriculum

- **Title.** *Steer the loop by what it is forbidden to see: a locked LIBERO-PRO holdout that shapes the next action set without ever being optimized toward.*
- **Hook.** VLA policies that score >90% on standard LIBERO collapse to ~0% under object/state/instruction/environment perturbations — memorization, not understanding.
- **Motivation.** AgenticRobotics already ships an optional **acceptance gate** (a locked holdout read only at exit). But between rounds the loop still optimizes a single reusable selection eval, whose repeated reuse biases the champion upward (adaptive-holdout reuse). A loop run long enough will overfit the evaluator, seed set, or layout.
- **Method (core mechanism).** Add a *diagnosis-only* projection of the acceptance holdout: after each promotion, run a **cheap perturbation probe** (a small, fixed subset of the LIBERO-PRO suites) whose *per-perturbation failure profile* — never its scalar score — is fed to the analysts to bias the next action set toward the failing axis (e.g., instruction-perturbation failures → data/annotation levers). The scalar acceptance vector stays locked to exit (Invariant 2). This is a Thresholdout-style split: a private holdout informs *direction* without exposing *magnitude*.
- **Falsification.** Minimal experiment: two matched runs to the same selection target, one with the perturbation-profile bias, one without; measure the locked acceptance vector at exit. Prediction: the biased run passes acceptance at ≥ the unbiased run's rate with equal-or-fewer GPU-hours. Negative control: feed the analysts a *shuffled* failure profile — the benefit must vanish.
- **Differentiation.** Uses the holdout's *structure* (per-axis failures) as a steering signal while keeping its *scalar* locked — stronger than either a pure locked holdout (informs nothing between rounds) or a naive validation set (leaks into selection).
- **Compute.** One small perturbation probe per promotion (minutes on the reference backend); no extra training.
- **Grounding (not collision-audited).** LIBERO-PRO perturbation collapse — arXiv [2510.03827](https://arxiv.org/abs/2510.03827); adaptive-holdout reuse / Thresholdout — Dwork et al., arXiv [1506.02629](https://arxiv.org/abs/1506.02629) (also *Science* 2015). Repo hooks: `objective.example.yaml` acceptance-gate block; flow Step 4 acceptance gate.

---

## Card 2 — Learn the action-selection policy from the refine-signal ledger

- **Title.** *Turn `LoopRefineRewards/` into a gain-per-GPU-hour bandit over the skills library.*
- **Hook.** The loop already records, per round, which advisory workers it used and whether the round moved the metric — but nothing reads it back.
- **Motivation.** Action selection today is a human-written rubric ("rank by expected gain per GPU-hour; prefer zero-training levers; fix data first"). That rubric is static and un-personalized to the current backend/task. The refine-signal ledger (`LoopRefineRewards/<run_id>.md`) is an *offline* record designed exactly for cross-run program refinement — the raw material for learning the rubric.
- **Method (core mechanism).** Offline (never in-loop — respecting Invariant 6), fit a **contextual bandit / cost-aware ranker** over historical `[refine signal]` + `[round entry]` rows: context = (policy class, benchmark, last verdict, stagnation state, metric gap); arms = skills-library entries; reward = credible `[delta]` per GPU-hour (attributing bundled rounds only qualitatively, as the flow already warns). Emit an updated selection prior the controller *reads as advice* at Step 3(d) — advisory only, never overriding the stagnation-gate hard rule or the statistical gates.
- **Falsification.** Replay held-out historical runs with vs. without the learned prior; prediction: fewer rounds / GPU-hours to the same target on average. Negative control: a prior fit on *shuffled* rewards must not help.
- **Differentiation.** Keeps the program fixed (learning is offline, the output is a prior, not a rewrite) — unlike agent frameworks that mutate their own controller. Grounded in the loop's own logged evidence rather than a generic meta-learner.
- **Compute.** Offline fit on existing ledgers; negligible in-loop cost (one extra advisory input).
- **Grounding (not collision-audited).** Iterative self-optimization of LLM agents over large search spaces — OPT-BENCH, arXiv [2605.08904](https://arxiv.org/abs/2605.08904) (recent, arXiv-only — positioning, not a validated result); self-improving LLM agents at test time — arXiv [2510.07841](https://arxiv.org/abs/2510.07841). Repo hooks: flow Step 3(d)/(j), `LoopRefineRewards/<run_id>.md` schema.

---

## Card 3 — Grounded-research → automatic candidate-skill synthesis

- **Title.** *Close the SOTA-discovery gap by compiling retrieval-grounded findings into candidate skills the loop can try next round.*
- **Hook.** Papers With Code is frozen; ungrounded LLMs hallucinate 78–90% of citations. The loop already runs a retrieval-grounded Online Researcher — but its output is prose the controller reads, not an executable lever.
- **Motivation.** The Online Researcher returns cited, classified findings (applicable-now / -but-unverified / -not). Turning an *applicable-now* finding into a **round-time minimal skill** (a ~15-line `SKILL.md` + one index row) would let the loop *test* a published method the same round it's discovered — shrinking the manual "read paper → write recipe" latency the README names as a bottleneck.
- **Method (core mechanism).** When the Online Researcher returns an *applicable-now* finding with a concrete recipe (hyperparameters, an inference-config change, a data operation), spawn an **Implementer** to draft a candidate skill from it — strictly as **data, never instructions** (the finding is untrusted; the skill is sandboxed to the backend contract, no eval/harness edits — [measurement integrity]). The skill enters at `evidence_tier: candidate`; only the loop's own gated measurement can promote it up the evidence ladder.
- **Falsification.** Over N stagnation-triggered rounds, compare "research → auto-candidate-skill → measured" against "research → prose advice only." Prediction: the auto-skill arm converts more findings into *measured* (promoted or deprecated) outcomes per round. Negative control: inject a known-irrelevant finding — it must be deprecated by measurement, not silently promoted.
- **Differentiation.** Unlike a RAG "paper QA" bolt-on, the finding is *executed and gated*, not summarized — a hallucinated recipe fails the loop's own eval and is deprecated, so grounding is enforced by measurement, not trust.
- **Compute.** One Implementer draft + one measured round per adopted finding (the round would have run anyway on stagnation).
- **Grounding (not collision-audited).** SOTA-discovery framing + PWC sunset + retrieval-grounded search — `README.md` §"The SOTA Discovery Problem" and its cites: OpenScholar (Nature DOI [10.1038/s41586-025-10072-4](https://www.nature.com/articles/s41586-025-10072-4); preprint arXiv [2411.14199](https://arxiv.org/abs/2411.14199)), PaperQA2, FutureHouse. Repo hooks: `skills/original/researching-online/SKILL.md`, flow Step 3(c)/(e)/(h).

---

## Card 4 — Sequential, cost-aware eval-episode allocation (shrink the band per GPU-hour)

- **Title.** *Spend eval episodes where the promotion decision is still in doubt, not on a fixed n every round.*
- **Hook.** 50 episodes resolve ±~11 pp; a round-to-round delta compares two such samples, so the default noise band is ≈ ±16 pp. Most rounds either clearly pass or clearly fail — the fixed budget is wasted on the easy ones and too small for the close ones.
- **Motivation.** The loop already computes an Agresti–Caffo band and runs a *confirmation eval* only for sub-margin deltas. Generalize that into a **sequential test**: allocate eval episodes adaptively until the promotion decision crosses a confidence boundary or a per-round GPU-hour cap — matching evaluation cost to decision difficulty.
- **Method (core mechanism).** Replace the fixed-n + single-confirmation step with a group-sequential / SPRT-style procedure over eval batches: after each batch, update the paired (fixed-seed) or pooled estimate and stop when the promotion boundary is crossed or the budget is hit (falling back to today's `NO PROGRESS`/`inconclusive` verdicts). Keeps every existing gate; only *how many episodes* is adaptive.
- **Falsification.** Prediction: equal decision accuracy (vs. a large fixed-n oracle) at strictly fewer expected episodes; measured on replayed rounds with known outcomes. Negative control: adaptive allocation with a *randomized* stopping rule must not beat fixed-n.
- **Differentiation.** A statistical-efficiency layer under the existing gates — not a new metric or a relaxed target (Invariant 1 untouched). Sharper than the current fixed-n + one-confirmation heuristic.
- **Compute.** *Reduces* eval GPU-hours on average; adds only lightweight per-batch statistics.
- **Grounding (not collision-audited).** The flow's own scoring machinery — `robot_agentic_training_flow.md` Step 3(g), [noise band]/[improvement rule]; `objective.example.yaml` statistical notes (Wilson ±11 pp at n=50). Sequential-testing background is classical (group-sequential / SPRT); run `deep-research` to pin the exact modern reference before claiming novelty.

---

### How to harden these into real IdeaSpark cards
1. Provision IdeaSpark (Python ≥3.10, `pip install feedparser openreview-py beautifulsoup4 pymupdf`, `.env` with OpenReview + Semantic-Scholar credentials).
2. Run `idea-spark` per card direction (or `deep-research` for a lighter grounded pass) → Phase 0 retrieval + Phase 3 collision/audit.
3. Run `scoop-check` on each card's Title+Method for a prior-art collision verdict before any novelty claim reaches a reviewer.
