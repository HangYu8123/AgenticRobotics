---
title: "AgenticRobotics: An LLM-Controller Loop for Autonomous, Statistically-Gated, Crash-Safe Robot-Policy Improvement"
authors: <fill in — project maintainers>
institutes: <fill in — or leave empty>
venue: ""    # unpublished project; NEVER write "arXiv"/"Preprint" here (paper2assets rule)
paper_url: <fill in — repo or preprint URL>
code_url: <fill in — repo URL>
title_audio_script: >-
  AgenticRobotics is an LLM-agent training loop that makes robot-policy improvement
  autonomous. A context-lean controller binds an external, immutable objective, then
  drives a pluggable backend through repeated train-evaluate-improve rounds until a
  measured target holds — with no iteration cap. It keeps every measurement decision in
  the controller, gates promotion with real statistics, and survives crashes by
  construction. In two SmolVLA-on-LIBERO runs it reached eighty-five and eighty-eight
  percent success from baselines of fifty-three and forty-six, one of them via a
  thirty-minute change that touched no weights at all.
---

<!--
Reusable dissemination substrate, produced per ResearchStudio-Reel `paper2assets`
(9 canonical sections; each with Necessary / Additional / Audio script). Downstream
renderers (paper2poster, paper2blog, paper2video) consume THIS file. All numbers are
derived from `tech_report.md` — keep them in sync; edit the report first, then this file.
Source authority for the 9-section shape: ResearchStudio-Reel/skills/paper2assets/SKILL.md.
-->

## Problem
**Necessary:** Robot-policy learning is bottlenecked by its *outer* loop — deciding what to train next, when to collect data, when to switch strategy — not by any single, already-automated training run.
**Additional:** That decision labor stays manual even when training is fully scripted, and applying SOTA methods is itself blocked by a degraded discovery landscape (Papers With Code frozen; 78–90% ungrounded-citation hallucination).
**Audio script:** Running one training job is a solved problem. What still takes a human is everything around it — which knob to turn next, whether to go collect more data, when a plateau means keep tuning versus change strategy entirely, and when to stop. That outer loop is the real bottleneck in robot learning, and it is exactly what this project automates.

## Motivation
**Necessary:** An LLM controller can own the full decision cycle from objective to exit condition, unattended, if — and only if — it keeps measurement rigor and crash-safety.
**Additional:** Published self-improving agents grow a side library but rarely couple it to statistically gated, crash-safe robot evaluation; naive AutoML sweeps fix a grid instead of an open action space.
**Audio script:** The bet is that a strong language model, kept lean and focused only on decisions, can run this loop by itself. The catch is that autonomy without rigor is dangerous: if the agent believes a noisy eval or loses its place after a crash, it will chase ghosts. So the design's real content is how it measures and how it recovers.

## Contribution
**Necessary:** (1) A controller/worker architecture that makes the outer loop autonomous while keeping every measurement decision in the controller; (2) a statistically-disciplined promotion rule plus an optional locked acceptance holdout; (3) a durable, crash-safe round-transaction and recovery protocol; (4) a live, evidence-tiered skills library that compounds across runs.
**Additional:** Ten invariants formalize the guarantees; negative results are retained as first-class, evidence-tiered outcomes.
**Audio script:** There are four contributions. A clean split between a decision-only controller and disposable workers. A promotion rule that treats evaluation noise as an adversary, backed by an optional locked holdout. A durability protocol that survives arbitrary kills. And a shared skills library that turns every run's lessons, including its failures, into reusable levers.

## Method
**Necessary:** A context-lean controller binds an immutable objective, then each round spawns stateless time-boxed workers to analyze/execute/research/debug, decides the action set itself, parses the metric from `eval_info.json` itself, scores against a noise band with a 1.5× margin and paired confirmation tests, registers reusable skills under a `flock`-shared library, logs a byte-exact ledger, and exits only when the target holds.
**Additional:** Backend-agnostic contract = a resumable trainer + an `eval_command` writing `{eval_dir}/eval_info.json`; durability is commit-keyed (6-phase sequence), generation-scoped, and lease-guarded, with a pure zero-I/O replay checker.
**Key equation:** Agresti–Caffo two-sample promotion band (95% half-width), per eval `$\tilde p = (k+1)/(n+2)$`, band `$1.96\sqrt{\tilde p_1(1-\tilde p_1)/(n_1+2) + \tilde p_2(1-\tilde p_2)/(n_2+2)}$`; promote outright when `$|\Delta| \ge 1.5\times$` band, else require a confirmation eval.
**Audio script:** Each round, the controller decides what to try, delegates the heavy work to short-lived workers, and then does the one thing it never delegates: it reads the evaluation file itself and computes whether the change really helped. A result only counts as progress if it clears a statistical margin, or survives a paired re-test. Anything reusable it learned becomes a new skill in a shared library, and the whole transaction is written so that a crash mid-round can be recovered, not repeated.

## Dataset / Benchmark
**Necessary:** Reference backend is LeRobot / SmolVLA / LIBERO; the visible optimization metric is `overall.pc_success`. An optional locked holdout (e.g. LIBERO-PRO perturbation suites) is the acceptance gate, read only at exit.
**Additional:** The loop is backend-independent — any library, simulator, reward-model scorer, or real rig that supplies a resumable trainer and an `eval_info.json`-writing eval command is supported (PushT/ACT is another worked example).
**Audio script:** The system is validated on SmolVLA policies evaluated on the LIBERO benchmark through the LeRobot framework, but nothing about the loop is specific to them. Any backend that can resume training and write a standard evaluation file plugs in, including a real robot scored by a reward model.

## Key Result
**Necessary:** Two autonomous SmolVLA-on-LIBERO runs reached 85.0 and 88.0 `overall.pc_success` from champion baselines of 53.0 and 46.0 — no human intervention after the objective was set.
**Additional:** The 46→88 run's decisive move was an inference action-horizon cut (50→10) that touched no weights; the 53→85 run cleared its 70% target in a single 30-minute round. Provenance is the skills library's Evidence records, not shipped run ledgers.
**Audio script:** In two separate runs, the loop lifted success from fifty-three to eighty-five, and from forty-six to eighty-eight percent, entirely on its own. Strikingly, one of those wins came from a thirty-minute change that retrained nothing — it just shortened how many actions the policy commits to before looking again.

## Ablation Study
**Necessary:** The action-horizon lever saturates: below horizon 10 it reverses (10→5 gave 48.0→43.0, −5.0; a controlled identical-weights A/B gave 44.0→33.0, −11 pp).
**Additional:** In that A/B, 39 of 100 episodes flipped outcome on identical weights — direct evidence that n=100 evaluation is itself noisy, motivating the paired tests and confirmation evals.
**Audio script:** The same experiment that produced the win also mapped its limit. Pushing the horizon below ten made things worse, not better, and a controlled comparison on identical weights saw nearly forty percent of episodes flip outcome — a vivid reminder of why the loop never trusts a single evaluation.

## Headline Numbers
**Necessary:** 85.0 and 88.0 final `pc_success` (from 53.0 / 46.0); Δ+32 and Δ+42 versus champion at n=100 fixed seeds; noise bands ±12.1 and ±11.8; one decisive round = 30 minutes, zero training.
**Additional:** Library = 26 skills (6 validated / 18 candidate / 1 deprecated by frontmatter); a measured-negative skill is retained as `deprecated`.
**Audio script:** The numbers to remember: eighty-five and eighty-eight percent success, up from fifty-three and forty-six; gains of thirty-two and forty-two points measured over a hundred fixed-seed episodes; and a thirty-minute, zero-training round doing the heavy lifting.

## Takeaway
**Necessary:** The manual outer loop of robot-policy improvement can be made autonomous without giving up measurement rigor or crash-safety — and a decision-only controller ranking levers by gain-per-GPU-hour finds cheap wins a human sweep would miss.
**Additional:** The compounding, evidence-tiered skills library — negatives included — is what makes each subsequent run smarter.
**Audio script:** The lasting message is that autonomy and rigor are not in tension. By keeping a strong controller focused only on decisions, measuring everything itself, and remembering both what worked and what didn't, the loop improves robot policies on its own — and sometimes the best move costs thirty minutes and no training at all.
