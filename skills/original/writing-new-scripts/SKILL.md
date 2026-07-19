---
name: writing-new-scripts
description: Write a new script when the behavior a round needs does not exist in the repo — data augmentation, curriculum scheduling, reward shaping, a custom eval, a metric extractor. Use when no existing skill or lerobot CLI covers the need.
metadata:
  lifecycle: candidate
  safety: mutating
---

# Write a new script

## When to use

The behavior you need does not exist in this repo or the LeRobot repo's CLIs.

## Prerequisites

Confirmed (index scan, `lerobot-* --help`) that no existing skill or CLI covers
the need.

## Do

Write it — data augmentation, curriculum scheduling, reward shaping, a custom
eval, a metric extractor. Put it under the run dir, not in `src/`, unless it is
genuinely reusable. If the script embodies a reusable behavior, register it as
a new skill afterwards (see `skills/index.md` §Creating a new skill).

## Mutates

Adds files under the run dir (or `src/`, only when genuinely reusable) — plus
whatever the script itself touches: state that in the [worker result].

## Validation

Run it on a case with a known answer before trusting anything it produces.

## Rollback

Delete the script; its outputs stay under the run dir.

## Watch out

A new script is new surface area. It can be buggy in a way that *fakes*
progress (e.g. an eval that scores the training episodes). Validate it before
you trust a metric it produced.

## Evidence

- Origin: OPTIONS.md O9 (seed option); not yet exercised in a logged round.
