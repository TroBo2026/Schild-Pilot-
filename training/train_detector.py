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


def evaluate(model, loader, device, iou_threshold=0.5, score_threshold=0.25):
    """Greedy per-image matching; reports diagnostic precision/recall, not COCO mAP."""
    tp = fp = fn = 0
    model.eval()
    with torch.inference_mode():
        for images, targets in loader:
            outputs = model([image.to(device) for image in images])
            for output, target in zip(outputs, targets):
                keep = output["scores"].cpu() >= score_threshold
                boxes = output["boxes"].cpu()[keep]
                labels = output["labels"].cpu()[keep]
                gt_boxes, gt_labels = target["boxes"], target["labels"]
                matched = set()
                order = torch.argsort(output["scores"].cpu()[keep], descending=True).tolist()
                for pred_index in order:
                    candidates = [i for i in range(len(gt_boxes))
                                  if i not in matched and int(gt_labels[i]) == int(labels[pred_index])]
                    if not candidates:
                        fp += 1
                        continue
                    pred = boxes[pred_index]
                    best_i, best_iou = None, 0.0
                    for i in candidates:
                        gt = gt_boxes[i]
                        left, top = torch.maximum(pred[:2], gt[:2])
                        right, bottom = torch.minimum(pred[2:], gt[2:])
                        inter = (right - left).clamp(min=0).prod().item()
                        area_p = (pred[2:] - pred[:2]).clamp(min=0).prod().item()
                        area_g = (gt[2:] - gt[:2]).clamp(min=0).prod().item()
                        iou = inter / max(area_p + area_g - inter, 1e-9)
                        if iou > best_iou:
                            best_i, best_iou = i, iou
                    if best_i is not None and best_iou >= iou_threshold:
                        matched.add(best_i)
                        tp += 1
                    else:
                        fp += 1
                fn += len(gt_boxes) - len(matched)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {"iou_threshold": iou_threshold, "score_threshold": score_threshold,
            "true_positives": tp, "false_positives": fp, "false_negatives": fn,
            "precision": precision, "recall": recall,
            "f1": 2 * precision * recall / max(precision + recall, 1e-12)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/detection"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/sign_detector"))
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261113)
    args = parser.parse_args()
    if min(args.epochs, args.batch_size) < 1:
        raise SystemExit("Epochen und Batchgröße müssen positiv sein.")
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
    weights = "DEFAULT"
    model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 3)
    model.to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
                                lr=0.002, momentum=0.9, weight_decay=0.0005)
    args.output.mkdir(parents=True, exist_ok=True)
    history, best_f1 = [], -1.0
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
        metrics = evaluate(model, val_loader, device)
        row = {"epoch": epoch + 1, "mean_train_loss": running / max(steps, 1), **metrics}
        history.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            torch.save(model.state_dict(), args.output / "best_detector.pth")
            (args.output / "best_validation_metrics.json").write_text(
                json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")
    metadata = {
        "architecture": "fasterrcnn_mobilenet_v3_large_320_fpn",
        "classes": ["background", "Traffic Sign", "Damaged Traffic Sign"],
        "epochs": args.epochs, "best_validation_f1": best_f1,
        "training_images": len(train_ds), "validation_images": len(val_ds),
        "pretrained_initialization": "Torchvision COCO weights",
        "evaluation": "greedy IoU>=0.5 precision/recall at score>=0.25; not COCO mAP",
        "limitations": ["Two-class dataset only", "Small pilot dataset",
                        "No independent external benchmark", "Not safety validated"]
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (args.output / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
