---
name: evicting-hf-dataset-caches
description: Frees disk by deleting regenerable HuggingFace datasets builder caches (parquet arrow conversions) that no live process holds. Use when a training launch needs a new ~dataset-sized arrow cache and free disk is insufficient, before touching any source data.
metadata:
  lifecycle: candidate
  safety: reversible
---

# Evict dead HF datasets builder caches

## Prerequisites
`~/.cache/huggingface/datasets/parquet/default-*` entries exist; `lsof` available; the caches' SOURCE datasets still exist on disk (caches are pure derived artifacts and rebuild on demand).

## Do
For each `default-*` dir: skip if any process holds files in it (`lsof +D <dir>`); skip if <1G; otherwise record size+mtime to a manifest in the run's evidence dir and `rm -rf` it. Re-check `lsof` immediately before each removal.

## Mutates
Shared HF datasets cache (derived artifacts only — never source datasets, never checkpoints).

## Validation
`df` shows the expected space freed; every skipped entry was genuinely held (lsof) or small; manifest written.

## Rollback
None needed — caches rebuild automatically on the next unfiltered dataset load (costs one rebuild pass).

## Watch out
- A LIVE training's cache being deleted would not crash it (Linux keeps open mmaps alive) but frees no space and forces a rebuild later — the lsof guard is mandatory, not optional.
- `Dataset.from_parquet` builds the cache FILTERED-size when `--dataset.episodes` is set; unfiltered loads need ~full-dataset-size free. Budget before launch.

## Evidence
- run _70_002 round 1 (2026-07-15): evicted 97G across 8 dead-run caches (manifest in round_1/evidence/); unblocked a 30G arrow-cache training launch on a 96%-full disk; sibling run and external job caches lsof-skipped, unharmed.
