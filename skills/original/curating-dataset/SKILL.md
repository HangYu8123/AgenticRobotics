---
name: curating-dataset
description: Inspect, clean, augment, or restrict the training dataset to the evaluation suite. Use when you suspect the data rather than the model, including when a broad training mixture dilutes the suite the objective measures.
metadata:
  lifecycle: validated
  safety: irreversible
---

# Inspect, clean, or augment the dataset

## When to use

You suspect the data, not the model. Always cheaper than a training run.

## Prerequisites

The dataset's repo id, and a suspicion grounded in something concrete (a viz
pass, a `diagnosing-qualitatively` finding) — not a hunch. Snapshot the dataset
dir before any destructive operation.

## Do

```bash
# look at an episode
uv run lerobot-dataset-viz --repo-id <user/dataset> --episode-index 0
# drop/fix episodes (operations: delete_episodes, split, merge,
#                    remove_feature, modify_tasks, convert_image_to_video)
uv run lerobot-edit-dataset --repo_id=<user/dataset> \
  --operation.type=delete_episodes --operation.episode_indices="[3,7]"
uv run python src/lerobot/scripts/augment_dataset_quantile_stats.py --help
```

Dataset schema, frame counts and fps come from the dataset's own
`meta/info.json` (or `LeRobotDatasetMetadata`), not from a CLI flag.

To specialize without rewriting the dataset, run `continuing-training` with
the evaluated suite's episode ids as one quoted argument:

```bash
uv run lerobot-train \
  --config_path=<train_dir>/checkpoints/last/pretrained_model/train_config.json \
  --resume=true --steps=<target> \
  '--dataset.episodes=[<evaluated suite episode ids>]'
```

Use the full resume preflight from `continuing-training`. Confirm from the log
that `dataset.num_episodes` and `num_frames` shrink to the intended subset; if
they do not, the shell consumed or split the list argument.

## Mutates

Dataset edits mutate the training dataset in place. Viewing
(`lerobot-dataset-viz`) mutates nothing. Suite specialization leaves the
dataset unchanged and writes new checkpoints to the training lineage.

## Validation

For dataset edits, `meta/info.json` reflects the edit (episode/frame counts)
and an edited episode passes a visual spot-check. For suite specialization,
the resolved training log shows the intended episode/frame subset and the
objective's gate evaluates the resulting checkpoint.

## Rollback

Deleting or merging episodes has no tool-level undo: restore the pre-edit
snapshot, or treat the edit as irreversible. Suite specialization leaves the
dataset and prior champion untouched; roll back by returning the lineage to
that champion.

## Watch out

`lerobot-info` is **not** a dataset tool — it parses no arguments at all and
just prints host/torch/CUDA info, so `lerobot-info --repo-id=...` *succeeds
while silently ignoring the flag*. Likewise
`augment_dataset_quantile_stats.py` is not a `lerobot-*` entry point and must
be run as a module path. Editing a dataset invalidates every metric measured
against the old one: re-baseline after.

## Evidence
- Round 1 (smolvla_libero10_80_002, 2026-07-14): filtered `HuggingFaceVLA/libero` (1693 eps / 40 tasks, all 4 suites)
  down to the 379 episodes / 10 tasks of the target suite via `--dataset.episodes=[0..378]`, bundled with a
  `continuing-training` resume (60k->75k, batch 32). **35.0 -> 48.0 pc_success on libero_10 (+13.0, n=100).**
  Rationale that picked it: the eval-video diagnosis showed the defect was two-grasp composition (23% vs 52%
  one-grasp), and 3 of the 4 LIBERO suites are single-grasp — the mixture was actively teaching
  "grasp the salient thing, place it, done". After: two-grasp 23%->32%, one-grasp 52%->72%.
  **Specialize on the suite the objective actually measures** when the training mixture dilutes it.
  (Delta covers the whole bundle — the filter and the extra steps are not separately attributed.)

- Round 2 (smolvla_libero10_80_001): resumed 60k->100k on the 379 libero_10
  episodes instead of the merged four-suite mixture. **39.0 -> 49.0
  pc_success (+10.0)**, with both previously zero-scoring tasks recovering.
  The unscored 10k-step curve was 39.0, 44.0, 46.0, 48.0, 49.0, showing that
  the gain saturated rather than continuing at its initial rate.

- Origin: OPTIONS.md O5 (seed option).
