"""Audit an ImageFolder-style dataset without loading images into memory.

Expected layout: root/{train,val,test}/<class_name>/<image files>.
Only exact SHA-256 duplicates across splits are flagged; near-duplicates
and physical-scene leakage still require a sequence/scene-aware review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".ppm", ".webp"}
SPLITS = ("train", "val", "test")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_dataset(root: Path) -> dict:
    root = Path(root)
    report = {"root": str(root), "splits": {}, "errors": [], "warnings": [], "exact_duplicates": []}
    hashes: dict[str, list[dict[str, str]]] = {}
    reference_classes = None

    for split in SPLITS:
        split_dir = root / split
        if not split_dir.is_dir():
            report["errors"].append(f"Fehlender Split-Ordner: {split_dir}")
            continue
        class_dirs = sorted(p for p in split_dir.iterdir() if p.is_dir())
        classes = [p.name for p in class_dirs]
        if not classes:
            report["errors"].append(f"Keine Klassenordner in {split_dir}")
        if reference_classes is None:
            reference_classes = classes
        elif classes != reference_classes:
            report["errors"].append(f"Klassen in {split} stimmen nicht mit {SPLITS[0]} überein.")

        counts = {}
        total = 0
        for class_dir in class_dirs:
            images = sorted(
                p for p in class_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
            )
            counts[class_dir.name] = len(images)
            total += len(images)
            if not images:
                report["warnings"].append(f"Leere Klasse: {split}/{class_dir.name}")
            for image_path in images:
                digest = sha256_file(image_path)
                hashes.setdefault(digest, []).append({
                    "split": split,
                    "path": image_path.relative_to(root).as_posix(),
                })
        if total == 0:
            report["errors"].append(f"Keine unterstützten Bilddateien in {split_dir}")
        report["splits"][split] = {"images": total, "classes": counts}

    for digest, entries in hashes.items():
        split_names = {entry["split"] for entry in entries}
        if len(entries) > 1 and len(split_names) > 1:
            report["exact_duplicates"].append({"sha256": digest, "files": entries})
    if report["exact_duplicates"]:
        report["errors"].append("Identische Bilddateien kommen in mehreren Splits vor.")
    report["ok"] = not report["errors"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/signs"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/dataset_audit.json"))
    args = parser.parse_args()
    report = audit_dataset(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
