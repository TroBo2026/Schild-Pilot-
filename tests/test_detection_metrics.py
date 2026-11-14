import unittest

from training.detection_metrics import box_iou, evaluate_thresholds


class DetectionMetricsTests(unittest.TestCase):
    def test_iou_for_identical_boxes(self):
        self.assertEqual(box_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)

    def test_iou_for_half_overlap(self):
        self.assertAlmostEqual(box_iou([0, 0, 10, 10], [5, 0, 15, 10]), 1 / 3)

    def test_one_prediction_matches_one_ground_truth(self):
        result = evaluate_thresholds(
            [[{"box": [0, 0, 10, 10], "label": 1, "score": 0.9}]],
            [[{"box": [0, 0, 10, 10], "label": 1}]],
            score_thresholds=[0.5],
        )["best"]
        self.assertEqual((result["true_positives"], result["false_positives"],
                          result["false_negatives"]), (1, 0, 0))
        self.assertEqual(result["f1"], 1.0)

    def test_class_mismatch_is_false_positive_and_false_negative(self):
        result = evaluate_thresholds(
            [[{"box": [0, 0, 10, 10], "label": 2, "score": 0.9}]],
            [[{"box": [0, 0, 10, 10], "label": 1}]],
            score_thresholds=[0.5],
        )["best"]
        self.assertEqual((result["true_positives"], result["false_positives"],
                          result["false_negatives"]), (0, 1, 1))

    def test_ground_truth_can_only_be_matched_once(self):
        result = evaluate_thresholds(
            [[
                {"box": [0, 0, 10, 10], "label": 1, "score": 0.9},
                {"box": [0, 0, 10, 10], "label": 1, "score": 0.8},
            ]],
            [[{"box": [0, 0, 10, 10], "label": 1}]],
            score_thresholds=[0.5],
        )["best"]
        self.assertEqual((result["true_positives"], result["false_positives"],
                          result["false_negatives"]), (1, 1, 0))

    def test_validation_sweep_selects_best_operating_point(self):
        predictions = [
            [
                {"box": [0, 0, 10, 10], "label": 1, "score": 0.9},
                {"box": [20, 20, 30, 30], "label": 1, "score": 0.2},
            ],
            [{"box": [0, 0, 10, 10], "label": 1, "score": 0.4}],
        ]
        ground_truth = [
            [{"box": [0, 0, 10, 10], "label": 1}],
            [{"box": [0, 0, 10, 10], "label": 1}],
        ]
        result = evaluate_thresholds(
            predictions, ground_truth, score_thresholds=[0.1, 0.3, 0.5]
        )
        self.assertEqual(result["best"]["score_threshold"], 0.3)
        self.assertEqual(result["best"]["f1"], 1.0)

    def test_rejects_invalid_boxes_and_thresholds(self):
        with self.assertRaises(ValueError):
            box_iou([0, 0, 0, 1], [0, 0, 1, 1])
        with self.assertRaises(ValueError):
            evaluate_thresholds([[]], [[]], score_thresholds=[1.1])
        with self.assertRaises(ValueError):
            evaluate_thresholds([[]], [[]], score_thresholds=[])


if __name__ == "__main__":
    unittest.main()
