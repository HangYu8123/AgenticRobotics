"""Pure consistency checks for decoded durable round-state mappings."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any


_COMMIT_PHASES = (
    "READY_TO_SCORE",
    "SCORE_APPLIED",
    "REGISTRATION_COMMITTED",
    "CLEANUP_COMPLETE",
    "LEDGER_COMMITTED",
    "ROUND_ADVANCED",
)
_PHASE_INDEX = {phase: index for index, phase in enumerate(_COMMIT_PHASES)}
_PRE_SCORE_PHASES = {"ROUND_START", "EXECUTING", "REMEASURE_ONLY"}
_KNOWN_PHASES = _PRE_SCORE_PHASES | set(_COMMIT_PHASES)
_RECEIPT_MIN_PHASE = {
    "score_applied": 1,
    "registration_committed": 2,
    "ledger_committed": 4,
    "round_advanced": 5,
}
_WAIT_IDENTITY_FIELDS = (
    "owner",
    "launch_key",
    "event_trigger_key",
    "fallback_trigger_key",
    "execution_lease",
    "cmd_sha256",
)
_MEASUREMENT_IDENTITY_FIELDS = ("wait_generation", "checkpoint", "eval_dir", "command")
_WAIT_STATUS_INDEX = {
    "PREPARED": 0,
    "WAITING": 1,
    "CLAIMED": 2,
}


def _error(message: str) -> None:
    raise ValueError(message)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _required_mapping(state: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    value = state.get(name)
    if not isinstance(value, Mapping):
        _error(f"{name} must be a mapping")
    return value


def _required_nonnegative_int(state: Mapping[str, Any], name: str) -> int:
    value = state.get(name)
    if not _is_int(value) or value < 0:
        _error(f"{name} must be a non-negative integer")
    return value


def _generation_number(key: object, label: str) -> int:
    if not isinstance(key, str) or not key.isascii() or not key.isdigit() or key.startswith("0"):
        _error(f"{label} key {key!r} must be a normalized positive decimal string")
    value = int(key)
    if value < 1:
        _error(f"{label} key {key!r} must be positive")
    return value


def _phase(state: Mapping[str, Any]) -> str:
    inputs = _required_mapping(state, "round_log_inputs")
    phase = inputs.get("phase")
    if not isinstance(phase, str) or not phase:
        _error("round_log_inputs.phase must be a non-empty string")
    if phase not in _KNOWN_PHASES:
        _error(f"unknown round_log_inputs.phase {phase!r}")
    return phase


def _prepared_block(prepared: Mapping[str, Any]) -> tuple[bytes, int, str]:
    if not isinstance(prepared, Mapping):
        _error("prepared ledger block must be a mapping")
    block_text = prepared.get("block")
    if not isinstance(block_text, str):
        _error("prepared.block must be a string")
    block = block_text.encode("utf-8")
    byte_length = prepared.get("byte_length")
    if not _is_int(byte_length) or byte_length != len(block) or byte_length < 1:
        _error("prepared.byte_length does not match the UTF-8 block length")
    block_digest = prepared.get("block_sha256")
    if block_digest != hashlib.sha256(block).hexdigest():
        _error("prepared.block_sha256 does not match the UTF-8 block")
    offset = prepared.get("pre_append_offset")
    if not _is_int(offset) or offset < 0:
        _error("prepared.pre_append_offset must be a non-negative integer")
    prefix_digest = prepared.get("pre_append_prefix_sha256")
    if (
        not isinstance(prefix_digest, str)
        or len(prefix_digest) != 64
        or any(character not in "0123456789abcdef" for character in prefix_digest)
    ):
        _error("prepared.pre_append_prefix_sha256 must be a lowercase sha256 digest")
    return block, offset, prefix_digest


def _wait_maps(state: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    active = _required_mapping(state, "active_waits")
    completed = _required_mapping(state, "completed_waits")
    overlap = set(active) & set(completed)
    if overlap:
        _error(f"wait generations appear in both active and completed maps: {sorted(overlap)}")
    return active, completed


def _validate_commit_phase(state: Mapping[str, Any], phase: str) -> None:
    phase_index = _PHASE_INDEX.get(phase)
    if phase_index is None:
        return

    receipts: dict[str, str] = {}
    for field, minimum_phase in _RECEIPT_MIN_PHASE.items():
        value = state.get(field)
        if value is not None and (not isinstance(value, str) or not value):
            _error(f"{field} must be null or a non-empty string")
        if value is not None:
            if phase_index < minimum_phase:
                _error(f"{field} is committed before phase {_COMMIT_PHASES[minimum_phase]}")
            receipts[field] = value
        elif phase_index >= minimum_phase:
            _error(f"phase {phase} requires {field}")

    commit_keys = set(receipts.values())
    if len(commit_keys) > 1:
        _error("committed receipt fields do not name one commit key")

    cleanup = state.get("cleanup")
    if cleanup is not None and not isinstance(cleanup, Mapping):
        _error("cleanup must be null or a mapping")
    cleanup_complete = isinstance(cleanup, Mapping) and cleanup.get("complete") is True
    if cleanup_complete:
        if phase_index < _PHASE_INDEX["CLEANUP_COMPLETE"]:
            _error("cleanup is complete before phase CLEANUP_COMPLETE")
        if cleanup.get("commit_key") not in commit_keys:
            _error("cleanup does not name the committed score key")
    elif phase_index >= _PHASE_INDEX["CLEANUP_COMPLETE"]:
        _error(f"phase {phase} requires complete cleanup")

    if phase == "ROUND_ADVANCED":
        current_round = _required_nonnegative_int(state, "current_round")
        next_round = _required_nonnegative_int(state, "next_round")
        if next_round != current_round + 1:
            _error("ROUND_ADVANCED requires next_round == current_round + 1")
        if state.get("status") != "COMPLETED":
            _error("ROUND_ADVANCED requires status COMPLETED")


def _validate_state(state: Mapping[str, Any]) -> None:
    if not isinstance(state, Mapping):
        _error("each replay state must be a mapping")
    if not _is_int(state.get("schema_version")) or state["schema_version"] != 1:
        _error("schema_version must be 1")
    if not isinstance(state.get("status"), str) or not state["status"]:
        _error("status must be a non-empty string")
    _required_nonnegative_int(state, "current_round")
    _required_nonnegative_int(state, "next_round")
    if not isinstance(state.get("objective_digest"), str) or not state["objective_digest"]:
        _error("objective_digest must be a non-empty string")
    run_id = state.get("run_id")
    if run_id is not None and (not isinstance(run_id, str) or not run_id):
        _error("run_id must be a non-empty string when present")
    _required_mapping(state, "score_state")

    generation_high_water = _required_nonnegative_int(state, "generation_high_water")
    measurement_high_water = _required_nonnegative_int(
        state, "measurement_generation_high_water"
    )
    active, completed = _wait_maps(state)
    _required_mapping(state, "execution_leases")
    _required_mapping(state, "phase_transitions")
    measurements = _required_mapping(state, "measurement_attempts")

    waits: dict[str, Mapping[str, Any]] = {}
    for label, wait_map in (("active_waits", active), ("completed_waits", completed)):
        for key, record in wait_map.items():
            generation = _generation_number(key, label)
            if generation > generation_high_water:
                _error(f"wait generation {generation} exceeds generation_high_water")
            if not isinstance(record, Mapping):
                _error(f"{label}[{key}] must be a mapping")
            if not isinstance(record.get("owner"), str) or not record["owner"]:
                _error(f"{label}[{key}].owner must be a non-empty string")
            if not isinstance(record.get("status"), str) or not record["status"]:
                _error(f"{label}[{key}].status must be a non-empty string")
            if record["status"] not in _WAIT_STATUS_INDEX:
                _error(f"{label}[{key}].status is not a known wait status")
            for field in _WAIT_IDENTITY_FIELDS:
                if field in record and not isinstance(record[field], str):
                    _error(f"{label}[{key}].{field} must be a string")
            if label == "completed_waits" and record["status"] != "CLAIMED":
                _error(f"completed_waits[{key}].status must be CLAIMED")
            if label == "completed_waits" and (
                not isinstance(record.get("outcome"), str) or not record["outcome"]
            ):
                _error(f"completed_waits[{key}] must include a non-empty outcome")
            if label == "completed_waits":
                verification = record.get("verification")
                if not (
                    (isinstance(verification, str) and verification)
                    or (isinstance(verification, Mapping) and verification)
                ):
                    _error(
                        f"completed_waits[{key}] must include non-empty verification evidence"
                    )
            waits[key] = record

    for key, attempt in measurements.items():
        measurement = _generation_number(key, "measurement_attempts")
        if measurement > measurement_high_water:
            _error(
                f"measurement generation {measurement} exceeds "
                "measurement_generation_high_water"
            )
        if not isinstance(attempt, Mapping):
            _error(f"measurement_attempts[{key}] must be a mapping")
        for field in ("outcome", "checkpoint", "eval_dir", "command"):
            if field in attempt and not isinstance(attempt[field], str):
                _error(f"measurement_attempts[{key}].{field} must be a string")
        wait_generation = attempt.get("wait_generation")
        if not _is_int(wait_generation) or wait_generation < 1:
            _error(f"measurement_attempts[{key}].wait_generation must be a positive integer")
        wait = waits.get(str(wait_generation))
        if wait is None:
            _error(f"measurement {key} has no reciprocal wait {wait_generation}")
        if wait.get("owner") != f"measure:{key}":
            _error(f"wait {wait_generation} does not reciprocally own measurement {key}")

    for wait_key, wait in waits.items():
        owner = wait["owner"]
        if not owner.startswith("measure:"):
            continue
        measurement_key = owner.removeprefix("measure:")
        _generation_number(measurement_key, f"wait {wait_key} measurement owner")
        attempt = measurements.get(measurement_key)
        if not isinstance(attempt, Mapping):
            _error(f"measurement-owned wait {wait_key} has no measurement {measurement_key}")
        if attempt.get("wait_generation") != int(wait_key):
            _error(f"measurement-owned wait {wait_key} has a conflicting reciprocal binding")

    cleanup = state.get("cleanup")
    if cleanup is not None:
        if not isinstance(cleanup, Mapping):
            _error("cleanup must be null or a mapping")
        if not isinstance(cleanup.get("commit_key"), str) or not cleanup["commit_key"]:
            _error("cleanup.commit_key must be a non-empty string")
        if not isinstance(cleanup.get("complete"), bool):
            _error("cleanup.complete must be a boolean")

    prepared = state.get("prepared_ledger_block")
    if prepared is not None:
        _prepared_block(prepared)

    _validate_commit_phase(state, _phase(state))


def _preserves_fields(
    before: Mapping[str, Any], after: Mapping[str, Any], fields: Sequence[str], label: str
) -> None:
    for field in fields:
        if field in before and after.get(field) != before[field]:
            _error(f"{label} changed immutable field {field}")


def _validate_transition(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    before_wait_high = before["generation_high_water"]
    after_wait_high = after["generation_high_water"]
    before_measurement_high = before["measurement_generation_high_water"]
    after_measurement_high = after["measurement_generation_high_water"]
    if after_wait_high < before_wait_high:
        _error("generation_high_water decreased")
    if after_measurement_high < before_measurement_high:
        _error("measurement_generation_high_water decreased")

    before_run_id = before.get("run_id")
    if before_run_id is not None and after.get("run_id") != before_run_id:
        _error("run_id changed or was dropped across a replacement")

    before_round = before["current_round"]
    after_round = after["current_round"]
    if after_round < before_round or after_round > before_round + 1:
        _error("current_round must stay fixed or advance by one")
    same_round = before_round == after_round
    if not same_round:
        before_phase = _phase(before)
        after_phase = _phase(after)
        if before_phase != "ROUND_ADVANCED" or after_phase not in {
            "ROUND_START",
            "REMEASURE_ONLY",
        }:
            _error("a new round must start from ROUND_ADVANCED")
        if after_round != before["next_round"] or after["next_round"] != after_round + 1:
            _error("new-round numbering does not match the ROUND_ADVANCED tombstone")
        if after_wait_high != before_wait_high or after_measurement_high != before_measurement_high:
            _error("generation high-water marks changed during round initialization")
        if after.get("status") != "IN_PROGRESS":
            _error("a newly initialized round must have status IN_PROGRESS")
        if after.get("objective_digest") != before.get("objective_digest"):
            _error("objective_digest changed during round initialization")
        if after.get("score_state") != before.get("score_state"):
            _error("score_state changed during round initialization")
        for field in (
            "active_waits",
            "completed_waits",
            "execution_leases",
            "phase_transitions",
            "measurement_attempts",
        ):
            if after.get(field) != {}:
                _error(f"a newly initialized round must clear {field}")
        for field in (
            "score_snapshot",
            "score_applied",
            "registration_committed",
            "cleanup",
            "prepared_ledger_block",
            "ledger_committed",
            "round_advanced",
        ):
            if after.get(field) is not None:
                _error(f"a newly initialized round must clear {field}")

    before_active, before_completed = _wait_maps(before)
    after_active, after_completed = _wait_maps(after)
    before_waits = {**before_active, **before_completed}
    after_waits = {**after_active, **after_completed}

    for key in set(after_waits) - set(before_waits):
        if int(key) <= before_wait_high:
            _error(f"wait generation {key} was reused")
    for key in set(before_waits) & set(after_waits):
        _preserves_fields(
            before_waits[key], after_waits[key], _WAIT_IDENTITY_FIELDS, f"wait generation {key}"
        )
        if _WAIT_STATUS_INDEX[after_waits[key]["status"]] < _WAIT_STATUS_INDEX[
            before_waits[key]["status"]
        ]:
            _error(f"wait generation {key} status regressed")
    if same_round:
        for key in set(before_active) - set(after_active):
            if key not in after_completed:
                _error(f"active wait generation {key} was removed instead of atomically completed")
            if after_completed[key]["status"] != "CLAIMED":
                _error(f"active wait generation {key} moved before it was CLAIMED")
        for key in set(before_completed) - set(after_completed):
            _error(f"completed wait generation {key} disappeared within a round")

    before_measurements = _required_mapping(before, "measurement_attempts")
    after_measurements = _required_mapping(after, "measurement_attempts")
    for key in set(after_measurements) - set(before_measurements):
        if int(key) <= before_measurement_high:
            _error(f"measurement generation {key} was reused")
    for key in set(before_measurements) & set(after_measurements):
        _preserves_fields(
            before_measurements[key],
            after_measurements[key],
            _MEASUREMENT_IDENTITY_FIELDS,
            f"measurement generation {key}",
        )
    if same_round and set(before_measurements) - set(after_measurements):
        _error("measurement attempts disappeared within a round")

    if same_round:
        before_phase = _phase(before)
        after_phase = _phase(after)
        before_index = _PHASE_INDEX.get(before_phase)
        after_index = _PHASE_INDEX.get(after_phase)
        if before_index is None and after_index is not None and after_index != 0:
            _error("commit sequence must enter at READY_TO_SCORE")
        if before_index is not None:
            if after_index is None or after_index not in (before_index, before_index + 1):
                _error(f"invalid commit phase transition {before_phase} -> {after_phase}")
        for field in _RECEIPT_MIN_PHASE:
            previous = before.get(field)
            if previous is not None and after.get(field) != previous:
                _error(f"committed receipt {field} changed within a round")
        previous_cleanup = before.get("cleanup")
        if isinstance(previous_cleanup, Mapping) and previous_cleanup.get("complete") is True:
            if after.get("cleanup") != previous_cleanup:
                _error("completed cleanup changed within a round")


def check_replay(states: Sequence[Mapping[str, object]]) -> None:
    """Validate decoded snapshots and their deterministic replay transitions.

    The function does not parse, read, write, or migrate durable state files.
    """

    if isinstance(states, (str, bytes)) or not isinstance(states, Sequence) or not states:
        _error("states must be a non-empty sequence of mappings")
    for state in states:
        _validate_state(state)
    for before, after in zip(states, states[1:]):
        _validate_transition(before, after)


def recover_partial_append(ledger: bytes, prepared: Mapping[str, object]) -> bytes:
    """Repair one anchored partial UTF-8 block append, or return a complete append unchanged."""

    if not isinstance(ledger, bytes):
        _error("ledger must be bytes")
    if not isinstance(prepared, Mapping):
        _error("prepared must be a mapping")

    block, offset, prefix_digest = _prepared_block(prepared)
    if offset > len(ledger):
        _error("prepared.pre_append_offset is outside the ledger")
    prefix = ledger[:offset]
    if prefix_digest != hashlib.sha256(prefix).hexdigest():
        _error("ledger prefix does not match pre_append_prefix_sha256")

    tail = ledger[offset:]
    if tail == block:
        return ledger
    if not tail:
        _error("ledger has no non-empty partial append tail")
    if len(tail) >= len(block) or not block.startswith(tail):
        _error("ledger tail is not a strict prefix of the prepared block")
    return prefix + block
