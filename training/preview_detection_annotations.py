"""Create an offline visual review of COCO-style detection annotations.

The tool copies a deterministic sample of annotated images to a local preview
folder and draws the supplied ground-truth boxes. It does not run a model,
change source images, download data, or upload anything.
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import math
import random
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SPLITS = ("train", "val", "test")
COLORS = ("#f2c14e", "#4ea5d9", "#7bc96f", "#d78bd4", "#f08a5d", "#69c6b3")


def _positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Annotationen nicht lesbar ({path}): {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("COCO-Wurzel muss ein JSON-Objekt sein.")
    for key in ("images", "annotations", "categories"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"'{key}' muss eine Liste sein.")
    return data


def _safe_image_path(image_dir: Path, filename: object) -> Path:
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Bilddatei hat keinen gültigen Dateinamen.")
    candidate = (image_dir / filename).resolve()
    try:
        candidate.relative_to(image_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"Unsicherer Bildpfad: {filename}") from exc
    if not candidate.is_file():
        raise ValueError(f"Bilddatei fehlt: {filename}")
    return candidate


def _validated_box(value: object, width: int, height: int, annotation_id: int) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError(f"Annotation {annotation_id}: ungültige Bounding Box [x,y,w,h].")
    numbers = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"Annotation {annotation_id}: ungültige Bounding Box [x,y,w,h].")
        try:
            number = float(item)
        except (OverflowError, ValueError):
            raise ValueError(f"Annotation {annotation_id}: ungültige Bounding Box [x,y,w,h].")
        if not math.isfinite(number):
            raise ValueError(f"Annotation {annotation_id}: ungültige Bounding Box [x,y,w,h].")
        numbers.append(number)
    x, y, box_width, box_height = numbers
    if (
        x < 0
        or y < 0
        or box_width <= 0
        or box_height <= 0
        or x + box_width > width + 1e-6
        or y + box_height > height + 1e-6
    ):
        raise ValueError(f"Annotation {annotation_id}: Bounding Box liegt außerhalb des Bildes oder ist leer.")
    return x, y, box_width, box_height


def _render_preview(
    source_path: Path,
    destination: Path,
    image_width: int,
    image_height: int,
    annotations: list[dict],
    categories: dict[int, str],
    max_edge: int,
) -> None:
    with Image.open(source_path) as opened:
        if opened.size != (image_width, image_height):
            raise ValueError(
                f"Bildmaße stimmen nicht mit COCO überein ({source_path.name}): "
                f"{opened.size} statt {(image_width, image_height)}."
            )
        image = opened.convert("RGB")

    scale = min(1.0, max_edge / max(image.size))
    if scale < 1.0:
        resized = (
            max(1, round(image.width * scale)),
            max(1, round(image.height * scale)),
        )
        image = image.resize(resized, Image.Resampling.LANCZOS)

    scale_x = image.width / image_width
    scale_y = image.height / image_height
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    line_width = max(2, round(min(image.size) * 0.003))

    for annotation in annotations:
        x, y, box_width, box_height = annotation["bbox"]
        category_id = annotation["category_id"]
        color = COLORS[(category_id - 1) % len(COLORS)]
        left = max(0, min(image.width - 1, round(x * scale_x)))
        top = max(0, min(image.height - 1, round(y * scale_y)))
        right = max(left + 1, min(image.width - 1, round((x + box_width) * scale_x)))
        bottom = max(top + 1, min(image.height - 1, round((y + box_height) * scale_y)))
        draw.rectangle((left, top, right, bottom), outline=color, width=line_width)

        label = categories[category_id]
        text_bounds = draw.textbbox((0, 0), label, font=font)
        text_width = text_bounds[2] - text_bounds[0]
        text_height = text_bounds[3] - text_bounds[1]
        label_top = max(0, top - text_height - 6)
        label_right = min(image.width - 1, left + text_width + 8)
        draw.rectangle((left, label_top, label_right, label_top + text_height + 5), fill=color)
        draw.text((left + 4, label_top + 2), label, fill="#111111", font=font)

    image.save(destination, format="JPEG", quality=90, optimize=True)


def generate_annotation_preview(
    data_root: Path,
    output_dir: Path,
    *,
    split: str = "val",
    sample_count: int = 12,
    seed: int = 42,
    max_edge: int = 1600,
) -> dict:
    """Generate a deterministic, local-only visual sample of ground-truth boxes."""
    if split not in SPLITS:
        raise ValueError(f"Split muss einer von {', '.join(SPLITS)} sein.")
    if type(sample_count) is not int or sample_count <= 0:
        raise ValueError("sample_count muss eine positive ganze Zahl sein.")
    if type(max_edge) is not int or max_edge <= 0:
        raise ValueError("max_edge muss eine positive ganze Zahl sein.")
    if type(seed) is not int:
        raise ValueError("seed muss eine ganze Zahl sein.")

    data_root = Path(data_root).resolve()
    output_dir = Path(output_dir).resolve()
    if output_dir == data_root or data_root in output_dir.parents:
        raise ValueError("Der Ausgabeordner darf nicht innerhalb des Datensatzordners liegen.")

    split_dir = data_root / split
    image_dir = split_dir / "images"
    if not image_dir.is_dir():
        raise ValueError(f"Bildordner fehlt: {image_dir}")
    data = _load_json(split_dir / "annotations.json")

    categories: dict[int, str] = {}
    for category in data["categories"]:
        if not isinstance(category, dict):
            raise ValueError("Ungültiger Kategorieeintrag.")
        category_id, name = category.get("id"), category.get("name")
        if not _positive_int(category_id) or not isinstance(name, str) or not name.strip():
            raise ValueError("Kategorie benötigt eine positive Ganzzahl-ID und einen Namen.")
        if category_id in categories:
            raise ValueError(f"Doppelte Kategorie-ID: {category_id}")
        categories[category_id] = name.strip()

    images: dict[int, dict] = {}
    for item in data["images"]:
        if not isinstance(item, dict):
            raise ValueError("Ungültiger Bildeintrag.")
        image_id = item.get("id")
        width, height = item.get("width"), item.get("height")
        if not _positive_int(image_id) or image_id in images:
            raise ValueError(f"Ungültige oder doppelte Bild-ID: {image_id}")
        if not _positive_int(width) or not _positive_int(height):
            raise ValueError(f"Bild {image_id} benötigt positive Ganzzahl-Dimensionen.")
        images[image_id] = {
            "file_name": item.get("file_name"),
            "width": width,
            "height": height,
            "path": _safe_image_path(image_dir, item.get("file_name")),
        }

    annotations_by_image: dict[int, list[dict]] = {image_id: [] for image_id in images}
    annotation_ids: set[int] = set()
    for annotation in data["annotations"]:
        if not isinstance(annotation, dict):
            raise ValueError("Ungültiger Annotationseintrag.")
        annotation_id = annotation.get("id")
        image_id = annotation.get("image_id")
        category_id = annotation.get("category_id")
        if not _positive_int(annotation_id) or annotation_id in annotation_ids:
            raise ValueError(f"Ungültige oder doppelte Annotations-ID: {annotation_id}")
        annotation_ids.add(annotation_id)
        if not _positive_int(image_id) or image_id not in images:
            raise ValueError(f"Annotation {annotation_id} verweist auf ein unbekanntes Bild.")
        if not _positive_int(category_id) or category_id not in categories:
            raise ValueError(f"Annotation {annotation_id} verweist auf eine unbekannte Kategorie.")
        image_info = images[image_id]
        bbox = _validated_box(
            annotation.get("bbox"),
            image_info["width"],
            image_info["height"],
            annotation_id,
        )
        annotations_by_image[image_id].append({
            "bbox": bbox,
            "category_id": category_id,
        })

    annotated_ids = sorted(
        image_id for image_id, entries in annotations_by_image.items() if entries
    )
    if not annotated_ids:
        raise ValueError(f"Im Split '{split}' wurden keine gültigen annotierten Bilder gefunden.")

    rng = random.Random(seed)
    selected_ids = sorted(rng.sample(annotated_ids, min(sample_count, len(annotated_ids))))
    output_dir.mkdir(parents=True, exist_ok=True)

    preview_items = []
    for index, image_id in enumerate(selected_ids, start=1):
        image_info = images[image_id]
        preview_name = f"preview_{index:03d}.jpg"
        entries = annotations_by_image[image_id]
        _render_preview(
            image_info["path"],
            output_dir / preview_name,
            image_info["width"],
            image_info["height"],
            entries,
            categories,
            max_edge,
        )
        counts = Counter(categories[item["category_id"]] for item in entries)
        preview_items.append({
            "image_id": image_id,
            "source_filename": image_info["file_name"],
            "preview_filename": preview_name,
            "width": image_info["width"],
            "height": image_info["height"],
            "annotation_count": len(entries),
            "categories": dict(sorted(counts.items())),
        })

    report = {
        "split": split,
        "seed": seed,
        "requested_sample_count": sample_count,
        "generated_preview_count": len(preview_items),
        "max_edge": max_edge,
        "images": preview_items,
        "notice": (
            "Lokale Sichtprüfung der vorhandenen Ground-Truth-Boxen. "
            "Keine Modellinferenz und keine Aussage zur Erkennungsleistung."
        ),
    }
    (output_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    cards = []
    for item in preview_items:
        filename = html_lib.escape(str(item["source_filename"]), quote=True)
        category_text = ", ".join(
            f"{html_lib.escape(name)} ({count})"
            for name, count in item["categories"].items()
        )
        cards.append(
            "<article class='card'>"
            f"<img src='{item['preview_filename']}' alt='Annotiertes Bild {item['image_id']}'>"
            f"<h2>Bild-ID {item['image_id']}</h2>"
            f"<p class='source'>{filename}</p>"
            f"<p>{item['annotation_count']} Box(en) · {category_text}</p>"
            "</article>"
        )
    page = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Schild Pilot – Boxenprüfung</title>
<style>
:root{color-scheme:dark;background:#10151b;color:#edf2f6;font:16px system-ui,sans-serif}
body{margin:0;padding:24px;max-width:1200px;margin-inline:auto}
h1{font-size:clamp(1.5rem,4vw,2.2rem)}.notice{color:#c9d2dc;line-height:1.5}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:18px}
.card{background:#1a232d;border:1px solid #34414d;border-radius:14px;padding:14px;min-width:0}
.card img{display:block;width:100%;height:auto;max-height:420px;object-fit:contain;background:#080c10;border-radius:8px}
.card h2{font-size:1rem;margin:12px 0 4px}.card p{font-size:.85rem;color:#c1ccd6;overflow-wrap:anywhere}
.source{color:#91a1af!important}
</style>
</head>
<body>
<h1>Schild Pilot – visuelle Bounding-Box-Prüfung</h1>
<p class="notice">Diese lokale Offline-Ansicht zeigt vorhandene Ground-Truth-Annotationen.
Sie führt keine KI-Inferenz aus und bewertet keine Modellleistung. Quelldateien bleiben unverändert.</p>
<div class="grid">
""" + "\n".join(cards) + """
</div>
</body>
</html>
"""
    (output_dir / "index.html").write_text(page, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/detection"))
    parser.add_argument("--split", choices=SPLITS, default="val")
    parser.add_argument("--output", type=Path, default=Path("artifacts/detection_preview"))
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-edge", type=int, default=1600)
    args = parser.parse_args()
    try:
        report = generate_annotation_preview(
            args.data,
            args.output,
            split=args.split,
            sample_count=args.samples,
            seed=args.seed,
            max_edge=args.max_edge,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
