# ORD-EVID case-time uncertainty sensitivity (2026-11-21)

**Status:** report-only software-readiness increment. It does **not** establish per-case execution timestamps, a continuous uncertainty bound, E-VALID, DRIFT-VALID, a reference-host admission, a numeric baseline/SLA, or a Performance Gate. Parent work item **QENV-AA-02.ORD-EVID remains OPEN**.

## Problem addressed

The line observer records the interval in which the Python process reads a complete output line. The only currently defensible per-side case-time interval remains:

`[parent pre-spawn snapshot, line receipt]`

This is deliberately broad. Go test output buffering may defer a result line until after benchmark work has finished; the pipe may already contain bytes before `os.read` begins; Python may be descheduled between the read and the post-read clock sample; and synchronous sidecar serialization/writes can backpressure the pipe. A line receipt is therefore an upper bound, not the case's actual start, end, or execution midpoint.

The prior 5m model uses the midpoint of the two whole-process intervals for each pair. Until now, it did not quantify how the fitted order/time coefficient and four corner confidence intervals could change when each case's actual paired time is somewhere inside its receipt-derived uncertainty interval.

## Added report-only diagnostic

`scripts/qa005_ord_time_uncertainty.py` derives a per-case paired midpoint interval from both sides:

- Each side contributes its verified `[earliest_possible_case_ns, latest_possible_case_ns]`.
- The paired-case midpoint lower/upper bounds are the arithmetic means of the baseline and candidate side bounds.
- Doubled nanoseconds preserve exact integer arithmetic for half-nanosecond midpoints.
- Missing, duplicated, contradictory, Boolean-spoofed, reversed, or cross-pair-overlapping evidence is rejected.

For each case-metric, the analyzer passes every **unique one of the (2^{10}=1024) pair-interval endpoint assignments** through the existing `fit_one` implementation, preserving the owner-approved 5m Bonferroni model and existing 5%/7.5% margins. It reports:

- the sampled range of the time coefficient;
- maximum sampled design condition;
- the four joint 5m corner-CI envelopes;
- sampled assignments outside the fixed bounds;
- invalid/singular endpoint fits and their reasons; and
- the exact paired-case interval widths and endpoint values.

Repeated Student-t critical values are cached; the diagnostic does not invoke Go benchmarks or change the comparator.

## Interpretation and limits

This is an **endpoint sensitivity sweep**, not a proof over the continuous product of ten intervals. A rational regression fit can have interior extrema or near-singular designs that are not represented by interval endpoints. Consequently:

- `continuous_interval_bound_proved=false` and `case_time_precision_proved=false` are unconditional.
- Any invalid endpoint fit is `INCONCLUSIVE_INVALID_ENDPOINT_FIT`.
- Any sampled endpoint outside the fixed bounds is reported as an unqualified out-of-bound assignment.
- If every sampled endpoint is within bounds, the status remains `ENDPOINT_SWEEP_WITHIN_FIXED_BOUNDS_UNPROVEN`.
- Every parent report still has `qualification=DRIFT-INCONCLUSIVE`, `environment_validity=E-UNKNOWN`, `host_mode_admission=NOT_PERFORMED`, and `performance_gate=DISABLED`.

The original process-midpoint model remains visible as a separate diagnostic; the endpoint sweep does not silently replace its approved model or claim the line receipt is the true case time.

## Buffering, pipe and observer effects

A new synthetic subprocess test writes a benchmark result to a non-interactive buffered stdout, records completion of simulated work, delays, and only then flushes. It verifies that the observer's receipt timestamp can be later than the simulated case completion. This tests the limitation; it does not model or qualify Go's exact internal buffering behavior.

Static observer-path review also confirms that:
- the timestamp brackets `os.read`, not the time the producer first placed bytes in the pipe;
- scheduler delay before the post-read clock can widen the bracket;
- JSON encoding, SHA-256, and synchronous sidecar writes are performed on the reader path; and
- a slow sidecar write can delay further pipe reads and eventually backpressure the benchmark process.

No observer overhead percentage or sampling-error threshold is introduced. Those require a separately authorized, controlled-host comparison with exact source/fixture parity and paired evidence. The synthetic tests are not a substitute for that experiment.

## Lightweight verification scope

The Phase-Q ORD-EVID workflow adds syntax validation for the new module and runs the synthetic `test_qa005_ord_*.py` suite. The added cases cover exact zero-width intervals, a wide-interval slope change, all 1024 endpoint assignments, malformed/missing/duplicate bounds, Boolean spoofing, nonchronological intervals, buffered stdout delay, and unconditional inconclusive disposition.

No real A/A pair, benchmark, stress, soak, extended fuzz, production Go code, public API, wire contract, Source-V1 fixture, tag, release, numeric SLA, or Performance Gate is changed or exercised.

## Remaining work

1. The continuous enclosure now includes a separate outward-rounded interval evaluator for the actual production `fit_one` binary64 operation sequence, plus explicit binary64 conversion and pivot-tolerance handling ([design note](NETA_GO_ORD_TIME_INTERVAL_ENCLOSURE_2026-11-21.md)). Dedicated CI and independent code review are still required; `continuous_interval_bound_proved` remains false.
2. Characterize actual Go test output buffering and observer scheduling/backpressure without assuming line arrival equals case completion.
3. Quantify observer overhead and temporal error on the accepted dedicated reference host; preserve the three distinct observer modes.
4. Review nonlinear/transient drift and model adequacy with complete host telemetry and exact A/A evidence.
5. Apply strict duplicate-safe JSON decoding to manifests, process records, snapshots and line sidecars; reject non-standard NaN/infinity constants and bind the parser helper SHA ([strict JSON note](NETA_GO_ORD_JSON_STRICTNESS_2026-11-22.md)).
6. Obtain separate authorization before any real QA-004/Core/Full 10-pair measurement.

**Accounting is unchanged:** 18 normalized top-level packages remain open (9 Qualification, 7 Owner Decisions, 2 Release). Q-COR-01 remains closed. No Qualification package is closed by this synthetic implementation.
