"""Strict anchored patch checks for QA-005 owned-buffer overlay.

No source tree mutation and no claim of qualified attributable memory.
"""
import importlib.util
import pathlib
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name("qa005_owned_buffers_overlay.py")
spec = importlib.util.spec_from_file_location("qa005_owned_buffers_overlay", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class OwnedBuffersOverlayTest(unittest.TestCase):
    def test_fails_closed_on_wrong_function_or_missing_anchor(self):
        with self.assertRaisesRegex(ValueError, "outbound frame identity"):
            mod.patch_internal("package neta\n")
        with self.assertRaisesRegex(ValueError, "inbound application charge"):
            mod.patch_charges("package neta\n")
        with self.assertRaisesRegex(ValueError, "inbound body allocation"):
            mod.patch_transport("package neta\n")
        with self.assertRaisesRegex(ValueError, "existing sampler marker"):
            mod.patch_benchmark("type qa005ChargeProbe struct {\n")

    def test_allocation_uses_capacity_and_release_is_once(self):
        internal = (
            "type outboundFrame struct {\n\tafterWrite         func()\n}\n"
            "type inboundFrame struct {\n\tcompletionCapacityErr bool\n}\n"
            "type Session struct {\n\tactiveWrite               *outboundFrame\n}\n"
            "func (s *Session) enqueueControlLocked(item *outboundFrame) error {\n"
            "\ts.queuedControlBytes = next\n\tif item.barrier {\n"
            "}\nfunc (s *Session) enqueueApplicationLocked(item *outboundFrame) error {\n"
            "\ts.appQueue = append(s.appQueue, item)\n\ts.cond.Signal()\n}\n"
            "func (s *Session) releaseFrameChargeLocked(item *outboundFrame) {\n"
            "\tif item == nil {\n\t\treturn\n\t}\n\tif item.control {\n}\n"
        )
        patched = mod.patch_internal(internal)
        self.assertEqual(patched.count("item.qa005Observed = true"), 2)
        self.assertIn("uint64(cap(item.bytes))", patched)
        self.assertIn("qa005OwnedOutgoingApp", patched)
        self.assertIn("qa005OwnedPeak", patched)
        self.assertIn("qa005OwnedTotal", patched)
        self.assertIn("qa005Enqueued = true", patched)
        self.assertIn("qa005AfterAllocation", patched)
        self.assertIn("qa005RegisterControlLocked", mod.SESSION_HELPERS)
        self.assertIn("qa005DiscardControlBeforeQueueLocked", mod.SESSION_HELPERS)
        self.assertIn("TestQA005OwnedOverlayPreQueueControlTransferAndReject", mod.BENCHMARK_HELPERS)
        self.assertIn("TestQA005OwnedOverlayDeduplicatesSessionIdentity", mod.BENCHMARK_HELPERS)
        self.assertIn("seen := make(map[*Session]struct{}", mod.BENCHMARK_HELPERS)
        self.assertIn("qa005OwnedRegistryComplete", mod.BENCHMARK_HELPERS)
        self.assertIn("TestQA005OwnedOverlayFrozenRegistry", mod.BENCHMARK_HELPERS)
        self.assertIn("else if !item.qa005Observed", patched)
        self.assertIn("qa005OwnedIncomingReply", patched)
        self.assertIn("item.qa005Observed = false", patched)
        self.assertNotIn("retained-attributed-B", patched)

    def test_charge_release_after_callback_and_allocation_after_make(self):
        charges = (
            "type applicationReadCharge struct {\n\tbytes            uint64\n\tqueueReleased\n}\n"
            "type completionReadCharge struct {\n\tbytes    uint64\n\treleased bool\n}\n"
            "func app() {\n\tc.retainedReleased = true\n"
            "\tif next, ok := checkedSubUint64(\n}\n"
            "func completion() {\n\tc.released = true\n"
            "\tif next, ok := checkedSubUint64(\n}\n"
        )
        patched = mod.patch_charges(charges)
        self.assertIn("qa005SubtractOwnedLocked(s, &s.qa005OwnedIncomingApp", patched)
        self.assertIn("qa005SubtractOwnedLocked(s, &s.qa005OwnedIncomingReply", patched)
        transport = (SCRIPT.parent.parent / "session_transport.go").read_text()
        patched = mod.patch_transport(transport)
        allocation = patched.find("body = make([]byte, bodyLength)")
        observed = patched.find("qa005AddOwnedLocked(", allocation)
        read_body = patched.find("if _, err := io.ReadFull(s.conn, body);", allocation)
        self.assertGreaterEqual(allocation, 0)
        self.assertGreaterEqual(observed, 0)
        self.assertGreaterEqual(read_body, 0)
        self.assertLess(allocation, observed)
        self.assertLess(observed, read_body)

    def test_refuses_output_inside_checkout_before_writing(self):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            with self.assertRaisesRegex(ValueError, "outside source checkout"):
                mod.prepare(root, root / "inside")
            self.assertFalse((root / "inside").exists())


    def test_actual_source_outbound_build_to_queue_transfer(self):
        source = (SCRIPT.parent.parent / "session.go").read_text()
        patched = mod.patch_session(source)
        self.assertEqual(patched.count("qa005Transferred := false"), 3)
        self.assertEqual(patched.count("qa005Transferred = true"), 3)
        self.assertEqual(patched.count("qa005Observed: true"), 3)
        self.assertEqual(patched.count("qa005SubtractOwnedLocked(s, &s.qa005OwnedOutgoingApp"), 3)
        self.assertIn("frame = make([]byte, length)", patched)
        self.assertIn("qa005AddOwnedLocked(owner, &owner.qa005OwnedOutgoingApp", patched)
        self.assertIn("payload, s)", patched)
        self.assertIn("after := owner.qa005AfterAllocation", patched)
        self.assertIn("TestQA005OwnedOverlayForcedCloseDuringBuild", mod.BENCHMARK_HELPERS)
        self.assertEqual(source.count("qa005Transferred"), 0)
        with self.assertRaisesRegex(ValueError, "frame builder optional observer"):
            mod.patch_session(patched)

    def test_control_paths_patch_in_real_sources(self):
        source = SCRIPT.parent.parent
        session = mod.patch_session((source / "session.go").read_text())
        control = mod.patch_control((source / "session_control.go").read_text())
        self.assertIn("qa005RegisterControlLocked(s, control)", session)
        self.assertIn("qa005DiscardControlBeforeQueueLocked(s, control)", session)
        self.assertIn("qa005RegisterControlLocked(s, item)", control)
        self.assertIn("qa005DiscardControlBeforeQueueLocked(s, item)", control)
        self.assertIn("session_control.go", mod.SOURCE_FILES)
        self.assertNotIn('retained-attributed-B")', session)

    def test_partial_manifest_is_fail_closed(self):
        self.assertIn('"covered_categories": []', SCRIPT.read_text())
        self.assertIn('"coverage_status": "PARTIAL_INCONCLUSIVE"', SCRIPT.read_text())
        self.assertIn('"observed_partial_categories"', SCRIPT.read_text())
        self.assertNotIn('b.ReportMetric(float64(p.ownedPeak), "retained-attributed-B")', mod.BENCHMARK_HELPERS)

    def test_gap_and_snapshot_cost_are_diagnostic_only(self):
        source = (SCRIPT.parent.parent / "benchmark_test.go").read_text()
        patched = mod.patch_benchmark(source)
        self.assertIn('probe-owned-max-sample-gap-ns', patched)
        self.assertIn('probe-owned-max-snapshot-ns', patched)
        self.assertIn('ownedLastSampleAt time.Time', patched)
        self.assertIn('started.Sub(p.ownedLastSampleAt)', patched)
        self.assertIn('qa005RecordSamplingWindow(p, sampleStartedAt, snapshotDuration)', patched)
        self.assertNotIn('ReportMetric(float64(p.ownedPeak), "retained-attributed-B")', patched)


    def test_transient_admission_epoch_patch_matches_real_source(self):
        source = SCRIPT.parent.parent
        server = mod.patch_server_lifecycle((source / "server_lifecycle.go").read_text())
        struct = mod.patch_types((source / "types.go").read_text())
        fixture = mod.patch_benchmark((source / "benchmark_test.go").read_text())
        self.assertIn("s.qa005OwnedAdmissionEpoch++", server)
        self.assertIn("qa005OwnedAdmissionEpoch uint64", struct)
        self.assertIn("qa005OwnedBaselineAdmissionEpoch uint64", fixture)
        self.assertIn("qa005OwnedBaselineAdmissionEpoch = env.server.qa005OwnedAdmissionEpoch", mod.BENCHMARK_HELPERS)
        self.assertIn("TestQA005OwnedOverlayTransientAdmissionChurn", mod.BENCHMARK_HELPERS)
        self.assertIn("server_lifecycle.go", mod.SOURCE_FILES)
        self.assertIn("types.go", mod.SOURCE_FILES)
        with self.assertRaisesRegex(ValueError, "Server Session registration epoch"):
            mod.patch_server_lifecycle("package neta\\n")


    def test_unreserved_inbound_bind_patch_and_source_unchanged(self):
        source = SCRIPT.parent.parent
        internal = mod.patch_internal((source / "session_internal.go").read_text())
        transport = mod.patch_transport((source / "session_transport.go").read_text())
        self.assertIn("qa005TransientBodyBytes uint64", internal)
        self.assertIn("qa005OwnedInboundTransient", internal)
        self.assertIn("qa005AddOwnedLocked(s, &s.qa005OwnedInboundTransient", transport)
        self.assertIn("qa005SubtractOwnedLocked(s, &s.qa005OwnedInboundTransient", transport)
        self.assertIn("qa005TransientBodyBytes: qa005TransientBodyBytes", transport)
        self.assertIn("s.mu.Lock()\n\t\t\tqa005AddOwnedLocked(s, &s.qa005OwnedInboundTransient", transport)
        self.assertIn("TestQA005OwnedOverlayTransientInboundBindLifecycle", mod.BENCHMARK_HELPERS)
        self.assertIn('"F5-unreserved-inbound-body"', SCRIPT.read_text())
        self.assertNotIn("qa005TransientBodyBytes", (source / "session_internal.go").read_text())


    def test_session_category_total_reconciliation_is_fail_closed(self):
        helper = mod.BENCHMARK_HELPERS
        self.assertIn("func qa005OwnedConsistentLocked(s *Session) bool", helper)
        self.assertIn("summed == s.qa005OwnedTotal", helper)
        self.assertIn("consistent := qa005OwnedConsistentLocked(session)", helper)
        self.assertIn("valid := qa005OwnedConsistentLocked(session)", helper)
        self.assertIn("TestQA005OwnedOverlayCategoryReconciliation", helper)
        self.assertIn('"reconciles_all_observed_categories_to_session_total": True', SCRIPT.read_text())


    def test_d1_stack_only_alias_dedup_and_no_complete_memory_claim(self):
        h = mod.BENCHMARK_HELPERS
        self.assertIn("func qa005D1StackTextSession(s *Session) (uint64, bool)", h)
        self.assertIn("seen := make(map[uint64]string", h)
        self.assertIn("s.panicMu.Lock()", h)
        self.assertIn("TestQA005OwnedOverlayD1StackTextRetention", h)
        self.assertIn("probe-d1-unique-stack-text-peak-B",
                      mod.patch_benchmark((SCRIPT.parent.parent / "benchmark_test.go").read_text()))
        self.assertIn('"observes_d1_unique_stack_text_only": True', SCRIPT.read_text())
        self.assertNotIn('ReportMetric(float64(p.d1StackPeak), "retained-attributed-B")', h)


    def test_m1_pending_identity_hooks_and_no_unapproved_byte_estimator(self):
        source = SCRIPT.parent.parent
        session = mod.patch_session((source / "session.go").read_text())
        internal = mod.patch_internal((source / "session_internal.go").read_text())
        self.assertIn("qa005RegisterPendingLocked(s, pending)", session)
        self.assertIn("qa005ReleasePendingLocked(s, pending)", session)
        self.assertIn("qa005M1PendingLive map[*pendingRequest]struct{}", internal)
        self.assertIn("TestQA005OwnedOverlayM1PendingIdentityLifetime", mod.BENCHMARK_HELPERS)
        fixture = mod.patch_benchmark((source / "benchmark_test.go").read_text())
        self.assertIn("probe-m1-pending-object-peak-count", fixture)
        self.assertIn('"observes_m1_pending_object_identity_count_not_bytes": True', SCRIPT.read_text())
        self.assertNotIn("unsafe.Sizeof", mod.SESSION_HELPERS)


    def test_m1_static_struct_footprint_remains_separate_unqualified_diagnostic(self):
        source = SCRIPT.parent.parent
        benchmark = mod.patch_benchmark((source / "benchmark_test.go").read_text())
        self.assertIn('"unsafe"', benchmark)
        self.assertIn("probe-m1-pending-struct-logical-peak-B", benchmark)
        self.assertIn("unsafe.Sizeof(pendingRequest{})", mod.BENCHMARK_HELPERS)
        self.assertIn("TestQA005OwnedOverlayM1PendingStructFootprint", mod.BENCHMARK_HELPERS)
        self.assertIn('"m1_pending_struct_logical_footprint_is_not_allocator_bytes": True', SCRIPT.read_text())
        self.assertNotIn('ReportMetric(float64(p.m1PendingStructPeak), "retained-attributed-B")', benchmark)


    def test_worker_queue_capacity_dedup_observer_is_logical_only(self):
        h = mod.BENCHMARK_HELPERS
        self.assertIn("func qa005M1WorkerQueueSample(env *benchmarkEnv)",h)
        self.assertIn("pool.mu.Lock()", h)
        self.assertIn("seenPools := make(map[*callbackWorkerPool]struct{})",h)
        self.assertIn("seenLanes := make(map[*callbackSessionQueue]struct{})",h)
        self.assertIn("seenBacking := make(map[*callbackTask]struct{})",h)
        self.assertIn("unsafe.SliceData(queue.tasks)",h)
        self.assertIn("capacity*taskSize",h)
        self.assertIn("TestQA005OwnedOverlayM1WorkerQueueBackingLifetime",h)
        patched = mod.patch_benchmark((SCRIPT.parent.parent / "benchmark_test.go").read_text())
        self.assertIn("probe-m1-worker-task-slots-logical-peak-B",patched)
        self.assertIn("probe-m1-worker-queue-struct-logical-peak-B",patched)
        self.assertNotIn('ReportMetric(float64(p.m1WorkerSlotPeak), "retained-attributed-B")',patched)
        self.assertIn('"m1_worker_queue_sizes_are_logical_not_allocator_bytes": True',SCRIPT.read_text())


    def test_worker_scheduler_is_immutable_digest_dependency(self):
        self.assertIn('"worker_scheduler.go", "client_connect.go", "client_lifecycle.go")', SCRIPT.read_text())
        self.assertIn('"worker_scheduler_source_sha_is_compatibility_dependency": True', SCRIPT.read_text())
        self.assertNotIn("worker_scheduler.go", mod.PATCHES)


    def test_static_worker_footprint_excludes_channel_and_stack_allocations(self):
        helper = mod.BENCHMARK_HELPERS
        self.assertIn("func qa005M1WorkerStructFootprint(count uint64)",helper)
        self.assertIn("unsafe.Sizeof(callbackWorker{})",helper)
        self.assertIn("TestQA005OwnedOverlayM1WorkerStructFootprint",helper)
        patched = mod.patch_benchmark((SCRIPT.parent.parent / "benchmark_test.go").read_text())
        self.assertIn("probe-m1-worker-struct-logical-peak-B",patched)
        self.assertNotIn('ReportMetric(float64(p.m1WorkerStructPeak), "retained-attributed-B")',patched)
        self.assertIn('"m1_worker_struct_footprint_excludes_stacks_channels_allocator": True',SCRIPT.read_text())


    def test_real_worker_queue_lifetime_uses_scheduler_not_synthetic_only(self):
        self.assertIn("TestQA005OwnedOverlayM1RealWorkerQueueLifecycle",mod.BENCHMARK_HELPERS)
        self.assertIn("newCallbackWorkerPool(callbackApplication, 1, 25*time.Millisecond)",mod.BENCHMARK_HELPERS)
        self.assertIn("slots==0 && queueBytes==0 && lanes==0",mod.BENCHMARK_HELPERS)
        self.assertIn("if live==0 { break }",mod.BENCHMARK_HELPERS)
        self.assertIn("worker_scheduler.go",SCRIPT.read_text())


    def test_client_generation_freeze_and_source_contract(self):
        h = mod.BENCHMARK_HELPERS
        self.assertIn("qa005OwnedClientRegistryValid = true", h)
        self.assertIn("client.generation == expected", h)
        self.assertIn("client.current == env.qa005OwnedClientIdentity[client]", h)
        self.assertIn("client.connectDone == nil", h)
        self.assertIn("TestQA005OwnedOverlayClientTransientGenerationChurn", h)
        self.assertIn("TestQA005OwnedOverlayClientCurrentAndInFlightInvalidation", h)
        fixture = mod.patch_benchmark((SCRIPT.parent.parent / "benchmark_test.go").read_text())
        self.assertIn("qa005OwnedClientEpoch map[*Client]uint64", fixture)
        source = (SCRIPT.parent.parent / "client_connect.go").read_text()
        self.assertIn("c.generation++", source)
        self.assertIn("c.current = session", source)
        self.assertIn("c.current = nil", source)
        self.assertIn('"client_generation_and_current_frozen_fail_closed": True', SCRIPT.read_text())


    def test_retired_client_callback_session_fails_closed(self):
        h = mod.BENCHMARK_HELPERS
        self.assertIn("qa005CallbackOwnerSessionsComplete", h)
        self.assertIn("!env.qa005OwnedCallbackRegistryValid", h)
        self.assertIn("TestQA005OwnedOverlayRetiredClientCallbackSessionFailsClosed", h)
        self.assertIn("TestQA005OwnedOverlayKnownCallbackSessionIsDeduplicated", h)
        self.assertIn("TestQA005OwnedOverlayLateRetiredCallbackSessionInvalidatesWindow", h)
        self.assertIn("qa005CallbackOwnerSessionsComplete(env.server.callbacks, env.qa005OwnedIndex", h)
        self.assertIn('"client_retired_callback_sessions_fail_closed": True', SCRIPT.read_text())
        self.assertIn('"observer_gc_liveness_bias": "NOT_MEASURED"', SCRIPT.read_text())

    def test_sampling_window_integrity_is_diagnostic_only(self):
        h = mod.BENCHMARK_HELPERS
        self.assertIn("func qa005RecordSamplingWindow", h)
        self.assertIn("gap <= 0", h)
        self.assertIn("duration < 0", h)
        self.assertIn("TestQA005OwnedOverlaySamplingWindowEvidence", h)
        self.assertIn('"sampling_window_monotonicity_and_snapshot_duration_tested": True', SCRIPT.read_text())
        self.assertIn('"sampler_max_gap_policy": "NOT_APPROVED_DIAGNOSTIC_ONLY"', SCRIPT.read_text())

    def test_client_real_reconnect_window_regression(self):
        h = mod.BENCHMARK_HELPERS
        self.assertIn("TestQA005OwnedOverlayClientRealReconnectInvalidatesWindow",h)
        self.assertIn("env := newBenchmarkEnv(t, 1, 1, 1, true, false)",h)
        self.assertIn("env.clients[0].Connect(ctx)",h)
        self.assertIn("if qa005OwnedRegistryComplete(env)",h)
        self.assertIn("if _,valid := qa005OwnedPeakUpper(env); valid",h)
        self.assertNotIn("retained-attributed-B",h.split("func TestQA005OwnedOverlayClientRealReconnectInvalidatesWindow",1)[1])


if __name__ == "__main__":
    unittest.main()
