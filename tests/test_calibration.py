import unittest

from training.calibrate_thresholds import calibrate_thresholds


class CalibrationTests(unittest.TestCase):
    def test_returns_thresholds_meeting_minimum_coverage(self):
        labels = [0, 0, 1, 1, 2]
        probabilities = [
            [0.95, 0.03, 0.02],
            [0.60, 0.35, 0.05],
            [0.10, 0.85, 0.05],
            [0.48, 0.45, 0.07],
            [0.05, 0.10, 0.85],
        ]
        result = calibrate_thresholds(labels, probabilities, min_coverage=0.80)
        self.assertGreaterEqual(result["coverage"], 0.80)
        self.assertGreaterEqual(result["min_score"], 0.0)
        self.assertGreaterEqual(result["min_margin"], 0.0)
        self.assertEqual(result["validation_samples"], 5)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            calibrate_thresholds([], [], min_coverage=0.8)
        with self.assertRaises(ValueError):
            calibrate_thresholds([0], [[0.5, 0.5]], min_coverage=0)
        with self.assertRaises(ValueError):
            calibrate_thresholds([0], [[0, 0]], min_coverage=0.8)


if __name__ == "__main__":
    unittest.main()
