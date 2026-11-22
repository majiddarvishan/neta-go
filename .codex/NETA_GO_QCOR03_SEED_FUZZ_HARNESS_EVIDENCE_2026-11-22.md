# Q-COR-03 — Deterministic Seed Replay and Bounded Fuzz Harness

**Date:** 2026-11-22  
**Branch:** `qual/q-cor03-seed-replay-2026-11-22`  
**Status:** Harness implemented and smoke-validated; extended fuzz Qualification remains OPEN.

## Harness components

- `scripts/phase-q-cor03-seed-check.sh`: clean-worktree preflight, enumerates all embedded fuzz targets, replays deterministic seeds, records exact source/Go identity, logs and SHA-256 evidence.
- `scripts/phase-q-cor03-fuzz-campaign.sh`: runs the seven V1/V2 parser fuzz targets sequentially with bounded parallel workers, per-target timeout, exact source identity, logs, status manifest and SHA-256 sums. Go's built-in fuzz engine minimizes a discovered failing input.
- `.github/workflows/phase-q-cor03-seeds.yml`: runs seed replay plus a default 1-second-per-target fuzz smoke on the task branch. Manual dispatch exposes a per-target duration input; longer campaigns are not started automatically and require separate owner authorization.

## Validation

1. [Deterministic seed replay](https://github.com/majiddarvishan/neta-go/actions/runs/45024840700) — PASS.
2. [Seed replay + bounded fuzz smoke](https://github.com/majiddarvishan/neta-go/actions/runs/45025704458) — PASS; both evidence artifacts uploaded.

The bounded fuzz smoke used `FUZZTIME=1s` and `FUZZ_PARALLEL=2` for each of these seven targets:

- `FuzzParseHeader`
- `FuzzDecodeFrame`
- `FuzzDecodeBindRequest`
- `FuzzDecodeBindResponse`
- `FuzzDecodeStreamRequest`
- `FuzzDecodeBindRequestV2`
- `FuzzDecodeBindResponseV2`

All **7/7** targets passed. The run executed approximately **257,947** fuzz inputs in total. No failing corpus or crash was reported.

## Limits

- One second per target validates the harness only; it is not an extended fuzz campaign or a statistical confidence claim.
- No long-duration fuzz, soak, stress/load or performance test was run.
- The workflow's longer manual duration input is a capability only; it does not authorize starting a long campaign.
- Q-COR-03 remains OPEN until the separately authorized extended fuzz/mutation acceptance campaign is completed and reviewed.
- This branch is not merged to protected `main`; no release/tag or Performance Gate change.
