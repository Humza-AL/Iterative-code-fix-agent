import unittest

from buggy_code_working import calculate_average


class CalculateAverageTests(unittest.TestCase):
    def test_normal_input(self):
        self.assertEqual(calculate_average([1, 2, 3, 4]), 2.5)

    def test_empty_list(self):
        self.assertEqual(calculate_average([]), 0)

    def test_negative_and_floating_point_input(self):
        self.assertEqual(calculate_average([-2, 1.5, 3.5]), 1.0)


if __name__ == "__main__":
    unittest.main()
