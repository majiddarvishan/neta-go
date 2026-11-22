#!/usr/bin/env bash
# Q-COR-04: bounded real-peer V1 interoperability + deterministic transport faults.
# Run from a clean neta-go checkout after building the pinned private C++ peer.
set -Eeuo pipefail
umask 077

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GO_BIN="${GO:-go}"
PEER_BIN="${NETA_CPP_PEER_BIN:-}"
PEER_SOURCE_SHA="${NETA_CPP_PEER_SOURCE_SHA:-}"
EXPECTED_PEER_SOURCE_SHA="f7bd1eb779baff0d10e624f20522df345e6ee747"
OUT_DIR="${1:-${TMPDIR:-/tmp}/neta-qcor04-$(git rev-parse --short HEAD)}"
OUT_DIR="$(realpath -m -- "$OUT_DIR")"
GOLDEN_BIN="$OUT_DIR/neta-cpp-wire-golden"

if [[ -z "$PEER_BIN" || ! -x "$PEER_BIN" ]]; then
  echo "NETA_CPP_PEER_BIN must name an executable pinned neta-cpp peer" >&2
  exit 2
fi
if [[ "$PEER_SOURCE_SHA" != "$EXPECTED_PEER_SOURCE_SHA" ]]; then
  echo "Refusing unpinned C++ peer source SHA: $PEER_SOURCE_SHA" >&2
  exit 2
fi
case "$OUT_DIR" in
  "$ROOT"|"$ROOT"/*)
    echo "Q-COR-04 artifact directory must be outside the source checkout" >&2
    exit 2
    ;;
esac

command -v "$GO_BIN" >/dev/null
command -v g++ >/dev/null
command -v realpath >/dev/null
command -v sha256sum >/dev/null
command -v timeout >/dev/null
command -v diff >/dev/null

if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "Q-COR-04 requires a clean neta-go source worktree" >&2
  exit 2
fi

SOURCE_SHA="$(git rev-parse HEAD)"
PEER_BINARY_SHA="$(sha256sum "$PEER_BIN" | awk '{print $1}')"
GO_VERSION="$("$GO_BIN" version)"
mkdir -p -- "$OUT_DIR"
OUT_DIR="$(cd -- "$OUT_DIR" && pwd)"
GOLDEN_BIN="$OUT_DIR/neta-cpp-wire-golden"

tests=(
  TestLegacyNetaCPPClientConfigUsesV1
  TestNetaCPPServerWithGoClient
  TestGoServerWithNetaCPPClient
  TestTCPFragmentedBindAndOutOfOrderResponses
  TestSlowTrickleCannotExtendBindResponseDeadline
  TestAbruptTCPResetClosesBoundGeneration
  TestGracefulEOFClosesBoundGeneration
)
listed="$("$GO_BIN" test -list '^Test' .)"
for test_name in "${tests[@]}"; do
  if ! grep -Fxq "$test_name" <<<"$listed"; then
    echo "Required Q-COR-04 test missing: $test_name" >&2
    exit 2
  fi
done
pattern="^($(IFS='|'; echo "${tests[*]}"))$"

COMPLETED=0
ACTIVE=""
trap 'finish $?' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

finish() {
  local rc="$1"
  trap - EXIT
  if [[ -n "$ACTIVE" ]]; then
    printf '%s\tINTERRUPTED\t%s\tunknown\t%s\n' "$ACTIVE" "$rc" "$(date -u +%FT%TZ)" >> "$OUT_DIR/stages.tsv"
  fi
  local result=FAIL
  if (( rc == 0 && COMPLETED == 4 )) && [[ -z "$ACTIVE" ]]; then result=PASS; fi
  {
    echo "task=Q-COR-04"
    echo "source_sha=$SOURCE_SHA"
    echo "go_version=$GO_VERSION"
    echo "cpp_peer_source_sha=$PEER_SOURCE_SHA"
    echo "cpp_peer_binary_sha256=$PEER_BINARY_SHA"
    echo "cpp_peer_version=Pinex 1.5.0"
    echo "interop_directions=Go Client to C++ Server; C++ Client to Go Server"
    echo "protocol_version=V1 explicit on Go Client; pinned C++ peer uses V1"
    echo "fault_cases=fragmented Bind/out-of-order responses; absolute Bind deadline; TCP RST; graceful EOF"
    echo "fault_case_peer=deterministic Go raw TCP peer; not C++ fault injection"
    echo "golden_fixture=compiled pinned C++ fixture and compared"
    echo "test_count=${#tests[@]}"
    printf 'test=%s\n' "${tests[@]}"
    echo "stress_load_soak=NOT_RUN"
    echo "extended_fuzz=NOT_RUN"
    echo "performance_gate=DISABLED"
    echo "retained-attributed-B=INCONCLUSIVE"
    echo "completed_stages=$COMPLETED/4"
    echo "result=$result"
    echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$OUT_DIR/status.txt"
  find "$OUT_DIR" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 -r sha256sum > "$OUT_DIR/SHA256SUMS"
  echo "Q-COR-04 $result ($COMPLETED/4 stages); evidence: $OUT_DIR"
  echo "---- Q-COR-04 manifest ----"
  cat "$OUT_DIR/status.txt"
  echo "---- Q-COR-04 checksums ----"
  cat "$OUT_DIR/SHA256SUMS"
  if [[ "$result" != PASS ]]; then exit 1; fi
}

printf 'stage\tstatus\texit_code\tstarted_utc\tfinished_utc\n' > "$OUT_DIR/stages.tsv"

stage() {
  local label="$1"; shift
  local started rc
  started="$(date -u +%FT%TZ)"
  ACTIVE="$label"
  echo "====== Q-COR-04 $label ======"
  set +e
  "$@" 2>&1 | tee "$OUT_DIR/$label.log"
  rc=${PIPESTATUS[0]}
  set -e
  printf '%s\t%s\t%s\t%s\t%s\n' "$label" "$([[ "$rc" -eq 0 ]] && echo PASS || echo FAIL)" "$rc" "$started" "$(date -u +%FT%TZ)" >> "$OUT_DIR/stages.tsv"
  ACTIVE=""
  if (( rc != 0 )); then return "$rc"; fi
  COMPLETED=$((COMPLETED+1))
}

stage build-cpp-golden g++ -std=c++20 -O2 -Wall -Wextra \
  -I testdata/neta-cpp-1.5.0/source/include \
  testdata/neta-cpp-1.5.0/golden.cpp -o "$GOLDEN_BIN"

stage compare-cpp-golden bash -c \
  'set -euo pipefail; "$1" > "$2"; diff -u "$3" "$2"' \
  _ "$GOLDEN_BIN" "$OUT_DIR/cpp-golden.txt" "testdata/neta-cpp-1.5.0/golden.txt"

stage live-interop-and-faults env GOMAXPROCS=2 NETA_CPP_PEER_BIN="$PEER_BIN" \
  timeout 120s "$GO_BIN" test -count=1 -timeout=90s -run "$pattern" .

stage live-interop-and-faults-race env GOMAXPROCS=2 NETA_CPP_PEER_BIN="$PEER_BIN" \
  timeout 120s "$GO_BIN" test -race -count=1 -timeout=90s -run "$pattern" .

echo "Q-COR-04 bounded real-peer interoperability and transport-fault checks completed."
