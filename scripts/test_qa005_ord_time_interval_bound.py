"""Synthetic tests for the continuous case-time interval enclosure candidate."""
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from qa005_ord_drift import cached_student_t_critical, fit_one
from qa005_ord_time_interval_bound import (
    _case_time_scaled_intervals,
    continuous_interval_enclosure,
)


ORDER = [1 if i % 2 == 0 else -1 for i in range(10)]
TIME = [-1 + 2 * i / 9 for i in range(10)]
Y = [0.015 * value for value in TIME]
FAMILY_SIZE = 5
MARGIN = .075
CRITICAL = cached_student_t_critical(.05 / (5 * FAMILY_SIZE), 7)


def make_intervals(width_ns=200_000_000):
    intervals = []
    for index in range(10):
        lower = 2 * (1_000_000_000 + index * 1_000_000_000)
        upper = lower + 2 * width_ns
        intervals.append({
            "pair": index + 1,
            "lower_pair_midpoint_twice_ns": lower,
            "upper_pair_midpoint_twice_ns": upper,
            "width_pair_midpoint_ns": width_ns,
        })
    return intervals


def fit_for_raw_times(y, order, raw_times, margin=MARGIN):
    span = raw_times[-1] - raw_times[0]
    scaled = [2.0 * (value - raw_times[0]) / span - 1.0
              for value in raw_times]
    return fit_one(y, order, scaled, margin, FAMILY_SIZE)


class ContinuousTimeIntervalEnclosureTests(unittest.TestCase):
    def assert_fit_inside_enclosure(self, fit, enclosure, raw_times=None):
        self.assertTrue(enclosure["continuous_interval_enclosure_complete"])
        self.assertFalse(enclosure["continuous_interval_bound_proved"])
        self.assertFalse(enclosure["case_time_precision_proved"])
        for corner in fit["joint_5m_corners"]:
            key = "order=%+d,time=%+d" % (
                corner["first_side_order"], int(corner["scaled_time"])
            )
            envelope = enclosure["joint_5m_corner_ci_envelope"][key]["ci_log_envelope"]
            self.assertLessEqual(envelope[0], corner["ci_log"][0] + 1e-12)
            self.assertGreaterEqual(envelope[1], corner["ci_log"][1] - 1e-12)
        beta = fit["model_coefficients_mean_order_time"][2]
        slope = enclosure[
            "time_coefficient_log_ratio_per_normalized_window_interval"
        ]
        self.assertLessEqual(slope[0], beta + 1e-12)
        self.assertGreaterEqual(slope[1], beta - 1e-12)

    def test_exact_case_times_produce_complete_enclosure(self):
        intervals = make_intervals(width_ns=0)
        result = continuous_interval_enclosure(
            Y, ORDER, intervals, MARGIN, CRITICAL
        )
        self.assertTrue(result["continuous_interval_enclosure_complete"])
        self.assertFalse(result["continuous_interval_bound_proved"])
        self.assertEqual(result["qualification"], "DRIFT-INCONCLUSIVE")
        exact = [item["lower_pair_midpoint_twice_ns"] for item in intervals]
        self.assert_fit_inside_enclosure(
            fit_for_raw_times(Y, ORDER, exact), result, exact
        )

    def test_all_endpoint_and_deterministic_interior_fits_are_enclosed(self):
        intervals = make_intervals(width_ns=200_000_000)
        result = continuous_interval_enclosure(
            Y, ORDER, intervals, MARGIN, CRITICAL
        )
        self.assertTrue(result["continuous_interval_enclosure_complete"])
        lower = [item["lower_pair_midpoint_twice_ns"] for item in intervals]
        upper = [item["upper_pair_midpoint_twice_ns"] for item in intervals]

        for mask in range(1 << 10):
            raw = [upper[i] if mask & (1 << i) else lower[i]
                   for i in range(10)]
            self.assert_fit_inside_enclosure(
                fit_for_raw_times(Y, ORDER, raw), result, raw
            )

        for sample in range(256):
            raw = [
                lower[i] + ((sample * 37 + i * 101) % 997) / 996
                * (upper[i] - lower[i])
                for i in range(10)
            ]
            self.assert_fit_inside_enclosure(
                fit_for_raw_times(Y, ORDER, raw), result
            )

    def test_wide_box_with_near_collinear_order_fails_closed(self):
        order = [1] * 5 + [-1] * 5
        result = continuous_interval_enclosure(
            [0.0] * 10, order, make_intervals(500_000_000), .05, CRITICAL
        )
        self.assertFalse(result["continuous_interval_enclosure_complete"])
        self.assertFalse(result["continuous_interval_bound_proved"])
        self.assertIn("sum-of-squares lower bound is nonpositive", result["reason"])
        self.assertEqual(result["qualification"], "DRIFT-INCONCLUSIVE")

    def test_near_singular_box_respects_production_fit_one_pivot_threshold(self):
        epsilon = 5e-7
        normalized = (
            [-1 + index * epsilon for index in range(5)] +
            [1 - (9 - index) * epsilon for index in range(5, 10)]
        )
        raw_times = [
            1_000_000_000 + round((value + 1) * 500_000_000)
            for value in normalized
        ]
        intervals = [
            {
                "pair": index + 1,
                "lower_pair_midpoint_twice_ns": 2 * value,
                "upper_pair_midpoint_twice_ns": 2 * value,
            }
            for index, value in enumerate(raw_times)
        ]
        result = continuous_interval_enclosure(
            [0.0] * 10, [1] * 5 + [-1] * 5, intervals, .05, CRITICAL
        )
        self.assertFalse(result["continuous_interval_enclosure_complete"])
        self.assertIn("production fit_one pivot tolerance", result["reason"])
        lower, upper = result["residualized_time_sum_squares_interval"]
        self.assertGreater(lower, 0)
        self.assertLessEqual(lower, result["fit_one_pivot_tolerance"])
        self.assertEqual(result["fit_one_pivot_tolerance"], 1e-11)
        with self.assertRaisesRegex(ValueError, "numerically singular"):
            fit_one([0.0] * 10, [1] * 5 + [-1] * 5,
                    [2.0 * (value - raw_times[0]) /
                     (raw_times[-1] - raw_times[0]) - 1.0
                     for value in raw_times], .05, FAMILY_SIZE)

    def test_large_integer_time_normalization_encloses_python_float_operations(self):
        base = 1 << 60
        span = 1 << 54
        step = span // 9
        width = 1 << 20
        pair_intervals = [
            {
                "pair": index + 1,
                "lower_pair_midpoint_twice_ns": 2 * (base + index * step),
                "upper_pair_midpoint_twice_ns": 2 * (base + index * step + width),
            }
            for index in range(10)
        ]
        enclosed = _case_time_scaled_intervals(pair_intervals)
        for mask in range(1 << 10):
            raw = [
                item["upper_pair_midpoint_twice_ns"] // 2
                if mask & (1 << index)
                else item["lower_pair_midpoint_twice_ns"] // 2
                for index, item in enumerate(pair_intervals)
            ]
            actual = [
                2.0 * (value - raw[0]) / (raw[-1] - raw[0]) - 1.0
                for value in raw
            ]
            for index, value in enumerate(actual):
                self.assertLessEqual(enclosed[index][0], value)
                self.assertGreaterEqual(enclosed[index][1], value)

    def test_out_of_bound_corner_envelope_is_not_hidden(self):
        result = continuous_interval_enclosure(
            [0.5] * 10, ORDER, make_intervals(100_000_000), .05, CRITICAL
        )
        self.assertTrue(result["continuous_interval_enclosure_complete"])
        self.assertFalse(result["all_corner_ci_envelopes_inside_fixed_bounds"])
        self.assertEqual(
            result["continuous_interval_bound_status"],
            "ENCLOSURE_EXPOSES_OUT_OF_BOUND_POSSIBILITY",
        )
        self.assertEqual(result["qualification"], "DRIFT-INCONCLUSIVE")

    def test_unbalanced_order_and_malformed_intervals_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "balanced 5/5"):
            continuous_interval_enclosure(
                Y, [1] * 9 + [-1], make_intervals(), MARGIN, CRITICAL
            )
        intervals = make_intervals()
        intervals[0]["pair"] = True
        with self.assertRaisesRegex(ValueError, "paired-case time interval"):
            continuous_interval_enclosure(Y, ORDER, intervals, MARGIN, CRITICAL)
        intervals = make_intervals()
        intervals[0]["lower_pair_midpoint_twice_ns"] = True
        with self.assertRaisesRegex(ValueError, "endpoints"):
            continuous_interval_enclosure(Y, ORDER, intervals, MARGIN, CRITICAL)
        intervals = make_intervals()
        intervals[0]["lower_pair_midpoint_twice_ns"] = 1 << 100
        intervals[0]["upper_pair_midpoint_twice_ns"] = 1 << 100
        with self.assertRaisesRegex(ValueError, "endpoints"):
            continuous_interval_enclosure(Y, ORDER, intervals, MARGIN, CRITICAL)

    def test_nonfinite_y_or_critical_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "paired log ratio"):
            continuous_interval_enclosure(
                [float("nan")] + Y[1:], ORDER, make_intervals(), MARGIN, CRITICAL
            )
        with self.assertRaisesRegex(ValueError, "critical value"):
            continuous_interval_enclosure(
                Y, ORDER, make_intervals(), MARGIN, float("inf")
            )


if __name__ == "__main__":
    unittest.main()
