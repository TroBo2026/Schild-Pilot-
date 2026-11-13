import unittest

from core.decision import decide_prediction


class DecisionTests(unittest.TestCase):
    def test_accepts_clear_prediction(self):
        result = decide_prediction([0.92, 0.05, 0.03], ["A", "B", "C"])
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["label"], "A")

    def test_abstains_when_score_is_low(self):
        result = decide_prediction([0.40, 0.35, 0.25], ["A", "B", "C"])
        self.assertEqual(result["status"], "uncertain")
        self.assertIsNone(result["label"])
        self.assertEqual(result["reason"], "score_too_low")

    def test_abstains_when_top_classes_are_close(self):
        result = decide_prediction([0.46, 0.42, 0.12], ["A", "B", "C"])
        self.assertEqual(result["status"], "uncertain")
        self.assertEqual(result["reason"], "top_classes_too_close")

    def test_normalizes_scores(self):
        result = decide_prediction([92, 5, 3], ["A", "B", "C"])
        self.assertAlmostEqual(result["model_score"], 0.92)

    def test_rejects_invalid_scores(self):
        for scores in ([], [0, 0], [float("nan"), 1], [-0.1, 1]):
            with self.subTest(scores=scores):
                with self.assertRaises(ValueError):
                    decide_prediction(scores, ["A", "B"] if scores else [])

    def test_rejects_length_mismatch(self):
        with self.assertRaises(ValueError):
            decide_prediction([0.9, 0.1], ["only-one"])


if __name__ == "__main__":
    unittest.main()
