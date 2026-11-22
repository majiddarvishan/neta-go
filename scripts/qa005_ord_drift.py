#!/usr/bin/env python3
"""Fail-closed, report-only QENV-AA-02.ORD Option A diagnostics.

Analyzes existing unchanged benchmark logs and optional ORD-EVID process traces.
Never qualifies a host, baseline, Mode or Performance Gate. A process midpoint
is only a temporal proxy, NOT a per-benchmark-case timestamp. Synthetic tests
can validate the prespecified 5m statistics without accepting real evidence.
"""
import argparse
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
import statistics

from qa005_compare import (
    DEADLINE_METRICS, EXPECTED_QA005_SCENARIOS, PAIRS,
    P99_MIN_OBSERVATIONS, REQUIRED_METRICS, complete_matrix,
    parse_benchmark, student_t_critical,
)
from qa005_ord_time_uncertainty import (
    endpoint_sensitivity, pair_case_time_intervals,
)
from qa005_ord_telemetry_verify import verify_process_trace
from qa005_ord_time_interval_bound import continuous_interval_enclosure
from qa005_ord_stream_verify import verify_stream
from qa005_ord_json import loads as strict_json_loads
from qa005_ord_stream_capture import CHUNK_BYTES, MAX_LINE_BYTES

METRICS = ("throughput_ops_s", "p50_ns", "p95_ns", "p99_ns",
           "cpu_ns_op", "allocs_op")
MODE_COUNTS = {"qa004": 5, "core": 48, "full": 144}
BOUNDS = {"throughput_ops_s": .05, "p50_ns": .05, "p95_ns": .05,
          "p99_ns": .075, "cpu_ns_op": .075, "allocs_op": .075,
          "deadline_detection_p99_ns": .075}


@lru_cache(maxsize=16)
def cached_student_t_critical(alpha, degrees):
    """Avoid reintegrating identical critical values during interval sweeps."""
    return student_t_critical(alpha, degrees)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inverse3(m):
    """Gauss-Jordan inverse and infinity-norm condition estimate (3x3)."""
    if len(m) != 3 or any(len(row) != 3 for row in m):
        raise ValueError("Expected 3x3 design matrix")
    aug = [list(map(float, row)) + [float(i == j) for j in range(3)]
           for i, row in enumerate(m)]
    scale = max(abs(x) for row in m for x in row)
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("Non-finite or singular design")
    for col in range(3):
        pivot = max(range(col, 3), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) <= (1e-12 * scale):
            raise ValueError("Rank deficient or numerically singular order/time model")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        diag = aug[col][col]
        aug[col] = [value / diag for value in aug[col]]
        for i in range(3):
            if i == col:
                continue
            factor = aug[i][col]
            aug[i] = [a - factor * b for a, b in zip(aug[i], aug[col])]
    inverse = [row[3:] for row in aug]
    def norm(a):
        return max(sum(abs(x) for x in row) for row in a)
    return inverse, norm(m) * norm(inverse)


def inner(a, b):
    return sum(x * y for x, y in zip(a, b))


def fit_one(y, order, time_scaled, d, family_size):
    """Original m-equivalence + owner-approved joint 5m Bonferroni mean/corners.

    Return statistical *diagnostics* only; the caller must not promote a
    numeric result into DRIFT-VALID without environmental/time-proxy proofs.
    """
    n = PAIRS
    if (len(y) != n or len(order) != n or len(time_scaled) != n or
            any(not math.isfinite(v) for v in y + time_scaled) or
            any(o not in (-1, +1) for o in order)):
        raise ValueError("Invalid or incomplete ten-pair model input")
    if d not in (.05, .075) or family_size not in (5, 48, 144):
        raise ValueError("Unexpected margin or family")
    if min(time_scaled) < -1 - 1e-9 or max(time_scaled) > 1 + 1e-9:
        raise ValueError("Unnormalized chronological time")
    x = [[1.0, float(o), t] for o, t in zip(order, time_scaled)]
    xtx = [[sum(row[j] * row[k] for row in x) for k in range(3)]
           for j in range(3)]
    inv, condition = inverse3(xtx)
    xty = [sum(row[j] * obs for row, obs in zip(x, y)) for j in range(3)]
    beta = [inner(row, xty) for row in inv]
    residuals = [obs - inner(row, beta) for obs, row in zip(y, x)]
    mse = inner(residuals, residuals) / (n - 3)
    if mse < 0 or not math.isfinite(mse):
        raise ValueError("Invalid residual variance")
    covariance = [[mse * v for v in row] for row in inv]
    log_limit = math.log1p(d)
    original_mean = statistics.fmean(y)
    original_sem = statistics.stdev(y) / math.sqrt(n)

    def interval(estimate, standard_error, critical):
        if not all(math.isfinite(v) for v in
                   (estimate, standard_error, critical)):
            raise ValueError("Nonfinite statistical contrast")
        low, high = estimate - critical * standard_error, estimate + critical * standard_error
        return {
            "estimate_log": estimate,
            "se_log": standard_error,
            "ci_log": [low, high],
            "inside_fixed_bound": (low > -log_limit and high < log_limit),
        }

    original_critical = cached_student_t_critical(.05 / family_size, n - 1)
    joint_mean_critical = cached_student_t_critical(.05 / (5 * family_size), n - 1)
    joint_corner_critical = cached_student_t_critical(.05 / (5 * family_size), n - 3)
    original = interval(original_mean, original_sem, original_critical)
    joint_mean = interval(original_mean, original_sem, joint_mean_critical)
    corners = []
    for o in (-1, +1):
        for t in (-1., +1.):
            row = [1.0, float(o), t]
            variance = sum(row[i] * covariance[i][j] * row[j]
                           for i in range(3) for j in range(3))
            if variance < -1e-12:
                raise ValueError("Negative contrast variance")
            corner = interval(inner(row, beta), math.sqrt(max(0, variance)),
                              joint_corner_critical)
            corner.update({"first_side_order": o, "scaled_time": t})
            corners.append(corner)
    all_cis = [original, joint_mean, *corners]
    result = {
        "original_m_family_mean": original,
        "joint_5m_mean": joint_mean,
        "joint_5m_corners": corners,
        "joint_5m_family_size": 5 * family_size,
        "alpha_two_sided_per_contrast": .05 / (5 * family_size),
        "margin_ratio": d,
        "margin_log": log_limit,
        "raw_paired_log_ratios": list(y),
        "original_unadjusted_first_half_mean": statistics.fmean(y[:5]),
        "original_unadjusted_last_half_mean": statistics.fmean(y[5:]),
        "first_side_baseline_mean": statistics.fmean(
            v for v, o in zip(y, order) if o == 1
        ),
        "first_side_candidate_mean": statistics.fmean(
            v for v, o in zip(y, order) if o == -1
        ),
        "model_coefficients_mean_order_time": beta,
        "xtx": xtx,
        "xtx_condition_inf": condition,
        "residual_df": n - 3,
        "residual_mse": mse,
        "residuals": residuals,
        "residual_max_abs": max(abs(e) for e in residuals),
        "time_scaled": list(time_scaled),
        "first_side_order": list(order),
        "fixed_bounds_result": ("WITHIN_FIXED_BOUNDS"
                                if all(q["inside_fixed_bound"] for q in all_cis)
                                else "OUTSIDE_FIXED_BOUNDS"),
    }
    return result


def validated_inputs(root, mode):
    """Bind all 20 side traces to untouched logs, environment and chronology."""
    if mode not in MODE_COUNTS:
        raise ValueError("Unsupported Mode")
    evidence = root / "ord-evidence"
    env = {}
    collector_digest = digest(Path(__file__).with_name("qa005_ord_evidence.py"))
    observed_boot_id = None
    observed_kernel = None
    for side in ("baseline", "candidate"):
        path = root / side / "environment.json"
        meta = strict_json_loads(path.read_text(encoding="utf-8"))
        if meta.get("scenario_mode") != mode:
            raise ValueError("Environment Mode mismatch")
        for name in ("source_sha", "go_version", "harness_sha256",
                     "workload_config", "scenario_version", "cpu_model",
                     "machine_id", "goarch", "goos", "gomaxprocs"):
            if not isinstance(meta.get(name), str) or not meta[name]:
                raise ValueError("Missing environment field: " + name)
        env[side] = (meta, digest(path))
    keys = ("source_sha", "go_version", "harness_sha256",
            "workload_config", "scenario_version", "machine_id", "cpu_model",
            "goarch", "goos", "gomaxprocs")
    if any(env["baseline"][0][k] != env["candidate"][0][k] for k in keys):
        raise ValueError("A/A source, fixture or toolchain parity mismatch")
    reads = {"baseline": [], "candidate": []}
    runs = []
    observed_sampling_interval_ms = None
    for pair in range(1, PAIRS + 1):
        for order_index, side in enumerate(
                ("baseline", "candidate") if pair % 2 else ("candidate", "baseline")):
            stem = "%02d-%s" % (pair, side)
            record_file = evidence / (stem + ".json")
            trace_file = evidence / (stem + ".jsonl")
            line_events_file = evidence / (stem + ".lines.jsonl")
            log_file = root / side / ("%02d.log" % pair)
            record = strict_json_loads(record_file.read_text(encoding="utf-8"))
            if (record.get("mode") != mode or type(record.get("pair")) is not int or
                    record.get("pair") != pair or
                    record.get("side") != side or record.get("source_sha") != env[side][0]["source_sha"] or
                    record.get("toolchain") != env[side][0]["go_version"] or
                    record.get("harness_sha256") != env[side][0]["harness_sha256"] or
                    record.get("workload_config") != env[side][0]["workload_config"] or
                    record.get("environment_sha256") != env[side][1] or
                    record.get("collector_sha256") != collector_digest or
                    record.get("strict_json_sha256") != digest(
                        Path(__file__).with_name("qa005_ord_json.py")) or
                    record.get("observer_script_sha256") != digest(
                        Path(__file__).with_name("qa005_ord_stream_capture.py")) or
                    record.get("line_events_sha256") != digest(line_events_file) or
                    record.get("log_sha256") != digest(log_file) or
                    record.get("trace_sha256") != digest(trace_file) or
                    record.get("complete") is not True or
                    type(record.get("exit_code")) is not int or record.get("exit_code") != 0):
                raise ValueError("Corrupt/mismatched run provenance: " + stem)
            samples = [strict_json_loads(line) for line in
                       trace_file.read_text(encoding="utf-8").splitlines()]
            trace_info = verify_process_trace(record, samples)
            sampling_interval_ms = trace_info["sampling_interval_ms"]
            if observed_sampling_interval_ms is None:
                observed_sampling_interval_ms = sampling_interval_ms
            elif sampling_interval_ms != observed_sampling_interval_ms:
                raise ValueError("Sampling interval changed across A/A runs")
            kernel = record.get("host_kernel")
            if not isinstance(kernel, str) or not kernel:
                raise ValueError("Host kernel identity missing: " + stem)
            if observed_kernel is None:
                observed_kernel = kernel
            elif kernel != observed_kernel:
                raise ValueError("Host kernel changed across A/A runs")
            boot_id = trace_info["boot_id"]
            if observed_boot_id is None:
                observed_boot_id = boot_id
            elif observed_boot_id != boot_id:
                raise ValueError("Host reboot/boot-id mismatch across runs")
            start = trace_info["start_monotonic_ns"]
            launch = trace_info["launch_monotonic_ns"]
            end = trace_info["end_monotonic_ns"]
            parsed = parse_benchmark(log_file)
            observed = verify_stream(
                log_file, line_events_file, start, end, set(parsed),
                pre_spawn_utc_ns=trace_info["start_utc_ns"],
                process_exit_utc_ns=trace_info["end_utc_ns"],
            )
            reads[side].append(parsed)
            runs.append({
                "case_line_observation": observed,
                "pair": pair, "side": side,
                "first_side_order": 1 if pair % 2 else -1,
                "sequence_in_pair": order_index,
                "start_monotonic_ns": start,
                "launch_monotonic_ns": launch,
                "end_monotonic_ns": end,
                "duration_ns": end - start,
                "max_sample_gap_ns": trace_info["observed_max_sample_gap_ns"],
                "sampling_interval_ms": sampling_interval_ms,
                "all_snapshot_gap_count": trace_info["all_snapshot_gap_count"],
                "scheduled_gap_count": trace_info["scheduled_gap_count"],
                "median_scheduled_gap_ns": trace_info["median_scheduled_gap_ns"],
                "p95_scheduled_gap_ns": trace_info["p95_scheduled_gap_ns"],
                "max_scheduled_gap_ns": trace_info["max_scheduled_gap_ns"],
                "max_gap_to_interval_ratio": trace_info["max_scheduled_gap_to_interval_ratio"],
                "missing_sensors": trace_info["missing_sensors"],
                "record_sha256": digest(record_file),
            })
    if not complete_matrix(reads["baseline"] + reads["candidate"], mode):
        raise ValueError("Incomplete or substituted selected scenario matrix")
    for a, b in zip(runs, runs[1:]):
        if b["start_monotonic_ns"] < a["end_monotonic_ns"]:
            raise ValueError("Nonsequential process chronology; cannot infer order/time")
    pair_times = []
    pair_windows = []
    for i in range(PAIRS):
        first, second = runs[2 * i], runs[2 * i + 1]
        point = sum((r["start_monotonic_ns"] + r["end_monotonic_ns"]) / 2
                    for r in (first, second)) / 2
        pair_times.append(point)
        pair_windows.append({
            "earliest_process_proxy_ns":
                (first["start_monotonic_ns"] + second["start_monotonic_ns"]) / 2,
            "latest_process_proxy_ns":
                (first["end_monotonic_ns"] + second["end_monotonic_ns"]) / 2,
        })
    start, end = min(pair_times), max(pair_times)
    if not end > start:
        raise ValueError("Invalid or missing actual elapsed pair chronology")
    normalized = [2 * (x - start) / (end - start) - 1 for x in pair_times]
    order = [1 if i % 2 == 0 else -1 for i in range(PAIRS)]
    return reads, runs, pair_windows, order, normalized, env


def analyze(root, mode):
    report = {
        "schema": "neta-qa005-ord-diagnostics-v1",
        "analyzer_sha256": digest(Path(__file__)),
        "regression_comparator_sha256": digest(Path(__file__).with_name("qa005_compare.py")),
        "mode": mode,
        "qualification": "DRIFT-INCONCLUSIVE",
        "environment_validity": "E-UNKNOWN",
        "host_mode_admission": "NOT_PERFORMED",
        "time_precision": "CASE_LINE_ARRIVALS_OBSERVED; PER_CASE_START_END_UNPROVEN; CONTINUOUS_INTERVAL_ENCLOSURE_CANDIDATE_NOT_INDEPENDENTLY_PROVED; OBSERVER_OVERHEAD_UNMEASURED_BACKPRESSURE_POSSIBLE",
        "performance_gate": "DISABLED",
        "statistical_diagnostics": "INCONCLUSIVE",
        "sampling_accuracy": {
            "measurement_status": "NOT_VALIDATED",
            "recorded_interval_ms": None,
            "acceptance_limit": "NOT_ESTABLISHED",
            "sampling_accuracy_proved": False,
            "run_summaries": [],
        },
        "observer_overhead": {
            "measurement_status": "NOT_MEASURED",
            "overhead_proved": False,
            "capture_mode": "INLINE_STDOUT_PIPE_FORWARDER",
            "backpressure_possible": True,
            "raw_log_write_in_reader": True,
            "sidecar_write_in_reader": True,
            "read_chunk_bytes": CHUNK_BYTES,
            "max_line_bytes": MAX_LINE_BYTES,
            "timestamp_semantics": {
                "read_start_monotonic_ns": "immediately_before_os_read",
                "read_end_monotonic_ns": "immediately_after_os_read",
                "read_end_utc_ns": "time.time_ns_after_os_read",
                "multiple_lines_in_one_read": "share_the_same_read_bracket",
                "line_spanning_reads": "uses_the_bracket_of_the_chunk_that_completes_the_line",
                "case_execution_start_end": "not_observed",
            },
        },
        "reasons": ["Line receipts bound possible case times but do not prove case execution "
                    "start/end; the continuous interval enclosure is a report-only candidate "
                    "pending independent equivalence review.",
                    "The observer is an inline pipe forwarder: raw-log and sidecar writes can "
                    "block its reader and backpressure child stdout. Observer overhead is "
                    "NOT_MEASURED.",
                    "Sampling cadence is reported only when telemetry provenance validates; "
                    "no acceptance threshold or sampling-accuracy proof is established.",
                    "Mode admission also requires complete host telemetry/E-VALID and "
                    "independent nonlinear/model-fit review."],
        "scenarios": {},
    }
    try:
        reads, runs, pair_windows, order, time_scaled, env = validated_inputs(root, mode)
        metric_keys = (("deadline_detection_p99_ns",) if mode == "qa004"
                       else METRICS)
        cases = sorted(reads["baseline"][0])
        m = len(cases) * len(metric_keys)
        if m != MODE_COUNTS[mode]:
            raise ValueError("Unexpected 5/48/144 family size")
        scheduled_runs = [run for run in runs if run["scheduled_gap_count"] > 0]
        report["sampling_accuracy"] = {
            "measurement_status": (
                "OBSERVED_UNQUALIFIED" if scheduled_runs else "NO_SCHEDULED_GAPS"
            ),
            "recorded_interval_ms": runs[0]["sampling_interval_ms"],
            "acceptance_limit": "NOT_ESTABLISHED",
            "sampling_accuracy_proved": False,
            "maximum_snapshot_gap_ns": max(run["max_sample_gap_ns"] for run in runs),
            "maximum_observed_scheduled_gap_ns": (
                max(run["max_scheduled_gap_ns"] for run in scheduled_runs)
                if scheduled_runs else None
            ),
            "maximum_gap_to_recorded_interval_ratio": (
                max(run["max_gap_to_interval_ratio"] for run in scheduled_runs)
                if scheduled_runs else None
            ),
            "run_summaries": [
                {
                    "pair": run["pair"],
                    "side": run["side"],
                    "all_snapshot_gap_count": run["all_snapshot_gap_count"],
                    "scheduled_gap_count": run["scheduled_gap_count"],
                    "median_scheduled_gap_ns": run["median_scheduled_gap_ns"],
                    "p95_scheduled_gap_ns": run["p95_scheduled_gap_ns"],
                    "max_scheduled_gap_ns": run["max_scheduled_gap_ns"],
                    "max_gap_to_recorded_interval_ratio": run["max_gap_to_interval_ratio"],
                }
                for run in runs
            ],
        }
        report["source_sha"] = env["baseline"][0]["source_sha"]
        report["fixture_sha256"] = env["baseline"][0]["harness_sha256"]
        report["paired_runs"] = runs
        report["pair_time_uncertainty"] = pair_windows
        report["first_side_order"] = order
        report["time_scaled_process_proxy"] = time_scaled
        statuses = []
        time_sensitivity_statuses = []
        for case in cases:
            report["scenarios"][case] = {}
            case_intervals = pair_case_time_intervals(runs, case)
            for metric in metric_keys:
                baseline = [row[case][metric] for row in reads["baseline"]]
                candidate = [row[case][metric] for row in reads["candidate"]]
                counts = [row[case]["observations"] for side in reads.values()
                          for row in side]
                if (metric in ("p99_ns", "deadline_detection_p99_ns") and
                        min(counts) < P99_MIN_OBSERVATIONS):
                    raise ValueError("Insufficient P99 observations for " + case)
                if any(v is None or not isinstance(v, (float, int)) or
                       not math.isfinite(v) or v <= 0 for v in
                       baseline + candidate):
                    raise ValueError("Missing, zero or nonfinite metric: " + case + "/" + metric)
                y = [math.log(c / b) for b, c in zip(baseline, candidate)]
                model = fit_one(y, order, time_scaled, BOUNDS[metric], m)
                model["case_time_sensitivity"] = endpoint_sensitivity(
                    y, order, case_intervals, BOUNDS[metric], m, fit_one
                )
                joint_corner_critical = cached_student_t_critical(
                    .05 / (5 * m), len(y) - 3
                )
                model["case_time_continuous_enclosure"] = continuous_interval_enclosure(
                    y, order, case_intervals, BOUNDS[metric], joint_corner_critical
                )
                report["scenarios"][case][metric] = model
                statuses.append(model["fixed_bounds_result"])
                time_sensitivity_statuses.append(
                    model["case_time_sensitivity"]["sensitivity_status"]
                )
        continuous_enclosures = [
            model["case_time_continuous_enclosure"]
            for case_metrics in report["scenarios"].values()
            for model in case_metrics.values()
        ]
        invalid_enclosure = any(
            not item["continuous_interval_enclosure_complete"]
            for item in continuous_enclosures
        )
        outside_enclosure = any(
            item["continuous_interval_enclosure_complete"] and
            not item["all_corner_ci_envelopes_inside_fixed_bounds"]
            for item in continuous_enclosures
        )
        invalid_sensitivity = any(
            s == "INCONCLUSIVE_INVALID_ENDPOINT_FIT"
            for s in time_sensitivity_statuses
        )
        outside_sensitivity = any(
            s == "ENDPOINT_SWEEP_EXPOSES_OUT_OF_BOUND_ASSIGNMENT"
            for s in time_sensitivity_statuses
        )
        process_outside = any(s != "WITHIN_FIXED_BOUNDS" for s in statuses)
        if outside_sensitivity or process_outside:
            report["statistical_diagnostics"] = "OUTSIDE_FIXED_BOUNDS_UNQUALIFIED"
        elif invalid_sensitivity or invalid_enclosure or outside_enclosure:
            report["statistical_diagnostics"] = "INCONCLUSIVE"
        else:
            report["statistical_diagnostics"] = "WITHIN_FIXED_BOUNDS_UNQUALIFIED"
        report["case_metric_count"] = len(statuses)
        if invalid_enclosure:
            report["reasons"].append(
                "At least one continuous time enclosure could not complete a positive-denominator bound."
            )
        elif outside_enclosure:
            report["reasons"].append(
                "At least one conservative continuous time enclosure crosses a fixed bound; "
                "a feasible out-of-bound assignment is not established."
            )
        report["case_time_sensitivity_summary"] = {
            "case_metric_count": len(time_sensitivity_statuses),
            "endpoint_sweep_outside_fixed_bounds": sum(
                s == "ENDPOINT_SWEEP_EXPOSES_OUT_OF_BOUND_ASSIGNMENT"
                for s in time_sensitivity_statuses
            ),
            "invalid_endpoint_sweep": sum(
                s == "INCONCLUSIVE_INVALID_ENDPOINT_FIT"
                for s in time_sensitivity_statuses
            ),
            "within_fixed_bounds_unproven": sum(
                s == "ENDPOINT_SWEEP_WITHIN_FIXED_BOUNDS_UNPROVEN"
                for s in time_sensitivity_statuses
            ),
            "continuous_interval_enclosures_complete": sum(
                item["continuous_interval_enclosure_complete"]
                for item in continuous_enclosures
            ),
            "continuous_interval_enclosures_inconclusive": sum(
                not item["continuous_interval_enclosure_complete"]
                for item in continuous_enclosures
            ),
            "continuous_interval_enclosures_exposing_out_of_bound_possibility": sum(
                item["continuous_interval_enclosure_complete"] and
                not item["all_corner_ci_envelopes_inside_fixed_bounds"]
                for item in continuous_enclosures
            ),
            "continuous_interval_bound_proved": False,
            "qualification": "DRIFT-INCONCLUSIVE",
        }
        if any(x["missing_sensors"] for x in runs):
            report["reasons"].append(
                "One or more required host sensor values were unavailable; E-UNKNOWN."
            )
        comparison = strict_json_loads((root / "comparison.json").read_text(encoding="utf-8"))
        if comparison.get("matrix_complete") is not True:
            report["reasons"].append("Independent comparator matrix not complete")
        report["existing_regression_status"] = comparison.get("relative_status", "INCONCLUSIVE")
        # Existing comparator includes uninstrumented retained memory; never
        # claim its full PASS just from six non-retention metrics.
    except (OSError, ValueError, TypeError, KeyError, IndexError,
            ArithmeticError, json.JSONDecodeError) as exc:
        report["reasons"].append("Incomplete or malformed provenance/statistics: " + str(exc))
        report["statistical_diagnostics"] = "INCONCLUSIVE"
        report["scenarios"] = {}
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paired-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=tuple(MODE_COUNTS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze(args.paired_dir, args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error("Refusing to overwrite existing ORD report")
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2,
                                     allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("mode", "qualification", "statistical_diagnostics",
                       "case_metric_count") if k in report}, sort_keys=True))


if __name__ == "__main__":
    main()
