"""Train a compact two-class detector on COCO-style TrafficSigns-Raw data."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_320_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.transforms.functional import to_tensor

from training.detection_metrics import evaluate_thresholds


DEFAULT_SCORE_THRESHOLDS = (0.01, 0.025, 0.05, 0.10, 0.25, 0.50)


class CocoDetectionDataset(Dataset):
    def __init__(self, root: Path, split: str):
        self.root = Path(root) / split
        data = json.loads((self.root / "annotations.json").read_text(encoding="utf-8"))
        self.images = data["images"]
        self.annotations = {}
        for ann in data["annotations"]:
            self.annotations.setdefault(ann["image_id"], []).append(ann)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        info = self.images[index]
        image = Image.open(self.root / "images" / info["file_name"]).convert("RGB")
        image_tensor = to_tensor(image)
        boxes, labels, areas, crowds = [], [], [], []
        for ann in self.annotations.get(info["id"], []):
            x, y, width, height = ann["bbox"]
            boxes.append([x, y, x + width, y + height])
            labels.append(int(ann["category_id"]))
            areas.append(float(ann.get("area", width * height)))
            crowds.append(int(ann.get("iscrowd", 0)))
        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "image_id": torch.tensor([info["id"]]),
            "area": torch.tensor(areas, dtype=torch.float32),
            "iscrowd": torch.tensor(crowds, dtype=torch.int64),
        }
        return image_tensor, target


def collate(batch):
    return tuple(zip(*batch))


def evaluate(model, loader, device, score_thresholds=DEFAULT_SCORE_THRESHOLDS,
             iou_threshold=0.5):
    """Collect predictions once, then sweep score thresholds on this split."""
    predictions_by_image = []
    ground_truths_by_image = []
    model.eval()
    with torch.inference_mode():
        for images, targets in loader:
            outputs = model([image.to(device) for image in images])
            for output, target in zip(outputs, targets):
                boxes = output["boxes"].detach().cpu().tolist()
                labels = output["labels"].detach().cpu().tolist()
                scores = output["scores"].detach().cpu().tolist()
                predictions_by_image.append([
                    {"box": box, "label": int(label), "score": float(score)}
                    for box, label, score in zip(boxes, labels, scores)
                ])
                gt_boxes = target["boxes"].detach().cpu().tolist()
                gt_labels = target["labels"].detach().cpu().tolist()
                ground_truths_by_image.append([
                    {"box": box, "label": int(label)}
                    for box, label in zip(gt_boxes, gt_labels)
                ])
    return evaluate_thresholds(
        predictions_by_image,
        ground_truths_by_image,
        score_thresholds=score_thresholds,
        iou_threshold=iou_threshold,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/detection"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/sign_detector"))
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261113)
    args = parser.parse_args()
    if min(args.epochs, args.batch_size) < 1 or args.workers < 0:
        raise SystemExit("Epochen und Batchgröße müssen positiv sein; Worker dürfen nicht negativ sein.")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = CocoDetectionDataset(args.data, "train")
    val_ds = CocoDetectionDataset(args.data, "val")
    if not len(train_ds) or not len(val_ds):
        raise SystemExit("Train- und Val-Datensatz müssen nicht leer sein.")
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers, collate_fn=collate)
    model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=None, weights_backbone=None)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 3)
    model.to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
                                lr=0.002, momentum=0.9, weight_decay=0.0005)
    args.output.mkdir(parents=True, exist_ok=True)
    history = []
    best_f1 = -1.0
    best_row = None
    checkpoint_path = args.output / "best_detector.pth"

    for epoch in range(args.epochs):
        model.train()
        running, steps = 0.0, 0
        for images, targets in train_loader:
            images = [image.to(device) for image in images]
            targets = [{k: v.to(device) for k, v in target.items()} for target in targets]
            loss_dict = model(images, targets)
            loss = sum(loss_dict.values())
            if not torch.isfinite(loss):
                raise RuntimeError(f"Nicht-endlicher Trainingsverlust: {loss.item()}")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            running += float(loss.detach())
            steps += 1

        sweep = evaluate(model, val_loader, device)
        selected = sweep["best"]
        row = {
            "epoch": epoch + 1,
            "mean_train_loss": running / max(steps, 1),
            **selected,
            "threshold_sweep": sweep["thresholds"],
        }
        history.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

        if selected["f1"] > best_f1:
            best_f1 = selected["f1"]
            best_row = row
            (args.output / "best_validation_metrics.json").write_text(
                json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")
            if best_f1 > 0.0:
                torch.save(model.state_dict(), checkpoint_path)

    (args.output / "history.json").write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    metadata = {
        "architecture": "fasterrcnn_mobilenet_v3_large_320_fpn",
        "classes": ["background", "Traffic Sign", "Damaged Traffic Sign"],
        "epochs": args.epochs,
        "training_images": len(train_ds),
        "validation_images": len(val_ds),
        "pretrained_initialization": "random initialization; no external model weights",
        "validation_threshold_selection": (
            "score threshold selected by maximum validation F1 from "
            f"{list(DEFAULT_SCORE_THRESHOLDS)} at IoU >= 0.5"
        ),
        "evaluation": "greedy per-image IoU matching; diagnostic precision/recall, not COCO mAP",
        "limitations": [
            "Two-class dataset only",
            "Small pilot dataset",
            "No independent external benchmark",
            "Not safety validated",
        ],
    }

    if best_row is None or best_f1 <= 0.0 or not checkpoint_path.is_file():
        metadata.update({
            "status": "failed_no_positive_validation_f1",
            "best_validation_f1": max(best_f1, 0.0),
            "test_evaluation": "not run because validation produced no true positives",
        })
        (args.output / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        raise SystemExit(
            "Keine echte positive Detektion auf dem Validierungssplit; "
            "Testsplit bleibt unangetastet. Kein nutzbarer Detektor erzeugt."
        )

    # Only after a positive validation result is the separate test split opened.
    test_ds = CocoDetectionDataset(args.data, "test")
    if not len(test_ds):
        raise SystemExit("Test-Datensatz ist leer.")
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                             num_workers=args.workers, collate_fn=collate)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
    test_sweep = evaluate(
        model, test_loader, device,
        score_thresholds=[float(best_row["score_threshold"])],
    )
    test_metrics = {
        **test_sweep["best"],
        "threshold_source": "validation_split",
        "validation_score_threshold": float(best_row["score_threshold"]),
    }
    (args.output / "test_metrics.json").write_text(
        json.dumps(test_metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    metadata.update({
        "status": "completed" if test_metrics["true_positives"] > 0 else "failed_no_test_true_positives",
        "best_validation_f1": best_f1,
        "best_validation_score_threshold": float(best_row["score_threshold"]),
        "test_images": len(test_ds),
        "test_metrics_file": "test_metrics.json",
        "test_f1": test_metrics["f1"],
        "test_threshold_source": "validation_split",
    })
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"test_metrics": test_metrics, "status": metadata["status"]},
                     ensure_ascii=False), flush=True)
    if test_metrics["true_positives"] == 0:
        raise SystemExit(
            "Validierung war positiv, aber auf dem unangetasteten Testsplit "
            "wurde keine echte Detektion gefunden."
        )


if __name__ == "__main__":
    main()
