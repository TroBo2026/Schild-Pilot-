"""Verify and convert the directly released TrafficSigns-Raw dataset to COCO.

The caller must verify the archive SHA-256 before extraction. This script also
requires the dataset-specific CC BY 4.0 notice and preserves upstream splits.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

CLASS_NAMES = ["Traffic Sign", "Damaged Traffic Sign"]
SPLITS = {
    "train": ("Train_Data/images/train", "Train_Data/labels/train"),
    "val": ("Train_Data/images/val", "Train_Data/labels/val"),
    "test": ("Train_Data/test/images", "Train_Data/test/labels"),
}


def yolo_to_coco(line: str, image_width: int, image_height: int) -> tuple[int, list[float]]:
    parts = line.split()
    if len(parts) != 5:
        raise ValueError("YOLO-Zeile muss genau fünf Werte enthalten.")
    class_id = int(parts[0])
    cx, cy, width, height = map(float, parts[1:])
    if class_id not in (0, 1):
        raise ValueError(f"Unbekannte Klasse: {class_id}")
    values = (cx, cy, width, height)
    if any(not 0 <= value <= 1 for value in values) or width <= 0 or height <= 0:
        raise ValueError("YOLO-Koordinaten müssen normalisiert und positiv sein.")
    x = (cx - width / 2) * image_width
    y = (cy - height / 2) * image_height
    w = width * image_width
    h = height * image_height
    if x < 0 or y < 0 or x + w > image_width + 1e-5 or y + h > image_height + 1e-5:
        raise ValueError("Bounding Box liegt außerhalb des Bildes.")
    return class_id + 1, [x, y, w, h]


def convert(source: Path, output: Path, license_file: Path) -> dict:
    notice = license_file.read_text(encoding="utf-8")
    required = ("Creative Commons Attribution 4.0 International (CC BY 4.0)",
                "TrafficSigns-Raw source images", "author-owned")
    if any(token not in notice for token in required):
        raise ValueError("Die erwartete TrafficSigns-spezifische CC BY 4.0-Lizenznotiz fehlt oder ist unvollständig.")
    if not (source / "README.md").is_file() or "TrafficSigns-Raw" not in (source / "README.md").read_text(encoding="utf-8"):
        raise ValueError("TrafficSigns-Raw-README fehlt oder stimmt nicht.")
    report = {"source": str(source), "license": "CC BY 4.0", "splits": {}}
    for split, (image_rel, label_rel) in SPLITS.items():
        image_dir, label_dir = source / image_rel, source / label_rel
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise FileNotFoundError(f"Split-Ordner fehlen: {split}")
        images = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
        if not images:
            raise ValueError(f"Split {split} enthält keine Bilder.")
        out_images = output / split / "images"
        out_images.mkdir(parents=True, exist_ok=True)
        coco_images, coco_annotations = [], []
        missing_labels = []
        annotation_id = 1
        for image_id, image_path in enumerate(images, start=1):
            label_path = label_dir / (image_path.stem + ".txt")
            if not label_path.is_file():
                missing_labels.append(image_path.name)
                continue
            with Image.open(image_path) as im:
                width, height = im.size
                im.verify()
            if width <= 0 or height <= 0:
                raise ValueError(f"Ungültige Bildmaße: {image_path}")
            copied_name = image_path.name
            shutil.copy2(image_path, out_images / copied_name)
            coco_images.append({"id": image_id, "file_name": copied_name, "width": width, "height": height})
            rows = [line.strip() for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not rows:
                raise ValueError(f"Leere Labeldatei: {label_path}")
            for line in rows:
                category_id, bbox = yolo_to_coco(line, width, height)
                coco_annotations.append({
                    "id": annotation_id, "image_id": image_id, "category_id": category_id,
                    "bbox": bbox, "area": bbox[2] * bbox[3], "iscrowd": 0,
                })
                annotation_id += 1
        if missing_labels:
            raise ValueError(f"{split}: {len(missing_labels)} Bildern fehlen Labeldateien; erstes Beispiel: {missing_labels[0]}")
        categories = [{"id": i + 1, "name": name, "supercategory": "traffic_sign"} for i, name in enumerate(CLASS_NAMES)]
        out_dir = output / split
        (out_dir / "annotations.json").write_text(
            json.dumps({"images": coco_images, "annotations": coco_annotations, "categories": categories},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        report["splits"][split] = {"images": len(coco_images), "annotations": len(coco_annotations)}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/detection"))
    parser.add_argument("--license-file", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("artifacts/traffic_signs_raw_intake.json"))
    args = parser.parse_args()
    report = convert(args.source, args.output, args.license_file)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
