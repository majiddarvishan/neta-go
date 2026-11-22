"""Fail-closed tests of sidecar line identity and conservative receipt brackets."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from qa005_ord_stream_verify import verify_stream

HERE = Path(__file__).parent
SCRIPT = HERE / "qa005_ord_stream_capture.py"
NAME = "BenchmarkPendingDeadlineDetection/synthetic-pending=32"
ROW = (NAME + "-4 1200 1000 ns/op\n").encode()


class StreamVerificationTests(unittest.TestCase):
    @staticmethod
    def observe(root):
        logfile = root / "01.log"
        events = root / "01.lines.jsonl"
        command = [
            sys.executable, "-B", str(SCRIPT), "--events", str(events),
            "--", sys.executable, "-c",
            "import sys;sys.stdout.buffer.write(%r)" % (b"header\r\n" + ROW),
        ]
        with logfile.open("wb") as stream:
            result = subprocess.run(
                command, stdout=stream, stderr=subprocess.PIPE, timeout=10
            )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        records = [json.loads(line) for line in events.read_text().splitlines()]
        launch = min(x["read_start_monotonic_ns"] for x in records) - 10**9
        end = max(x["read_end_monotonic_ns"] for x in records) + 10**9
        return logfile, events, launch, end

    def test_conservative_interval_never_precision_pass(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            r = verify_stream(log, events, launch, end, {NAME})
            self.assertFalse(r["precision_proved"])
            self.assertEqual(r["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertEqual(r["observed_benchmark_cases"], 1)
            case = r["case_observation_intervals"][NAME]
            self.assertEqual(case["earliest_possible_case_ns"], launch)
            self.assertEqual(
                case["interval_width_ns"], case["arrival_monotonic_ns"] - launch
            )

    def test_duplicate_benchmark_case_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log, events = root / "01.log", root / "01.lines.jsonl"
            command = [
                sys.executable, "-B", str(SCRIPT), "--events", str(events),
                "--", sys.executable, "-c",
                "import sys;sys.stdout.buffer.write(%r)" % (ROW + ROW),
            ]
            with log.open("wb") as dest:
                outcome = subprocess.run(
                    command, stdout=dest, stderr=subprocess.PIPE, timeout=10
                )
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            launch = min(x["read_start_monotonic_ns"] for x in rows) - 10**9
            end = max(x["read_end_monotonic_ns"] for x in rows) + 10**9
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                verify_stream(log, events, launch, end, {NAME})

    def test_invalid_event_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            events.write_text("123\n")
            with self.assertRaisesRegex(ValueError, "count differs"):
                verify_stream(log, events, launch, end, {NAME})

    def test_duplicate_json_object_keys_in_sidecar_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            lines = events.read_text().splitlines()
            lines[0] = lines[0].replace(
                '"line_index":1,',
                '"line_index":1,"line_index":1,',
                1,
            )
            events.write_text("\\n".join(lines) + "\\n")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON object key: line_index"):
                verify_stream(log, events, launch, end, {NAME})

    def test_nonstandard_json_numeric_constant_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            lines = events.read_text().splitlines()
            lines[0] = lines[0][:-1] + ',"unused":NaN}'
            events.write_text("\\n".join(lines) + "\\n")
            with self.assertRaisesRegex(ValueError, "Non-standard JSON numeric constant: NaN"):
                verify_stream(log, events, launch, end, {NAME})

    def test_raw_log_tampering_detected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            with log.open("ab") as stream:
                stream.write(b"tampered\n")
            with self.assertRaisesRegex(ValueError, "count differs"):
                verify_stream(log, events, launch, end, {NAME})

    def test_wrong_case_and_missing_case_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            with self.assertRaisesRegex(ValueError, "Unexpected"):
                verify_stream(log, events, launch, end, {"BenchmarkWrong"})
            with self.assertRaises(ValueError):
                verify_stream(log, events, launch, end, set())

    def test_clock_regression_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            rows[1]["read_end_monotonic_ns"] = launch - 1
            events.write_text("".join(json.dumps(x) + "\n" for x in rows))
            with self.assertRaisesRegex(ValueError, "receipt clock"):
                verify_stream(log, events, launch, end, {NAME})

    def test_boolean_provenance_fields_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            rows[0]["line_index"] = True
            events.write_text("".join(json.dumps(x) + "\n" for x in rows))
            with self.assertRaisesRegex(ValueError, "identity"):
                verify_stream(log, events, launch, end, {NAME})

    def test_receipt_outside_process_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            rows[-1]["read_end_monotonic_ns"] = end + 1
            events.write_text("".join(json.dumps(x) + "\n" for x in rows))
            with self.assertRaisesRegex(ValueError, "receipt clock"):
                verify_stream(log, events, launch, end, {NAME})

    def test_utc_receipt_must_stay_inside_process_wall_clock_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            start_utc = min(x["read_end_utc_ns"] for x in rows) - 10**9
            end_utc = max(x["read_end_utc_ns"] for x in rows) + 10**9
            rows[-1]["read_end_utc_ns"] = end_utc + 1
            events.write_text("".join(json.dumps(x) + "\n" for x in rows))
            with self.assertRaisesRegex(ValueError, "receipt clock"):
                verify_stream(
                    log, events, launch, end, {NAME},
                    pre_spawn_utc_ns=start_utc,
                    process_exit_utc_ns=end_utc,
                )

    def test_zero_iteration_benchmark_result_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log, events = root / "01.log", root / "01.lines.jsonl"
            zero_row = (NAME + "-4 0 100 ns/op\n").encode()
            command = [
                sys.executable, "-B", str(SCRIPT), "--events", str(events),
                "--", sys.executable, "-c",
                "import sys;sys.stdout.buffer.write(%r)" % zero_row,
            ]
            with log.open("wb") as dest:
                outcome = subprocess.run(
                    command, stdout=dest, stderr=subprocess.PIPE, timeout=10
                )
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            launch = min(x["read_start_monotonic_ns"] for x in rows) - 10**9
            end = max(x["read_end_monotonic_ns"] for x in rows) + 10**9
            with self.assertRaisesRegex(ValueError, "iteration count"):
                verify_stream(log, events, launch, end, {NAME})

    def test_sidecar_line_hash_tampering_detected(self):
        with tempfile.TemporaryDirectory() as d:
            log, events, launch, end = self.observe(Path(d))
            rows = [json.loads(x) for x in events.read_text().splitlines()]
            rows[1]["line_sha256"] = "0" * 64
            events.write_text("".join(json.dumps(x) + "\n" for x in rows))
            with self.assertRaisesRegex(ValueError, "mismatch"):
                verify_stream(log, events, launch, end, {NAME})


if __name__ == "__main__":
    unittest.main()
