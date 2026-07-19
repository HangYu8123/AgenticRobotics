---
name: reinforcing-with-rl
description: Fine-tunes the policy with reinforcement learning against an environment reward so it can improve BEYOND the demonstration distribution (new-behavior discovery), instead of only imitating demos. Use when supervised/config levers have stagnated AND an env reward (binary success is enough) or a trainable reward classifier is available.
metadata:
  lifecycle: candidate
  evidence_tier: candidate
  safety: mutating
---

# Reinforce the policy with RL to escape the demo distribution

## Prerequisites
A resumable starting [checkpoint]; an interactive env exposing a per-episode reward — a gym/sim (LIBERO, ManiSkill, RoboTwin) or a real rig with a reward signal. Sparse **binary success is sufficient** — no dense reward design needed. With no reward at all, first get one: `harvesting-rollouts` + `scoring-with-reward-model`/`annotating-data`.

**Know your policy class before you pick a recipe.** Standard PPO/GRPO need a tractable
`log pi(a|o)`. Autoregressive/discretized-token VLAs (OpenVLA-OFT, QueST) provide one; a
**flow-matching or diffusion action expert (SmolVLA, pi0) does not** — SimpleVLA-RL states this
outright (arXiv 2509.09674). Applying a token-VLA recipe to a flow-matching checkpoint is not a
tuning problem, it does not run.

## Do
Run one RL fine-tune, then measure through the objective's [eval_command] like any other round.

**The controller picks the recipe and names it in the [round brief]** (flow Step 3d is never
delegated); as a worker, execute the one you were given — do not choose from this table yourself.

| Recipe | Family | Reward needed | Policy classes it actually runs on |
|---|---|---|---|
| LeRobot HIL-SERL / TDMPC | off-policy actor–learner | reward classifier or keypress | LeRobot RL policies — the reference backend's built-in path |
| SimpleVLA-RL (arXiv 2509.09674) | GRPO, outcome-only 0/1 | sparse binary | **OpenVLA-OFT only.** Flow-matching support is roadmap, not released |
| RIPT-VLA (arXiv 2505.17016) | leave-one-out REINFORCE | sparse binary | QueST, OpenVLA-OFT (both autoregressive) |
| RLinf-VLA (arXiv 2510.06710) | unified PPO/GRPO + many | sparse binary | OpenVLA, OpenVLA-OFT, GR00T, **and pi0/pi0.5 via its piRL work** |
| piRL (arXiv 2510.25889) | PPO over an ODE→SDE reformulation | sparse binary | **flow-matching**: pi0, pi0.5. The published fix for the log-prob problem |
| VLA-RFT (arXiv 2510.00406) | GRPO via a learned per-step variance head | dense, from a world model | **flow-matching**: VLA-Adapter |
| ConRFT (arXiv 2502.05450) | offline BC+Q, then online consistency-policy | learned Q + human intervention | Octo (diffusion head); real-robot, not sim |
| `conditioning-on-advantage` | no policy gradient at all | sparse per-episode outcome | **flow-matching**: the SmolVLA-shaped option — see that skill |

**Only the reference-backend row is Executor work.** Every other row is a separate
checkout with no entry point in this repo, so it is **Implementer** work via
`writing-new-scripts` / `preparing-runtime` — the round brief must carry the target
repo URL from the Evidence block below, and the round's deliverable is a working
integration, not a metric. Do not vendor those repos. **Reference backend (LeRobot-native):**
`pip install -e ".[hilserl]"`; `python -m lerobot.rl.learner --config_path <cfg>` and
`python -m lerobot.rl.actor --config_path <cfg>`, with reward from a trainable
`RewardClassifierConfig` (vision success detector) or a keypress.

## Mutates
Policy weights — writes RL-fine-tuned [checkpoint]s in a fresh [train_dir] lineage. The champion is untouched.

## Validation
Score the RL checkpoint against the [noise band] like any other round; run it isolated for attribution.

## Rollback
RL produces a new lineage, so the champion still stands: on a confirmed regression use `reverting-to-champion`, or keep partial gains with `souping-task-vectors`.

## Watch out
- Needs a reward/env; without one this is not runnable — harvest+label first.
- RL is expensive and **higher-variance than SFT** — budget [time budget] generously and keep it in its own round.
- RL optimizes the reward, not the task: a mis-specified or gameable reward invites reward-hacking (policy learns to trip the success detector). Gate the result on the locked `[acceptance gate]` and `[measurement integrity]`, never on the RL reward alone.
- It is the one lever that can invent motor behavior absent from the demos (SimpleVLA-RL reports LIBERO avg 91.0→99.1 and LIBERO-Long 86.5→98.5, discovering a novel "pushcut"); reach for it when the failure is a *capability* gap, not staleness (which `tuning-action-horizon` already covers).
- **None of these recipes has been demonstrated on SmolVLA.** The reference backend's policy is flow-matching, so the applicable columns are `conditioning-on-advantage`, piRL, and VLA-RFT — and all three were published on pi0/pi0.5/VLA-Adapter, not SmolVLA. Treat a SmolVLA application as an original experiment.
- This repo does not vendor LeRobot or any external RL repo: confirm the entry points (`.[hilserl]`, `lerobot.rl.learner`/`actor`) and every external repo's scripts and flags against the **installed commit** before relying on them. RLinf in particular is a fast-moving multi-algorithm mono-repo whose README claims outrun its releases — spot-check that the algorithm/backbone pair you need is actually present.

## Evidence
<!-- Upstream: github.com/huggingface/lerobot (hilserl/tdmpc, docs huggingface.co/docs/lerobot/hilserl);
     github.com/PRIME-RL/SimpleVLA-RL (arxiv 2509.09674); github.com/RLinf/RLinf (arxiv 2510.06710,
     and piRL arxiv 2510.25889); github.com/Ariostgx/ript-vla (arxiv 2505.17016);
     github.com/cccedric/conrft (arxiv 2502.05450); github.com/OpenHelix-Team/VLA-RFT (arxiv 2510.00406);
     github.com/rail-berkeley/hil-serl (arxiv 2410.21845). Commit: unpinned.
     Compatibility: see the recipe table's policy-class column — token-VLA recipes do NOT run on a
     flow-matching action expert. Permissions/mutation scope: writes new checkpoints only.
     Reviewer: unreviewed. -->
- none — original, offline 2026-07-19. No logged round yet; candidate. Record the first round's isolated
  delta ± band, seeds, task, hardware, GPU-hours, and verdict here (positive and negative) when run.
