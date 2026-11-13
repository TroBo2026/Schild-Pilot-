"""Evaluate a trained cropped-sign classifier on a separate ImageFolder test split.

Run from repository root:
    python -m training.evaluate_classifier --data data/signs/test
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

from core.decision import decide_prediction


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/signs/test"))
    parser.add_argument("--model-dir", type=Path, default=Path("artifacts/sign_classifier"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation"))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--min-score", type=float, default=0.45)
    parser.add_argument("--min-margin", type=float, default=0.10)
    args = parser.parse_args()

    if args.batch_size < 1:
        raise SystemExit("--batch-size muss positiv sein.")
    metadata_path = args.model_dir / "metadata.json"
    weights_path = args.model_dir / "best_model.pth"
    if not args.data.is_dir() or not metadata_path.is_file() or not weights_path.is_file():
        raise SystemExit("Testdaten oder trainiertes Modell/Metadaten fehlen.")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    classes = metadata.get("classes")
    if not isinstance(classes, list) or not classes:
        raise SystemExit("Ungültige Klassenliste in metadata.json.")
    dataset = datasets.ImageFolder(args.data, transform=transforms.Compose([
        transforms.Resize((int(metadata.get("image_size", 224)),) * 2),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ]))
    if dataset.classes != classes:
        raise SystemExit("Testklassen oder Klassenreihenfolge stimmen nicht mit dem Modell überein.")
    if len(dataset) == 0:
        raise SystemExit("Der Testdatensatz ist leer.")

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
    model.eval()
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    confusion = [[0 for _ in classes] for _ in classes]
    accepted = correct_accepted = 0
    total = 0
    abstained = 0
    with torch.inference_mode():
        for images, labels in loader:
            probabilities = torch.softmax(model(images), dim=1)
            for row, truth in zip(probabilities.tolist(), labels.tolist()):
                decision = decide_prediction(
                    row, classes, min_score=args.min_score, min_margin=args.min_margin
                )
                candidate = classes.index(decision["candidate"])
                confusion[truth][candidate] += 1
                total += 1
                if decision["status"] == "accepted":
                    accepted += 1
                    if candidate == truth:
                        correct_accepted += 1
                else:
                    abstained += 1

    top1 = sum(confusion[i][i] for i in range(len(classes))) / total
    metrics = {
        "samples": total,
        "top1_accuracy_before_abstention": top1,
        "accepted_predictions": accepted,
        "abstained_predictions": abstained,
        "coverage": accepted / total,
        "accuracy_on_accepted": correct_accepted / accepted if accepted else None,
        "min_score": args.min_score,
        "min_margin": args.min_margin,
        "note": "Model scores are not calibrated safety probabilities. This is a research evaluation only.",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (args.output / "confusion_matrix.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["true\\predicted", *classes])
        for name, values in zip(classes, confusion):
            writer.writerow([name, *values])
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"Auswertung gespeichert: {args.output}")


if __name__ == "__main__":
    main()
