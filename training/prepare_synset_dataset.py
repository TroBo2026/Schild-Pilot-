"""Prepare a small, class-balanced pilot subset from Fraunhofer's Synset Signset.

The source contains synthetic rendered traffic-sign scenes, not real camera photos.
Only a bounded subset is materialized so a free CPU CI runner can run a pilot.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from datasets import load_dataset


DATASET_ID = "FraunhoferIOSB/Synset-Signset-Germany"
LICENSE = "CC-BY-4.0"


def safe_class_name(label: int, name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "class"
    return f"{label:03d}_{slug}"


def grouped_indices(split):
    labels = split["label"]
    groups: dict[int, list[int]] = {}
    for index, label in enumerate(labels):
        groups.setdefault(int(label), []).append(index)
    return groups


def write_rows(split, indices, output: Path, class_names: dict[int, str]) -> int:
    count = 0
    for index in indices:
        row = split[int(index)]
        label = int(row["label"])
        image = row["image"].convert("RGB")
        folder = output / safe_class_name(label, class_names[label])
        folder.mkdir(parents=True, exist_ok=True)
        image.save(folder / f"{index:07d}.jpg", quality=92)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/signs"))
    parser.add_argument("--config", default="Cycles")
    parser.add_argument("--per-class-train", type=int, default=20)
    parser.add_argument("--per-class-val", type=int, default=5)
    parser.add_argument("--per-class-test", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261113)
    args = parser.parse_args()
    if min(args.per_class_train, args.per_class_val, args.per_class_test) < 1:
        raise SystemExit("Alle Stichprobengrößen müssen mindestens 1 sein.")

    print(f"Lade {DATASET_ID} / {args.config} …", flush=True)
    dataset = load_dataset(DATASET_ID, args.config)
    if "train" not in dataset or "test" not in dataset:
        raise SystemExit(f"Erwartete train/test-Splits fehlen: {list(dataset.keys())}")

    train, test = dataset["train"], dataset["test"]
    train_groups = grouped_indices(train)
    test_groups = grouped_indices(test)
    class_ids = sorted(set(train_groups) & set(test_groups))
    if not class_ids:
        raise SystemExit("Keine gemeinsamen Klassen in Train- und Testsplit gefunden.")

    # Deterministic per-class selection; test remains from the source's held-out split.
    import random
    rng = random.Random(args.seed)
    train_indices: list[int] = []
    val_indices: list[int] = []
    test_indices: list[int] = []
    class_names: dict[int, str] = {}

    for label in class_ids:
        train_pool = list(train_groups[label])
        test_pool = list(test_groups[label])
        rng.shuffle(train_pool)
        rng.shuffle(test_pool)
        class_names[label] = str(train[train_pool[0]]["class_name"])
        needed_train = args.per_class_train + args.per_class_val
        if len(train_pool) < needed_train or len(test_pool) < args.per_class_test:
            raise SystemExit(
                f"Klasse {label} hat zu wenig Daten: train={len(train_pool)}, "
                f"test={len(test_pool)}"
            )
        train_indices.extend(train_pool[:args.per_class_train])
        val_indices.extend(train_pool[args.per_class_train:needed_train])
        test_indices.extend(test_pool[:args.per_class_test])

    for split_name in ("train", "val", "test"):
        target = args.output / split_name
        if target.exists():
            import shutil
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    counts = {
        "train": write_rows(train, train_indices, args.output / "train", class_names),
        "val": write_rows(train, val_indices, args.output / "val", class_names),
        "test": write_rows(test, test_indices, args.output / "test", class_names),
    }
    manifest = {
        "dataset": DATASET_ID,
        "configuration": args.config,
        "license": LICENSE,
        "source": "https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany",
        "source_type": "synthetic_rendered_traffic_sign_scenes",
        "seed": args.seed,
        "classes": len(class_ids),
        "class_names": {str(k): v for k, v in class_names.items()},
        "counts": counts,
        "sampling": {
            "train_per_class": args.per_class_train,
            "validation_per_class": args.per_class_val,
            "test_per_class": args.per_class_test,
        },
        "limitations": [
            "Synthetic scenes; not real camera photographs.",
            "German sign taxonomy only; not international coverage.",
            "Classification pilot; not a full-scene detector.",
            "Not validated for vehicle or safety-critical use.",
        ],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
