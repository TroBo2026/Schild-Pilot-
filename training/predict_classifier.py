"""Run classification on one already-cropped traffic-sign image.

This is a classifier, not a detector: the input should contain one sign crop.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--model-dir", type=Path, default=Path("artifacts/sign_classifier"))
    parser.add_argument("--min-confidence", type=float, default=0.65)
    args = parser.parse_args()

    metadata_path = args.model_dir / "metadata.json"
    weights_path = args.model_dir / "best_model.pth"
    if not args.image.is_file() or not metadata_path.is_file() or not weights_path.is_file():
        raise SystemExit("Bild oder trainiertes Modell/Metadaten nicht gefunden.")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    classes = metadata["classes"]
    size = int(metadata.get("image_size", 224))
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
    image = Image.open(args.image).convert("RGB")
    with torch.no_grad():
        probabilities = torch.softmax(model(transform(image).unsqueeze(0)), dim=1)[0]
    score, index = probabilities.max(dim=0)
    confidence = float(score.item())
    if confidence < args.min_confidence:
        print(f"Nicht sicher erkannt (Modellscore {confidence:.1%}).")
    else:
        print(f"Vorhersage: {classes[int(index.item())]} (Modellscore {confidence:.1%})")
    print("Hinweis: Der Score ist keine kalibrierte Sicherheitswahrscheinlichkeit.")
    print("Dieses Skript klassifiziert nur einen zugeschnittenen Schild-Ausschnitt.")


if __name__ == "__main__":
    main()
