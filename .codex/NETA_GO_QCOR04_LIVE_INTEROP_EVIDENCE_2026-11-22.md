# Q-COR-04 — Live Go/C++ V1 TCP Interoperability and Fault Harness Evidence

**Date:** 2026-11-22  
**Candidate branch:** `qual/q-cor04-live-fault-harness-2026-11-22`  
**Production source baseline:** protected `main` `d376cd8a375328aa971cd4441d989920bf6009a0`  
**Initial harness-only candidate SHA:** `18b69ed2c934f75c6c2461ed6d6c3cb32b65de57`  
**Consolidated candidate tested SHA:** `63cbb9f41c76090d5fd32452e3fe48dafdfd223e`  
**Disposition:** Q-COR-04 correctness acceptance CLOSED on unchanged production source; no performance qualification implied.

## Harness

`scripts/phase-q-cor04-live.sh` is a bounded, reproducible runner that:

1. Requires an executable C++ peer and the exact pinned source revision.
2. Compiles the pinned C++ golden fixture and compares output byte-for-byte.
3. Runs both real TCP directions:
   - Go Client → pinned C++ Server.
   - Pinned C++ Client → Go Server.
4. Runs deterministic transport fault cases:
   - fragmented Bind and out-of-order responses;
   - absolute Bind-response deadline under slow trickle;
   - abrupt TCP RST;
   - graceful EOF.
5. Repeats the selected tests under Go's race detector.
6. Prints exact source/toolchain/peer identity, result manifest and SHA-256 checksums.

The fault cases use the deterministic Go raw TCP peer; they are not represented as C++ fault injection. The live interoperability directions use the actual pinned C++ Client/Server peer.

## Exact validation

[Pinex candidate workflow run 45025742813](https://github.com/majiddarvishan/pinex/actions/runs/45025742813) and [consolidated-candidate run 45026010703](https://github.com/majiddarvishan/pinex/actions/runs/45026010703) — **both overall SUCCESS**.

- Pinned C++ source: `f7bd1eb779baff0d10e624f20522df345e6ee747` (Pinex 1.5.0).
- C++ peer binary SHA-256: `63dd13eaca9430bda0de3bcfc1302f89cf2f2af51d6e9543d3e4ffb49ca8d38e`.
- Go toolchain: `go1.23.12 linux/amd64`.
- Candidate neta-go harness SHAs: initial `18b69ed2c934f75c6c2461ed6d6c3cb32b65de57`; consolidated candidate `63cbb9f41c76090d5fd32452e3fe48dafdfd223e` (same harness source, docs-only changes afterward).
- Four stages PASS: C++ golden build, byte-for-byte golden comparison, live interop + fault tests, and the same test set under `-race`.
- Seven selected tests PASS:
  `TestLegacyNetaCPPClientConfigUsesV1`,
  `TestNetaCPPServerWithGoClient`,
  `TestGoServerWithNetaCPPClient`,
  `TestTCPFragmentedBindAndOutOfOrderResponses`,
  `TestSlowTrickleCannotExtendBindResponseDeadline`,
  `TestAbruptTCPResetClosesBoundGeneration`,
  `TestGracefulEOFClosesBoundGeneration`.

The workflow attempted to upload its artifact, but GitHub's artifact storage quota was exhausted. The upload step is explicitly non-blocking; the harness printed the complete manifest and SHA-256 checksums into the retained job log. The test job itself completed successfully. No test result was inferred from the artifact-upload status.

## Qualification boundary

- Q-COR-04 is closed for the specified live TCP correctness and deterministic fault scope.
- No production Go source, public API, wire format or official `v1.0.0` source/tag changed.
- Q-COR-02 full stress/load/reconnect campaign remains OPEN.
- Q-COR-03 extended fuzz campaign remains OPEN; the one-second-per-target smoke is harness validation only.
- No reference-host A/A, benchmark matrix, long soak, numerical baseline/SLA or Performance Gate was run or approved.
