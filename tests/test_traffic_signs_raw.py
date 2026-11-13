import unittest

from training.prepare_traffic_signs_raw import yolo_to_coco


class TrafficSignsRawConversionTests(unittest.TestCase):
    def test_converts_normal_box(self):
        category, box = yolo_to_coco("0 0.5 0.5 0.2 0.4", 200, 100)
        self.assertEqual(category, 1)
        self.assertEqual(box, [80.0, 30.0, 40.0, 40.0])

    def test_clips_box_crossing_left_and_top_edges(self):
        category, box = yolo_to_coco("1 0.05 0.05 0.2 0.2", 100, 100)
        self.assertEqual(category, 2)
        self.assertEqual(box, [0.0, 0.0, 15.0, 15.0])

    def test_rejects_fully_outside_box(self):
        with self.assertRaises(ValueError):
            yolo_to_coco("0 1.2 0.5 0.1 0.1", 100, 100)

    def test_rejects_unknown_class(self):
        with self.assertRaises(ValueError):
            yolo_to_coco("2 0.5 0.5 0.2 0.2", 100, 100)


if __name__ == "__main__":
    unittest.main()
