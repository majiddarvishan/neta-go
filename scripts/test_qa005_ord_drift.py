"""Fast synthetic tests: fixed Option-A formula only, never physical qualification."""
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from qa005_ord_drift import analyze, fit_one, inverse3, MODE_COUNTS

ORDER = [1 if i % 2 == 0 else -1 for i in range(10)]
TIME = [-1 + 2 * i / 9 for i in range(10)]
SYNTHETIC_SENSORS = {
    "loadavg": "0.00 0.00 0.00 1/1 1",
    "cpu_psi": "some avg10=0.00 avg60=0.00 avg300=0.00 total=0",
    "memory_psi": "some avg10=0.00 avg60=0.00 avg300=0.00 total=0",
    "io_psi": "some avg10=0.00 avg60=0.00 avg300=0.00 total=0",
    "cpu_stat": "usage_usec 1",
    "cpu_max": "max 100000",
    "cpuset": "0-3",
    "memory_events": "low 0",
    "swap_cgroup": "0",
    "boot_id": "synthetic-boot-id",
    "vmstat": {"pswpin": "0", "pswpout": "0", "pgmajfault": "0"},
    "governors": {"/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor": "performance"},
    "frequencies_khz": {"/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq": "2000000"},
    "thermal_millidegrees": {"/sys/class/thermal/thermal_zone0/temp": "42000"},
}


class OrdDriftTests(unittest.TestCase):
    def test_zero_log_ratio_fits_original_mean_and_all_four_corners(self):
        for family in (5, 48, 144):
            model = fit_one([0.] * 10, ORDER, TIME, .075, family)
            self.assertEqual(model["fixed_bounds_result"], "WITHIN_FIXED_BOUNDS")
            self.assertEqual(model["joint_5m_family_size"], 5 * family)
            self.assertTrue(model["original_m_family_mean"]["inside_fixed_bound"])
            self.assertTrue(model["joint_5m_mean"]["inside_fixed_bound"])
            self.assertEqual(model["residual_df"], 7)
            self.assertEqual(len(model["joint_5m_corners"]), 4)
            self.assertEqual(
                {(v["first_side_order"], v["scaled_time"])
                 for v in model["joint_5m_corners"]},
                {(-1, -1.), (-1, 1.), (1, -1.), (1, 1.)},
            )

    def test_constant_ratio_outside_prospective_margin(self):
        model = fit_one([math.log(1.09)] * 10, ORDER, TIME, .05, 48)
        self.assertEqual(model["fixed_bounds_result"], "OUTSIDE_FIXED_BOUNDS")
        self.assertFalse(model["joint_5m_mean"]["inside_fixed_bound"])

    def test_balanced_mean_cannot_hide_order_bias(self):
        y = [0.07 if o == 1 else -0.07 for o in ORDER]
        model = fit_one(y, ORDER, TIME, .05, 5)
        self.assertAlmostEqual(model["original_m_family_mean"]["estimate_log"], 0.)
        self.assertEqual(model["fixed_bounds_result"], "OUTSIDE_FIXED_BOUNDS")
        self.assertTrue(any(not c["inside_fixed_bound"]
                            for c in model["joint_5m_corners"]))

    def test_balanced_mean_cannot_hide_time_drift(self):
        y = [t * .09 for t in TIME]
        model = fit_one(y, ORDER, TIME, .075, 5)
        self.assertAlmostEqual(model["original_m_family_mean"]["estimate_log"], 0.)
        self.assertTrue(model["original_m_family_mean"]["inside_fixed_bound"])
        self.assertEqual(model["fixed_bounds_result"], "OUTSIDE_FIXED_BOUNDS")

    def test_bonferroni_joint_mean_more_conservative_than_original(self):
        y = [.005 * t + (.004 if i % 2 else -.004)
             for i, t in enumerate(TIME)]
        for m in MODE_COUNTS.values():
            model = fit_one(y, ORDER, TIME, .05, m)
            original = model["original_m_family_mean"]
            joint = model["joint_5m_mean"]
            self.assertGreaterEqual(
                joint["ci_log"][1] - joint["ci_log"][0],
                original["ci_log"][1] - original["ci_log"][0],
            )
            self.assertAlmostEqual(
                model["alpha_two_sided_per_contrast"], .05 / (5 * m)
            )

    def test_zero_missing_nonfinite_and_rank_deficiency_fail_closed(self):
        for bad in ([0.] * 9, [float("nan")] * 10):
            with self.assertRaises(ValueError):
                fit_one(bad, ORDER, TIME, .05, 5)
        with self.assertRaises(ValueError):
            fit_one([0.] * 10, ORDER, [float(i) for i in ORDER], .05, 5)
        with self.assertRaises(ValueError):
            fit_one([0.] * 10, ORDER, TIME, .20, 6)
        with self.assertRaises(ValueError):
            inverse3([[1., 0, 0], [1., 0, 0], [0, 0, 1.]])

    def test_missing_or_substituted_evidence_never_claims_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for mode in MODE_COUNTS:
                report = analyze(root, mode)
                self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
                self.assertEqual(report["environment_validity"], "E-UNKNOWN")
                self.assertEqual(report["statistical_diagnostics"], "INCONCLUSIVE")
                self.assertEqual(report["scenarios"], {})
                self.assertTrue(report["reasons"])

    @staticmethod
    def make_complete_qa004(root, early_receipt=False):
        (root / "baseline").mkdir()
        (root / "candidate").mkdir()
        (root / "ord-evidence").mkdir()
        meta = {
            "source_sha": "a" * 40,
            "go_version": "go version go1.23.9 linux/amd64",
            "scenario_mode": "qa004",
            "harness_sha256": "b" * 64,
            "workload_config": "synthetic-1200x-qa004",
            "scenario_version": "qa004-or-qa005-selected-v2",
            "cpu_model": "synthetic",
            "machine_id": "synthetic-controlled-host",
            "goarch": "amd64", "goos": "linux", "gomaxprocs": "default",
        }
        for side in ("baseline", "candidate"):
            (root / side / "environment.json").write_text(json.dumps(meta))
        for pair in range(1, 11):
            ordered = (("baseline", "candidate") if pair % 2 else
                       ("candidate", "baseline"))
            for seq, side in enumerate(ordered):
                log_path = root / side / f"{pair:02}.log"
                lines = [
                    "BenchmarkPendingDeadlineDetection/synthetic-pending="
                    f"{n}-4 1200 1000 ns/op 1200 detect-samples 100000 detect-p99-ns"
                    for n in (32, 128, 512, 2048, 8192)
                ]
                log_path.write_text("\n".join(lines) + "\n")
                ordinal = (pair - 1) * 2 + seq
                start = (ordinal + 1) * 1_000_000_000
                stamp = lambda t: {"monotonic_ns": t, "utc_ns": t + 1000000000}
                # Synthetic line events preserve raw bytes and provenance.
                offset = 0
                line_events = []
                for line_index, raw_line in enumerate(
                        log_path.read_bytes().splitlines(keepends=True), 1):
                    received_at = (start + 1_500 + line_index * 900
                                   if early_receipt and pair == 1 and side == "baseline"
                                   else start + 20_000 + line_index * 3_000)
                    line_events.append({
                        "line_index": line_index,
                        "byte_offset": offset,
                        "length_bytes": len(raw_line),
                        "line_sha256": hashlib.sha256(raw_line).hexdigest(),
                        "kind": "benchmark_result",
                        "benchmark_name": raw_line.split(None, 1)[0].decode(),
                        "benchmark_iterations": 1200,
                        "read_start_monotonic_ns": received_at - 100,
                        "read_end_monotonic_ns": received_at,
                        "read_end_utc_ns": received_at + 1_000_000_000,
                    })
                    offset += len(raw_line)
                line_events_path = root / "ord-evidence" / (
                    f"{pair:02}-{side}.lines.jsonl")
                line_events_path.write_text(
                    "".join(json.dumps(x) + "\n" for x in line_events))
                samples = [
                    {"kind": kind, "sampling_interval_ms": 250,
                     "sample_start": stamp(t), "sample_end": stamp(t + 1),
                     "missing_sensors": [], "sensors": dict(SYNTHETIC_SENSORS)}
                    for kind, t in (
                        ("before_spawn", start - 100_000),
                        ("after_spawn", start + 10_000),
                        ("during", start + 60_000),
                        ("after_exit", start + 100_000),
                    )
                ]
                base = f"{pair:02}-{side}"
                trace = root / "ord-evidence" / (base + ".jsonl")
                trace.write_text("".join(json.dumps(x) + "\n" for x in samples))
                checksum = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
                record = {
                    "mode": "qa004", "pair": pair, "side": side,
                    "source_sha": meta["source_sha"], "toolchain": meta["go_version"],
                    "harness_sha256": meta["harness_sha256"],
                    "workload_config": meta["workload_config"],
                    "environment_sha256": checksum(root / side / "environment.json"),
                    "collector_sha256": hashlib.sha256(
                        (HERE / "qa005_ord_evidence.py").read_bytes()
                    ).hexdigest(),
                    "strict_json_sha256": hashlib.sha256(
                        (HERE / "qa005_ord_json.py").read_bytes()
                    ).hexdigest(),
                    "observer_script_sha256": hashlib.sha256(
                        (HERE / "qa005_ord_stream_capture.py").read_bytes()
                    ).hexdigest(),
                    "line_events_sha256": checksum(line_events_path),
                    "host_kernel": "synthetic linux 6.x",
                    "log_sha256": checksum(log_path),
                    "trace_sha256": checksum(trace),
                    "complete": True, "exit_code": 0,
                    "start_before_spawn": stamp(start),
                    "start_after_spawn": stamp(start + 10_000),
                    "exit_after_wait": stamp(start + 100_000),
                    "sample_count": 4, "missing_sensors": [],
                    "sampling_interval_ms": 250,
                    "observed_max_sample_gap_ns": 110_000,
                }
                (root / "ord-evidence" / (base + ".json")).write_text(
                    json.dumps(record))
        (root / "comparison.json").write_text(json.dumps(
            {"matrix_complete": True, "relative_status": "PASS"}
        ))

    def test_complete_synthetic_qa004_model_never_admits_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            report = analyze(root, "qa004")
            self.assertEqual(report["case_metric_count"], 5, report["reasons"])
            self.assertEqual(report["statistical_diagnostics"],
                             "WITHIN_FIXED_BOUNDS_UNQUALIFIED")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertEqual(report["host_mode_admission"], "NOT_PERFORMED")
            self.assertEqual(report["existing_regression_status"], "PASS")
            sampling = report["sampling_accuracy"]
            self.assertEqual(sampling["measurement_status"], "OBSERVED_UNQUALIFIED")
            self.assertEqual(sampling["recorded_interval_ms"], 250)
            self.assertEqual(sampling["acceptance_limit"], "NOT_ESTABLISHED")
            self.assertFalse(sampling["sampling_accuracy_proved"])
            self.assertEqual(len(sampling["run_summaries"]), 20)
            self.assertEqual(sampling["maximum_snapshot_gap_ns"], 110_000)
            self.assertEqual(sampling["maximum_observed_scheduled_gap_ns"], 50_000)
            first_sampling_run = sampling["run_summaries"][0]
            self.assertEqual(first_sampling_run["median_scheduled_gap_ns"], 50_000)
            self.assertEqual(first_sampling_run["p95_scheduled_gap_ns"], 50_000)
            self.assertEqual(first_sampling_run["max_scheduled_gap_ns"], 50_000)
            self.assertAlmostEqual(
                first_sampling_run["max_gap_to_recorded_interval_ratio"], 0.0002
            )
            self.assertEqual(len(report["paired_runs"]), 20)
            self.assertEqual(len(report["pair_time_uncertainty"]), 10)
            self.assertEqual(len(report["scenarios"]), 5)
            summary = report["case_time_sensitivity_summary"]
            self.assertEqual(summary["case_metric_count"], 5)
            self.assertFalse(summary["continuous_interval_bound_proved"])
            self.assertEqual(summary["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertEqual(summary["continuous_interval_enclosures_complete"], 5)
            self.assertEqual(summary["continuous_interval_enclosures_inconclusive"], 0)
            self.assertFalse(summary["continuous_interval_bound_proved"])
            for metrics in report["scenarios"].values():
                sensitivity = metrics["deadline_detection_p99_ns"]["case_time_sensitivity"]
                self.assertEqual(sensitivity["endpoint_combinations"], 1024)
                self.assertFalse(sensitivity["case_time_precision_proved"])
                self.assertFalse(sensitivity["continuous_interval_bound_proved"])
                enclosure = metrics["deadline_detection_p99_ns"]["case_time_continuous_enclosure"]
                self.assertTrue(enclosure["continuous_interval_enclosure_complete"])
                self.assertFalse(enclosure["continuous_interval_bound_proved"])
                self.assertEqual(enclosure["qualification"], "DRIFT-INCONCLUSIVE")

    def test_sampling_interval_mismatch_across_runs_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            record_path = root / "ord-evidence" / "01-candidate.json"
            trace_path = root / "ord-evidence" / "01-candidate.jsonl"
            record = json.loads(record_path.read_text())
            samples = [json.loads(line) for line in trace_path.read_text().splitlines()]
            for sample in samples:
                sample["sampling_interval_ms"] = 500
            trace_path.write_text("".join(json.dumps(sample) + "\n" for sample in samples))
            record["sampling_interval_ms"] = 500
            record["trace_sha256"] = hashlib.sha256(trace_path.read_bytes()).hexdigest()
            record_path.write_text(json.dumps(record))
            report = analyze(root, "qa004")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertTrue(any(
                "Sampling interval changed across A/A runs" in reason
                for reason in report["reasons"]
            ))

    def test_report_keeps_observer_overhead_unmeasured_and_backpressure_possible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            report = analyze(root, "qa004")
            observer = report["observer_overhead"]
            self.assertEqual(observer["measurement_status"], "NOT_MEASURED")
            self.assertFalse(observer["overhead_proved"])
            self.assertTrue(observer["backpressure_possible"])
            self.assertTrue(observer["raw_log_write_in_reader"])
            self.assertTrue(observer["sidecar_write_in_reader"])
            self.assertEqual(observer["read_chunk_bytes"], 65536)
            self.assertEqual(observer["max_line_bytes"], 1024 * 1024)
            self.assertEqual(
                observer["timestamp_semantics"]["case_execution_start_end"],
                "not_observed",
            )
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")

    def test_duplicate_json_keys_in_environment_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            path = root / "baseline" / "environment.json"
            content = path.read_text()
            content = content.replace(
                '"source_sha":',
                '"source_sha": "a000000000000000000000000000000000000000", "source_sha":',
                1,
            )
            path.write_text(content)
            report = analyze(root, "qa004")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertEqual(report["statistical_diagnostics"], "INCONCLUSIVE")
            self.assertTrue(any(
                "Duplicate JSON object key: source_sha" in reason
                for reason in report["reasons"]
            ))

    def test_duplicate_json_keys_in_process_record_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            path = root / "ord-evidence" / "01-baseline.json"
            content = path.read_text()
            content = content.replace(
                '"pair": 1,',
                '"pair": 1, "pair": 1,',
                1,
            )
            path.write_text(content)
            report = analyze(root, "qa004")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertTrue(any(
                "Duplicate JSON object key: pair" in reason
                for reason in report["reasons"]
            ))

    def test_boolean_pair_identity_and_exit_code_fail_closed(self):
        for field, value in (("pair", True), ("exit_code", False)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_complete_qa004(root)
                record_path = root / "ord-evidence" / "01-baseline.json"
                record = json.loads(record_path.read_text())
                record[field] = value
                record_path.write_text(json.dumps(record))
                report = analyze(root, "qa004")
                self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
                self.assertTrue(any(
                    "Corrupt/mismatched run provenance" in reason
                    for reason in report["reasons"]
                ))

    def test_boolean_trace_clock_fails_closed_after_hash_rebinding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            trace_path = root / "ord-evidence" / "01-baseline.jsonl"
            samples = [json.loads(line) for line in trace_path.read_text().splitlines()]
            samples[0]["sample_start"]["monotonic_ns"] = True
            trace_path.write_text("".join(json.dumps(x) + "\n" for x in samples))
            record_path = root / "ord-evidence" / "01-baseline.json"
            record = json.loads(record_path.read_text())
            record["trace_sha256"] = hashlib.sha256(trace_path.read_bytes()).hexdigest()
            record_path.write_text(json.dumps(record))
            report = analyze(root, "qa004")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertTrue(any("clock integer" in reason for reason in report["reasons"]))

    def test_line_receipt_utc_outside_process_window_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            record_path = root / "ord-evidence" / "01-baseline.json"
            record = json.loads(record_path.read_text())
            line_path = root / "ord-evidence" / "01-baseline.lines.jsonl"
            events = [json.loads(line) for line in line_path.read_text().splitlines()]
            events[-1]["read_end_utc_ns"] = record["exit_after_wait"]["utc_ns"] + 1
            line_path.write_text("".join(json.dumps(x) + "\n" for x in events))
            record["line_events_sha256"] = hashlib.sha256(line_path.read_bytes()).hexdigest()
            record_path.write_text(json.dumps(record))
            report = analyze(root, "qa004")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertTrue(any(
                "Line receipt clock outside process monotonic/UTC interval" in reason
                for reason in report["reasons"]
            ))

    def test_early_line_receipt_before_post_spawn_clock_is_allowed(self):
        # Python observer child may emit before the parent's post-Popen clock.
        # The authoritative lower bound is the parent's pre-spawn bracket.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root, early_receipt=True)
            report = analyze(root, "qa004")
            self.assertEqual(report["case_metric_count"], 5, report["reasons"])
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")
            first = report["paired_runs"][0]
            self.assertEqual(first["side"], "baseline")
            observed = first["case_line_observation"]["case_observation_intervals"]
            self.assertTrue(any(
                row["arrival_monotonic_ns"] < first["launch_monotonic_ns"]
                for row in observed.values()
            ))

    def test_changed_host_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            path = root / "candidate" / "environment.json"
            meta = json.loads(path.read_text())
            meta["machine_id"] = "unexpected-host"
            path.write_text(json.dumps(meta))
            report = analyze(root, "qa004")
            self.assertEqual(report["statistical_diagnostics"], "INCONCLUSIVE")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")

    def test_tampered_line_sidecar_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            sidecar = root / "ord-evidence" / "01-baseline.lines.jsonl"
            sidecar.write_text(sidecar.read_text() + "tampering\n")
            report = analyze(root, "qa004")
            self.assertEqual(report["statistical_diagnostics"], "INCONCLUSIVE")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")

    def test_missing_line_sidecar_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            (root / "ord-evidence" / "01-baseline.lines.jsonl").unlink()
            report = analyze(root, "qa004")
            self.assertEqual(report["statistical_diagnostics"], "INCONCLUSIVE")
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")

    def test_tampered_raw_benchmark_log_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_qa004(root)
            with (root / "candidate" / "01.log").open("a") as log:
                log.write("tamper\n")
            report = analyze(root, "qa004")
            self.assertEqual(report["statistical_diagnostics"], "INCONCLUSIVE")
            self.assertEqual(report["scenarios"], {})
            self.assertEqual(report["qualification"], "DRIFT-INCONCLUSIVE")

    def test_process_midpoint_is_not_case_level_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = analyze(Path(tmp), "qa004")
            self.assertIn("PER_CASE_START_END_UNPROVEN", report["time_precision"])


if __name__ == "__main__":
    unittest.main()
