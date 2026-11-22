#!/usr/bin/env bash
# Q-COR-03 bounded parser fuzz campaign. Default is a 1s-per-target harness smoke;
# longer campaigns require an explicit FUZZTIME override.
set -Eeuo pipefail
umask 077

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GO_BIN="${GO:-go}"
FUZZTIME="${FUZZTIME:-1s}"
FUZZ_PARALLEL="${FUZZ_PARALLEL:-2}"
FUZZ_TARGET_TIMEOUT="${FUZZ_TARGET_TIMEOUT:-10m}"
OUT_DIR="${1:-${TMPDIR:-/tmp}/neta-qcor03-fuzz-$(git rev-parse --short HEAD)}"
OUT_DIR="$(realpath -m -- "$OUT_DIR")"

if [[ ! "$FUZZTIME" =~ ^[1-9][0-9]*(ms|s|m)$ ]]; then
  echo "FUZZTIME must be a positive Go duration such as 1s, 30s or 2m" >&2
  exit 2
fi
if [[ ! "$FUZZ_PARALLEL" =~ ^[1-9][0-9]*$ ]] || (( FUZZ_PARALLEL > 8 )); then
  echo "FUZZ_PARALLEL must be an integer from 1 through 8" >&2
  exit 2
fi
case "$OUT_DIR" in
  "$ROOT"|"$ROOT"/*)
    echo "Q-COR-03 artifacts must be outside the source checkout" >&2
    exit 2
    ;;
esac

command -v "$GO_BIN" >/dev/null
command -v realpath >/dev/null
command -v timeout >/dev/null
command -v sha256sum >/dev/null
if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "Q-COR-03 requires a clean source worktree" >&2
  exit 2
fi

SOURCE_SHA="$(git rev-parse HEAD)"
GO_VERSION="$("$GO_BIN" version)"
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
for target in "${targets[@]}"; do
  if ! grep -Fxq "$target" <<<"$listed"; then
    echo "Required fuzz target missing: $target" >&2
    exit 2
  fi
done

mkdir -p -- "$OUT_DIR"
OUT_DIR="$(cd -- "$OUT_DIR" && pwd)"
COMPLETED=0
ACTIVE=""
trap 'finish $?' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

finish() {
  local rc="$1"
  trap - EXIT
  if [[ -n "$ACTIVE" ]]; then
    printf '%s\tINTERRUPTED\t%s\t%s\n' "$ACTIVE" "$rc" "$(date -u +%FT%TZ)" >> "$OUT_DIR/targets.tsv"
  fi
  if [[ -d internal/wire/testdata/fuzz ]]; then
    mkdir -p "$OUT_DIR/failing-or-saved-corpus"
    cp -a internal/wire/testdata/fuzz/. "$OUT_DIR/failing-or-saved-corpus/"
  fi
  git status --short --untracked-files=all > "$OUT_DIR/source-status-after.txt" || true
  local result=FAIL
  if (( rc == 0 && COMPLETED == ${#targets[@]} )) && [[ -z "$ACTIVE" ]]; then result=PASS; fi
  {
    echo "task=Q-COR-03"
    echo "source_sha=$SOURCE_SHA"
    echo "go_version=$GO_VERSION"
    echo "fuzztime_per_target=$FUZZTIME"
    echo "parallel=$FUZZ_PARALLEL"
    echo "target_timeout=$FUZZ_TARGET_TIMEOUT"
    echo "target_count=${#targets[@]}"
    printf 'target=%s\n' "${targets[@]}"
    echo "failing_input_minimization=Go built-in fuzz minimization"
    echo "long_soak=NOT_RUN"
    echo "performance_gate=DISABLED"
    echo "completed_targets=$COMPLETED/${#targets[@]}"
    echo "result=$result"
    echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$OUT_DIR/status.txt"
  find "$OUT_DIR" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 -r sha256sum > "$OUT_DIR/SHA256SUMS"
  echo "Q-COR-03 bounded fuzz $result ($COMPLETED/${#targets[@]} targets); evidence: $OUT_DIR"
  if [[ "$result" != PASS ]]; then exit 1; fi
}

printf 'target\tstatus\texit_code\tstarted_utc\tfinished_utc\n' > "$OUT_DIR/targets.tsv"
for target in "${targets[@]}"; do
  started="$(date -u +%FT%TZ)"
  ACTIVE="$target"
  echo "====== Q-COR-03 $target ($FUZZTIME, parallel=$FUZZ_PARALLEL) ======"
  set +e
  env GOMAXPROCS=2 timeout "$FUZZ_TARGET_TIMEOUT" "$GO_BIN" test \
    -run='^$' -fuzz="^$target$" -fuzztime="$FUZZTIME" \
    -parallel="$FUZZ_PARALLEL" -timeout=9m ./internal/wire \
    2>&1 | tee "$OUT_DIR/$target.log"
  rc=${PIPESTATUS[0]}
  set -e
  printf '%s\t%s\t%s\t%s\t%s\n' "$target" "$([[ "$rc" -eq 0 ]] && echo PASS || echo FAIL)" "$rc" "$started" "$(date -u +%FT%TZ)" >> "$OUT_DIR/targets.tsv"
  ACTIVE=""
  if (( rc != 0 )); then exit "$rc"; fi
  COMPLETED=$((COMPLETED+1))
done
