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

    def test_accepts_valid_coco_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                self._make_split(root, split, payload=split.encode())
            report = audit_detection_dataset(root)
            self.assertTrue(report["ok"], report["errors"])
            self.assertEqual(report["splits"]["train"]["annotations"], 1)

    def test_rejects_box_outside_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                self._make_split(root, split, payload=split.encode())
            path = root / "train" / "annotations.json"
            data = json.loads(path.read_text())
            data["annotations"][0]["bbox"] = [90, 70, 20, 20]
            path.write_text(json.dumps(data), encoding="utf-8")
            report = audit_detection_dataset(root)
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
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                self._make_split(root, split, payload=split.encode())
            path = root / "val" / "annotations.json"
            data = json.loads(path.read_text())
            data["annotations"][0]["image_id"] = 999
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(audit_detection_dataset(root)["ok"])


if __name__ == "__main__":
    unittest.main()
