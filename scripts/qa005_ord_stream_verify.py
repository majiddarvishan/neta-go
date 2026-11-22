#!/usr/bin/env python3
"""Read-only integrity validation for opt-in ORD per-line arrival evidence.

A per-line receipt timestamp is NOT a benchmark-case execution timestamp.
Only [pre-spawn, line receipt] is available as a conservative case
time envelope; it is too wide for an automatic DRIFT-VALID conclusion.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from qa005_ord_json import loads as strict_json_loads

ROW = re.compile(rb"^(Benchmark\S+)\s+([0-9]+)(?:\s|$)")


def raw_lines(data):
    """Yield LF-delimited raw lines including CR, NUL and invalid UTF-8."""
    pos = 0
    while pos < len(data):
        end = data.find(b"\n", pos)
        if end == -1:
            yield pos, data[pos:]
            break
        yield pos, data[pos:end + 1]
        pos = end + 1


def normalize_case_name(name):
    """Convert Go's -P benchmark execution suffix to comparator case ID."""
    if not re.search(r"-\d+$", name):
        raise ValueError("Missing Go test GOMAXPROCS row suffix")
    return re.sub(r"-\d+$", "", name)


def verify_stream(raw_log, sidecar, pre_spawn_ns, process_exit_ns,
                  expected_cases, pre_spawn_utc_ns=None,
                  process_exit_utc_ns=None):
    """Reject missing, duplicated, manipulated or misordered case evidence.

    pre_spawn_ns is the outer parent snapshot taken before child creation;
    these are receipt-time observations, NOT precise case execution times.
    """
    raw_log, sidecar = Path(raw_log), Path(sidecar)
    if (type(pre_spawn_ns) is not int or
            type(process_exit_ns) is not int or
            not 0 < pre_spawn_ns < process_exit_ns):
        raise ValueError("Invalid monotonic process launch/exit")
    if ((pre_spawn_utc_ns is None) != (process_exit_utc_ns is None) or
            (pre_spawn_utc_ns is not None and
             (type(pre_spawn_utc_ns) is not int or
              type(process_exit_utc_ns) is not int or
              not 0 < pre_spawn_utc_ns <= process_exit_utc_ns))):
        raise ValueError("Invalid UTC process launch/exit")
    if not isinstance(expected_cases, set) or not expected_cases:
        raise ValueError("Expected benchmark case IDs required")
    raw = raw_log.read_bytes()
    events = [strict_json_loads(line) for line in
              sidecar.read_text(encoding="utf-8").splitlines()]
    originals = list(raw_lines(raw))
    if len(events) != len(originals):
        raise ValueError("Raw log/event count differs")
    case_rows = {}
    last_observed_ns = pre_spawn_ns
    last_utc_ns = pre_spawn_utc_ns if pre_spawn_utc_ns is not None else 0
    for i, (event, (offset, line)) in enumerate(zip(events, originals), 1):
        if not isinstance(event, dict):
            raise ValueError("Invalid line event object")
        kind = "other"
        name = None
        iterations = None
        m = ROW.match(line.rstrip(b"\r\n"))
        if m:
            kind, name, iterations = (
                "benchmark_result", m.group(1).decode("utf-8"), int(m.group(2))
            )
            if iterations <= 0:
                raise ValueError("Benchmark iteration count must be positive")
        # JSON Boolean is a Python int subclass: accept only exact int types.
        if (type(event.get("line_index")) is not int or
                type(event.get("byte_offset")) is not int or
                type(event.get("length_bytes")) is not int or
                (event.get("benchmark_iterations") is not None and
                 type(event.get("benchmark_iterations")) is not int) or
                event.get("line_index") != i or
                event.get("byte_offset") != offset or
                event.get("length_bytes") != len(line) or
                event.get("line_sha256") != hashlib.sha256(line).hexdigest() or
                event.get("kind") != kind or
                event.get("benchmark_name") != name or
                event.get("benchmark_iterations") != iterations):
            raise ValueError("Line identity, kind or raw-log SHA mismatch")
        t0 = event.get("read_start_monotonic_ns")
        t1 = event.get("read_end_monotonic_ns")
        utc_ns = event.get("read_end_utc_ns")
        if (type(t0) is not int or type(t1) is not int or
                type(utc_ns) is not int or utc_ns <= 0 or utc_ns < last_utc_ns or
                (process_exit_utc_ns is not None and utc_ns > process_exit_utc_ns) or not
                (pre_spawn_ns <= t0 <= t1 <= process_exit_ns) or
                t1 < last_observed_ns):
            raise ValueError("Line receipt clock outside process monotonic/UTC interval")
        last_observed_ns = t1
        last_utc_ns = utc_ns
        if name:
            case = normalize_case_name(name)
            if case not in expected_cases:
                raise ValueError("Unexpected benchmark case: " + case)
            if case in case_rows:
                raise ValueError("Duplicate benchmark result: " + case)
            case_rows[case] = {
                "benchmark_iterations": iterations,
                "line_index": i,
                "arrival_monotonic_ns": t1,
                "arrival_utc_ns": utc_ns,
                "earliest_possible_case_ns": pre_spawn_ns,
                "latest_possible_case_ns": t1,
                "interval_width_ns": t1 - pre_spawn_ns,
                "timing_semantics": "case_finished_no_later_than_stdout_receipt;start_unobserved",
            }
    if set(case_rows) != expected_cases:
        raise ValueError("Missing expected benchmark case results")
    return {
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "events_sha256": hashlib.sha256(sidecar.read_bytes()).hexdigest(),
        "observed_lines": len(events),
        "observed_benchmark_cases": len(case_rows),
        "case_observation_intervals": case_rows,
        "precision_proved": False,
        "qualification": "DRIFT-INCONCLUSIVE",
    }
