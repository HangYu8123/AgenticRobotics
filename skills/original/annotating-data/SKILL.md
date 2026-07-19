---
name: annotating-data
description: Annotate or re-label dataset episodes with lerobot-annotate for multi-stage or language-conditioned tasks. Use when reward or success labels are suspected wrong or missing; label mutation is irreversible, so snapshot the labels first and spot-check against video after.
metadata:
  lifecycle: candidate
  safety: irreversible
---

# Annotate or re-label episodes

> Re-registered offline 2026-07-15: the original registration (untracked, O7)
> was deleted from the working tree the same day with no update_logs entry;
> this body was re-authored from the pre-deletion scripts_overview row and the
> `context/` index snapshot.

## Prerequisites

A multi-stage or language-conditioned task whose reward/success labels are
suspected wrong, or that needs new sub-task labels; the dataset accessible to
`lerobot-annotate`.

## Do

Snapshot the current labels first (copy the annotation/metadata files aside
under the run dir). Then run `lerobot-annotate` against the dataset and apply
the corrected labels.

## Mutates

The dataset's label/annotation metadata — **irreversibly** once the snapshot
is skipped.

## Validation

Spot-check a sample of re-labeled episodes against their videos: the new
labels must match what the video actually shows.

## Rollback

Only via the pre-run snapshot; without it, none known — treat as irreversible.

## Watch out

- Label mutation is irreversible; never skip the snapshot.
- Wrong success labels poison every later training and eval round that
  consumes them — validate before the next training action, not after.

## Evidence

- Origin: OPTIONS.md O7; not yet exercised in a logged round.
- 2026-07-15: deleted from the working tree undocumented; re-authored offline
  per the note above.
