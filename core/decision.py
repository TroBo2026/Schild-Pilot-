"""Conservative decision policy for traffic-sign classifier outputs.

This module does not make model scores calibrated probabilities. It only
implements an explicit abstention rule for a vector of non-negative scores.
"""
from __future__ import annotations

import math
from typing import Iterable


def decide_prediction(
    scores: Iterable[float],
    class_names: list[str],
    *,
    min_score: float = 0.65,
    min_margin: float = 0.10,
) -> dict[str, object]:
    """Return an accepted label or abstain when the result is ambiguous.

    Scores are normalized to sum to one. They must be finite and non-negative.
    The returned score is a model score, not a calibrated safety probability.
    """
    values = [float(value) for value in scores]
    if not values or len(values) != len(class_names):
        raise ValueError("Scores und Klassennamen müssen gleich lang und nicht leer sein.")
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("Scores müssen endlich und nicht-negativ sein.")
    if not (0.0 <= min_score <= 1.0):
        raise ValueError("min_score muss zwischen 0 und 1 liegen.")
    if not (0.0 <= min_margin <= 1.0):
        raise ValueError("min_margin muss zwischen 0 und 1 liegen.")

    total = sum(values)
    if total <= 0:
        raise ValueError("Die Summe der Scores muss größer als null sein.")

    normalized = [value / total for value in values]
    ranked = sorted(range(len(normalized)), key=normalized.__getitem__, reverse=True)
    best_index = ranked[0]
    best_score = normalized[best_index]
    second_score = normalized[ranked[1]] if len(ranked) > 1 else 0.0
    margin = best_score - second_score

    accepted = best_score >= min_score and margin >= min_margin
    return {
        "status": "accepted" if accepted else "uncertain",
        "label": class_names[best_index] if accepted else None,
        "candidate": class_names[best_index],
        "model_score": best_score,
        "margin": margin,
        "reason": "thresholds_met" if accepted else (
            "score_too_low" if best_score < min_score else "top_classes_too_close"
        ),
    }
