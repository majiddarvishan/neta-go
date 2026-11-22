# ORD-EVID strict JSON evidence decoding (2026-11-22)

**Status:** software-only fail-closed parser hardening. It does not qualify the host, time evidence, sampling accuracy, observer overhead, or any performance/memory metric. Parent ORD-EVID and Q-ENV-01 remain OPEN; reports remain `DRIFT-INCONCLUSIVE`.

## Problem

Python's default `json.loads` accepts duplicate object keys using last-key-wins semantics and accepts non-standard `NaN`, `Infinity`, and `-Infinity` constants. A contradictory evidence object could therefore be interpreted differently by another parser, and unknown non-finite fields could pass through a schema that validates only selected keys.

## Change

`scripts/qa005_ord_json.py` provides one strict decoder that:
- rejects duplicate keys at every object depth;
- rejects non-standard non-finite JSON numeric constants;
- preserves normal JSON types and rejects malformed input.

The collector uses it for the environment manifest before spawning the child. The analyzer uses it for environment manifests, process records, raw telemetry snapshots and comparison metadata. The line-sidecar verifier uses it for every per-line observer event.

The collector records `strict_json_sha256` in each process record; the analyzer verifies that digest, binding the evidence to the exact parser helper used by the collector.

## Synthetic tests

Tests cover valid nested objects, duplicate top-level and nested keys, all three non-standard numeric constants, malformed JSON, duplicate environment/process/sidecar keys, and a collector refusal before the benchmark child starts.

## Limits

This is input-interpretation integrity only. It does not make evidence authentic or signed, establish sensor completeness, prove the observer's timing accuracy, or change any qualification result. No benchmark, A/A, stress, soak, extended fuzz, baseline/SLA, Performance Gate, public API, wire, v1.0.0 source or tag changes.
