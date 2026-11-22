# Q-COR-02 bounded reconnect and lifecycle harness (2026-11-22)

**Status:** deterministic software-only harness. Q-COR-02 remains OPEN; this is not a Stress/Load/Soak Qualification result.

## Deterministic reconnect scenario

`phase_q_cor02_test.go` runs one Client through three TCP Session generations:
1. A peer accepts Bind and returns a successful V2 Bind Response.
2. The peer resets the connection (TCP RST); the test verifies OnClose reports the correct Session and a terminal cause.
3. The Client must not create another connection while `WithAutoReconnect(false)` is configured. The test waits a bounded 50 ms observation window and asserts the accepted-connection count did not change.
4. The test explicitly calls `Client.Connect` for the next generation and verifies a new Session pointer is published.
5. After two explicit reconnects, the third generation completes a Stream Request/Response and graceful Unbind.

The peer has a bounded five-second per-connection deadline; the test has a ten-second context. No randomized workload or implicit retry is involved.

## Bounded test set

`scripts/phase-q-cor02-light.sh` runs the reconnect scenario plus existing tests for fragmented frames, absolute Bind deadlines, TCP reset/EOF, duplicate identity, pre-Bind and bound-session capacity, concurrent Bind admission, request-credit oversubscription, worker enqueue/retirement/forced-close races, incoming aggregate overflow, and Client generation visibility.

The script:
- requires a clean tracked/untracked source worktree;
- records exact source SHA and Go toolchain;
- verifies every named test exists before execution;
- runs one `-race -count=1` pass with `GOMAXPROCS=2` and a 90-second Go test timeout;
- writes a manifest, full log and SHA-256 sums.

The workflow uploads the bounded evidence artifact. The harness is deterministic and has no random seed (`NOT_USED`).

## Explicit exclusions

No high-volume load, prolonged stress, reconnect soak, benchmark, 30-minute soak, extended fuzz, Reference Host, numeric baseline/SLA, Performance Gate or production behavior change is included. The 50 ms no-auto-retry observation is a bounded correctness assertion, not a reconnect reliability qualification.

Q-COR-02 remains OPEN until its full owner-approved campaign and acceptance criteria are run on the appropriate environment.
