"""Audit COCO-style traffic-sign detection splits before any model training.

Expected layout:
  root/{train,val,test}/images/*
  root/{train,val,test}/annotations.json

This validates annotation integrity and exact cross-split image duplicates. It
cannot detect near-duplicates, shared physical scenes, or incorrect labels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SPLITS = ("train", "val", "test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _positive_int(value: object) -> bool:
    """COCO IDs and image dimensions must be positive JSON integers, not bools."""
    return type(value) is int and value > 0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_split(split_dir: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    annotation_file = split_dir / "annotations.json"
    image_dir = split_dir / "images"
    if not annotation_file.is_file():
        return {}, [f"Fehlende Annotation-Datei: {annotation_file}"]
    if not image_dir.is_dir():
        return {}, [f"Fehlender Bildordner: {image_dir}"]
    try:
        data = json.loads(annotation_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, [f"Annotationen nicht lesbar ({annotation_file}): {exc}"]
    if not isinstance(data, dict):
        return {}, [f"COCO-Wurzel muss ein JSON-Objekt sein: {annotation_file}"]
    for key in ("images", "annotations", "categories"):
        if not isinstance(data.get(key), list):
            errors.append(f"{annotation_file}: '{key}' muss eine Liste sein.")
    return data, errors


def audit_detection_dataset(root: Path) -> dict:
    root = Path(root)
    report = {
        "root": str(root), "format": "COCO-style JSON",
        "splits": {}, "errors": [], "warnings": [], "exact_duplicates": [],
    }
    hashes: dict[str, list[dict[str, str]]] = {}
    reference_categories = None

    for split in SPLITS:
        split_dir = root / split
        if not split_dir.is_dir():
            report["errors"].append(f"Fehlender Split-Ordner: {split_dir}")
            continue
        data, errors = _load_split(split_dir)
        report["errors"].extend(errors)
        if errors:
            continue

        images, annotations, categories = data["images"], data["annotations"], data["categories"]
        if not images:
            report["errors"].append(f"Leerer Bildsplit: {split}")
        category_pairs = []
        category_ids = set()
        for category in categories:
            if not isinstance(category, dict):
                report["errors"].append(f"{split}: ungültige Kategorie.")
                continue
            cid, name = category.get("id"), category.get("name")
            if not _positive_int(cid) or not isinstance(name, str) or not name.strip():
                report["errors"].append(
                    f"{split}: Kategorie-ID muss eine positive ganze Zahl und der Name nicht leer sein."
                )
                continue
            if cid in category_ids:
                report["errors"].append(f"{split}: doppelte category id {cid}.")
            category_ids.add(cid)
            category_pairs.append((cid, name))
        category_signature = sorted(category_pairs, key=lambda item: item[0])
        if reference_categories is None:
            reference_categories = category_signature
        elif category_signature != reference_categories:
            report["errors"].append(f"Kategorien in {split} weichen von {SPLITS[0]} ab.")

        image_ids = set()
        image_paths = {}
        image_count = 0
        image_dir = split_dir / "images"
        for item in images:
            if not isinstance(item, dict):
                report["errors"].append(f"{split}: ungültiger image-Eintrag.")
                continue
            image_id, filename = item.get("id"), item.get("file_name")
            width, height = item.get("width"), item.get("height")
            if not _positive_int(image_id):
                report["errors"].append(f"{split}: image id muss eine positive ganze Zahl sein.")
                continue
            if image_id in image_ids:
                report["errors"].append(f"{split}: doppelte image id {image_id}.")
                continue
            image_ids.add(image_id)
            if not isinstance(filename, str) or not filename.strip():
                report["errors"].append(f"{split}: image {image_id} hat keinen Dateinamen.")
                continue
            rel = Path(filename)
            candidate = (image_dir / rel).resolve()
            try:
                candidate.relative_to(image_dir.resolve())
            except ValueError:
                report["errors"].append(f"{split}: unsicherer Bildpfad: {filename}")
                continue
            if rel.suffix.lower() not in IMAGE_SUFFIXES or not candidate.is_file():
                report["errors"].append(f"{split}: Bilddatei fehlt oder Format unbekannt: {filename}")
                continue
            if not _positive_int(width) or not _positive_int(height):
                report["errors"].append(
                    f"{split}: Bildbreite und -höhe müssen positive ganze Zahlen sein ({filename})."
                )
                continue
            image_paths[image_id] = (filename, float(width), float(height))
            image_count += 1
            digest = _sha256(candidate)
            hashes.setdefault(digest, []).append({"split": split, "path": filename})

        annotation_ids = set()
        annotation_count = 0
        annotations_by_category = {cid: 0 for cid in category_ids}
        image_annotation_counts = {image_id: 0 for image_id in image_paths}
        bbox_area_ratios = []
        for ann in annotations:
            if not isinstance(ann, dict):
                report["errors"].append(f"{split}: ungültiger Annotationseintrag.")
                continue
            aid, image_id, category_id = ann.get("id"), ann.get("image_id"), ann.get("category_id")
            if not _positive_int(aid):
                report["errors"].append(f"{split}: annotation id muss eine positive ganze Zahl sein.")
                continue
            if aid in annotation_ids:
                report["errors"].append(f"{split}: doppelte annotation id {aid}.")
                continue
            annotation_ids.add(aid)
            if not _positive_int(image_id):
                report["errors"].append(f"{split}: Annotation {aid} hat eine ungültige image_id.")
                continue
            if image_id not in image_paths:
                report["errors"].append(f"{split}: Annotation {aid} verweist auf unbekanntes Bild {image_id}.")
                continue
            if not _positive_int(category_id):
                report["errors"].append(f"{split}: Annotation {aid} hat eine ungültige category_id.")
                continue
            if category_id not in category_ids:
                report["errors"].append(f"{split}: Annotation {aid} verweist auf unbekannte Kategorie {category_id}.")
                continue
            bbox = ann.get("bbox")
            if (not isinstance(bbox, list) or len(bbox) != 4
                    or any(isinstance(v, bool) or not isinstance(v, (int, float))
                           or not math.isfinite(v) for v in bbox)):
                report["errors"].append(f"{split}: Annotation {aid} hat keine gültige [x,y,w,h]-Box.")
                continue
            x, y, width, height = map(float, bbox)
            image_width, image_height = image_paths[image_id][1:]
            if (x < 0 or y < 0 or width <= 0 or height <= 0
                    or x + width > image_width + 1e-6
                    or y + height > image_height + 1e-6):
                report["errors"].append(f"{split}: Bounding Box {aid} liegt außerhalb des Bildes oder ist leer.")
                continue
            annotation_count += 1
            annotations_by_category[category_id] += 1
            image_annotation_counts[image_id] += 1
            bbox_area_ratios.append((width * height) / (image_width * image_height))

        sorted_ratios = sorted(bbox_area_ratios)
        if sorted_ratios:
            middle = len(sorted_ratios) // 2
            median_ratio = (
                sorted_ratios[middle] if len(sorted_ratios) % 2
                else (sorted_ratios[middle - 1] + sorted_ratios[middle]) / 2
            )
            area_ratio_summary = {
                "min": sorted_ratios[0],
                "median": median_ratio,
                "max": sorted_ratios[-1],
            }
        else:
            area_ratio_summary = None

        report["splits"][split] = {
            "images": image_count,
            "annotations": annotation_count,
            "categories": len(category_ids),
            "annotations_by_category": {
                str(cid): annotations_by_category[cid] for cid in sorted(annotations_by_category)
            },
            "images_without_annotations": sum(
                count == 0 for count in image_annotation_counts.values()
            ),
            "bbox_area_ratio": area_ratio_summary,
        }
        if image_count and annotation_count == 0:
            report["warnings"].append(f"{split}: keine positiven Schilder-Annotationen gefunden.")
        if any(count == 0 for count in annotations_by_category.values()):
            report["warnings"].append(f"{split}: mindestens eine Kategorie hat keine gültigen Annotationen.")

    for digest, entries in hashes.items():
        if len({entry["split"] for entry in entries}) > 1:
            report["exact_duplicates"].append({"sha256": digest, "files": entries})
    if report["exact_duplicates"]:
        report["errors"].append("Identische Bilddateien kommen in mehreren Splits vor.")
    report["ok"] = not report["errors"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/detection"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/detection_audit.json"))
    args = parser.parse_args()
    report = audit_detection_dataset(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
