"""Classify one cropped traffic-sign image with a trained checkpoint.

Run from the repository root:
    python -m training.predict_classifier path/to/sign_crop.jpg

This is a classifier, not a detector. It does not locate signs in a full road scene.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms

from core.decision import decide_prediction


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--model-dir", type=Path, default=Path("artifacts/sign_classifier"))
    parser.add_argument("--min-score", type=float, default=0.45)
    parser.add_argument("--min-margin", type=float, default=0.10)
    args = parser.parse_args()

    if not 0.0 <= args.min_score <= 1.0 or not 0.0 <= args.min_margin <= 1.0:
        raise SystemExit("--min-score und --min-margin müssen zwischen 0 und 1 liegen.")

    metadata_path = args.model_dir / "metadata.json"
    weights_path = args.model_dir / "best_model.pth"
    if not args.image.is_file() or not metadata_path.is_file() or not weights_path.is_file():
        raise SystemExit("Bild oder trainiertes Modell/Metadaten nicht gefunden.")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    classes = metadata.get("classes")
    if not isinstance(classes, list) or not classes or not all(isinstance(x, str) for x in classes):
        raise SystemExit("Ungültige Klassenliste in metadata.json.")

    size = int(metadata.get("image_size", 224))
    if size < 1:
        raise SystemExit("Ungültige Bildgröße in metadata.json.")

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    state = torch.load(weights_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    try:
        with Image.open(args.image) as source:
            image = source.convert("RGB")
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Bild konnte nicht gelesen werden: {exc}") from exc

    with torch.inference_mode():
        scores = torch.softmax(model(transform(image).unsqueeze(0)), dim=1)[0].tolist()

    decision = decide_prediction(
        scores,
        classes,
        min_score=args.min_score,
        min_margin=args.min_margin,
    )
    if decision["status"] == "accepted":
        print(f"Vorhersage: {decision['label']}")
    else:
        print("Nicht sicher erkannt – bitte nicht als eindeutige Erkennung behandeln.")
        print(f"Unverbindlicher Kandidat: {decision['candidate']}")

    print(f"Modellscore: {decision['model_score']:.1%}")
    print(f"Abstand zur zweitbesten Klasse: {decision['margin']:.1%}")
    print("Modellscore ist keine kalibrierte Sicherheitswahrscheinlichkeit.")
    print("Dieses Skript klassifiziert nur einen zugeschnittenen Schild-Ausschnitt.")


if __name__ == "__main__":
    main()
