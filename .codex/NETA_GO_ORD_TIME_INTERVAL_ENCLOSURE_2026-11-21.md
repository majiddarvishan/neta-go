# ORD-EVID continuous case-time interval enclosure candidate (2026-11-21)

**Status:** report-only continuous enclosure with an added operation-by-operation interval evaluation of the production `fit_one` binary64 path. The bound remains deliberately unproved pending CI and independent review of this implementation; `continuous_interval_bound_proved=false`, `case_time_precision_proved=false`, and all parent reports remain `DRIFT-INCONCLUSIVE`.

## Why endpoint sampling is insufficient

The endpoint sweep in [ORD-EVID time uncertainty preparation](NETA_GO_ORD_TIME_UNCERTAINTY_PREP_2026-11-21.md) evaluates every unique one of the (2^{10}) endpoint assignments, but endpoint samples alone do not bound interior assignments of the ten paired-case time intervals.

## Candidate continuous enclosure

`scripts/qa005_ord_time_interval_bound.py` constructs a conservative independent box for each normalized case-time coordinate.

For paired-case midpoint (x_i), with (x_i in [l_i,u_i]), normalization is:

[
t_i = 2\frac{x_i-x_1}{x_{10}-x_1}-1
]

The ten paired intervals are strictly chronological. For interior cases, monotonicity of this expression gives an enclosing coordinate interval by selecting the appropriate extrema of (x_i), (x_1), and (x_{10}). The first and last normalized coordinates are exactly -1 and +1. The independent coordinate box may include infeasible combinations, which widens rather than narrows the result.

For the approved balanced 5/5 order vector, the regression has an orthogonal intercept/order block. The implementation uses the equivalent closed forms for:

- residualized time sum of squares and time/order covariance;
- time, intercept and order coefficient intervals;
- residual sum-of-squares upper bound;
- leverage for each of the four ((order,time)) corners; and
- the four joint 5m corner-CI envelopes.

Every interval arithmetic operation is outward-rounded with `math.nextafter`. Integer-to-binary64 conversion is enclosed before multiply/divide/subtract, so timestamps above 2^53 are not treated as exactly representable. The candidate also mirrors the production normalization operation order. If the residualized time sum-of-squares lower bound does not clear the production `inverse3()` pivot threshold (`1e-12 * scale`; scale is 10 for this balanced ten-row design), the helper returns an explicit inconclusive result rather than attempting division or silently dropping the assignment.

A second enclosure now evaluates the actual `fit_one()` binary64 operation sequence: X'X/XY accumulation, the fixed no-swap Gauss-Jordan pivot path, pivot tolerance, inverse rows, coefficients, residuals, MSE, covariance, corner contrasts, variance, square root and CI arithmetic. The no-swap pivot sequence is derived from the ten strictly chronological normalized times and balanced 5/5 order: the first two pivots are 10 and the final pivot is the residualized-time Schur complement. If interval evidence cannot prove a pivot clears the production tolerance, the float-path enclosure fails closed.

## Current report fields

Each case-metric now has `case_time_continuous_enclosure` with:
- `continuous_interval_enclosure_complete`;
- `continuous_interval_bound_proved=false` pending independent review;
- normalized per-case time intervals;
- residualized time sum-of-squares interval;
- time-coefficient interval;
- residual sum-of-squares upper bound;
- four joint 5m corner-CI envelopes; and
- whether every corner envelope remains inside the existing fixed margin.

The report-level statistical diagnostic becomes INCONCLUSIVE if any enclosure cannot establish a positive denominator or if a conservative enclosure crosses a fixed bound without a concrete feasible fit showing the violation. OUTSIDE-FIXED-BOUNDS-UNQUALIFIED is reserved for an actual endpoint/process fit outside the bound. Even a complete in-bound enclosure is not a Qualification PASS.

## Validation and limitations

Synthetic tests compare both enclosures against all 1024 endpoint fits and 256 deterministic interior assignments, including the production `fit_one()` time coefficient, corner estimates and all four corner CIs. Additional cases cover exact times, a near-collinear design whose positive residualized sum-of-squares still falls below the production pivot tolerance, large integer timestamps above 2^53, out-of-bound values, invalid order, malformed intervals and nonfinite inputs.

The implementation remains a candidate: the operation-by-operation interval path is intended to enclose every floating-point operation used by production `fit_one`, but the claim is not promoted until the dedicated CI run and independent review pass. The tests are regression evidence, not a formal proof of Python/runtime conformance. The line receipt still bounds a possible case time; it is not the actual case start/end. Host E-VALID, observer overhead, A/A parity, nonlinear drift and independent acceptance remain open.

No heavy benchmark, stress, soak or extended fuzz campaign is run. No baseline/SLA, Performance Gate, public API, wire contract, v1.0.0 source or tag is changed.
