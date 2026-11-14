"""Dependency-free precision/recall metrics for object-detection pilots."""
from __future__ import annotations

import math
from typing import Sequence


def _box_xyxy(value: object) -> tuple[float, float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError("Box muss vier xyxy-Koordinaten enthalten.")
    coords = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in coords):
        raise ValueError("Box-Koordinaten müssen endlich sein.")
    x1, y1, x2, y2 = coords
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Box muss eine positive Fläche haben.")
    return x1, y1, x2, y2


def box_iou(box_a: object, box_b: object) -> float:
    """Intersection over Union for two [x1, y1, x2, y2] boxes."""
    ax1, ay1, ax2, ay2 = _box_xyxy(box_a)
    bx1, by1, bx2, by2 = _box_xyxy(box_b)
    left, top = max(ax1, bx1), max(ay1, by1)
    right, bottom = min(ax2, bx2), min(ay2, by2)
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return intersection / (area_a + area_b - intersection)


def _image_counts(
    predictions: Sequence[dict],
    ground_truth: Sequence[dict],
    *,
    score_threshold: float,
    iou_threshold: float,
) -> tuple[int, int, int]:
    prepared_predictions = []
    for prediction in predictions:
        if not isinstance(prediction, dict):
            raise ValueError("Jede Vorhersage muss ein Objekt sein.")
        score = float(prediction["score"])
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError("Vorhersagescores müssen endlich und zwischen 0 und 1 liegen.")
        prepared_predictions.append({
            "box": _box_xyxy(prediction["box"]),
            "label": int(prediction["label"]),
            "score": score,
        })

    prepared_truth = []
    for truth in ground_truth:
        if not isinstance(truth, dict):
            raise ValueError("Jede Ground-Truth-Annotation muss ein Objekt sein.")
        prepared_truth.append({
            "box": _box_xyxy(truth["box"]),
            "label": int(truth["label"]),
        })

    candidates = [
        prediction for prediction in prepared_predictions
        if prediction["score"] >= score_threshold
    ]
    candidates.sort(key=lambda item: item["score"], reverse=True)

    matched: set[int] = set()
    true_positives = 0
    false_positives = 0
    for prediction in candidates:
        best_index = None
        best_iou = 0.0
        for index, truth in enumerate(prepared_truth):
            if index in matched or truth["label"] != prediction["label"]:
                continue
            overlap = box_iou(prediction["box"], truth["box"])
            if overlap > best_iou:
                best_index, best_iou = index, overlap
        if best_index is not None and best_iou >= iou_threshold:
            matched.add(best_index)
            true_positives += 1
        else:
            false_positives += 1

    false_negatives = len(prepared_truth) - len(matched)
    return true_positives, false_positives, false_negatives


def evaluate_thresholds(
    predictions_by_image: Sequence[Sequence[dict]],
    ground_truths_by_image: Sequence[Sequence[dict]],
    *,
    score_thresholds: Sequence[float] = (0.01, 0.025, 0.05, 0.10, 0.25, 0.50),
    iou_threshold: float = 0.50,
) -> dict:
    """Sweep score thresholds; choose an operating point on validation data.

    This is a compact diagnostic, not COCO mAP. Callers must only use the
    selected threshold on a separate test split after selecting it on val.
    """
    if len(predictions_by_image) != len(ground_truths_by_image):
        raise ValueError("Vorhersagen und Ground Truth müssen gleich viele Bilder enthalten.")
    if not math.isfinite(float(iou_threshold)) or not 0.0 <= float(iou_threshold) <= 1.0:
        raise ValueError("IoU-Schwelle muss zwischen 0 und 1 liegen.")
    thresholds = [float(value) for value in score_thresholds]
    if not thresholds:
        raise ValueError("Mindestens eine Score-Schwelle ist erforderlich.")
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in thresholds):
        raise ValueError("Score-Schwellen müssen endlich und zwischen 0 und 1 liegen.")

    results = []
    for threshold in dict.fromkeys(thresholds):
        tp = fp = fn = 0
        for predictions, ground_truth in zip(predictions_by_image, ground_truths_by_image):
            image_tp, image_fp, image_fn = _image_counts(
                predictions, ground_truth,
                score_threshold=threshold,
                iou_threshold=float(iou_threshold),
            )
            tp += image_tp
            fp += image_fp
            fn += image_fn
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        results.append({
            "score_threshold": threshold,
            "iou_threshold": float(iou_threshold),
            "images_evaluated": len(predictions_by_image),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })

    # Prefer higher precision, then a stricter threshold when F1 ties.
    best = max(results, key=lambda item: (
        item["f1"], item["precision"], item["score_threshold"]
    ))
    return {"best": best, "thresholds": results}
