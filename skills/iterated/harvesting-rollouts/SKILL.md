---
name: harvesting-rollouts
description: Autonomously rolls out the current policy to GENERATE new trajectories and logs their env rewards into the training dataset (a self-generated data flywheel), instead of depending only on human demos. Use when the policy fails states thinly covered by the demos and more on-distribution data is needed without teleoperation; when no env reward exists it records episodes and flags them for labeling.
metadata:
  lifecycle: candidate
  evidence_tier: candidate
  safety: mutating
---

# Harvest self-generated rollouts into the dataset

## Prerequisites
A deployable [checkpoint]; an env or real rig to roll out in; a target dataset repo to append to. Snapshot the dataset first — this appends to it.

## Do
Deploy the policy to record its own rollouts continuously. Reference backend (LeRobot-native): `lerobot-rollout --strategy.type=sentry --strategy.upload_every_n_episodes=5 --policy.path={checkpoint} --dataset.repo_id=<user/dataset> --duration=<seconds>` (`sentry` = continuous autonomous record + auto-upload, built for large-scale data collection; `dagger` adds human-in-the-loop). Store the env reward as a `next.reward`/`reward` feature in the dataset's `features` at `LeRobotDataset.create(...)`, mirroring LeRobot's own RL `Transition` schema (`lerobot/rl/buffer.py`). **No env reward** → record episodes anyway, then attach labels: keypress success/fail in HIL-SERL record mode, or `annotating-data`, or score post-hoc with `scoring-with-reward-model`.

## Mutates
The training dataset — appends episodes (and reward/label columns).

## Validation
`meta/info.json` episode count increased by the expected K; new episodes visualize sanely (`lerobot-dataset-viz`); each new episode carries a reward or is filed for labeling. Then it feeds a `continuing-training`, `reinforcing-with-rl`, or `conditioning-on-advantage` round — the metric moves there, not here. `conditioning-on-advantage` is the usual consumer for a flow-matching policy, and it wants **per-episode outcomes plus any expert corrections**, so record corrections as episodes rather than discarding them.

## Rollback
Restore the pre-run dataset snapshot, or drop the appended episode indices with `curating-dataset` (quoted `--dataset.episodes=[...]`).

## Watch out
- Autonomous rollouts inherit the policy's own biases — a narrow policy harvests narrow data (distribution collapse). Vary initial states/scenes; interleave with diverse resets (cf. SOAR's VLM task proposer).
- A rewardless or mislabeled dataset silently teaches the wrong thing — never train on unlabeled harvested episodes; the label/reward is the whole point.
- Real-robot autonomous rollout is unsupervised motion — gate on hardware safety (`checking-hardware`) and supervise.
- This repo does not vendor LeRobot: confirm `lerobot-rollout` and `--strategy.type=sentry` exist in the installed LeRobot version before relying on them (CLI/flag names drift across releases).

## Evidence
<!-- Upstream: github.com/huggingface/lerobot (lerobot-rollout, docs huggingface.co/docs/lerobot/il_robots;
     dataset schema huggingface.co/docs/lerobot/lerobot-dataset-v3). Method refs: auto-improvement.github.io
     (SOAR), robofume.github.io (RoboFuME reward classifier). Commit: unpinned.
     Compatibility: LeRobot rollout tooling + LeRobotDataset v3. Permissions/mutation scope: appends dataset
     episodes/labels only. Reviewer: unreviewed. -->
- none — original, offline 2026-07-19. No logged round yet; candidate. Record K episodes harvested, reward
  coverage, downstream metric delta when the harvested data is trained on, seeds, and cost here when run.
