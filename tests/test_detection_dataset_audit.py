import json
import tempfile
import unittest
from pathlib import Path

from training.audit_detection_dataset import audit_detection_dataset


class DetectionDatasetAuditTests(unittest.TestCase):
    def _make_split(self, root: Path, split: str, payload: bytes = b"image") -> None:
        folder = root / split
        (folder / "images").mkdir(parents=True)
        (folder / "images" / "scene.jpg").write_bytes(payload)
        data = {
            "images": [{"id": 1, "file_name": "scene.jpg", "width": 100, "height": 80}],
            "annotations": [{"id": 1, "image_id": 1, "category_id": 4, "bbox": [10, 12, 30, 20]}],
            "categories": [{"id": 4, "name": "traffic_sign"}],
        }
        (folder / "annotations.json").write_text(json.dumps(data), encoding="utf-8")

    def _audit_with_train_mutation(self, mutate) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                self._make_split(root, split, payload=split.encode())
            path = root / "train" / "annotations.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            mutate(data)
            path.write_text(json.dumps(data), encoding="utf-8")
            return audit_detection_dataset(root)

    def test_accepts_valid_coco_splits_and_reports_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                self._make_split(root, split, payload=split.encode())
            report = audit_detection_dataset(root)
            self.assertTrue(report["ok"], report["errors"])
            train = report["splits"]["train"]
            self.assertEqual(train["annotations"], 1)
            self.assertEqual(train["annotations_by_category"], {"4": 1})
            self.assertEqual(train["images_without_annotations"], 0)
            self.assertAlmostEqual(train["bbox_area_ratio"]["median"], 0.075)

    def test_rejects_box_outside_image(self):
        report = self._audit_with_train_mutation(
            lambda data: data["annotations"][0].update(bbox=[90, 70, 20, 20])
        )
        self.assertFalse(report["ok"])
        self.assertTrue(any("Bounding Box" in error for error in report["errors"]))

    def test_rejects_exact_duplicates_across_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                self._make_split(root, split, payload=b"same bytes")
            report = audit_detection_dataset(root)
            self.assertFalse(report["ok"])
            self.assertEqual(len(report["exact_duplicates"]), 1)

    def test_rejects_unknown_image_reference(self):
        report = self._audit_with_train_mutation(
            lambda data: data["annotations"][0].update(image_id=999)
        )
        self.assertFalse(report["ok"])

    def test_rejects_non_integer_or_non_positive_category_ids(self):
        for invalid in (True, 1.5, "4", 0, -1, []):
            with self.subTest(invalid=invalid):
                report = self._audit_with_train_mutation(
                    lambda data, value=invalid: data["categories"][0].update(id=value)
                )
                self.assertFalse(report["ok"])

    def test_rejects_invalid_ids_without_crashing(self):
        mutations = (
            lambda data: data["images"][0].update(id=[]),
            lambda data: data["annotations"][0].update(id=True),
            lambda data: data["annotations"][0].update(image_id={}),
            lambda data: data["annotations"][0].update(category_id=[]),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                report = self._audit_with_train_mutation(mutate)
                self.assertFalse(report["ok"])

    def test_rejects_non_integer_or_invalid_image_dimensions(self):
        mutations = (
            lambda data: data["images"][0].update(width=True),
            lambda data: data["images"][0].update(height=80.0),
            lambda data: data["images"][0].update(width=0),
            lambda data: data["images"][0].update(height=float("nan")),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                report = self._audit_with_train_mutation(mutate)
                self.assertFalse(report["ok"])

    def test_rejects_boolean_box_coordinates(self):
        report = self._audit_with_train_mutation(
            lambda data: data["annotations"][0].update(bbox=[True, 12, 30, 20])
        )
        self.assertFalse(report["ok"])
        self.assertTrue(any("Bounding Box" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
