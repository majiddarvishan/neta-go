> **PHASE Q STEP 10 — SOFTWARE-ONLY CORRECTNESS AND MEMORY HARNESS PREPARATION (2026-11-22):** Consolidated candidate branch: `qual/phase-q-software-harnesses-2026-11-22`; protected `main` remains `d376cd8a375328aa971cd4441d989920bf6009a0`. No production Go/API/wire source changes. Consolidated candidate source tested by the Q-COR-04 Pinex job: `63cbb9f41c76090d5fd32452e3fe48dafdfd223e`; later candidate commits are documentation-only.
>
> - **Q-COR-02:** bounded explicit reconnect/RST/OnClose/no-implicit-retry harness is merged on main; dedicated Q-COR-02 CI #45014929050 and required Go #45014929048 / C++ #45014929039 all PASS. Full stress/load/reconnect campaign and resource teardown remain OPEN.
> - **Q-COR-03:** deterministic seed replay plus a bounded 1s-per-target fuzz smoke passed 7/7 V1/V2 parser fuzz targets with 2 workers (~368,043 executions) in [CI #45025904772](https://github.com/majiddarvishan/neta-go/actions/runs/45025704458). Reproducible campaign runner and manifest/artifact workflow are in the candidate. Extended fuzz/mutation acceptance remains OPEN and was not run.
> - **Q-COR-04:** CLOSED for the defined correctness scope. [Pinex CI #45026010703](https://github.com/majiddarvishan/pinex/actions/runs/45026010703) passed pinned C++ 1.5.0 peer build, byte-exact golden fixture, both live TCP directions, deterministic fragmented/deadline/RST/EOF fault tests, and the same Go tests under `-race`. C++ source SHA `f7bd1eb779baff0d10e624f20522df345e6ee747`; C++ binary SHA-256 and test manifest were printed in the job log. Artifact upload was blocked by GitHub storage quota; upload is non-blocking and the overall test job passed.
> - **MEM-004/005 V19:** [CI #45025289359](https://github.com/majiddarvishan/neta-go/actions/runs/45025289359) passed 22 Python adapter tests and generated Go lifecycle/sampling tests under `-race`. Unknown retired callback-owned Sessions fail closed at freeze and at each sample; known sessions deduplicate. Sampling timestamp/gap/snapshot-duration integrity is synthetic only. MEM-004/005 remain OPEN/INCONCLUSIVE: callback churn between sample observations, strong-reference/GC liveness bias, complete M1/D1 coverage, observer overhead and accepted sampling thresholds are not proved.
>
> **Current normalized open packages: 17 = 8 Qualification + 7 Owner Decisions + 2 Release.** Q-COR-01, Q-COR-04 and P9-06 are closed; Q-COR-02, Q-COR-03, Q-ENV-01, QA-004/005, MEM-004/005/006 and the remaining owner/release packages stay open.
>
> No heavy stress/soak, extended fuzz, reference-host A/A, 10-pair qualification, numeric baseline/SLA approval or Performance Gate activation. [PR #59](https://github.com/majiddarvishan/neta-go/pull/59) is OPEN for review. All five checks PASS on head `926f3b244f4e85fe27478c4767c282730426f9e0`: Go #45026358040, C++ Wire #45026357958, parser mutation #45026357916, Q-COR-03 #45026357905, MEM-004/005 #45026357903. No merge/tag/release has been performed. Do not merge to main or delete candidate branches without explicit owner approval.
>
> Active candidate branches are intentionally retained for review: `qual/q-cor03-seed-replay-2026-11-22`, `qual/q-cor04-live-fault-harness-2026-11-22`, `qual/mem004-retired-callback-guard-2026-11-22`, and `qual/phase-q-software-harnesses-2026-11-22`. The earlier Q-COR-02 branch is still present although its bounded harness is already merged. Pinex's temporary integration-test branch is `test/neta-go-qcor04-live-harness-2026-11-22`.

> **PHASE Q STEP 9 — ORD-EVID FLOAT-PATH AND STRICT JSON HARDENING MERGED (2026-11-22):** [PR #56](https://github.com/majiddarvishan/neta-go/pull/56) squash-merged to protected `main` at `b0dbd53799db5e481f7336a26fdb44a64f0bd803`. Adds integer-to-binary64 conversion enclosure (including >2^53 timestamps), production `fit_one` pivot-threshold guard, and a second outward-rounded interval evaluator for the production Gauss-Jordan/coefficients/residual/MSE/covariance/corner-CI float path. Where interval covariance/variance cannot prove the production path, it fails closed and retains closed-form diagnostics only; `continuous_interval_bound_proved=false` and `case_time_precision_proved=false` remain. Adds strict JSON parsing that rejects duplicate keys and NaN/Infinity for collector manifests, analyzer records/snapshots/comparison inputs and line-observer sidecars; parser helper SHA is bound in evidence. ORD-EVID synthetic suite **87/87 PASS**; PR Go CI, C++ Wire Compatibility and Parser Mutation PASS; postmerge main Go/C++ required checks PASS. Only `main` remains; merged feature branch cleanup SUCCESS. No Qualification package closes; all parent reports remain `DRIFT-INCONCLUSIVE`. No benchmark/A-A, stress, soak, extended fuzz, Reference Host admission, baseline/SLA, Performance Gate, memory PASS, public API/wire, v1.0.0 source or tag changes. Next: complete remaining software-only Q-COR-02/03/04 harnesses and MEM-004/005 synthetic lifecycle/sampling tests.

> **PHASE Q STEP 8 — ORD-EVID SAMPLING CADENCE INTEGRITY MERGED (2026-11-21):** [PR #54](https://github.com/majiddarvishan/neta-go/pull/54) squash-merged to protected `main` at `db267ebe0993f898a8ff10bf6dbd650f7c3e7e42`. Collector-recorded 100..5000 ms cadence is copied into every raw telemetry snapshot (and therefore the trace SHA), verified against the process record and across all 20 A/A runs. Per-run cadence statistics now use only gaps ending at scheduled `during` snapshots; immediate pre-spawn and final post-exit boundaries are excluded. The report includes median/p95/max scheduled gap and max-gap/recorded-interval ratio, with `acceptance_limit=NOT_ESTABLISHED` and `sampling_accuracy_proved=false`. Synthetic suite: **75/75 PASS**; PR Go/C++/bounded mutation checks PASS; merged feature branch cleanup SUCCESS and only `main` remains. Postmerge main Go and C++ required checks PASS; feature-branch cleanup SUCCESS and only `main` remains. No Qualification PASS or accepted sampling threshold is claimed. No A/A/QA-005 benchmark, stress, soak, extended fuzz, baseline/SLA, Performance Gate, memory PASS, API/wire, v1.0.0 source or tag change. Next: independently review continuous time-enclosure algebra/float equivalence and complete remaining ORD-EVID fail-closed cases before Q-COR harness work.

> **PHASE Q STEP 7 — ORD-EVID OBSERVER BACKPRESSURE ANALYSIS MERGED (2026-11-21):** [PR #52](https://github.com/majiddarvishan/neta-go/pull/52) squash-merged to protected `main` at `394352765679bea36c055a06efacaa10c6cba11d`. Source audit confirms the capture wrapper is an inline stdout-pipe forwarder; raw-log and sidecar writes occur in the reader path, so downstream stalls can backpressure child stdout. The report now exposes `observer_overhead.measurement_status=NOT_MEASURED`, `overhead_proved=false`, and `backpressure_possible=true`, with explicit read-bracket semantics. Synthetic suite: **71/71 PASS (3.372s)**; PR Go/C++/bounded mutation checks PASS; postmerge main Go and C++ required checks PASS; cleanup SUCCESS and only `main` remains. No overhead estimate or negligible-overhead claim. Actual observer-on/off measurement, scheduler perturbation and sampling accuracy remain Reference-Host work; E-UNKNOWN and DRIFT-INCONCLUSIVE remain. No benchmark/A-A/stress/soak/extended fuzz/baseline/SLA/Performance Gate/memory PASS/API-wire/v1.0.0 source or tag changes. Next: validate requested sampling interval provenance and report observed sample-gap distribution without inventing an acceptance threshold.

> **PHASE Q STEP 6 — CONTINUOUS CASE-TIME ENCLOSURE CANDIDATE MERGED (2026-11-21):** [PR #50](https://github.com/majiddarvishan/neta-go/pull/50) squash-merged to protected `main` at `f50c45eeab9cb3b370a4fb9c76c722d8de3910be`. Adds an outward-rounded interval enclosure over a conservative independent normalized-time box for the balanced-order OLS time coefficient and four joint 5m corner-CI envelopes. Synthetic suite: **68/68 PASS (3.212s)**, including all 1024 endpoint fits and 256 deterministic interior assignments; PR Go/C++/bounded parser mutation checks PASS; postmerge main Go and C++ required checks PASS. Merged-branch cleanup SUCCESS; only `main` remains. This remains a candidate pending independent production `fit_one` floating-point equivalence review: `continuous_interval_bound_proved=false`, `case_time_precision_proved=false`, E-UNKNOWN and DRIFT-INCONCLUSIVE remain. No host admission, A/A/QA-005, stress, soak, extended fuzz, baseline/SLA, Performance Gate, retained-memory PASS, public API/wire, v1.0.0 source or tag change. Next: characterize observer inline-pipe backpressure and sampling semantics without measuring or claiming overhead on an unqualified host.

> **PHASE Q STEP 5 — ORD-EVID TELEMETRY FAIL-CLOSED VALIDATION MERGED (2026-11-21):** [PR #48](https://github.com/majiddarvishan/neta-go/pull/48) squash-merged to protected `main` at `3e6596111d4f6faf3187b848cb5d898d0d551f7a`. Strict exact-type process/UTC clock validation, process/snapshot chronology, non-overlapping sample windows, exact sensor schema, partial sensor-map absence accounting, missing-sensor union consistency, boot-ID continuity and process-bounded line receipt UTC are integrated. Synthetic ORD-EVID suite: **62/62 PASS (3.701s)**; PR Go/C++/bounded mutation checks PASS; postmerge main Go and C++ required checks PASS; cleanup job SUCCESS and live branch list contains only `main`. This is evidence-integrity hardening only: E-UNKNOWN and DRIFT-INCONCLUSIVE remain; QENV-AA-02.ORD-EVID and Q-ENV-01 remain OPEN. No real A/A/QA-005, stress, soak, extended fuzz, host admission, baseline/SLA, memory PASS, Performance Gate, production API/wire, v1.0.0 source or tag change. Next: continue software-only observer/continuous time-uncertainty analysis; do not infer host qualification from synthetic tests.

> **PHASE Q STEP 4 — ORD-EVID CASE-TIME UNCERTAINTY SENSITIVITY MERGED (2026-11-21):** [PR #46](https://github.com/majiddarvishan/neta-go/pull/46) squash-merged to protected `main` at `30885bc90d1beea11573bde60fb8b4f7f8b793db`. The new report-only `qa005_ord_time_uncertainty.py` derives ten paired-case time intervals from verified pre-spawn/line-receipt bounds and sweeps all unique (2^{10}) endpoint assignments through the existing 5m fit; it reports slope ranges, design-condition maxima and four corner-CI envelopes. Synthetic ORD-EVID suite: **41/41 PASS (2.717s)**; PR Go/C++/bounded parser-mutation checks PASS; postmerge main Go and C++ required checks PASS. Merged-branch cleanup job SUCCESS; live branch list contains only `main`. The endpoint sweep is **not** a continuous interval bound: `continuous_interval_bound_proved=false`, `case_time_precision_proved=false`, all qualification remains `DRIFT-INCONCLUSIVE`, QENV-AA-02.ORD-EVID and Q-ENV-01 remain OPEN. No heavy QA-005/A/A, stress, soak or extended fuzz campaign, host admission, baseline/SLA, retained-memory PASS, Performance Gate, runtime Go/API/wire, v1.0.0 source or tag change. Next: investigate a defensible continuous time-uncertainty bound and independently characterize observer buffering/backpressure/overhead before any real A/A authorization.

> **PHASE Q STEP 3 POSTMERGE + PRE-SPAWN CLOCK CORRECTION (2026-11-21):** [PR #44](https://github.com/majiddarvishan/neta-go/pull/44) was squash-merged to protected `main` at `48773af7f44471652f4fd72b14712fe0ec546891`; 33/33 ORD synthetic tests, PR Go/C++/mutation checks PASS, required postmerge [Go](https://github.com/majiddarvishan/neta-go/actions/runs/44819697132) and [C++](https://github.com/majiddarvishan/neta-go/actions/runs/44819697141) SUCCESS, merged branch deleted. [PR #45](https://github.com/majiddarvishan/neta-go/pull/45) fixes an overstrict sidecar-window lower bound: parent post-spawn clock may follow a valid early observer receipt, so verified per-case envelope starts at the **pre-spawn** snapshot; an early-receipt synthetic 20-run fixture must remain DRIFT-INCONCLUSIVE. No heavy qualification or production Go change. ORD-EVID still OPEN, 18 normalized top-level items remain, numeric baseline/SLA not approved, Performance Gate DISABLED; next independent observer overhead / buffering and case-time sensitivity proof.

> **PHASE Q STEP 3 — ORD CASE-LINE RECEIPT INSTRUMENTATION (2026-11-21):** [PR #44](https://github.com/majiddarvishan/neta-go/pull/44) adds opt-in byte-for-byte output relay `qa005_ord_stream_capture.py`, SHA-256-bound per-line receipt-time sidecars, independent `qa005_ord_stream_verify.py` checks and synthetic fail-closed tests across the 20-run QA004 fixture; see [scope and limitations](NETA_GO_ORD_LINE_OBSERVER_PREP_2026-11-21.md). Original `go test` flags, workload fixtures, non-ORD path and product comparator are unchanged. **Case-line receipt is NOT case execution timing**; wide uncertainty, buffering/observer overhead, time proxy robustness, nonlinear drift, dedicated-host E-VALID and real A/A Mode qualification remain OPEN. No heavy benchmarks run, no runtime Go/wire changes, no baseline/SLA/retained-memory acceptance or Performance Gate. `DRIFT-INCONCLUSIVE` mandatory. 18 normalized top-level items remain: 9 Qualification, 7 Owner Decisions, 2 Release. Validate PR and postmerge Go/C++ CI before advancing; official `v1.0.0` remains immutable.

> **PHASE Q STEP 2 — QENV-AA-02.ORD-EVID REPORT-ONLY MODEL IMPLEMENTATION (2026-11-20):** [PR #43](https://github.com/majiddarvishan/neta-go/pull/43) adds standalone `scripts/qa005_ord_drift.py` with owner-approved joint 5m Bonferroni 95% mean+four-corner CI, exact source/fixture/log/trace provenance validation, 5/48/144 non-memory matrix checks, 10-pair actual process chronology and synthetic failure/order/time-bias tests; [model contract](NETA_GO_ORD_EVID_REPORT_ONLY_MODEL_2026-11-20.md). Existing comparator and default runner remain unchanged; model runs only when `NETA_QA005_ORD_EVID=1`. **Every result remains DRIFT-INCONCLUSIVE:** process timestamps are not individual benchmark-case timings, host E-VALID/nonlinear drift/observer accuracy/real A/A evidence unproven. ORD-EVID and Q-ENV-01 remain [ ] OPEN. Q-COR-01 [x] CLOSED; 18 top-level packages OPEN (9 Qualification, 7 Owner Decisions, 2 Release). No change to `v1.0.0` tags, Production Go, Source-V1, numerical baseline, SLA, retained-memory status or disabled Performance Gate. Next: finish PR #43 CI and exact-main merge verification, then address per-case timing precision under a separately justified non-perturbation method.

> **PHASE Q STEP 1 — EXACT RELEASE CORRECTNESS VERIFIED (2026-11-20):** **Q-COR-01 CLOSED** on immutable annotated `v1.0.0` commit `d8437f36ec812a596bada1398c7af9b530a18118`: [PR #41](https://github.com/majiddarvishan/neta-go/pull/41), [six-stage GA runner 44807019239 PASS](https://github.com/majiddarvishan/neta-go/actions/runs/44807019239), postmerge `main` `74872c649b9f525f5fb8338f80322e5b1491285b` [Go](https://github.com/majiddarvishan/neta-go/actions/runs/44807267236) + [C++ wire](https://github.com/majiddarvishan/neta-go/actions/runs/44807267191) both SUCCESS. Merged Q-COR branch deleted by exact-SHA guard. ORD-EVID is being prepared separately in [PR #42](https://github.com/majiddarvishan/neta-go/pull/42), opt-in source/fixture-bound process timing and continuous sampled environmental telemetry with synthetic tests; **not** sufficient per-case timing/model, E-VALID or DRIFT-VALID. Canonical remaining **18 = 9 Qualification + 7 Owner Decisions + 2 Release**. Keep Q-ENV-01 / QA-004/005 / MEM-004/005/006 OPEN; `retained-attributed-B` INCONCLUSIVE, Performance Gate DISABLED, numerical baseline/SLA unapproved, immutable source and release tags unchanged. Next: complete ORD-EVID evidence accuracy/statistical diagnostics then prepare Q-COR-02/03/04 only under their separate heavy-run limits.

> **OFFICIAL v1.0.0 GA TAG + RELEASE VERIFIED — 2026-11-20:** [Decision §86](DECISION_LOG.md), [GA evidence](GA_RELEASE_VERIFIED_2026-11-20.md): official annotated tag `v1.0.0` object `b5c5ce7b9fe6c3ea4fceec0eb98a4621b749e28b` peels to source SHA `d8437f36ec812a596bada1398c7af9b530a18118`; [GitHub Release](https://github.com/majiddarvishan/neta-go/releases/tag/v1.0.0) published as non-prerelease, exact-SHA Go, C++ and publisher jobs SUCCESS. Immutable `v1.0.0-rc.1` unaffected. **P9-06 [x] CLOSED under owner GA publication override; 19 main open work packages remain (10 Qualification+7 decisions+2 Release R-01/R-02)**. Full Q-ENV-01/QA-004/005/MEM-004/005/006 and Q-COR qualification remains OPEN/INCONCLUSIVE, performance gate DISABLED, no numeric SLA or retained-memory proof. After GA-evidence PR merge, [cleanup workflow](../.github/workflows/cleanup-merged-release-branches.yml) may delete only the 13 known unchanged merged PR heads; verify outcome before declaring Branch cleanup complete. Future `main` documentation updates must NOT move official tags.

> **OFFICIAL v1.0.0 OWNER-APPROVED PUBLICATION — 2026-11-20:** [Decision §85](DECISION_LOG.md) supersedes the previous publication hold and directs **official `v1.0.0` Tag and non-prerelease GitHub Release** for the same library code as already-verified `v1.0.0-rc.1`. Release preparation occurs on `release/v1.0.0-ga-2026-11-20`: VERSION/changelog/readme/release notes/decision log plus a narrowly scoped exact-main GA publisher and merged-PR branch cleanup workflow. **Do not claim completion until actual GA tag and Release API evidence.** Owner also authorized cleanup of **11 prior merged docs/release branch heads** plus new release documentation branches after GA verification, with PR merge and unchanged SHA checks. Full Phase Q has NOT passed (Q-ENV-01, QA-004/005, MEM-004/005/006 and Q-COR remain OPEN/INCONCLUSIVE); owner overrides publication hold, NOT test correctness. Source code/benchmarks/Go API/wire remain unchanged; Performance Gate DISABLED. The existing v1.0.0-rc.1 tag must not move. [Parallel test schedule](NETA_GO_PHASE_Q_PARALLEL_EXECUTION_PLAN_2026-11-20.md) unchanged.

> **RC-01 VERIFIED TAG PUBLISHED — 2026-11-20:** [Decision Log §84](DECISION_LOG.md) independently confirms annotated Git tag **`v1.0.0-rc.1`**, tag-object SHA `1e07c00f97b6243f932aba91c544f81b73e6fc9d`, target source commit `0bd50760a9200194f9ae0088d26751d0f6ee00c7` (release PR #37). Both required protected-main Go + pinned C++ checks and tag-publisher workflow **SUCCESS on the exact source SHA**; no open PRs after publication. `go get github.com/majiddarvishan/neta-go@v1.0.0-rc.1` now pins that immutable integration RC; a later docs-only main update does not move tag. **RC-01 [x] CLOSED**; final `v1.0.0` R-01/R-02/P9-06, 10 Qualification and 7 decisions remain OPEN (20), retained-attributed memory INCONCLUSIVE and Performance Gate DISABLED. [W1–W4 parallel test plan](NETA_GO_PHASE_Q_PARALLEL_EXECUTION_PLAN_2026-11-20.md) is filed but heavy Phase Q and source instrumentation remain separately gated. This entry supersedes pre-publication status above.

> **INTEGRATION RC + PARALLEL QUALIFICATION PLAN — 2026-11-20:** Owner requested an immediately pinnable version/tag for other Go applications while preserving independent Phase Q qualification. [Decision §83](DECISION_LOG.md) scopes this as **`v1.0.0-rc.1` (pre-qualification RC)**, not final GA. Preflight protected `main` `a53c90c1df5e353bb2effc5868a7e345c4077d21` has **zero open PRs**. Current release-preparation branch `release/v1.0.0-rc.1-candidate-2026-11-20` adds VERSION, candidate notes, readme usage, a one-shot exact-green-SHA annotated tag publisher and [four-week parallel Phase Q test plan](NETA_GO_PHASE_Q_PARALLEL_EXECUTION_PLAN_2026-11-20.md). **Do not claim tag creation until GitHub refs verify it**; PR and postmerge checks and tag collision must be verified. Keep 20 main OPEN packages, MEM-004/005 INCONCLUSIVE, Performance Gate DISABLED and separate final v1.0.0 release gate. No heavy benchmark, production/API/CI performance-gate, numeric SLA or host acceptance authorized by this planning action.

> **QENV-AA-02.ORD OWNER OPTION A APPROVED — 2026-11-20:** [Binding order/time statistical contract](NETA_GO_QENV_AA_ORDER_DRIFT_POLICY_2026-11-20.md) and [Decision Log §82](DECISION_LOG.md) establish 10 same-SHA pairs with a **joint 5m Bonferroni 95% simultaneous original mean+four order/time corner CI** within the previously approved d=5%/7.5%, no new margin. Owner choice A **CLOSED as statistical policy**, distinct **QENV-AA-02.ORD-EVID [ ] OPEN**: exact timestamps, case-time uncertainty, CPU/thermal/frequency/PSI/cgroup/swap evidence, model diagnostics and future separately authorized runner changes. The current deterministic alternation and host before/after snapshots do NOT qualify a mode. Q-ENV-01 OPEN, `DRIFT-INCONCLUSIVE` pending evidence, no code/Phase-Q heavy run/host/Mode admission/numeric baseline/SLA/release/Gate; 20 top-level open packages unchanged.

> **QENV-AA-02 OWNER OPTION A APPROVED — 2026-11-20:** [Statistical contract](NETA_GO_QENV_AA_EQUIVALENCE_POLICY_2026-11-20.md) and [Decision Log §81](DECISION_LOG.md) fix *new, prospective, symmetric same-SHA A/A measurement-noise margins*: **5%** for QA-005 throughput/P50/P95 and **7.5%** for QA-005 P99/CPU/op/allocs/op plus QA-004 internal terminal-settlement P99; evaluate per Mode with 10 paired runs and Bonferroni simultaneous 95% paired-log intervals (QA004=5, Core=48, Full=144 case-metrics). QENV-AA-02 policy/margin subdecision **CLOSED**; **QENV-AA-02.ORD statistical rule is now [x] CLOSED under Option A (§82)**; ORD-EVID remains [ ] OPEN for order/time evidence and actual measurement validation. Parent Q-ENV-01 still OPEN, Modes and physical host NOT ADMITTED, existing one-sided comparator/runner unchanged, heavy Phase Q not authorized, memory metric INCONCLUSIVE, numerical baseline/SLA not approved, Performance Gate DISABLED; 20 top-level open packages unchanged and Source-V1 immutable anchor unchanged. Next: separately authorize any needed ORD-EVID tooling; establish actual host/toolchain inventory, then obtain permission for controlled measurements.

> **QENV-AA-01 OWNER CHOICE CLOSED — 2026-11-20:** **Option B approved**, fail-closed **per-mode** reference-host admission for `qa004`, `core`, `full` separately ([Decision Log §80](DECISION_LOG.md), [decision contract](NETA_GO_QENV_AA_ADMISSION_DECISION_2026-11-20.md)). Dedicated host E-VALID preflight must precede each mode; every applicable non-memory case/metric and order-drift/symmetric-equivalence criterion must pass once prospectively approved. Current 10-pair 95%-Bonferroni comparator `PASS` is one-sided *non-regression* only, not an equivalence proof; no new numeric bounds, host, mode, source numeric baseline or SLA approved. **Q-ENV-01 still OPEN**; no heavy Phase-Q permission. 20 open top-level packages unchanged. OD-ENV-01=A, OD-MEM-01=A, memory INCONCLUSIVE, Gate DISABLED and source anchor preserved. The owner decision is recorded on the independent docs branch `docs/qenv-aa01-owner-b-2026-11-20` for PR/review.

> **PHASE-Q HOST AND MEMORY ADMISSION DESIGN — 2026-11-20:** Created [Q-ENV-01 / MEM-004/005 admission specification](NETA_GO_PHASE_Q_HOST_MEMORY_ADMISSION_SPEC_2026-11-20.md) using verified protected `main` `0c01ac27bdffd9031f59b3ae466823f036839cf5` as the documentation review checkpoint. It proposes dedicated Linux host/toolchain/governor/thermal/swap admission evidence, ten-pair Core/Full/QA004 A/A metric review, F1–F5/M1/D1 allocation/ownership/simultaneous-peak and missed-short-peak proof, and three-mode observer overhead validity. **PROPOSED, not automatically accepted:** specific host identity/Go patch, all-applicable-metric A/A filter, numeric observer overhead/error bounds still require explicit owner review; no tests/benchmarks run, no source or runner changes. OD-ENV-01=A and OD-MEM-01=A remain the only approved policy choices; **20 unique open packages = 10 Qualification + 7 other Owner Decisions + 3 Release**, gate DISABLED. See [Phase-Q backlog](NETA_GO_PHASE_Q_EXECUTION_BACKLOG_2026-11-20.md) and [TASKS](TASKS.md).

> **OWNER POLICY UPDATE — 2026-11-20:** Two choices approved: **OD-ENV-01=A** (use dedicated, controlled reference host; exact host/governor/Go/toolchain and A/A acceptance still OPEN in Q-ENV-01) and **OD-MEM-01=A** (fail-closed retained-attributed-B stays INCONCLUSIVE without complete category ownership, alias/lifetime, simultaneous peak and time/overhead validity; existing M1/D1 incremental Option B preserved). [Decision Log §79](DECISION_LOG.md), [TASKS](TASKS.md), [Phase Q backlog](NETA_GO_PHASE_Q_EXECUTION_BACKLOG_2026-11-20.md). **20 packages remain: 10 Qualification + 7 other owner decisions + 3 Release**. No permission for heavy testing, new baseline, metric qualification, mandatory gate, source anchor change or release.

> **CURRENT GITHUB HANDOFF — 2026-11-20 (reconciled from live protected `main` `bd8421cf3cabc5cb72263ed964434a48bf54ef22`):** [PR #24](https://github.com/majiddarvishan/neta-go/pull/24) integrated QA-007 and Phase D 16/16; [#25](https://github.com/majiddarvishan/neta-go/pull/25) aligned release-readiness docs; [#26](https://github.com/majiddarvishan/neta-go/pull/26) added an early multi-peer router and [#27](https://github.com/majiddarvishan/neta-go/pull/27) generalized it into `server-peer-router` + `client-peer-router` and added `WithClientOnRequestHandler` with V1/V2 TCP validation. All four are **MERGED**. There are **14 runnable example commands** (historical Phase-D fast smoke tested its original 12; do not misattribute it to the extra two). On exact current `main`, required [Go 44630477642](https://github.com/majiddarvishan/neta-go/actions/runs/44630477642) and [C++ wire 44630477596](https://github.com/majiddarvishan/neta-go/actions/runs/44630477596) checks **SUCCESS**. QA-007 CLOSED; QA-004/QA-005 and MEM-004/005/006 OPEN/INCONCLUSIVE. **No new reference-machine, 10-pair benchmark, canonical `retained-attributed-B`, 30-minute soak, or absolute SLA was qualified by this documentation update.** Mandatory Performance Gate **DISABLED**; `QA004-QA005-SOURCE-V1` immutable SHA `9b7b2318f73d173a99d22489042f84f8ce58b745` unchanged; no `v1.0.0` tag/release authorized. Canonical active status: [TASKS](TASKS.md). Unique outstanding packages: **22 = 10 Qualification + 9 Owner Decisions + 3 Release**, with exact acceptance/dependencies/reference host requirements in [Phase-Q backlog](NETA_GO_PHASE_Q_EXECUTION_BACKLOG_2026-11-20.md). Historical prior-branch/no-PR restrictions below apply only to their dated checkpoints. This reconciliation uses independent documentation commits on `docs/task-reconciliation-phase-q-2026-11-20`.

> **TASK LEDGER RECONCILIATION — 2026-11-19:** Final cross-file audit identified only DEV-01/02/03 stale `[ ]` markers in the detailed Phase-D backlog, despite prior independent GitHub evidence and `TASKS.md` completion. Corrected exactly these three document checkboxes, linking to source audit/category/compatibility evidence. All 16 DEV/EX statuses now align in `TASKS.md` and the detailed backlog. No runtime/benchmark/API changes. `DEV_READY_FOR_QUALIFICATION` technical sign-off remains valid; heavy Q still not authorized.

> **PHASE D TECHNICAL DEVELOPMENT COMPLETE — DEV_READY_FOR_QUALIFICATION (2026-11-19):** `DEV 6/6 DONE + EX 10/10 DONE = 16/16` in [TASKS](TASKS.md). **BLOCKED eligible Phase D: 0** (distinct owner-gated PV/Q/Release decisions explicitly excluded from Phase D). See [formal owner-reviewable closeout](NETA_GO_DEV_READY_FOR_QUALIFICATION_2026-11-19.md) and [example evidence](NETA_GO_DEV_04_05_EXAMPLES_LIGHT_VALIDATION_2026-11-19.md). Last reviewed feature content `5c31494dea16b8f6aed600ff438604aaa7ca3609`; 12 runnable Client/Server public-API examples, unchanged originals, 10 independently committed new commands, strict config and bounded CI. Three real lightweight CI runs PASS, latest [44542311954](https://github.com/majiddarvishan/neta-go/actions/runs/44542311954) including real reconnect and negative cases. 71 production/examples Go+script paths have identical blob SHA to tested CI snapshot. Comparison against initial Feature HEAD `a58d2bb...` shows 24 additional commits and 35 files (mostly examples/docs), **zero production/root Go, Wire, QA reference, source anchor or original smoke modifications**. No new baseline, 30m soak, 10 matched pairs, long fuzz/stress or full race; QA-004/005 and MEM-004/005/006 still OPEN/INCONCLUSIVE; `retained-attributed-B` not qualified. Performance Gate DISABLED. **Do not launch heavy Phase Q, PR, Merge, Tag or Release without new owner authorization.** Temporary fast-CI ref `ci/neta-go-examples-fast-2026-11-19` exists solely for isolated non-heavy validation; do not merge it.

> **PHASE D 15/16 COMPLETE — DEV-04/05 + TEN EXAMPLES VERIFIED (2026-11-19):** **DEV 5/6 DONE, EX 10/10 DONE, BLOCKED eligible DEV 0; DEV-06 pending.** Ten new stdlib/public-API commands added by separate implementation commits to the requested Feature branch, joining unchanged `examples/client` and `examples/server`. No production/wire changes. DEV-04 `scripts/examples-dev-smoke.sh` builds 12 commands, executes focused example unit tests, 12 bounded positive/negative loopback pairs, real abrupt Server kill/restart and second Client OnBound. CI [44540355649](https://github.com/majiddarvishan/neta-go/actions/runs/44540355649), [44541733512](https://github.com/majiddarvishan/neta-go/actions/runs/44541733512) and final [44542311954](https://github.com/majiddarvishan/neta-go/actions/runs/44542311954) independently PASS with format/vet/build/smoke. **Git tree SHA equality checked for 71 tracked Go/script paths** between Feature `807f60968e2ef48c07c64820ae6972bde82e417b` and fully formatted tested CI `af013c9c1fefd4fbab937d8e9178f00dd9d9cd0a`. DEV-05 `examples/README.md`, sample JSON, root README and docs/API/CONFIGURATION updated. See [evidence matrix](NETA_GO_DEV_04_05_EXAMPLES_LIGHT_VALIDATION_2026-11-19.md). Tests ran only on isolated CI branch to avoid automatic heavy QA workflows on Feature; original CI/scripts untouched except additive scoped fast workflow. MEM-004 canonical metric, full QA-004/005 qualification, Q/race/fuzz/soak, numeric gate and PR/Merge/Release remain OPEN/unauthorized. **Next DEV-06 closeout only; no heavy tests.**

> **DEV-03 COMPLETE — EXISTING EXAMPLE COMPATIBILITY (2026-11-19):** [DEV-03 frozen contract](NETA_GO_DEV_03_EXAMPLE_COMPATIBILITY_CONTRACT_2026-11-19.md) preserves `examples/client` flags `-addr/-system-id`, `examples/server` `-listen`, output tokens and `scripts/example-smoke.sh` coverage/loopback/Stop expectations. Production/client/server example sources unchanged in feature-vs-main compare. Historic [run 44529571646](https://github.com/majiddarvishan/neta-go/actions/runs/44529571646) Go verify and paired smoke step independently SUCCESS; no fresh Go build/test for this docs-only freeze. New configs are separate packages, stdlib only; lightweight all-examples build/smoke is DEV-04. Phase D **DEV 3/6, EX 0/10; 13/16 remain**. Next EX-C01 + EX-S01.

> **DEV-02 COMPLETE — BOUNDED HYBRID-B IMPLEMENTATION SCOPE 2026-11-19:** [F1–F5/M1/D1 category-by-category matrix](NETA_GO_DEV_02_HYBRID_B_CATEGORY_MATRIX_2026-11-19.md) reviewed against production source, V9 F1–F5, V10–V12 pending/D1, V13–V16 Worker/Queue and V17–V18 Client freeze evidence. Existing test-only overlays produce partial diagnostics with prior CI, NOT canonical attributable retained peak. Each missing category has explicit EXCLUDED/INCONCLUSIVE disposition and an external qualification/ownership prerequisite; no additional production hot-path instrumentation or V19 tool churn was authorized. **DEV-02 classification done does NOT close MEM-004/005/006** or change benchmark/source SHA, reference qualification or gate. No fresh tests for doc-only commit. Phase D **DEV 2/6, EX 0/10; 14/16 remain**. Next DEV-03.

> **DEV-01 COMPLETE — SOURCE AUDIT 2026-11-19:** Inspected live HEAD `a58d2bb50fe5f8d09d1a700f50f5b37d512b5ed1`, main `24b7c5f6eb4e001f30dd8a564a337ca1f506eac8`, compare 119 ahead/0 behind, 13 modified production Go files, existing examples/CLI/smoke and relevant protocol/API/QA contracts. New [DEV-01 evidence](NETA_GO_DEV_01_PRODUCTION_API_AUDIT_2026-11-19.md). No confirmed new in-scope production behavior defect identified by static review; important public documentation drift (Session.Diagnostics, Server.AcceptDone/AcceptErr, panic-diagnostic options and credit-backed OnClose) assigned to DEV-05. MEM-004 F1–F5/M1/D1 remains DEV-02 *measurement implementation classification*, not a request for indefinite overlay revisions; true retained-attributed-B, peak gap/overhead and Q benchmarks remain OPEN. No tests run for this documentation-only audit, no performance gate/release. Phase D tally **DEV 1/6 DONE, EX 0/10 DONE**, 15/16 outstanding. Next DEV-02.

> **CURRENT OWNER PRIORITY — DEVELOPMENT FIRST (2026-11-19):** User wants all **authorized** development tasks finished **before** the heavy qualification/test phase, with substantially more runnable examples and Client/Server configuration samples. Canonical [DEV/EX Phase D backlog](NETA_GO_DEVELOPMENT_FIRST_EXAMPLES_BACKLOG_2026-11-19.md) and [16 new task checkboxes in TASKS](TASKS.md), recorded in [DECISION_LOG §78](DECISION_LOG.md). Existing only two example commands `examples/client` and `examples/server` must remain backward compatible, including `scripts/example-smoke.sh`. Target 5 **new** Client executables (config flags/JSON; bounded parallel Requests; reconnect; explicit V1; diagnostics) and 5 **new** Server executables (config flags/JSON; Bind allowlist; bounded multi-Session; V1-only; diagnostics), total **12** runnable programs. 6 DEV workstream tasks cover real feature-vs-main implementation audit, bounded MEM-004 code completeness, example compatibility, lightweight deterministic example smoke, docs and DEV-ready handoff. Do NOT start full benchmark/race/fuzz/soak/10-pair qualification during Phase D; focused builds/unit/loopback checks are permitted to make implemented tasks verifiable. No new library API or external dependency solely for example config. Unapproved PV-02/04/05 negotiation, protection changes, owner release-note approvals and PR/Merge/Tag/Release remain separate decision/release boundaries. **This response only extracted/planned tasks: no new production/example code or heavy tests run.** Original QA004-QA005 Source-V1 `9b7b2318f73d173a99d22489042f84f8ce58b745` unchanged, performance gate DISABLED. At each follow-up report completed DEV/EX tasks, remaining true code tasks, owner blockers and postponed Q, rather than number of commits.

> **LATEST QA-005 MEM-004 CLIENT GENERATION V17/V18 VERIFIED (2026-11-19):** Latest code commit `ef117e38da1b2e2ca73b174d33ecaa902d21ba83`, latest [Client freeze evidence](NETA_GO_QA005_CLIENT_GENERATION_FREEZE_V17_V18_EVIDENCE_2026-11-19.md). V17 `c8cf0467` added test-only Client.mu frozen Client.generation/current pointer registry, rejects active Connect at freeze, stopped Client and epoch/pointer changes after freeze (including ephemeral reconnect between sample ticks). Adds untouched `client_connect.go` and `client_lifecycle.go` source SHA to mandatory original/effective pinned-source parity. Historical [CI 44528814317](https://github.com/majiddarvishan/neta-go/actions/runs/44528814317) overall green but optional FAIL from obsolete exact Python worker_scheduler-last-file assertion; fixed in independent commit `3fe01bb2`. [V17 CI 44529067306](https://github.com/majiddarvishan/neta-go/actions/runs/44529067306) **all three jobs/four optional stages PASS**: 19 Python anchored overlay tests, Go lifecycle -race, 6 Python parity tests, pinned baseline Go -race and short 3-mode overhead preview. V18 adds actual loopback TCP Client reconnect test (old Session Forced Close, Done, Client.Connect with new Bound generation, old observed window must reject sampled bytes and HWM). [V18 CI 44529571646](https://github.com/majiddarvishan/neta-go/actions/runs/44529571646) PASS all required jobs and four optional stages, 20 Python overlay and 6 Python parity tests; real Go -race reconnect PASS. Fixed Source-V1 SHA `9b7b2318f73d173a99d22489042f84f8ce58b745` and original Go files unchanged. Critical exclusions: earlier retired Client generations with callbacks already alive BEFORE freeze, frozen registry's own heap/GC liveness effect, sequential cross-owner sampling and missing M1/D1 structures. NO canonical `retained-attributed-B`, NO accepted 10 paired overhead/reference or numeric performance gate; 25x hosted preview `FEASIBILITY_ONLY_INCONCLUSIVE`. **MEM-004/005/006 QA-004/005 OPEN; QA-007 CLOSED; Gate DISABLED; no PR/merge/tag/release.**

> **LATEST QA-005 MEM-004 M1 WORKER QUEUE V13–V16 (2026-11-19):** Latest code `4a133d83bbddc21ebd69ba231769039126c19033`. New [M1 Worker/Queue evidence](NETA_GO_QA005_M1_WORKER_QUEUE_V13_V16_EVIDENCE_2026-11-19.md) records four independently validated test-only adapters. V13 [CI 44524558066](https://github.com/majiddarvishan/neta-go/actions/runs/44524558066): pool.mu snapshots with owner/pool/queue/backing identity dedup, retained Task-slice capacity × `sizeof(callbackTask)`, `callbackSessionQueue` static bytes, Worker/lane counts; fail closed corrupt head/alias. V14 [CI 44525104589](https://github.com/majiddarvishan/neta-go/actions/runs/44525104589): `worker_scheduler.go` original/effective SHA now mandatory for exact Source-V1 compatibility, source file remains untouched. V15 [CI 44525522696](https://github.com/majiddarvishan/neta-go/actions/runs/44525522696): callbackWorker static object bytes × observed workerCount, overflow-safe, 2 Workers/96 Go logical struct B in 1x hosted smoke, excludes stack/channel/timer/runtime. V16 [CI 44525968814](https://github.com/majiddarvishan/neta-go/actions/runs/44525968814): actual blocked callback + second queued, verifies backing/Queue release and idle Worker retirement under -race. Each of four CI runs PASS all 3 required jobs AND all 4 separately checked optional stages. V16 18 Python overlay, 18 Go -race lifecycle, 5 Python Source Anchor compatibility and pinned Go -race PASS. Hosted three-mode 25x overhead `FEASIBILITY_ONLY_INCONCLUSIVE`; two samples with observed Queue slots=0 do NOT prove no Queue allocations. Original code/SOURCE-V1 anchor `9b7b2318f73d173a99d22489042f84f8ce58b745`, historical 370 rows unchanged. `retained-attributed-B` unissued; M1 Map buckets/other structs, D1 other rendered diagnostic text, client-generation completeness, global peak timing and overhead/soak remain OPEN. **MEM-004/005/006, QA-004/005 OPEN; QA-007 CLOSED; Performance Gate DISABLED; no PR/merge/tag/release.**

> **LATEST QA-005 MEM-004 M1/D1 OPTION B — V10–V12 VERIFIED (2026-11-19):** Source-v1 `9b7b2318f73d173a99d22489042f84f8ce58b745` fixed. [Decision §77](DECISION_LOG.md) documents owner-approved incremental neta-owned M1/D1 scope, excluding raw user graphs and runtime. V10 code `b2ad2803e18ddcc2f1e30fccd139ccaca549c8ab`, [Actions 44510555448](https://github.com/majiddarvishan/neta-go/actions/runs/44510555448) all three jobs and all optional stages PASS: D1 unique Panic stack text length from `string(debug.Stack())`, deduplicated by `PanicRecord.Sequence` across First/Recent/OnClose, source+adapter parity. V11 code `edbf5ea0963ef634c6759134cc4c6ff7b6feb6e5`, [Actions 44511176165](https://github.com/majiddarvishan/neta-go/actions/runs/44511176165) PASS: test-only M1 pendingRequest identity live until Completion return/cancel even after Done/map reset, fail-closed missing admission/duplicate release; *count only*. V12 code `b97949242188704b35f29422a8a6c9919de4614c`, [Actions 44511644311](https://github.com/majiddarvishan/neta-go/actions/runs/44511644311) PASS all three jobs and optional overlay, Source Anchor compatibility, and unqualified three-mode A/A preview. V12 reports `probe-m1-pending-struct-logical-peak-B`: `unsafe.Sizeof(pendingRequest{})` × unique still-owned count, overflow checked; **40 B** for one pending in a 1x Core RR hosted-runner smoke is Go struct footprint, NOT allocator bytes or a qualified total. Go -race lifecycle V10–V12 all PASS; Python anchored overlay tests 12, 13, 14 respectively; parity Python 4 each. D1 without Panic returns sampled zero (no claim of total D1 memory), and neither independent D1/M1 peaks nor F1–F5 can be summed to a simultaneous global maximum. V12 MEM-005 three 25x samples `FEASIBILITY_ONLY_INCONCLUSIVE`; source tree and historic 370 rows unchanged. **MEM-004/005/006 and QA-004/005 OPEN, QA-007 CLOSED, Performance Gate DISABLED, no PR/merge/tag/release.**

> **OWNER DECISION QA-005-MEM-004 M1/D1 SCOPE B (2026-11-19):** Owner explicitly selected **B** from the preceding M1/D1 audit: incremental attribution restricted to neta-created M1 metadata and internally rendered D1 storage with unique ownership, alias dedup and lifecycle proof. Raw recovered foreign graphs, user closure captures, goroutine stacks and allocator/runtime costs remain excluded. Only test-only adapter experiments and independent commits in current branch; Source-V1 `9b7b2318f73d173a99d22489042f84f8ce58b745` immutable. Numeric definition, sampling, overhead and full coverage still INCONCLUSIVE; no performance gate, PR/merge/tag/release. [Decision §77](DECISION_LOG.md), [audit](NETA_GO_QA005_M1_D1_OWNERSHIP_SCOPE_AUDIT_2026-11-19.md).

> **LATEST QA-005 M1/D1 OWNERSHIP SCOPE AUDIT (2026-11-19):** Source review of `diagnostics.go`, `session_internal.go`, `types.go`, `resource_ledger.go` identified M1 map/queue/Task lifetime/alias risks and D1 First/OnClose/Recent strings plus raw recovered reference graphs. The bounded `recentBytes` budget does NOT cover First/OnClose or raw retained graphs; these are not reliable actual-memory figures. New [M1/D1 ownership scope audit](NETA_GO_QA005_M1_D1_OWNERSHIP_SCOPE_AUDIT_2026-11-19.md) documents direct evidence, test-only next steps and scope A/B/C **without selecting any new owner policy**. V9 remains `QA005-OWNED-BUFFER-OVERLAY-V9-UNQUALIFIED`; fixed source anchor unchanged, MEM-004/005/006 OPEN, Performance Gate DISABLED.

> **LATEST QA-005 MEM-004G F5 INBOUND BIND / V9 CATEGORY RECONCILIATION (2026-11-19):** Latest code commit `7c043cac141da88755ab5ae1dfd0cb3769337569`, [Actions 44490084898](https://github.com/majiddarvishan/neta-go/actions/runs/44490084898) PASS all three jobs AND 4 individually inspected optional stages. V8 introduced test-only F5 unreserved inbound Body backing-slice ownership in `readFrame` (not a policy reservation), under Session.mu from allocation through immediate read-error rollback or `handleInboundFrame` return. The deterministic net.Pipe Bind Request test exercises both successful receive/handler error and truncated Body error, without changing Production source. V9 adds fail-closed `qa005OwnedConsistentLocked`: sum of F1–F5 category bytes must equal `qa005OwnedTotal` under the SAME Session mutex before sample/HWM acceptance. Silent-inconsistent-category Go test confirms rejection. V9 CI evidence: 11 Python overlay tests, 12 Go lifecycle tests under -race, 4 Python exact Source-V1 adapter tests and pinned-source Go -race, 5 Python unqualified overhead-parser tests plus three 25x scenario modes; status `FEASIBILITY_ONLY_INCONCLUSIVE`. Earlier [Actions 44489743062](https://github.com/majiddarvishan/neta-go/actions/runs/44489743062) V8 PASS after anchored Python fixture correction. Preserve two prior overall-green but optional-FAIL runs [44488997407](https://github.com/majiddarvishan/neta-go/actions/runs/44488997407) and [44489465368](https://github.com/majiddarvishan/neta-go/actions/runs/44489465368) from stale synthetic fixtures and incorrect Header-vs-Body ReadFull assertion; standalone corrections 0c0dcca0, 538eb70d. New ownership categories still PARTIAL_INCONCLUSIVE; F4 Bind pre-Session allocations, M1 metadata/queues/maps/Worker records, D1 diagnostic strings/foreign graphs and runtime allocation overhead remain outside verified attribution. Source-V1 SHA `9b7b2318f73d173a99d22489042f84f8ce58b745` and original Go sources unchanged. No retained-attributed-B emitted, no new performance SLA/gate, no 370-row rerun, PR/merge/tag/release. **MEM-004/005/006 and QA-004/005 OPEN; QA-007 CLOSED.**

> **LATEST QA-005 MEM-004F / MEM-005 INITIAL THREE-MODE OVERHEAD (2026-11-19):** V7 frozen Session registry now checks an admission epoch under Server.mu; even a Server Session added AND removed between observations invalidates measurement, rather than appearing as false zero. Code `6a38a331aa43f99ba04794dddeab391f9db5c5bc` [Actions 44486113768](https://github.com/majiddarvishan/neta-go/actions/runs/44486113768) PASS three jobs, optional owned-buffer stage and pinned source compatibility independently checked; 9 Python overlay tests, 10 Go overlay -race lifecycle tests, 4 Python compatibility tests and pinned-source Go -race. Two preceding green workflows contained **failed optional** V7 stages: [44485521207](https://github.com/majiddarvishan/neta-go/actions/runs/44485521207) failed on a strict tab anchor; [44485822929](https://github.com/majiddarvishan/neta-go/actions/runs/44485822929) failed because the test incorrectly attempted to reinitialize the frozen identity registry. Fixes are independent `dc692f8a`, `6a38a331`. For MEM-005, `scripts/qa005_overhead_advisory.py` and 5 strict parser tests run exactly three one-off `25x` Core RR-64B-S1-C1-medium variants at same source SHA: native 37486 ns/op, overlay+sampler OFF 41786 ns/op, overlay+sampler ON 35932 ns/op. Run [44486737303](https://github.com/majiddarvishan/neta-go/actions/runs/44486737303) at `fbadb55124193b5da45172071cd29ff80bbb1162` PASS all jobs and *all* optional steps. Very short, unpaired hosted CI data can show misleading negative incremental sampler overhead: result is explicitly `FEASIBILITY_ONLY_INCONCLUSIVE`, not performance PASS, no 10 matched pairs, no approved host, no thresholds. [44486575046](https://github.com/majiddarvishan/neta-go/actions/runs/44486575046) zero-job YAML FAILURE from literal replacement of `$'`, fixed via callback-safe insertion from good workflow in fbadb551. Memory category F1–F4 still partial, M1/D1 and unclassified allocations missing. MEM-004/005/006 OPEN; QA-004/005 OPEN; QA-007 CLOSED. Baseline Source-V1 `9b7b2318f73d173a99d22489042f84f8ce58b745`, prior 370 rows and original Go production sources unchanged. Performance Gate DISABLED, no PR, merge, tag or release.

> **LATEST QA-005-MEM-004E V6 SOURCE-ANCHOR ADAPTER COMPATIBILITY (2026-11-19):** At code SHA `629772e238a89110009c9596b61f02c67596c945`, [Actions 44426946019](https://github.com/majiddarvishan/neta-go/actions/runs/44426946019) PASS all three jobs AND optional owned-buffer and exact-source-anchor compatibility steps individually. Source-V1 immutable `9b7b2318f73d173a99d22489042f84f8ce58b745` was fetched into a clean detached temporary worktree, compared against candidate using the SAME V6 test-only adapter; 4 Python compatibility tests and historical-source Go -race overlay tests PASS. Seven source/benchmark files and effective file hashes match, including source fixture SHA256 `6a3adf62a50508f5c5aef8ac6e062176523d20e9fae95c11e225bf1e1e937172` and effective fixture SHA256 `6de7a16cfd40f998d023d25b29af2712a949749fc3a657366895482f2f4ea94f`. Scope: **SOURCE/ADAPTER COMPATIBILITY ONLY**, not numerical baseline or eligible memory metric. A prior [Actions 44426784337](https://github.com/majiddarvishan/neta-go/actions/runs/44426784337) had malformed YAML / zero jobs; repaired from known-good YAML at 629772e2, retain failure evidence. V4 [44425666635](https://github.com/majiddarvishan/neta-go/actions/runs/44425666635) 6 Python + 8 Go -race PASS; V5 [44425989651](https://github.com/majiddarvishan/neta-go/actions/runs/44425989651) 7 Python + 9 Go -race PASS; V6 [44426342867](https://github.com/majiddarvishan/neta-go/actions/runs/44426342867) 8 Python + 9 Go -race PASS. V6 adds prequeue F4 Unbind/Enquire tracking, Session identity dedup, explicit PARTIAL_INCONCLUSIVE category manifest, and sampled max-gap/snapshot-duration diagnostics. Latest 1x at 629772e2: sampled peak **0 B** (2 samples), per-Session HWM upper **212 B**, max sample gap **202518 ns**, max snapshot duration **661 ns**. All are unqualified diagnostics. F4 Bind/other pre-queue path, M1/D1 metadata and external graphs, transient unknown storage, sample density/overhead and 10 paired runs remain OPEN. No emitted `retained-attributed-B`, no production source change, Source Anchor or 370 old rows changed, no reference machine/SLA approval or Performance Gate activation, no PR/merge/tag/release. **MEM-004/005/006 and QA-004/005 OPEN, QA-007 CLOSED.**

> **LATEST MEM-004D FROZEN SESSION REGISTRY / ACTIVE CALLBACK EVIDENCE (2026-11-19):** Feature SHA `58e655a79fe61084179b82ed1b42882bc02cc8a2` [Actions 44424670741](https://github.com/majiddarvishan/neta-go/actions/runs/44424670741) PASS all 3 jobs and optional owned-buffer smoke separately inspected: 5 Python anchored tests, 7 test-only Go lifecycle tests under -race, actual Core RR-64B-S1-C1-medium 1x. Adapter `QA005-OWNED-BUFFER-OVERLAY-V3-UNQUALIFIED` freezes the set of Client/Server Sessions at sample-window start, retains removed Server Session identities for active callback F2/F3 responsibility, and invalidates samples on any live unregistered Server Session. Tests include F1 pre-enqueue/duplicate transfer/Forced Close, F2/F3 callbacks continuing after Done, Panic cleanup, Control Frame, frozen registry. Smoke sample peak **0 B**, only **2 samples**, and independent Session event-HWM upper **212 B**: sampler missed short allocations; neither is an instantaneous global attributed peak. F4 construction, metadata/worker queues/diagnostics, excluded foreign Panic graphs, missing instantaneous observation/overhead proof and baseline-vs-candidate adapter equivalence remain. No retained-attributed-B emitted. Source-V1 fixed at `9b7b2318f73d173a99d22489042f84f8ce58b745`; no production source changes. QA-004/005 and MEM-004/005/006 OPEN, QA-007 CLOSED, mandatory gate DISABLED. No PR/merge/tag/release.

> **QA-005-MEM-004C VERIFIED F1 PRE-ADMISSION CORRECTION (2026-11-19):** At SHA 26aa2873812abfe1349679be306bd2e8fd363702, [Actions 44423378544](https://github.com/majiddarvishan/neta-go/actions/runs/44423378544) passed all 3 jobs and the separately checked optional owned-buffer step: 5 Python tests, 3 Go overlay lifecycle tests with -race, 1x actual Core RR. Test-only V2 adapter accounts F1 at allocation under Session lock before Queue Admission, transfers the same responsibility through Queue/Writer, and releases pre-queue rejects. A 5ms sampler saw 0 B over 2 samples while sum of Session event-HWM was 212 B: neither is an exact global peak nor valid retained-attributed-B. Earlier [44422549332](https://github.com/majiddarvishan/neta-go/actions/runs/44422549332) at 50abb663 optional smoke FAIL (misclassified transfer); [44423060164](https://github.com/majiddarvishan/neta-go/actions/runs/44423060164) at ae9f78b6 optional Python import FAIL (Go test outside generator fixture). Both top-level workflows were green; failures preserved. Fixed in 26aa2873. Fixed Source Anchor SHA 9b7b2318f73d173a99d22489042f84f8ce58b745 and six Production/Benchmark blobs unchanged. Coverage, concurrent Forced Close/callback, dynamic Session registry, metadata/worker/external graphs, sampler gap and matched effective adapter remain missing. MEM-004/005/006, QA-004/005 OPEN, QA-007 CLOSED; gate DISABLED; no PR/merge/tag/release.

> **LATEST QA-005-MEM-004B EVENT-HWM EVIDENCE (2026-11-19):** At exact SHA `ad0ff9eef114b7ec44aa0ecf25d1eb678b1b097d`, [QA final Actions 44420200998](https://github.com/majiddarvishan/neta-go/actions/runs/44420200998) **SUCCESS all three jobs**; optional **owned-buffer** step itself PASS: 4 Python patch tests, both Go test-overlay F1/F2/F3/F4 lifecycle sanity tests under `-race` and actual 1x RR 64B benchmark. Overlay reports **sampled owned-buffer peak=74 B**, **sum of per-Session event-HWM upper=212 B**, **2 observed samples**; the figures differ because sampled observation can miss fast in-window ownership peaks and HWM maxima can occur at different times. These numbers **are not exact global retained memory, do not satisfy 10 paired/95%/15% qualification, and do not approve a baseline**. The immediately prior [Actions 44419652396](https://github.com/majiddarvishan/neta-go/actions/runs/44419652396) PASS had a 0 B 1x sampled peak, demonstrating missed short-lived allocations. Both main measurement source fixture and four modified source targets have **identical GitHub blobs** between fixed source anchor `9b7b2318f73d173a99d22489042f84f8ce58b745` and feature SHA `dfb33283`; equivalent compiled adapters still require proof for two distinct versions. Existing production code, public API, QA-007 semantics untouched. Also preserve the failed advisory smoke from 40f8a5a3 (Go compile error in extra test) and failed zero-job YAML from 40016b5e, subsequently corrected in dfb33283. **QA-004 and QA-005 OPEN; QA-007 CLOSED; Performance Gate DISABLED; no PR/merge/tag/release.**

> **QA-005-MEM-004A VERIFIED SHORT REAL-SOURCE OVERLAY SMOKE (2026-11-19):** At exact feature SHA `1a9c9bb80538d3a44ea1dbfd4373fd2424f131e7`, [QA final Actions #44417224436](https://github.com/majiddarvishan/neta-go/actions/runs/44417224436) **PASS in all 3 jobs**, including optional advisory memory overlay step. Python synthetic tests **2/2 PASS**; real repository Go 1.23 runner successfully compiled `go test -overlay` and ran one `Core/RR-64B-S1-C1-medium` operation (`-benchtime=1x`). Adapter `QA005-CHARGE-OVERLAY-PROBE-V1-UNQUALIFIED`; exact original fixture SHA256 `6a3adf62a50508f5c5aef8ac6e062176523d20e9fae95c11e225bf1e1e937172`, effective fixture SHA256 `ec0b0f521e5d6f80122da323d433031d8c31b6c5a615388d67a975c9303eb42e`. Probe emitted `probe-owner-charge-peak-B=74`, `probe-owner-charge-samples=2`: **NOT actual attributable memory, not meaningful peak estimate, not SLA or gate qualification**. The earlier malformed YAML run #44416997076 was corrected in `1a9c9bb8`; do not erase its FAIL evidence. Need prove actual allocated memory and sampling bias/overhead before `retained-attributed-B`. Fixed source-V1 anchor, QA-004/005 OPEN, QA-007 CLOSED, Performance Gate DISABLED.

> **CI YAML FAILURE AND TARGETED REPAIR (2026-11-19):** Workflow on `d4a7898c` had malformed benchmark shell text after an incorrect source-string replacement; GitHub Actions run [44416997076](https://github.com/majiddarvishan/neta-go/actions/runs/44416997076) reported FAILURE with **zero jobs** (not a Go/BENCH performance failure). This commit **rebuilds only the QA-final YAML from the previously valid b93e3e45 revision**, restores all original jobs plus the isolated 1x optional overlay smoke, and preserves the report-only status. Do not call this repair PASS until the new exact-SHA run succeeds. No Production code or benchmark fixture change, no Performance Gate, PR, merge, tag or release.

> **QA-005-MEM-004A SHORT REAL-SOURCE CI SMOKE ADDED (2026-11-19):** Feature-only `.github/workflows/qa-final-validation.yml` now runs the synthetic Python overlay tests, generates a read-only overlay against the *actual* repository's original `benchmark_test.go`, and attempts a single 1x Core 64B request/response benchmark with `NETA_QA005_MEMORY_PROBE=1`. The step is **continue-on-error/advisory**, writes separate artifacts, and **does not emit or gate on `retained-attributed-B`**. CI outcome NOT YET VERIFIED at this documentation update. Existing full advisory CI is unchanged except this short optional diagnostic. No mandatory Performance Gate, numerical baseline, production changes, PR, merge, tag or release.

> **MEM-004A OVERLAY GENERATOR PROTOTYPE (2026-11-19):** Added `scripts/qa005_memory_overlay.py` + synthetic `scripts/test_qa005_memory_overlay.py`. It generates an external `go test -overlay` replacement for the **existing** benchmark test file, adds a 5ms owner-ledger *charged-byte* sampling goroutine only under `NETA_QA005_MEMORY_PROBE=1`, and emits only `probe-owner-charge-peak-B` + sample count, **NOT** `retained-attributed-B`. The two SHA-256 digests distinguish original and effective fixture. Synthetic Python unit tests 2/2 and synthetic Go overlay compile/1x benchmark PASS in isolated Go 1.23.2 container; **NOT verified against the real neta-go source or owner's Go 1.27 toolchain**. This is advisory feasibility code; no qualified attribution, memory comparator approval, overhead evidence, source anchor change, or production instrumentation. Do not run full suite or create PR/merge/tag/release without separate owner permission.

> **QA-005-MEM-004 OWNER APPROVAL (2026-11-19):** Owner approved the metric *definition*: maximum observed neta-attributable retained bytes inside active QA-005 workload, with declared coverage/exclusions; incomplete evidence is INCONCLUSIVE. Approved entering *limited tooling/testing* only. No permission to equate reserved owner ledger capacity with actual memory, to assert an exact instantaneous peak from sampled snapshots, to modify source baseline, or to activate a Performance Gate. Begin with a diagnostic-only overlay feasibility probe; production instrumentation and a qualifying `retained-attributed-B` still require real category evidence and hot-path overhead checks. `QA004-QA005-SOURCE-V1` pinned source SHA unchanged; QA-004/005 open, QA-007 closed.

> **QA-005-MEM-003 MEASUREMENT COMPATIBILITY DESIGN (2026-11-19):** [Measurement plan](NETA_GO_QA005_MEMORY_MEASUREMENT_QUALIFICATION_PLAN_2026-11-19.md) documents same-source SHA/fixture checks, proposed identical effective benchmark adapter, overlay feasibility (NOT YET VERIFIED), precise measurement-window rules, sampled peak vs per-owner charged high-water distinction, time-series distribution, excluded unknown external graphs and fail-closed evidence criteria. Existing `qa005_qualify.sh` rejects dirty sources/untracked Go files and mismatched fixtures; `qa005_compare.py` expects `retained-attributed-B` and rejects missing/zero values. **This is design only.** MEM-003 specification [x], MEM-004 final metric/method review [ ], MEM-005 instrumentation and tests [ ]. Source anchor `9b7b2318f73d173a99d22489042f84f8ce58b745` unchanged; archived 370 rows not rerun; QA-004/005 OPEN, QA-007 CLOSED; mandatory gate DISABLED. No PR, merge, tag or release.

> **QA-005-MEM-001 OWNER DECISION + OWNERSHIP DESIGN (2026-11-19):** Owner approved **B / Hybrid Ownership Accounting**. Audited real production source at `f00e7920bd2f336ab9bbe5822fe11467a7851855` and recorded exact ownership/charge lifetimes, exclusions and missing instrumentation in [MEM-001 draft](NETA_GO_QA005_ATTRIBUTABLE_MEMORY_OWNERSHIP_DESIGN_2026-11-19.md). Admission retained/queued bytes are overlapping budgets, not exact attributable heap; post-workload zero is not Peak; raw panic values may hold unknown external graphs. **MEM-003 adapter compatibility and MEM-004 metric definition are still OPEN.** This commit is DOCUMENTATION ONLY; no production implementation, bench, reference hardware approval, numerical baseline, gate enablement, PR, merge, tag or release. Pinned source anchor remains `9b7b2318f73d173a99d22489042f84f8ce58b745`, QA-004/005 OPEN, QA-007 CLOSED.

> **CLEANUP ROOT CAUSE CONFIRMED FROM OWNER CONSOLE (2026-11-19):** Draft numeric SOURCE-V1 capture's 30 benchmark runs and 370 rows were successful, but final script `FAIL` came from `git worktree remove` leaving `/tmp/neta-numeric-ref.5S0ymlDB/source` with sole untracked `scripts/__pycache__/` (shown by owner-provided `git status --short --ignored`). `importlib` Python bytecode generated inside detached source blocked non-force removal. A minimal script-only fix at `68c861233a280cac3929c0d3db85e9d10dbe94cf` sets `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`; no benchmark rerun, no production changes. Owner should delete only that temporary cache and use ordinary `git worktree remove` (not `--force`). Root-cause evidence: `docs/performance-baselines/QA004_QA005_SOURCE_V1_NUMERIC_CAPTURE_2026-11-18.md`. Numerical baseline unapproved; QA-004/005 open and gate disabled.

> **OWNER-LOCAL QA004/005 SOURCE-V1 NUMERIC CAPTURE, reviewed 2026-11-19:** Uploaded `source-v1-all-20261118T215013Z-2501287.tar.gz` (SHA256 `fb1581c95ead3fa55c626646370637a4d1dd4b5cfd6b736fbdaa1c368427d036`). The pinned source SHA `9b7b2318f73d173a99d22489042f84f8ce58b745` produced **10/10 Core, 10/10 Full and 10/10 QA-004 PASS benchmark executions** (370 selected benchmark rows); all three ordered-log SHA256 digests were independently verified; 320 traffic rows showed zero capacity rejects and zero post-workload ledger counters; 50 QA-004 rows had 1200 internal settlement samples each (60,000). **Original collector overall status FAIL was solely due to failed temporary Git worktree cleanup**, for which stderr was NOT captured; root cause unknown. A separate follow-up script-only fix captures cleanup diagnostics and separates measurement/cleanup statuses. Full QA-005 contains unstable single-Session P99 cases (worst run CV 40.59%); observed host pswpout increased by 5495 pages. **Numerical baseline and hardware not owner-approved, attributable retained memory unmeasured, absolute SLA unset, Performance Gate DISABLED**. See `docs/performance-baselines/QA004_QA005_SOURCE_V1_NUMERIC_CAPTURE_2026-11-18.md` and its CSV summaries. QA-004/005 remain open; QA-007 closed. No product-code change, PR/merge/release.

> **OPTION A NUMERIC REFERENCE COLLECTION TOOL PREPARED (2026-11-19):** Owner-approved **source anchor** `QA004-QA005-SOURCE-V1` stays at exact SHA `9b7b2318f73d173a99d22489042f84f8ce58b745`. Added `scripts/qa005_baseline_capture.sh`: one local command captures 10 *independent* Core + Full (1s each benchmark) and QA-004 (1200x) runs on a temporary detached checkout of the pinned source SHA, checks complete exact scenario matrices and resource reports, computes SHA-256/draft statistics and bundles a single `.tar.gz`. **Tool has NOT been run on owner workstation; all numeric draft manifests have `owner_approved=false`**. This is not 10 paired cross-version runs; an actual future candidate must be evaluated against the pinned source with fresh 10 matched alternated runs. Host, numeric acceptance, retained memory, absolute SLAs and gate still unapproved. QA-004/005 remain open; QA-007 closed; no PR/merge/tag/release.

> **OWNER APPROVED OPTION A — QA004/005 INITIAL SOURCE ANCHOR (2026-11-19):** Use exact feature SHA `9b7b2318f73d173a99d22489042f84f8ce58b745` as `QA004-QA005-SOURCE-V1` **for future code-regression comparisons only**. Do NOT compare older `main` as a retroactive baseline. Structured record: `docs/performance-baselines/qa004-qa005-source-v1.json`; canonical decision: `.codex/DECISION_LOG.md` §74. This is SOURCE approval, **not** approval of machine, numeric measurement baseline, memory metric, absolute SLA, `qa005_compare.py` approval manifest or mandatory performance gate. QA-004/005 remain open; QA-007 complete; no PR/merge/tag/release.

> **OWNER-LOCAL QA-004 A/A (2026-11-18, exact SHA `ff38ceb29107fa156e0f87555f59bc6a5fa393d9`):** Received `aa-qa004-20261118T202222Z-2358305.tar.gz`: complete **10 alternating A/A pairs**, 5 synthetic Pending populations, 100 successful benchmark rows × 1200 internal terminal-settlement samples = **120,000 observations**; all **5/5 relative P99 metrics PASS** with run-level P99 CV 0.93–3.01%. Host i5-12400/Go 1.27, `powersave`, load increased 1.09 -> 1.70, pswpin +87 and pswpout +0. **A/A comparator status remains INCONCLUSIVE, baseline_approved=false, performance gate DISABLED** despite relative_status=PASS. Distinguish from QA-005's 1s A/A (P99 4/8 INCONCLUSIVE). QA-004/005 Task qualification remain OPEN, QA-007 CLOSED. This tool evidence does not approve a reference machine, absolute SLA or historical baseline. See docs/PERFORMANCE_QUALIFICATION.md.

> **SECOND OWNER-LOCAL A/A CORE PROBE (2026-11-18, 1s):** Owner uploaded `aa-core-20261118T152119Z-1872550.tar.gz` (SHA `193d9c2e58e021319a92b4abb37cce69d8074dc1`). A/A 10 pairs / 160 rows / 8 Core cases, matrix complete, env comparable, benchmark fixture digest identical to 250ms run. Non-retention measured metrics: **36 PASS / 12 INCONCLUSIVE / 0 FAIL**, vs prior **31/17/0**; eight retained-attributed-memory metrics uninstrumented INCONCLUSIVE. P99 still **4 PASS / 4 INCONCLUSIVE**; mean per-scenario P99 CV ~23.5% -> 11.8%, but RR 64KiB single Session CV remains 33.8%. Governor powersave, host load changed, pswpin +124, pswpout 0. **No approved reference baseline or performance gate**. Next non-invasive step: owner-local `bash scripts/qa005_noise_probe.sh qa004` with NO BENCHTIME override. QA-007 closed. Details in docs/PERFORMANCE_QUALIFICATION.md.

> **OWNER-LOCAL A/A CORE MEASUREMENT (2026-11-18):** 10 alternating pairs with identical exact SHA `a6c2b1373e01b716bf8bf8f89d71abe0708630fe` on the Linux i5-12400 / Go 1.27 workstation: all 160 output rows complete, 0 capacity rejections, post-workload resource counters zero, 31 PASS / 17 INCONCLUSIVE / 0 FAIL measured Core metrics **plus 8 uninstrumented retained-memory INCONCLUSIVE**. Several single-Session P99 measurements exhibited 38–50% sample CV, so **machine is not yet qualified as a stable reference**; `comparison.status=INCONCLUSIVE`, `baseline_approved=false`, gate remains DISABLED. Added an optional 1s per-benchmark A/A rerun (`NETA_QA005_BENCHTIME=1s bash scripts/qa005_noise_probe.sh core`), default remains 250ms, for owner-local execution; this new diagnostic has not been run yet. No production code touched, QA-007 stays closed. More detail in the final-validation report.

> **QA-004/QA-005 LOCAL REFERENCE PREPARATION (2026-11-18):** Added an isolated, single-command **A/A noise probe** on commit `63f80470b60be4c27475d3f681b2475d7c37b6db`: `bash scripts/qa005_noise_probe.sh core` on the owner's Linux workstation. It runs ten matched alternating pairs of **identical** exact-SHA worktrees, captures governor/load/memory/swap/pressure evidence, and emits one local .tar.gz. This is an **unexecuted probe tool awaiting owner-local run**; it has not qualified or approved a reference machine, historical baseline, retained-memory metric or absolute SLA. QA-004/005 remain OPEN and Performance Gate DISABLED; QA-007 stays CLOSED. No PR/merge/tag/release. See `docs/PERFORMANCE_QUALIFICATION.md`.

> **LOCAL QA-007 RETEST, 2026-11-18 (owner-supplied console output; code+test SHA `2db90faf67923ea796ed611629390197cffb0e43`):** After a flaky `TestQA007ForcedClosePreservesAllCompletionAndCredit` failure under coverage on the first local final validation, a **test-only** fix awaits the asynchronous Panic diagnostics record after Completion credit release (no production-code change). Owner subsequently executed `go test -race -count=100 -run '^TestQA007ForcedClosePreservesAllCompletionAndCredit$' .` (PASS), `go test -cover -count=100 -run '^TestQA007ForcedClosePreservesAllCompletionAndCredit$' .` (PASS; targeted-test-only coverage 25.0%) and `make smoke` (PASS; root coverage **82.7%**, wire **92.0%**, example loopback Request/Response, one-way event and graceful stop PASS). **QA-007 remains [x] CLOSED on feature branch; the reported local flaky test issue is resolved for these retests.** The earlier 30-minute soak and advisory QA-004/005 measurements were performed on the previous code+test SHA; production source is unchanged, so they are preserved as earlier evidence rather than claimed reruns. QA-004/005 reference qualification remains OPEN, Performance Gate DISABLED. No PR/merge/tag/release performed. This paragraph supersedes earlier local smoke-failure status.

> **LATEST VERIFIED QA EVIDENCE — 2026-11-18 (source SHA `99dd68848eb73dd15ccf0a178861aa7f7cf82fef`):** [GitHub Actions #44313332548](https://github.com/majiddarvishan/neta-go/actions/runs/44313332548) PASS in all three jobs: gofmt/vet/uncached Go unit+races/paired smoke, pinned C++ V1 golden, five QA-004 P99 benchmarks with **1,200 terminal-settlement observations each**, QA-005 8 Core plus 24 Full advisory workloads, and **16 Python comparator tests**. Exact workload-name verification now checks the Go fixture; malformed/duplicate/unreadable evidence is INCONCLUSIVE. Successful QA-005 workloads report accepted operations, offered producer count, zero capacity rejections, and post-run owner resource counters (all zero in 32 Core+Full output rows). These are **post-run snapshots, not attributable memory peaks or stable reference qualification**. QA-007 COMPLETE on this feature branch; QA-004 and QA-005 remain OPEN pending approved stable machine/baseline, 10 matched pairs, 30-minute soak, actual retention method and owner-approved absolute SLAs. Performance Gate DISABLED. No PR, merge, tag or release permitted.

> **LATEST VERIFIED QA QUALIFICATION UPDATE (2026-11-18):** On isolated feature branch, source HEAD `eaf022357e369b8d484376a3385b16f2ce4fafd6` passed [final Actions #44310174076](https://github.com/majiddarvishan/neta-go/actions/runs/44310174076): Go format/vet/unit/race/smoke, pinned C++ V1 golden, QA-004 detection with **1,200 samples for each of five Pending populations**, QA-005 8 Core and all **24 Full** advisory benchmarks, and 12 Python comparator tests. Linux process CPU/op is measured only in benchmark code. Paired QA-004 P99 and QA-005 qualification now reject mismatched baseline fixture SHA/matrix and report missing attribution honestly. **QA-007 remains complete; QA-004 and QA-005 remain OPEN** because an owner-approved stable machine/baseline, 10 matched pairs, 30-minute soak, attributable retention evidence and absolute SLA approval remain outstanding. Mandatory Performance Gate DISABLED. No PR, merge, tag or release authorized. This paragraph supersedes older partial-status descriptions below.

> **LATEST IMPLEMENTATION HANDOFF — 2026-11-18, feature branch:** The owner separately authorized source changes, tests and final CI for QA-004/005/007 on `feature/qa004-qa005-qa007-implementation-2026-11-18`. Confirmed main base `24b7c5f6eb4e001f30dd8a564a337ca1f506eac8`, merged PR #22; verified CODE HEAD `e852392542c20daf5a79cba2aaee7fbd55e454f8`. [Final workflow run 44306325369](https://github.com/majiddarvishan/neta-go/actions/runs/44306325369) PASS across Go correctness/race/examples, pinned C++ V1 golden and advisory performance; no automatic merge/release/tag. QA-007 implementation/test is COMPLETE; QA-004 linear scan and QA-005 qualification tooling are implemented with advisory results, but their master tasks are OPEN until reference-machine evidence, 10 matched pairs, 30-minute soak and any absolute SLA owner approval. Mandatory Performance Gate DISABLED. The [validation report](NETA_GO_QA004_QA005_QA007_FINAL_VALIDATION_2026-11-18.md) and [TASKS](TASKS.md) supersede historical docs-only / design-only notes below. Do not create PR, merge or release without separate owner authorization.

> **LATEST OWNER CONTRACT HANDOFF — 2026-11-18, docs-only branch:** Main source base `397dedf6435196195eafa2c50c9fdab71c2af2c1`. Owner approved QA-004.3=C, QA-005.3=C/.4=B/.5=C/.6=C/.7=B/.8=C and QA-007.14–30; additionally resolved QA-007.26=A (retain all accepted-Request Completion on any Forced Close) and QA-007.30=A (reserve OnClose event credit before eligible Session admission; reject admission at capacity). **These new target contracts supersede legacy Completion cancellation and best-effort OnClose skip**, but are **DESIGN ONLY**, not source/CI verified. Canonical full text: [QA contract](NETA_GO_QA_004_005_007_APPROVED_CONTRACTS_2026-11-18.md); tracked work: [TASKS](TASKS.md); decision chronology: [DECISION_LOG](DECISION_LOG.md) §73. Qualified environment, numeric absolute SLA and implementations remain open. This update was explicitly authorized for documentation only, with **no tests, code, CI, PR, merge, tag or release authorization**. Do not interpret older historical descriptions below as overriding these newer approvals.

> **ACTIVE HANDOFF — 2026-11-18:** neta-go protected `main` HEAD `0824a70127594df72f78d1048cc360e33f57bd5b` after QA-006 fix ([PR #17](https://github.com/majiddarvishan/neta-go/pull/17)). QA-001 genuine C++ V1 TCP E2E now **PASS normally and with -race** using the private pinned C++ 1.5.0 source on neta-go exact SHA `0824a701...` ([private run 44260379077](https://github.com/majiddarvishan/pinex/actions/runs/44260379077)), with workflow merged in private pinex PR #29. QA-001, QA-002, QA-003 and QA-006 are closed; QA-004 is measured but open, QA-005/007/008/009 remain open. Canonical tracking: [TASKS.md](TASKS.md); QA-001 detail: [verification](NETA_GO_QA001_REAL_TCP_VERIFICATION_2026-11-18.md). **No release authorization.**

# Project Handoff — neta-go / Pinex Compatibility

> **CANONICAL REVISION (2026-11-17):** Q-003-R1, PERF-002 A, PERF-003 A model, API-001b-FC-A, N-ORD2, DONE-A, C-ORD-B and WORKER-001..009C remain owner-approved. PROTOCOL-001 fixes Pinex's maximum Frame at 1 MiB total including the 10-byte Header. **Phases 1–8 are COMPLETE / CI PASS.** Phase 9 is owner-authorized and IN PROGRESS: P9-00 tracker reconciliation is complete; P9-01..P9-05 are authorized; P9-06 release tagging remains separately gated on explicit owner approval. Latest verified pre-Phase-9 HEAD: `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5`; production source HEAD: `209c24a7dbc5a5aa3db95ec63705915406acacb6`. Go CI [44108072039](https://github.com/majiddarvishan/neta-go/actions/runs/44108072039), Pinex Wire Compatibility [44108072167](https://github.com/majiddarvishan/neta-go/actions/runs/44108072167), and Phase 8 Performance [44105272003](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003) PASS.

**Updated:** 2026-11-17  
**Repository:** majiddarvishan/neta-go  
**Branch:** main  
**Implementation status:** PHASES 1–8 COMPLETE / CI PASS; PHASE 9 IN PROGRESS / OWNER AUTHORIZED
**Current work:** P9-00 through P9-04 are complete. P9-05 automated checks now pass on test-hardened HEAD `958601ee55dd6229021e36135a017527dfa8f778`: `make verify`, coverage capture, both example builds, paired loopback Request/Response + SendNoWait, graceful Client/Server Stop, and Pinex compatibility. Remaining: owner/admin review of main branch protection and GitHub Release settings. The owner approved current `CHANGELOG.md` entries and intended `v1.0.0` on 2026-11-17 (no tag authorization). Copyright holder/year (`Majid Darvishan`, `2026`) and commercial use under existing Apache-2.0 were explicitly confirmed by owner on 2026-11-17; LICENSE notice updated. Go/platform support remains approved (Go 1.23 minimum; Ubuntu 24.04/Linux amd64 CI-tested). P9-06 release tagging remains separately gated on explicit owner approval.

## 1. Repository state

- Canonical implementation checklist: [TASKS.md](TASKS.md). Update it whenever a task changes status.

- Default branch: main
- Phase 3 source verification HEAD: `cc0d25e9252b48f38dcddeeb53eaa6e7fe1cbf4c`.
- Phase 4 resource-admission source verification HEAD: `2935402366603267ba60c181a057d26cf0e7e9a6`.
- Phase 5 worker-scheduler source verification HEAD: `c72136693f85e61239bfca42bd04b40e66eddc27`.
- Phase 6 Server lifecycle/admission source verification HEAD: `8eead509c6817722d6b7c6f5e5a17e1734749911` (11 tests; Go and Pinex golden CI PASS).
- `.codex/AGENT_CONTEXT.md`: not present on `main` at the verified HEAD.
- Verified baseline before WORKER-001 documentation updates: 525487737c1b75c62d021a391a395e03c1aadb1e
- Phase 1, Phase 2, Phase 3, Phase 4 and Phase 5 source/tests are committed and verified by GitHub Actions.
- Phases 1–8 are implemented/verified and Phase 8 is closed. Phase 9 is now owner-authorized; P9-00..P9-05 are in scope, while release tagging remains separately gated.

## 2. Source inputs

### Uploaded Go sample

- Archive: ss7.tgz
- SHA-256: 25b3e0cdfed10c170cf1a4aa02945bfe765bfa1378ef979ed5546883dadd8aa3
- 24 Go files total; 14 non-generated package files and generated Protobuf files.
- Treat it as a behavioral/features reference, not as the authoritative current Pinex wire specification.

### C++ Pinex compatibility target

- Repository: github.com/majiddarvishan/pinex
- Branch: develop
- Version: 1.5.0
- High-level API: messaging_client / messaging_server
- Source-audited develop HEAD on 2026-11-17: `f7bd1eb779baff0d10e624f20522df345e6ee747` (CMake version 1.5.0); re-pin/re-audit before implementation or cross-language testing.
- Main is not the compatibility target for this work.

## 3. New planning documents

- PINEX_GO_PORT_TASKS_2026-11-16.md — task breakdown, dependencies, acceptance criteria, open decisions.
- PINEX_WIRE_PROTOCOL_2026-11-16.md — current Pinex 1.5.0 wire contract and differences from the uploaded Go sample.
- NETA_GO_PUBLIC_API_CONFIG_DESIGN_2026-11-16.md — design-only draft of public API, config, session lifecycle, concurrency, idle keepalive, request tracking and backpressure; Q-006 through Q-010 policy approvals are reflected.
- NETA_GO_API_004_CONFIGURATION_CONTRACT_2026-11-16.md — APPROVED API-004 A: Functional Options, complete internal defaults, independent explicit overrides including idle 0, validated immutable per-instance config.
- NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md — draft Client/Server/Session Public API; API-001a owner approved A (nonblocking/callback-first). API-001b, ownership and callback termination semantics remain OPEN.
- NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md — owner explicitly requires performance as first-class V1 concern; measurement matrix, copy/allocation and bounded completion design work (PERF-001..003), no numeric targets approved.
- NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md — Q-008 outgoing 4 MiB/Fail-Fast, Q-009 B incoming overflow close, and Q-010 A configurable inbound/global/session/pre-bind/control defaults are approved. API-004 design remains open.
- NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md — WORKER-001 owner-approved Client/Server instance-scoped worker ownership; WORKER-002 active-worker ceiling topology is the next open decision.
- DECISION_LOG.md — authoritative approved decisions Q-001 through Q-010 (as applicable), plus NAM-001; distinguishes remaining open API details.
- SERVER_REVIEW_2026-11-16.md — original static review of the uploaded server sample.

## 4. Confirmed protocol facts

- 10-byte header: total length BE u32, command ID u8, command status u8, sequence BE u32.
- Maximum accepted inbound Frame in pinned Pinex 1.5.0: 1,048,576 bytes total including the header; maximum Body 1,048,566 bytes. Go must enforce this maximum in both directions.
- Command IDs: Bind 0x01/0x81, Stream 0x02/0x82, Unbind 0x03/0x83, Enquire Link 0x04/0x84.
- Status: rok 0x00, rfail 0xFF.
- Bind body: bind_type u8 followed by null-terminated system_id; bind_type 0=uni_direction, 1=bi_direction.
- Bind Response uses the same body shape and carries server system_id.
- Stream payload is raw remaining frame bytes, with no extra length prefix or mandatory Protobuf envelope.
- Enquire Link response and Unbind response reuse the request sequence number.
- Sequence is per Session, increments, and skips zero.
- Pinex uses a 10-second Unbind protocol deadline.
- Current Pinex pre-bind defaults: 30-second handshake deadline, 128 pending sessions, optional per-IP quota disabled by default.
- Current Pinex Client defaults documented on develop: 30-second connect timeout, 30-second Bind response timeout, 5-second reconnect delay when auto-reconnect is enabled.
- Pinex default behavior responds to Enquire Link and uses OS TCP Keepalive; it does not send periodic Enquire Link by default.

## 5. Important incompatibilities found in uploaded Go sample

1. Go Bind Request/Response bodies omit the Bind Type byte required by Pinex 1.5.0.
2. Go ConnectionReader drops command_status from the Header.
3. Go ClientProtocolHandler.handleBindResponse incorrectly reads the first Body byte as Status; Pinex status is Header offset 5 and Bind Body begins with bind_type.
4. submit_req/submit_resp names differ from Pinex stream_req/stream_resp, but their numeric wire values match (0x02/0x82).
5. The sample uses random Sequence values and automatic deduplication; Pinex uses per-session increasing nonzero sequence values and does not define Sequence-based deduplication as a protocol feature.

Therefore, copying the sample's protocol handling verbatim would not interoperate with current Pinex.

## 6. Task status

See PINEX_GO_PORT_TASKS_2026-11-16.md for the complete backlog.

- GO-PINEX-001: protocol source baseline pinned to Pinex develop `f7bd1eb779baff0d10e624f20522df345e6ee747`; Maximum Frame Size verified as 1 MiB total including Header; golden-frame artifacts are compiled and compared in CI. Live socket-level cross-language confirmation remains Phase 7.
- Phases 1–5 (Configuration, Wire Codec, Session Transport/Lifecycle, Resource Admission and Worker Scheduler) are COMPLETE / CI PASS.
- GO-PINEX-002 through GO-PINEX-014 remain broader integration/backlog items; the `.codex/TASKS.md` is the canonical implementation tracker, while Phases 6–9 remain gated.

## 7. Owner decisions

- **Q-001 — APPROVED (Option A, 2026-11-16):** Pinex-compatible Bind Validator callback based on System ID and actual remote address. No password/token on the wire, no change to Bind PDU layout. Accepted Bind => rok 0x00; rejected => rfail 0xFF. This is not cryptographic identity authentication. See DECISION_LOG.md.
- **Q-005 — APPROVED (Option B, 2026-11-16):** If no Bind Validator callback is supplied, allow an otherwise-valid Bind by default, matching Pinex C++. Duplicate `system_id`, malformed Bind, invalid state and admission limits are still enforced. If a callback is provided, enforce its allow/reject result. This is permissive admission, not authenticated peer identity. See DECISION_LOG.md.
- **Q-002 — APPROVED (2026-11-16):** Configurable, idle-only Enquire Link on Go Client and Server. Send automatically only after no successful frame exchange in either direction for a positive idle interval; `0` disables automatic sending, not replies to peer Enquire Link requests. Never send a second probe while one is outstanding; protocol bytes unchanged. Numeric idle default is **30s** (Q-006); matching-probe response timeout default **10s** and failure closure are approved (Q-007). See DECISION_LOG.md.
- **Q-003 — REVISED BY Q-003-R1 (2026-11-16):** Goroutine-safe Client/Server/Session APIs; **configurable bounded parallel Application callbacks per Session (1 = serial)** with FIFO dispatch selection; callback completion may be out-of-order at >1. Cross-Session isolation, frame-safe concurrent sends and controlled shutdown remain. Internal protocol/timer/Close engine proceeds independently of user callbacks. Exact concurrency default and user-facing notification callback lanes remain OPEN. Implementation details (queue capacity, deadline, API signatures) still need design. See DECISION_LOG.md.
- **Q-004 — CLOSED / APPROVED OPTION A (2026-11-16):** Lean V1 Core retains Pinex interoperability, sessions, backpressure, bounded FIFO, reconnect/timeout and idle-only Enquire Link. Defer Circuit Breaker, business Rate Limiter, Priority Queue, Prometheus exporter and SS7/Protobuf integrations; exclude automatic sequence dedup. Transport admission/backpressure remains mandatory. See DECISION_LOG.md.

## 8. Next action

Q-001, Q-002, Q-003, Q-004, Q-005, Q-006, Q-007, Q-008, Q-009, Q-010 and NAM-001 are **CLOSED** as design decisions. Q-010 Option A (2026-11-16) approved **configurable** initial capacities and global-overload rules: inbound 4 MiB per Session, outgoing 4 MiB per Session (Q-008), aggregate queued Application 256 MiB per Server, 1024 bound Sessions, 128 pre-bind, 30s pre-bind timeout, 4 KiB Control reserve per Session. These are defaults, not preallocated memory or process RSS limits.

**Next action:** Phase 6 is complete. Do not begin Phase 7 live Go↔Pinex TCP interoperability, Phase 8 performance benchmarking/optimization or Phase 9 examples/release without separate owner authorization. Keep `.codex/TASKS.md` as the canonical tracker.

## 9. Approved Go library name

**NAM-001 CLOSED (2026-11-16):** The owner selected `neta-go` as the name of the native Go TCP Messaging library. NETA was originally proposed as "Network Easy Transport API" but the selected name itself, rather than the expansion, is the approved decision. The project owner subsequently renamed the GitHub repository to `majiddarvishan/neta-go` (confirmed accessible on `main`). No Go module/package-path change or source implementation has been performed or approved in this documentation phase. Pinex C++ stays named Pinex. No code has been written. See DECISION_LOG.md.


## 10. Enquire Link default decision

**Q-006 CLOSED, Option B (2026-11-16):** neta-go Client/Server use an idle-only, configurable Enquire Link interval with a **30-second default**. It is not a fixed 30-second periodic probe: actual incoming/outgoing messages reset idle time. Explicit `0` disables automatic requests but never disables responding to incoming Enquire Link. Probe response policy is approved in Q-007: **10-second configurable default**, matching response Sequence required; timeout closes the Session and Client reconnect is conditional on Auto Reconnect.


## 11. Enquire Link response timeout decision

**Q-007 CLOSED (2026-11-16):** Enquire Link response timeout is separately configurable, **10 seconds by default** on Go Client and Server. It begins after the full Request is written. Only matching `enquire_link_resp` (same Sequence) satisfies it; unrelated traffic cannot satisfy it. On expiry, Session closes once and pending operations terminate; Client retries only if Auto Reconnect was enabled. No Pinex wire changes or implementation were authorized.


## 12. Outgoing resource decision and ingress design

**Q-008 CLOSED / approved Option A (2026-11-16):** configurable 4 MiB outgoing Application Stream FIFO per Session, including serialized Frame headers, immediate Queue Full when full; no partial enqueue, silent drops, or orphan request trackers. Control path capacity must be separate and bounded, without violating single-writer framing or Pinex Unbind ordering/deadline.

**Q-009 CLOSED / APPROVED B (2026-11-16):** if a new incoming Application Frame cannot fit the bounded Callback queue, promptly close **that Session only** with an overload cause; no silent drop or pause/resume fallback. Other Sessions continue unaffected. Go cannot forcibly terminate a blocked user callback; avoid indefinite shutdown waits and finalize terminal callback semantics in API design.

**Q-010 CLOSED / APPROVED A (2026-11-16):** ALL defaults are configurable: incoming 4 MiB/Session, aggregate queued Application 256 MiB/Server (NOT process RSS), 1024 bound Sessions, 128 pre-bind, absolute 30s pre-bind deadline, and 4 KiB Control reserve/Session. Outgoing failed local/global admission => Queue Full, keep Session. Incoming failed local/global admission => close only offender. At bound limit reject new Bind without eviction; at pre-bind capacity refuse socket. Outgoing 4 MiB/Session from Q-008 also remains configurable. See resource design.

**API-004 CLOSED / OWNER APPROVED A:** typed Functional Options over complete internal defaults, independently applied explicit overrides including idle 0, validation before Dial/Listen, immutable effective per-instance snapshots. No hot reload approved.


## 13. Incoming overload decision

**Q-009 CLOSED — approved Option B (2026-11-16):** A new Application Stream Frame which cannot fit the bounded Session-local incoming Callback backlog triggers a prompt **close of that Session**, not Pause/Resume. No impact on other Sessions, no silent drop, no duplicate terminal event; pending state and queue charges are released. In the presence of blocked user callback code, transport shutdown must not wait indefinitely for arbitrary user logic. Exact callback delivery/close ordering awaits API design. Q-010 configurable default capacities and global admission rules are now APPROVED. No code changes authorized.

## 14. Q-010 final owner decision and configurability handoff

**Q-010 CLOSED — OPTION A WITH ALL SETTINGS CONFIGURABLE (2026-11-16).** Approved defaults and outcomes are defined in [Decision Log](DECISION_LOG.md), [Resource Design](NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md) and [API/Config Design](NETA_GO_PUBLIC_API_CONFIG_DESIGN_2026-11-16.md). An omitted setting selects the approved default; an explicit valid override is honored. API-004 A specifies Functional Options, internal defaults, and immutable validated per-instance config. Explicit `EnquireLinkIdleInterval=0` disables automatic probes.

**No implementation is authorized.** API-004 A is owner-approved; public method names, callback termination policy and request completion style are not yet approved.

## 15. API-004 closure and API-001 follow-up

**API-004 CLOSED / OWNER APPROVED OPTION A (2026-11-16):** Go-native typed Functional Options, complete defaults, independent explicit overrides including idle=0, pre-network validation, immutable effective configuration. [Approved configuration contract](NETA_GO_API_004_CONFIGURATION_CONTRACT_2026-11-16.md).

**API-001a CLOSED / OWNER APPROVED A:** [Public API draft](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md) defines callback-first asynchronous request submission, with prompt local admission feedback and later one-shot completion via callback. Option B synchronous Context-first as primary API not selected. Other open design details: callback/terminal close/Done behavior, outgoing/incoming payload lifetime, error categories, startup/Stop and reconnect defaults, exact package/module path. Preserve approved Q-003 per-session callback serialization, do not promise forced termination of indefinitely blocked user callbacks. **No source code, module changes, tests or execution.**

## 16. API-001a closure and performance-first V1 constraint

**API-001a CLOSED / OPTION A APPROVED (2026-11-16).** Nonblocking/callback-first SendRequest-style API is primary. Successful queue admission does not guarantee remote delivery or processing. Matching response, timeout and close all compete for one terminal callback completion; API-001b must define precise delivery and Stop/Done guarantees.

**PERFORMANCE OWNER PRIORITY:** high throughput/low tail latency/low allocation overhead and scalability are important for V1. Propose reproducible measurements of msgs/s, p50/p95/p99 latency, allocation and copy counts, GC/RSS, contention and multi-Session load without precommitting unsupported numeric SLAs. See [Performance Contract](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md).

**Next open decisions:** PERF-002 payload `[]byte` lifetime (safe-copy vs borrowed), PERF-003 pending/completion bounds and API-001b callback/Close/Done semantics. No coding or tests permitted.

## 17. GitHub repository path changed by owner (2026-11-16)

**Current canonical repository:** `majiddarvishan/neta-go`  
**SSH URL:** `git@github.com:majiddarvishan/neta-go.git`  
**Branch:** `main` — existing `.codex` documents verified accessible via the GitHub connector.

The owner **already renamed the GitHub repository** from `majiddarvishan/go-simple-net`; this update only synchronizes documentation references. No repository rename, source code edit, `go.mod` edit, test, or build is performed by the assistant. A `go.mod` file was **not found at repository root on main**; do not presume a Go module path is configured. Keep API-003 (package/module path) open. C++ Pinex remains unchanged.

**Next:** continue PERF-002 payload ownership/copy-lifetime and PERF-003 bounded async completions; performance remains first-class V1 requirement. No coding authorization.


## 18. PERF-002 / PERF-003 / API-001b follow-up review (2026-11-16)

**Baseline inspected:** `main` HEAD was exactly `0fe42d3f0ac634a5a1c9617d1e800b68a00fdf9f` before these documentation changes. `.codex/AGENT_CONTEXT.md` was not found (404); all requested remaining design documents were read.

**New design draft:** [NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md). This contains **proposals, not new owner approvals**:

- **PERF-002 CLOSED / OWNER APPROVED A:** outbound independent snapshot before accepted async send returns, receiving directly into owned user-retainable payload with no extra receive copy. Borrowed callback-lifetime B and transfer C were not selected. Pooling only for proven-safe private internal buffers after evidence; no end-to-end zero-copy claim.
- **PERF-003 OWNER APPROVED A MODEL:** independently configurable per-Session and Server aggregate count ceiling for pending + queued + active request completions; new Request immediately rejected on exhaustion without closing Session. Independent incoming event-count cap remains an unapproved proposal. Suggested `1024` / `65536` are illustrative **unapproved** counts, not defaults. Existing Q-008/009/010 byte ceilings stay unchanged.
- **API-001b OPEN:** blocked callback makes prompt `OnClose` and strict per-Session callback serialization mutually incompatible. Proposed `Done()` reflects transport/accounting termination independent of arbitrary callback return; `OnClose` at-most-once on serial dispatcher. Forced-close Option A cancels unstarted callbacks promptly but creates an explicit exception to user-visible completion delivery; Option B retains bounded deferred completions but may retain closed workers indefinitely. **Owner must choose**; do not silently claim callback-delivery exactly once in all failure modes.
- **API-002 / API-003 OPEN:** timeouts/reconnect/Stop defaults and module path `github.com/majiddarvishan/neta-go` / package `neta` proposed only; no `go.mod` added.

**Next owner decision:** API-001b forced-close callback-delivery policy A vs B; then PERF-003 numeric caps and potential inbound event-count cap. PERF-002 A is CLOSED; PERF-003 A count-admission model is APPROVED. Existing owner decisions Q-001..Q-010, NAM-001, API-004 A and API-001a A remain unchanged. No Go/C++ source, test, benchmark, build, CI, deployment or operational change performed. Main has documentation commits only for this review.


## 19. PERF-002 owner approval and remaining work (2026-11-16)

**Owner approval just recorded:** **PERF-002 CLOSED / Option A (Safe Snapshot + Owned Receive)**; authoritative entry in [DECISION_LOG.md](DECISION_LOG.md). This is an **API semantics** decision, not implementation authorization. For accepted asynchronous Stream sends, one independent outbound payload snapshot is complete before successful return; the caller can then reuse its source. A callback-visible received payload is separately owned, directly filled where possible, may be retained after callback return and is never returned to a library pool. No end-to-end zero-copy promise; no concurrent mutation during the outbound snapshot.

**Synced docs:** [NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md), [NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md), [NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md), [PINEX_GO_PORT_TASKS_2026-11-16.md](PINEX_GO_PORT_TASKS_2026-11-16.md).

**Remaining design questions (not approved):**

1. **PERF-003:** approve count-bounded completion-credit admission for all pending/queued/active callback-based requests, Server aggregate cap, and incoming callback event-count cap. Rejection of *new* SendRequest on count exhaustion leaves Session connected, separate from Q-008 byte-based Queue Full. Incoming application event overflow follows already-approved Session-only close policy, but proposed count limit and numeric defaults require review. Illustrative 1024 per Session / 65536 Server are **NOT APPROVED**; no benchmark has run.
2. **API-001b:** choose forced-close Option A (prompt cancel of not-yet-executing user callbacks with at-most-once `OnClose`, `Done` closes independently) vs B (defer bounded terminal completion to worker, possible unbounded worker lifetime for permanently blocked user code), and callback registration API shape. Internal request result settlement once is distinct from invocation of user callback; do not claim both immediate `OnClose` and same-Session serialization under permanent user block.
3. **API-002:** decide request deadline origin (admission vs wire Write), timeout/reconnect/Stop defaults, pending cancellation and terminal errors. Preserve approved Q-006/007 idle heartbeat and Pinex wire deadline.
4. **API-003:** Go module path still undecided; no `go.mod` creation. C++ develop HEAD and golden-wire vectors must be pinned before authorized implementation/testing.

**Current guardrail:** docs only. No Go/C++ code, tests, benchmarks, builds, live operations or module changes performed. Latest source HEAD before this documentation sequence was `08fb5df8f582d7d91c53308988f31906a68ac557`.


## 20. PERF-003 A owner-approved model and API-001b follow-up (2026-11-16)

**Baseline verified before these documentation edits:** `main@52a126617fbe194c171926cf21fe2fb13893238b`. The owner chose **PERF-003 Option A** in the subsequent conversation. **Authoritative approved policy:** [DECISION_LOG.md](DECISION_LOG.md) section PERF-003. Previous historical notes describing the entire PERF-003 model as OPEN are superseded.

### Current contract truth

- **PERF-002:** CLOSED, owner-approved A: snapshot outgoing before successful async Send return; direct owned/retainable incoming payload, no reuse after callback handoff.
- **PERF-003:** **Option A MODEL APPROVED**. Bound by count: active outstanding Request waiting for response, queued completion callback, running completion callback; independently configurable per Session and Server aggregate with API-004 Functional Options. New request exceeding either limit rejected promptly, without sending, orphan pending state or disconnect. No per-Request goroutine or unbounded Completion queue. The existing Q-008 outgoing byte Queue Full and Q-009/Q-010 incoming/global queue and overload policy remain binding.
- **PERF-003 details still OPEN:** final numeric defaults (the sample 1024 Session / 65536 Server are NOT approved), optional separate **incoming callback event-count cap** and precise error identifiers, memory ownership of active/partial frames, forced-close credit release and timing. Pooling/benchmarks not authorized.
- **API-001b still OPEN:** the same-Session serialization rule makes unconditional immediate `OnClose` impossible behind an indefinitely blocked user callback. A proposed `Done` signal indicates prompt internal transport/resource closure independently of callback progress, **not owner approved**. **Choice A:** cancel not-yet-running callback work at forced Close and best-effort `OnClose`, favoring bounded teardown but allowing a request completion not to invoke the user callback. **Choice B:** defer a bounded set of terminal callbacks, improving delivery if callback progresses but permitting closed worker/queue retention indefinitely when blocked. Neither approved. Settle outcome internally once, regardless of callback delivery. Avoid conflating API-001b forced-close A/B with PERF-003 A (already approved).
- **API-002:** request deadline start (admission vs full Write), Connect/Bind/Reconnect/Stop defaults OPEN. **API-003:** module/package path OPEN. Go/C++ source untouched.

### Design records synchronized

- [NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md) §10 includes quota reservation, release, race handling, and API-001b alternatives.
- [NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md), [NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md), and [PINEX_GO_PORT_TASKS_2026-11-16.md](PINEX_GO_PORT_TASKS_2026-11-16.md) reflect approval.

**Next owner decision:** choose **API-001b forced-close Option A vs Option B** after explicit tradeoff explanation. Do not finalize without approval. Afterward review PERF-003 numerical count defaults and inbound event-count cap. No code, go.mod, tests, benchmarks, builds or operational changes. Branch `main` docs only.

## 21. Q-003-R1 owner revision: parallel callbacks + independent internal engine (2026-11-16)

**Repository:** `github.com/majiddarvishan/neta-go` / `main`. **Last verified HEAD BEFORE this documentation sequence:** `4f12ce80e28e8fd2fb56a626058bbc7132441207`.

**Owner action:** explicitly rejected old Q-003 mandatory serial same-Session processing as wrong and selected **Option B: configurable parallel Application callbacks**, with `Concurrency=1` providing serial application handling. Asked whether the library's *internal* callbacks/events can remain independent of blocked user callbacks. **Answer: yes** — isolate internal protocol and lifecycle state transitions from arbitrary user handler execution.

### Current approved semantics

1. **Q-003-R1 CLOSED / OWNER APPROVED:** per-Session, bounded, configurable positive max simultaneous Application callbacks; `1` serial and >1 concurrent; incoming queue dispatch selection FIFO, completion ordering unconstrained in parallel mode. TCP Wire and single Writer remain unchanged.
2. Internal Control (Bind/Unbind/Enquire Link), Reader/Writer, Request/Response correlation, Timers, internal once-only terminal state and transport Close/Done settlement **cannot depend on return of Application callback**, regardless of concurrency. This does not mean arbitrarily blocked **user** callbacks can be killed.
3. Q-009/Q-010 remain active: per-Session 4 MiB waiting incoming queue + 256 MiB aggregate Server queued Application budget; saturation closes only offending Session. A maximum of N executing user callbacks creates extra active-payload/stack resource cost beyond those waiting queues; separate accounting and lifecycle-safe global concurrency caps are **OPEN** design.
4. PERF-002 A snapshot/owned receive and PERF-003 A bounded outstanding Request/Completion **model** remain approved. PERF-003 counts (1024 Session / 65536 Server) remain unapproved examples.

### Open API-001b design choices — do not finalize without owner

- `OnClose` and per-Request completion handlers are **user callbacks**, not internal engine logic. Consider a **separate, bounded user notification dispatcher** isolated from Application callback workers, so `OnRequest` blockage does not automatically stall these notifications. A stuck notification callback still cannot be forcibly stopped, and resource bounds/forced-close behavior must be explicit.
- Old API-001b Forced Close Option A (cancel not-yet-started callbacks) versus B (retain bounded terminal callbacks for eventual delivery if work progresses) remains **OPEN** and must be reconsidered in the parallel-handler design. Owner's **Q-003-R1 Option B** is NOT an approval of forced-close Option B.
- Choose callback concurrency **default**, max validation, optional global running-handler budget and behavior if previous Session's user callback remains blocked after forced Close / reconnect; avoid accumulated orphan workers. Choose event count cap for empty incoming frames (still open).
- Decide whether `Done()` should signal prompt internal transport closure separately from `OnClose` callback, callback lane ordering, forced-close terminal delivery guarantee, and API-002 Request timeout start. All remain **OPEN**.
- Library name and repository path approved; Go module/package path still API-003 OPEN.

**Docs updated:** [Decision Log](DECISION_LOG.md), [Public API design](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md), [Public API/Config draft](NETA_GO_PUBLIC_API_CONFIG_DESIGN_2026-11-16.md), [Resource Admission draft](NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md), [Performance Contract](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md), [PERF-002/PERF-003/API-001b](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md), [Tasks](PINEX_GO_PORT_TASKS_2026-11-16.md).

**No implementation authorization:** documentation-only. No Go/C++ source code, `go.mod`, tests, benchmarks, CI or operations. Further owner decision only needed for API-001b user notification/forced-close semantics and callback concurrency defaults/aggregate resource caps.

## 22. API-001b-N1 owner-approved notification isolation (2026-11-16)

**GitHub initial checked HEAD:** `d68b04a7e11bfa53ca8d355b7b2bb8513b743ff8` on `main` before this documentation-only sequence.

**Owner confirmation:** explicitly approved making **`OnClose` and per-Request Completion user callbacks independent from Application `OnRequest` workers through a separate bounded user Notification dispatch lane**. Binding decision in [DECISION_LOG.md](DECISION_LOG.md) § `API-001b-N1`.

### Current architecture authority

- **Internal Protocol/Lifecycle:** independent of all arbitrary user callbacks: TCP codec Reader/Writer, Bind/Unbind/Enquire Link, pending response matching, timeout, internal once-only Request settlement and prompt resource/accounting close. No network/protocol goroutine blocks while invoking user functions.
- **Application callback lane:** `OnRequest` with **owner-approved Q-003-R1** configurable bounded concurrency per Session. `1` = serial; >1 permits parallel callbacks and non-ordered completion. Bounded inbound waiting queue preserves Q-009/Q-010 overflow (Session-only close).
- **Notification callback lane:** `OnClose`, per-Request Completion user functions dispatched separately from Application workers, with **bounded work and concurrency**, cannot prevent internal engine teardown. A stuck notification callback cannot be forcibly terminated and can stall its own worker; not a promise of guaranteed notification delivery.
- **Owner-approved other contracts:** API-001a A nonblocking callback-first request, API-004 A functional options, PERF-002 A independent outbound snapshot + incoming owned retainable payload, PERF-003 A configurable bounded pending/completion counts per Session and Server, Q-008/009/010 admission. No change to Pinex 1.5.0 wire.

**Historical snapshot:** the following open-question list predates owner approvals API-001b-FC-A, N-ORD2, DONE-A and C-ORD-B; it is retained only as a record of the earlier state. Current open items are summarized at the top and in §§25–27.

### Explicitly OPEN — next chat should continue here

1. **API-001b forced-close choice:** A (cancel queued/unstarted notification callbacks promptly) vs B (defer bounded terminal events until user callbacks return, at potential memory/worker retention cost). User did **not** select either. Reevaluate in light of independent notification lane; decide exact semantics for admitted Request callback delivery when Session closes, and `OnClose` lifecycle ordering.
2. **Notification execution contract:** one shared bounded lane vs further lanes, notification ordering/fairness, worker/concurrency and queue/count budgets, blocked notification-worker behavior. Only domain separation and boundedness approved; **no numeric default** or exact public signature approved.
3. **Q-003-R1 concurrency default:** user approved configurable `1` serial or >1 parallel; default and any Server-wide active callback guard still OPEN. Must bound active payloads separately from waiting queue bytes.
4. **PERF-003** numeric completion ceilings: earlier 1024/Session and 65536/Server illustrative **not approved**; inbound callback event-count cap proposal OPEN.
5. **API-002** Request timeout origin (admission vs Write), connect/bind/reconnect/stop defaults OPEN; **API-003** Go module/package path OPEN. Exact Pinex C++ `develop` SHA and golden vectors to pin before authorized implementation.

**Updated docs this turn:** `.codex/DECISION_LOG.md`, `NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md`, `NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md`, `NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md`, `PINEX_GO_PORT_TASKS_2026-11-16.md`, and `HANDOFF.md`.

**Strict guardrail:** Design and documents only; no source code, Go module, tests, benchmarks, builds, deployment or operational changes. Never silently finalize the remaining API-001b options; ask owner only for essential material choice.

## 23. Historical API-001b-R2 forced-close / Notification capacity review (superseded by §§24–25)

**Historical status at the time:** the GitHub baseline was `main@893b96629b69b0c67b5aaf456b3e0f178e9fc811`. The comparison below predates the subsequent owner approvals of Forced Close A and N-ORD2 recorded in §§24–25. Full engineering matrix and race/credit/worker discussion: [NETA_GO_API_001B_FORCED_CLOSE_NOTIFICATION_REVIEW_2026-11-16.md](NETA_GO_API_001B_FORCED_CLOSE_NOTIFICATION_REVIEW_2026-11-16.md). Decision-log trace: [DECISION_LOG.md](DECISION_LOG.md) § API-001b-R2.

**Historical note:** this statement described the state before the owner later approved API-001b-FC-A and API-001b-NORD2. The other owner-approved contracts listed here remain authoritative.

**Historical recommendation:** Forced Close A was recommended here and was subsequently approved in §24. The B comparison is no longer an open choice. N-ORD2 was subsequently approved in §25; Done semantics were subsequently resolved in §26; C-ORD-B is subsequently resolved in §27. Numeric capacities remain open.

**Historical next-decision prompt:** A/B and N-ORD1/N-ORD2 have since been resolved by owner approval. Done and within-Completion concurrency were subsequently resolved in §§26–27. Numeric worker/event caps, PERF-003 values, API-002 and API-003 remain open.

**Guardrail unchanged:** no code/go.mod, tests, benchmarks, CI, builds, deployments, operational actions or new owner decision inferred from this document.

## 24. Historical API-001b-FC-A approval and N-ORD1/N-ORD2 comparison (superseded by §25)

**Verified baseline before documentation commit:** `main@4183d182264d768f8c2856d8cead22b37f758c63`. Owner **APPROVED API-001b Forced Close Option A**; previous `API-001b-R2` comparison was historical and A/B selection is no longer open. Binding authority: [Decision Log](DECISION_LOG.md) § `API-001b-FC-A`.

**On Forced Close:** internal Request result settles exactly once; not-yet-started queued `OnRequest` and per-Request Completion callbacks are cancelled, with queued library-owned payload/metadata/credits released. A Completion already queued after a successful response can still be cancelled if its invocation has not started. Already-running user callbacks cannot be interrupted and may outlive Session closure. Transport/pending/timer/registry cleanup must not wait. Completion user callback execution is at-most-once, **not** unconditionally guaranteed for every admitted Request. `OnClose` is best effort/at-most-once. Exact `Done`/OnClose ordering and callback overlap are still **OPEN**.

**Historical note:** this section was written before the owner selected N-ORD2. The A/B Forced Close policy remains binding, but its N-ORD1/N-ORD2 comparison and next-decision prompt are superseded by [§25](#25-api-001b-nord2-approval-and-worker-done-design-handoff-2026-11-16).

**Implementation guardrail:** documentation only; no Go/C++ code, go.mod, test, build, benchmark, CI, or operations. Continue from actual GitHub main HEAD, not historical handoff SHAs.

## 25. API-001b-NORD2 approval and Worker / Done design handoff (2026-11-16)

**Verified baseline before documentation commit:** main@45485f7c23390c2689469c959a24ee4588b4a800. Owner explicitly **APPROVED N-ORD2**. Binding authority: [Decision Log](DECISION_LOG.md) § API-001b-NORD2.

**Approved Notification contract:** Completion and OnClose execute in distinct, independently bounded sublanes. OnClose may execute concurrently with an already-running Completion callback for the same Session; it does not wait for Completion return. A single unpartitioned Notification worker pool with no reserved OnClose capacity would violate this decision. OnClose remains best-effort/at-most-once. Forced Close A still cancels not-yet-started Completion events and does not terminate already-running callbacks.

**Worker design (proposal only):** separate bounded Completion and OnClose worker capacity per owning Server/Client instance; Completion event queue uses the already-reserved PERF-003 per-Session + aggregate Request completion credits; OnClose has its own at-most-one-per-Session event and independent global active+queued event budget. Retain active-worker charges for callbacks surviving Session closure/reconnect. Prefer bounded lazy worker pools and fair ready-Session scheduling; never one goroutine per event. Historical candidate (superseded by §27): at most one active Completion callback per Session. The owner subsequently approved configurable same-Session concurrency under C-ORD-B; see §27. FIFO start selection remains by terminal-settlement enqueue order, while callback return order is not guaranteed for concurrency greater than 1. Numeric worker counts, event caps, fairness and per-Server vs process-wide aggregate are **OPEN**.

**Done design:** the preceding Done proposal has been approved as API-001b-DONE-A; see §26. The read-only Session Done() <-chan struct{} closes after internal teardown and immutable terminal-cause publication, never waits for user callbacks, and gates OnClose eligibility. A running Completion retains its worker and PERF-003 credit until return; OnClose may overlap it under N-ORD2. The exported terminal-cause accessor and Close return semantics remain OPEN.

**Next work:** finalize numeric Completion concurrency default and worker/event capacity dimensions, aggregate scope, OnClose saturation, Completion payload-byte/frame-size bounds, PERF-003 count/event limits, API-002 timeout/Stop/reconnect and API-003 package/module. Do not infer numeric values from earlier examples.

**Guardrail:** no Go/C++ code, go.mod, tests, builds, benchmarks, CI or operations. All worker values remain proposals; no numeric defaults were invented.

## 26. API-001b-DONE-A — Owner-approved Session Done contract and next Worker design (2026-11-16)

**Owner decision:** Option A is **APPROVED**. Binding source: [DECISION_LOG.md](DECISION_LOG.md) § API-001b-DONE-A.

**Contract:** Session exposes a read-only **Done() <-chan struct{}** signal. It closes exactly once after admission stops, pending Request outcomes settle once, on a Forced Close path, unstarted Application/Completion callbacks are cancelled under Forced Close A; transport and internal Reader/Writer/control loops stop, timers/registry/internal accounting are cleaned up, and terminal cause is immutable. Done never joins or waits for any running Application, Completion or OnClose callback. An admitted OnClose event is eligible only after Done closes; under N-ORD2 it may overlap a Completion callback already running for the same Session. OnClose remains best-effort/at-most-once.

**Still open:** terminal-cause accessor name/signature; Close return semantics; numeric Completion concurrency default; worker/event counts and aggregate scope; OnClose event saturation; Completion payload-byte/frame-size bounds; PERF-003 numeric limits and optional incoming event-count cap; API-002 and API-003. C-ORD-B policy itself is closed.

**Worker design recommendation (not approved as API defaults):** three separate bounded callback classes (Application, Completion, OnClose); per-Session FIFO work queues feeding finite bounded owner-instance worker capacity; fair ready-Session scheduling; no goroutine per event; no global/registry lock while invoking user code. Keep the resource ledgers distinct:
- Application waiting frames: Q-009/Q-010 byte caps; active handlers: Q-003-R1 per-Session concurrency plus a still-open Server aggregate active-worker cap.
- Completion lifecycle: PERF-003 per-Session + aggregate Request credits reserved before SendRequest acceptance and held through pending, queued, and running callback; active Completion Worker permit is a separate physical-execution cap.
- OnClose: at most one event per Session, independent event admission and active Worker capacity; it never consumes Request completion credits. Done closes even if OnClose cannot be admitted.
- Running callbacks from retired Session generations continue consuming the owning Client/Server worker capacity until return, including after reconnect.

**Next decision:** select the within-Completion concurrency/ordering contract. Recommended alternatives and consequences are recorded in [the detailed review](NETA_GO_API_001B_FORCED_CLOSE_NOTIFICATION_REVIEW_2026-11-16.md) §11.8. All numeric limits remain OPEN.

## 27. API-001b-CORD-B approval — configurable Completion concurrency (2026-11-16)

**Owner decision:** C-ORD-B is **APPROVED**. Binding authority: [DECISION_LOG.md](DECISION_LOG.md) § API-001b-CORD-B.

**Contract:** positive configurable maximum concurrent Completion callbacks per Session; 1 means serial, values greater than 1 permit overlap. The Session dispatcher preserves FIFO start selection by serialized per-Session terminal-result settlement/enqueue order, not SendRequest admission order. Callback return order is not guaranteed for concurrency greater than 1. Shared mutable state used by concurrent Completion callbacks is the application's synchronization responsibility. Per-Session concurrency is intersected with a finite aggregate active Completion-worker ceiling; no goroutine-per-Request.

**Still open:** numeric default and public option name/range; active worker ceilings and aggregate scope; Completion queue/event and payload-byte/frame-size bounds; OnClose saturation; terminal-cause accessor and Close return behavior; API-002 Stop/drain/reconnect and API-003 module/package.

**Guardrail:** design/docs only. No Go/C++ implementation, tests, benchmarks, builds, CI, dependencies or operations.


## 28. WORKER-001 — Owner-scoped Worker capacity and next design decision (2026-11-16)

**Verified baseline before this documentation sequence:** `main@525487737c1b75c62d021a391a395e03c1aadb1e`.  
**Owner decision:** WORKER-001 **Option A APPROVED**.

### Binding contract

- Each Client instance and each Server instance owns an independent callback-worker resource domain.
- All Sessions of one Server share its Server-owned budgets.
- All reconnect generations of one Client share its Client-owned budgets.
- A callback started by a retired Session generation remains charged to the owning instance until it returns; reconnect cannot reset the charge.
- Independent Client/Server instances do not share a hidden process-global worker pool or mandatory process-global active-worker cap.

This decision fixes only the worker **ownership scope**. It does not select numeric worker counts, physical pool layout, per-class aggregate-cap policy, queue/event limits, payload-byte bounds or OnClose saturation behavior.

### Synchronized design records

- [DECISION_LOG.md](DECISION_LOG.md) — binding WORKER-001 entry.
- [Worker Capacity & Resource Accounting Design](NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md) — consolidated resource ledgers; WORKER-001 and WORKER-002 are approved; WORKER-003 is the next open decision.
- [API-001b review](NETA_GO_API_001B_FORCED_CLOSE_NOTIFICATION_REVIEW_2026-11-16.md), [PERF-002/003 design](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md), [Public API design](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md), [Performance Contract](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md) and [Resource Admission design](NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md) updated consistently.

### Next decision at that time — WORKER-002 (SUPERSEDED / RESOLVED BY §29)

The owner subsequently approved explicit independent owner-wide active-worker ceilings for Application, Completion and OnClose. See §29 and the binding Decision Log entry.

**Guardrail:** documentation/design only. No Go/C++ code, go.mod, tests, benchmarks, builds, dependencies, CI or operational changes.

## 29. WORKER-002 — Independent owner-wide active-worker ceilings (OWNER APPROVED, 2026-11-16)

**Owner selection:** WORKER-002 Option A.

### Binding contract

Each Client and Server instance has three independently configurable aggregate active-worker ceilings:

- Application callbacks.
- Completion callbacks.
- OnClose callbacks.

Per-Session concurrency is intersected with the remaining owner-wide ceiling for the same class. Classes cannot borrow or consume one another's active permits. Ceilings count physically executing callbacks; queued/event populations are separately bounded.

WORKER-001 owner scope remains binding across all Sessions and Client reconnect generations. A started callback from a retired Session remains charged to the same owner/class ceiling until it returns. There is no mandatory process-global active-worker ceiling.

### Synchronized documents

- [DECISION_LOG.md](DECISION_LOG.md) — binding WORKER-002 entry.
- [Worker Capacity & Resource Accounting Design](NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md) — detailed capacity model and WORKER-003 proposal.
- API-001b review, PERF-002/003 design, Public API design, Performance Contract and Resource Admission design updated.

### Next decision — WORKER-003

Choose the OnClose saturation policy: skip a new OnClose callback when the owner's bounded active+queued event budget is full (recommended, consistent with best-effort delivery), or reserve an event slot at Session admission and apply backpressure to new Session/reconnect admission when no reservation is available.

Numeric defaults and public option names remain open. No implementation, tests, benchmarks, builds or operational changes.

## 30. WORKER-003 — OnClose event-budget saturation (OWNER APPROVED, OPTION A, 2026-11-16)

The owner selected Option A: when the owner's bounded OnClose event budget is full, skip the new OnClose invocation permanently.

### Binding behavior

- The owner-scoped event budget counts queued + running OnClose events; at most one event per Session.
- After Session Done closes, the engine makes one nonblocking reservation attempt.
- If full, skip OnClose with no retry, overflow goroutine, hidden queue or wait.
- An admitted event holds its event credit until callback return.
- Done, terminal cause, transport cleanup and reconnect are unaffected.
- Client reconnect generations share the same OnClose event budget.

### Next decision at that time — WORKER-004 (RESOLVED BY §31)

This was the pending choice when WORKER-003 was first recorded. The owner subsequently approved Option A; the binding result is recorded in §31 and DECISION_LOG.md.

No numeric event capacity or implementation authorized. No code, tests, benchmarks, builds or operational changes.


## 31. WORKER-004 — Three class-isolated worker pools (OWNER APPROVED, OPTION A, 2026-11-16)

The owner-approved WORKER-004 Option A is now registered in the Decision Log and synchronized design records. Initial registration commit: `fd3b4bdbe9ab424a444c237dd6017b99b60c3193`.

### Binding contract

- Every Client and Server owner has three independent pools: Application, Completion and OnClose.
- Each pool owns its own scheduler, ready-work queue, dispatch path, lock domain and wake-up mechanism.
- Worker creation is lazy. A worker is reused only within its own class. No goroutine is created per Request, frame or callback.
- A worker executes one callback synchronously. A blocked class cannot consume another class's workers or scheduler resources.
- Worker goroutine count per class is bounded by the corresponding WORKER-002 ceiling. Idle workers do not hold active-callback permits, but their goroutines/stacks remain resource usage.
- Internal protocol and transport processing remains outside all user callback pools.
- Shared internal worker-loop code is allowed; shared pools, queues, dispatch locks and wake-up state across callback classes are not.
- WORKER-001 owner scope, WORKER-002 independent class ceilings and WORKER-003 OnClose event saturation remain binding. No process-global pool or ceiling is introduced.

### Synchronized documents

- [DECISION_LOG.md](DECISION_LOG.md) — binding WORKER-004 approval.
- [Worker Capacity & Resource Accounting Design](NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md) — WORKER-004 contract and WORKER-005 proposal.
- [API-001b review](NETA_GO_API_001B_FORCED_CLOSE_NOTIFICATION_REVIEW_2026-11-16.md).
- [PERF-002/003 design](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md).
- [Performance Contract](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md).
- [Public API design](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md).
- [Resource Admission design](NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md).

### Next decision at that time — WORKER-005 (RESOLVED BY §32)

The owner subsequently approved finite idle retirement (Option B), with a zero warm-idle floor. The binding result is recorded in §32 and DECISION_LOG.md.

**Guardrail:** documentation/design only. No Go/C++ code, go.mod, tests, benchmarks, builds, dependencies, CI or operational changes.


## 32. WORKER-005 — Finite idle worker retirement (OWNER APPROVED, OPTION B, 2026-11-16)

The owner approved Option B: idle workers retire after a finite configurable grace period.

### Binding contract

- Worker pools remain class-isolated per WORKER-004 and workers are created lazily.
- After callback return, a worker with no dispatchable work may enter Idle and start its class-specific finite grace timeout.
- Work arriving before expiry reuses the idle worker. If the timeout expires with no work, the worker atomically removes itself from the pool count and exits.
- The default warm-idle floor is zero. A class pool may return to zero idle goroutines after sufficient inactivity.
- Application, Completion and OnClose idle timeouts are independently configurable. Numeric defaults/ranges are deferred to WORKER-009.
- A running or permanently blocked callback is never retired by the idle timeout; its active permit remains charged until actual return.
- Retirement never discards queued work or releases queue-byte, Request or event credits.
- Enqueue versus retirement has one linearization point; no lost wakeup, stranded ready Session or worker-count overshoot is permitted.
- No goroutine per timeout and no process-global reaper. Reusable timer/wait state is preferred.
- Owner shutdown/drain behavior remains API-002.

### Synchronized documents

- [DECISION_LOG.md](DECISION_LOG.md) — binding WORKER-005 approval.
- [Worker Capacity & Resource Accounting Design](NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md) — WORKER-005 contract and WORKER-006 proposal.
- API-001b review, PERF-002/003 design, Performance Contract, Public API design and Resource Admission design — lifecycle and scheduling constraints.

### Next decision at that time — WORKER-006 (RESOLVED BY §33)

The owner subsequently approved Option A: per-class round-robin, one callback per eligible Session turn. The binding result is recorded in §33 and DECISION_LOG.md.

**Guardrail:** documentation/design only. No Go/C++ code, tests, benchmarks, builds, dependencies, CI or operational changes.


## 33. WORKER-006 — Fair Scheduling Between Sessions (OWNER APPROVED, OPTION A, 2026-11-16)

The owner approved per-class round-robin scheduling, with one callback dispatch per eligible Session turn.

### Binding contract

- Application, Completion and OnClose each have an independent FIFO ready-Session rotation.
- A Session has at most one reusable ready node per class pool.
- Each turn dispatches one callback from the head Session's own FIFO. If work remains and a per-Session concurrency slot is free, that Session moves to the tail.
- If no work remains, its ready state is cleared. If its concurrency limit is full, it is temporarily ineligible and is reconsidered at the tail when a callback returns.
- Per-Session FIFO callback-start order is preserved. Completion follows C-ORD-B terminal-result settlement/enqueue order, not SendRequest admission order; parallel return order is unspecified.
- Fairness applies to continuously eligible Sessions within one owner/class. It does not promise equal CPU time or preempt callbacks.
- Pools, queues, locks and wakeups remain class-isolated. No lock is held during user code. No per-callback goroutine or per-turn allocation is required.
- Forced Close/start linearization and WORKER-001..005 remain unchanged.

### Synchronized documents

- [DECISION_LOG.md](DECISION_LOG.md) — binding WORKER-006 approval and WORKER-007 proposal.
- [Worker Capacity & Resource Accounting Design](NETA_GO_WORKER_CAPACITY_RESOURCE_ACCOUNTING_DESIGN_2026-11-16.md) — approved scheduler contract and WORKER-007 alternatives.
- [Resource Admission design](NETA_GO_RESOURCE_ADMISSION_DESIGN_2026-11-16.md) and [PERF-002/003 design](NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md) — queue and credit accounting.
- [API-001b review](NETA_GO_API_001B_FORCED_CLOSE_NOTIFICATION_REVIEW_2026-11-16.md), [Public API design](NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md) and [Performance Contract](NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md).

### Next decision at that time — WORKER-007 (RESOLVED BY §34)

The owner subsequently approved Option A: per-Session incoming/outgoing Application frame-count caps plus one aggregate Server count covering both directions. Completion and OnClose reuse their existing independent credits.

**Guardrail:** documentation/design only. No Go/C++ code, tests, benchmarks, builds, dependencies, CI or operational changes.


## 34. WORKER-007 — Queue Capacity and Event Capacity (OWNER APPROVED, OPTION A, 2026-11-16)

The owner approved per-Session incoming and outgoing Application frame-count ceilings plus one Server-aggregate queued Application frame-count ceiling across both directions. Incoming count saturation closes only the offending Session under Q-009/Q-010; outgoing count saturation returns Queue Full and keeps the Session. Outgoing frames remain counted through full Writer completion. Incoming Request count is released at callback start. Completion reuses PERF-003 Request credits; OnClose reuses WORKER-003 queued+running event credits. No duplicate Completion/OnClose event credit or shared cross-class budget is added. Existing byte limits and 4 KiB Control reserve remain independent. Numeric count defaults/ranges and public option names remain for WORKER-009/API-004.

### Next decision at that time — WORKER-008 (RESOLVED BY §35)

The owner subsequently approved Option A: separate owner-scoped retained-payload byte ledgers for Application and Completion classes. The binding contract is recorded in DECISION_LOG.md and Worker Capacity Design §15.

**Guardrail:** documentation/design only. No Go/C++ code, tests, benchmarks, builds, dependencies, CI or operational changes.


## 35. WORKER-008 — Resource Accounting and Payload Memory Ceiling (OWNER APPROVED, OPTION A, 2026-11-17)

The owner approved two independent retained-payload byte ledgers: Application and Completion. Each has per-Session and aggregate per-owner ceilings; Client reconnect generations share the same Client owner ledger. Application covers inbound Request storage from validated-header reservation through active OnRequest return/cancellation and outgoing private frame storage through full Writer completion. Completion covers matched Response storage from before body allocation through queued/running Completion return or Forced Close A cancellation. Queue byte/count limits remain independent sub-limits and are not added to retained-payload bytes as if they were separate physical allocations. Queue-to-active releases queue-only charges while the retained-byte charge follows the same buffer. Started callbacks remain charged until actual return; unstarted cancelled callbacks release once. No user-visible inbound buffer recycling.

**Completion-byte exhaustion — CLOSED / OWNER APPROVED OPTION A (2026-11-17):** when a valid, in-limit Response matches a live Pending Request but its full declared frame cannot reserve Session or owner Completion bytes, do not allocate its Body. Drain exactly the declared Body through one small fixed-size scratch buffer. If drain completes and no competing terminal event has won, invoke the normal Completion callback once with no Response payload and a typed terminal Resource Capacity error; keep the Session open and retain its existing Request credit until callback return/cancellation. If timeout/close/another terminal event wins during drain, it remains the sole settlement; do not invoke a duplicate callback. If drain fails due to EOF, timeout/read error or concurrent transport close, close the Session under the existing transport-error/Forced Close policy. Malformed or over-maximum frames use protocol-error handling. Exact read-timeout behavior remains API-002 work.

**Still open before Architecture Freeze:** golden-frame artifacts and Go/C++ cross-language confirmation against pinned Pinex HEAD; API-002/API-003 decisions. WORKER-009 numeric limits/defaults and hard validation ranges are closed. Maximum Frame Size is source-verified as 1 MiB total. No silent Response drop is allowed.

### Next decision — WORKER-009

WORKER-009A, WORKER-009B1 and WORKER-009B2 are CLOSED / OWNER APPROVED. B1 defaults: Application and Completion callback concurrency=1 per Session; Application, Completion and OnClose idle grace=30s independently. B2 count/event and Request-credit defaults are recorded in §38. Next owner decision: WORKER-009B3 retained-payload byte defaults.

**Guardrail:** documentation/design only. No Go/C++ code, tests, benchmarks, builds, dependencies, CI or operational changes.


## 36. WORKER-009A — CPU-derived worker defaults (OWNER APPROVED OPTION A, 2026-11-17)

The owner approved Option A. At Client/Server effective-configuration construction, capture P=max(1,runtime.GOMAXPROCS(0)) once. Resolve owner-wide active-worker defaults as Application=min(max(4,4P),128), Completion=min(max(2,2P),64), and OnClose=min(max(2,P),32). These are lazy worker ceilings, not eager goroutine counts. The resulting values remain immutable for the owner lifetime; later CPU quota/GOMAXPROCS changes do not resize a live instance. All other queue, count and retained-byte quotas remain fixed finite defaults, independently configurable. The formula caps are not hard maxima for explicit overrides; WORKER-009C will decide those.

**Next:** WORKER-009B3 — review retained Application and Completion payload-byte defaults. WORKER-009B2 is CLOSED / OWNER APPROVED; its six count/event defaults and saturation rules are recorded in §38 and DECISION_LOG.md.

**Guardrail:** documentation/design only. No code, tests, benchmarks, builds, dependency or operational changes.


## 37. WORKER-009B1 — per-Session concurrency and idle retirement (OWNER APPROVED, 2026-11-17)

The owner approved all five defaults: Application callback concurrency=1 per Session; Completion callback concurrency=1 per Session; Application idle grace=30s; Completion idle grace=30s; OnClose idle grace=30s. All are independently configurable. Concurrency 1 preserves serial callback execution by default; higher positive values remain configurable subject to the existing per-Session and owner-wide ceilings. Each idle grace starts only after callback return and when no dispatchable work exists; it never interrupts running callbacks. WORKER-005's zero warm-idle floor, class isolation and atomic enqueue/retirement rules remain binding. Explicit zero is not Unlimited or an immediate-retirement shorthand and is invalid for these positive settings.

**Next:** WORKER-009C — proposed hard maxima, valid ranges, cross-field constraints and semantic Functional-Option mapping. WORKER-009B2 and WORKER-009B3 are CLOSED / OWNER APPROVED.

**Guardrail:** documentation/design only. No code, tests, benchmarks, builds, dependency or operational changes.


## 38. WORKER-009B2 — count/event and Request-credit defaults (OWNER APPROVED OPTION A, 2026-11-17)

The owner approved all six proposed defaults as official V1 defaults, independently configurable through typed Functional Options:

| Setting | Approved default | Scope |
|---|---:|---|
| OnClose event credits | 1,024 | Per Client/Server owner; queued + running |
| Incoming Application frames | 256 | Per Session |
| Outgoing Application frames | 256 | Per Session, including Writer-owned frame until full Write/discard |
| Aggregate queued Application frames | 65,536 | Per Server, incoming + outgoing |
| Outstanding Requests | 128 | Per Session, full async lifecycle through Completion callback return/cancellation |
| Aggregate outstanding Requests | 32,768 | Per Client/Server owner; Client reconnect generations share the same budget |

Incoming local or aggregate count saturation closes only the offending Session. Outgoing local or aggregate count saturation returns Queue Full and keeps the Session open. OnClose saturation permanently skips the new event. Request-credit saturation rejects a new callback-based SendRequest before enqueue/transmission with a typed capacity error; it does not close the Session. SendNoWait and SendResponse do not consume Request credits. Completion reuses the PERF-003 Request credit; OnClose reuses the WORKER-003 event credit. Queue bytes/counts, active-worker permits, Request/Event credits and retained-payload bytes remain distinct admission ledgers, not additive physical-memory totals. Aggregate frame-count and Request-credit defaults are intentionally lower than the sum of their theoretical per-Session ceilings; cross-field validation must not force the aggregate values to equal or exceed those products. These values are defaults, not WORKER-009C hard maxima.

**Next:** WORKER-009C — owner review of proposed hard maxima, valid ranges, cross-field constraints and semantic Functional-Option mapping.

**Guardrail:** documentation/design only. No code, tests, benchmarks, builds, dependency or operational changes.

## 39. WORKER-008 Completion retained-byte exhaustion — OWNER APPROVED OPTION A (2026-11-17)

The owner selected Option A. For a syntactically valid, in-limit Response matched to a live Pending Request, if the declared full frame cannot reserve the Session or owner Completion retained-byte budget, the Reader must not allocate a Body-sized payload buffer. It drains exactly the declared Body through a small fixed-size scratch buffer. After successful drain, if the Request has not already been terminally settled, invoke its normal Completion callback once with no Response payload and a typed terminal Resource Capacity error; keep the Session open. The existing PERF-003 Request credit remains held through callback return or Forced Close A cancellation; no second Completion/event credit is created. A timeout/close/other terminal event that wins during drain remains the sole settlement. Drain/transport failure closes the Session under the existing transport-error/Forced Close policy and does not also emit the Resource Capacity completion. Malformed or over-maximum frames use protocol-error handling. The scratch buffer is bounded independently of Body length; exact read-timeout behavior remains API-002 work.

**Next:** WORKER-009B3 — review the four proposed retained-payload byte defaults; then WORKER-009C.

**Guardrail:** documentation/design only. No code, tests, benchmarks, builds, dependency or operational changes.

## 40. WORKER-009B3 — retained-payload byte defaults (OWNER APPROVED OPTION A, 2026-11-17)

The owner approved all four values as official V1 defaults:

| Setting | Approved default | Scope |
|---|---:|---|
| Retained Application bytes | 16 MiB | Per Session |
| Aggregate retained Application bytes | 512 MiB | Per Client/Server owner |
| Retained Completion bytes | 16 MiB | Per Session |
| Aggregate retained Completion bytes | 256 MiB | Per Client/Server owner |

The limits are independent, finite and lazily enforced; they do not preallocate memory or define process RSS. Client owner budgets are shared across reconnect generations. Queue byte/count limits remain independent admission sub-limits and are not added to retained-payload bytes as separate physical allocations. Queue-to-active transitions release queue-only charges while retained-byte accounting follows the same payload. Started callbacks remain charged until actual return; user-retained inbound data after callback return is outside the library-owned ledger.

**Next:** WORKER-009C owner review.

## 41. WORKER-009C — hard maxima and validation (CLOSED / OWNER APPROVED / OPTION A, 2026-11-17)

The owner approved all proposed WORKER-009C hard maxima, valid ranges, cross-field validation rules and semantic Functional-Option mapping.

| Setting | Hard maximum |
|---|---:|
| Application Workers / Owner | 512 |
| Completion Workers / Owner | 256 |
| OnClose Workers / Owner | 128 |
| Application Concurrency / Session | 32 |
| Completion Concurrency / Session | 32 |
| Worker Idle Grace | 10m (minimum 1ms) |
| OnClose Event Credits / Owner | 4,096 |
| Incoming Frames / Session | 1,024 |
| Outgoing Frames / Session | 1,024 |
| Aggregate Frames / Server | 262,144 |
| Outstanding Requests / Session | 512 |
| Outstanding Requests / Owner | 131,072 |
| Application Retained Bytes / Session | 64 MiB |
| Application Retained Bytes / Owner | 2 GiB |
| Completion Retained Bytes / Session | 64 MiB |
| Completion Retained Bytes / Owner | 1 GiB |

Count and ordinary byte limits have minimum 1; retained-byte limits have minimum 10 bytes. Validate after applying every Functional Option, and complete validation before creating sockets or goroutines. `EnquireLinkIdleInterval=0` remains the only intentional zero exception. Owner and Session limits are independent; aggregate limits may be lower than theoretical Session sums. Session concurrency intersects owner worker ceilings at dispatch. Queue, retained-byte, Request, OnClose and Worker Permit ledgers remain independent with no payload double-counting. All calculations/counters are overflow-safe. Limits are per Client/Server owner, not process-wide. Ten bytes covers only a header-sized frame. The 1 MiB total-frame maximum is source-verified against pinned Pinex C++ 1.5.0; it is a separate Protocol Compatibility fact, not a WORKER-009C setting.

**Typed Functional Options:** one independent option per semantic setting, mapped to Client/Server owner or Session scope as appropriate; aggregate queued Application frame count is Server-only; worker idle grace is separately configurable per class. Defaults remain when omitted; explicit values override only their own setting. Exact exported identifiers and constructor/Session placement remain API-001 work.

**Status:** CLOSED / OWNER APPROVED / OPTION A. Implementation remains NOT AUTHORIZED.


## 42. PROTOCOL-001 — Pinex 1.5.0 source baseline and Maximum Frame Size (SOURCE VERIFIED, 2026-11-17)

Pinned source snapshot: `majiddarvishan/pinex` branch `develop`, HEAD `f7bd1eb779baff0d10e624f20522df345e6ee747`; CMake declares version 1.5.0. In `session.hpp`, `receive_buf_` is `flat_buffer<uint8_t, 1024 * 1024>`; `command_length` includes the 10-byte Header and values above the fixed buffer capacity are rejected. Exact maximum accepted inbound Frame: **1,048,576 bytes total**, maximum Body **1,048,566 bytes**. The bound applies before Bind and after Bind. Pinex's send path does not preflight the same cap, but the receiving Pinex Session rejects over-limit frames; neta-go must enforce the limit on both inbound and outbound frames. Re-pin/re-audit the branch before future implementation or cross-language tests. Golden-frame and real socket-level Go↔C++ confirmation remain OPEN; no tests or code were run.


## 43. API-002 — Lifecycle, Timeout, Reconnect and Shutdown (DESIGN IN PROGRESS, 2026-11-17)

Detailed draft: `NETA_GO_API_002_LIFECYCLE_TIMEOUT_SHUTDOWN_DESIGN_2026-11-17.md`. It preserves all approved Done/Forced Close/Notification/Worker contracts and proposes context-aware terminal Client/Server Stop that waits for internal Done but never joins arbitrary callbacks. **API-002-01 CLOSED / OWNER APPROVED / OPTION A:** RequestTimeout=30s from successful local admission, including Queue/Writer/peer time. **API-002-02 CLOSED / OWNER APPROVED / OPTION A:** FrameAssemblyTimeout=30s absolute from first byte of each Frame Header on a Bound Session, not reset by progress; expiry closes only that Session. **API-002-03 CLOSED / OWNER APPROVED / OPTION A:** ConnectTimeout=30s absolute per Client Dial attempt, including DNS and TCP establishment; earlier caller Context deadline/cancellation wins; timeout creates no Session and does not enable reconnect. These settings are independently configurable and positive-only. Pre-Bind remains 30s absolute from TCP accept. Next owner decision: API-002-04 Bind response timeout. Unbind, write-stall, reconnect, Stop aggregation and API-001 surface names remain open. No implementation or tests authorized.


## 44. API-002-01 — Request Timeout (CLOSED / OWNER APPROVED / OPTION A, 2026-11-17)

- Default: **30s**, independently configurable per Client/Server owner with typed Functional Options; positive only; zero does not disable.
- Start: immediately after successful atomic local admission (Sequence + Request credit + queue frame/bytes + retained-payload reservation + FIFO insertion). Queue wait, Writer wait/Write and peer response all consume the deadline.
- If timeout wins before Writer claim: cancel queued frame; release queue and queued-payload charges exactly once; never transmit. Deliver one timeout Completion; retain Request credit/Sequence protection until Completion callback return or permitted cancellation.
- If Writer claim wins first: send ownership cannot be revoked; late Response is ignored; Writer-owned memory stays accounted until Write completion or transport teardown.
- Timeout alone does not close Session; timeout/Response/Close race has one terminal settlement winner.
- Rejected: start-after-full-Write and per-call-required timeout.

**Next owner decision:** API-002-04 Bind response timeout. Proposal: 30s absolute deadline from TCP establishment, before Bind Write, covering Bind Write and matching Bind Response wait. No implementation/tests authorized.


## 45. API-002-02 — Frame Assembly Timeout (CLOSED / OWNER APPROVED / OPTION A, 2026-11-17)

- **Default:** 30s absolute deadline per inbound Frame on a Bound Session.
- **Start:** first byte of that Frame's Header observed by Reader; one deadline covers remaining Header and full declared Body. Incremental progress never resets it.
- **Expiry:** close only the affected Session via existing terminal/Forced Close path. No byte skipping or stream resynchronization; other Sessions remain unaffected.
- **Partial Header:** retain only bounded parser/header storage until a complete valid Header exists; no Body allocation from incomplete/unvalidated length. Release partial parser state once on timeout.
- **Partial Body:** after Header validation, WORKER-008 full declared-frame retained-byte and applicable queue/count reservations remain held until full read or terminal cleanup. On timeout, release reservation and partial storage exactly once.
- Completion retained-byte failure's bounded scratch-buffer Body drain remains under the same original Frame Assembly deadline. If it expires, close Session and do not emit Resource Capacity Completion.
- Applies to Application and protocol/control Frames on Bound Sessions. No callback for an incomplete Frame.
- Independently configurable per Client/Server owner via typed Functional Options; positive-only, explicit zero invalid; accepted Server Sessions inherit the Server value. No additional hard maximum approved.
- The absolute 30s Pre-Bind handshake deadline from TCP accept remains unchanged and is not extended by Frame progress. Pinex C++ 1.5.0 has no separate equivalent deadline; no wire change.

**Next:** API-002-04 Bind response timeout. Proposal: 30s absolute from TCP establishment, covering Bind Write and response wait. No implementation/tests authorized.


## 46. API-002-03 — TCP Connect Timeout (CLOSED / OWNER APPROVED / OPTION A, 2026-11-17)

- **Default:** 30s absolute per Client Dial attempt.
- **Start/scope:** immediately before Dial; includes DNS/name resolution and TCP establishment. No DNS lookup outside the bounded context.
- **Context precedence:** caller cancellation always applies; an earlier caller deadline wins. If the caller has no earlier deadline, internal ConnectTimeout bounds the attempt.
- **Timeout outcome:** cancel only the current Dial attempt. No Session is created/published, no Bind is sent, and no Session Reader/Writer or callback worker starts. Close a socket returned concurrently after timeout has won.
- **Success:** if TCP establishment wins, proceed to the separate Bind handshake and its own deadline; ConnectTimeout is not reused.
- **Configuration:** Client-only typed Functional Option; positive finite duration; zero invalid; no additional hard maximum approved.
- This does not enable AutoReconnect or authorize retries. No wire change; no implementation/tests authorized.

**Next:** API-002-04 Bind response timeout. Proposal: 30s absolute from TCP establishment, before Bind Write, including Bind Write and matching response wait.


## 47. Consolidated Architecture Freeze decision register (2026-11-17)

All remaining owner choices are collected in [NETA_GO_ARCHITECTURE_FREEZE_DECISION_REGISTER_2026-11-17.md](NETA_GO_ARCHITECTURE_FREEZE_DECISION_REGISTER_2026-11-17.md): API-002-04..08, final API-001 public surface, API-003 module/package boundaries and PROTOCOL-001 adoption of the source-verified 1 MiB total-frame ceiling. The register is a proposal, not an approval. No implementation, tests, benchmarks, builds or dependency changes are authorized.

## 48. Architecture Freeze completed — 2026-11-17

**Owner approval:** Option A for API-002-04..08, API-001, API-003 and PROTOCOL-001.  
**Status:** ARCHITECTURE FROZEN — all fundamental owner decisions CLOSED / OWNER APPROVED.  
**Implementation:** NOT AUTHORIZED.

Binding final records: DECISION_LOG.md; NETA_GO_API_002_LIFECYCLE_TIMEOUT_SHUTDOWN_DESIGN_2026-11-17.md; NETA_GO_PUBLIC_API_001_DESIGN_2026-11-16.md; NETA_GO_API_003_MODULE_PACKAGE_ARCHITECTURE_2026-11-17.md; NETA_GO_API_004_CONFIGURATION_CONTRACT_2026-11-16.md; PINEX_WIRE_PROTOCOL_2026-11-16.md; NETA_GO_ARCHITECTURE_FREEZE_AND_IMPLEMENTATION_ROADMAP_2026-11-17.md.

No fundamental owner decision remains open. Golden-frame vectors, bidirectional Go↔C++ socket verification, correctness/race/fuzz/soak tests, baseline benchmarks and evidence-driven PERF-004 are implementation validation tasks, not architecture blockers. Begin none of them until explicit implementation authorization. The previous §47 decision register is now CLOSED / OWNER APPROVED / OPTION A for all eight entries.


## Implementation Authorization — Phase 1 (2026-11-17)

Owner explicitly authorized Phase 1 in this conversation: «آره، اجازه داری». This supersedes the previous global NOT AUTHORIZED boundary only for Phase 1.

- **Authorized:** module skeleton (go.mod, root package neta), typed Client/Server/Session Functional Options, immutable effective configuration, approved defaults, apply-all-then-validate construction, WORKER-009C validation and checked arithmetic, public configuration errors/state declarations required by API-001, focused tests and CI.
- **Baseline before this authorization:** f3f525e5f36f65235a4c8e023cfafb4bfd6b5737.
- **Current Phase 1 test-hardening commit:** 18bec96bb13cbdfa5a7819301b23d61e3fb3db75 (Server-side WORKER-009C maximum/minimum and final-option precedence tests; CI pending at time of this handoff update).
- **Explicitly not authorized:** Phase 2 Wire Protocol, transport/runtime, worker scheduler, reconnect, cross-language integration, benchmarks and deployment. Obtain separate owner authorization before starting Phase 2.
- No approved architecture decision is reopened.


## Phase 1 completion evidence — 2026-11-17

**Status:** COMPLETE / CI PASS.

- Module path and Go module: github.com/majiddarvishan/neta-go, Go 1.23.
- Sole public package: root package neta.
- Typed ClientOption, ServerOption and SessionOption with independent functional settings.
- Immutable effective configuration; all options are applied before final validation.
- Approved defaults and WORKER-009C maxima/ranges are enforced before any socket or goroutine is created.
- EnquireLinkIdleInterval=0 is the sole approved duration-zero exception.
- Owner and Session budgets remain independent; checked uint64 add/subtract/multiply helpers reject overflow/underflow.
- Nil typed options are rejected; Session option slices are snapshotted.
- TCP endpoint syntax is validated without opening sockets.
- Focused tests cover defaults, GOMAXPROCS worker defaults, zero rules, hard maxima, inclusive boundaries, Client and Server owner budgets, independent cross-field limits, final option precedence and arithmetic guards.
- Latest verified commit: cb3bdbc2964c1a0444cd40684117e1987f4cf092.
- GitHub Actions run 44040206052: PASS — gofmt, go vet, go test, go test -race.

**Next:** Phase 2 — pure-Go internal/wire and Pinex-compatible frame codecs. This phase remains NOT AUTHORIZED until the owner explicitly approves it. No Phase 2 source has been started.


## Phase 2 Authorization — Wire Protocol (2026-11-17)

The owner explicitly approved beginning Phase 2 by replying «ادامه بده» after being asked whether Phase 2 (Wire Protocol) was authorized. This approval is scoped to protocol implementation only.

**Authorized scope:** pure-Go `internal/wire` package; Pinex 1.5.0 10-byte frame header and Big Endian fields; frame encode/decode and size validation; Bind Request/Response with bind_type and C-octet system_id; Stream Request/Response raw body; Unbind and Enquire Link control PDUs; sequence fields/semantics; unit and golden-vector tests; documentation and CI.

**Compatibility reference:** Pinex C++ develop HEAD `f7bd1eb779baff0d10e624f20522df345e6ee747`, version 1.5.0. Re-pin/re-audit if the develop branch moves before interoperability testing.

**Hard protocol maximum:** 1,048,576 bytes total including the 10-byte header; maximum Body 1,048,566 bytes. The limit is fixed, not configurable, and applies inbound and outbound.

**Not authorized:** TCP transport/read-write loops, Client/Server runtime integration, lifecycle/shutdown/reconnect, worker scheduler, resource-admission runtime, cross-language socket test harness requiring C++ execution, benchmarks, release or deployment. Those belong to later phases and require separate owner approval.

No frozen architecture decision is reopened. Phase 1 remains complete with CI PASS. Phase 2 implementation must not import root package `neta` from `internal/wire`; the package uses only the Go standard library.


## Phase 2 — Wire Protocol implementation authorization (2026-11-17)

Owner approval was explicitly granted in this conversation by replying «ادامه بده» to the question asking permission to start Phase 2. This approval supersedes the earlier Phase-2-not-authorized wording, only for the scope below.

**Scope:** pure-Go `internal/wire`; Pinex 1.5.0 frame Header and complete Frame codec; Bind Request/Response; raw Stream Request/Response; empty Unbind and Enquire Link Request/Response; per-Session nonzero Sequence generator; fixed 1 MiB total frame bound; focused golden/boundary/concurrency tests.

**Compatibility source:** Pinex develop HEAD `f7bd1eb779baff0d10e624f20522df345e6ee747`, version 1.5.0. Wire fields are BE u32 length, u8 command, u8 status, BE u32 sequence; Bind body is u8 bind_type followed by NUL-terminated system_id (maximum 19 bytes); Stream body is raw bytes.

**Out of scope / not authorized:** TCP transport, read/write loops, Client/Server runtime integration, Session lifecycle, worker scheduling, resource admission runtime, reconnect, socket-level cross-language test execution, benchmarks, release and deployment. Those require later phase authorization.

Implementation must stay inside `internal/wire`, use only the standard library, and must not import root package `neta`. Root `neta` may depend on `internal/wire`.



## Phase 2 implementation evidence — 2026-11-17

**Phase 2 Wire Codec: COMPLETE** within the explicitly owner-authorized scope.

- Verified implementation commit and code/test baseline: `b026dadd9ad0b33118b05f49477e1412a4255978`.
- Go CI run `44044273742`: PASS — gofmt, go vet, go test, go test -race.
- C++ compatibility CI run `44044273818`: PASS — compile pinned C++ PDU serializer snapshot, regenerate/diff golden frames, run Go golden tests.
- Pinned Pinex source: version 1.5.0, commit `f7bd1eb779baff0d10e624f20522df345e6ee747`.
- Corrected Pinex's omitted/empty Bind Response Body semantics; Go now returns default `bi_direction` and empty system ID.
- Source snapshot provenance and original Git blob hashes: `testdata/neta-cpp-1.5.0/source/SNAPSHOT.md`.

The C++ fixture generator uses actual production PDU serializer templates; its Header writer mirrors the audited private `session::serialize_header` implementation. The private Pinex repo cannot be checked out by neta-go Actions without a cross-repository credential, so the exact pinned source headers are snapshotted in this repo. This is compiled C++ golden compatibility, not live TCP/socket interoperability.

**Not authorized:** Phase 3 TCP transport/read/write loops, runtime integration, Session lifecycle, worker scheduler, resource admission runtime, reconnect, live socket interoperability, benchmarks, release and deployment. Obtain separate owner authorization before starting Phase 3.


## 20. Phase 3 authorization — Session Transport & Lifecycle Engine (2026-11-17)

The owner explicitly authorized Phase 3 in the continuation of chat pg_07 by replying «اره هست و مجوز داری» to the question asking permission to begin Phase 3.

**Authorized scope:** implement the private Session transport/lifecycle engine against the frozen API and protocol contracts:
- one Reader and one serialized Writer per Session; no user callback executes inline in either loop;
- internal Bind/Pre-Bind state transitions and handshake primitives, including the absolute Pre-Bind/Bind deadlines;
- absolute Frame Assembly and per-Frame Writer deadlines, plus idle-only Enquire Link state and matching response timeout;
- Request Sequence allocation/correlation, 30s deadline from successful local admission, exactly-once internal settlement, and late-response suppression;
- Graceful Unbind, Forced Close A, immutable terminal cause, Done publication, and exact internal teardown.

**Implementation boundary:** Phase 3 may use the already-approved per-Session FIFO/queue limits as the minimal bounded transport admission needed by the Writer. It must not implement the full independent queue/count/retained-byte/owner ledgers of Phase 4, the three-class worker scheduler of Phase 5, or Client/Server Dial/Listen/reconnect/session-generation orchestration of Phase 6. Callback dispatch is behind a private interface so Phase 5 can supply the approved isolated bounded workers. No public API expansion, new protocol behavior, third-party dependency, benchmark, release or deployment is authorized.

**Baseline:** remote main HEAD ebf269dc9ba1a8f5d88922cf1e6ab29c99782a05; Phase 1 and Phase 2 remain complete. Pinex compatibility baseline remains version 1.5.0 at f7bd1eb779baff0d10e624f20522df345e6ee747.

**Exit evidence required:** focused net.Pipe transport/lifecycle tests, fragmented and slow-trickle Frame tests, request timeout/late response/close races, partial writes and Writer timeout, Unbind FIFO/timeout, Bind/Pre-Bind handshake tests, gofmt, go vet ./..., go test ./..., and go test -race ./... in GitHub Actions. Live Pinex TCP interoperability remains Phase 7 evidence, not a Phase 3 gate.


## Phase 3 implementation evidence — Session Transport & Lifecycle COMPLETE (2026-11-17)

**Status:** COMPLETE / CI PASS within the explicitly owner-authorized Phase 3 boundary.

- Phase 3 source verification HEAD: `cc0d25e9252b48f38dcddeeb53eaa6e7fe1cbf4c`.
- The Session engine is implemented in `session.go`, `session_control.go`, `session_internal.go` and `session_transport.go`; focused coverage is in `session_test.go`.
- `session_test.go` contains 33 focused Session/transport/lifecycle tests.
- Correctness hardening includes outbound-activity cancellation of queued Enquire Link, ignoring a Response before Writer claim, preserving the first post-Bind Frame Assembly deadline, exact Writer-ownership Write deadline, Request timeout origin after successful local admission, and Unbind Context terminal-cause classification.
- Go GitHub Actions run `44057820360`: PASS — gofmt, go vet ./..., go test ./..., go test -race ./....
- Pinex Wire Compatibility run `44057820405`: PASS — compile the pinned Pinex C++ 1.5.0 production serializer fixture, compare golden Frames, and run Go wire compatibility tests.
- The compatibility workflow is a compiled C++ golden check, not live Go↔Pinex TCP interoperability.

**Still gated:** Phase 4 full resource admission/owner ledgers; Phase 5 bounded callback worker pools; Phase 6 Client/Server orchestration and reconnect; Phase 7 live socket interoperability/fault-injection; Phase 8 performance campaign; Phase 9 release. No work outside Phase 3 is authorized by this result.


## Phase 4 authorization — Resource Admission & Accounting (2026-11-17)

The owner explicitly instructed: “اول این رو اضافه کن به مخزن. بعدش پیاده ساطی رو ادامهع بده” after being shown that Phase 4 was the next implementation phase. This authorizes Phase 4 only.

**Scope:** implement the already-approved per-Session and per-owner resource ledgers; outgoing/incoming Application byte and frame admission; Server aggregate queued Application byte/frame budgets; retained Application/Completion payload accounting; Request credits; OnClose event credits; pre-allocation reservations; fixed-scratch Response drain on Completion-byte exhaustion; exact lifecycle transfer/release and focused tests.

**Strict boundary:** no Phase 5 worker scheduler, no Phase 6 Client/Server Dial/Listen/reconnect orchestration, no Phase 7 live TCP interoperability/fault-injection campaign, no Phase 8 benchmarks/pooling, and no Phase 9 release/deployment. No public API, default, wire or owner decision is reopened.



## Phase 4 implementation evidence — COMPLETE / CI PASS

# Phase 4 — Resource Admission & Accounting Implementation Report

**Status:** COMPLETE / CI PASS  
**Source verification HEAD:** `2935402366603267ba60c181a057d26cf0e7e9a6`  
**Date:** 2026-11-17  
**Authorization:** Explicit owner instruction in this conversation; Phase 4 only.

## Implemented scope

- Added an owner-scoped resource ledger created independently by each `NewClient` and `NewServer`. Session construction supports injection of an existing owner ledger so Phase 6 can share one Client/Server budget across all Sessions and reconnect generations.
- Added checked, mutex-protected reserve/release counters for owner Request credits, retained Application bytes, retained Completion bytes, OnClose event credits and Server aggregate queued Application bytes/frames.
- Server aggregate queue admission is one combined budget across incoming and outgoing Application Frames. Client owners do not acquire the Server-only aggregate queue ceiling.
- Outgoing `SendRequest`, `SendNoWait` and `SendResponse` reserve local queue/count and retained-Application capacity plus owner/Server capacity before allocating/copying the Frame. Rejected capacity does not consume a Sequence or publish Pending state.
- Request credits are reserved before payload copy and remain held through response wait, queued Completion and active Completion callback; they release exactly once on callback return/cancellation or forced terminal cleanup.
- Incoming Stream Request Headers reserve full declared Frame bytes/count and retained-Application bytes before Body allocation. Incoming overload closes only the offending Session. Queue-only bytes/count release at callback start; retained bytes release after callback return/cancellation.
- Matched Stream Responses reserve retained Completion bytes before Body allocation. If capacity is unavailable, the Body is drained with a fixed 4 KiB scratch buffer under the original absolute Frame Assembly deadline; a still-live Request receives a normal Completion with no payload and `ErrCapacity`, while the Session remains open.
- Unknown, late and pre-Writer-claim Responses are drained without allocating a retained Body.
- OnClose is best-effort: it reserves one owner event credit after Done, skips permanently if the owner budget is full, and releases the credit after callback return/cancellation.
- Added idempotent release paths for partial reads, Completion drain timeout, Forced Close A, queued callback cancellation, callbacks that outlive Session Done and Writer-owned frames.

## Verification

- `session_test.go`: 46 focused Session/transport/resource-accounting tests.
- `resource_ledger_test.go`: 8 owner-ledger tests.
- Go Actions [44062568415](https://github.com/majiddarvishan/neta-go/actions/runs/44062568415): PASS — gofmt, go vet ./..., go test ./..., go test -race ./....
- Pinex Wire Compatibility [44062568425](https://github.com/majiddarvishan/neta-go/actions/runs/44062568425): PASS — compile pinned C++ 1.5.0 production serializer fixture, compare golden Frames and run Go wire compatibility tests.
- The compatibility workflow is a golden-frame check, **not** live Go↔Pinex TCP interoperability.

## Explicitly not implemented in Phase 4

- Phase 5 physical callback Worker Scheduler and fair per-Session worker dispatch.
- Phase 6 Client Dial/Server Listen/accept, Bind registry, reconnect and Session-generation orchestration.
- Phase 7 live TCP interoperability/fault-injection campaign.
- Phase 8 performance benchmark/pooling work.
- Phase 9 examples, release and deployment.

No public API, wire behavior, defaults, resource ceilings or frozen owner decisions were changed.



## Phase 5 implementation authorization — 2026-11-17

The owner explicitly approved Phase 5 by replying «آره» in this conversation.

Authorized: implement the frozen WORKER-001..009C worker scheduler: three isolated lazy pools; owner-wide worker ceilings; per-Session concurrency; round-robin ready-Session fairness; finite per-class idle retirement; Forced Close A start/cancel linearization; OnClose after Done with bounded best-effort event credits; lifecycle/fairness/isolation/race tests and CI.

Out of scope: Phase 6 Client/Server networking/reconnect, Phase 7 live TCP interoperability, Phase 8 performance optimization/benchmarks and Phase 9 release/deployment. No public API, defaults, wire contract or architecture decision is reopened.



## Phase 5 implementation evidence — COMPLETE / CI PASS

Source verification HEAD: `c72136693f85e61239bfca42bd04b40e66eddc27`. See [Phase 5 implementation report](NETA_GO_PHASE_5_WORKER_SCHEDULER_IMPLEMENTATION_2026-11-17.md) and the canonical [TASKS.md](TASKS.md). Go CI [44066876353](https://github.com/majiddarvishan/neta-go/actions/runs/44066876353) and Pinex Wire Compatibility [44066876291](https://github.com/majiddarvishan/neta-go/actions/runs/44066876291) both PASS. Phase 6+ remain unauthorized.


## Phase 6 Server implementation evidence — 2026-11-17

- Server `Start/Addr/Accept`, bounded Pre-Bind admission before Session allocation, absolute Pre-Bind deadline, Bound Session capacity, BindValidator and atomic duplicate-SystemID reservations.
- Server Sessions are registered before their transport goroutines start and share the Server resource ledger and callback dispatcher.
- Registry promotion occurs only after successful Bind Response Write; cleanup uses Session pointer identity and releases pre-published reservations safely.
- Server Stop closes Listener first, closes Pre-Bind Sessions, concurrently Graceful-Unbinds Bound Sessions and forces remaining Sessions on caller Context expiry. It does not wait for user callbacks.
- 11 focused tests in `server_lifecycle_test.go`.
- Source verification HEAD: `8eead509c6817722d6b7c6f5e5a17e1734749911`.
- Go CI [44070940615](https://github.com/majiddarvishan/neta-go/actions/runs/44070940615): PASS — gofmt, vet, unit and race.
- Pinex Wire Compatibility [44070940706](https://github.com/majiddarvishan/neta-go/actions/runs/44070940706): PASS.

**Remaining Phase 6:** Client Connect/Dial/Bind, CurrentSession, Client Stop, reconnect supervisor, generation fencing and corresponding tests. Client Bind requires owner clarification of SystemID and BindType configuration before code.


## Phase 6 Client lifecycle evidence — 2026-11-17

- `Client.CurrentSession() (*Session, bool)` returns only the Bound generation and clears stale non-Bound pointers.
- `Client.Stop(ctx)` is terminal/idempotent; cancels active Connect/reconnect contexts when present, Gracefully Unbinds Bound Sessions, forces on Context expiry and waits for internal Done only.
- 4 focused Client lifecycle tests.
- Source verification HEAD: `a05a735aa0383d2588b41b1a2258282d734ff72b`.
- Go CI [44071959633](https://github.com/majiddarvishan/neta-go/actions/runs/44071959633): PASS — gofmt, vet, unit and race.
- Pinex Wire Compatibility [44071959704](https://github.com/majiddarvishan/neta-go/actions/runs/44071959704): PASS.
- Client Connect/Bind and reconnect were subsequently implemented after the owner approved Option B; final CI is PASS at HEAD `f8ce7669d2bbde33d3134d300e3256ae290dc529`.


## 18. Client Bind identity decision and implementation handoff (2026-11-17)

The owner approved **Option B**:
- WithClientSystemID(string) is mandatory and validated before any Dial.
- WithClientBindType(BindType) is optional; default BindTypeBiDirectional, with BindTypeUniDirectional available.
- Client.Connect(ctx) signature remains unchanged.
- Uni-directional Client behavior is requester-only and follows Pinex 1.5.0: outgoing Requests are allowed; incoming peer Requests are drained/ignored; SendResponse is rejected.

The Phase 6 Client implementation now includes:
- absolute per-attempt Dial timeout and separate absolute Bind Response timeout, both bounded by caller Context;
- one serialized Client connection-attempt gate, monotonic generation fencing and publication only after successful Bind;
- Client-owned resource ledger and callback dispatcher reused across all Session generations;
- one optional reconnect supervisor with exponential Full Jitter (1s base window, 30s cap, reset after 30s continuously Bound);
- retry only for transient Dial failures/timeouts and unexpected post-Bound transport failures; Bind rejection/timeout are not retried; no Request replay;
- Stop cancels Dial/Bind/reconnect and waits for supervisor/internal Session Done without joining user callbacks.

Implementation commit and CI evidence are to be appended after verification. Phase 7–9 remain gated.


## 19. Phase 6 completion — Client Connect/Bind and reconnect (2026-11-17)

**Status:** COMPLETE / CI PASS  
**Final verified source HEAD:** f8ce7669d2bbde33d3134d300e3256ae290dc529

- Owner-approved Option B is implemented: mandatory WithClientSystemID(string), optional WithClientBindType(BindType), bi-directional default, uni-directional supported.
- Client.Connect(ctx) performs TCP Dial + Bind with independent absolute timeouts and caller Context precedence.
- Monotonic generation fencing publishes only the active Bound Session; all generations share Client-owned resource and callback infrastructure.
- One opt-in reconnect supervisor applies exponential Full Jitter (1s base, 30s cap, reset after 30s continuously Bound); Bind rejection/timeout are non-retryable and Requests are never replayed.
- Uni-directional Client semantics match Pinex 1.5.0 requester-only behavior.
- A Bind-vs-Context cancellation race is covered: completed Bind wins over a later Context cancellation.
- New tests cover configuration validation, Bind/Unbind, Bind timeout/rejection, reconnect generation replacement, uni-directional behavior and the Context race.
- Go CI [44078517718](https://github.com/majiddarvishan/neta-go/actions/runs/44078517718): PASS — gofmt, go vet ./..., go test ./..., go test -race ./....
- Pinex Wire Compatibility [44078517770](https://github.com/majiddarvishan/neta-go/actions/runs/44078517770): PASS — pinned C++ 1.5.0 golden fixtures.

Phase 6 is closed. Phase 7 live TCP interoperability, Phase 8 performance and Phase 9 release remain gated pending separate owner authorization.


The final Go verification also hardened an existing Worker Scheduler race-test assertion: it now waits for the callback worker's deferred resource release after the callback-return signal, avoiding a false transient 15-byte retained-resource observation. Final Go and Pinex workflows both pass at the source HEAD recorded above.


## 20. Phase 7 authorization and implementation handoff — 2026-11-17

**Owner authorization:** The owner explicitly approved Phase 7 by replying «آره» in this conversation. P7-01..P7-08 are authorized. Phase 8 performance work and Phase 9 release/deployment remain outside the authorization.

**Current neta-go source HEAD:** be2511ba9701313526fdc03e27e8e51583f4af21.

**P7-01:** Pinex develop remains version 1.5.0 at exact SHA f7bd1eb779baff0d10e624f20522df345e6ee747; no compatibility baseline drift was found.

**Implemented verification harness:**
- test/interop/neta_cpp_peer.cpp uses the actual Pinex public high-level C++ Client and Server APIs.
- phase7_interop_test.go exercises Go Client ↔ Pinex C++ Server and Pinex C++ Client ↔ Go Server over loopback TCP.
- phase7_transport_test.go covers fragmented Bind Response, out-of-order Stream Responses, slow-trickle absolute Frame Assembly timeout and abrupt TCP reset.
- internal/wire/wire_fuzz_test.go adds five fuzz targets.
- phase7_soak_test.go adds an environment-gated bounded reconnect soak.

**CI evidence so far:**
- Go CI [44079860986](https://github.com/majiddarvishan/neta-go/actions/runs/44079860986): PASS — formatting, vet, unit and race.
- Pinex Golden Compatibility [44079861215](https://github.com/majiddarvishan/neta-go/actions/runs/44079861215): PASS; this is not live TCP proof.
- Dedicated Pinex workflow run [44080043667](https://github.com/majiddarvishan/pinex/actions/runs/44080043667) is the cross-repository live verification gate. It builds the peer against Pinex develop, whose exact SHA is asserted against the frozen baseline.

**Task status:** P7-01 complete; P7-05 and P7-06 pass on the race CI; P7-02, P7-03 and P7-07 await the dedicated workflow; P7-04 remains open for graceful EOF and privileged kernel-level SYN blackhole evidence; P7-08 remains open.

No public API, wire format, defaults, resource ceilings or frozen architecture decisions were changed. Continue autonomously within Phase 7. Record each task only after its evidence passes. Do not begin Phase 8 or Phase 9.


## 21. Phase 7 completion — Live interoperability and fault verification (2026-11-17)

**Status:** COMPLETE / CI PASS  
**Final neta-go source HEAD:** 209c24a7dbc5a5aa3db95ec63705915406acacb6  
**Pinex compatibility baseline:** version 1.5.0, develop SHA f7bd1eb779baff0d10e624f20522df345e6ee747

The owner authorized P7-01..P7-08. All eight tasks are now complete:

- Both real TCP directions passed using the actual Pinex high-level C++ messaging_client / messaging_server APIs.
- Five Go wire fuzz targets each ran for 10 seconds; aggregate 1,810,074 executions, no crash or failing input.
- Transport matrix passed: fragmented frames, short writes, slow-trickle absolute Bind Response timeout, silent accepted-socket blackhole, graceful EOF, RST, reordered Responses, Bind rejection and timeout/cancellation races.
- Existing admission and Worker Scheduler fault matrices passed under the race detector.
- A 30-second, three-Client reconnect soak passed; owner resource charges returned to zero after Stop and callback worker ceilings were respected.
- Golden compatibility passed.

**Final CI evidence:**
- Dedicated Pinex live interop [44081220680](https://github.com/majiddarvishan/pinex/actions/runs/44081220680): PASS — exact Pinex source re-pin, C++ peer build, bidirectional real sockets, Go race/fault tests, soak and fuzz.
- Go CI [44081197715](https://github.com/majiddarvishan/neta-go/actions/runs/44081197715): PASS — format, vet, unit and race.
- Pinex Golden Compatibility [44081197688](https://github.com/majiddarvishan/neta-go/actions/runs/44081197688): PASS.

The dedicated Pinex workflow remains on test-only branch test/neta-go-phase7-interop; Pinex develop was not changed. The test suite exercises an application-stage silent TCP Bind peer as the blackhole case. Privileged firewall-level SYN-drop/network-namespace injection was not run and is not claimed.

No public API, wire format, defaults, resource ceilings or frozen architecture decisions were changed. Phase 7 is closed. Phase 8 performance/optimization and Phase 9 release/deployment remain NOT AUTHORIZED and require separate owner approval.


## 22. Phase 8 authorization and performance handoff — 2026-11-17

**Owner authorization:** The owner approved the complete Phase 8 scope by replying «ادامه بده» after being explicitly asked to approve Phase 8. P8-01..P8-05 are authorized. Phase 9 is not authorized.

**Starting repository HEAD:** 7f9fe62e4ffa85966b5f028365086707ec08fed2 (Phase 7 completion documentation commit; source baseline remains 209c24a7dbc5a5aa3db95ec63705915406acacb6).

**Repository inspection:** .codex/AGENT_CONTEXT.md is not present on main; the canonical tracker is `.codex/TASKS.md`. Reviewed NETA_GO_PERFORMANCE_CONTRACT_2026-11-16.md, NETA_GO_PERF_002_003_API_001B_DESIGN_2026-11-16.md, Worker Capacity/Resource Accounting design, Architecture Freeze/Decision Register, current implementation and CI workflows.

**Binding performance constraints:**
- PERF-002 A: one outbound snapshot on successful admission; inbound payload is directly read into owned, user-retainable memory; never recycle user-visible inbound payload.
- Existing bounded byte/count/resource ledgers, worker class isolation, fair per-Session scheduling, Request credit lifecycle, callback order and single serialized TCP Writer remain unchanged.
- No numeric throughput/latency SLA exists yet. Establish a reproducible baseline before proposing thresholds.
- -race is a correctness gate, not a performance measurement.
- No public API, wire format, defaults, timeout/reconnect policy or resource ceiling changes.

**P8 tasks:** P8-01 benchmark suite and environment capture; P8-02 latency/throughput/allocation/CPU/heap/GC/goroutine/RSS/contention metrics; P8-03 CPU/heap/mutex/block profiling; P8-04 evidence-based PERF-004 evaluation; P8-05 correctness/interop/performance regression gate.

Initial work must remain test/benchmark/CI/documentation-only. Do not begin Phase 9. Record exact source HEAD and runner details for every result.


## 23. Phase 8 — Repeatable local/CI automation (2026-11-17)

**Repository HEAD before automation commit:** 58abc598bb62cd9e86eee7849a959ded80dbc2a7

The owner asked that the Phase 8 correctness/performance tests be repeatable automatically and that local requests be reduced to short scripts only where machine-local execution is necessary.

Added repository automation:
- `Makefile`: `check`, `race`, `verify`, `perf-smoke`, `soak`, `phase8`.
- `scripts/ci-check.sh`: gofmt, vet, uncached unit and race checks.
- `scripts/phase8-benchmark.sh`: smoke, soak and full benchmark/profile modes.
- `.gitignore`: ignore generated `artifacts/`.
- GitHub Go and Phase 8 workflows invoke the same Makefile targets as local runs.
- Artifacts capture source SHA, worktree state, Go toolchain/environment, logs, explicit PASS/FAIL status, benchmark output and profiles.

**Validation status at handoff:** repository changes committed; the new GitHub Actions runs must be inspected before declaring automation validated. The Phase 8 performance baseline remains IN PROGRESS. Do not start Phase 9 or change production behavior.


## 24. Phase 8 — Correctness automation verified locally and in GitHub (2026-11-17)

Owner executed `make verify` on source HEAD `708d5776e389dd04f0b60b347fa8cd15d42d40bc` after safely stashing prior local work and fast-forwarding to `origin/main`.

- Local gofmt, vet, uncached unit tests and uncached race tests: PASS.
- Local worktree: clean and aligned with `origin/main`.
- Original local modifications remain preserved in `stash@{0}`; do not drop or apply until reviewed.
- Go CI [44103718615](https://github.com/majiddarvishan/neta-go/actions/runs/44103718615): PASS; shared Makefile/script path exercised and artifact uploaded.
- Pinex Wire Compatibility [44103718477](https://github.com/majiddarvishan/neta-go/actions/runs/44103718477): PASS.
- Phase 8 full performance run [44103718627](https://github.com/majiddarvishan/neta-go/actions/runs/44103718627): still running at this handoff update; do not mark P8-01 or full automation validation complete until artifacts are reviewed.

No production code or frozen contract changed.


## 25. Phase 8 — SendNoWait benchmark correlation hardening (2026-11-17)

A test-only benchmark measurement flaw was corrected before accepting the baseline: concurrent SendNoWait producers previously consumed delivery notifications from one shared channel, so a producer could be assigned another producer's delivery timestamp.

The harness now routes notifications by TCP peer address and the returned per-Session sequence, including the race where server delivery precedes waiter registration. A focused test covers out-of-order and early notifications. The Phase 8 workflow was also configured to trigger when `phase8_pinex_benchmark_test.go` changes.

The previous full Phase 8 run [44103718627](https://github.com/majiddarvishan/neta-go/actions/runs/44103718627) predates this fix and must not be used as final SendNoWait latency/fairness evidence. Run and inspect a fresh full workflow on the corrected harness. No production code or frozen contract changed.


## 26. Phase 8 — Preliminary full-run evidence and profile review (2026-11-17)

The first complete Phase 8 workflow [44103718627](https://github.com/majiddarvishan/neta-go/actions/runs/44103718627) completed PASS and uploaded artifact [14338171799](https://github.com/majiddarvishan/neta-go/actions/runs/44103718627/artifacts/14338171799), source SHA `708d5776e389dd04f0b60b347fa8cd15d42d40bc`.

The artifact was downloaded and inspected. The five-minute soak passed with baseline/final heap 319,200/317,944 bytes, max HeapInuse 4 MiB, max RSS 88,492 KiB, 4,609 GC cycles and two goroutines after cleanup. Server retained/queued Application bytes stayed at zero in periodic samples. The 512-Session Request/Response scaling, queue-full, codec and profile results are summarized in the Phase 8 baseline report.

SendNoWait metrics from this run are excluded because the initial test harness could attribute one producer's delivery signal to another producer. This was corrected in commit `c5ebca4d3d0b7f1d36270501add0b059525df2c2`; a new full Phase 8 run is required and is currently queued/running.

Profile review identifies outbound `buildStreamFrame` as a possible allocation optimization and inbound `Session.readFrame` as an ownership-required allocation. PERF-002 A forbids recycling inbound payloads. Any outbound reuse must be strictly bounded and reconciled with owner resource accounting. No production optimization has been accepted yet.


## 27. Phase 8 — End-to-end SendNoWait routing test (2026-11-17)

Added `phase8_delivery_test.go`: eight concurrent producers send one-way Requests over two live TCP Sessions. It verifies per-connection sequence routing, overlapping sequence values across Sessions, and early/out-of-order delivery notification. This runs under normal and race CI; no production code changed.


## 28. Phase 8 COMPLETE — corrected baseline, profiles and PERF-004 closure (2026-11-17)

**Latest repository HEAD before this documentation update:** `8986636f1fefbd2ebcad20df8e3fe66ed6c5fbbc`  
**Production source HEAD:** `209c24a7dbc5a5aa3db95ec63705915406acacb6` (unchanged throughout Phase 8).  
**Corrected full Phase 8 workflow:** [44105272003](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003) PASS.  
**Artifact:** [14338552627](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003/artifacts/14338552627), benchmark harness SHA `c5ebca4d3d0b7f1d36270501add0b059525df2c2`.

P8-01..P8-05 are COMPLETE:
- Reproducible loopback benchmark matrix and environment metadata captured.
- Throughput, latency percentiles, submission latency, allocation, heap/GC, goroutine, worker, RSS and contention metrics recorded.
- Small/large CPU, heap, mutex and block profiles reviewed.
- PERF-004 = **NO CHANGE**. Inbound payload pooling is forbidden by PERF-002 A; outbound pooling lacks a proven material performance win and would add hard-bounded retention/lifecycle/accounting complexity.
- Correctness/Pinex compatibility CI PASS on latest repository HEAD [8986636f1fefbd2ebcad20df8e3fe66ed6c5fbbc](https://github.com/majiddarvishan/neta-go/actions/runs/44107389341) and [44107389316](https://github.com/majiddarvishan/neta-go/actions/runs/44107389316). The eight-producer/two-Session SendNoWait delivery-routing integration test is included in these gates.
- Owner's local `make verify` on 2026-11-17 passed on HEAD `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5`: PASS (gofmt, vet, uncached unit and race); local stash `stash@{0}` remains preserved and has not been applied or dropped.

The five-minute soak completed with heap 335,696 → 308,088 bytes, max HeapInuse 4,374,528 bytes, max RSS 91,348 KiB, 4,549 GC cycles and two goroutines after cleanup. Server retained/queued Application bytes stayed zero in periodic samples.

No production code, public API, wire format, default, timeout/reconnect policy, worker ceiling or resource limit changed. Numeric performance thresholds remain intentionally unset pending owner workload review. At the time this Phase 8 closure entry was written, Phase 9 had not yet been authorized; Phase 9 was subsequently authorized in §29.


## 29. Phase 9 authorization and P9-00 tracker reconciliation — 2026-11-17

**Status:** Phase 9 IN PROGRESS / OWNER AUTHORIZED. P9-00 COMPLETE. P9-01..P9-05 authorized. P9-06 release tag NOT YET AUTHORIZED.

The owner approved the Phase 9 execution plan by replying «ادامه بده» after the plan and release boundary were presented.

### Authorized scope

- P9-00: reconcile stale project status and tracker records; refine Phase 9 tasks, acceptance criteria and dependencies; record this authorization.
- P9-01/P9-02: add runnable, standard-library-only Client and Server examples using only the frozen public API.
- P9-03: complete public GoDoc, configuration, lifecycle, callback, ownership, error and Quick Start documentation.
- P9-04: document the pinned Pinex 1.5.0 compatibility contract and available golden/live TCP evidence.
- P9-05: review test/CI coverage, supported Go/platform baseline, changelog/versioning and release readiness.

**Separate gate:** P9-06 may create a V1 tag/release only after all prior acceptance gates pass and the owner gives explicit release approval. The general Phase 9 approval does not authorize a release tag.

### P9-00 baseline and result

- Baseline repository HEAD: `d40467e44ef0535ba0a5ef83c9c5ce4a9109d9a5`.
- Production source HEAD remains: `209c24a7dbc5a5aa3db95ec63705915406acacb6`.
- Correctness CI [44108072039](https://github.com/majiddarvishan/neta-go/actions/runs/44108072039): PASS.
- Pinex Wire Compatibility CI [44108072167](https://github.com/majiddarvishan/neta-go/actions/runs/44108072167): PASS.
- Phase 8 full performance run [44105272003](https://github.com/majiddarvishan/neta-go/actions/runs/44105272003): PASS.
- P9-00 is documentation/tracker/authorization-only. No production source, API, protocol, default or resource-accounting behavior changes.

### Local stash limitation

The owner's `stash@{0}` is local Git state and is not exposed by GitHub. The exact stash patch has therefore **not** been reviewed. It must remain untouched. To inspect it safely in the owner clone:

```bash
git stash show --stat stash@{0}
git stash show --patch stash@{0} -- \
  .github/workflows/go.yml \
  .github/workflows/phase8-performance.yml
```

Do not apply or drop the stash as part of this review.

### Next action

P9-05 implementation commit `c038fa60ffafd1f895e133db6d8cca08e7a2cc49` added the coverage and paired-example CI gate; script fix commit `6d2521a22a476ee24f90dee364249e137357b756` corrected shell expansion. Final Go CI [44119107169](https://github.com/majiddarvishan/neta-go/actions/runs/44119107169) and Pinex Wire Compatibility [44119107078](https://github.com/majiddarvishan/neta-go/actions/runs/44119107078) both PASS. Coverage: neta 79.7%, internal/wire 90.3%, examples 0% (no package-local tests). Paired runtime and graceful shutdown smoke PASS. Next: owner-dependent release review. Keep all frozen production contracts unchanged.


## 30. P9-05 — Owner-approved Go/platform support baseline (2026-11-17)

**Status: APPROVED.** The owner answered «آره» to the explicit support baseline proposal. Minimum supported Go: **1.23** (module directive `go 1.23`; CI selector `1.23.x`). Continuously CI-verified environment: **Ubuntu 24.04 / Linux amd64**. The owner's local `make verify` with Go 1.27.0 was previously reported PASS, but the local platform was not captured. Other GOOS/GOARCH targets remain unverified and cannot be advertised as supported without new evidence.

Pre-decision CI at HEAD `22af702cfedb1d92848a5483194459caad15f407`: Go correctness + paired-example smoke [44119456370](https://github.com/majiddarvishan/neta-go/actions/runs/44119456370) PASS, Pinex Wire Compatibility [44119455809](https://github.com/majiddarvishan/neta-go/actions/runs/44119455809) PASS. Support decision is closed in `.codex/TASKS.md`, `docs/SUPPORT.md` and `docs/RELEASE_READINESS.md`.

P9-05 remains IN PROGRESS pending LICENSE copyright holder/year, changelog/version approval and branch-protection/release-settings verification. P9-06 is NOT AUTHORIZED. No release/tag, production changes or local stash operations were performed.


## 31. P9-05 — Copyright notice and commercial-use permission (2026-11-17)

**Status: OWNER CONFIRMED / COMPLETE.** The owner supplied the exact copyright holder **Majid Darvishan**, year **2026**, and stated that others may use neta-go commercially.

- Retained the existing Apache License, Version 2.0, including its full terms and conditions (Sections 1–9).
- Updated the copyright notice in the `LICENSE` appendix from its placeholder to `Copyright 2026 Majid Darvishan`.
- README explains that commercial and proprietary use, modification and redistribution are permitted subject to Apache-2.0 conditions, including applicable license and attribution notices. No additional restriction on commercial use was imposed.
- Closed only the copyright/licensing subtask in the canonical tracker and release checklist; P9-05 remains IN PROGRESS.
- Remaining: verify GitHub classic branch protection/release settings (integration lacks the required administration scope), owner review of changelog/versioning. P9-06 tag and GitHub Release still need separate explicit owner approval.
- No production source, public API, protocol, defaults, CI automation, tests or local `stash@{0}` were changed.


## 32. P9-05 — Owner-approved v1.0.0 and CHANGELOG; branch release risk (2026-11-17)

**Owner decision: APPROVED** — owner answered «آره» to the direct request to approve the intended semantic version `v1.0.0` and the **current `CHANGELOG.md` Unreleased content**. The changelog content is preserved unchanged and remains under `Unreleased` until an actual separately authorized publication.

- Go correctness/coverage/paired-example CI [44159858260](https://github.com/majiddarvishan/neta-go/actions/runs/44159858260) PASS and Pinex Wire Compatibility [44159858233](https://github.com/majiddarvishan/neta-go/actions/runs/44159858233) PASS on pre-decision HEAD `11d2a0a9508b59e603f038e14772d29bb1bb17ea`.
- GitHub branch metadata reports `main.protected=false` and repository rulesets API returns `[]`. Classic branch protection details are inaccessible via the integration (HTTP 403), so do not claim the branch has enforced protection.
- Repository tags: none. Published GitHub Releases: none. GitHub Release settings require owner/admin inspection.
- `docs/RELEASE_READINESS.md` now has a PASS / NOT VERIFIED / NOT AUTHORIZED matrix. `.codex/TASKS.md` and Phase 9 plan record version/changelog decision as COMPLETE.
- **P9-05 stays IN PROGRESS:** branch protection / release settings still need owner/admin review or explicit risk acceptance. **P9-06 is NOT AUTHORIZED**; no tag, release, production code change or local stash operation was performed.


## 33. P9-05 — Owner-approved main protection; application still pending (2026-11-17)

The owner approved the required-CI policy for `main`. Exact GitHub check names: `test` (Go) and `Verify Go wire codec against pinned Pinex C++ 1.5.0` (Pinex). Both completed PASS on commit `b3fad24938dd689cd270b6954a3a98e37f630614`; both workflows run on `pull_request` and `push`.

**NOT APPLIED:** branch API currently reports `protected=false`, repository rulesets empty; classic branch-protection endpoint is HTTP 403 and connected GitHub tools have no mutation capability. The approved policy, runnable admin-only `gh api` request and verification steps are in [NETA_GO_MAIN_BRANCH_PROTECTION_APPLICATION_2026-11-17.md](NETA_GO_MAIN_BRANCH_PROTECTION_APPLICATION_2026-11-17.md). Do not mark protection as enabled without real GitHub confirmation.

P9-05 remains IN PROGRESS pending protection application/verification and release-settings admin check. P9-06 V1 tag/Release is not authorized. Owner's local `stash@{0}` remains untouched.


## 34. P9-05 — Verified active main protection (2026-11-17)

After the owner reported completing GitHub web configuration («انجام شد»), the live branch API for `main` returned **`protected=true`**. Its public metadata reports `required_status_checks.enforcement_level=everyone` with the **two exact required contexts** `test` and `Verify Go wire codec against pinned Pinex C++ 1.5.0`. Both checks completed PASS on `b992beac7495934ce43111bd3a692ec272c8195d`: [Go 44163815612](https://github.com/majiddarvishan/neta-go/actions/runs/44163815612), [Pinex 44163815661](https://github.com/majiddarvishan/neta-go/actions/runs/44163815661).

The actual protection activation and exact required check names are now **VERIFIED**, not merely approved. The integration still receives HTTP 403 for full classic branch protection details, so the `strict` (require up-to-date) and admin-bypass configuration remain unverified. GitHub Release settings review remains open. Do not run the previously supplied PUT command merely to verify settings; it overwrites existing rules.

The release tracker and checklist require a feature branch / pull request to record this post-protection evidence. P9-05 remains IN PROGRESS until outstanding verifications; P9-06 tag/Release remains NOT AUTHORIZED. Local stash unchanged.


## 35. P9-05 — Post-merge CI and real PR enforcement acceptance (2026-11-17)

- Protected `main` HEAD `b5839a42b0de99f1ce9abf278e1fba3ff66d6617`: Go [44165799994](https://github.com/majiddarvishan/neta-go/actions/runs/44165799994) **PASS**, Pinex Compatibility [44165800103](https://github.com/majiddarvishan/neta-go/actions/runs/44165800103) **PASS**. Required check contexts `test` and `Verify Go wire codec against pinned Pinex C++ 1.5.0` both completed successfully.
- Live [PR #2](https://github.com/majiddarvishan/neta-go/pull/2): `mergeable_state=blocked` while check runs in progress, later `clean` with successful checks, and squash-merged. Actual required-check gating is demonstrated, not just configured.
- GitHub repository: public, no tags, no Releases; release listing accessible. Connected integration has no release publication or full branch protection settings-read action. Therefore strict up-to-date, exact administrator bypass settings and release-creation permissions remain **NOT INDEPENDENTLY VERIFIED**. Owner reported completing browser configuration; this report does not substitute for seeing private admin configuration.
- `.codex/TASKS.md`, `docs/RELEASE_READINESS.md`, branch guide and Phase 9 plan updated with verifiable evidence and unresolved gate. **P9-05 remains IN PROGRESS**; **P9-06 still NOT AUTHORIZED**; `CHANGELOG.md` remains Unreleased. Local stash untouched.


## 36. P9-05 — Qualified engineering sign-off; P9-06 release remains gated (2026-11-17)

P9-05 review is **COMPLETE with explicit verification limitations**. All technical gates (Go correctness/race, examples and loopback smoke, Pinex compatibility, coverage report, protected PR CI enforcement) passed; owner-approved V1 baseline is Go 1.23 on Ubuntu 24.04/Linux amd64, Apache-2.0 Copyright 2026 Majid Darvishan, version `v1.0.0` and current Unreleased changelog entries.

Most recent pre-signoff protected `main` commit `cbd07421fec639a2d0db0bec7de03484bbcdb831`: Go [44167295340](https://github.com/majiddarvishan/neta-go/actions/runs/44167295340) **PASS** and Pinex [44167295551](https://github.com/majiddarvishan/neta-go/actions/runs/44167295551) **PASS**. The owner reported completing the GitHub UI protection steps; GitHub independently reports `protected=true`, mandatory checks and `enforcement_level=everyone`, with actual blocked/then-merged PR enforcement. Full classic branch-protection read remains HTTP 403; do not claim exact `strict` or administrator bypass flags as independently verified.

The repo is public; connected owner-repository metadata reports admin permission, and GitHub Releases/tags APIs can be read with zero existing releases/tags. Actual release creation permission and release configuration are **NOT TESTED** to avoid unauthorized publication. Those detailed admin checks, final target SHA/CI revalidation and **fresh explicit owner release approval** are mandatory prepublication P9-06 gates, not silently waived. **P9-06 remains NOT AUTHORIZED**; `CHANGELOG.md` stays Unreleased. Local stash untouched. Use protected feature branch + PR for this review closure.


## 37. PROTOCOL-VERSION-001 — Owner selects Session-level versioning (2026-11-18)

The owner explicitly instructed **not to change code**, asked about dropping the NUL terminator after Bind SystemID while staying backward compatible, then approved **selecting the protocol version once per Session instead of adding a per-Frame version byte**.

This is a design-only decision. V1 stays default and wire-identical to Pinex C++ 1.5.0: 10-byte header; BindType + `c_octet_str<20>` NUL-terminated SystemID; omitted BindResp body allowed with defaults. The old Pinex C++ decoder explicitly searches for NUL; sending V2 Bind without it to a legacy peer is incompatible. Positive peer capability agreement is required before V2. The selection/handshake mechanism, possible V2 Bind optimization and API contracts remain OPEN — no speculative in-band negotiation, version probing or automatic downgrade allowed.

Formal architecture record: [NETA_GO_SESSION_PROTOCOL_VERSIONING_DESIGN_2026-11-18.md](NETA_GO_SESSION_PROTOCOL_VERSIONING_DESIGN_2026-11-18.md); canonical `.codex/TASKS.md` tracks PV-02..PV-05 as future, separately unauthorised tasks. No source/tests/CI/golden fixtures were changed. P9-06 `v1.0.0` release **NOT AUTHORIZED**; local stash untouched.


## 38. PV-01 — Go-only Session protocol version API, V2 local default (2026-11-18)

Owner explicitly authorized a **Go-only** protocol version selection and changed the Session default to `ProtocolVersionV2`. Public declarations: `ProtocolVersion`, `ProtocolVersionV1`, `ProtocolVersionV2`, `WithProtocolVersion(version)` (SessionOption), and `(*Session).ProtocolVersion()`. Validation rejects 0 or unsupported values, defaults and overrides tested; Client/Server inherit Session options.

This is a **local version setting only**. Both values continue to use **identical Pinex 1.5.0 wire bytes**, including the 10-byte Header and NUL-terminated Bind SystemID. No wire negotiation or on-wire V2, no NUL removal, no Pinex C++ changes. Future PV-02/PV-03 decide actual V2 wire or negotiation separately.

The previous P9-05 signoff predates this API/default change. PV-01-R now requires fresh protected-main Go/race/example/Pinex CI and owner approval of the amended Unreleased CHANGELOG before any `v1.0.0` release. P9-06 remains NOT AUTHORIZED. Do not create tags/Releases and do not touch the owner's local stash.


## 39. PV-02A — Go V2 NUL-free Bind; reconnect to GitHub (2026-11-18)

The owner approved removing the trailing NUL only for V2. GitHub writes were temporarily unavailable, then recovered; implementation was staged on feature branch `feature/v2-nul-free-bind-2026-11-18` after rereading protected main `bd7cb466a4e4e7c3ae5013f5a9c99bbd7c3884ea`.

Actual behavior: V1 codec remains unchanged. V2 Bind Request/Response omit the terminator; new Go Server (V2 default) detects legacy/V2 Bind format and responds using the same version. Selected protocol version is stored in Session under mu. A Go Client defaults to V2 and must set `WithProtocolVersion(ProtocolVersionV1)` to bind to Pinex C++ 1.5.0. No automatic negotiation/downgrade or new Header bytes. Codec and Go loopback tests added.

Review release-boundary carefully: PV-02A and PV-02A-R tasks in `TASKS.md` require real PR/Go/Pinex CI evidence before closure; no prior CI results imply V2-wire validation. P9-06 remains NOT AUTHORIZED; no tag or release.


## 40. PV-02B — Raise V2 SystemID byte limit to 20 (2026-11-18)

Owner explicitly requested expanding `SystemID` capacity to **20 bytes** after V2 NUL removal. Implementation in `feature/v2-system-id-20-bytes-2026-11-18`: internal V2 Bind codec now allows 20 rather than 19 bytes for both Request and Response; legacy V1 codec retains 19 bytes plus NUL. Go Client construction derives the byte limit from `ProtocolVersion`, including default V2=20 and explicit V1=19. New codec and TCP tests cover boundaries and actual Session identity. No new Header field, no Pinex C++ change, no V2 auto-fallback.

Track `PV-02B` and `PV-02B-R` separately in `.codex/TASKS.md`. Merge only after protected-PR Go/race/example and Pinex wire CI PASS. Post-merge main CI and renewed changelog review remain release preflight. P9-06 is NOT AUTHORIZED, no tag/Release; local stash remains untouched.

## 72. Owner-approved QA contracts — 2026-11-18 (documentation only)

Protected-main base at the start of this documentation work: `bf0f27e6116d6ad5bf99403df615bc57923b5883`. Owner approved QA-004.1 A / QA-004.2 B, QA-005.1 B / QA-005.2 B, and QA-007 B with all QA-007.1..13 sub-decisions. See [full approved contracts](NETA_GO_QA_004_005_007_APPROVED_CONTRACTS_2026-11-18.md) and [canonical tracker](TASKS.md).

**IMPORTANT:** design approved does not mean remediation code/QA tests have been completed. Open numerical / API contracts require fresh owner approval, notably Panic recent-record minimum byte budget, diagnostic public API, and quantitative regression gates with reference workloads. Keep QA-004, QA-005, QA-007 unchecked until their acceptance evidence is complete. Do not change code, run tests or create PRs under the documentation-only authorization. No `v1.0.0` tag or Release without explicit separate permission.
