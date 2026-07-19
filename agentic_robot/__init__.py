"""agentic-robot — a small, deterministic control-plane reference implementation.

This package does NOT run the training loop; that is the LLM controller's job
(see robot_agentic_training_flow.md). It implements only the deterministic
control-plane operations an operator or the controller can lean on: objective
validation, evidence hashing, an append-only event ledger with atomic writes,
metric-vector scoring, and recovery/replay checks (wrapping recovery.replay_checker).
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
