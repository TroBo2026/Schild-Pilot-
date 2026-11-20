import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from training.preview_detection_annotations import generate_annotation_preview


class DetectionAnnotationPreviewTests(unittest.TestCase):
    def _make_dataset(self, root: Path, count: int = 3) -> None:
        split_dir = root / "val"
        image_dir = split_dir / "images"
        image_dir.mkdir(parents=True)
        images = []
        annotations = []
        for index in range(count):
            filename = f"scene_{index}.jpg"
            Image.new("RGB", (64, 48), (index * 30, 80, 120)).save(image_dir / filename)
            images.append({
                "id": index + 1,
                "file_name": filename,
                "width": 64,
                "height": 48,
            })
            annotations.append({
                "id": index + 1,
                "image_id": index + 1,
                "category_id": 1,
                "bbox": [8, 7, 24, 18],
            })
        payload = {
            "images": images,
            "annotations": annotations,
            "categories": [{"id": 1, "name": "Speed <limit>"}],
        }
        (split_dir / "annotations.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def test_creates_offline_previews_and_escapes_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            output = Path(tmp) / "preview"
            self._make_dataset(root, count=2)
            report = generate_annotation_preview(root, output, sample_count=2)

            self.assertEqual(report["generated_preview_count"], 2)
            self.assertTrue((output / "preview_001.jpg").is_file())
            self.assertTrue((output / "preview_002.jpg").is_file())
            self.assertTrue((output / "report.json").is_file())
            page = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("&lt;limit&gt;", page)
            self.assertNotIn("<limit>", page)
            self.assertNotIn("https://", page)

    def test_sample_is_reproducible_for_same_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            self._make_dataset(root, count=5)
            first = generate_annotation_preview(
                root, Path(tmp) / "first", sample_count=2, seed=17
            )
            second = generate_annotation_preview(
                root, Path(tmp) / "second", sample_count=2, seed=17
            )
            self.assertEqual(
                [item["image_id"] for item in first["images"]],
                [item["image_id"] for item in second["images"]],
            )

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            self._make_dataset(root, count=1)
            annotation_path = root / "val" / "annotations.json"
            data = json.loads(annotation_path.read_text(encoding="utf-8"))
            data["images"][0]["file_name"] = "../outside.jpg"
            annotation_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsicherer Bildpfad"):
                generate_annotation_preview(root, Path(tmp) / "preview")

    def test_rejects_box_outside_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            self._make_dataset(root, count=1)
            annotation_path = root / "val" / "annotations.json"
            data = json.loads(annotation_path.read_text(encoding="utf-8"))
            data["annotations"][0]["bbox"] = [50, 40, 20, 20]
            annotation_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Bounding Box"):
                generate_annotation_preview(root, Path(tmp) / "preview")

    def test_rejects_image_dimension_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            self._make_dataset(root, count=1)
            annotation_path = root / "val" / "annotations.json"
            data = json.loads(annotation_path.read_text(encoding="utf-8"))
            data["images"][0]["width"] = 80
            annotation_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Bildmaße stimmen nicht"):
                generate_annotation_preview(root, Path(tmp) / "preview")


    def test_sampling_prefers_rare_category_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            split_dir = root / "val"
            image_dir = split_dir / "images"
            image_dir.mkdir(parents=True)
            images = []
            annotations = []
            for image_id in range(1, 4):
                filename = f"scene_{image_id}.jpg"
                Image.new("RGB", (64, 48), (30, image_id * 30, 120)).save(
                    image_dir / filename
                )
                images.append({
                    "id": image_id,
                    "file_name": filename,
                    "width": 64,
                    "height": 48,
                })
                annotations.append({
                    "id": image_id,
                    "image_id": image_id,
                    "category_id": 1 if image_id < 3 else 2,
                    "bbox": [8, 7, 24, 18],
                })
            payload = {
                "images": images,
                "annotations": annotations,
                "categories": [
                    {"id": 1, "name": "common"},
                    {"id": 2, "name": "rare"},
                ],
            }
            (split_dir / "annotations.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )

            report = generate_annotation_preview(
                root, Path(tmp) / "preview", sample_count=2, seed=17
            )
            sampled_ids = {item["image_id"] for item in report["images"]}
            self.assertIn(3, sampled_ids, "The only image with the rare category should be selected.")
            self.assertEqual(report["sampled_categories"], ["common", "rare"])
            self.assertIn("inverse-frequency category coverage", report["sampling_strategy"])

if __name__ == "__main__":
    unittest.main()
