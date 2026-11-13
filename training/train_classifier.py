"""Transfer-learning starter for ImageFolder traffic-sign data.

Expected layout:
data/signs/
  train/<class_name>/*.jpg
  val/<class_name>/*.jpg

This script trains a classifier on already-cropped signs. It does NOT detect
signs in full road scenes. Keep test data separate from train/val.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/signs"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/sign_classifier"))
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--workers", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_dir, val_dir = args.data / "train", args.data / "val"
    if not train_dir.is_dir() or not val_dir.is_dir():
        raise SystemExit(
            f"Datensatz fehlt. Erwartet werden {train_dir} und {val_dir}. "
            "Bitte erst einen lizenzierten Datensatz vorbereiten."
        )
    if args.epochs < 1 or args.batch_size < 1:
        raise SystemExit("--epochs und --batch-size müssen positiv sein.")

    mean, std = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
    train_tf = transforms.Compose([
        transforms.Resize((args.image_size, args.image_size)),
        transforms.RandomRotation(12),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((args.image_size, args.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    train_ds = datasets.ImageFolder(train_dir, transform=train_tf)
    val_ds = datasets.ImageFolder(val_dir, transform=val_tf)
    if train_ds.classes != val_ds.classes:
        raise SystemExit("Train- und Val-Klassen stimmen nicht überein.")
    if len(train_ds) == 0 or len(val_ds) == 0:
        raise SystemExit("Train- und Val-Ordner dürfen nicht leer sein.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers)

    weights = models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    for parameter in model.parameters():
        parameter.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, len(train_ds.classes))
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    best_accuracy = 0.0
    args.output.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(images), labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * images.size(0)

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                predictions = model(images).argmax(dim=1)
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        accuracy = correct / max(total, 1)
        print(f"Epoch {epoch + 1}/{args.epochs} | "
              f"train_loss={train_loss / len(train_ds):.4f} | val_accuracy={accuracy:.4f}")
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            torch.save(model.state_dict(), args.output / "best_model.pth")

    metadata = {
        "architecture": "resnet18",
        "classes": train_ds.classes,
        "image_size": args.image_size,
        "validation_accuracy": best_accuracy,
        "task": "classification_of_cropped_signs",
        "pretrained_weights": "ResNet18_Weights.DEFAULT",
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Bestes Validierungsergebnis: {best_accuracy:.4f}")
    print("Hinweis: Das Modell klassifiziert zugeschnittene Schilder, es detektiert sie nicht.")


if __name__ == "__main__":
    main()
