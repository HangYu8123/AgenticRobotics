---
name: conditioning-on-advantage
description: RL-improves a FLOW-MATCHING or diffusion policy (SmolVLA, pi0) by conditioning it on a binarized advantage label instead of a policy gradient, because those policies expose no tractable action log-probabilities for PPO/GRPO. Use when the policy class is flow-matching/diffusion, SFT and config levers have stalled, and autonomous rollouts with per-episode outcomes (optionally plus expert corrections) are available.
metadata:
  lifecycle: candidate
  evidence_tier: candidate
  safety: mutating
---

# Condition a flow-matching policy on advantage (RECAP-style)

## Prerequisites
A resumable starting [checkpoint] whose action head is **flow-matching or diffusion**
(SmolVLA, pi0/pi0.5); a corpus of rollouts carrying a per-episode outcome — produce it with
`harvesting-rollouts`. Expert corrections/interventions are optional but are what the method
was designed around. Compute for a second, smaller value model.

**Why this skill exists.** PPO/GRPO need `log pi(a|o)`. A flow-matching action expert integrates
a deterministic ODE and exposes no such density, so the GRPO/REINFORCE recipes in
`reinforcing-with-rl` do **not** apply to it unmodified — SimpleVLA-RL states this outright
(arXiv 2509.09674: diffusion-based action decoding "lack[s] the action distributions necessary
for both random sampling and policy gradient computation"). Two published families fix it:
convert the ODE to an SDE to recover a density (πRL, VLA-RFT — see `reinforcing-with-rl`), or
skip policy gradients entirely and condition on advantage. This skill is the second family: it
trains with the **stock flow-matching loss**, so it needs no surgery on the action expert.

## Do
Four stages. Every command below is illustrative — this repo vendors no training backend, so
resolve the real entry points against the installed one first.

1. **Collect.** Pool: the existing demos, autonomous on-robot/sim rollouts from
   `harvesting-rollouts`, and any expert corrections. Label each episode with a sparse return
   (RECAP uses `0` on success, `-C_fail` on failure, `-1` per other step — i.e. "steps until
   success").
2. **Fit a value function.** Train a separate, smaller **distributional** value model
   `V(o_t, instruction)` against the *empirical Monte-Carlo return* (RECAP: a 670M Gemma-3 head
   over 201 discretized return bins, cross-entropy loss — not TD bootstrapping). During
   post-training an N≈50-step lookahead return replaces the full-episode return.
3. **Binarize the advantage and condition.** Advantage `A_t = actual_return_t - V(o_t)`. Emit the
   indicator `1[A_t > eps]`, where the per-task threshold `eps` is **calibrated so ~30% of demo
   data (~40% of fine-tuning rollouts) lands positive** — do not pick `eps` by feel. Inject it as
   a plain text token alongside the usual language input, `"Advantage: positive"` /
   `"Advantage: negative"`, and fine-tune with the ordinary flow-matching loss. Drop the token on
   **30%** of samples so the model also learns the unconditional distribution. Expert corrections
   are force-labeled positive regardless of computed advantage.
4. **Serve positive.** At inference always condition on `"Advantage: positive"`. Optionally sharpen
   with classifier-free guidance between the conditional and unconditional velocity fields,
   `beta` in `[1.5, 2.5]`.

Then measure through the objective's [eval_command] like any other round.

## Mutates
Policy weights — writes a new [train_dir] lineage. Adds a separate value-model checkpoint. The
champion is untouched.

## Validation
Before spending the fine-tune: confirm the positive-label fraction actually lands near the
calibration target, and that the value model's predictions correlate with held-out episode
returns (a value model that predicts the mean everywhere makes every advantage zero and the whole
run degenerates to plain SFT on the pooled data). After: score the checkpoint against the
[noise band] like any other round; run it isolated for attribution. Also check the conditioning
does something — evaluating with `"Advantage: negative"` should be measurably *worse*; if it is
not, the token is being ignored.

## Rollback
A new lineage, so the champion stands: on a confirmed regression use `reverting-to-champion`, or
keep partial gains with `souping-task-vectors`.

## Watch out
- **No reference implementation exists.** Physical Intelligence published no code for RECAP. The
  RLinf repo lists a `RECAP` algorithm, but its fidelity to the paper is **unverified** — diff it
  against the paper's formulas before trusting it, and record what you found in Evidence.
- Not demonstrated on SmolVLA by anyone. The published results are pi*0.6 on real robots; treat
  a SmolVLA/LIBERO application as an original experiment, not a reproduction.
- The value model is the load-bearing part. A bad `V` produces noise-labeled data and the fine-tune
  learns nothing while looking perfectly healthy.
- Reward hacking still applies even without a policy gradient: the label comes from a learned
  value model, so gate the result on the locked `[acceptance gate]` and `[measurement integrity]`,
  never on training-side advantage statistics.
- The paper's gains come substantially from **expert corrections**, not autonomous data alone. With
  zero corrections, expect less than the published effect and say so in the round entry.
- Compare annealed-to-annealed, per `continuing-training`'s Watch out — a re-warmed fine-tune reads
  transiently worse mid-schedule.

## Evidence
<!-- Upstream: RECAP / pi*0.6, arXiv 2511.14759 (paper-only, no public code from Physical
     Intelligence; https://github.com/RLinf/RLinf lists a community "RECAP" of unverified fidelity).
     Log-prob intractability for flow/diffusion action heads stated in SimpleVLA-RL arXiv 2509.09674.
     Alternative (SDE-conversion) family: piRL arXiv 2510.25889, VLA-RFT arXiv 2510.00406.
     Commit: unpinned. Compatibility: flow-matching / diffusion action experts (SmolVLA, pi0/pi0.5);
     NOT needed for autoregressive-token VLAs. Permissions/mutation scope: writes new policy and
     value checkpoints only. Reviewer: unreviewed. -->
- none — original, offline 2026-07-19. No logged round yet; candidate. Record the value model's
  held-out calibration, the realized positive-label fraction, the isolated delta ± band, seeds,
  task, hardware, GPU-hours, and verdict here (positive and negative) when run.
