> **LATEST PHASE Q SOFTWARE-HARNESS STATUS — 2026-11-22:** Protected `main` is `d376cd8a375328aa971cd4441d989920bf6009a0`. Q-COR-02 bounded reconnect harness is merged on main and its dedicated, Go and C++ checks PASS; its full stress/load/reconnect campaign remains OPEN. Q-COR-03 seed replay plus 1s-per-target fuzz smoke passed **7/7** targets on the task branch; extended fuzz remains OPEN. Q-COR-04 two-way live Go/C++ V1 TCP, pinned C++ golden comparison and deterministic transport faults passed normal and race runs; **Q-COR-04 is CLOSED** ([evidence](NETA_GO_QCOR04_LIVE_INTEROP_EVIDENCE_2026-11-22.md)). MEM-004/005 V19 synthetic retired-callback and sampling-integrity checks passed, but both remain OPEN/INCONCLUSIVE because GC liveness bias, sample-gap acceptance and observer overhead are unproved ([V19 evidence](NETA_GO_QA005_RETIRED_CALLBACK_GUARD_V19_EVIDENCE_2026-11-22.md)). The consolidated candidate is `qual/phase-q-software-harnesses-2026-11-22`; [PR #59](https://github.com/majiddarvishan/neta-go/pull/59) is OPEN for review and all five PR checks PASS on head `926f3b244f4e85fe27478c4767c282730426f9e0` (Go #45026358040, C++ Wire #45026357958, parser mutation #45026357916, Q-COR-03 #45026357905, MEM-004/005 #45026357903). No production Go/API/wire changes, main merge, tag/release or Performance Gate activation. **17 normalized open packages remain: 8 Qualification + 7 Owner Decisions + 2 Release.**

> **PHASE Q ORD-EVID SAMPLING CADENCE INTEGRITY MERGED (2026-11-21):** [PR #54](https://github.com/majiddarvishan/neta-go/pull/54) merged as `db267ebe0993f898a8ff10bf6dbd650f7c3e7e42`. The collector-recorded interval is bound into every raw snapshot and verified against the process record and across all 20 A/A runs. Per-run scheduled `during` gaps (excluding pre-spawn/post-exit boundaries) report median/p95/max and max-gap/interval ratio. **75/75 synthetic tests PASS**; `acceptance_limit=NOT_ESTABLISHED` and `sampling_accuracy_proved=false` remain ([design](NETA_GO_ORD_SAMPLING_CADENCE_2026-11-21.md)).
> **PHASE Q ORD-EVID OBSERVER OVERHEAD ANALYSIS MERGED (2026-11-21):** [PR #52](https://github.com/majiddarvishan/neta-go/pull/52) merged as `394352765679bea36c055a06efacaa10c6cba11d`. Source audit confirms inline stdout-pipe forwarding and possible downstream backpressure. The report exposes `NOT_MEASURED`, `overhead_proved=false`, and `backpressure_possible=true`; timestamp semantics are explicit. **71/71 synthetic tests PASS**, including same-read timestamp brackets and a 512 KiB slow-reader byte-preservation fixture; postmerge Go/C++ checks PASS. Actual observer-on/off overhead and sampling accuracy remain Reference-Host work ([analysis](NETA_GO_ORD_OBSERVER_OVERHEAD_ANALYSIS_2026-11-21.md)).
> **PHASE Q ORD-EVID CONTINUOUS CASE-TIME ENCLOSURE HARDENING MERGED (2026-11-22):** [PR #56](https://github.com/majiddarvishan/neta-go/pull/56) merged at `b0dbd53799db5e481f7336a26fdb44a64f0bd803`. Adds binary64 input-conversion enclosure, the production `fit_one` pivot-tolerance guard and a second outward-rounded interval evaluator for the production Gauss-Jordan/coefficients/residual/covariance/corner-CI operation path. Synthetic coverage checks the closed-form enclosure against 1024 endpoints and 256 interiors, validates production `fit_one` float-path containment for exact-time inputs, covers >2^53 timestamps and a positive-but-below-pivot-threshold design, and requires broad covariance/variance uncertainty to fail closed while preserving diagnostics. **87/87 ORD-EVID synthetic tests PASS**. `continuous_interval_bound_proved=false`, `case_time_precision_proved=false`, E-UNKNOWN and DRIFT-INCONCLUSIVE remain.

> **PHASE Q ORD-EVID STRICT JSON HARDENING MERGED (2026-11-22):** PR #56 adds `qa005_ord_json.py`, rejecting duplicate object keys at any depth and non-standard NaN/infinity constants. Collector, analyzer and line-sidecar verifier use it; process evidence binds `strict_json_sha256`. Synthetic tests cover nested/top-level duplicates, malformed JSON, non-standard constants and pre-spawn refusal. Evidence integrity only; no Qualification result changes ([design](NETA_GO_ORD_JSON_STRICTNESS_2026-11-22.md)).
> **PHASE Q ORD-EVID TELEMETRY FAIL-CLOSED VALIDATION MERGED (2026-11-21):** [PR #48](https://github.com/majiddarvishan/neta-go/pull/48) merged as `3e6596111d4f6faf3187b848cb5d898d0d551f7a`. Strict process/snapshot clock typing, ordered non-overlapping windows, exact sensor-schema and missing-sensor consistency, process-bounded line-receipt UTC, and positive benchmark-iteration validation are integrated. **62/62 synthetic tests PASS**; postmerge Go/C++ checks PASS; branch cleanup verified. This is data-integrity hardening only; E-UNKNOWN and DRIFT-INCONCLUSIVE remain; no Qualification package closes.
> **PHASE Q ORD-EVID CASE-TIME SENSITIVITY MERGED (2026-11-21):** [PR #46](https://github.com/majiddarvishan/neta-go/pull/46) merged as `30885bc90d1beea11573bde60fb8b4f7f8b793db`. Added report-only paired-case interval endpoint sensitivity over all unique (2^{10}) assignments, with time-slope and joint 5m corner-CI envelopes. **41/41 synthetic tests PASS**; postmerge Go/C++ checks PASS; branch cleanup verified. This is not a continuous interval bound; every result remains `DRIFT-INCONCLUSIVE`. No heavy Qualification, host admission, numeric baseline/SLA, memory PASS or Performance Gate change; normalized **18 top-level packages remain open**.

> **PHASE Q CORRECTNESS ACCEPTED — 2026-11-20:** **Q-COR-01 [x] CLOSED**: released immutable annotated `v1.0.0` source `d8437f36ec812a596bada1398c7af9b530a18118` passed **6/6** scoped stages ([exact-tag qualification CI 44807019239](https://github.com/majiddarvishan/neta-go/actions/runs/44807019239), [PR #41](https://github.com/majiddarvishan/neta-go/pull/41)); 14 example builds, V1/V2 OnRequest/QA-007 race, bounded full example smoke, 2 live routed peer clients/negative route and graceful stops. After squash merge `74872c649b9f525f5fb8338f80322e5b1491285b`, required [Go 44807267236](https://github.com/majiddarvishan/neta-go/actions/runs/44807267236) and [C++ 44807267191](https://github.com/majiddarvishan/neta-go/actions/runs/44807267191) postmerge checks both SUCCESS. **18 normalized top-level packages remain = 9 Qualification + 7 Owner Decisions + 2 Release**. `QENV-AA-02.ORD-EVID` remains OPEN (collector preparation is not DRIFT-VALID), Q-ENV-01/QA-004/005/MEM-004/005/006 OPEN, numerical baseline/SLA unapproved, retained memory INCONCLUSIVE, performance gate DISABLED. Official tags unchanged.

> **OFFICIAL v1.0.0 TAG + GITHUB RELEASE VERIFIED — 2026-11-20:** [GA evidence](GA_RELEASE_VERIFIED_2026-11-20.md) shows annotated tag object `b5c5ce7b9fe6c3ea4fceec0eb98a4621b749e28b` peels exactly to protected-main GA source `d8437f36ec812a596bada1398c7af9b530a18118`; non-prerelease [GitHub Release](https://github.com/majiddarvishan/neta-go/releases/tag/v1.0.0), publisher and both exact-SHA Go/C++ checks SUCCESS. **P9-06 [x] CLOSED (publication only, owner override §85)**; R-01 and R-02 remain OPEN because full Qualification/admin review is not complete. Current **19 normalized open top-level packages = 10 Qualification + 7 Owner Decisions + 2 remaining Release**. Pending **GA-CLEAN** merged-branch cleanup is a supplementary maintenance task triggered by the GA evidence marker merge, not a Qualification PASS. Q-ENV-01, QA-004/005, MEM-004/005/006 still INCONCLUSIVE, Gate DISABLED; RC tag unchanged.

> **OFFICIAL v1.0.0 RELEASE & CLEANUP OWNER AUTHORIZATION — 2026-11-20:** [Decision §85](DECISION_LOG.md) explicitly approves publishing the same Go/wire code as official **`v1.0.0`**, with truthful incomplete-Qualification disclosure and retiring only previously merged, unchanged, allowlisted branch refs. [GA approval](GA_RELEASE_APPROVAL_2026-11-20.md), [release notes](../docs/RELEASE_V1.0.0_NOTES.md). **GA-01 [ ] PENDING exact-green-main annotated tag + GitHub Release verification; GA-CLEAN [ ] PENDING merged-branch deletion evidence.** P9-06 remains [ ] until actual publication. Q-ENV-01, QA-004/005, MEM-004/005/006 and Q-COR Phase Q still OPEN/INCONCLUSIVE; numerical baseline/SLA unapproved, Performance Gate DISABLED. Existing RC tag immutable. Active normalized tally remains 20 until actual verified publication.

> **INTEGRATION RC — OWNER APPROVED (2026-11-20):** all previous work already on protected `main` (no open PRs at preflight). [Decision §83](DECISION_LOG.md) authorizes immutable **`v1.0.0-rc.1`** candidate version/tag from a reviewed **postmerge green exact SHA** for parallel application use; [RC approval record](PRERELEASE_TAG_APPROVAL_2026-11-20.md), [execution plan](NETA_GO_PHASE_Q_PARALLEL_EXECUTION_PLAN_2026-11-20.md). **RC-01 [x] CLOSED: annotated tag ref independently verified** at object `1e07c00f97b6243f932aba91c544f81b73e6fc9d`, peeling to protected-main release SHA `0bd50760a9200194f9ae0088d26751d0f6ee00c7`; both required exact-SHA postmerge Go/C++ checks and one-shot tag workflow SUCCESS. See [Decision §84](DECISION_LOG.md). Phase Q 10 packages, 7 owner decisions and 3 final-GA release packages still OPEN (20 total); no change to final `v1.0.0` P9-06, Q-ENV-01, memory INCONCLUSIVE or Gate DISABLED.

> **QENV-AA-02.ORD — OWNER OPTION A APPROVED (2026-11-20):** [order/time policy](NETA_GO_QENV_AA_ORDER_DRIFT_POLICY_2026-11-20.md) and [Decision Log §82](DECISION_LOG.md) fix the **joint 5m Bonferroni 95% simultaneous mean-plus-four-corners test** for each QA-004/Core/Full case-metric, inside existing symmetric 5%/7.5% bounds and after E-VALID. **ORD statistical policy [x] CLOSED; ORD-EVID collection/tooling and actual proof [ ] OPEN** under Q-ENV-01 [ ] OPEN. Missing timing/thermal evidence or poor model fit => DRIFT-INCONCLUSIVE; no host/Mode admission, runner edits, heavy Qualification or Gate authorized. 20 main open packages unchanged.

> **QENV-AA-02 — OWNER OPTION A APPROVED (2026-11-20):** [symmetric-equivalence contract](NETA_GO_QENV_AA_EQUIVALENCE_POLICY_2026-11-20.md) and [Decision Log §81](DECISION_LOG.md) establish **5%** for QA-005 throughput/P50/P95, and **7.5%** for QA-005 P99/CPU/op/allocs/op and QA-004 terminal-settlement P99, using 10 matched same-SHA pairs and mode-family Bonferroni-adjusted simultaneous two-sided 95% paired-log CIs. **QENV-AA-02 policy/margin [x] CLOSED; QENV-AA-02.ORD Option A statistical rule [x] CLOSED; QENV-AA-02.ORD-EVID measurement/evidence [ ] OPEN.** No specific host or Mode qualified, no run authorized, Q-ENV-01 [ ] OPEN; 20 top-level open packages unchanged, Gate DISABLED.

> **QENV-AA-01 — OWNER OPTION B APPROVED (2026-11-20):** policy subdecision is **[x] CLOSED**; fail-closed reference-host admission is **per mode** (`qa004`, `core`, `full`), with valid dedicated-host evidence and all non-retained applicable per-case results; no single-mode admission implies another. The comparator's relative `PASS` is only one-sided non-regression and a separately owner-approved symmetric A/A equivalence/ordering-drift rule remains necessary. [Decision Log §80](DECISION_LOG.md), [admission policy](NETA_GO_QENV_AA_ADMISSION_DECISION_2026-11-20.md). **No host or mode qualified**, **Q-ENV-01 stays [ ] OPEN**; 20 normalized open top-level packages unchanged, Phase Q not authorized, Gate DISABLED.

> **PHASE-Q HOST/MEMORY ADMISSION DESIGN — 2026-11-20:** Proposed host CPU/toolchain/governor/thermal/swap checks, all-applicable-metric A/A review, category-by-category Hybrid-B coverage, non-atomic peak/sampling validity and three-mode observer overhead are documented in [Q-ENV/MEM Admission Spec](NETA_GO_PHASE_Q_HOST_MEMORY_ADMISSION_SPEC_2026-11-20.md). **PROPOSAL, not approval.** Q-ENV-01, MEM-004/005 and ten total Qualification work packages remain `[ ]`; 20 distinct packages remain open (10 Qualification, 7 other Owner Decisions, 3 Release). Existing OD-ENV-01=A and OD-MEM-01=A decisions stay approved; reference machine, numeric thresholds, source baseline/SLA and heavy Phase Q remain unapproved. Reviewed protected `main` at `0c01ac27bdffd9031f59b3ae466823f036839cf5` (PR #29 merged, both required postmerge checks successful).

> **OWNER DECISIONS (2026-11-20):** OD-ENV-01 **Option A** = dedicated controlled qualification host (policy selection only, not host acceptance); OD-MEM-01 **Option A** = fail-closed `retained-attributed-B` **INCONCLUSIVE** until coverage/ownership/sampling/bias evidence is valid (does not replace M1/D1 instrumentation Option B). Both decisions are `[x]` in the active register; **open unique packages now 20 = 10 Qualification + 7 Owner Decisions + 3 Release**. Heavy Phase Q remains unauthorized, Performance Gate DISABLED, numeric baseline/absolute SLA unapproved. [Decision Log §79](DECISION_LOG.md).

> **CURRENT VERIFIED MAIN STATUS (2026-11-20; SHA `bd8421cf3cabc5cb72263ed964434a48bf54ef22`):** [PR #24](https://github.com/majiddarvishan/neta-go/pull/24) (Phase D/QA), [#25](https://github.com/majiddarvishan/neta-go/pull/25) (readiness), [#26](https://github.com/majiddarvishan/neta-go/pull/26) (multi-peer Server) and [#27](https://github.com/majiddarvishan/neta-go/pull/27) (generic peer routing and Client OnRequest) are **ALL MERGED**. **Phase D 16/16 complete; 14 runnable examples** (2 original, 10 Phase D, 2 generic routers). Additive `WithClientOnRequestHandler` is merged for bidirectional Client Sessions with V1/V2 real TCP tests, nil handler compatibility, and rejection of non-nil handler for one-way Bind. Exact current main SHA required [Go CI 44630477642](https://github.com/majiddarvishan/neta-go/actions/runs/44630477642) and [C++ wire 44630477596](https://github.com/majiddarvishan/neta-go/actions/runs/44630477596) both **SUCCESS**. QA-007 **MERGED/CLOSED**; QA-004/005 and MEM-004/005/006 **OPEN/INCONCLUSIVE**; Performance Gate **DISABLED**, no numeric baseline or `v1.0.0` release authorization. [Normalized Phase-Q/Owner/Release backlog](NETA_GO_PHASE_Q_EXECUTION_BACKLOG_2026-11-20.md). Older dated sections below are historical, not current merge status.

> **OWNER-LOCAL QA-004 A/A (2026-11-18, exact SHA `ff38ceb29107fa156e0f87555f59bc6a5fa393d9`):** Received `aa-qa004-20261118T202222Z-2358305.tar.gz`: complete **10 alternating A/A pairs**, 5 synthetic Pending populations, 100 successful benchmark rows × 1200 internal terminal-settlement samples = **120,000 observations**; all **5/5 relative P99 metrics PASS** with run-level P99 CV 0.93–3.01%. Host i5-12400/Go 1.27, `powersave`, load increased 1.09 -> 1.70, pswpin +87 and pswpout +0. **A/A comparator status remains INCONCLUSIVE, baseline_approved=false, performance gate DISABLED** despite relative_status=PASS. Distinguish from QA-005's 1s A/A (P99 4/8 INCONCLUSIVE). QA-004/005 Task qualification remain OPEN, QA-007 CLOSED. This tool evidence does not approve a reference machine, absolute SLA or historical baseline. See docs/PERFORMANCE_QUALIFICATION.md.

> **SECOND OWNER-LOCAL A/A CORE PROBE (2026-11-18, 1s):** Owner uploaded `aa-core-20261118T152119Z-1872550.tar.gz` (SHA `193d9c2e58e021319a92b4abb37cce69d8074dc1`). A/A 10 pairs / 160 rows / 8 Core cases, matrix complete, env comparable, benchmark fixture digest identical to 250ms run. Non-retention measured metrics: **36 PASS / 12 INCONCLUSIVE / 0 FAIL**, vs prior **31/17/0**; eight retained-attributed-memory metrics uninstrumented INCONCLUSIVE. P99 still **4 PASS / 4 INCONCLUSIVE**; mean per-scenario P99 CV ~23.5% -> 11.8%, but RR 64KiB single Session CV remains 33.8%. Governor powersave, host load changed, pswpin +124, pswpout 0. **No approved reference baseline or performance gate**. Next non-invasive step: owner-local `bash scripts/qa005_noise_probe.sh qa004` with NO BENCHTIME override. QA-007 closed. Details in docs/PERFORMANCE_QUALIFICATION.md.

> **OWNER-LOCAL A/A CORE MEASUREMENT (2026-11-18):** 10 alternating pairs with identical exact SHA `a6c2b1373e01b716bf8bf8f89d71abe0708630fe` on the Linux i5-12400 / Go 1.27 workstation: all 160 output rows complete, 0 capacity rejections, post-workload resource counters zero, 31 PASS / 17 INCONCLUSIVE / 0 FAIL measured Core metrics **plus 8 uninstrumented retained-memory INCONCLUSIVE**. Several single-Session P99 measurements exhibited 38–50% sample CV, so **machine is not yet qualified as a stable reference**; `comparison.status=INCONCLUSIVE`, `baseline_approved=false`, gate remains DISABLED. Added an optional 1s per-benchmark A/A rerun (`NETA_QA005_BENCHTIME=1s bash scripts/qa005_noise_probe.sh core`), default remains 250ms, for owner-local execution; this new diagnostic has not been run yet. No production code touched, QA-007 stays closed. More detail in the final-validation report.

> **QA-004/QA-005 LOCAL REFERENCE PREPARATION (2026-11-18):** Added an isolated, single-command **A/A noise probe** on commit `63f80470b60be4c27475d3f681b2475d7c37b6db`: `bash scripts/qa005_noise_probe.sh core` on the owner's Linux workstation. It runs ten matched alternating pairs of **identical** exact-SHA worktrees, captures governor/load/memory/swap/pressure evidence, and emits one local .tar.gz. This is an **unexecuted probe tool awaiting owner-local run**; it has not qualified or approved a reference machine, historical baseline, retained-memory metric or absolute SLA. QA-004/005 remain OPEN and Performance Gate DISABLED; QA-007 stays CLOSED. No PR/merge/tag/release. See `docs/PERFORMANCE_QUALIFICATION.md`.

> **LOCAL QA-007 RETEST, 2026-11-18 (owner-supplied console output; code+test SHA `2db90faf67923ea796ed611629390197cffb0e43`):** After a flaky `TestQA007ForcedClosePreservesAllCompletionAndCredit` failure under coverage on the first local final validation, a **test-only** fix awaits the asynchronous Panic diagnostics record after Completion credit release (no production-code change). Owner subsequently executed `go test -race -count=100 -run '^TestQA007ForcedClosePreservesAllCompletionAndCredit$' .` (PASS), `go test -cover -count=100 -run '^TestQA007ForcedClosePreservesAllCompletionAndCredit$' .` (PASS; targeted-test-only coverage 25.0%) and `make smoke` (PASS; root coverage **82.7%**, wire **92.0%**, example loopback Request/Response, one-way event and graceful stop PASS). **QA-007 remains [x] CLOSED on feature branch; the reported local flaky test issue is resolved for these retests.** The earlier 30-minute soak and advisory QA-004/005 measurements were performed on the previous code+test SHA; production source is unchanged, so they are preserved as earlier evidence rather than claimed reruns. QA-004/005 reference qualification remains OPEN, Performance Gate DISABLED. No PR/merge/tag/release performed. This paragraph supersedes earlier local smoke-failure status.

> **LATEST VERIFIED QA EVIDENCE — 2026-11-18 (source SHA `99dd68848eb73dd15ccf0a178861aa7f7cf82fef`):** [GitHub Actions #44313332548](https://github.com/majiddarvishan/neta-go/actions/runs/44313332548) PASS in all three jobs: gofmt/vet/uncached Go unit+races/paired smoke, pinned C++ V1 golden, five QA-004 P99 benchmarks with **1,200 terminal-settlement observations each**, QA-005 8 Core plus 24 Full advisory workloads, and **16 Python comparator tests**. Exact workload-name verification now checks the Go fixture; malformed/duplicate/unreadable evidence is INCONCLUSIVE. Successful QA-005 workloads report accepted operations, offered producer count, zero capacity rejections, and post-run owner resource counters (all zero in 32 Core+Full output rows). These are **post-run snapshots, not attributable memory peaks or stable reference qualification**. QA-007 COMPLETE on this feature branch; QA-004 and QA-005 remain OPEN pending approved stable machine/baseline, 10 matched pairs, 30-minute soak, actual retention method and owner-approved absolute SLAs. Performance Gate DISABLED. No PR, merge, tag or release permitted.

> **LATEST VERIFIED QA QUALIFICATION UPDATE (2026-11-18):** On isolated feature branch, source HEAD `eaf022357e369b8d484376a3385b16f2ce4fafd6` passed [final Actions #44310174076](https://github.com/majiddarvishan/neta-go/actions/runs/44310174076): Go format/vet/unit/race/smoke, pinned C++ V1 golden, QA-004 detection with **1,200 samples for each of five Pending populations**, QA-005 8 Core and all **24 Full** advisory benchmarks, and 12 Python comparator tests. Linux process CPU/op is measured only in benchmark code. Paired QA-004 P99 and QA-005 qualification now reject mismatched baseline fixture SHA/matrix and report missing attribution honestly. **QA-007 remains complete; QA-004 and QA-005 remain OPEN** because an owner-approved stable machine/baseline, 10 matched pairs, 30-minute soak, attributable retention evidence and absolute SLA approval remain outstanding. Mandatory Performance Gate DISABLED. No PR, merge, tag or release authorized. This paragraph supersedes older partial-status descriptions below.

> **QA-004/005/007 implementation authorization — 2026-11-18:** Owner authorizes source, tests and single final validation only on `feature/qa004-qa005-qa007-implementation-2026-11-18` based on main `24b7c5f6eb4e001f30dd8a564a337ca1f506eac8`. Older docs-only restrictions are superseded for this scope. No PR, merge, release or tag is authorized. Implementation source and QA-007 verification passed on code SHA `e852392542c20daf5a79cba2aaee7fbd55e454f8`, Actions run [44306325369](https://github.com/majiddarvishan/neta-go/actions/runs/44306325369). QA-007 is complete; QA-004 and QA-005 remain open pending qualified reference evidence. Performance Gate stays DISABLED until stable reference hardware, immutable baseline and absolute SLA receive owner approval.

# neta-go — Canonical Implementation Task Tracker

**Repository:** `github.com/majiddarvishan/neta-go`  
**Branch:** `main`  
**Tracker owner:** Project owner  
**Last reconciled:** 2026-11-20 (protected `main` `bd8421cf3cabc5cb72263ed964434a48bf54ef22`); older HEADs below identify historical reviews  
**Original tracker baseline HEAD:** `c98f731fef89519d62d95248982538f25a36db82`  
**Last verified repository HEAD before P9-00:** `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5`  
**Last verified production source HEAD:** `209c24a7dbc5a5aa3db95ec63705915406acacb6`  
**Current phase:** Phase D authorized development COMPLETE (16/16), with generic peer-router examples and the additive Client OnRequest API merged. Phase Q software-only preparation is owner-authorized and in progress; heavy Reference-Host Qualification remains deferred pending separate execution authorization. P9-00..P9-06 are complete; official `v1.0.0` remains immutable.

This file is the **single canonical implementation task tracker** for `neta-go`. It lives in `.codex/TASKS.md`; the former repository-root `TASKS.md` was consolidated here on 2026-11-18. Update the checkboxes together with their acceptance evidence. Keep architecture decisions in `DECISION_LOG.md`; this file records implementation status and verification.

## Status legend

- `[x]` Implemented and accepted with evidence recorded below.
- `[ ]` Not complete. A task may be in progress only when its phase heading says so.
- A completed design decision does **not** mean its implementation task is complete.
- CI links refer to GitHub Actions runs for the exact source/documentation HEAD shown.

## Overall status

| Phase | Scope | Status | Authorization |
|---|---|---|---|
| 0 | Architecture and contract freeze | COMPLETE | Complete |
| 1 | Module and immutable configuration | COMPLETE / CI PASS | Complete |
| 2 | Pinex-compatible Wire Codec | COMPLETE / CI PASS | Complete |
| 3 | Session transport and lifecycle | COMPLETE / CI PASS | Complete |
| 4 | Resource admission and accounting | COMPLETE / CI PASS | Authorized 2026-11-17 |
| 5 | Bounded callback Worker Scheduler | COMPLETE / CI PASS | Owner approved 2026-11-17 |
| 6 | Client/Server orchestration and reconnect | COMPLETE / CI PASS | Owner approved 2026-11-17 |
| 7 | Live interoperability and fault-injection verification | COMPLETE / CI PASS | Owner authorized 2026-11-17 |
| 8 | Performance baseline and evidence-driven optimization | COMPLETE / CI PASS | Owner authorized 2026-11-17 |
| 9 | Documentation/examples complete; publication gated at P9-06 | IN PROGRESS (release only) | Release tag separately gated |

---

## Active work register — normalized and deduplicated (2026-11-20)

**Authority:** protected `main` `d376cd8a375328aa971cd4441d989920bf6009a0` (2026-11-22). Historical task checkboxes later in this file may describe earlier snapshots or repeat the same work. **Current normalized open packages = 17: Qualification 8 + Owner Decisions 7 + Release 2; Q-COR-01, Q-COR-04 and P9-06 are CLOSED.** Two owner-policy choices (OD-ENV-01 and OD-MEM-01) remain closed with Option A. Concrete host acceptance, sampling proof and heavy testing remain open. Each package below counts once. See the [Phase-Q execution backlog](NETA_GO_PHASE_Q_EXECUTION_BACKLOG_2026-11-20.md) for acceptance evidence, dependency order and reference-host needs.

### Development and examples — COMPLETE

- [x] **DEV-01..DEV-06 (6/6), EX-C01..EX-C05 (5/5), EX-S01..EX-S05 (5/5).** Authorized Phase D **16/16 DONE**, merged via PR #24; original 12-command bounded CI [44542311954](https://github.com/majiddarvishan/neta-go/actions/runs/44542311954) PASS.
- [x] **EX-G01 — `server-peer-router`:** generalized multi-bound-peer registry, exact-key fail-closed routing, JSON/CLI, bounded concurrency and no retry (PR #26 then #27).
- [x] **EX-G02 — `client-peer-router` and API-CLIENT-REQUEST — `WithClientOnRequestHandler`:** bidirectional Client inbound Requests, `Session.SendResponse`, nil/uni Bind behavior, panic Diagnostics and V1/V2 TCP tests; [PR #27](https://github.com/majiddarvishan/neta-go/pull/27) merged. Total **14 runnable example commands**, but the older 12-command smoke does not cover the 2 new routers.
- [x] **Current main required CI:** [Go 44630477642](https://github.com/majiddarvishan/neta-go/actions/runs/44630477642) and [C++ wire 44630477596](https://github.com/majiddarvishan/neta-go/actions/runs/44630477596) SUCCESS; PR #27 source tip [wire mutation 44630191298](https://github.com/majiddarvishan/neta-go/actions/runs/44630191298) SUCCESS. No claim of full Phase-Q acceptance.

### Qualification — 2 CLOSED, 8 OPEN (10 total)

- [ ] **Q-ENV-01 P0:** qualify stable reference hardware, reproducible A/A noise, approved runtime/CPU environment (requires reference machine).
  - [x] **QENV-AA-01 subdecision:** OWNER APPROVED **B** — fail-closed mode-scoped admission policy. **Not** machine admission; prospective symmetric equivalence/drift bounds and measured evidence still required ([Decision §80](DECISION_LOG.md)).
  - [x] **QENV-AA-02 policy/margin:** OWNER APPROVED **A** — fixed prospective 5%/7.5% simultaneous two-sided 95% log-equivalence margins, per mode, [Decision §81](DECISION_LOG.md).
  - [x] **QENV-AA-02.ORD policy:** OWNER OPTION **A** APPROVED; joint 5m family-wise two-sided 95% mean + four modeled order/time corner CI, all strictly inside the unchanged 5%/7.5% A/A budgets ([Decision §82](DECISION_LOG.md), [contract](NETA_GO_QENV_AA_ORDER_DRIFT_POLICY_2026-11-20.md)).
  - [ ] **QENV-AA-02.ORD-EVID readiness — IN PROGRESS, NOT QUALIFIED:** process-level telemetry collector ([PR #42](https://github.com/majiddarvishan/neta-go/pull/42)), joint 5m Bonferroni report-only model ([PR #43](https://github.com/majiddarvishan/neta-go/pull/43)), raw-byte-preserving line receipt observer ([PR #44](https://github.com/majiddarvishan/neta-go/pull/44)) and conservative pre-spawn receipt bound ([PR #45](https://github.com/majiddarvishan/neta-go/pull/45)) are integrated. PR #46 adds an exact (2^{10}) paired-case interval endpoint sensitivity sweep, reports time-slope/four-corner CI envelopes and adds synthetic buffered-stdout and fail-closed tests ([design/limits](NETA_GO_ORD_TIME_UNCERTAINTY_PREP_2026-11-21.md), [merged PR #46](https://github.com/majiddarvishan/neta-go/pull/46)). **Still OPEN:** endpoint sampling is not a continuous interval bound; actual Go buffering, pipe/scheduler uncertainty, observer overhead, nonlinear/model adequacy, complete dedicated-host E-VALID and separate authorization for real A/A Mode measurements remain unproven. Strict telemetry provenance/sensor validation is also hardened in [merged PR #48](https://github.com/majiddarvishan/neta-go/pull/48); a continuous case-time interval enclosure candidate is merged but not independently proved; observer backpressure is documented and overhead remains unmeasured; recorded cadence is now bound into raw snapshots and p50/p95/max gaps are reported; acceptance threshold and accuracy proof remain open; cadence evidence is report-only and unqualified; E-UNKNOWN and all reports remain DRIFT-INCONCLUSIVE; no benchmark campaign, new baseline/SLA, memory PASS or Performance Gate. Q-ENV-01 remains [ ] OPEN.
- [x] **Q-COR-01 P0 — CLOSED 2026-11-20:** immutable published v1.0.0 source `d8437f36ec812a596bada1398c7af9b530a18118` completed all 6 correctness stages ([PR #41 qualification run 44807019239](https://github.com/majiddarvishan/neta-go/actions/runs/44807019239)), including `make verify`, race, old+Phase-D smokes, 14 example builds and real 2-peer router routing/negative/stop test. After merge `74872c649b9f525f5fb8338f80322e5b1491285b`, required [Go](https://github.com/majiddarvishan/neta-go/actions/runs/44807267236) and [C++](https://github.com/majiddarvishan/neta-go/actions/runs/44807267191) checks both passed. Artifacts retained in GitHub Actions; no reference-host/performance/memory conclusion.
> **PHASE Q Q-COR-02 BOUNDED HARNESS MERGED ON MAIN (2026-11-22):** main `d376cd8a375328aa971cd4441d989920bf6009a0` includes the explicit three-generation reconnect/RST/OnClose/no-implicit-retry harness. Dedicated [Q-COR-02 harness CI #45014929050](https://github.com/majiddarvishan/neta-go/actions/runs/45014929050), required [Go #45014929048](https://github.com/majiddarvishan/neta-go/actions/runs/45014929048) and [C++ Wire #45014929039](https://github.com/majiddarvishan/neta-go/actions/runs/45014929039) all PASS. This closes harness preparation only; full stress/load/reconnect and resource teardown campaign remains OPEN.
- [ ] **Q-COR-02 P1:** full stress/load/reconnect campaign and resource teardown; bounded harness is preparation only (no reference machine strictly necessary).
- [ ] **Q-COR-03 P1:** extended fuzz and parser mutation (no reference machine). Seed replay + bounded fuzz harness implemented; [CI #45025904772](https://github.com/majiddarvishan/neta-go/actions/runs/45025704458) passed deterministic seeds and 7/7 fuzz targets at 1s/target, 2 workers (~368,043 executions). This is harness smoke only; extended fuzz campaign remains OPEN ([evidence](NETA_GO_QCOR03_SEED_FUZZ_HARNESS_EVIDENCE_2026-11-22.md)).
- [x] **Q-COR-04 P1 — CLOSED 2026-11-22:** both live TCP directions (Go Client→pinned C++ Server; pinned C++ Client→Go Server), explicit V1, pinned C++ golden fixture and deterministic fragmented/deadline/RST/EOF fault cases passed in normal and race runs ([Pinex CI #45026010703](https://github.com/majiddarvishan/pinex/actions/runs/45026010703), [evidence](NETA_GO_QCOR04_LIVE_INTEROP_EVIDENCE_2026-11-22.md)). GitHub artifact upload was unavailable because storage quota was exhausted; exact manifest/checksums were printed in the successful job log. No production source change.
- [ ] **QA-004 P0:** qualify Pending Deadline Scan and detection P99 against approved absolute SLA and reliable paired comparison.
- [ ] **QA-005 P0:** validate 8 Core/24 Full, ten matched pairs, 95% statistics, approved immutable numeric baseline and threshold limits.
- [ ] **MEM-004 P0:** close F1–F5/M1/D1 owned-byte/alias/lifetime/peak-validity evidence or remain INCONCLUSIVE; do not emit `retained-attributed-B` from partial diagnostics. V19 now fails closed for retired Client generations with active callback ownership, both at freeze and each sample; 22 Python tests plus generated Go race tests PASS ([CI #45025289359](https://github.com/majiddarvishan/neta-go/actions/runs/45025289359), [V19 evidence](NETA_GO_QA005_RETIRED_CALLBACK_GUARD_V19_EVIDENCE_2026-11-22.md)). Still OPEN: transient callback churn between samples, strong-reference/GC liveness bias, full ownership/alias coverage and accepted peak validity.
- [ ] **MEM-005 P0:** validate instrumentation observer overhead and sampling gaps/bias on accepted reference host. V19 adds synthetic monotonic timestamp, sample-gap and snapshot-duration integrity tests; no acceptance threshold is set, and actual observer overhead/GC bias remain NOT MEASURED. Remains OPEN ([V19 evidence](NETA_GO_QA005_RETIRED_CALLBACK_GUARD_V19_EVIDENCE_2026-11-22.md)).
- [ ] **MEM-006 P1:** qualify 30-minute long soak, memory stability and worker/Session teardown on accepted reference host.

### Owner Decisions — 2 CLOSED, 7 OPEN

- [x] **OD-ENV-01 P0 — OWNER OPTION A APPROVED (2026-11-20):** dedicated, controlled reference machine selected as policy. Actual hardware identity, Go toolchain/environment stability and A/A acceptance remain **OPEN under Q-ENV-01**. [Decision §79](DECISION_LOG.md).
- [x] **OD-MEM-01 P0 — OWNER OPTION A APPROVED (2026-11-20):** fail closed as **INCONCLUSIVE** until coverage, ownership/aliases, simultaneous peak, sampling gap and observer bias are proved. M1/D1 incremental Option B remains unchanged. **MEM-004/005 remain OPEN**; no canonical retained-attributed-B emitted. [Decision §79](DECISION_LOG.md).
- [ ] **OD-BASE-01 P0:** approve immutable numerical baseline and exact evidence/manifest, distinct from frozen Source-V1 SHA.
- [ ] **OD-SLA-01 P0:** approve absolute QA-004 P99 and relevant throughput/latency SLAs, with measured evidence.
- [ ] **OD-GATE-01 P2:** choose whether/when to activate mandatory Performance Gate; presently **DISABLED**.
- [ ] **OD-NOTES-01 P0:** approve latest Unreleased notes covering V2/default, V2 NUL-free/20-byte, Client OnRequest and peer routers; historical PV-01-R/02A-R/02B-R refer to this ONE approval.
- [ ] **OD-CHECK-01 P2:** optional rename of required C++ context through protected-main admin settings; old context kept unchanged meanwhile.
- [ ] **PV-02 P3 FUTURE:** owner-approved version-selection/negotiation mechanism, no automatic fallback.
- [ ] **PV-04/PV-05 P3 FUTURE:** capability/version extension design and authorization, not implicit V1 release blocker.

### Release — 2 OPEN, official publication P9-06 CLOSED (3 total)

- [ ] **R-01 P0:** exact-candidate-SHA release evidence and CI/Qualification gate review.
- [ ] **R-02 P0:** protected-main strict policy and publisher permission/tag-collision preflight by authorized admin.
- [x] **P9-06 P0 — official publication COMPLETE under explicit owner override:** immutable annotated `v1.0.0` tag verified at source `d8437f36ec812a596bada1398c7af9b530a18118`; non-prerelease GitHub Release and exact-SHA Go/C++ required checks all PASS ([verified GA evidence](GA_RELEASE_VERIFIED_2026-11-20.md)). **Not a Phase Q acceptance.** Separate R-01/R-02 remain `[ ]`; older duplicate historical P9-06 entries are not additional tasks.
- [x] **RC-01 COMPLETE (supplementary, NOT a 21st top-level task):** independent GitHub refs prove annotated `v1.0.0-rc.1` tag object `1e07c00f97b6243f932aba91c544f81b73e6fc9d` peels exactly to `0bd50760a9200194f9ae0088d26751d0f6ee00c7`, the release-preparation PR #37 squash-merge SHA. Required Go and pinned C++ Wire checks **SUCCESS on that exact SHA**, and tag publisher workflow **SUCCESS** ([Decision §84](DECISION_LOG.md)). Final GA R-01/R-02/P9-06 remain OPEN.

**Nonnegotiable boundary:** QA004-QA005 Source-V1 anchor `9b7b2318f73d173a99d22489042f84f8ce58b745` unchanged. No new baseline, production edit, heavy qualification, mandatory gate or tag/release approved.

---
## Phase 0 — Architecture and contract freeze

<badge>COMPLETE</badge>

- [x] Freeze the Pinex C++ 1.5.0 compatibility target and record source commit `f7bd1eb779baff0d10e624f20522df345e6ee747`.
- [x] Freeze the 10-byte Header, command/status/sequence layout and 1 MiB total Frame maximum.
- [x] Close API-001 public surface and root-package boundary.
- [x] Close API-002 timeout, reconnect and shutdown contracts.
- [x] Close API-003 module/package architecture.
- [x] Close API-004 Functional Options and immutable configuration semantics.
- [x] Close Q-008/Q-009/Q-010 queue and overload policies.
- [x] Close PERF-002 payload ownership and PERF-003 Request-credit model.
- [x] Close WORKER-001..009C ownership, worker topology, capacity defaults, limits and accounting policy.
- [x] Record final decisions and implementation boundaries in `DECISION_LOG.md`.

**Evidence:** `.codex/DECISION_LOG.md`, `.codex/NETA_GO_ARCHITECTURE_FREEZE_DECISION_REGISTER_2026-11-17.md`, and the linked design records.

## Phase 1 — Module and immutable configuration

<badge color="success">COMPLETE / CI PASS</badge>

- [x] Create `go.mod` with module path `github.com/majiddarvishan/neta-go` and root package `neta`.
- [x] Implement typed `ClientOption`, `ServerOption` and `SessionOption`.
- [x] Implement complete defaults and immutable effective Client/Server/Session configuration snapshots.
- [x] Apply all options before final validation; reject nil/invalid options deterministically.
- [x] Implement API-004 and WORKER-009C ranges, hard maxima, cross-field validation and checked arithmetic.
- [x] Add typed public error categories and Session state declarations.
- [x] Add configuration/default/range/precedence tests.
- [x] Pass formatting, vet, unit and race checks.

**Evidence:** Phase 1 implementation recorded in `IMPLEMENTATION_AUTHORIZATION_2026-11-17.md`; CI run [44040206052](https://github.com/majiddarvishan/neta-go/actions/runs/44040206052).

## Phase 2 — Pinex-compatible Wire Codec

<badge color="success">COMPLETE / CI PASS</badge>

- [x] Implement pure-Go `internal/wire` Header and Frame codec.
- [x] Implement Bind, Stream, Unbind and Enquire Link codecs with Pinex-compatible command/status/sequence semantics.
- [x] Enforce the 1 MiB total Frame maximum inbound and outbound, before Body allocation.
- [x] Add deterministic golden fixtures generated from the pinned production C++ serializer source snapshot.
- [x] Compile the C++ fixture generator and compare Go codec output against the golden fixtures in CI.
- [x] Match Pinex's omitted Bind Response Body default-value behavior.
- [x] Pass gofmt, vet, unit and race tests plus C++ golden compatibility workflow.

**Evidence:** `NETA_GO_PHASE_2_WIRE_IMPLEMENTATION_2026-11-17.md`; Go CI [44044273742](https://github.com/majiddarvishan/neta-go/actions/runs/44044273742), C++ golden CI [44044273818](https://github.com/majiddarvishan/neta-go/actions/runs/44044273818).

## Phase 3 — Session transport and lifecycle

<badge color="success">COMPLETE / CI PASS</badge>

- [x] Implement one Reader and one serialized Writer per Session.
- [x] Implement client Bind and server Pre-Bind Session-side handshake primitives and state transitions.
- [x] Implement absolute Bind/Pre-Bind, Frame Assembly and per-Frame Writer deadlines.
- [x] Implement idle-only Enquire Link, matching response tracking and incoming Enquire Link replies.
- [x] Implement per-Session nonzero Sequence allocation and Request correlation.
- [x] Implement Request timeout, late-response suppression and exactly-once internal settlement.
- [x] Implement bounded per-Session outgoing Application FIFO byte/frame admission and separate Control-PDU reserve.
- [x] Implement Graceful Unbind, Forced Close A, immutable terminal cause and Done after internal teardown.
- [x] Ensure no user callback runs inline in Reader or Writer; retain private dispatcher boundary for Phase 5.
- [x] Harden queued Enquire Link cancellation after outbound activity.
- [x] Ignore Responses that arrive before Writer claims their Request.
- [x] Preserve the first post-Bind Frame Assembly deadline across the server Bind transition.
- [x] Start RequestTimeout after successful local FIFO admission.
- [x] Add focused fragmentation, partial-write, timeout, correlation, close and race tests.
- [x] Pass gofmt, vet, unit and race CI.

**Evidence:** `NETA_GO_PHASE_3_SESSION_TRANSPORT_LIFECYCLE_2026-11-17.md`; source verification HEAD `cc0d25e9252b48f38dcddeeb53eaa6e7fe1cbf4c`; Go CI [44057820360](https://github.com/majiddarvishan/neta-go/actions/runs/44057820360), C++ golden compatibility CI [44057820405](https://github.com/majiddarvishan/neta-go/actions/runs/44057820405). The C++ workflow is golden-frame compatibility, **not** live TCP interoperability.

## Phase 4 — Resource Admission and Accounting

<badge color="success">COMPLETE / CI PASS</badge>

**Owner authorization:** 2026-11-17, this conversation. Scope is limited to the already-approved WORKER/Q-008/Q-009/Q-010/PERF-002/PERF-003 contracts. Do not change public API, defaults, wire behavior or frozen overload policies.

### Existing Phase 3 prerequisites

- [x] Per-Session outgoing Application FIFO byte and frame limits; the active Writer-owned frame remains charged until full Write or discard.
- [x] Separate bounded per-Session Control-PDU byte reserve.
- [x] Per-Session pending Request population is bounded and held through normal Completion callback return/cancellation.

### Implementation tasks

- [x] **P4-01 — Reservation primitives:** implement race-safe, checked reserve/release primitives for owner byte and count resources; reject overflow/underflow. Session lifecycle idempotency is verified in the integration tasks below.
- [x] **P4-02 — Owner ledgers:** implement independent Client/Server-owned counters for outstanding Request credits, retained Application bytes, retained Completion bytes and OnClose event credits. NewClient/NewServer each create one independent owner ledger; Phase 6 will inject the same Client ledger into every reconnect generation.
- [x] **P4-03 — Server aggregate queue ledger:** one combined incoming+outgoing Application queued-frame byte (256 MiB default) and frame-count (65,536 default) budget per Server.
- [x] **P4-04 — Outgoing Application admission:** per-Session queue/count, retained Application and owner/Server budgets reserved before Frame allocation/copy or Request publication; Queue Full and Capacity remain distinct; rejected work consumes no Sequence/Pending state.
- [x] **P4-05 — Incoming Application admission:** full declared Frame bytes/count and retained Application capacity reserved after Header validation but before Body allocation; offender-only close on overload; partial-read/cancel/return release paths covered.
- [x] **P4-06 — Completion admission:** matched Response retained bytes reserved before Body allocation; capacity exhaustion uses fixed 4 KiB scratch drain under the original absolute Frame Assembly deadline, then no-payload `ErrCapacity` Completion if the Request still wins.
- [x] **P4-07 — Request credits:** per-Session and owner Request ceilings; credits held through response wait and Completion callback, released once on return/cancel/terminal cleanup.
- [x] **P4-08 — OnClose event credits:** one nonblocking owner reservation after Done; permanent skip at capacity; release after callback return/cancellation.
- [x] **P4-09 — Lifecycle transfer/release:** queue-only charges release at callback start; retained payloads follow callback ownership after Done; Writer completion, partial I/O, timeout, Forced Close A and callback cancellation release paths tested.
- [x] **P4-10 — Admission verification:** exact/over boundaries, concurrent owner admission, multi-Session aggregate limits, scratch-drain success/timeout, partial reads, cancellation and callback-retention tests.
- [x] **P4-11 — CI acceptance:** gofmt, go vet ./..., go test ./... and go test -race ./... all PASS on Phase 4 source HEAD.

**Phase 4 exclusions:** no Client Dial/Server Listen or reconnect orchestration (Phase 6), no live Pinex TCP interoperability campaign (Phase 7), no benchmark/pooling work (Phase 8), and no release/deployment (Phase 9). Phase 5 is separately authorized below.

## Phase 5 — Bounded callback Worker Scheduler

<badge color="success">COMPLETE / CI PASS</badge>

- [x] **P5-01 — Three isolated pools:** each Client/Server owner now creates separate lazy Application, Completion and OnClose pools with independent queue, lock, ready list and wake-up state.
- [x] **P5-02 — Active permits:** owner/class worker ceilings and per-Session concurrency intersections are enforced; the same owner dispatcher is reusable by every Client generation and every Server Session.
- [x] **P5-03 — Fair scheduling:** one reusable ready-Session node per class; FIFO per-Session tasks and round-robin one-callback-per-eligible-Session turns.
- [x] **P5-04 — Idle retirement:** per-class configurable grace, 30s default, reusable worker timer, zero warm-idle floor, worker reuse before expiry and no retirement of running callbacks.
- [x] **P5-05 — Forced Close A:** callback start is linearized with Forced Close by Session.dispatchMu; queued Application/Completion work is cancelled once, while started callbacks retain permits and payload/Request charges through return.
- [x] **P5-06 — OnClose policy:** queued only after Done, best-effort/at-most-once, existing owner event credit covers queued + running callbacks, and saturation permanently skips the event.
- [x] **P5-07 — Isolation/liveness tests:** blocked Application does not consume Completion/OnClose workers; blocked OnClose does not consume Application/Completion workers; real Session Reader/Writer and Done progress while callbacks block; no goroutine-per-event.
- [x] **P5-08 — Race and churn tests:** concurrent enqueue/retirement and enqueue/Forced Close tests, retired-generation permit retention, queued+running OnClose credit saturation, fairness tests and Go race detector pass.
- [x] **P5-09 — CI acceptance:** gofmt, go vet ./..., go test ./... and go test -race ./... pass; Pinex C++ 1.5.0 golden compatibility workflow passes.

### Phase 5 completion evidence — 2026-11-17

- Implementation report: [.codex/NETA_GO_PHASE_5_WORKER_SCHEDULER_IMPLEMENTATION_2026-11-17.md](NETA_GO_PHASE_5_WORKER_SCHEDULER_IMPLEMENTATION_2026-11-17.md).
- Source verification HEAD: `c72136693f85e61239bfca42bd04b40e66eddc27`.
- 16 Worker Scheduler tests; existing 46 Session tests and 8 owner-ledger tests remain green.
- Go CI [44066876353](https://github.com/majiddarvishan/neta-go/actions/runs/44066876353) PASS; Pinex Wire Compatibility [44066876291](https://github.com/majiddarvishan/neta-go/actions/runs/44066876291) PASS.
- Phase 6 was authorized on 2026-11-17; implementation is in progress. See the Phase 6 plan and authorization addendum.

## Phase 6 — Client and Server orchestration

<badge color="success">COMPLETE / CI PASS — 2026-11-17</badge>

**Authorization:** Owner replied «ادامه بده» after the explicit Phase 6 authorization question. Scope is limited to P6-01..P6-11. Phase 7+ remain gated.

**Client Bind input decision CLOSED:** Owner approved Option B. WithClientSystemID(string) is mandatory; WithClientBindType(BindType) is optional with bi-directional default and uni-directional support. Client.Connect(ctx) signature remains unchanged. See DECISION_LOG.md §56.

- [x] **P6-01 — Client Connect:** Dial with absolute ConnectTimeout, Bind with absolute BindResponseTimeout and Context cancellation semantics.
- [x] **P6-02 — Client lifecycle:** CurrentSession exposes only the active Bound generation; terminal/idempotent Stop cancels Dial/Bind/reconnect, gracefully Unbinds or forces the current Session, and waits for internal Done; generation publication and stale-generation fencing are implemented.
- [x] **P6-03 — Reconnect supervisor:** opt-in AutoReconnect=false by default; approved bounded exponential Full Jitter policy; no Request replay/resend; share owner resource/worker ledgers across generations.
- [x] **P6-04 — Server listener:** Start/Addr/Accept lifecycle and listener-close ordering.
- [x] **P6-05 — Pre-Bind admission:** enforce pending socket count before Session allocation, absolute accept-to-Bind deadline and early refusal.
- [x] **P6-06 — Bound Session registry:** enforce MaxBoundSessions without eviction, reject excess Bind with Pinex rfail where feasible.
- [x] **P6-07 — Identity admission:** BindValidator and duplicate System ID rejection with atomic registry insertion/removal.
- [x] **P6-08 — Server Stop:** terminal/idempotent Stop; close listener and Pre-Bind Sessions, concurrently Graceful-Unbind Bound Sessions, force remaining Sessions on caller Context expiry.
- [x] **P6-09 — Owner integration:** Server Sessions share the Server resource ledger and worker owner; every Client generation reuses the Client resource ledger and callback dispatcher.
- [x] **P6-10 — Lifecycle tests:** Server lifecycle/admission, Client Stop/CurrentSession, Connect/Bind, timeout/rejection, reconnect generation replacement and uni-directional requester-only tests are implemented.
- [x] **P6-11 — CI acceptance:** gofmt, go vet ./..., go test ./..., go test -race ./... and pinned Pinex C++ 1.5.0 Golden Compatibility all PASS at source HEAD f8ce7669d2bbde33d3134d300e3256ae290dc529.

### Phase 6 Server implementation evidence — 2026-11-17

- Report: [Phase 6 Server implementation report](NETA_GO_PHASE_6_SERVER_IMPLEMENTATION_2026-11-17.md).
- Source verification HEAD: `8eead509c6817722d6b7c6f5e5a17e1734749911`.
- P6-04 through P6-08 complete; P6-02 is partially complete (Client CurrentSession/Stop); P6-09 and P6-10 are partially complete across Server and Client lifecycle slices.
- 11 focused Server lifecycle/admission tests.
- Go CI [44070940615](https://github.com/majiddarvishan/neta-go/actions/runs/44070940615) PASS; Pinex Wire Compatibility [44070940706](https://github.com/majiddarvishan/neta-go/actions/runs/44070940706) PASS.
- At this historical checkpoint, Client Connect/Bind remained blocked by the missing Bind identity input. The owner later approved Option B; Client Connect/Bind and reconnect are now complete. See the Client implementation evidence below.

## Phase 7 — Live interoperability and fault-injection verification

<badge color="success">COMPLETE / CI PASS — 2026-11-17</badge>

**Authorization:** The owner explicitly approved Phase 7 by replying «آره» in this conversation. P7-01..P7-08 are complete. Phase 8 performance optimization and Phase 9 release/deployment remain outside the authorization.

- [x] **P7-01 — Re-pin Pinex:** rechecked majiddarvishan/pinex develop; version remains 1.5.0, exact HEAD f7bd1eb779baff0d10e624f20522df345e6ee747, identical to the frozen compatibility Snapshot. No Wire/API/default change was required.
- [x] **P7-02 — Bidirectional TCP interoperability:** real loopback TCP passed in both directions: Go Client ↔ actual Pinex C++ Server and actual Pinex C++ Client ↔ Go Server. Both directions verified Bind identity, Request/Response payload, Sequence correlation and graceful Unbind.
- [x] **P7-03 — Wire fuzzing:** all five Header/Frame/Bind/Stream fuzz targets passed bounded 10-second campaigns. Aggregate: 1,810,074 executions, no crash or failing input.
- [x] **P7-04 — Transport faults:** passed fragmented reads/writes, slow-trickle absolute Bind Response timeout, silent accepted-socket blackhole, graceful EOF, abrupt RST, reordered Responses, Bind rejection and timeout/cancellation races. Firewall-level SYN-drop/network-namespace injection was not run; the application-stage silent Bind blackhole was exercised without privileged host-network changes.
- [x] **P7-05 — Admission faults:** queue/byte/count/Request/retained-memory limits, scratch-drain timeout, offender-only close, partial-read release and owner-ledger accounting passed under race CI.
- [x] **P7-06 — Callback faults:** blocked callback isolation, Forced Close cancellation/start races, OnClose saturation, fairness and retired-generation permit retention passed under race CI.
- [x] **P7-07 — Long-running soak:** 30-second reconnect soak with three Clients passed; Bound generation churn stayed within configured worker ceilings and owner Request/retained-byte/event credits returned to zero after Stop.
- [x] **P7-08 — Compatibility acceptance:** all pinned golden vectors and both real-socket Go↔Pinex directions passed. Final Go race, fault, soak and fuzz campaign passed.

### Final Phase 7 implementation and verification evidence — 2026-11-17

- Final verified neta-go source HEAD: 209c24a7dbc5a5aa3db95ec63705915406acacb6.
- Dedicated Pinex live interoperability workflow [44081220680](https://github.com/majiddarvishan/pinex/actions/runs/44081220680): PASS. It verified Pinex develop SHA f7bd1eb779baff0d10e624f20522df345e6ee747, built the real C++ peer, checked out the exact neta-go HEAD above, and passed both real TCP directions, go vet, go test -race, the 30-second reconnect soak and all five fuzz campaigns.
- Fuzz campaign totals from the workflow logs: 365,447 + 359,928 + 363,418 + 361,403 + 359,878 = 1,810,074 executions across five targets, each for 10 seconds with two workers.
- Go CI [44081197715](https://github.com/majiddarvishan/neta-go/actions/runs/44081197715): PASS — gofmt, go vet ./..., go test ./..., go test -race ./....
- Pinex Golden Compatibility [44081197688](https://github.com/majiddarvishan/neta-go/actions/runs/44081197688): PASS.
- Implementation report: [.codex/NETA_GO_PHASE_7_IMPLEMENTATION_2026-11-17.md](NETA_GO_PHASE_7_IMPLEMENTATION_2026-11-17.md).
- The dedicated interoperability workflow lives on Pinex test-only branch test/neta-go-phase7-interop. Pinex develop and its production source were not modified.
- No public API, wire format, timeout/reconnect policy, resource ceiling or frozen architecture decision was changed.

## Phase 8 — Performance baseline and evidence-driven optimization

<badge color="success">COMPLETE — 2026-11-17</badge>

**Authorization:** The owner approved the complete Phase 8 scope by replying «ادامه بده» after the explicit Phase 8 approval question. P8-01..P8-05 are authorized. Phase 9 examples, documentation polish, release readiness and deployment remain outside scope.

**Guardrails:** measure before optimizing. No public API, Wire Protocol, default, timeout/reconnect policy, resource ceiling, callback-ordering contract or frozen architecture decision may be changed in this phase. PERF-004 pooling/batching remains a measured engineering choice, not an assumed optimization. Do not create numeric performance SLAs before the reproducible baseline and owner workload review.

- [x] **P8-01 — Reproducible baseline:** full loopback TCP benchmark matrix PASS; Go 1.23.12, Ubuntu 24.04/Linux amd64, Intel Xeon 6975P-C, 4 vCPU, exact source SHA and artifacts recorded. See Phase 8 report §14.
- [x] **P8-02 — Record metrics:** throughput, p50/p95/p99, submission latency, allocations, bytes/op, CPU profiles, heap/GC, goroutines, worker snapshots, RSS, mutex and block profiles captured. Race runs remained separate.
- [x] **P8-03 — Profile hot paths:** small- and large-payload CPU/heap/mutex/block profiles captured and reviewed. Allocation hotspots and expected ownership costs documented.
- [x] **P8-04 — PERF-004 decision: NO CHANGE.** Outbound frame reuse is a potential allocation candidate but no safe material throughput/tail-latency win was proven. A generic `sync.Pool` lacks the hard retained-memory bound; per-Session pooling adds retained memory and complex writer/close/admission recycling. PERF-002 A inbound ownership remains unchanged; no inbound pooling.
- [x] **P8-05 — Regression/verification gate:** shared correctness and Pinex compatibility CI PASS; corrected full benchmark/profile workflow PASS and artifacts archived. No production optimization was accepted, so no before/after optimization comparison was applicable. Numeric performance regression thresholds remain intentionally unset pending owner workload/SLA review.

### Phase 8 repeatable automation — 2026-11-17

- [x] Add a shared Makefile entry point for correctness and Phase 8 workloads.
- [x] Add child-process scripts with uncached correctness tests, metadata, per-run logs and explicit PASS/FAIL status.
- [x] Make GitHub Actions invoke the same scripts used locally.
- [x] Store generated logs/profiles under ignored `artifacts/` and upload them from CI.
- [x] Validate the complete Phase 8 performance workflow and inspect its benchmark/profile artifacts — corrected run [44105272003](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003), artifact [14338552627](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003/artifacts/14338552627).
- [x] Provide the owner a short local invocation and confirm local execution on their machine — local `make verify` PASS on 2026-11-17.

### Phase 8 baseline implementation plan — 2026-11-17

- Existing approved performance contract and workload matrix are in .codex/NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md; PERF-002 A and all resource/worker limits remain binding.
- Initial benchmark code and CI workflow are being added as test-only infrastructure. No production code is changed for baseline collection.
- The first baseline is loopback Go↔Go and pure-Go wire codec. The Phase 7 actual Pinex C++ peer is retained as the cross-language correctness gate; any direct performance comparison to C++ must use a separately matched benchmark harness and disclose language/runtime differences.
- The initial runner baseline is an Ubuntu 24.04 GitHub-hosted runner. Results are environment-specific and are not production hardware guarantees.
- Detailed measurements, profile analysis, benchmark commands, artifact links and decisions will be appended to .codex/NETA_GO_PHASE_8_PERFORMANCE_BASELINE_2026-11-17.md.

### Phase 8 completion evidence — 2026-11-17

- Corrected full Phase 8 workflow [44105272003](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003): PASS; artifact [14338552627](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003/artifacts/14338552627); benchmark harness SHA `c5ebca4d3d0b7f1d36270501add0b059525df2c2`.
- Final pre-Phase-9 repository HEAD `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5`: Go correctness [44108072039](https://github.com/majiddarvishan/neta-go/actions/runs/44108072039) PASS; Pinex Wire Compatibility [44108072167](https://github.com/majiddarvishan/neta-go/actions/runs/44108072167) PASS.
- Owner's local `make verify` passed on HEAD `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5` on 2026-11-17: PASS (gofmt, vet, uncached unit and race). The prior local stash remains preserved as `stash@{0}`; it has not been applied or dropped.
- Five-minute soak: PASS; baseline/final heap 335,696/308,088 bytes; max HeapInuse 4,374,528 bytes; max RSS 91,348 KiB; 4,549 GC cycles; two goroutines after cleanup; retained/queued Application bytes stayed zero.
- 512-Session Request/Response: 64 B at 123,864 ops/s (p95 6.57 ms, p99 9.58 ms, fairness ratio 1.352); 256 B at 116,244 ops/s (p95 8.84 ms, p99 11.97 ms, fairness ratio 1.319).
- SendNoWait delivery correlation is now per TCP peer and per-Session sequence; concurrent routing integration test [delivery_test.go](../delivery_test.go) passes ordinary and race CI.
- PERF-004 closed as **NO CHANGE**. No production code, public API, Pinex wire protocol, defaults, timeouts, worker ceilings or resource limits changed.
- Phase 9 was subsequently authorized by the owner on 2026-11-17; P9-00..P9-05 are in scope. P9-06 remains gated on separate explicit release approval. Numeric performance regression thresholds are not set; the workflow archives weekly evidence, not hard SLA enforcement.

## Phase 9 — Documentation, examples and V1 release readiness

**Status: IN PROGRESS — OWNER AUTHORIZED 2026-11-17.**

**Authorization boundary:** P9-00 through P9-05 are authorized. P9-06 may create a V1 release tag only after all release gates pass and the owner gives separate explicit release approval. This Phase 9 authorization does not reopen the frozen production API, wire protocol, configuration defaults, timeout/reconnect policy, worker topology, resource ceilings or payload-ownership contracts.

- [x] **P9-00 — Documentation and tracker reconciliation:** correct Phase 8/HEAD status; synchronize README, HANDOFF and authorization records; refine Phase 9 acceptance criteria/dependencies; record the owner authorization and release-tag boundary. No production source changed.
- [x] **P9-01 — Client example:** added `examples/client/main.go` covering configuration, Connect/Bind, SendRequest/Completion, SendNoWait, error handling and graceful Stop. Uses only the frozen public API; compiled and passed Go correctness CI.
- [x] **P9-02 — Server example:** added `examples/server/main.go` covering Start/Addr, BindValidator, OnRequest/SendResponse, OnClose and graceful Stop. Uses only the frozen public API; compiled and passed Go correctness CI.
- [x] **P9-03 — Public API and usage documentation:** completed GoDoc for exported declarations and all 56 `With...` constructors; added API, Configuration and Lifecycle guides; expanded README with prerequisites, development installation, Quick Start and documentation links.
  - [x] Audit GoDoc for every exported type, constant, function, method and Functional Option; all exported declarations are documented.
  - [x] Document configuration defaults, valid ranges, hard maxima, zero-value semantics, inheritance and independent Client/Server/Session resource budgets.
  - [x] Document payload ownership, callback lanes/concurrency/order, admission errors, Request completion semantics, errors.Is/errors.As, timeouts, reconnect and shutdown/Done semantics.
  - [x] Expand README with prerequisites, installation, Quick Start, links to the examples and documentation index.
- [x] **P9-04 — Historical wire interoperability documentation:** initial engineering verification was recorded in a dedicated compatibility guide. That public-facing guide was retired by the 2026-11-18 cleanup; current neta-go framing/version documentation is `docs/PROTOCOL.md`, while historical provenance remains in `.codex/`.
- [x] **P9-05 — Test, CI and release-readiness review (COMPLETE; documented publication-time checks remain in P9-06):**
  - [x] Add `make smoke` and a CI gate after `make verify`; preserve coverage and example-smoke logs as artifacts.
  - [x] Build both examples and run paired Client/Server loopback smoke: Request/Response, SendNoWait event delivery and graceful Client/Server Stop all PASS.
  - [x] Record `go test -count=1 -cover ./...`: root `neta` 79.7%; `internal/wire` 90.3%; example main packages 0.0% because they have no package-local unit tests. No minimum coverage threshold is approved.
  - [x] Run the complete Go correctness gate and Pinex compatibility gate on the P9-05 CI commit.
  - [x] Record toolchain/platform evidence and publish the owner-approved V1 support statement.
  - [x] Add an Unreleased `CHANGELOG.md` and release-readiness checklist; current changelog entries OWNER APPROVED on 2026-11-17 as proposed V1 release notes, pending separate release permission.
  - [x] Review dependency footprint: no third-party Go modules are declared and no `go.sum` is present.
  - [x] Owner confirms Go 1.23 minimum and Linux/amd64 (Ubuntu 24.04) CI-tested platform; approved 2026-11-17; other platforms remain unverified.
  - [x] Owner approved copyright holder **Majid Darvishan** and year **2026**, confirmed commercial use is permitted, and the Apache-2.0 `LICENSE` notice was updated on 2026-11-17.
  - [x] Owner approved protecting `main` with two mandatory GitHub Actions checks on 2026-11-17: `test` and `Verify Go wire codec against pinned Pinex C++ 1.5.0`. Verified their exact names, success and `pull_request` triggers; see `.codex/NETA_GO_MAIN_BRANCH_PROTECTION_APPLICATION_2026-11-17.md`.
  - [x] Owner applied `main` protection in GitHub UI on 2026-11-17. Verified by GitHub branch API: `protected=true`, `required_status_checks.enforcement_level=everyone`, and **exactly both** required contexts `test` and `Verify Go wire codec against pinned Pinex C++ 1.5.0`. Both checks PASS on commit `b992beac7495934ce43111bd3a692ec272c8195d`.
  - [x] Verify protected-branch Pull Request enforcement in a real end-to-end PR: [#2](https://github.com/majiddarvishan/neta-go/pull/2) was `blocked` while its required Go/Pinex checks were pending, became `clean` after both checks PASS, and was then successfully squash-merged to `main` (`b5839a42b0de99f1ce9abf278e1fba3ff66d6617`). Latest post-merge Go [44165799994](https://github.com/majiddarvishan/neta-go/actions/runs/44165799994) and Pinex [44165800103](https://github.com/majiddarvishan/neta-go/actions/runs/44165800103) CI PASS on the same HEAD.
  - [x] Complete documented review of restricted admin settings and release publication capability **without claiming independent verification**: owner reported completing UI protection steps; GitHub reports `protected=true` with `enforcement_level=everyone` and both required contexts, confirmed by real PR #2; strict-up-to-date / specific bypass toggle is **NOT independently readable** (403). Repo is public with admin permission reported; releases/tags are absent and release listing works. Actual release publishing ability remains **NOT RUN** and moves to mandatory P9-06 preflight (no publication authorized).
  - [x] Owner APPROVED current `CHANGELOG.md` (Unreleased draft) and semantic version **`v1.0.0`** for the intended initial release on 2026-11-17. This approval is **not** authorization to create a tag or GitHub Release.
- [ ] **P9-06 — V1 release tag:** still NOT AUTHORIZED. Before any tag/release: obtain explicit fresh owner permission; verify release-creator access and the strict-up-to-date/admin-bypass controls in GitHub settings or via authorized admin; recheck exact current `main` SHA and both passing required checks; create `v1.0.0` tag/release only on that approved SHA and finalize release notes. Never infer release authorization from P9-05 closure.

### Phase 9 completion evidence and authorization

- Owner authorization: the owner replied «ادامه بده» on 2026-11-17 after reviewing and approving the Phase 9 execution plan.
- P9-00 baseline HEAD: `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5`; the production source remains at `209c24a7dbc5a5aa3db95ec63705915406acacb6`.
- Final pre-Phase-9 Go CI [44108072039](https://github.com/majiddarvishan/neta-go/actions/runs/44108072039) and Pinex Wire Compatibility [44108072167](https://github.com/majiddarvishan/neta-go/actions/runs/44108072167) both PASS on the baseline HEAD.
- P9-00 changes only project documentation/tracking/authorization records; no production source, tests, API, protocol or defaults are changed.
- P9-00 documentation commits: [dcb67647cd5748b6a92b54743b257c667d582450](https://github.com/majiddarvishan/neta-go/commit/dcb67647cd5748b6a92b54743b257c667d582450), [c6ac25338851edda1630dd6301a8eaf509f994c0](https://github.com/majiddarvishan/neta-go/commit/c6ac25338851edda1630dd6301a8eaf509f994c0), and final link/evidence correction [a43b0e5ca9b50f592ae402d18968b538af5bc128](https://github.com/majiddarvishan/neta-go/commit/a43b0e5ca9b50f592ae402d18968b538af5bc128).
- Final P9-00 Go CI [44114430747](https://github.com/majiddarvishan/neta-go/actions/runs/44114430747): PASS (`make verify`); Pinex Wire Compatibility [44114430634](https://github.com/majiddarvishan/neta-go/actions/runs/44114430634): PASS, both on HEAD `c6ac25338851edda1630dd6301a8eaf509f994c0`.
- Internal Markdown link audit found and corrected one pre-existing broken Phase 4 report link in root `TASKS.md`; all audited relative links now resolve.
- Final P9-00 Go CI [44114744808](https://github.com/majiddarvishan/neta-go/actions/runs/44114744808): PASS; Pinex Wire Compatibility [44114744875](https://github.com/majiddarvishan/neta-go/actions/runs/44114744875): PASS on HEAD `a43b0e5ca9b50f592ae402d18968b538af5bc128`.
- P9-01/P9-02 example commit: [04d905f75786542c9b51f48a33228b9bd372b419](https://github.com/majiddarvishan/neta-go/commit/04d905f75786542c9b51f48a33228b9bd372b419).
- Go correctness CI [44115049164](https://github.com/majiddarvishan/neta-go/actions/runs/44115049164): PASS (`make verify`: formatting, vet, unit and race); `go test ./...` compiles both example packages. Pinex Wire Compatibility [44115049277](https://github.com/majiddarvishan/neta-go/actions/runs/44115049277): PASS.
- P9-03/P9-04 documentation and GoDoc commits: [119be0adc61d1306c595f7aca6d7dc551c445fce](https://github.com/majiddarvishan/neta-go/commit/119be0adc61d1306c595f7aca6d7dc551c445fce), [631382c97f0702ea822203532f73567eeb594611](https://github.com/majiddarvishan/neta-go/commit/631382c97f0702ea822203532f73567eeb594611), formatting correction [a9ac0f6b530e2246fc73914d9db4ffcf3664db04](https://github.com/majiddarvishan/neta-go/commit/a9ac0f6b530e2246fc73914d9db4ffcf3664db04), and final helper restoration [3adca4f49e8565010344411dfdb0d83976218688](https://github.com/majiddarvishan/neta-go/commit/3adca4f49e8565010344411dfdb0d83976218688).
- Go correctness CI [44116677209](https://github.com/majiddarvishan/neta-go/actions/runs/44116677209): PASS (`make verify`: gofmt, go vet, unit tests and race tests) on final P9-03/P9-04 HEAD `3adca4f49e8565010344411dfdb0d83976218688`.
- Pinex Wire Compatibility CI [44116675706](https://github.com/majiddarvishan/neta-go/actions/runs/44116675706): PASS on the same HEAD.
- GoDoc audit: all exported top-level declarations in the root production package have comments; all 56 exported `With...` constructors are documented. Internal Markdown link audit: PASS.
- P9-03/04 changed documentation and comments only. The private `newConfigError` helper was restored unchanged; no production behavior/API/protocol/default/resource policy changed.
- P9-05 implementation commit: [c038fa60ffafd1f895e133db6d8cca08e7a2cc49](https://github.com/majiddarvishan/neta-go/commit/c038fa60ffafd1f895e133db6d8cca08e7a2cc49); shell expansion fix: [6d2521a22a476ee24f90dee364249e137357b756](https://github.com/majiddarvishan/neta-go/commit/6d2521a22a476ee24f90dee364249e137357b756); test-only deferred-credit assertion fix: [958601ee55dd6229021e36135a017527dfa8f778](https://github.com/majiddarvishan/neta-go/commit/958601ee55dd6229021e36135a017527dfa8f778).
- Final P9-05 Go CI [44119107169](https://github.com/majiddarvishan/neta-go/actions/runs/44119107169): PASS on HEAD `958601ee55dd6229021e36135a017527dfa8f778`; includes `make verify` and `make smoke`. Pinex Wire Compatibility [44119107078](https://github.com/majiddarvishan/neta-go/actions/runs/44119107078): PASS.
- Coverage: root `neta` 79.7%; `internal/wire` 90.3%; example main packages 0.0% (no package-local tests). These are visibility metrics only; no coverage threshold is approved.
- Runtime smoke: ephemeral loopback TCP, Client Request/Response, SendNoWait event observed by Server, and graceful Client/Server shutdown all PASS. Both example binaries built successfully.
- Final Phase 9 evidence artifact: [14344846005](https://github.com/majiddarvishan/neta-go/actions/runs/44119107169/artifacts/14344846005).
- The first smoke attempt [44118086700](https://github.com/majiddarvishan/neta-go/actions/runs/44118086700) exposed a shell-parameter expansion escape; the script was corrected in `6d2521a` and the final run passed.
- A Phase 8 Performance workflow [44118086752](https://github.com/majiddarvishan/neta-go/actions/runs/44118086752) was automatically triggered because the Phase 9 commit changed `Makefile`, which is in its path filter. It is an extra verification run; Phase 8 remains COMPLETE and no P8 task was reopened.
- Owner approved the V1 support baseline on 2026-11-17: Go 1.23 minimum and Ubuntu 24.04/Linux amd64 as CI-tested. Local Go 1.27.0 verification is additional evidence; other platforms are unverified. This closes only the support approval subtask.
- Copyright/licensing decision CLOSED on 2026-11-17: owner specified `Majid Darvishan`, `2026` and explicitly permits commercial use. Existing Apache-2.0 license retained (including its conditions); copyright notice filled in. No extra non-commercial restriction or alternative license introduced.
- Changelog/version review CLOSED on 2026-11-17: the owner approved the existing Unreleased changelog content and the intended semantic version `v1.0.0` for V1. The changelog remains Unreleased until a separately authorized publication.
- Repository metadata check: `main` reports `protected=false` and the repository ruleset list is empty; classic branch-protection details are not readable through the integration (HTTP 403). Tags: 0; GitHub Releases: 0. This is a visible release-readiness risk, not evidence of enforced branch protection. GitHub Release settings still require owner/admin verification.
- 2026-11-17: owner approved protecting `main` and requiring the exact Go `test` and Pinex `Verify Go wire codec against pinned Pinex C++ 1.5.0` status checks. GitHub verified that both jobs pass on `b3fad24938dd689cd270b6954a3a98e37f630614`, and both workflows trigger on pull requests. No protection-write action is offered by the GitHub integration; an admin application/verification guide was committed to `.codex/NETA_GO_MAIN_BRANCH_PROTECTION_APPLICATION_2026-11-17.md`.
- Branch protection now **ACTIVE / REQUIRED CHECKS VERIFIED** on 2026-11-17: after the owner's GitHub UI changes, `main.protected=true` and `required_status_checks.enforcement_level=everyone` with exactly `test` and `Verify Go wire codec against pinned Pinex C++ 1.5.0`. On HEAD `b992beac7495934ce43111bd3a692ec272c8195d` both Go [44163815612](https://github.com/majiddarvishan/neta-go/actions/runs/44163815612) and Pinex [44163815661](https://github.com/majiddarvishan/neta-go/actions/runs/44163815661) CI PASS. Classic protection-detail endpoint remains HTTP 403; strict-up-to-date/admin-bypass flags remain independently unverified.
- End-to-end protected PR workflow is independently VERIFIED: [PR #2](https://github.com/majiddarvishan/neta-go/pull/2) was initially blocked pending two mandatory check runs, became mergeable after both succeeded, and was squash-merged as [b5839a42](https://github.com/majiddarvishan/neta-go/commit/b5839a42b0de99f1ce9abf278e1fba3ff66d6617). Both post-merge Go [44165799994](https://github.com/majiddarvishan/neta-go/actions/runs/44165799994) and Pinex [44165800103](https://github.com/majiddarvishan/neta-go/actions/runs/44165800103) CI PASS on that SHA.
- P9-05 qualified engineering readiness review COMPLETE: latest verified post-merge `main` HEAD `cbd07421fec639a2d0db0bec7de03484bbcdb831` has Go [44167295340](https://github.com/majiddarvishan/neta-go/actions/runs/44167295340) and Pinex [44167295551](https://github.com/majiddarvishan/neta-go/actions/runs/44167295551) **PASS**. User approved support, license, version/changelog and reported finishing branch UI setup; actual protected PR enforcement PASS. Unreadable strict/admin toggle and untested GitHub Release publisher capability are explicitly **not** called verified; those checks are mandatory for P9-06 publication-time preflight.
- P9-06 remains **NOT AUTHORIZED**; no `v1.0.0` tag or GitHub Release exists. The local `stash@{0}` was not touched.
- The exact content of the owner's local `stash@{0}` cannot be read through GitHub. The stash remains untouched; its patch review is still a local follow-up.

---

## PV-02B — Extend V2 SystemID to 20 bytes (owner-authorized 2026-11-18)

**Post-merge requalification audit:** [PV-01 / PV-02A / PV-02B CI and release-notes gate](NETA_GO_PROTOCOL_V2_POSTMERGE_REQUALIFICATION_2026-11-18.md). CI PASS does **not** imply new release-note approval or release-publication permission.

- [x] **PV-02B — Version-specific SystemID limit:** V2 accepts up to 20 bytes in Bind Request/Response (without a NUL); V1 remains 19 bytes + NUL. Go Client validation honors the selected Session protocol version; Encode/Decode reject exceeding lengths. New tests verify V2 accepts 20/rejects 21, V1 accepts 19/rejects 20, Request/Response round-trips and real TCP V2 Bind of 20 bytes. Protected [PR #8](https://github.com/majiddarvishan/neta-go/pull/8): Go [44187040490](https://github.com/majiddarvishan/neta-go/actions/runs/44187040490) **PASS** and Pinex [44187040470](https://github.com/majiddarvishan/neta-go/actions/runs/44187040470) **PASS** on SHA `9e2ede41284684c640897d282b39f36468335424`. Post-merge main CI evidence is recorded in PV-02B-R; amended Unreleased notes still require fresh owner approval.
- [ ] **PV-02B-R — Release requalification:** post-merge CI evidence is recorded and verified; **owner review/approval of the new V2 20-byte SystemID Unreleased release notes remains OPEN**. No owner approval is inferred from earlier V1 notes. **P9-06 remains NOT AUTHORIZED**; no tag/release.
  - [x] Post-merge protected `main` HEAD `a0db0c5bfbfa364731f6b106f7f5b04de41d5ba2` (PR #8): [Go CI 44187548178](https://github.com/majiddarvishan/neta-go/actions/runs/44187548178) **PASS**, including shared correctness, race, coverage and paired-example smoke; [Pinex CI 44187548184](https://github.com/majiddarvishan/neta-go/actions/runs/44187548184) **PASS**, including pinned C++ fixture/golden comparison.
  - [ ] Owner explicitly approves amended V2 20-byte SystemID release-note wording.

## PV-02A — V2 NUL-free Bind (owner-authorized 2026-11-18)

- [x] **PV-02A — Remove trailing NUL from V2 Bind Request/Response:** Go V2 Client sends NUL-free Bind; default Go V2 Server detects V1/V2 from the first Bind and responds in that format; Go V1-only Server rejects V2; V1 codec and pinned Pinex 1.5.0 fixture unchanged. Codec, real Go loopback, legacy test-fixture, correctness and race checks verified on [PR #7](https://github.com/majiddarvishan/neta-go/pull/7), commit `d456afb2149b5976f560b57674be2e14da0f460a`: [Go CI PASS](https://github.com/majiddarvishan/neta-go/actions/runs/44183468231) and [Pinex Compatibility PASS](https://github.com/majiddarvishan/neta-go/actions/runs/44183468234).
- [ ] **PV-02A-R — Re-review release evidence:** previous P9-05 wire-identity claims were superseded for V2 Bind; **post-merge CI is VERIFIED**, while new owner approval of the NUL-free V2 Bind CHANGELOG remains OPEN. P9-06 remains NOT AUTHORIZED.
  - [x] Go/Pinex post-merge CI on exact `a0db0c5bfbfa364731f6b106f7f5b04de41d5ba2` as linked in PV-02B-R, preserving V1 C++ golden compatibility.
  - [ ] Owner explicitly approves amended NUL-free V2 Bind release-note wording and the requirement for explicit V1 when connecting to legacy Pinex.

## PV-01 — Go-only Session protocol version (owner authorized 2026-11-18)

- [x] **PV-01 — Go protocol-version configuration:** add `ProtocolVersionV1`/`ProtocolVersionV2`, immutable per-Session local version and `WithProtocolVersion` via existing Client/Server Session options; **default V2**, reject unsupported values and test defaults/overrides. At PV-01 completion both versions sent legacy Pinex bytes; **PV-02A supersedes this for V2 Bind only**. V1 remains Pinex-identical. Check Go/Pinex CI on the protected PR before merging.
- [ ] **PV-01-R — Pre-release requalification:** **post-merge CI is VERIFIED** for the version-option/default change; **owner review/approval of the new V2-default public API CHANGELOG remains OPEN**. This does not close P9-06.
  - [x] Go correctness/race, coverage, paired examples and Pinex fixture CI PASS on exact protected `main` HEAD `a0db0c5bfbfa364731f6b106f7f5b04de41d5ba2`, linked in PV-02B-R.
  - [ ] Owner explicitly approves amended Session-version / default-V2 release-note wording.

## Future protocol evolution — owner-approved architecture, implementation NOT AUTHORIZED

- [x] **PROTOCOL-VERSION-001 — Session-scoped version selection (DESIGN ONLY):** owner approved selecting the effective protocol version **once per Session**, with no extra version byte in each Frame. V1 / Pinex 1.5.0 remains unchanged; the earlier default-V1 decision was superseded by owner-approved default V2 (PV-01) and NUL-free Bind V2 (PV-02A). Session versions remain fixed. [Architecture decision](NETA_GO_SESSION_PROTOCOL_VERSIONING_DESIGN_2026-11-18.md).
- [ ] **PV-02 — Select a safe version-selection / negotiation mechanism:** out-of-band peer/endpoint configuration is a candidate; safe in-band negotiation is **not established** for legacy Pinex. Separate design/owner approval is required.
- [x] **PV-03 (NUL-free V2 Bind scope) — Implemented under PV-02A:** the new V2 Bind Request/Response omit the NUL; V1 Bind stays Pinex 1.5.0-compatible and the 10-byte Frame Header/Stream frames are unchanged. Any further version-specific wire changes require separate approval.
- [ ] **PV-04/PV-05 — Peer capability validation and future V2-wire-specific APIs and cross-version tests:** PV-01 provides only local Go configuration; negotiation and wire-dependent behavior still require separate design/approval.

**Release boundary:** Future negotiation work remains out of scope; owner-approved PV-01, PV-02A and PV-02B introduce separately documented Go changes without reopening the legacy V1 wire contract. The P9-06 `v1.0.0` release task still requires separate explicit owner authorization.

---

## Repository structure and public documentation cleanup — 2026-11-18

- [x] Replace implementation-phase filenames with descriptive tests for interoperability, transport faults, reconnect soak, delivery and benchmarks.
- [x] Rename performance and example-smoke scripts, Makefile targets, and the performance workflow; update Go CI and benchmark selectors.
- [x] Remove `docs/PINEX_COMPATIBILITY.md` and replace it with a self-contained `docs/PROTOCOL.md` documenting neta-go's Header, commands, V1/V2 Bind and Session behavior.
- [x] Refocus README, public API, configuration, lifecycle, support and changelog on neta-go.
- [x] Preserve the existing required C++ golden-wire CI job name because it is a protected-`main` required status context. Test fixtures and interoperability tests remain internal.
- [x] Verify Go correctness/race, example smoke and wire golden checks after the cleanup/merge lineage. **On current protected main** `bd8421cf3cabc5cb72263ed964434a48bf54ef22`, required [Go 44630477642](https://github.com/majiddarvishan/neta-go/actions/runs/44630477642) and [C++ wire 44630477596](https://github.com/majiddarvishan/neta-go/actions/runs/44630477596) checks SUCCESS. This confirms ordinary CI, **not** Phase-Q acceptance.
- [ ] Obtain renewed approval of changed Unreleased release notes; release tagging remains separately unauthorized.

**Naming/CI handoff:** [Repository cleanup report](NETA_GO_REPOSITORY_HYGIENE_2026-11-18.md). Historic `.codex/` phase records are archived evidence and may mention superseded paths.

## neta-cpp naming consolidation — 2026-11-18

- [x] Rename maintained Go/C++ interoperability helpers, test identifiers, test logs and C++ peer executable source to use `neta-cpp` in text and `NetaCPP` / `neta_cpp` in legal source identifiers.
- [x] Replace the interoperability binary setting with `NETA_CPP_PEER_BIN`.
- [x] Move pinned C++ compatibility fixture directory to `testdata/neta-cpp-1.5.0/` and retain byte-identical third-party header snapshots for reproducibility.
- [x] Rename the workflow file to `.github/workflows/neta-cpp-wire-compat.yml` and its display name to `neta-cpp Wire Compatibility`.
- [x] Standardize the maintained C++ peer display name to `neta-cpp` across source/test diagnostics, docs and CI.
- [ ] **GitHub protection prerequisite:** the required status context currently remains `Verify Go wire codec against pinned Pinex C++ 1.5.0`. Change that protected-`main` required check in GitHub settings before renaming the actual job label. Retain its current name meanwhile to avoid breaking merges.
- [x] Verify protected-PR and post-merge Go/wire CI on the completed neta-cpp naming cleanup while retaining the old protected required context. [PR #13](https://github.com/majiddarvishan/neta-go/pull/13) merged at `0fadd380d558028a85333fa044eeb4c93ae5c11f`; present main Go/C++ required checks SUCCESS. **Renaming the required check itself is a separate still-open owner/admin decision.**

Historical `.codex/` documents and verbatim upstream C++ includes/namespace `pa/pinex` retain factual source provenance. They are not the project-facing branding or public neta-go API.

## Independent senior engineering audit — 2026-11-18

**Original review-only findings; QA-001..QA-003 remediation authorized 2026-11-18 and in progress in PR #15.** Source HEAD `0fadd380d558028a85333fa044eeb4c93ae5c11f`. [Full findings, exact paths and regression plans](NETA_GO_SENIOR_CODE_AUDIT_2026-11-18.md). Current exact-SHA Go [44202868979](https://github.com/majiddarvishan/neta-go/actions/runs/44202868979), wire [44202868919](https://github.com/majiddarvishan/neta-go/actions/runs/44202868919), full performance [44202869096](https://github.com/majiddarvishan/neta-go/actions/runs/44202869096) CI all PASS. These do not cover every scenario below.

- [x] **QA-001 / P1 — Legacy C++ live interoperability:** Go Client test/benchmark select explicit V1 while public default remains V2. Two real TCP directions, `TestNetaCPPServerWithGoClient` and `TestGoServerWithNetaCPPClient`, both **PASS normally and under `go test -race`** against pinned private C++ 1.5.0, in [private workflow 44260379077](https://github.com/majiddarvishan/pinex/actions/runs/44260379077) on exact neta-go `0824a70127594df72f78d1048cc360e33f57bd5b`. CI was merged as private `pinex` [PR #29](https://github.com/majiddarvishan/pinex/pull/29); runs weekly and on private develop changes. [Evidence and limitations](NETA_GO_QA001_REAL_TCP_VERIFICATION_2026-11-18.md). Public PR golden checks remain separate (QA-009).
- [x] **QA-002 / P1 — Bound BindValidator lifetime and stale identity:** Server-owned permits (ceiling = `maxPendingPreBindSessions`) are held for each running validator until it actually returns, even after TCP timeout. Waiting validators exit when their Session closes. A retired Session cannot reserve an ID after `sessionDone`. Negative tests cover repeated timed-out Binds, Stop while validators block, late return and ID reuse. Arbitrarily blocked user functions cannot be forcibly cancelled; callers must enforce downstream deadlines.
- [x] **QA-003 / P2 — Early Bind length guard:** reject Bind Request/Response bodies >21 bytes after Header parse, before reading or allocating the Body. Header-only transport regression tests cover both Client and Server; the existing exact-limit V1/V2 tests still apply.
- [ ] **QA-004 / P2 — Pending deadline scan: IMPLEMENTATION AND ADVISORY MICROBENCHMARKS PASS; reference-machine qualification, absolute P99 SLA and mandatory gate remain OPEN.** Linear Scan preserved; relative P99 detection regression tolerance 15% with credible statistics; absolute P99 limit requires future measured evidence and owner approval. 2048/8192 synthetic one-Session scan cases do not override the 512 per-Session Request-credit cap. [Contract](NETA_GO_QA_004_005_007_APPROVED_CONTRACTS_2026-11-18.md).
- [ ] **QA-005 / P2 — Performance acceptance: implementation and advisory verification PASS; reference qualification OPEN.** Exact 8 Core / 24 Full matrix, 10-pair/95% comparator and 30-minute soak tooling; latest 24 Full hosted advisory execution and 16 comparator unit tests PASS [run 44313332548](https://github.com/majiddarvishan/neta-go/actions/runs/44313332548). Actual stable machine/immutable baseline, 10 paired reference runs, 30-minute soak, owner-attributable retained-memory metric and owner-approved absolute SLA remain OPEN. Relative 10%/15% tolerances remain report-only; mandatory gate DISABLED. [Contract](NETA_GO_QA_004_005_007_APPROVED_CONTRACTS_2026-11-18.md).
- [x] **QA-006 / P2 — Fatal Accept handling:** PR #17 adds `Server.AcceptDone()` and `AcceptErr()`, preserves the terminal Accept error, refuses silently restarted listeners, and leaves bound Sessions alive until owner Stop. New tests inject both permanent errors and unexpected `net.ErrClosed`; normal Stop remains error-free. Go CI [44259357730](https://github.com/majiddarvishan/neta-go/actions/runs/44259357730) and wire CI [44259357765](https://github.com/majiddarvishan/neta-go/actions/runs/44259357765) PASS on PR. Protected-main QA-006 CI [Go 44259964992](https://github.com/majiddarvishan/neta-go/actions/runs/44259964992) and [Wire 44259965112](https://github.com/majiddarvishan/neta-go/actions/runs/44259965112) both PASS on `0824a70127594df72f78d1048cc360e33f57bd5b`.
- [x] **QA-007 / P2 — Callback panic: IMPLEMENTED AND VERIFIED on isolated feature branch and MERGED via PR #24 (QA-007.1–30, including Completion preservation QA-007.26 and admission-reserved OnClose QA-007.30).** `make verify` including Race, protocol, worker/lifecycle, accounting, late-panic and BindValidator panic/handshake rollback tests PASS [run 44306325369](https://github.com/majiddarvishan/neta-go/actions/runs/44306325369). Supersede legacy Forced Close queued-Completion cancellation and OnClose saturation skip; new design requires preserve Completion and reserve OnClose credit before eligible Session admission. [Contract](NETA_GO_QA_004_005_007_APPROVED_CONTRACTS_2026-11-18.md).
- [x] **QA-008 / P3 — Clean code/docs:** removed duplicate client Bind serialization while retaining early validation and ensuring the Session's actual Sequence is written in the same Frame. V1/V2 exact-wire/sequence and invalid-identity ownership regressions. Merged [PR #19](https://github.com/majiddarvishan/neta-go/pull/19), protected-main SHA `5b7b61fcb78d99e5b489670a328cb13f6adbfd6b` [Go 44266450962](https://github.com/majiddarvishan/neta-go/actions/runs/44266450962) and [wire 44266450928](https://github.com/majiddarvishan/neta-go/actions/runs/44266450928) PASS.
- [x] **QA-009 / P2 — Scheduled fuzz mutation and actual C++ TCP CI:** PR #20 adds V2 Bind Request/Response mutation fuzz targets and a dedicated public `wire-fuzz.yml` job for all seven fuzz targets (3s/target on PR, 12s/target weekly/manual). Real PR mutation run [44266748134](https://github.com/majiddarvishan/neta-go/actions/runs/44266748134) **PASS**, ~1.62M fuzz executions; ordinary Go and golden CI also pass. Genuine two-direction C++ V1 TCP + Go Race workflow is already merged privately in pinex PR #29 and runs weekly/manual, [postmerge PASS 44260379077](https://github.com/majiddarvishan/pinex/actions/runs/44260379077). These are supplemental gates; private C++ job is **not** a mandatory status check on every public Go PR. [Verification detail](NETA_GO_QA009_MUTATION_FUZZ_CI_2026-11-18.md).

**Release gate (historical 2026-11-18 implementation update, reconciled 2026-11-20):** QA-001/002/003/006/007/008/009 are implemented as evidenced; QA-007 is now **MERGED** through PR #24. QA-004/005 qualification, stable reference environment, absolute SLA and mandatory performance gate remain open. [Approved QA contracts](NETA_GO_QA_004_005_007_APPROVED_CONTRACTS_2026-11-18.md). Do not claim release readiness or create v1.0.0 Tag/Release without distinct owner authorization.

## QA-005-MEM-001 — attributable retained memory (2026-11-19; B APPROVED, DESIGN DRAFT)

- [x] **MEM-001 — Owner decision:** Hybrid Ownership Accounting (B), with no heavy new global hot-path atomic; confirmed on 2026-11-19. [Design](NETA_GO_QA005_ATTRIBUTABLE_MEMORY_OWNERSHIP_DESIGN_2026-11-19.md).
- [x] **MEM-002 — Technical ownership audit:** inspected Session/owner ledger, inbound/outbound frames, pending and Completion/OnClose charge lifetimes, worker queues and Panic diagnostics; documented under/overcount risks and what the existing counts do not measure.
- [x] **MEM-003 — Measurement adapter compatibility design and diagnostic prototype:** versioned test-only overlays with original/effective source SHA-256 manifests and strict patch anchors; full equal-on-both-sides 10-pair qualification NOT STARTED. [Measurement plan](NETA_GO_QA005_MEMORY_MEASUREMENT_QUALIFICATION_PLAN_2026-11-19.md).
- [ ] **MEM-004 — PARTIALLY VERIFIED / OPEN; full attributed retained-memory INCONCLUSIVE:** V9 test-only F1–F5 observed backing-buffer diagnostic extends V7. F5 covers unreserved non-drained inbound Body slices (especially Bind Request/Response) from read allocation until handler return, plus immediate read-error rollback under Session.mu; M1 maps/worker/pending and D1 diagnostic graphs remain excluded. V9 also requires sum of five category counters to equal the Session total at every sample and HWM observation; otherwise both are invalid. [Actions 44489743062](https://github.com/majiddarvishan/neta-go/actions/runs/44489743062) V8 PASS 3 jobs and all 4 optional stages (10 Python tests, 11 Go -race lifecycle, exact pinned-source parity, unqualified overhead). [Actions 44490084898](https://github.com/majiddarvishan/neta-go/actions/runs/44490084898) V9 PASS all 3 jobs plus all optional stages (11 Python tests, 12 Go -race lifecycle tests, 4 Python parity tests, 5 Python overhead tool tests and short one-scenario smoke). Historical intermediate green workflows [44488997407](https://github.com/majiddarvishan/neta-go/actions/runs/44488997407) and [44489465368](https://github.com/majiddarvishan/neta-go/actions/runs/44489465368) had FAILING optional owned-buffer/parity/overhead steps due outdated synthetic fixtures and wrong first-ReadFull assertion; fixed by separate commits 0c0dcca0 and 538eb70d. Source-V1 fixed 9b7b2318; original production source unchanged. Sampling max with two observations is not simultaneous global peak, Session HWM upper is not the actual peak; F4 pre-Session Bind encoder, M1/D1, decoded objects/other transients, unapproved sample density and overhead thresholds still OPEN. Never emit retained-attributed-B; no numeric baseline or gate.
- [x] **MEM-004 M1/D1 audit and owner scope decision B:** [Source ownership audit](NETA_GO_QA005_M1_D1_OWNERSHIP_SCOPE_AUDIT_2026-11-19.md); B approved 2026-11-19 for incremental test-only attribution of neta-created M1 metadata / D1 rendered text with alias dedup and proven lifetime; foreign raw graphs/runtime excluded. [DECISION_LOG §77](DECISION_LOG.md). No new complete-memory metric or gate approved.
- [ ] **MEM-004 M1/D1 Option B implementation — PARTIALLY VERIFIED, OPEN:** [Owner decision §77](DECISION_LOG.md) approved incremental neta-only ownership. [V10 Actions 44510555448](https://github.com/majiddarvishan/neta-go/actions/runs/44510555448) all three jobs and optional owned/parity/overhead PASS: D1 retained unique `string(debug.Stack())` *logical text length* by per-Session Panic `Sequence`, dedup First/OnClose/Recent aliases, retain First/OnClose outside Recent budget, exclude all raw recovered foreign graphs. [V11 Actions 44511176165](https://github.com/majiddarvishan/neta-go/actions/runs/44511176165) all three jobs/optional stages PASS: M1 admitted `pendingRequest` object identity retained after Pending map removal / simulated Done until Completion release; duplicate/missing transitions invalid; **object count only**. [V12 Actions 44511644311](https://github.com/majiddarvishan/neta-go/actions/runs/44511644311) all three jobs/optional stages PASS: static *logical* `unsafe.Sizeof(pendingRequest{})` footprint with checked multiplication, separate `probe-m1-pending-struct-logical-peak-B`, 40 B for one live pending on that runner; allocator bucket/map/closure not included. 12/13/14 Python anchored tests respectively, Go lifecycle -race and source-anchor compatibility with each exact adapter. All evidence diagnostic and `PARTIAL_INCONCLUSIVE`: M1 structural maps/other objects; queue/worker subsets only, D1 other rendered strings/metadata, global simultaneous peak, 10 paired overhead/qualification, sample-gap policy remain OPEN. No canonical `retained-attributed-B` or gate. **V13–V16 partial Worker/Queue evidence:** [Dedicated evidence](NETA_GO_QA005_M1_WORKER_QUEUE_V13_V16_EVIDENCE_2026-11-19.md). [V13 CI 44524558066](https://github.com/majiddarvishan/neta-go/actions/runs/44524558066) PASS all required/optional stages: per-pool mutex logical task-slice capacity and Queue struct size, dedup owners/backing, reject aliases. [V14 CI 44525104589](https://github.com/majiddarvishan/neta-go/actions/runs/44525104589) PASS: worker_scheduler.go mandatory original/effective Source-V1 SHA. [V15 CI 44525522696](https://github.com/majiddarvishan/neta-go/actions/runs/44525522696) PASS: distinct callbackWorker static Go struct logical footprint, observed 2 Workers/96 logical B, no goroutine/Channel/timer costs. [V16 CI 44525968814](https://github.com/majiddarvishan/neta-go/actions/runs/44525968814) PASS: actual blocked Worker + queued callback, backing release and Worker idle retirement under -race. V13/V14/V15/V16 Python tests 15/16/17/18 PASS; Source Anchor parity and optional overhead previews independently PASS; preview status INCONCLUSIVE. Queue/Worker subsets verified ONLY as diagnostics; Map buckets, other metadata, client session churn and actual total retained memory OPEN. No qualified retained-attributed-B or gate.
- [x] **MEM-004 Client generation snapshot integrity — V17/V18 TEST-ONLY COMPLETE (not full MEM-004):** [Client generation freeze evidence](NETA_GO_QA005_CLIENT_GENERATION_FREEZE_V17_V18_EVIDENCE_2026-11-19.md). V17 `c8cf0467` freezes under Client.mu each Client generation/current identity plus a no-in-flight-Connect precondition, deduplicates Clients, detects transient reconnect that opens/closes between sampling ticks, current pointer swap, and stopped Client; both `client_connect.go` and `client_lifecycle.go` mandatory original/effective SHA parity. Historical [CI 44528814317](https://github.com/majiddarvishan/neta-go/actions/runs/44528814317) overall GREEN but optional owned/parity/overhead steps FAIL from stale Python last-file assertion; independently fixed `3fe01bb2`. [V17 CI 44529067306](https://github.com/majiddarvishan/neta-go/actions/runs/44529067306) all three jobs/four optional steps PASS: 19 Python overlay tests, Go -race, 6 Python parity tests, pinned source Go -race. V18 `ef117e38` adds an actual Client TCP close/reconnect lifecycle test proving the old ownership window is invalid after real new Bound generation; [V18 CI 44529571646](https://github.com/majiddarvishan/neta-go/actions/runs/44529571646) all jobs/optional steps PASS, 20 Python overlay tests and real Client reconnect Go -race, 6 SHA parity tests. Exclusions still include pre-window historical Client generations with active callbacks, frozen registry GC liveness bias, non-atomic cross-owner snapshots, Map/runtime allocations, sampling gaps and all-M1/D1 coverage. V18 overhead 25x hosted `FEASIBILITY_ONLY_INCONCLUSIVE`; `retained-attributed-B` unissued; gate DISABLED. 
- [ ] **MEM-005 — LIMITED 3-MODE FEASIBILITY VERIFIED, QUALIFICATION OPEN:** At `fbadb55124193b5da45172071cd29ff80bbb1162`, [Actions 44486737303](https://github.com/majiddarvishan/neta-go/actions/runs/44486737303) PASS all jobs and optional stage, including 5 Python overhead-parser tests and real Core RR-64B-S1-C1-medium 25x each on the SAME source SHA: no overlay 37486 ns/op, overlaid bookkeeping with Sampler OFF 41786 ns/op, overlaid with Sampler ON 35932 ns/op. These are single noisy unpaired hosted-runner measurements, NOT overhead performance verdicts; output `FEASIBILITY_ONLY_INCONCLUSIVE`, no approval, no gating or 10-pair equivalence. Probe separates source-to-overlay/bookkeeping and overlay-OFF-to-ON sampling effects but cannot distinguish fixture-side and counter-side components alone. [44486575046](https://github.com/majiddarvishan/neta-go/actions/runs/44486575046) failed with zero jobs from YAML literal `$'` interpolation, repaired at fbadb551. Reference Go 1.27 stable host, Core 8 / Full 24 scenario matrices, paired 10x randomized A/A, 30m soak, max-gap threshold, numeric coverage bounds/overhead acceptance NOT DONE. Gate DISABLED.
- [ ] **MEM-006 — Reference-machine, numeric baseline, paired qualification, absolute SLAs, mandatory gate:** NOT APPROVED; gate DISABLED.
- [x] **QA-007** remains CLOSED and merged in PR #24; **QA-004/005** remain OPEN. Later owner-authorized PRs #24–#27 were merged; no tag/release.

## QA-004 / QA-005 / QA-007 — owner-approved design-to-implementation checklist (2026-11-18)

- [x] Owner-approved QA-004.1–3, QA-005.1–8 and QA-007/.1–30 choices transcribed in the contract document (documentation-only branch).
- [x] Owner separately resolved legacy conflicts: QA-007.26=A for **all** Forced Close causes and QA-007.30=A for **admission-reserved** OnClose credit; old choices are marked superseded, not silently erased from historical records.
- [x] Implemented and verified on feature branch: adapt Forced Close Completion scheduling and Request-credit lifecycle; prove no accepted Completion is silently dropped and no double result/start occurs.
- [x] Implemented and verified on feature branch: adapt OnClose credit reservation at eligible Session admission across Server Bind, Client Connect, failures, reconnect and Stop; preserve capped workers and bounded owner credits; prove rejected admission cannot leak credit.
- [x] Implemented and verified on feature branch: implement `ErrCallbackPanic`, typed `Session.Diagnostics()`, bounded lazy recent-ring, safe rendering, monotonic sequences and immutable independent snapshot.
- [x] Implemented and verified on feature branch: test concurrent panic/Close/snapshot, late panic after Done, OnClose panic isolation, worker starvation, blocked callbacks, race and exact accounting release.
- [x] Implemented and verified on feature branch: implement QA-004 representative microbenchmark and valid traffic workloads, P99 internal timeout settlement detection (not callback dispatch), including 512 per-Session cap distinction.
- [x] Implemented and verified on feature branch: implement QA-005 fixed 8 Core/24 Full workload, paired 10-run statistical comparison, 95% confidence, tolerance/zero handling, INCONCLUSIVE status, 30-minute stability and versioned historical baselines.
- [ ] Qualify a stable reference benchmark environment and obtain separate owner approval for any absolute numeric SLA and mandatory CI performance gate.
- [x] Owner explicitly authorized scoped source/test/CI implementation on the isolated feature branch; no additional permission was needed for the approved work.
- [x] Obtain scoped owner PR/Merge permission and merge approved integration/documentation/examples through PRs #24–#27. **Release/tag permission remains OPEN separately (P9-06)**; QA-004/005 remain unchecked and QA-007 is merged.

## Verification and update log

| Date | HEAD / Commit | Scope | Evidence |
|---|---|---|---|
| 2026-11-17 | `cc0d25e9252b48f38dcddeeb53eaa6e7fe1cbf4c` | Phase 3 source | Go [44057820360](https://github.com/majiddarvishan/neta-go/actions/runs/44057820360) PASS; C++ golden [44057820405](https://github.com/majiddarvishan/neta-go/actions/runs/44057820405) PASS |
| 2026-11-17 | `c98f731fef89519d62d95248982538f25a36db82` | Documentation/handoff | Go [44058276200](https://github.com/majiddarvishan/neta-go/actions/runs/44058276200) PASS; C++ golden [44058274150](https://github.com/majiddarvishan/neta-go/actions/runs/44058274150) PASS |
| 2026-11-17 | `8eead509c6817722d6b7c6f5e5a17e1734749911` | Phase 6 Server lifecycle/admission | Go [44070940615](https://github.com/majiddarvishan/neta-go/actions/runs/44070940615) PASS; Pinex Wire Compatibility [44070940706](https://github.com/majiddarvishan/neta-go/actions/runs/44070940706) PASS |
| 2026-11-17 | `a05a735aa0383d2588b41b1a2258282d734ff72b` | Phase 6 Client CurrentSession/Stop lifecycle | Go [44071959633](https://github.com/majiddarvishan/neta-go/actions/runs/44071959633) PASS; Pinex Wire Compatibility [44071959704](https://github.com/majiddarvishan/neta-go/actions/runs/44071959704) PASS |
| 2026-11-17 | `f8ce7669d2bbde33d3134d300e3256ae290dc529` | Phase 6 Client Connect/Bind, reconnect and final acceptance | Go [44078517718](https://github.com/majiddarvishan/neta-go/actions/runs/44078517718) PASS; Pinex Wire Compatibility [44078517770](https://github.com/majiddarvishan/neta-go/actions/runs/44078517770) PASS |

## Canonical references

- [Project handoff](HANDOFF.md)
- [Phase 9 release-readiness plan](NETA_GO_PHASE_9_RELEASE_READINESS_PLAN_2026-11-17.md)
- [Architecture freeze and implementation roadmap](NETA_GO_ARCHITECTURE_FREEZE_AND_IMPLEMENTATION_ROADMAP_2026-11-17.md)
- [Implementation authorization](IMPLEMENTATION_AUTHORIZATION_2026-11-17.md)
- [Resource admission design](NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md)
- [Worker capacity and resource accounting design](NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md)
- [Performance contract](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md)
- [Phase 6 Server implementation report](NETA_GO_PHASE_6_SERVER_IMPLEMENTATION_2026-11-17.md)
- [Phase 6 Client lifecycle report](NETA_GO_PHASE_6_CLIENT_STOP_IMPLEMENTATION_2026-11-17.md)
- [Decision log](DECISION_LOG.md)


### Phase 4 progress evidence — 2026-11-17

- P4-01 and P4-02 implemented in `resource_ledger.go`; Client/Server constructors now create independent owner ledgers.
- Tests cover exact capacity, over-capacity rejection, release/underflow protection, independent Application/Completion budgets, shared Server aggregate queue counters, Client-vs-Server aggregate behavior, OnClose event credits, owner isolation and concurrent Request admission.
- Implementation commit: `9f2514115b601c7cdc2efb91fe98daa628b1c7b0`; formatting-only follow-up: `94760d4d0cb2a319b7c49665b0cfcffc4b7b45db`.
- Go CI [44060075443](https://github.com/majiddarvishan/neta-go/actions/runs/44060075443) PASS; Pinex Wire Compatibility [44060075468](https://github.com/majiddarvishan/neta-go/actions/runs/44060075468) PASS.
- Current source baseline for the next Phase 4 slice: `94760d4d0cb2a319b7c49665b0cfcffc4b7b45db`.


### Phase 4 completion evidence — 2026-11-17

- Implementation report: [NETA_GO_PHASE_4_RESOURCE_ADMISSION_IMPLEMENTATION_2026-11-17.md](NETA_GO_PHASE_4_RESOURCE_ADMISSION_IMPLEMENTATION_2026-11-17.md).
- Source verification HEAD: `2935402366603267ba60c181a057d26cf0e7e9a6`.
- 46 Session tests + 8 owner-ledger tests.
- Go CI [44062568415](https://github.com/majiddarvishan/neta-go/actions/runs/44062568415) PASS; Pinex Wire Compatibility [44062568425](https://github.com/majiddarvishan/neta-go/actions/runs/44062568425) PASS.
- At the time Phase 4 closed, Phase 5 had not yet been authorized. Phase 5 was subsequently authorized and is now COMPLETE / CI PASS; see the Phase 5 completion evidence below.


### Phase 5 implementation authorization — 2026-11-17

The owner explicitly approved Phase 5 by replying «آره» after the request to begin the bounded callback Worker Scheduler.

**Authorized scope:** implement the already-frozen WORKER-001..009C contracts only:
- Three independent owner-scoped Application, Completion and OnClose pools; lazy creation; no shared scheduling/lock/wakeup domain across classes.
- Enforce owner active-worker ceilings and per-Session concurrency intersections; preserve owner accounting across Session generations.
- Per-class FIFO round-robin scheduling with one reusable ready-Session node and one callback per eligible Session turn.
- Independently configurable 30s idle retirement grace, zero warm-idle floor, worker reuse and enqueue/retirement linearization.
- Forced Close A cancellation/start linearization; queued Application/Completion cancellation and exact resource release; started callbacks retain permits/credits until return.
- OnClose only after Done, best-effort/at-most-once, bounded queued+running event credits and permanent skip at saturation.
- Isolation, fairness, lifecycle, race and churn tests plus gofmt, vet, unit and race CI.

**Not authorized by this approval:** Phase 6 Client/Server networking and reconnect, Phase 7 live Pinex TCP interoperability, Phase 8 benchmark/pooling optimization, Phase 9 examples/release/deployment. No frozen decision, default, public API or wire contract is reopened.


### Phase 5 authorization closure

Phase 5 was explicitly authorized by the owner on 2026-11-17 and is now COMPLETE / CI PASS. This closure does not authorize Phase 6 or later phases.


### Phase 6 Client lifecycle evidence — 2026-11-17

- Report: [Client CurrentSession/Stop lifecycle](NETA_GO_PHASE_6_CLIENT_STOP_IMPLEMENTATION_2026-11-17.md).
- Source verification HEAD: `a05a735aa0383d2588b41b1a2258282d734ff72b`.
- 4 focused Client lifecycle tests.
- Go CI [44071959633](https://github.com/majiddarvishan/neta-go/actions/runs/44071959633) PASS; Pinex Wire Compatibility [44071959704](https://github.com/majiddarvishan/neta-go/actions/runs/44071959704) PASS.
- At this earlier Client lifecycle checkpoint, Connect/Bind still awaited the owner Bind identity decision; Option B was subsequently approved and implemented. Final evidence is recorded in the completion section below.


### Phase 6 Client Connect/Bind and reconnect implementation — 2026-11-17

- Owner decision: Option B, recorded in .codex/DECISION_LOG.md §56.
- Added mandatory WithClientSystemID(string) and optional WithClientBindType(BindType); default is bi-directional.
- Added Client.Connect(ctx) with absolute Dial and Bind deadlines, caller Context precedence and no post-success Context coupling.
- Added generation fencing and a single reconnect supervisor using the approved 1s/30s Full-Jitter exponential windows; retries only Dial failures/timeouts and unexpected post-Bound transport failures. Bind rejection/timeout are non-retryable. No Request replay.
- Every generation reuses the Client-owned resource ledger and callback dispatcher.
- Uni-directional Client behavior is requester-only and compatible with Pinex 1.5.0.
- Added Client Bind validation, connect/stop, timeout, rejection, reconnect-generation, uni-directional behavior and Bind-vs-Context race tests. Also hardened the Worker Scheduler test to wait for deferred resource release after callback return, eliminating a timing-sensitive false failure. Final Go and Pinex CI evidence is recorded below.


### Phase 6 Client Connect/Bind and reconnect completion evidence — 2026-11-17

- Report: [.codex/NETA_GO_PHASE_6_CLIENT_CONNECT_IMPLEMENTATION_2026-11-17.md](NETA_GO_PHASE_6_CLIENT_CONNECT_IMPLEMENTATION_2026-11-17.md).
- Owner decision: Option B, DECISION_LOG.md §56.
- Final verified source HEAD: f8ce7669d2bbde33d3134d300e3256ae290dc529.
- Go CI [44078517718](https://github.com/majiddarvishan/neta-go/actions/runs/44078517718) PASS: gofmt, vet, unit tests and race tests.
- Pinex Wire Compatibility [44078517770](https://github.com/majiddarvishan/neta-go/actions/runs/44078517770) PASS: pinned C++ 1.5.0 golden fixtures.
- Phase 6 P6-01..P6-11 are COMPLETE. Phase 7 live TCP interoperability, Phase 8 performance and Phase 9 release remain NOT AUTHORIZED.


## 2026-11-18 QA-004/005/007 implementation branch tracker

- [x] Check main HEAD, read approved contracts and create isolated feature branch.
- [x] Prepare bounded typed QA-007 panic diagnostics, recovery, Completion and OnClose lifecycle changes with targeted unit tests.
- [x] Prepare QA-004 linear-scan 32/128/512/2048/8192 synthetic benchmarks and internal terminal deadline detection timestamps.
- [x] Prepare QA-005 8 Core/24 Full benchmark matrix, 10-pair 95% comparator and 30-minute soak support.
- [x] Verify Go formatting, vet, uncached Go unit/race, lifecycle, accounting, protocol and panic tests on latest verified source SHA `eaf022357e369b8d484376a3385b16f2ce4fafd6`: PASS, [run 44310174076](https://github.com/majiddarvishan/neta-go/actions/runs/44310174076).
- [x] Capture QA-004 Scan + 1,200-sample Detection P99 and QA-005 Core+Full (8 / 24) advisory measurements on GitHub-hosted runner: PASS as tool execution only, [run 44310174076](https://github.com/majiddarvishan/neta-go/actions/runs/44310174076) (not an approved baseline).
- [x] Harden paired qualification with immutable source preflight (tracked and untracked Go file guards), exact 8/24 workload-name match cross-checked against Go fixture, matched source/equipment evidence, and separate QA-004 P99 comparison. Malformed, duplicate or unreadable evidence returns INCONCLUSIVE; comparator has 16 PASS unit tests, [run 44313332548](https://github.com/majiddarvishan/neta-go/actions/runs/44313332548).
- [x] Record per-workload accepted operation count, offered producer count, capacity rejections and post-run owner resource counters; all post-run counters zero on 32 advisory Core+Full output rows in [run 44313332548](https://github.com/majiddarvishan/neta-go/actions/runs/44313332548). These are not measured peak retained-memory bytes or a qualified baseline.
- [ ] Develop/approve attributable retained-library-memory evidence (never equate instant process heap to owned retained memory); absent valid measure remains INCONCLUSIVE.
- [x] Close local QA-007 coverage-triggered flaky test after owner-reported repeat evidence on `2db90faf67923ea796ed611629390197cffb0e43`: 100× race PASS, 100× targeted coverage PASS, `make smoke` PASS with root 82.7% / wire 92.0%, real loopback and graceful stop. Only test synchronization modified; production code unchanged. **QA-007 [x] remains closed.**
- [x] **QA004/005-SOURCE-V1 — Owner Option A approved (2026-11-19):** pin exact current feature-branch SHA `9b7b2318f73d173a99d22489042f84f8ce58b745` as the initial **source anchor for future changes**; see `docs/performance-baselines/qa004-qa005-source-v1.json` and `.codex/DECISION_LOG.md` §74. This is **not** owner approval of numeric benchmark results or the reference hardware.
- [x] Prepare local draft reference capture for pinned `QA004-QA005-SOURCE-V1`: `scripts/qa005_baseline_capture.sh` (modes all/Core/Full/QA-004, 10 independent measurements per mode, SHA-256 logs, exact scenario checks, Linux CPU/op, post-workload ledger, fail-closed archive; `owner_approved=false` always). **Not run yet; production code unchanged.**
- [x] Owner-local draft numeric evidence captured and independently reviewed: pinned SOURCE-V1 SHA `9b7b2318f73d173a99d22489042f84f8ce58b745`, 10 Core + 10 Full + 10 QA-004 benchmark processes PASS (370 rows), ordered-log SHA-256 confirmed, 320 traffic resource rows zero, 60,000 QA-004 samples. **Original script overall reported FAIL due to unrecorded Git worktree cleanup error** (not a benchmark failure); numerical approval remains OPEN. See [full draft evidence](../docs/performance-baselines/QA004_QA005_SOURCE_V1_NUMERIC_CAPTURE_2026-11-18.md).
- [x] Harden reference capture cleanup diagnostics without forcing deletion: `scripts/qa005_baseline_capture.sh` now records `measurement_status` and `worktree_cleanup_status` separately and stores `worktree-cleanup.log` on failure (not yet executed locally after modification).
- [x] Diagnose stale worktree from owner-local capture: owner reports `?? scripts/__pycache__/` as the only untracked directory in `/tmp/neta-numeric-ref.5S0ymlDB/source`; Python importlib-generated bytecode cache blocked non-force Git cleanup. Commit `68c861233a280cac3929c0d3db85e9d10dbe94cf` disables bytecode writes (`PYTHONDONTWRITEBYTECODE=1`, `python3 -B`) in the local baseline collector; no benchmark rerun or production change. Old worktree cleanup not yet confirmed by owner.
- [ ] Capture and approve versioned numerical reference measurements for `QA004-QA005-SOURCE-V1` on an accepted stable host, with a valid attributable-retention method; retain all evidence immutably. Do not set `owner_approved=true` for numeric manifests without a separate owner review.
- [ ] Record 10-pair/95% QA-005 comparison and credible QA-004 P99 on a matched, owner-approved reference environment; no absolute SLA is approved.
- [ ] Run qualified 30-minute soak and 10-pair comparison on owner-approved stable hardware (otherwise NOT RUN).
- [x] Obtain scoped PR/Merge permission for approved PRs #24–#27, all merged after required checks. **No Tag/Release permission** is inferred (P9-06 still open).

**QA-007 = [x] after all required Go/race tests PASS. QA-004 = [ ] and QA-005 = [ ] until full reference qualification.**

## Development-First: complete authorized code and 12 example programs before heavy QA (owner 2026-11-19)

**HISTORICAL PHASE-D PLANNING SNAPSHOT (now 16/16 DONE; Phase Q deferred):** no heavy QA-004/QA-005 qualification or mandatory Performance Gate. [Detailed file-level tasks, dependencies and acceptance criteria](NETA_GO_DEVELOPMENT_FIRST_EXAMPLES_BACKLOG_2026-11-19.md). Date-scoped source audit: feature HEAD `7866125c264cc97491785fca94278efe8d81d191`, protected-main HEAD `24b7c5f6eb4e001f30dd8a564a337ca1f506eac8`. Exactly **2 existing executable examples**, `examples/client` and `examples/server`, both preserved.

**Development closure tasks (6 total; counts below exclude approval-blocked future features):**
- [x] **DEV-01 (P0) — STATIC AUDIT COMPLETE (2026-11-19):** verified 119-commit feature-vs-main delta, 13 changed production Go files, public API/CLI surface, QA-004/005/007 and DEV/EX/Q/R categorization; no confirmed missing production behavior from this source review. Documentation gaps assigned to DEV-05; MEM-004 measurement scoped to DEV-02. No fresh build/test executed for this documentation-only audit; see [DEV-01 audit](NETA_GO_DEV_01_PRODUCTION_API_AUDIT_2026-11-19.md).
- [x] **DEV-02 (P0) — BOUNDED SCOPE CLASSIFICATION COMPLETE (2026-11-19):** documented F1–F5 and each M1/D1 category with source, lifecycle/alias, supported test-only diagnostic, explicit exclusions and exact remaining qualification blockers; no new V-numbered probe or production hot-path code justified. This closes only the development *classification* task; MEM-004 canonical retained-attributed-B still PARTIAL_INCONCLUSIVE/OPEN, MEM-005/006 and QA-005 OPEN. See [DEV-02 matrix](NETA_GO_DEV_02_HYBRID_B_CATEGORY_MATRIX_2026-11-19.md). No new tests for this documentation-only task; historical tests identified separately.
- [x] **DEV-03 (P0) — COMPATIBILITY CONTRACT FROZEN (2026-11-19):** original Client/Server paths, default addresses, flags, log-based smoke tokens and Ctrl-C Stop semantics recorded in [examples compatibility contract](NETA_GO_DEV_03_EXAMPLE_COMPATIBILITY_CONTRACT_2026-11-19.md). Existing package source unchanged since historical CI 44529571646 where Go verify+paired smoke PASS; no fresh build for this doc-only commit. New executable packages must use stdlib/public neta options. DEV-04 supplies new bounded smoke.
- [x] **DEV-04 (P1):** bounded, lightweight build and loopback smoke for all example packages, deterministic startup, termination and logs; not full benchmark/race/fuzz/soak. **Verified:** 12 binaries, focused Go unit tests, 12 bounded positive/negative loopback pairs and real restarted-Server reconnect; go vet/gofmt, [CI 44542311954](https://github.com/majiddarvishan/neta-go/actions/runs/44542311954).
- [x] **DEV-05 (P1):** `examples/README.md` scenario matrix, runnable commands, optional JSON config files, links from README and docs/CONFIGURATION.md; note defaults and V1/V2 incompatibility. **Verified:** [12-example guide](../examples/README.md), JSON fixtures, CLI mapping, README/API/CONFIGURATION links and V1/safety/Stop caveats.
- [x] **DEV-06 (P0):** owner-reviewable DEV_READY_FOR_QUALIFICATION report: all authorized DEV and EX tasks individually DONE with lightweight evidence, no missing production behavior concealed under QA-005 and no blocked future features auto-approved. **Closeout:** [DEV_READY_FOR_QUALIFICATION report](NETA_GO_DEV_READY_FOR_QUALIFICATION_2026-11-19.md); verified 16/16 Development tasks with source-level SHA parity and three PASS lightweight CI runs, listed owner-decision/Phase-Q/Phase-R blockers, no heavy testing/release. Technical scope complete; owner must separately authorize Phase Q.

**Five NEW Client examples (the current `examples/client` remains unchanged):**
- [x] **EX-C01 (P0):** `examples/client-config`: typed Functional Options configured through explicit CLI flags + optional strict JSON, durations, V1/V2, timeouts, auto-reconnect, worker/queue limits; explicit CLI > JSON > library defaults. **Verified:** strict JSON + explicit CLI precedence unit tests; config/config-json loopback.
- [x] **EX-C02 (P1):** `examples/client-concurrent`: bounded parallel SendRequest/Completion, count/inflight flags, correlation and capacity/cancellation handling. **Verified:** bounded workers/credits, eight correlated concurrent Completions loopback.
- [x] **EX-C03 (P1):** `examples/client-reconnect`: opt-in reconnect, generation-aware OnBound/OnClose/CurrentSession; **no automatic message replay**. **Verified:** actual second OnBound after kill/restart same port in CI 44541733512 & 44542311954, no replay.
- [x] **EX-C04 (P1):** `examples/client-v1`: explicit ProtocolVersionV1, SystemID max 19 bytes, no automatic downgrade. **Verified:** V1 loopback to V1-only Server; 19-byte invalid-case test.
- [x] **EX-C05 (P2):** `examples/client-diagnostics`: Completion error, OnClose, Session.Diagnostics() and safe bounded lifecycle. **Verified:** timeout, local Completion panic and peer OnRequest panic scenarios with typed Diagnostics.

**Five NEW Server examples (the current `examples/server` remains unchanged):**
- [x] **EX-S01 (P0):** `examples/server-config`: strict CLI/JSON config using public Server/Session Options, max Sessions, admission, callback workers, budgets/timeouts. **Verified:** strict JSON/CLI negative config tests and config/config-json loopback.
- [x] **EX-S02 (P1):** `examples/server-bind-validator`: explicit demo-only allowlist and duplicate/invalid identity rejection, without claiming production authentication. **Verified:** allowlist acceptance/negative rejection and same-ID duplicate Bind integration unit test; explicit refusal logging.
- [x] **EX-S03 (P1):** `examples/server-concurrency`: concurrent Sessions with separate per-Session/owner bounded worker and queue capacity; paired with EX-C02. **Verified:** bounded multi-session server paired with eight correlated concurrent Client Requests.
- [x] **EX-S04 (P1):** `examples/server-v1`: V1-only Server paired with EX-C04, reject default V2, no invented protocol negotiation. **Verified:** V1 pairing, V2 default mismatch loopback and distinct-ID rejection unit test.
- [x] **EX-S05 (P2):** `examples/server-diagnostics`: OnBound/Request/OnClose, bounded Panic diagnostics with controlled optional trigger, Server.Stop(ctx). **Verified:** OnBound/OnRequest/OnClose diagnostics, safe defaults, explicit peer-panic smoke and Graceful Stop.

**Not executable DEV blockers without owner permission:** PV-02/PV-04/PV-05 protocol negotiation & capabilities, protection-required-check renaming, release-note owner approvals, PR/Merge/Tag/Release. Track them separately as `BLOCKED BY OWNER/RELEASE`, not as hidden Done tasks.

**Phase Q parked after DEV completion (not started by this request):** QA-004 reference P99, QA-005 approved Core/Full 8/24 matrix, 10-pair/95% comparison, measured MEM-004 attributable bytes and MEM-005 overhead validity, 30-minute soak, reference-machine, absolute SLA and optional owner-approved performance gate. Historical completed CI evidence is not erased and must not be reported as new final Q evidence. No full heavy suites in the DEV plan; targeted compilation/individual smoke is permitted. **No new PR, merge, tag, release or production code from this planning change.**
