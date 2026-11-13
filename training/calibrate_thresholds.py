"""Calibrate a conservative abstention policy on validation data only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import math


def calibrate_thresholds(labels, probabilities, *, min_coverage=0.80):
    """Choose score/margin thresholds maximizing selective accuracy at min coverage.

    This is a validation-set operating-point selection, not probability
    calibration and not a safety guarantee. The held-out test set is never read.
    """
    if not 0 < min_coverage <= 1:
        raise ValueError("min_coverage muss in (0, 1] liegen.")
    if len(labels) != len(probabilities) or not labels:
        raise ValueError("Labels und Wahrscheinlichkeiten müssen gleich lang und nicht leer sein.")

    confidence, margins, correct = [], [], []
    for truth, row in zip(labels, probabilities):
        values = [float(x) for x in row]
        if not values or any(not math.isfinite(x) or x < 0 for x in values):
            raise ValueError("Wahrscheinlichkeiten müssen endlich und nicht-negativ sein.")
        total = sum(values)
        if total <= 0:
            raise ValueError("Jede Wahrscheinlichkeitszeile muss eine positive Summe haben.")
        values = [x / total for x in values]
        order = sorted(range(len(values)), key=values.__getitem__, reverse=True)
        first = values[order[0]]
        second = values[order[1]] if len(order) > 1 else 0.0
        confidence.append(first)
        margins.append(first - second)
        correct.append(order[0] == int(truth))

    # A compact, deterministic grid avoids overfitting thresholds to individual
    # validation samples. Both conditions must be met to accept a prediction.
    grid = [i / 20 for i in range(21)]
    best = None
    total = len(labels)
    for score_threshold in grid:
        for margin_threshold in grid:
            accepted = [i for i in range(total)
                        if confidence[i] >= score_threshold and margins[i] >= margin_threshold]
            coverage = len(accepted) / total
            if coverage + 1e-12 < min_coverage:
                continue
            accuracy = sum(correct[i] for i in accepted) / len(accepted)
            candidate = (accuracy, coverage, score_threshold, margin_threshold, len(accepted))
            if best is None or candidate[:2] > best[:2]:
                best = candidate

    if best is None:
        raise RuntimeError("Kein Schwellenwertpaar erfüllt die Mindestabdeckung.")
    accuracy, coverage, score_threshold, margin_threshold, accepted_count = best
    return {
        "min_score": score_threshold,
        "min_margin": margin_threshold,
        "validation_samples": total,
        "accepted_predictions": accepted_count,
        "coverage": coverage,
        "accuracy_on_accepted": accuracy,
        "target_min_coverage": min_coverage,
        "selection_method": "grid_search_max_selective_accuracy_at_minimum_coverage",
        "warning": "Validation operating point only; scores are not calibrated safety probabilities.",
    }


def main():
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from torchvision import datasets, models, transforms

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/signs/val"))
    parser.add_argument("--model-dir", type=Path, default=Path("artifacts/sign_classifier"))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--min-coverage", type=float, default=0.80)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size muss positiv sein.")

    metadata_path = args.model_dir / "metadata.json"
    weights_path = args.model_dir / "best_model.pth"
    if not args.data.is_dir() or not metadata_path.is_file() or not weights_path.is_file():
        raise SystemExit("Validierungsdaten oder trainiertes Modell/Metadaten fehlen.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    classes = metadata.get("classes")
    if not isinstance(classes, list) or not classes:
        raise SystemExit("Ungültige Klassenliste.")

    size = int(metadata.get("image_size", 224))
    dataset = datasets.ImageFolder(args.data, transform=transforms.Compose([
        transforms.Resize((size, size)), transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ]))
    if dataset.classes != classes or not len(dataset):
        raise SystemExit("Validierungsklassen stimmen nicht überein oder Datensatz ist leer.")

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
    model.eval()
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    labels, probabilities = [], []
    with torch.inference_mode():
        for images, targets in loader:
            probs = torch.softmax(model(images), dim=1)
            labels.extend(targets.tolist())
            probabilities.extend(probs.tolist())

    result = calibrate_thresholds(labels, probabilities, min_coverage=args.min_coverage)
    output = args.model_dir / "calibrated_thresholds.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Schwellenwerte gespeichert: {output}")


if __name__ == "__main__":
    main()
