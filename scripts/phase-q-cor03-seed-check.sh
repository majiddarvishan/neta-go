#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GO_BIN="${GO_BIN:-go}"
OUT_DIR="${1:-${TMPDIR:-/tmp}/neta-qcor03-seeds-$(git rev-parse --short HEAD)}"
FUZZ_FILE="internal/wire/wire_fuzz_test.go"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Q-COR-03 seed replay requires a clean tracked worktree" >&2
  exit 2
fi
if [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
  echo "Q-COR-03 seed replay refuses untracked source files" >&2
  exit 2
fi

SOURCE_SHA="$(git rev-parse HEAD)"
GO_VERSION="$("$GO_BIN" version)"
mkdir -p "$OUT_DIR"

targets=(
  FuzzParseHeader
  FuzzDecodeFrame
  FuzzDecodeBindRequest
  FuzzDecodeBindResponse
  FuzzDecodeStreamRequest
  FuzzDecodeBindRequestV2
  FuzzDecodeBindResponseV2
)

listed="$("$GO_BIN" test -list '^Fuzz' ./internal/wire)"
{
  echo "qualification=Q-COR-03"
  echo "scope=deterministic embedded fuzz seed replay only"
  echo "source_sha=$SOURCE_SHA"
  echo "go_version=$GO_VERSION"
  echo "gomaxprocs=2"
  echo "race_detector=enabled"
  echo "seed_source=source-embedded f.Add"
  echo "randomized_mutation=NOT_RUN"
  echo "extended_fuzz=NOT_RUN"
  echo "fuzztime=NOT_APPLICABLE"
  for target in "${targets[@]}"; do
    if ! grep -Fxq "$target" <<<"$listed"; then
      echo "Required fuzz target missing: $target" >&2
      exit 2
    fi
    block="$(sed -n "/^func $target(f \\*testing.F) {/,/^}/p" "$FUZZ_FILE")"
    seed_count="$(grep -c 'f.Add(' <<<"$block" || true)"
    if [[ "$seed_count" -lt 1 ]]; then
      echo "Fuzz target has no embedded seed: $target" >&2
      exit 2
    fi
    echo "target=$target seeds=$seed_count"
  done
} >"$OUT_DIR/manifest.txt"

set +e
GOMAXPROCS=2 "$GO_BIN" test -race -count=1 -timeout=60s -run '^Fuzz' ./internal/wire 2>&1 | tee "$OUT_DIR/seed-replay.log"
status=${PIPESTATUS[0]}
set -e

{
  echo "exit_code=$status"
  echo "result=$([[ "$status" -eq 0 ]] && echo PASS || echo FAIL)"
} >>"$OUT_DIR/manifest.txt"
sha256sum "$OUT_DIR/manifest.txt" "$OUT_DIR/seed-replay.log" >"$OUT_DIR/SHA256SUMS"

echo "Q-COR-03 deterministic seed replay exit code: $status"
echo "Evidence directory: $OUT_DIR"
exit "$status"
