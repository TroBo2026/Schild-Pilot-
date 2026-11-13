"""Prepare a small, class-balanced pilot subset from Fraunhofer's Synset Signset.

The published dataset exposes train and validation splits (not a test split).
We derive disjoint val/test subsets from its validation split and document this.
Images are synthetic rendered scenes, not real camera photographs.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from pathlib import Path

from datasets import load_dataset

DATASET_ID = "FraunhoferIOSB/Synset-Signset-Germany"
LICENSE = "CC-BY-4.0"


def safe_class_name(label: int, name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "class"
    return f"{label:03d}_{slug}"


def grouped_indices(split):
    groups: dict[int, list[int]] = {}
    for index, label in enumerate(split["label"]):
        groups.setdefault(int(label), []).append(index)
    return groups


def write_rows(split, indices, output: Path, class_names: dict[int, str]) -> int:
    count = 0
    for index in indices:
        row = split[int(index)]
        label = int(row["label"])
        folder = output / safe_class_name(label, class_names[label])
        folder.mkdir(parents=True, exist_ok=True)
        row["image"].convert("RGB").save(folder / f"{index:07d}.jpg", quality=92)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/signs"))
    parser.add_argument("--config", default="Cycles")
    parser.add_argument("--per-class-train", type=int, default=80)
    parser.add_argument("--per-class-val", type=int, default=10)
    parser.add_argument("--per-class-test", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20261113)
    args = parser.parse_args()
    if min(args.per_class_train, args.per_class_val, args.per_class_test) < 1:
        raise SystemExit("Alle Stichprobengrößen müssen mindestens 1 sein.")

    print(f"Lade {DATASET_ID} / {args.config} …", flush=True)
    dataset = load_dataset(DATASET_ID, args.config)
    if "train" not in dataset or "validation" not in dataset:
        raise SystemExit(f"Erwartete train/validation-Splits fehlen: {list(dataset.keys())}")

    train, source_val = dataset["train"], dataset["validation"]
    train_groups, val_groups = grouped_indices(train), grouped_indices(source_val)
    class_ids = sorted(set(train_groups) & set(val_groups))
    if not class_ids:
        raise SystemExit("Keine gemeinsamen Klassen in train/validation gefunden.")

    rng = random.Random(args.seed)
    train_indices: list[int] = []
    val_indices: list[int] = []
    test_indices: list[int] = []
    class_names: dict[int, str] = {}

    for label in class_ids:
        train_pool, heldout_pool = list(train_groups[label]), list(val_groups[label])
        rng.shuffle(train_pool)
        rng.shuffle(heldout_pool)
        class_names[label] = str(train[train_pool[0]]["class_name"])
        if len(train_pool) < args.per_class_train:
            raise SystemExit(f"Klasse {label}: zu wenige Trainingsbilder ({len(train_pool)}).")
        if len(heldout_pool) < args.per_class_val + args.per_class_test:
            raise SystemExit(
                f"Klasse {label}: validation hat {len(heldout_pool)} Bilder; "
                f"benötigt werden {args.per_class_val + args.per_class_test}."
            )
        train_indices.extend(train_pool[:args.per_class_train])
        val_indices.extend(heldout_pool[:args.per_class_val])
        test_indices.extend(heldout_pool[args.per_class_val:args.per_class_val + args.per_class_test])

    for split_name in ("train", "val", "test"):
        target = args.output / split_name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    counts = {
        "train": write_rows(train, train_indices, args.output / "train", class_names),
        "val": write_rows(source_val, val_indices, args.output / "val", class_names),
        "test": write_rows(source_val, test_indices, args.output / "test", class_names),
    }
    manifest = {
        "dataset": DATASET_ID,
        "configuration": args.config,
        "license": LICENSE,
        "source": "https://huggingface.co/datasets/FraunhoferIOSB/Synset-Signset-Germany",
        "source_type": "synthetic_rendered_traffic_sign_scenes",
        "source_splits": {"train": "train", "val": "validation", "test": "validation"},
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
            "Validation source split is divided into disjoint val/test subsets; no official test split is published in this configuration.",
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
