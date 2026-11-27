import stat
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from training.extract_traffic_signs_raw import extract_traffic_signs_raw


class TrafficSignsRawSafeExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive = self.root / "source.zip"
        self.destination = self.root / "extracted"

    def tearDown(self):
        self.temp.cleanup()

    def write_archive(self, entries):
        with zipfile.ZipFile(self.archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries:
                if isinstance(name, zipfile.ZipInfo):
                    archive.writestr(name, data)
                else:
                    archive.writestr(name, data)

    def valid_entries(self, extra=()):
        return [
            ("bundle/traffic_signs_raw/README.md", "TrafficSigns-Raw"),
            ("bundle/traffic_signs_raw/Train_Data/images/train/a.jpg", "image-bytes"),
            ("bundle/LICENSES/traffic_signs_license.txt", "CC BY 4.0"),
            ("bundle/unrelated/large.bin", "not-selected" * 100),
            *extra,
        ]

    def test_extracts_only_raw_dataset_and_license(self):
        self.write_archive(self.valid_entries())
        report = extract_traffic_signs_raw(self.archive, self.destination)

        self.assertTrue((self.destination / "bundle/traffic_signs_raw/README.md").is_file())
        self.assertTrue((self.destination / "bundle/traffic_signs_raw/Train_Data/images/train/a.jpg").is_file())
        self.assertTrue((self.destination / "bundle/LICENSES/traffic_signs_license.txt").is_file())
        self.assertFalse((self.destination / "bundle/unrelated").exists())
        self.assertEqual(report["files_extracted"], 3)
        self.assertEqual(
            (self.destination / "traffic_signs_raw_source_path.txt").read_text(),
            "bundle/traffic_signs_raw/",
        )

    def test_rejects_parent_traversal_in_selected_path(self):
        self.write_archive(self.valid_entries([
            ("bundle/traffic_signs_raw/../escape.txt", "nope"),
        ]))
        with self.assertRaisesRegex(ValueError, "Unsicherer ZIP-Pfad"):
            extract_traffic_signs_raw(self.archive, self.destination)
        self.assertFalse(self.destination.exists())

    def test_rejects_absolute_selected_path(self):
        self.write_archive([
            ("/bundle/traffic_signs_raw/README.md", "TrafficSigns-Raw"),
            ("bundle/LICENSES/traffic_signs_license.txt", "CC BY 4.0"),
        ])
        with self.assertRaisesRegex(ValueError, "Absoluter ZIP-Pfad"):
            extract_traffic_signs_raw(self.archive, self.destination)

    def test_rejects_backslash_paths(self):
        self.write_archive([
            (r"bundle\\traffic_signs_raw\\README.md", "TrafficSigns-Raw"),
            ("bundle/LICENSES/traffic_signs_license.txt", "CC BY 4.0"),
        ])
        with self.assertRaisesRegex(ValueError, "README"):
            extract_traffic_signs_raw(self.archive, self.destination)

    def test_rejects_symbolic_links(self):
        link = zipfile.ZipInfo("bundle/traffic_signs_raw/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.write_archive(self.valid_entries([(link, "target")]))
        with self.assertRaisesRegex(ValueError, "Symbolischer Link"):
            extract_traffic_signs_raw(self.archive, self.destination)

    def test_enforces_expanded_total_size_limit(self):
        self.write_archive(self.valid_entries())
        with self.assertRaisesRegex(ValueError, "Gesamtgrößenlimit"):
            extract_traffic_signs_raw(
                self.archive, self.destination, max_total_bytes=10, max_file_bytes=100
            )

    def test_enforces_single_file_size_limit(self):
        self.write_archive(self.valid_entries())
        with self.assertRaisesRegex(ValueError, "Einzeldateilimit"):
            extract_traffic_signs_raw(
                self.archive, self.destination, max_total_bytes=100, max_file_bytes=5
            )

    def test_enforces_file_count_limit(self):
        self.write_archive(self.valid_entries())
        with self.assertRaisesRegex(ValueError, "Dateianzahl-Limit"):
            extract_traffic_signs_raw(
                self.archive, self.destination, max_total_bytes=100, max_file_bytes=100,
                max_files=2,
            )

    def test_refuses_existing_destination(self):
        self.destination.mkdir()
        with self.assertRaises(FileExistsError):
            extract_traffic_signs_raw(self.archive, self.destination)

    def test_rejects_invalid_limits(self):
        self.write_archive(self.valid_entries())
        with self.assertRaises(ValueError):
            extract_traffic_signs_raw(self.archive, self.destination, max_total_bytes=True)


if __name__ == "__main__":
    unittest.main()
