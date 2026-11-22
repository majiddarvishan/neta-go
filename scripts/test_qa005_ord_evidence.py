"""Fast, no-benchmark tests for the opt-in ORD-EVID collection wrapper."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).parent
SCRIPT = HERE / "qa005_ord_evidence.py"
ROOT = HERE.parent

class OrdEvidenceTests(unittest.TestCase):
    def invoke(self, root, pair=1, side="baseline", body="print('ord-fixture')"):
        out = pathlib.Path(root)
        envfile = out / "environment.json"
        if not envfile.exists():
            envfile.write_text(json.dumps({
                "source_sha": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
                ).strip(),
                "go_version": subprocess.check_output(
                    ["go", "version"], cwd=ROOT, text=True
                ).strip(),
                "scenario_mode": "core",
                "harness_sha256": "a" * 64,
                "workload_config": "synthetic-core-no-benchmark",
            }))
        command = [
            sys.executable, "-B", str(SCRIPT),
            "--environment", str(envfile),
            "--output", str(out / "evidence"),
            "--log", str(out / "benchmark.log"),
            "--pair", str(pair),
            "--side", side,
            "--mode", "core",
            "--interval-ms", "100",
            "--", sys.executable, "-c", body,
        ]
        return subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, timeout=15
        )

    def test_success_keeps_log_and_fails_closed_on_host_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.invoke(directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            root = pathlib.Path(directory)
            self.assertEqual((root / "benchmark.log").read_text(), "ord-fixture\n")
            record = json.loads((root / "evidence/01-baseline.json").read_text())
            self.assertEqual(record["schema"], "neta-qa005-ord-process-evidence-v1")
            self.assertEqual(record["harness_sha256"], "a" * 64)
            self.assertEqual(record["workload_config"], "synthetic-core-no-benchmark")
            self.assertEqual(
                record["strict_json_sha256"],
                hashlib.sha256((HERE / "qa005_ord_json.py").read_bytes()).hexdigest(),
            )
            self.assertEqual(len(record["environment_sha256"]), 64)
            self.assertEqual(len(record["collector_sha256"]), 64)
            self.assertEqual(record["pair"], 1)
            self.assertEqual(record["side"], "baseline")
            self.assertEqual(record["mode"], "core")
            self.assertEqual(record["exit_code"], 0)
            self.assertTrue(record["complete"])
            self.assertEqual(record["qualification"], "DRIFT-INCONCLUSIVE")
            self.assertLessEqual(
                record["start_before_spawn"]["monotonic_ns"],
                record["start_after_spawn"]["monotonic_ns"],
            )
            self.assertLessEqual(
                record["start_after_spawn"]["monotonic_ns"],
                record["exit_after_wait"]["monotonic_ns"],
            )
            self.assertGreaterEqual(record["sample_count"], 3)
            self.assertEqual(record["sampling_interval_ms"], 100)
            self.assertEqual(len(record["log_sha256"]), 64)
            self.assertEqual(len(record["trace_sha256"]), 64)
            trace = (root / "evidence/01-baseline.jsonl").read_text().splitlines()
            self.assertEqual(len(trace), record["sample_count"])
            self.assertEqual(json.loads(trace[0])["kind"], "before_spawn")
            self.assertTrue(all(
                json.loads(line)["sampling_interval_ms"] == 100 for line in trace
            ))

    def test_nonzero_exit_is_recorded_and_not_qualified(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.invoke(directory, body="import sys; sys.exit(7)")
            self.assertEqual(result.returncode, 7, result.stderr)
            record = json.loads(
                (pathlib.Path(directory) / "evidence/01-baseline.json").read_text()
            )
            self.assertFalse(record["complete"])
            self.assertEqual(record["exit_code"], 7)
            self.assertEqual(record["qualification"], "DRIFT-INCONCLUSIVE")

    def test_existing_evidence_refused_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            original = self.invoke(directory)
            self.assertEqual(original.returncode, 0, original.stderr)
            before = (pathlib.Path(directory) / "benchmark.log").read_bytes()
            duplicate = self.invoke(directory)
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertEqual(
                (pathlib.Path(directory) / "benchmark.log").read_bytes(), before
            )

    def test_snapshot_marks_partially_unreadable_sensor_map_missing(self):
        from pathlib import Path
        from unittest.mock import patch
        from qa005_ord_evidence import snapshot

        paths = {
            "scaling_governor": [
                Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
                Path("/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor"),
            ],
            "scaling_cur_freq": [
                Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"),
            ],
            "thermal_zone": [
                Path("/sys/class/thermal/thermal_zone0/temp"),
            ],
        }

        def fake_glob(_root, pattern):
            for key, values in paths.items():
                if key in pattern:
                    return values
            return []

        def fake_read_sensor(path):
            value = str(path)
            if value == "/proc/vmstat":
                return "pswpin 0\npswpout 0\npgmajfault 0\n"
            if value.endswith("cpu1/cpufreq/scaling_governor"):
                return None
            if value.endswith("scaling_governor"):
                return "performance"
            if value.endswith("scaling_cur_freq"):
                return "2000000"
            if value.endswith("/temp"):
                return "42000"
            return "synthetic"

        with patch("qa005_ord_evidence.Path.glob", autospec=True, side_effect=fake_glob):
            with patch("qa005_ord_evidence.read_sensor", side_effect=fake_read_sensor):
                sample = snapshot("during")
        self.assertIn("governors", sample["missing_sensors"])
        self.assertNotIn("frequencies_khz", sample["missing_sensors"])
        self.assertNotIn("thermal_millidegrees", sample["missing_sensors"])

    def test_duplicate_environment_json_key_fails_before_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "environment.json").write_text(
                '{"source_sha":"first","source_sha":"second",'
                '"go_version":"synthetic","scenario_mode":"core",'
                '"harness_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
                '"workload_config":"synthetic-core"}'
            )
            result = self.invoke(directory)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Duplicate JSON object key: source_sha", result.stderr)
            self.assertFalse((root / "benchmark.log").exists())

    def test_wrong_source_or_mode_fails_before_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "environment.json").write_text(json.dumps({
                "source_sha": "0" * 40,
                "go_version": subprocess.check_output(
                    ["go", "version"], text=True
                ).strip(),
                "scenario_mode": "core",
                "harness_sha256": "a" * 64,
                "workload_config": "synthetic-core",
            }))
            result = self.invoke(directory)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((root / "benchmark.log").exists())

    def test_out_of_range_pair_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.invoke(directory, pair=11)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((pathlib.Path(directory) / "benchmark.log").exists())

if __name__ == "__main__":
    unittest.main()
