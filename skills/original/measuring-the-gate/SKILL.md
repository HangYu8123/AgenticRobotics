---
name: measuring-the-gate
description: Run the objective's eval command verbatim to produce the round's metric — the loop's mandatory feedback signal. Use every round at the Measure step; never substitute a hand-rolled eval variant for the objective's own command.
metadata:
  lifecycle: validated
  safety: reversible
---

# Measure the gate

## When to use

Every round, at flow Step 3f (and Step 1 baseline). This is the loop's feedback
signal, not a discretionary action.

## Prerequisites

A checkpoint at `{checkpoint}`, and an [eval_command] that already passed the
flow's [command preflight] (Step 0).

## Do

Run the objective spec's `eval_command` verbatim. Never a hand-rolled variant.
The command's backend is whatever the objective points at; the skill is the same
for all of them, because the contract is the same for all of them.

### Reference backend (LeRobot / LIBERO)

```bash
uv run lerobot-eval \
  --policy.path=<train_dir>/checkpoints/last/pretrained_model \
  --env.type=<env> --eval.n_episodes=<N> --eval.batch_size=<B> \
  --policy.device=cuda --output_dir=<run_dir>/round_<n>/eval
```

The command's only contract: write `{eval_dir}/eval_info.json` containing the
objective's `metric_path`. Report the eval's exit status and the eval_info.json
path back to the controller — the controller parses the metric itself
(Invariant 3), so do not summarize the number as your result.

## Mutates

Nothing — each run writes only its own fresh `{eval_dir}`.

## Validation

`{eval_dir}/eval_info.json` exists and contains the objective's `metric_path`.

## Rollback

None — reversible.

## Watch out

- **MEASURE THE GATE'S OWN NOISE BEFORE TRUSTING ANY DELTA.** Measured on LIBERO-10 with
  `lerobot-eval`, n=100, **a fixed seed, the identical checkpoint and the byte-identical command**:
  two runs scored **52.0 and 44.0 — an 8-point spread on identical weights.** The eval is NOT
  deterministic despite `--seed` (env/GPU nondeterminism), and its run-to-run spread EXCEEDED the
  objective's `min_delta` of 5.0. Consequences, learned the hard way:
    * A single n=100 measurement **cannot distinguish a real +6 from luck.** A +3 that looked like
      progress evaporated to a pooled **-1.0** once confirmed.
    * **Never promote a champion on one measurement** when the delta is anywhere near the band.
      The flow's Step 3(g) confirmation protocol is not ceremony — it caught a false positive here.
    * Cheap way to calibrate: evaluate the SAME checkpoint twice into different eval dirs and look
      at the spread. Do it once, early; it tells you what your `min_delta` has to be.
    * If you need to resolve deltas smaller than the spread, raise `--eval.n_episodes` (the spread
      shrinks ~1/sqrt(n)) — but that is an OBJECTIVE change and is the operator's call, not yours.

- **Do not extrapolate the eval's [time budget] from a cheap probe.** A failing episode runs
  the FULL step budget while a success exits early, so a probe with a higher success rate has a
  far cheaper mean episode than the real eval. An observed 66-min estimate from a 45%-success
  probe became a 134-min reality. Estimate from episodes x the WORST-case step cap, or re-plan
  the deadline explicitly while the work is verified healthy.

- **Wall-clock levers live in the objective, not here.** `--eval.batch_size` is the number of
  parallel vectorized envs (verified in lerobot_eval.py: `make_env(..., n_envs=cfg.eval.batch_size,
  use_async_envs=cfg.eval.use_async_envs)`) — the main eval speed knob; it does not change
  n_episodes. `--eval.use_async_envs` exists, but only `=false` is validated locally (an async-env
  failure forced `=false` on the PushT run). lerobot-train's in-training eval (renamed
  `env_eval_freq` in lerobot v0.6.0) runs only when a sim `cfg.env` is configured — not a
  measurement shortcut for real-robot data. All of these are objective (operator) changes:
  mid-run edits trip the integrity gate.

- **A benchmark number is not a capability claim — and LIBERO is one of the weaker benchmarks on
  this axis.** The 2026 audit "What Are We Actually Benchmarking in Robot Manipulation?"
  (arXiv 2606.04233) found that **only 19.8% of LIBERO SOTA claims are provably significant**, that
  a **0.09B probe with no language encoder and no robotics pretraining** scores 99.0/100.0/98.8/92.4
  on LIBERO Spatial/Object/Goal/Long — at or above most published VLA numbers — and that LIBERO,
  CALVIN, and SimplerEnv each fail several of its four diagnostics (shortcut solvability,
  statistical significance, creeping overfitting, data-source dependence) while RoboTwin 2.0 and
  RoboCasa fare better. This is *why* the flow spends rounds on a [noise band], a confirmation
  protocol, and a locked [acceptance gate] instead of trusting one aggregate number. It is also why
  a high `pc_success` on LIBERO alone should never be reported as a capability result.

- **LIBERO: `eval_info.json` `task_id` follows the LIBERO benchmark's own suite order, NOT the HF dataset's `task_index`.** Resolve names via `libero.libero.benchmark.get_benchmark_dict()['<suite>']().get_task(i)` — never by the dataset's task table, or a diagnosis will chase the wrong tasks (this happened; it cost a round's analysis).
- **LIBERO reward is sparse and terminal**: `sum_rewards == max_rewards` is binary, and `eval_info.json` carries no sub-task progress. Any long-horizon (multi-stage) diagnosis must come from the rollout VIDEOS, not the JSON.

When using the stock `lerobot-eval` CLI, the aggregate metric lives at
`overall.<key>` in `eval_info.json`, **not** `aggregated.<key>`. A custom eval
command may write a different shape, as long as it contains the objective's
`metric_path`. Raise `--eval.n_episodes` if the metric is noisy round-to-round;
a delta smaller than the eval's own variance is not progress — the flow's
[noise band] makes this judgment explicit.

## Evidence

- Origin: OPTIONS.md O3 (seed option); the mandatory measurement every round —
  validated by construction, since every logged round's Measure step exercises
  it.
- run _70_002 round 5 (2026-07-16): SAME checkpoint, command, seed, n=100 measured 63.0 then 55.0 — 8pp same-checkpoint spread confirmed on a soup checkpoint (matches the min_delta 8.0 rationale). Single-eval promotions at the band edge are provisional; budget a calibration re-measure before staking rounds on a fresh champion.
