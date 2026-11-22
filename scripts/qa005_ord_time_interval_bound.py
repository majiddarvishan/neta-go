"""Candidate outward-rounded continuous enclosure for ORD-EVID case-time uncertainty.

The enclosure uses a conservative independent box for normalized per-case time,
then interval arithmetic for the balanced-order regression and four corner CIs.
It is report-only: floating-point equivalence to fit_one still requires review.
"""
from __future__ import annotations

import math


PAIR_COUNT = 10
MAX_PAIR_MIDPOINT_TWICE_NS = (1 << 63) - 1
FIT_ONE_PIVOT_RELATIVE_TOLERANCE = 1e-12


def _finite_interval(value, label):
    if (type(value) is not tuple or len(value) != 2 or
            any(type(item) not in (int, float) or not math.isfinite(item)
                for item in value) or value[0] > value[1]):
        raise ValueError("Invalid interval: " + label)
    return (float(value[0]), float(value[1]))


def _down(value):
    if not math.isfinite(value):
        raise ValueError("Nonfinite lower interval arithmetic result")
    return math.nextafter(value, -math.inf)


def _up(value):
    if not math.isfinite(value):
        raise ValueError("Nonfinite upper interval arithmetic result")
    return math.nextafter(value, math.inf)


def _add(a, b):
    return (_down(a[0] + b[0]), _up(a[1] + b[1]))


def _sub(a, b):
    return (_down(a[0] - b[1]), _up(a[1] - b[0]))


def _mul(a, b):
    products = (
        a[0] * b[0], a[0] * b[1],
        a[1] * b[0], a[1] * b[1],
    )
    return (_down(min(products)), _up(max(products)))


def _square(value):
    if value[0] <= 0 <= value[1]:
        return (0.0, _up(max(value[0] * value[0], value[1] * value[1])))
    squares = (value[0] * value[0], value[1] * value[1])
    return (max(0.0, _down(min(squares))), _up(max(squares)))


def _integer_float_interval(value):
    """Enclose the exact integer after the same int-to-float conversion class.

    Python's int/int true division converts each operand to binary64 before the
    divide. A single nextafter around the final quotient is not enough when
    either integer is above the exact-integer range of binary64.
    """
    if type(value) is not int:
        raise ValueError("Expected exact integer time arithmetic operand")
    try:
        converted = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError("Integer time operand cannot be represented as float") from exc
    if not math.isfinite(converted):
        raise ValueError("Nonfinite converted integer time operand")
    if converted < value:
        return (converted, math.nextafter(converted, math.inf))
    if converted > value:
        return (math.nextafter(converted, -math.inf), converted)
    return (converted, converted)


def _divide_positive(numerator, denominator):
    if denominator[0] <= 0:
        raise ValueError("Interval denominator is not strictly positive")
    reciprocal = (_down(1.0 / denominator[1]),
                  _up(1.0 / denominator[0]))
    return _mul(numerator, reciprocal)


def _scale(value, factor):
    return _mul(value, (float(factor), float(factor)))


def _sum(values):
    result = (0.0, 0.0)
    for value in values:
        result = _add(result, value)
    return result


def _absolute_bounds(value):
    if value[0] <= 0 <= value[1]:
        return (0.0, max(abs(value[0]), abs(value[1])))
    return (min(abs(value[0]), abs(value[1])),
            max(abs(value[0]), abs(value[1])))


def _divide_nonzero(numerator, denominator):
    if denominator[0] <= 0 <= denominator[1]:
        raise ValueError("Floating-point fit pivot interval contains zero")
    reciprocal = (_down(1.0 / denominator[1]),
                  _up(1.0 / denominator[0]))
    return _mul(numerator, reciprocal)


def _quadratic_variance_lower_bound(covariance):
    """Bound x'Cov*x for x in {-1,+1}^3 without interval dependency loss.

    The production corner expression is a nine-term float sum. Its exact
    pre-summation quadratic form equals x'((C+C.T)/2)x. Gershgorin bounds the
    symmetric part from the actual covariance entries enclosed by C. A
    gamma_8 bound plus subnormal allowance covers the eight float additions.
    """
    symmetric = [
        [
            _scale(_add(covariance[i][j], covariance[j][i]), 0.5)
            for j in range(3)
        ]
        for i in range(3)
    ]
    eigenvalue_lower = math.inf
    for i in range(3):
        radius_upper = 0.0
        for j in range(3):
            if i == j:
                continue
            radius_upper = _up(
                radius_upper + _absolute_bounds(symmetric[i][j])[1]
            )
        eigenvalue_lower = min(
            eigenvalue_lower,
            _down(symmetric[i][i][0] - radius_upper),
        )

    absolute_sum_upper = 0.0
    for row in covariance:
        for value in row:
            absolute_sum_upper = _up(
                absolute_sum_upper + _absolute_bounds(value)[1]
            )
    unit_roundoff = 2.0 ** -53
    gamma_8 = _up((8.0 * unit_roundoff) / (1.0 - 8.0 * unit_roundoff))
    addition_rounding = _up(
        gamma_8 * absolute_sum_upper + 8.0 * math.ulp(0.0)
    )
    exact_quadratic_lower = _down(3.0 * eigenvalue_lower)
    return _down(exact_quadratic_lower - addition_rounding)


def _sqrt_nonnegative(value):
    if value[0] < 0 or value[1] < 0:
        raise ValueError("Negative square-root interval")
    lower = math.sqrt(value[0])
    upper = math.sqrt(value[1])
    return (
        0.0 if lower == 0 else max(0.0, _down(lower)),
        _up(upper),
    )


def _fit_one_float_path_enclosure(y, order, time_intervals, margin, critical):
    """Interval-evaluate fit_one's actual binary64 operation sequence.

    The interval Gauss-Jordan path requires a provably unique maximum pivot at
    every column. If interval uncertainty cannot prove the production pivot
    choice or its 1e-12 relative threshold, this helper fails closed.
    """
    n = PAIR_COUNT
    x = [
        ((1.0, 1.0), (float(o), float(o)), t)
        for o, t in zip(order, time_intervals)
    ]
    xtx = [
        [
            _sum([_mul(row[j], row[k]) for row in x])
            for k in range(3)
        ]
        for j in range(3)
    ]
    augmented = [
        list(row) + [
            (1.0, 1.0) if i == j else (0.0, 0.0)
            for j in range(3)
        ]
        for i, row in enumerate(xtx)
    ]
    scale_upper = max(
        _absolute_bounds(value)[1]
        for row in xtx for value in row
    )
    if not math.isfinite(scale_upper) or scale_upper <= 0:
        return {
            "complete": False,
            "reason": "Nonfinite or singular production design scale",
        }

    pivot_tolerance = FIT_ONE_PIVOT_RELATIVE_TOLERANCE * scale_upper
    # The caller supplies ten strictly chronological normalized times with
    # t[0] == -1 and t[9] == +1, and a balanced +/-1 order vector. Therefore:
    # - column 0: |sum(t)| < 8, strictly below the intercept pivot 10;
    # - column 1: |sum(order*t)| <= sum(|t|) < 10, below the order pivot 10;
    # - column 2: only the final Schur pivot remains.
    # This proves inverse3() selects rows 0, 1, 2 without swaps for every
    # feasible time assignment, even if the independent interval box is wider.
    if (sum(order) != 0 or time_intervals[0] != (-1.0, -1.0) or
            time_intervals[-1] != (1.0, 1.0) or
            any(lo < -1.0 or hi > 1.0 or lo > hi
                for lo, hi in time_intervals)):
        return {
            "complete": False,
            "reason": "Production fit_one fixed-pivot proof preconditions are not met",
        }
    for column in range(3):
        pivot = augmented[column][column]
        pivot_lower = _absolute_bounds(pivot)[0]
        if pivot_lower <= pivot_tolerance:
            return {
                "complete": False,
                "reason": "Production fit_one pivot interval does not clear relative tolerance",
                "pivot_column": column,
                "pivot_lower_abs": pivot_lower,
                "pivot_tolerance": pivot_tolerance,
            }
        augmented[column] = [
            _divide_nonzero(value, pivot)
            for value in augmented[column]
        ]
        for row_index in range(3):
            if row_index == column:
                continue
            factor = augmented[row_index][column]
            augmented[row_index] = [
                _sub(value, _mul(factor, pivot_value))
                for value, pivot_value in zip(
                    augmented[row_index], augmented[column]
                )
            ]
    inverse = [row[3:] for row in augmented]

    y_intervals = [(float(value), float(value)) for value in y]
    xty = [
        _sum([_mul(row[j], observation)
              for row, observation in zip(x, y_intervals)])
        for j in range(3)
    ]
    beta = [
        _sum([_mul(value, observation)
              for value, observation in zip(inverse_row, xty)])
        for inverse_row in inverse
    ]
    residuals = [
        _sub(observation, _sum([
            _mul(value, coefficient)
            for value, coefficient in zip(row, beta)
        ]))
        for observation, row in zip(y_intervals, x)
    ]
    mse = _divide_positive(
        _sum([_square(value) for value in residuals]),
        (float(n - 3), float(n - 3)),
    )
    covariance = [
        [_mul(mse, value) for value in row]
        for row in inverse
    ]

    log_limit = math.log1p(margin)
    corner_envelopes = {}
    all_inside = True
    maximum_standard_error_upper = 0.0
    for first_order in (-1, +1):
        for corner_time in (-1, +1):
            row = (
                (1.0, 1.0),
                (float(first_order), float(first_order)),
                (float(corner_time), float(corner_time)),
            )
            estimate = _sum([
                _mul(row[index], beta[index])
                for index in range(3)
            ])
            variance = _sum([
                _mul(_mul(row[i], covariance[i][j]), row[j])
                for i in range(3)
                for j in range(3)
            ])
            variance_lower_after_rounding = _quadratic_variance_lower_bound(
                covariance
            )
            if variance_lower_after_rounding < -1e-12:
                return {
                    "complete": False,
                    "reason": "Production fit_one corner variance may cross rejection threshold",
                    "variance_interval": list(variance),
                    "variance_lower_after_rounding_bound": variance_lower_after_rounding,
                }
            # The Gershgorin/rounding lower bound proves the production float
            # result cannot cross its -1e-12 rejection threshold. For sqrt,
            # zero is therefore a conservative lower bound after max(0, v).
            nonnegative_variance = (
                0.0,
                max(0.0, variance[1]),
            )
            standard_error = _sqrt_nonnegative(nonnegative_variance)
            maximum_standard_error_upper = max(
                maximum_standard_error_upper, standard_error[1]
            )
            half_width = _mul((float(critical), float(critical)), standard_error)
            ci_lower = _sub(estimate, half_width)
            ci_upper = _add(estimate, half_width)
            inside = ci_lower[0] > -log_limit and ci_upper[1] < log_limit
            all_inside = all_inside and inside
            key = "order=%+d,time=%+d" % (first_order, corner_time)
            corner_envelopes[key] = {
                "estimate_log_range": [estimate[0], estimate[1]],
                "ci_log_envelope": [ci_lower[0], ci_upper[1]],
                "inside_fixed_bound": inside,
            }

    return {
        "complete": True,
        "method": "outward-rounded interval evaluation of fit_one binary64 operations",
        "pivot_tolerance_upper": pivot_tolerance,
        "time_coefficient_interval": [beta[2][0], beta[2][1]],
        "maximum_corner_standard_error_upper": maximum_standard_error_upper,
        "joint_5m_corner_ci_envelope": corner_envelopes,
        "all_corner_ci_envelopes_inside_fixed_bounds": all_inside,
    }


def _case_time_scaled_intervals(pair_intervals):
    if not isinstance(pair_intervals, list) or len(pair_intervals) != PAIR_COUNT:
        raise ValueError("Exactly ten paired-case time intervals are required")
    lower = []
    upper = []
    for index, item in enumerate(pair_intervals):
        if (type(item) is not dict or type(item.get("pair")) is not int or
                item.get("pair") != index + 1):
            raise ValueError("Invalid or unordered paired-case time interval")
        lo = item.get("lower_pair_midpoint_twice_ns")
        hi = item.get("upper_pair_midpoint_twice_ns")
        if (type(lo) is not int or type(hi) is not int or
                not 0 < lo <= hi <= MAX_PAIR_MIDPOINT_TWICE_NS):
            raise ValueError("Invalid paired-case time interval endpoints")
        lower.append(lo)
        upper.append(hi)
    if any(upper[i] >= lower[i + 1] for i in range(PAIR_COUNT - 1)):
        raise ValueError("Paired-case time intervals are not strictly chronological")

    first_lower, first_upper = lower[0], upper[0]
    last_lower, last_upper = lower[-1], upper[-1]
    if first_upper >= last_lower:
        raise ValueError("First/last paired-case time intervals overlap")

    scaled = [(-1.0, -1.0)]
    for index in range(1, PAIR_COUNT - 1):
        # t_i = 2 * (x_i - x_1) / (x_10 - x_1) - 1.
        # It increases with x_i and decreases with x_1 and x_10. Enclose
        # each integer-to-binary64 conversion as well as multiply/divide/subtract
        # in the same operation order used by endpoint_sensitivity.
        min_delta = lower[index] - first_upper
        min_span = last_upper - first_upper
        max_delta = upper[index] - first_lower
        max_span = last_lower - first_lower
        if min_span <= 0 or max_span <= 0:
            raise ValueError("Invalid normalized case-time denominator")
        min_ratio = _divide_positive(
            _scale(_integer_float_interval(min_delta), 2.0),
            _integer_float_interval(min_span),
        )
        max_ratio = _divide_positive(
            _scale(_integer_float_interval(max_delta), 2.0),
            _integer_float_interval(max_span),
        )
        min_time = _sub(min_ratio, (1.0, 1.0))
        max_time = _sub(max_ratio, (1.0, 1.0))
        # Exact chronology guarantees the normalized value is in [-1, 1].
        lo = max(-1.0, min_time[0])
        hi = min(1.0, max_time[1])
        if lo > hi:
            raise ValueError("Normalized case-time interval outside [-1,1]")
        scaled.append((lo, hi))
    scaled.append((1.0, 1.0))
    return scaled


def continuous_interval_enclosure(y, order, pair_intervals, margin,
                                  joint_corner_critical):
    """Return an interval enclosure for all case-time assignments in the input box.

    The independent normalized-time box is a superset of the feasible normalized
    vectors. Interval arithmetic then encloses the exact balanced-order OLS
    coefficients and the four simultaneous corner confidence intervals.
    """
    if len(y) != PAIR_COUNT or len(order) != PAIR_COUNT:
        raise ValueError("Ten paired log ratios and order values are required")
    if any(type(value) not in (int, float) or not math.isfinite(value)
           for value in y):
        raise ValueError("Invalid paired log ratio")
    if any(type(value) is not int or value not in (-1, +1) for value in order):
        raise ValueError("Invalid first-side order")
    if sum(order) != 0:
        raise ValueError("Continuous enclosure requires balanced 5/5 order")
    if margin not in (.05, .075):
        raise ValueError("Unexpected approved fixed margin")
    if (type(joint_corner_critical) not in (int, float) or
            not math.isfinite(joint_corner_critical) or
            joint_corner_critical <= 0):
        raise ValueError("Invalid joint corner critical value")

    log_limit = math.log1p(margin)
    t = _case_time_scaled_intervals(pair_intervals)
    t_intervals = [_finite_interval(value, "normalized time") for value in t]
    y_intervals = [(float(value), float(value)) for value in y]
    order_intervals = [(float(value), float(value)) for value in order]
    n = PAIR_COUNT
    inv_n = (_down(1.0 / n), _up(1.0 / n))

    sum_t = _sum(t_intervals)
    sum_ot = _sum([
        _mul(o, value) for o, value in zip(order_intervals, t_intervals)
    ])
    sum_t2 = _sum([_square(value) for value in t_intervals])
    sum_y = _sum(y_intervals)
    sum_oy = _sum([
        _mul(o, value) for o, value in zip(order_intervals, y_intervals)
    ])
    sum_ty = _sum([
        _mul(t_value, y_value)
        for t_value, y_value in zip(t_intervals, y_intervals)
    ])
    sum_y2 = _sum([_square(value) for value in y_intervals])

    # The order vector is balanced: 1 and order are orthogonal columns.
    sst = _sub(
        _sub(sum_t2, _mul(_square(sum_t), inv_n)),
        _mul(_square(sum_ot), inv_n),
    )
    # fit_one() uses inverse3() with a relative pivot rejection threshold
    # of 1e-12 * scale. For a chronological, balanced ten-row design, the
    # first two diagonal pivots are exactly 10 and the final Schur pivot is
    # residualized time SS; all other X'X entries have magnitude < 10.
    # Therefore scale == 10 and the production final-pivot threshold is 1e-11.
    fit_one_pivot_tolerance = FIT_ONE_PIVOT_RELATIVE_TOLERANCE * float(n)
    if sst[0] <= fit_one_pivot_tolerance:
        return {
            "method": "outward-rounded interval arithmetic over an independent normalized-time box",
            "continuous_interval_enclosure_complete": False,
            "continuous_interval_bound_proved": False,
            "reason": (
                "Residualized time sum-of-squares lower bound does not exceed "
                "the production fit_one pivot tolerance"
            ),
            "fit_one_pivot_tolerance": fit_one_pivot_tolerance,
            "residualized_time_sum_squares_interval": list(sst),
            "normalized_case_time_intervals": [list(value) for value in t_intervals],
            "qualification": "DRIFT-INCONCLUSIVE",
        }

    syt = _sub(
        _sub(sum_ty, _mul(_mul(sum_t, sum_y), inv_n)),
        _mul(_mul(sum_ot, sum_oy), inv_n),
    )
    beta_time = _divide_positive(syt, sst)
    mean_y = _mul(sum_y, inv_n)
    mean_order_y = _mul(sum_oy, inv_n)
    mean_t = _mul(sum_t, inv_n)
    mean_order_t = _mul(sum_ot, inv_n)
    beta_intercept = _sub(mean_y, _mul(beta_time, mean_t))
    beta_order = _sub(mean_order_y, _mul(beta_time, mean_order_t))

    sse = _sub(
        _sub(
            _sub(sum_y2, _mul(beta_intercept, sum_y)),
            _mul(beta_order, sum_oy),
        ),
        _mul(beta_time, sum_ty),
    )
    if sse[1] < 0:
        return {
            "method": "outward-rounded interval arithmetic over an independent normalized-time box",
            "continuous_interval_enclosure_complete": False,
            "continuous_interval_bound_proved": False,
            "reason": "Residual sum-of-squares upper bound is negative",
            "residualized_time_sum_squares_interval": list(sst),
            "residual_sum_squares_interval": list(sse),
            "normalized_case_time_intervals": [list(value) for value in t_intervals],
            "qualification": "DRIFT-INCONCLUSIVE",
        }

    mse_upper = _up(max(0.0, sse[1]) / (n - 3))
    critical_upper = _up(float(joint_corner_critical))
    corner_envelopes = {}
    standard_error_uppers = []
    all_inside = True
    for first_order in (-1, +1):
        for corner_time in (-1, +1):
            estimate = _add(
                _add(beta_intercept, _scale(beta_order, first_order)),
                _scale(beta_time, corner_time),
            )
            residualized_corner = _sub(
                _sub((float(corner_time), float(corner_time)), mean_t),
                _scale(mean_order_t, first_order),
            )
            leverage = _add(
                _add(inv_n, inv_n),
                _divide_positive(_square(residualized_corner), sst),
            )
            variance_upper = _up(mse_upper * leverage[1])
            standard_error_upper = _up(math.sqrt(max(0.0, variance_upper)))
            standard_error_uppers.append(standard_error_upper)
            ci_lower = _down(estimate[0] - critical_upper * standard_error_upper)
            ci_upper = _up(estimate[1] + critical_upper * standard_error_upper)
            inside = ci_lower > -log_limit and ci_upper < log_limit
            all_inside = all_inside and inside
            key = "order=%+d,time=%+d" % (first_order, corner_time)
            corner_envelopes[key] = {
                "estimate_log_range": list(estimate),
                "ci_log_envelope": [ci_lower, ci_upper],
                "inside_fixed_bound": inside,
            }

    production_float_path = _fit_one_float_path_enclosure(
        y, order, t_intervals, margin, joint_corner_critical
    )
    if not production_float_path["complete"]:
        return {
            "method": (
                "outward-rounded interval arithmetic plus production fit_one "
                "binary64 operation enclosure"
            ),
            "continuous_interval_enclosure_complete": False,
            "continuous_interval_bound_proved": False,
            "reason": production_float_path["reason"],
            "production_fit_one_float_path_enclosure": production_float_path,
            "normalized_case_time_intervals": [list(value) for value in t_intervals],
            "residualized_time_sum_squares_interval": list(sst),
            "fit_one_pivot_tolerance": fit_one_pivot_tolerance,
            "qualification": "DRIFT-INCONCLUSIVE",
        }

    return {
        "method": (
            "outward-rounded independent normalized-time box, balanced-order "
            "OLS closed form, and production fit_one binary64 operation enclosure"
        ),
        "continuous_interval_enclosure_complete": True,
        # Keep this false pending independent review of equivalence to the
        # production fit_one floating-point implementation.
        "continuous_interval_bound_proved": False,
        "case_time_precision_proved": False,
        "normalized_case_time_intervals": [list(value) for value in t_intervals],
        "residualized_time_sum_squares_interval": list(sst),
        "fit_one_pivot_tolerance": fit_one_pivot_tolerance,
        "residual_sum_squares_upper": sse[1],
        "time_coefficient_log_ratio_per_normalized_window_interval": list(beta_time),
        "maximum_corner_standard_error_upper": max(standard_error_uppers),
        "closed_form_joint_5m_corner_ci_envelope": corner_envelopes,
        "production_fit_one_float_path_enclosure": production_float_path,
        "production_fit_one_time_coefficient_interval": production_float_path["time_coefficient_interval"],
        "joint_5m_corner_ci_envelope": production_float_path["joint_5m_corner_ci_envelope"],
        "fixed_margin_log": log_limit,
        "all_corner_ci_envelopes_inside_fixed_bounds": production_float_path["all_corner_ci_envelopes_inside_fixed_bounds"],
        "continuous_interval_bound_status": (
            "ENCLOSURE_WITHIN_FIXED_BOUNDS_UNPROVEN"
            if production_float_path["all_corner_ci_envelopes_inside_fixed_bounds"]
            else "ENCLOSURE_EXPOSES_OUT_OF_BOUND_POSSIBILITY"
        ),
        "qualification": "DRIFT-INCONCLUSIVE",
    }
