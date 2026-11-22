# ORD-EVID strict telemetry fail-closed validation (2026-11-21)

**Status:** software-only validation hardening; no host qualification. Parent work item **QENV-AA-02.ORD-EVID remains OPEN** and every report remains **DRIFT-INCONCLUSIVE**.

## Findings addressed

The prior analyzer used `isinstance(value, int)` for monotonic/UTC timestamps. Python Boolean values are integer subclasses, so `True` and `False` could pass selected timestamp checks. The run provenance comparison also accepted `False == 0` for an exit code and `True == 1` for pair 1. Sample count and missing-sensor summaries were not required to have exact JSON types.

The previous trace validation checked snapshot start-time ordering but did not enforce a complete snapshot-kind sequence, non-overlapping sample windows, exact sensor-key coverage, or consistency between sensor payloads and missing-sensor declarations. Line receipt UTC was checked for monotonicity but not bounded by the process's recorded UTC start/exit clocks.

## Implemented validation

`scripts/qa005_ord_telemetry_verify.py` now validates the process trace independently:

- Clock records must contain exact positive integer `monotonic_ns` and `utc_ns` fields; Boolean and floating-point values are rejected.
- Process chronology is strictly ordered: pre-spawn < post-spawn < exit, in both monotonic and UTC domains.
- Snapshot kinds must be `before_spawn`, `after_spawn`, zero or more `during`, and `after_exit`.
- Snapshot windows must be ordered and non-overlapping; boundary snapshots must correctly surround the process.
- Sample count, maximum start-to-start sampling gap, and process-level missing-sensor union must exactly match the raw trace.
- Sensor payload keys must match the collector schema. Scalar values, vmstat keys, path/value maps, and the mandatory boot identity are validated.
- Missing sensor declarations must exactly match null scalar/map readings. A partially missing governor/frequency/thermal map is explicitly declared missing rather than silently treated as complete.
- Missing boot identity, malformed or contradictory data, and incomplete snapshots fail closed.

The collector now marks a path/value sensor map as missing when any entry is unreadable. The drift analyzer uses exact integer checks for pair and exit-code provenance and binds every line-receipt UTC timestamp to the process UTC interval. The stream verifier also rejects zero-iteration benchmark rows.

## Synthetic coverage

New tests exercise Boolean/float spoofing, malformed clocks, sample-kind substitution, overlapping/regressing windows, process and line-receipt UTC bounds, omitted sensor keys, partial sensor maps, missing-sensor summary mismatch, boot-ID changes, sampling-gap mismatch, and zero-iteration benchmark rows.

These are data-integrity tests only. They do not demonstrate that the sensor paths exist on a Reference Host, that the observed sampling cadence is adequate, that the host is E-VALID, or that the observer is low-overhead.

## 2026-11-22 strict JSON extension

The evidence path now uses `scripts/qa005_ord_json.py` for environment manifests, process records, telemetry snapshots, comparison metadata and line-observer sidecars. Duplicate keys at any object depth and non-standard `NaN`/infinity constants are rejected. The collector records `strict_json_sha256`, and the analyzer verifies it. Synthetic tests cover duplicate environment/process/sidecar keys and collector refusal before child spawn. See [strict JSON note](NETA_GO_ORD_JSON_STRICTNESS_2026-11-22.md).

This hardens evidence interpretation only; it does not authenticate evidence, qualify host sensors, or change the mandatory `DRIFT-INCONCLUSIVE` disposition.

## Qualification boundary and remaining work

- `environment_validity` remains `E-UNKNOWN` until the approved host-admission and A/A evidence requirements are met.
- `host_mode_admission` remains `NOT_PERFORMED`; `qualification` remains `DRIFT-INCONCLUSIVE`.
- No real A/A, QA-004/005 benchmark, stress, soak, extended fuzz, numeric baseline/SLA, Performance Gate, retained-memory PASS, public API/wire change, v1.0.0 source or tag change is included.
- Real reference-host sensor coverage, sample cadence, observer overhead/backpressure, continuous case-time uncertainty, nonlinear model adequacy and independent evidence review remain open.

No Qualification package is closed by this work.
