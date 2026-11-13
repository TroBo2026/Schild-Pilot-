import unittest

from training.prepare_traffic_signs_raw import yolo_to_coco


class TrafficSignsRawConversionTests(unittest.TestCase):
    def test_yolo_box_converts_to_absolute_coco_xywh(self):
        category, bbox = yolo_to_coco("0 0.5 0.5 0.2 0.4", 100, 200)
        self.assertEqual(category, 1)
        self.assertEqual(bbox, [40.0, 60.0, 20.0, 80.0])

    def test_second_class_maps_to_category_two(self):
        category, _ = yolo_to_coco("1 0.5 0.5 0.2 0.2", 100, 100)
        self.assertEqual(category, 2)

    def test_clips_box_crossing_image_boundary(self):
        category, bbox = yolo_to_coco("0 0.02 0.5 0.2 0.2", 100, 100)
        self.assertEqual(category, 1)
        self.assertEqual(bbox, [0.0, 40.0, 12.0, 20.0])

    def test_rejects_unknown_class(self):
        with self.assertRaises(ValueError):
            yolo_to_coco("2 0.5 0.5 0.2 0.2", 100, 100)


if __name__ == "__main__":
    unittest.main()
