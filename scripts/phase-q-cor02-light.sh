#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GO_BIN="${GO_BIN:-go}"
OUT_DIR="${1:-${TMPDIR:-/tmp}/neta-qcor02-$(git rev-parse --short HEAD)}"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Q-COR-02 requires a clean tracked worktree" >&2
  exit 2
fi
if [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
  echo "Q-COR-02 refuses untracked files in the source worktree" >&2
  exit 2
fi

SOURCE_SHA="$(git rev-parse HEAD)"
GO_VERSION="$("$GO_BIN" version)"
mkdir -p "$OUT_DIR"

tests=(
  TestQCOR02ExplicitReconnectRequiresOwnerAction
  TestTCPFragmentedBindAndOutOfOrderResponses
  TestSlowTrickleCannotExtendBindResponseDeadline
  TestAbruptTCPResetClosesBoundGeneration
  TestGracefulEOFClosesBoundGeneration
  TestServerRejectsDuplicateSystemIDWithoutEvictingExistingSession
  TestServerMaxBoundSessionsRejectsNewIdentity
  TestServerPendingPreBindLimitRejectsBeforeSessionAllocation
  TestServerConcurrentDuplicateBindsHaveSingleWinner
  TestOwnerResourceLedgerConcurrentRequestAdmissionNeverOversubscribes
  TestWorkerConcurrentEnqueueAndIdleRetirementNeverStrandsWork
  TestWorkerConcurrentEnqueueAndForcedCloseSettlesEachTaskOnce
  TestSessionIncomingAggregateOverflowClosesOnlyOffendingSession
  TestSessionForcedCloseCancelsQueuedIncomingApplicationCharge
  TestClientCurrentSessionReturnsOnlyBoundGeneration
)

listed="$("$GO_BIN" test -list '^Test' .)"
for test_name in "${tests[@]}"; do
  if ! grep -Fxq "$test_name" <<<"$listed"; then
    echo "Required Q-COR-02 test missing: $test_name" >&2
    exit 2
  fi
done

pattern="^($(IFS='|'; echo "${tests[*]}"))$"
{
  echo "qualification=Q-COR-02"
  echo "scope=bounded deterministic correctness harness only"
  echo "source_sha=$SOURCE_SHA"
  echo "go_version=$GO_VERSION"
  echo "gomaxprocs=2"
  echo "race_detector=enabled"
  echo "random_seed=NOT_USED"
  echo "stress_campaign=NOT_RUN"
  echo "long_soak=NOT_RUN"
  echo "extended_fuzz=NOT_RUN"
  echo "benchmark=NOT_RUN"
  echo "test_count=${#tests[@]}"
  printf 'test=%s\n' "${tests[@]}"
} >"$OUT_DIR/manifest.txt"

set +e
GOMAXPROCS=2 "$GO_BIN" test -race -count=1 -timeout=90s -run "$pattern" ./... 2>&1 | tee "$OUT_DIR/go-test.log"
status=${PIPESTATUS[0]}
set -e

{
  echo "exit_code=$status"
  echo "result=$([[ "$status" -eq 0 ]] && echo PASS || echo FAIL)"
} >>"$OUT_DIR/manifest.txt"
sha256sum "$OUT_DIR/manifest.txt" "$OUT_DIR/go-test.log" >"$OUT_DIR/SHA256SUMS"

echo "Q-COR-02 bounded harness exit code: $status"
echo "Evidence directory: $OUT_DIR"
exit "$status"
