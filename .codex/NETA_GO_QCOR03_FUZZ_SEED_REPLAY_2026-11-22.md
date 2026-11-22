# Q-COR-03 reproducible fuzz seed replay (2026-11-22)

**Status:** Deterministic embedded-seed replay is reproducible, and the separate bounded fuzz harness passed its 1s-per-target smoke on the consolidated candidate. All seven parser targets passed (~368,043 executions); Q-COR-03 remains OPEN because extended fuzz/mutation acceptance is not complete.

## Fuzz target inventory

The current Go wire parser exposes seven fuzz targets in `internal/wire/wire_fuzz_test.go`:
- `FuzzParseHeader`
- `FuzzDecodeFrame`
- `FuzzDecodeBindRequest`
- `FuzzDecodeBindResponse`
- `FuzzDecodeStreamRequest`
- `FuzzDecodeBindRequestV2`
- `FuzzDecodeBindResponseV2`

Each target must retain at least one source-embedded `f.Add` seed. The deterministic replay harness validates target inventory and counts embedded seeds per target before running.

## Deterministic replay command

`scripts/phase-q-cor03-seed-check.sh`:
- requires a clean source worktree;
- records exact source SHA and Go toolchain;
- validates all seven fuzz target names and non-empty embedded seed sets;
- runs `GOMAXPROCS=2 go test -race -count=1 -timeout=60s -run '^Fuzz' ./internal/wire`;
- writes a manifest, complete log and SHA-256 sums.

In normal `go test` mode, `-run '^Fuzz'` replays the fixed seed corpus without randomized mutation. The seed-replay manifest correctly records `randomized_mutation=NOT_RUN` and `extended_fuzz=NOT_RUN`; randomized fuzzing is a separate step.

## Bounded fuzz smoke

`scripts/phase-q-cor03-fuzz-campaign.sh` runs the seven targets with a bounded per-target duration, parallel worker limit, per-target timeout, exact source identity, logs, status manifest and SHA-256 sums. The consolidated-candidate smoke used 1 second per target and 2 workers; all 7/7 targets passed (~368,043 executions) in [CI run #45025904772](https://github.com/majiddarvishan/neta-go/actions/runs/45025904772).

This is harness validation only. It is not an extended fuzz campaign, statistical confidence claim or Qualification acceptance. See [Q-COR-03 seed/fuzz harness evidence](NETA_GO_QCOR03_SEED_FUZZ_HARNESS_EVIDENCE_2026-11-22.md).

## Reproducibility boundary

The embedded seed corpus and its replay are deterministic. Go's mutation schedule is not claimed to be deterministic; future extended campaigns must retain exact source SHA, Go version, target, corpus, duration, worker count, crash corpus and artifact hashes.

Q-COR-03 remains OPEN pending an extended fuzz/mutation campaign and acceptance review. No heavy stress/soak or Performance Gate was run or approved.
