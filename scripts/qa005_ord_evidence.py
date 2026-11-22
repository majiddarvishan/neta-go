#!/usr/bin/env python3
"""Optional report-only Phase-Q ORD-EVID process timing/host-telemetry wrapper.

This is NOT a reference-host validator or an A/A numerical acceptance tool.
The wrapped go test arguments/stdout remain byte-for-byte unchanged. Timing is
a process launch/exit bracket, NOT exact per-benchmark-case timing.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from qa005_ord_json import loads as strict_json_loads

SENSORS = {
    "loadavg": "/proc/loadavg",
    "cpu_psi": "/proc/pressure/cpu",
    "memory_psi": "/proc/pressure/memory",
    "io_psi": "/proc/pressure/io",
    "cpu_stat": "/sys/fs/cgroup/cpu.stat",
    "cpu_max": "/sys/fs/cgroup/cpu.max",
    "cpuset": "/sys/fs/cgroup/cpuset.cpus.effective",
    "memory_events": "/sys/fs/cgroup/memory.events",
    "swap_cgroup": "/sys/fs/cgroup/memory.swap.current",
    "boot_id": "/proc/sys/kernel/random/boot_id",
}

def read_sensor(path):
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

def clock():
    return {
        "utc_ns": time.time_ns(),
        "monotonic_ns": time.monotonic_ns(),
    }

def snapshot(kind):
    before = clock()
    sensor_values = {key: read_sensor(path) for key, path in SENSORS.items()}
    vmstat = read_sensor("/proc/vmstat")
    wanted = {"pswpin", "pswpout", "pgmajfault"}
    vm = {}
    if vmstat is not None:
        for line in vmstat.splitlines():
            pieces = line.split()
            if len(pieces) == 2 and pieces[0] in wanted:
                vm[pieces[0]] = pieces[1]
    sensor_values["vmstat"] = vm if len(vm) == len(wanted) else None
    # Every CPU governor and frequency change is evidence, not an assumed constant.
    for label, pattern in (
        ("governors", "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"),
        ("frequencies_khz", "/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq"),
        ("thermal_millidegrees", "/sys/class/thermal/thermal_zone*/temp"),
    ):
        sensor_values[label] = {
            str(path): read_sensor(path)
            for path in sorted(Path("/").glob(pattern.lstrip("/")))
        }
        if not sensor_values[label]:
            sensor_values[label] = None
    after = clock()
    return {
        "kind": kind,
        "sample_start": before,
        "sample_end": after,
        "sensors": sensor_values,
        "missing_sensors": sorted(
            key for key, value in sensor_values.items()
            if value is None or (
                isinstance(value, dict) and
                any(reading is None for reading in value.values())
            )
        ),
    }

def run(args):
    if (args.line_events is None) != (args.observer_script is None):
        raise ValueError("Line evidence and observer source must be specified together")
    if args.observer_script is not None and not args.observer_script.is_file():
        raise ValueError("Missing immutable line observer source")
    environment_path = Path(args.environment)
    try:
        metadata = strict_json_loads(environment_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError("Missing or invalid environment evidence: " + str(exc)) from exc
    required = ("source_sha", "scenario_mode", "harness_sha256",
                "workload_config", "go_version")
    if not isinstance(metadata, dict) or any(
        not isinstance(metadata.get(key), str) or not metadata[key]
        for key in required
    ):
        raise ValueError("Incomplete source/fixture environment evidence")
    current_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    if metadata["source_sha"] != current_sha or metadata["scenario_mode"] != args.mode:
        raise ValueError("Source SHA or mode differs from bound environment")
    actual_go_version = subprocess.check_output(
        ["go", "version"], text=True
    ).strip()
    if metadata["go_version"] != actual_go_version:
        raise ValueError("Go toolchain differs from bound environment")
    destination = Path(args.output)
    destination.mkdir(parents=True, exist_ok=True)
    pair = args.pair
    side = args.side
    base = "%02d-%s" % (pair, side)
    trace = destination / (base + ".jsonl")
    record = destination / (base + ".json")
    output = Path(args.log)
    output.parent.mkdir(parents=True, exist_ok=True)
    if trace.exists() or record.exists() or output.exists():
        raise ValueError("Refusing to replace existing ORD-EVID/log evidence: " + base)
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("Missing benchmark command after --")
    if args.interval_ms < 100 or args.interval_ms > 5000:
        raise ValueError("Sampling interval must be 100..5000 milliseconds")
    interval = args.interval_ms / 1000.0

    completed = False
    process = None
    start = clock()
    launch = None
    end = None
    samples = []
    exit_code = None
    # Trace is stream-written so an interrupted run still leaves partial evidence.
    try:
        with trace.open("x", encoding="utf-8") as trace_stream, output.open("xb") as log:
            start_env = snapshot("before_spawn")
            start_env["sampling_interval_ms"] = args.interval_ms
            samples.append(start_env)
            trace_stream.write(json.dumps(start_env, sort_keys=True) + "\n")
            trace_stream.flush()
            start = clock()
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            launch = clock()
            current = snapshot("after_spawn")
            current["sampling_interval_ms"] = args.interval_ms
            samples.append(current)
            trace_stream.write(json.dumps(current, sort_keys=True) + "\n")
            trace_stream.flush()
            while True:
                try:
                    exit_code = process.wait(timeout=interval)
                    break
                except subprocess.TimeoutExpired:
                    current = snapshot("during")
                    current["sampling_interval_ms"] = args.interval_ms
                    samples.append(current)
                    trace_stream.write(json.dumps(current, sort_keys=True) + "\n")
                    trace_stream.flush()
            end = clock()
            current = snapshot("after_exit")
            current["sampling_interval_ms"] = args.interval_ms
            samples.append(current)
            trace_stream.write(json.dumps(current, sort_keys=True) + "\n")
            completed = (args.line_events is None or
                         (args.line_events.is_file() and
                          args.observer_script is not None and
                          args.observer_script.is_file()))
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        end = end or clock()
        gaps = [
            (b["sample_start"]["monotonic_ns"] -
             a["sample_start"]["monotonic_ns"])
            for a, b in zip(samples, samples[1:])
        ]
        required_missing = sorted({
            sensor for sample in samples
            for sensor in sample["missing_sensors"]
        })
        result = {
            "schema": "neta-qa005-ord-process-evidence-v1",
            "mode": args.mode,
            "pair": pair,
            "side": side,
            "command": command,
            "source_sha": current_sha,
            "toolchain": actual_go_version,
            "harness_sha256": metadata["harness_sha256"],
            "workload_config": metadata["workload_config"],
            "environment_sha256": sha256_file(environment_path),
            "collector_sha256": sha256_file(Path(__file__)),
            "strict_json_sha256": sha256_file(Path(__file__).with_name("qa005_ord_json.py")),
            "host_kernel": platform.platform(),
            "start_before_spawn": start,
            "start_after_spawn": launch,
            "exit_after_wait": end,
            "sampling_interval_ms": args.interval_ms,
            "sample_count": len(samples),
            "observed_max_sample_gap_ns": max(gaps) if gaps else None,
            "missing_sensors": required_missing,
            "exit_code": exit_code,
            "complete": completed and exit_code == 0,
            "log_sha256": sha256_file(output) if output.exists() else None,
            "trace_sha256": sha256_file(trace) if trace.exists() else None,
            "line_events_sha256": (sha256_file(args.line_events)
                                   if args.line_events and args.line_events.is_file() else None),
            "observer_script_sha256": (sha256_file(args.observer_script)
                                       if args.observer_script and args.observer_script.is_file() else None),
            "qualification": "DRIFT-INCONCLUSIVE",
            "reason": ("Timing/sensors are evidence only; independent 5m "
                       "statistical model, adequacy and host admission remain open."),
        }
        record.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if not completed or exit_code != 0:
        return exit_code if isinstance(exit_code, int) and exit_code > 0 else 1
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--mode", choices=("qa004", "core", "full"), required=True)
    parser.add_argument("--pair", type=int, choices=range(1, 11), required=True)
    parser.add_argument("--side", choices=("baseline", "candidate"), required=True)
    parser.add_argument("--interval-ms", type=int, default=250)
    parser.add_argument("--line-events", type=Path)
    parser.add_argument("--observer-script", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    return run(args)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print("ORD-EVID INCONCLUSIVE: " + str(exc), file=sys.stderr)
        sys.exit(2)
