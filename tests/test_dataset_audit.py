import tempfile
import unittest
from pathlib import Path

from training.audit_dataset import audit_dataset


class DatasetAuditTests(unittest.TestCase):
    def _make_split(self, root: Path, split: str, class_name: str = "speed_limit") -> Path:
        folder = root / split / class_name
        folder.mkdir(parents=True)
        return folder

    def test_accepts_matching_nonempty_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                (self._make_split(root, split) / f"{split}.jpg").write_bytes(split.encode())
            report = audit_dataset(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["splits"]["train"]["images"], 1)

    def test_rejects_missing_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_split(root, "train")
            self._make_split(root, "val")
            report = audit_dataset(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("test" in error for error in report["errors"]))

    def test_rejects_class_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for split in ("train", "val", "test"):
                name = "speed_limit" if split != "test" else "stop"
                (self._make_split(root, split, name) / "one.jpg").write_bytes(split.encode())
            self.assertFalse(audit_dataset(root)["ok"])

    def test_detects_exact_duplicate_across_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = b"same image bytes"
            for split in ("train", "val", "test"):
                (self._make_split(root, split) / "same.jpg").write_bytes(payload)
            report = audit_dataset(root)
            self.assertFalse(report["ok"])
            self.assertEqual(len(report["exact_duplicates"]), 1)


if __name__ == "__main__":
    unittest.main()
