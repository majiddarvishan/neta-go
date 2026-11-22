# QA-005 Owned-Buffer Overlay V19 — Retired Callback Ownership and Sampling Integrity

**Date:** 2026-11-22  
**Adapter:** `QA005-OWNED-BUFFER-OVERLAY-V19-UNQUALIFIED`  
**Branch:** `qual/mem004-retired-callback-guard-2026-11-22`  
**Status:** Synthetic diagnostic hardening only — MEM-004 and MEM-005 remain OPEN / INCONCLUSIVE.

## Purpose

V18 froze each Client's monotonic connect-attempt generation and current Session. That prevented a transient reconnect generation from silently changing the frozen owner set. One ownership hole remained: a Client generation could already be retired at the start of a measurement window while an application/completion/OnClose callback still retained its Session through a callback dispatcher's `callbackWorkerPool.sessions` map. Such a Session could be absent from `Client.current`, `benchmarkEnv.sessions` and the Server's live Session map.

V19 makes that condition fail closed without retaining an otherwise-unregistered Session pointer in the measurement registry.

## Changes

1. **Callback-owner audit at freeze.** The overlay snapshots the known Session identity set, then inspects each unique application/completion/OnClose callback pool one at a time under `pool.mu`. A nil/mismatched queue or a callback-owned Session absent from the frozen owner set invalidates the window.
2. **Callback-owner audit at every sample.** The same check runs from `qa005OwnedRegistryComplete`, so a newly visible unregistered callback-owned Session invalidates subsequent samples and the HWM upper.
3. **No implicit admission.** Unknown retired Sessions are not appended to the frozen registry. Doing so would keep them strongly reachable beyond the callback's own lifetime and could perturb GC/liveness.
4. **Sampling helper.** `qa005RecordSamplingWindow` records monotonic sample-start gaps and snapshot duration. Non-monotonic timestamps, zero timestamps and negative durations fail closed. It does not define or imply a maximum-gap acceptance threshold.

No production Go source, public API, wire behavior, Client lifecycle or callback scheduling code changed. The adapter remains an external Go test overlay.

## Synthetic validation

[GitHub Actions run 45025289359](https://github.com/majiddarvishan/neta-go/actions/runs/45025289359) — PASS.

- 22/22 Python anchored adapter tests PASS.
- Generated overlay Go lifecycle tests PASS under `go test -race`.
- Retired Client Session with an active callback present at freeze: rejected.
- Retired Client Session whose callback queue appears after freeze: subsequent sample/HWM rejected.
- Known active callback Session already in the frozen owner set: accepted once, with identity deduplication.
- Synthetic monotonic sample gaps and snapshot durations: recorded; duplicate timestamps, zero timestamps and negative durations rejected.
- Overlay generated outside the source checkout; source fixture and dependency hashes are recorded in the artifact manifest.

## Explicit limitations

- Callback pools are inspected one at a time; this is not an atomic cross-owner or process-wide heap snapshot.
- A callback queue that appears and disappears entirely between sampler observations can still escape observation. No approved maximum sample gap exists.
- The frozen registry continues to hold strong references to already-known Sessions. Observer-induced GC/liveness bias remains **NOT MEASURED**.
- V19 does not close all F1–F5/M1/D1 ownership, aliases, allocator/runtime overhead, external references, simultaneous peak, or retained-attributed memory.
- Sampling accuracy and observer overhead have not been proved on an accepted reference host.
- No reference-host A/A, 10 paired runs, long soak, heavy fuzz/stress campaign, numeric baseline/SLA or Performance Gate was run or approved.

## Qualification disposition

`coverage_status=PARTIAL_INCONCLUSIVE`  
`qualification=DIAGNOSTIC_ONLY`  
`sampler_max_gap_policy=NOT_APPROVED_DIAGNOSTIC_ONLY`  
`observer_gc_liveness_bias=NOT_MEASURED`

Do **not** emit `retained-attributed-B`, close MEM-004/MEM-005, approve a numeric memory baseline, or enable the mandatory Performance Gate from this evidence.
