"""Deterministic metric parsing and scoring.

The controller parses eval_info.json itself every round (flow Invariant 3:
"Progress is measured, never asserted"). These helpers make that parse and the
comparison deterministic and shared, including the optional acceptance metric
vector (a locked gate, kept separate from the single optimization metric).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_COMPARATORS = {
    ">=": lambda v, t: v >= t,
    ">": lambda v, t: v > t,
    "<=": lambda v, t: v <= t,
    "<": lambda v, t: v < t,
}


def parse_metric(eval_info: dict[str, Any], metric_path: str) -> float:
    """Read a dotted metric_path (e.g. 'overall.pc_success') from eval_info.

    Raises KeyError if any path segment is missing and ValueError if the leaf is
    not numeric.
    """

    node: Any = eval_info
    for segment in metric_path.split("."):
        if not isinstance(node, dict) or segment not in node:
            raise KeyError(f"metric_path {metric_path!r} not found at segment {segment!r}")
        node = node[segment]
    if isinstance(node, bool) or not isinstance(node, (int, float)):
        raise ValueError(f"metric_path {metric_path!r} resolved to a non-numeric value {node!r}")
    return float(node)


def compare(value: float, comparison: str, target: float) -> bool:
    """Apply one of the four objective comparison operators."""

    try:
        return _COMPARATORS[comparison](value, target)
    except KeyError:
        raise ValueError(f"unknown comparison operator {comparison!r}") from None


@dataclass(frozen=True)
class MetricResult:
    name: str
    value: float | None
    comparison: str
    target: float
    passed: bool
    detail: str = ""


def acceptance_report(eval_info: dict[str, Any], acceptance: dict[str, Any]) -> list[MetricResult]:
    """Score an eval_info against the acceptance metric vector.

    A missing metric is a failure (value None) — the gate never passes on absent
    evidence.
    """

    results: list[MetricResult] = []
    for name, spec in acceptance.items():
        comparison = spec["comparison"]
        target = float(spec["target"])
        try:
            value = parse_metric(eval_info, name)
        except (KeyError, ValueError) as exc:
            results.append(MetricResult(name, None, comparison, target, False, str(exc)))
            continue
        passed = compare(value, comparison, target)
        results.append(MetricResult(name, value, comparison, target, passed))
    return results


def acceptance_passed(results: list[MetricResult]) -> bool:
    """The gate holds only when every metric in the vector is present and passing."""

    return bool(results) and all(r.passed for r in results)
