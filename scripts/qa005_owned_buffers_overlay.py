#!/usr/bin/env python3
"""Generate a test-only Go overlay that observes owned buffer storage.

F1/F2/F3/F4 backing storage is tracked by Session under its existing mutex.
This is an UNQUALIFIED diagnostic. Metadata/closures/Panic objects are excluded,
and time sampling can miss fast peaks. Never emit retained-attributed-B.
No repository source file is edited by this script.
V8 additionally tracks F5 unreserved inbound Body through read/handler; all categories remain incomplete.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qa005_charge_probe", ROOT / "qa005_memory_overlay.py")
charge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(charge)

ADAPTER_ID = "QA005-OWNED-BUFFER-OVERLAY-V19-UNQUALIFIED"
SOURCE_FILES = ("benchmark_test.go", "session.go", "session_internal.go", "session_transport.go", "session_control.go", "resource_charges.go", "types.go", "server_lifecycle.go")
FIXTURES = ("qa005_qualification_benchmark_test.go", "benchmark_test.go")


def replace_once(content, needle, replacement, label):
    occurrences = content.count(needle)
    if occurrences != 1:
        raise ValueError(f"{label}: expected one anchor; found {occurrences}")
    return content.replace(needle, replacement, 1)


SESSION_HELPERS = """
// Test-overlay-only: counters represent live backing storage responsibility,
// not Go allocator buckets, policy reservation amounts or foreign object graphs.
func qa005AddOwnedLocked(s *Session, counter *uint64, amount uint64) {
    if amount == 0 { return }
    next, ok := checkedAddUint64(*counter, amount)
    total, totalOK := checkedAddUint64(s.qa005OwnedTotal, amount)
    if !ok || !totalOK { s.qa005OwnedFault = true; return }
    *counter = next
    s.qa005OwnedTotal = total
    if total > s.qa005OwnedPeak { s.qa005OwnedPeak = total }
}

// Control allocation may precede Queue admission, without transferring a
// duplicate allocation when admitted. Requires s.mu already held.
func qa005RegisterControlLocked(s *Session, frame *outboundFrame) {
    if frame == nil || !frame.control || frame.qa005Observed || frame.qa005Enqueued {
        s.qa005OwnedFault = true
        return
    }
    qa005AddOwnedLocked(s, &s.qa005OwnedControl, uint64(cap(frame.bytes)))
    frame.qa005Observed = true
}

// Release only a rejected, never-enqueued Control frame; the normal writer
// path owns the release after FIFO admission. Requires s.mu held.
func qa005DiscardControlBeforeQueueLocked(s *Session, frame *outboundFrame) {
    if frame == nil || !frame.control || frame.qa005Enqueued || !frame.qa005Observed {
        s.qa005OwnedFault = true
        return
    }
    qa005SubtractOwnedLocked(s, &s.qa005OwnedControl, uint64(cap(frame.bytes)))
    frame.qa005Observed = false
}

func qa005SubtractOwnedLocked(s *Session, counter *uint64, amount uint64) {
    if amount == 0 { return }
    next, ok := checkedSubUint64(*counter, amount)
    total, totalOK := checkedSubUint64(s.qa005OwnedTotal, amount)
    if !ok || !totalOK { s.qa005OwnedFault = true; return }
    *counter = next
    s.qa005OwnedTotal = total
}

// M1 test-only identity ledger. This is an OBJECT COUNT, not bytes.
// Active Completion closures can own pendingRequest after Session.Done resets
// s.pending: release ownership only when Completion returns/cancels.
// All functions require Session.mu; no global hot-path atomic in production.
func qa005RegisterPendingLocked(s *Session, pending *pendingRequest) {
    if pending == nil { s.qa005M1PendingFault = true; return }
    if s.qa005M1PendingLive == nil { s.qa005M1PendingLive = make(map[*pendingRequest]struct{}) }
    if _, exists := s.qa005M1PendingLive[pending]; exists { s.qa005M1PendingFault = true; return }
    s.qa005M1PendingLive[pending] = struct{}{}
}

func qa005ReleasePendingLocked(s *Session, pending *pendingRequest) {
    if pending == nil { s.qa005M1PendingFault = true; return }
    if _, ok := s.qa005M1PendingLive[pending]; !ok { s.qa005M1PendingFault = true; return }
    delete(s.qa005M1PendingLive, pending)
}
"""


def patch_internal(content):
    content = replace_once(
        content, "\tafterWrite         func()\n",
        "\tafterWrite         func()\n\tqa005Observed      bool // overlay-only, one charge per tracked allocation\n\tqa005Enqueued      bool // overlay-only, detect duplicate queue admission\n",
        "outbound frame identity")
    content = replace_once(
        content, "\tcompletionCapacityErr bool\n",
        "\tcompletionCapacityErr bool\n\tqa005TransientBodyBytes uint64 // overlay-only unreserved inbound Body\n",
        "inbound temporary frame identity")
    content = replace_once(
        content, "\tactiveWrite               *outboundFrame\n",
        "\tactiveWrite               *outboundFrame\n"
        "\tqa005OwnedOutgoingApp     uint64\n"
        "\tqa005OwnedIncomingApp     uint64\n"
        "\tqa005OwnedIncomingReply   uint64\n"
        "\tqa005OwnedInboundTransient uint64 // test-only Bind/unreserved inbound Body\n"
        "\tqa005OwnedControl         uint64\n"
        "\tqa005OwnedFault           bool\n"
        "\tqa005OwnedTotal           uint64\n"
        "\tqa005OwnedPeak            uint64\n"
        "\tqa005M1PendingLive map[*pendingRequest]struct{} // identity-only, not bytes\n"
        "\tqa005M1PendingFault bool\n"
        "\tqa005AfterAllocation      func() // deterministic overlay-only close interleaving\n",
        "session storage counters")
    content = replace_once(
        content, "\ts.queuedControlBytes = next\n\tif item.barrier {",
        "\ts.queuedControlBytes = next\n"
        "\tif item.qa005Enqueued { s.qa005OwnedFault = true } else if !item.qa005Observed {\n"
        "\t\tqa005AddOwnedLocked(s, &s.qa005OwnedControl, uint64(cap(item.bytes)))\n"
        "\t\titem.qa005Observed = true\n"
        "\t}\n"
        "\titem.qa005Enqueued = true\n\tif item.barrier {",
        "control admission")
    content = replace_once(
        content, "\ts.appQueue = append(s.appQueue, item)\n\ts.cond.Signal()",
        "\ts.appQueue = append(s.appQueue, item)\n"
        "\tif item.qa005Enqueued { s.qa005OwnedFault = true } else if !item.qa005Observed {\n"
        "\t\tqa005AddOwnedLocked(s, &s.qa005OwnedOutgoingApp, uint64(cap(item.bytes)))\n"
        "\t\titem.qa005Observed = true\n"
        "\t}\n"
        "\titem.qa005Enqueued = true\n\ts.cond.Signal()",
        "application queue")
    content = replace_once(
        content,
        "func (s *Session) releaseFrameChargeLocked(item *outboundFrame) {\n"
        "\tif item == nil {\n\t\treturn\n\t}\n\tif item.control {",
        "func (s *Session) releaseFrameChargeLocked(item *outboundFrame) {\n"
        "\tif item == nil {\n\t\treturn\n\t}\n"
        "\tif item.qa005Observed {\n"
        "\t\tif item.control {\n"
        "\t\t\tqa005SubtractOwnedLocked(s, &s.qa005OwnedControl, uint64(cap(item.bytes)))\n"
        "\t\t} else {\n"
        "\t\t\tqa005SubtractOwnedLocked(s, &s.qa005OwnedOutgoingApp, uint64(cap(item.bytes)))\n"
        "\t\t}\n"
        "\t\titem.qa005Observed = false\n"
        "\t}\n\tif item.control {",
        "writer/close release")
    return content.rstrip() + "\n" + SESSION_HELPERS


def patch_charges(content):
    content = replace_once(
        content, "\tbytes            uint64\n\tqueueReleased",
        "\tbytes            uint64\n\tqa005BodyBytes    uint64\n\tqueueReleased",
        "inbound application charge")
    content = replace_once(
        content, "\tbytes    uint64\n\treleased bool",
        "\tbytes    uint64\n\tqa005BodyBytes uint64\n\treleased bool",
        "inbound completion charge")
    content = replace_once(
        content, "\tc.retainedReleased = true\n\tif next, ok := checkedSubUint64(",
        "\tc.retainedReleased = true\n"
        "\tqa005SubtractOwnedLocked(s, &s.qa005OwnedIncomingApp, c.qa005BodyBytes)\n"
        "\tc.qa005BodyBytes = 0\n"
        "\tif next, ok := checkedSubUint64(",
        "application retained return")
    content = replace_once(
        content, "\tc.released = true\n\tif next, ok := checkedSubUint64(",
        "\tc.released = true\n"
        "\tqa005SubtractOwnedLocked(s, &s.qa005OwnedIncomingReply, c.qa005BodyBytes)\n"
        "\tc.qa005BodyBytes = 0\n"
        "\tif next, ok := checkedSubUint64(",
        "completion return")
    return content



def patch_session(content):
    """Register allocated F1 while holding Session.mu before copying the frame.

    Ownership starts at make, not after FIFO admission. An unqueued frame is
    released by its Send* call's defer; successful admission transfers the same
    observation to the outboundFrame. All changes exist only in the Go overlay.
    """
    builder = ("func buildStreamFrame(command wire.CommandID, status wire.CommandStatus, "
               "sequence uint32, payload []byte) ([]byte, error) {")
    content = replace_once(
        content, builder,
        builder.replace("payload []byte)", "payload []byte, qa005Owner ...*Session)"),
        "frame builder optional observer")
    content = replace_once(
        content, "\tframe := make([]byte, length)\n",
        "\tvar frame []byte\n"
        "\tif len(qa005Owner) == 0 || qa005Owner[0] == nil {\n"
        "\t\tframe = make([]byte, length)\n"
        "\t} else {\n"
        "\t\towner := qa005Owner[0]\n"
        "\t\towner.mu.Lock()\n"
        "\t\tframe = make([]byte, length)\n"
        "\t\tqa005AddOwnedLocked(owner, &owner.qa005OwnedOutgoingApp, uint64(cap(frame)))\n"
        "\t\tafter := owner.qa005AfterAllocation\n"
        "\t\towner.mu.Unlock()\n"
        "\t\tif after != nil { after() }\n"
        "\t}\n",
        "registered frame allocation")
    starts = (
        "func (s *Session) SendRequest(",
        "func (s *Session) SendNoWait(",
        "func (s *Session) SendResponse(",
    )
    end = "func (s *Session) applicationSendErrorLocked("
    for index, marker in enumerate(starts):
        begin = content.find(marker)
        after = content.find(starts[index+1] if index+1 < len(starts) else end, begin+len(marker))
        if begin < 0 or after < 0:
            raise ValueError("missing send function boundary: " + marker)
        segment = content[begin:after]
        call = "frame, err := buildStreamFrame("
        if segment.count(call) != 1:
            raise ValueError("send builder call changed: " + marker)
        line_end = segment.index("\n", segment.index(call))
        line = segment[segment.index(call):line_end]
        if not line.endswith("payload)"):
            raise ValueError("unexpected send builder call: " + marker)
        segment = segment.replace(line, line[:-1] + ", s)", 1)
        segment = replace_once(
            segment, "\n\n\ts.mu.Lock()\n\tif err != nil {",
            "\n\tqa005Transferred := false\n"
            "\tif err == nil {\n"
            "\t\tdefer func() {\n"
            "\t\t\tif !qa005Transferred {\n"
            "\t\t\t\ts.mu.Lock()\n"
            "\t\t\t\tqa005SubtractOwnedLocked(s, &s.qa005OwnedOutgoingApp, uint64(cap(frame)))\n"
            "\t\t\t\ts.mu.Unlock()\n"
            "\t\t\t}\n"
            "\t\t}()\n"
            "\t}\n\n\ts.mu.Lock()\n\tif err != nil {",
            "unqueued frame rollback " + marker)
        segment = replace_once(
            segment, "\titem := &outboundFrame{bytes: frame,",
            "\titem := &outboundFrame{bytes: frame, qa005Observed: true,",
            "enqueue ownership transfer " + marker)
        signal = "\ts.signalControl()"
        if segment.count(signal) != 1:
            raise ValueError("unexpected send success boundary: " + marker)
        before_signal = segment.index(signal)
        last_finish = segment.rfind("\ts.finishAdmissionLocked()\n", 0, before_signal)
        if last_finish < 0:
            raise ValueError("missing final admission completion: " + marker)
        segment = (segment[:last_finish] + "\tqa005Transferred = true\n" +
                   segment[last_finish:])
        content = content[:begin] + segment + content[after:]
    content = replace_once(
        content,
        "\t\tadmissionErr = s.enqueueControlLocked(&outboundFrame{bytes: frame, control: true, barrier: true, unbindRequest: true})",
        "\t\tcontrol := &outboundFrame{bytes: frame, control: true, barrier: true, unbindRequest: true}\n"
        "\t\tqa005RegisterControlLocked(s, control)\n"
        "\t\tadmissionErr = s.enqueueControlLocked(control)\n"
        "\t\tif admissionErr != nil { qa005DiscardControlBeforeQueueLocked(s, control) }",
        "Unbind control pre-Queue responsibility")
    content = replace_once(
        content,
        "\ts.pending[sequence] = pending\n",
        "\ts.pending[sequence] = pending\n"
        "\tqa005RegisterPendingLocked(s, pending) // accepted SendRequest; Session.mu held\n",
        "M1 pending admission identity")
    content = replace_once(
        content,
        "\ts.releaseRequestCreditLocked(pending)\n\ts.mu.Unlock()\n",
        "\ts.releaseRequestCreditLocked(pending)\n"
        "\tqa005ReleasePendingLocked(s, pending) // Completion return/cancel, even after Done\n"
        "\ts.mu.Unlock()\n",
        "M1 pending Completion release identity")
    return content


def patch_control(content):
    return replace_once(
        content,
        "\t\t\t\t\tif err := s.enqueueControlLocked(item); err != nil {",
        "\t\t\t\t\tqa005RegisterControlLocked(s, item)\n"
        "\t\t\t\t\tif err := s.enqueueControlLocked(item); err != nil {\n"
        "\t\t\t\t\t\tqa005DiscardControlBeforeQueueLocked(s, item)",
        "Enquire Link pre-Queue ownership")


def patch_transport(content):
    content = replace_once(
        content,
        "\t\tbody = make([]byte, bodyLength)\n\t\tif _, err := io.ReadFull(s.conn, body);",
        "\t\tbody = make([]byte, bodyLength)\n"
        "\t\tif applicationCharge != nil || completionCharge != nil {\n"
        "\t\t\ts.mu.Lock()\n"
        "\t\t\tif applicationCharge != nil {\n"
        "\t\t\t\tapplicationCharge.qa005BodyBytes = uint64(cap(body))\n"
        "\t\t\t\tqa005AddOwnedLocked(s, &s.qa005OwnedIncomingApp, uint64(cap(body)))\n"
        "\t\t\t} else {\n"
        "\t\t\t\tcompletionCharge.qa005BodyBytes = uint64(cap(body))\n"
        "\t\t\t\tqa005AddOwnedLocked(s, &s.qa005OwnedIncomingReply, uint64(cap(body)))\n"
        "\t\t\t}\n"
        "\t\t\ts.mu.Unlock()\n"
        "\t\t} else {\n"
        "\t\t\tqa005TransientBodyBytes = uint64(cap(body))\n"
        "\t\t\ts.mu.Lock()\n"
        "\t\t\tqa005AddOwnedLocked(s, &s.qa005OwnedInboundTransient, qa005TransientBodyBytes)\n"
        "\t\t\ts.mu.Unlock()\n"
        "\t\t}\n"
        "\t\tif _, err := io.ReadFull(s.conn, body);",
        "inbound body allocation")
    content = replace_once(
        content,
        "\tvar completionCharge *completionReadCharge\n",
        "\tvar completionCharge *completionReadCharge\n"
        "\tvar qa005TransientBodyBytes uint64 // overlay-only, within readFrame\n",
        "temporary inbound allocation lifetime")
    content = replace_once(
        content,
        "\t\t\tcompletionCharge.release()\n\t\t}\n",
        "\t\t\tcompletionCharge.release()\n"
        "\t\t\tif qa005TransientBodyBytes != 0 {\n"
        "\t\t\t\ts.mu.Lock()\n"
        "\t\t\t\tqa005SubtractOwnedLocked(s, &s.qa005OwnedInboundTransient, qa005TransientBodyBytes)\n"
        "\t\t\t\ts.mu.Unlock()\n"
        "\t\t\t}\n"
        "\t\t}\n",
        "read failure returns unreserved Body")
    content = replace_once(
        content,
        "\t\tcompletionCapacityErr: completionCapacityErr,\n",
        "\t\tcompletionCapacityErr: completionCapacityErr,\n"
        "\t\tqa005TransientBodyBytes: qa005TransientBodyBytes,\n",
        "transfer unreserved inbound Body to handler")
    content = replace_once(
        content,
        "func (s *Session) handleInboundFrame(inbound inboundFrame) error {\n",
        "func (s *Session) handleInboundFrame(inbound inboundFrame) error {\n"
        "\tif inbound.qa005TransientBodyBytes != 0 {\n"
        "\t\tdefer func() {\n"
        "\t\t\ts.mu.Lock()\n"
        "\t\t\tqa005SubtractOwnedLocked(s, &s.qa005OwnedInboundTransient, inbound.qa005TransientBodyBytes)\n"
        "\t\t\ts.mu.Unlock()\n"
        "\t\t}()\n"
        "\t}\n",
        "handler return after non-retained Body")
    return content


BENCHMARK_HELPERS = """
// This is a compile-time Go struct-layout footprint of callbackWorker,
// multiplied by the live workerCount registered under each pool's mutex.
// It excludes wake channel buffers, goroutine stacks, timers, runtime metadata,
// allocator size-class rounding and user callback references. It must remain
// a separate DIAGNOSTIC and cannot join independent memory peaks.
func qa005RecordSamplingWindow(p *qa005ChargeProbe, started time.Time, duration time.Duration) bool {
    if p == nil || started.IsZero() || duration < 0 {
        if p != nil { p.invalid = true }
        return false
    }
    if !p.ownedLastSampleAt.IsZero() {
        gap := started.Sub(p.ownedLastSampleAt)
        if gap <= 0 {
            p.invalid = true
            return false
        }
        if gap > p.ownedMaxSampleGap { p.ownedMaxSampleGap = gap }
    }
    p.ownedLastSampleAt = started
    if duration > p.ownedMaxSnapshotDuration { p.ownedMaxSnapshotDuration = duration }
    return true
}

// Sampling gaps are diagnostics only. This helper validates monotonic sample
// starts and records snapshot duration; it deliberately has no acceptance
// threshold or qualification PASS path.
func qa005M1WorkerStructFootprint(count uint64) (uint64, bool) {
    size := uint64(unsafe.Sizeof(callbackWorker{}))
    if size == 0 || count > ^uint64(0)/size { return 0, false }
    return count*size, true
}

// M1 Worker/Queue test-only read-only observation. Lock one owner worker
// pool at a time and NEVER acquire Session.mu while holding the pool lock.
// The queue struct itself is a neta-owned object while in p.sessions;
// task backing capacity is retained even if q.head has advanced. cap(tasks)
// (not queued task count) is the logical Go backing-array footprint.
// Counting the allocator's size class, worker goroutine stack, callback
// closure captures or application data is explicitly out of scope.
// A queue, pool or backing start pointer unexpectedly shared between two
// distinct ownership lanes is fail-closed instead of double counted.
func qa005M1WorkerQueueSample(env *benchmarkEnv) (slotBytes, laneBytes, workers, lanes uint64, valid bool) {
    if !qa005OwnedRegistryComplete(env) { return 0, 0, 0, 0, false }
    seenPools := make(map[*callbackWorkerPool]struct{})
    seenLanes := make(map[*callbackSessionQueue]struct{})
    seenBacking := make(map[*callbackTask]struct{})
    taskSize := uint64(unsafe.Sizeof(callbackTask{}))
    laneSize := uint64(unsafe.Sizeof(callbackSessionQueue{}))
    if taskSize == 0 || laneSize == 0 { return 0, 0, 0, 0, false }
    measurePool := func(pool *callbackWorkerPool) bool {
        if pool == nil { return true }
        if _, duplicated := seenPools[pool]; duplicated { return true }
        seenPools[pool] = struct{}{}
        pool.mu.Lock()
        defer pool.mu.Unlock()
        nextWorkers, ok := checkedAddUint64(workers, uint64(pool.workerCount))
        if !ok { return false }
        workers = nextWorkers
        for session, queue := range pool.sessions {
            if session == nil || queue == nil || queue.session != session ||
                queue.head < 0 || queue.head > len(queue.tasks) { return false }
            if _, duplicated := seenLanes[queue]; duplicated { return false }
            seenLanes[queue] = struct{}{}
            nextLanes, ok := checkedAddUint64(lanes, 1)
            if !ok { return false }
            lanes = nextLanes
            nextLaneBytes, ok := checkedAddUint64(laneBytes, laneSize)
            if !ok { return false }
            laneBytes = nextLaneBytes
            if cap(queue.tasks) == 0 { continue }
            backing := unsafe.SliceData(queue.tasks)
            if backing == nil { return false }
            if _, duplicated := seenBacking[backing]; duplicated { return false }
            seenBacking[backing] = struct{}{}
            capacity := uint64(cap(queue.tasks))
            if capacity > ^uint64(0)/taskSize { return false }
            nextSlots, ok := checkedAddUint64(slotBytes, capacity*taskSize)
            if !ok { return false }
            slotBytes = nextSlots
        }
        return true
    }
    measureOwner := func(owner *ownerCallbackDispatcher) bool {
        return owner == nil ||
            (measurePool(owner.application) && measurePool(owner.completion) &&
                measurePool(owner.onClose))
    }
    if !measureOwner(env.server.callbacks) { return 0, 0, 0, 0, false }
    for _, client := range env.clients {
        if client == nil || !measureOwner(client.callbacks) {
            return 0, 0, 0, 0, false
        }
    }
    return slotBytes, laneBytes, workers, lanes, true
}

// M1 per-Session identity count is independent of observed F1-F5 backing
// bytes. Pending map removal is not object-lifetime release: active Completion
// closures may retain objects after Session.Done and map reset.
func qa005M1PendingCount(env *benchmarkEnv) (uint64, bool) {
    if !qa005OwnedRegistryComplete(env) { return 0, false }
    var sum uint64
    for _, s := range qa005OwnedSessions(env) {
        s.mu.Lock()
        invalid := s.qa005M1PendingFault || s.resourceAccountingFailed
        for _, p := range s.pending {
            if _, found := s.qa005M1PendingLive[p]; !found { invalid = true }
        }
        count := uint64(len(s.qa005M1PendingLive))
        s.mu.Unlock()
        if invalid { return 0, false }
        next, ok := checkedAddUint64(sum, count)
        if !ok { return 0, false }
        sum = next
    }
    return sum, true
}

// This is the Go language-level requested struct footprint of one known
// neta-owned pendingRequest, including inline padding but excluding allocator
// size-class rounding, map buckets, callback closure/captures and foreign graphs.
// It is not a physical HeapAlloc estimate nor the qualified retained metric.
func qa005M1PendingStructFootprint(count uint64) (uint64, bool) {
    unit := uint64(unsafe.Sizeof(pendingRequest{}))
    if unit == 0 { return 0, false }
    if count > ^uint64(0)/unit { return 0, false }
    return count * unit, true
}

// D1: observe only neta-created string(debug.Stack()) retained by PanicRecord.
// First, OnClose, Recent can reference the SAME record. Dedup by unique
// per-Session PanicRecord.Sequence; ignore raw recovered foreign object graphs.
// This is requested text length, NOT allocator physical size or total D1 bytes.
func qa005D1StackTextSession(s *Session) (uint64, bool) {
    if s == nil { return 0, false }
    s.panicMu.Lock()
    defer s.panicMu.Unlock()
    seen := make(map[uint64]string, len(s.panicLog.recent)+2)
    var sum uint64
    add := func(r *PanicRecord) bool {
        if r == nil { return true }
        if r.Sequence == 0 || len(r.Stack) == 0 { return false }
        if old, ok := seen[r.Sequence]; ok { return old == r.Stack }
        next, ok := checkedAddUint64(sum, uint64(len(r.Stack)))
        if !ok { return false }
        seen[r.Sequence] = r.Stack
        sum = next
        return true
    }
    if !add(s.panicLog.first) || !add(s.panicLog.onClose) { return 0, false }
    for i := range s.panicLog.recent {
        if !add(&s.panicLog.recent[i].record) { return 0, false }
    }
    return sum, true
}

// Independent D1 and F1-F5 samples are NOT an atomic combined memory peak.
// No nested panicMu and Session.mu locks; same frozen owner-registry policy.
func qa005D1StackTextSample(env *benchmarkEnv) (uint64, bool) {
    if !qa005OwnedRegistryComplete(env) { return 0, false }
    var total uint64
    for _, s := range qa005OwnedSessions(env) {
        amount, ok := qa005D1StackTextSession(s)
        if !ok { return 0, false }
        total, ok = checkedAddUint64(total, amount)
        if !ok { return 0, false }
    }
    return total, true
}

// Stronger observation integrity (test-only): a Session's category storage
// must reconcile exactly with its own atomic-under-mutex total. This does
// NOT imply that the categories cover every allocation owned by neta-go.
func qa005OwnedConsistentLocked(s *Session) bool {
    if s.qa005OwnedFault || s.resourceAccountingFailed { return false }
    amounts := [5]uint64{
        s.qa005OwnedOutgoingApp, s.qa005OwnedIncomingApp,
        s.qa005OwnedIncomingReply, s.qa005OwnedControl,
        s.qa005OwnedInboundTransient,
    }
    var summed uint64
    for _, amount := range amounts {
        next, ok := checkedAddUint64(summed, amount)
        if !ok { return false }
        summed = next
    }
    return summed == s.qa005OwnedTotal
}

// Check callback-dispatcher ownership without taking Session.mu under pool.mu.
// A queue remains in pool.sessions while a callback is active or queued. If it
// references a Session absent from the frozen owner set, that retired generation
// is an untracked owner and the observation must fail closed.
func qa005CallbackOwnerSessionsComplete(owner *ownerCallbackDispatcher, knownSessions map[*Session]struct{}, seenPools map[*callbackWorkerPool]struct{}) bool {
    if owner == nil { return true }
    pools := []*callbackWorkerPool{owner.application, owner.completion, owner.onClose}
    for _, pool := range pools {
        if pool == nil { continue }
        if _, duplicate := seenPools[pool]; duplicate { continue }
        seenPools[pool] = struct{}{}
        pool.mu.Lock()
        for session, queue := range pool.sessions {
            if session == nil || queue == nil || queue.session != session {
                pool.mu.Unlock()
                return false
            }
            if _, known := knownSessions[session]; !known {
                pool.mu.Unlock()
                return false
            }
        }
        pool.mu.Unlock()
    }
    return true
}

// Overlay-only snapshot: briefly lock Server list, then each Session separately.
// The resulting global sample is NOT an atomic heap snapshot.
// Overlay-only ownership set: Server lock is released before Session locks.
func qa005OwnedSessions(env *benchmarkEnv) []*Session {
    if env.qa005OwnedRegistry != nil { return env.qa005OwnedRegistry }
    env.server.mu.Lock()
    // Freeze admission epoch under the same lock as the Server map snapshot.
    // A new Session that opens AND closes between samples still invalidates.
    env.qa005OwnedBaselineAdmissionEpoch = env.server.qa005OwnedAdmissionEpoch
    sessions := make([]*Session, 0, len(env.server.sessions)+len(env.sessions))
    seen := make(map[*Session]struct{}, len(env.server.sessions)+len(env.sessions))
    for session := range env.server.sessions {
        if _, exists := seen[session]; !exists {
            seen[session] = struct{}{}
            sessions = append(sessions, session)
        }
    }
    env.server.mu.Unlock()
    for _, session := range env.sessions {
        if _, exists := seen[session]; !exists {
            seen[session] = struct{}{}
            sessions = append(sessions, session)
        }
    }
    // Client generations may be created and retired without ever appearing in
    // env.sessions or Server's current map at the next sampling tick.
    // Freeze *both* the attempt epoch and the Client's current Session.
    // An in-flight Connect at freeze has no stable owner set: fail closed.
    env.qa005OwnedClientEpoch = make(map[*Client]uint64, len(env.clients))
    env.qa005OwnedClientIdentity = make(map[*Client]*Session, len(env.clients))
    env.qa005OwnedClientRegistryValid = true
    for _, client := range env.clients {
        if client == nil { env.qa005OwnedClientRegistryValid = false; continue }
        if _, duplicated := env.qa005OwnedClientEpoch[client]; duplicated { continue }
        client.mu.Lock()
        generation := client.generation
        current := client.current
        unsafeWindow := client.stopped || client.connectDone != nil ||
            generation == ^uint64(0)
        client.mu.Unlock()
        if unsafeWindow { env.qa005OwnedClientRegistryValid = false }
        env.qa005OwnedClientEpoch[client] = generation
        env.qa005OwnedClientIdentity[client] = current
        if current != nil {
            if _, known := seen[current]; !known {
                seen[current] = struct{}{}
                sessions = append(sessions, current)
            }
        }
    }
    // The dispatcher's Session map is the only live owner registry for a
    // retired generation whose callback is still queued/running. Do not retain
    // those Sessions in the measurement registry: that would perturb GC
    // liveness. If any such Session is absent from the initial owner snapshot,
    // mark the whole window INCONCLUSIVE.
    env.qa005OwnedCallbackRegistryValid = true
    seenPools := make(map[*callbackWorkerPool]struct{})
    if !qa005CallbackOwnerSessionsComplete(env.server.callbacks, seen, seenPools) {
        env.qa005OwnedCallbackRegistryValid = false
    }
    for _, client := range env.clients {
        if client != nil && !qa005CallbackOwnerSessionsComplete(client.callbacks, seen, seenPools) {
            env.qa005OwnedCallbackRegistryValid = false
        }
    }
    return sessions
}

// Reset each Session HWM at the start of the measured traffic window.
func qa005ResetOwnedHighwaters(env *benchmarkEnv) {
    sessions := qa005OwnedSessions(env)
    env.qa005OwnedRegistry = sessions
    env.qa005OwnedIndex = make(map[*Session]struct{}, len(sessions))
    for _, session := range sessions {
        env.qa005OwnedIndex[session] = struct{}{}
    }
    for _, session := range sessions {
        session.mu.Lock()
        session.qa005OwnedPeak = session.qa005OwnedTotal
        session.mu.Unlock()
    }
}

// A Session removed from the Server's current map may still own callback bodies.
func qa005OwnedRegistryComplete(env *benchmarkEnv) bool {
    if len(env.qa005OwnedRegistry) == 0 || !env.qa005OwnedClientRegistryValid ||
        !env.qa005OwnedCallbackRegistryValid {
        return false
    }
    if len(env.qa005OwnedClientEpoch) != len(env.qa005OwnedClientIdentity) {
        return false
    }
    // Verify Client's monotonic connect-attempt epoch and current identity
    // under the Client mutex. No nested Client/Server/Session lock.
    // A generation started AND retired between samples must invalidate.
    for _, client := range env.clients {
        if client == nil { return false }
        expected, known := env.qa005OwnedClientEpoch[client]
        if !known { return false }
        client.mu.Lock()
        complete := !client.stopped && client.connectDone == nil &&
            client.generation == expected &&
            client.current == env.qa005OwnedClientIdentity[client]
        client.mu.Unlock()
        if !complete { return false }
    }
    // Recheck callback queues at every sample. A retired generation can
    // enqueue/retain work after the initial freeze; never silently omit it.
    seenPools := make(map[*callbackWorkerPool]struct{})
    if !qa005CallbackOwnerSessionsComplete(env.server.callbacks, env.qa005OwnedIndex, seenPools) {
        return false
    }
    for _, client := range env.clients {
        if client == nil || !qa005CallbackOwnerSessionsComplete(client.callbacks, env.qa005OwnedIndex, seenPools) {
            return false
        }
    }
    env.server.mu.Lock()
    defer env.server.mu.Unlock()
    if env.server.qa005OwnedAdmissionEpoch != env.qa005OwnedBaselineAdmissionEpoch { return false }
    for session := range env.server.sessions {
        if _, known := env.qa005OwnedIndex[session]; !known { return false }
    }
    return true
}

// Sum of independently reached per-Session HWM values. This is an UPPER BOUND
// over tracked sessions and NOT a simultaneous global peak or retained-attributed-B.
func qa005OwnedPeakUpper(env *benchmarkEnv) (uint64, bool) {
    if !qa005OwnedRegistryComplete(env) { return 0, false }
    var upper uint64
    for _, session := range qa005OwnedSessions(env) {
        session.mu.Lock()
        peak := session.qa005OwnedPeak
        consistent := qa005OwnedConsistentLocked(session)
        session.mu.Unlock()
        if !consistent { return 0, false }
        next, ok := checkedAddUint64(upper, peak)
        if !ok { return 0, false }
        upper = next
    }
    return upper, true
}

func qa005SampleOwnedBuffers(env *benchmarkEnv) (uint64, bool) {
    if !qa005OwnedRegistryComplete(env) { return 0, false }
    sessions := qa005OwnedSessions(env)
    var total uint64
    for _, session := range sessions {
        session.mu.Lock()
        amounts := [5]uint64{
            session.qa005OwnedOutgoingApp, session.qa005OwnedIncomingApp,
            session.qa005OwnedIncomingReply, session.qa005OwnedControl,
            session.qa005OwnedInboundTransient,
        }
        valid := qa005OwnedConsistentLocked(session)
        session.mu.Unlock()
        if !valid { return 0, false }
        for _, amount := range amounts {
            next, ok := checkedAddUint64(total, amount)
            if !ok { return 0, false }
            total = next
        }
    }
    return total, true
}


// The end of one queue is not the end of inbound Application responsibility:
// its backing Body survives callback start and is freed at callback return.
// A matched inbound Response similarly survives until Completion release.
func TestQA005OwnedOverlayApplicationCompletionLifetimes(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    s.mu.Lock()
    if err := s.reserveOutgoingApplicationLocked(16); err != nil {
        s.mu.Unlock(); t.Fatal(err)
    }
    item := &outboundFrame{bytes: make([]byte, 16, 32), applicationCharged: true}
    if err := s.enqueueApplicationLocked(item); err != nil {
        s.mu.Unlock(); t.Fatal(err)
    }
    if s.qa005OwnedOutgoingApp != 32 {
        s.mu.Unlock(); t.Fatalf("outgoing owned = %d, want backing cap 32", s.qa005OwnedOutgoingApp)
    }
    // A writer claim only moves the existing frame pointer; no second charge.
    s.activeWrite = item
    if s.qa005OwnedOutgoingApp != 32 { s.mu.Unlock(); t.Fatal("double counted writer claim") }
    s.releaseFrameChargeLocked(item)
    s.activeWrite = nil
    if s.qa005OwnedOutgoingApp != 0 || item.qa005Observed || s.qa005OwnedTotal != 0 || s.qa005OwnedPeak < 32 || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("outgoing frame did not release exactly once")
    }

    app, err := s.reserveIncomingApplicationLocked(22)
    if err != nil { s.mu.Unlock(); t.Fatal(err) }
    app.qa005BodyBytes = 12
    qa005AddOwnedLocked(s, &s.qa005OwnedIncomingApp, 12)
    s.mu.Unlock()
    app.releaseQueue()
    s.mu.Lock()
    if s.qa005OwnedIncomingApp != 12 || app.retainedReleased {
        s.mu.Unlock(); t.Fatal("Application Body was lost at callback start")
    }
    s.mu.Unlock()
    app.releaseRetained()
    app.releaseRetained() // idempotent on callback completion
    s.mu.Lock()
    if s.qa005OwnedIncomingApp != 0 || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("Application Body was not released once")
    }

    completion := s.reserveCompletionLocked(22)
    if completion == nil { s.mu.Unlock(); t.Fatal("Completion reservation rejected") }
    completion.qa005BodyBytes = 12
    qa005AddOwnedLocked(s, &s.qa005OwnedIncomingReply, 12)
    if s.qa005OwnedIncomingReply != 12 { s.mu.Unlock(); t.Fatal("Completion Body missing") }
    s.mu.Unlock()
    completion.release()
    completion.release() // idempotent on terminal return
    s.mu.Lock()
    if s.qa005OwnedIncomingReply != 0 || s.qa005OwnedFault || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("Completion Body ownership or accounting invalid")
    }
    s.mu.Unlock()
}

// Overlay-only lifecycle sanity: an accepted control allocation is counted once,
// remains counted until release, and is not counted again at writer transfer.
func TestQA005OwnedOverlayControlLifecycle(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    s.mu.Lock()
    frame := &outboundFrame{control: true, bytes: make([]byte, 12, 32)}
    if err := s.enqueueControlLocked(frame); err != nil { s.mu.Unlock(); t.Fatal(err) }
    if s.qa005OwnedControl != 32 { s.mu.Unlock(); t.Fatalf("control bytes = %d, want 32", s.qa005OwnedControl) }
    if s.qa005OwnedFault { s.mu.Unlock(); t.Fatal("unexpected accounting fault") }
    s.releaseFrameChargeLocked(frame)
    if s.qa005OwnedControl != 0 || frame.qa005Observed { s.mu.Unlock(); t.Fatal("control storage must be released") }
    s.mu.Unlock()
}

// Regression: an F1 allocation is counted before Queue admission, and its
// Queue -> Writer transfer must not count it again.
func TestQA005OwnedOverlayPreQueueTransferAndRollback(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    payload := []byte("owned-frame")
    frame, err := buildStreamFrame(wire.CommandStreamRequest, wire.StatusOK, 0, payload, s)
    if err != nil { t.Fatal(err) }
    expected := uint64(cap(frame))
    s.mu.Lock()
    if s.qa005OwnedOutgoingApp != expected || s.qa005OwnedTotal != expected {
        s.mu.Unlock(); t.Fatal("F1 allocation not tracked before admission")
    }
    if err := s.reserveOutgoingApplicationLocked(uint64(len(frame))); err != nil {
        s.mu.Unlock(); t.Fatal(err)
    }
    item := &outboundFrame{bytes: frame, applicationCharged: true, qa005Observed: true}
    if err := s.enqueueApplicationLocked(item); err != nil {
        s.mu.Unlock(); t.Fatal(err)
    }
    if s.qa005OwnedOutgoingApp != expected || !item.qa005Enqueued || s.qa005OwnedFault {
        s.mu.Unlock(); t.Fatal("Queue must transfer, never duplicate, pre-owned F1")
    }
    s.activeWrite = item
    if s.qa005OwnedOutgoingApp != expected { s.mu.Unlock(); t.Fatal("Writer transfer double counted") }
    s.releaseFrameChargeLocked(item)
    s.activeWrite = nil
    s.releaseFrameChargeLocked(item)
    if s.qa005OwnedOutgoingApp != 0 || s.qa005OwnedTotal != 0 || s.qa005OwnedFault || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("F1 writer return/double release invalid")
    }
    s.mu.Unlock()
    orphan, err := buildStreamFrame(wire.CommandStreamRequest, wire.StatusOK, 0, payload, s)
    if err != nil { t.Fatal(err) }
    s.mu.Lock()
    if s.qa005OwnedOutgoingApp != uint64(cap(orphan)) {
        s.mu.Unlock(); t.Fatal("unqueued built frame missing")
    }
    qa005SubtractOwnedLocked(s, &s.qa005OwnedOutgoingApp, uint64(cap(orphan)))
    if s.qa005OwnedTotal != 0 || s.qa005OwnedFault {
        s.mu.Unlock(); t.Fatal("unqueued frame rollback failed")
    }
    s.mu.Unlock()
}

// Forced Close racing a real SendNoWait after make must keep the built F1
// allocation counted until the Send method returns and its defer runs.
func TestQA005OwnedOverlayForcedCloseDuringBuild(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    allocated := make(chan struct{})
    resume := make(chan struct{})
    s.mu.Lock()
    s.state = SessionStateBound
    s.qa005AfterAllocation = func() { close(allocated); <-resume }
    s.mu.Unlock()
    results := make(chan error, 1)
    go func() {
        _, err := s.SendNoWait([]byte("close-race"))
        results <- err
    }()
    select {
    case <-allocated:
    case <-time.After(2*time.Second):
        t.Fatal("SendNoWait failed to allocate during test")
    }
    s.mu.Lock()
    if s.qa005OwnedOutgoingApp == 0 || s.admissionCount != 1 || s.qa005OwnedFault {
        s.mu.Unlock(); t.Fatal("built frame not owned during in-flight admission")
    }
    s.mu.Unlock()
    s.beginClose(ErrClosed, true)
    select {
    case <-s.Done(): t.Fatal("Done closed before in-flight Send release")
    default:
    }
    close(resume)
    select {
    case err := <-results:
        if !errors.Is(err, ErrClosed) { t.Fatalf("SendNoWait after Close = %v, want ErrClosed", err) }
    case <-time.After(2*time.Second):
        t.Fatal("in-flight SendNoWait did not return")
    }
    select {
    case <-s.Done():
    case <-time.After(2*time.Second): t.Fatal("Done did not follow admission cleanup")
    }
    s.mu.Lock()
    if s.qa005OwnedOutgoingApp != 0 || s.qa005OwnedTotal != 0 || s.qa005OwnedFault || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("Close-raced F1 allocation not released exactly once")
    }
    s.mu.Unlock()
}

// The Queue charge ends at callback start; both F2 and F3 must survive Done
// while a user callback remains active, then release when that callback returns.
func TestQA005OwnedOverlayCallbacksAfterDone(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    s.mu.Lock()
    app, err := s.reserveIncomingApplicationLocked(32)
    if err != nil { s.mu.Unlock(); t.Fatal(err) }
    completion := s.reserveCompletionLocked(32)
    if completion == nil { s.mu.Unlock(); t.Fatal("completion reservation rejected") }
    app.qa005BodyBytes = 23
    completion.qa005BodyBytes = 19
    qa005AddOwnedLocked(s, &s.qa005OwnedIncomingApp, app.qa005BodyBytes)
    qa005AddOwnedLocked(s, &s.qa005OwnedIncomingReply, completion.qa005BodyBytes)
    s.mu.Unlock()
    app.releaseQueue()
    entered := make(chan struct{},2)
    resume := make(chan struct{})
    var active sync.WaitGroup
    active.Add(2)
    go func() {
        defer active.Done()
        s.invokeUserCallback("OnRequest", func() {
            defer app.releaseRetained()
            entered <- struct{}{}
            <-resume
        })
    }()
    go func() {
        defer active.Done()
        s.invokeUserCallback("Completion", func() {
            defer completion.release()
            entered <- struct{}{}
            <-resume
        })
    }()
    for i:=0; i<2; i++ {
        select {
        case <-entered:
        case <-time.After(2*time.Second): t.Fatal("callback did not start")
        }
    }
    s.beginClose(ErrClosed,true)
    select {
    case <-s.Done():
    case <-time.After(2*time.Second): t.Fatal("Close did not complete internal teardown")
    }
    s.mu.Lock()
    if s.qa005OwnedIncomingApp != 23 || s.qa005OwnedIncomingReply != 19 || s.qa005OwnedTotal != 42 {
        s.mu.Unlock(); t.Fatal("Done prematurely released active callback payloads")
    }
    s.mu.Unlock()
    close(resume)
    active.Wait()
    s.mu.Lock()
    if s.qa005OwnedTotal != 0 || s.qa005OwnedFault || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("active callback retention did not finish on return")
    }
    s.mu.Unlock()
}

// Panic recovery must run callback defers and release owned bodies while
// raw arbitrary recovered objects remain excluded from byte attribution.
func TestQA005OwnedOverlayPanicCleanup(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    s.mu.Lock()
    app, err := s.reserveIncomingApplicationLocked(30)
    if err != nil { s.mu.Unlock(); t.Fatal(err) }
    app.qa005BodyBytes = 20
    qa005AddOwnedLocked(s, &s.qa005OwnedIncomingApp, 20)
    s.mu.Unlock()
    app.releaseQueue()
    s.invokeUserCallback("OnRequest", func() {
        defer app.releaseRetained()
        panic("qa005-test-only")
    })
    s.mu.Lock()
    if s.qa005OwnedIncomingApp != 0 || s.qa005OwnedTotal != 0 || s.qa005OwnedFault || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("callback Panic leaked retained body accounting")
    }
    s.mu.Unlock()
    select {
    case <-s.Done():
    case <-time.After(2*time.Second): t.Fatal("Panic did not terminate the Session")
    }
}


// A Server Session disappears from the live map at Close but its active
// callbacks can still own F2/F3. Frozen registry observes it; a newly admitted
// unregistered Session makes the diagnostic invalid, not silently zero.
func TestQA005OwnedOverlayFrozenRegistry(t *testing.T) {
    serverSession := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    clientSession := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    server := &Server{sessions: make(map[*Session]struct{})}
    server.sessions[serverSession] = struct{}{}
    env := &benchmarkEnv{server: server, sessions: []*Session{clientSession}}
    qa005ResetOwnedHighwaters(env)
    if len(env.qa005OwnedRegistry) != 2 || !qa005OwnedRegistryComplete(env) {
        t.Fatal("initial owner Session registry incomplete")
    }
    serverSession.mu.Lock()
    qa005AddOwnedLocked(serverSession, &serverSession.qa005OwnedIncomingApp, 17)
    serverSession.mu.Unlock()
    server.mu.Lock()
    delete(server.sessions, serverSession)
    server.mu.Unlock()
    value, valid := qa005SampleOwnedBuffers(env)
    if !valid || value != 17 { t.Fatalf("removed Session lost: value=%d valid=%v",value,valid) }
    fresh := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    server.mu.Lock()
    server.sessions[fresh] = struct{}{}
    server.mu.Unlock()
    if _, valid := qa005SampleOwnedBuffers(env); valid {
        t.Fatal("unregistered Server Session must invalidate memory observation")
    }
    serverSession.mu.Lock()
    qa005SubtractOwnedLocked(serverSession, &serverSession.qa005OwnedIncomingApp, 17)
    if serverSession.qa005OwnedTotal != 0 || serverSession.qa005OwnedFault {
        serverSession.mu.Unlock(); t.Fatal("frozen Session failed final release")
    }
    serverSession.mu.Unlock()
}


// F4 is counted once from pre-Queue registration through FIFO/Writer transfer.
// A rejected Control frame must release its pre-Queue backing storage.
func TestQA005OwnedOverlayPreQueueControlTransferAndReject(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    s.mu.Lock()
    frame := &outboundFrame{control: true, bytes: make([]byte, 12, 64)}
    qa005RegisterControlLocked(s, frame)
    if s.qa005OwnedControl != 64 || s.qa005OwnedTotal != 64 {
        s.mu.Unlock(); t.Fatal("control pre-Queue registration missing")
    }
    if err := s.enqueueControlLocked(frame); err != nil { s.mu.Unlock(); t.Fatal(err) }
    if !frame.qa005Enqueued || s.qa005OwnedControl != 64 || s.qa005OwnedFault {
        s.mu.Unlock(); t.Fatal("control Queue admission duplicated pre-owned backing")
    }
    s.activeWrite = frame
    if s.qa005OwnedControl != 64 { s.mu.Unlock(); t.Fatal("control Writer transfer duplicated ownership") }
    s.releaseFrameChargeLocked(frame)
    s.activeWrite = nil
    if s.qa005OwnedTotal != 0 || s.qa005OwnedFault || s.resourceAccountingFailed {
        s.mu.Unlock(); t.Fatal("successful Control release wrong")
    }
    s.config.maxQueuedControlBytes = 1
    rejected := &outboundFrame{control: true, bytes: make([]byte, 12, 48)}
    qa005RegisterControlLocked(s, rejected)
    if s.qa005OwnedControl != 48 { s.mu.Unlock(); t.Fatal("rejected control not counted before Queue") }
    if err := s.enqueueControlLocked(rejected); !errors.Is(err, ErrCapacity) {
        s.mu.Unlock(); t.Fatalf("unexpected Control rejection: %v", err)
    }
    qa005DiscardControlBeforeQueueLocked(s, rejected)
    if s.qa005OwnedControl != 0 || s.qa005OwnedTotal != 0 || s.qa005OwnedFault ||
        rejected.qa005Enqueued || rejected.qa005Observed {
        s.mu.Unlock(); t.Fatal("Control rejection released incorrectly")
    }
    s.mu.Unlock()
}


// A Session reachable from both a Server set and an env slice is the same
// backing object, not two allocations; the snapshot must count it only once.
func TestQA005OwnedOverlayDeduplicatesSessionIdentity(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    server := &Server{sessions: make(map[*Session]struct{})}
    server.sessions[s] = struct{}{}
    env := &benchmarkEnv{server: server, sessions: []*Session{s, s}}
    qa005ResetOwnedHighwaters(env)
    if len(env.qa005OwnedRegistry) != 1 || !qa005OwnedRegistryComplete(env) {
        t.Fatal("duplicate Session identity not removed from observer registry")
    }
    s.mu.Lock()
    qa005AddOwnedLocked(s, &s.qa005OwnedOutgoingApp, 31)
    s.mu.Unlock()
    observed, valid := qa005SampleOwnedBuffers(env)
    upper, upperValid := qa005OwnedPeakUpper(env)
    if !valid || !upperValid || observed != 31 || upper != 31 {
        t.Fatalf("same owned object counted multiple times: sampled=%d valid=%v upper=%d upperValid=%v", observed,valid,upper,upperValid)
    }
    s.mu.Lock()
    qa005SubtractOwnedLocked(s, &s.qa005OwnedOutgoingApp, 31)
    if s.qa005OwnedFault || s.qa005OwnedTotal != 0 { s.mu.Unlock(); t.Fatal("duplicate identity release fault") }
    s.mu.Unlock()
}


// The live-map check alone misses a Server Session admitted then removed
// entirely between observer ticks. The immutable admission epoch catches it.
func TestQA005OwnedOverlayTransientAdmissionChurn(t *testing.T) {
    original := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    server := &Server{sessions: map[*Session]struct{}{original: {}}}
    env := &benchmarkEnv{server: server}
    qa005ResetOwnedHighwaters(env)
    if !qa005OwnedRegistryComplete(env) { t.Fatal("initial frozen identity invalid") }
    ephemeral := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    server.mu.Lock()
    server.sessions[ephemeral] = struct{}{}
    server.qa005OwnedAdmissionEpoch++
    delete(server.sessions, ephemeral)
    server.mu.Unlock()
    // No new entry remains in the map; the generation MUST still reject.
    if _, ok := qa005SampleOwnedBuffers(env); ok {
        t.Fatal("transient Server owner wrongly accepted after remove")
    }
    if _, ok := qa005OwnedPeakUpper(env); ok {
        t.Fatal("transient Server owner wrongly accepted in HWM upper")
    }
    // A frozen window cannot be reset in-place. Use a distinct benchmarkEnv
    // so a late Session cannot be silently admitted into an old evidence set.
    if qa005OwnedRegistryComplete(env) { t.Fatal("old window unexpectedly became valid") }
    nextWindow := &benchmarkEnv{server: server}
    qa005ResetOwnedHighwaters(nextWindow)
    if !qa005OwnedRegistryComplete(nextWindow) { t.Fatal("distinct new window should be valid") }
}


// F5 unreserved Bind Body belongs to this Session through read and handler.
// Read failures release before returning; successful reads transfer to handler.
func TestQA005OwnedOverlayTransientInboundBindLifecycle(t *testing.T) {
    frame, err := wire.EncodeBindRequestV2(19, wire.Bind{
        Type: wire.BindBiDirectional, SystemID: "qa005",
    })
    if err != nil { t.Fatal(err) }
    for _, cut := range []bool{false, true} {
        t.Run(map[bool]string{false:"handler-return", true:"read-error"}[cut], func(t *testing.T) {
            a, peer := net.Pipe()
            defer a.Close()
            s := newSession(a, defaultSessionConfig(),
                sessionIdentity{role: sessionRoleServer}, nil, sessionHandlers{})
            go func() {
                if cut { _, _ = peer.Write(frame[:len(frame)-1]) } else { _, _ = peer.Write(frame) }
                _ = peer.Close()
            }()
            inbound, readErr := s.readFrame()
            if cut {
                if readErr == nil { t.Fatal("expected truncated Body read error") }
                s.mu.Lock()
                live, total, fault := s.qa005OwnedInboundTransient, s.qa005OwnedTotal, s.qa005OwnedFault
                s.mu.Unlock()
                if live != 0 || total != 0 || fault {
                    t.Fatalf("F5 short-read failure leaked/underflowed: live=%d total=%d fault=%v",live,total,fault)
                }
                return
            }
            if readErr != nil { t.Fatal(readErr) }
            if inbound.applicationCharge != nil || inbound.completionCharge != nil ||
                inbound.qa005TransientBodyBytes == 0 { t.Fatal("unreserved Bind Body not classified F5") }
            s.mu.Lock()
            live, total := s.qa005OwnedInboundTransient, s.qa005OwnedTotal
            s.mu.Unlock()
            if live != uint64(cap(inbound.frame.Body)) || total != live {
                t.Fatalf("F5 read ownership live=%d total=%d cap=%d",live,total,cap(inbound.frame.Body))
            }
            // Trigger an immediate terminal handler path, without Bind-validator activity.
            inbound.frame.Header.Sequence = 0
            if err := s.handleInboundFrame(inbound); err == nil {
                t.Fatal("expected zero-sequence protocol error")
            }
            s.mu.Lock()
            live, total, fault := s.qa005OwnedInboundTransient, s.qa005OwnedTotal, s.qa005OwnedFault
            s.mu.Unlock()
            if live != 0 || total != 0 || fault {
                t.Fatalf("F5 handler cleanup live=%d total=%d fault=%v",live,total,fault)
            }
        })
    }
}


// An apparently plausible HWM or sampled value must be rejected if any tracked
// category has drifted from the per-Session total without setting a fault flag.
func TestQA005OwnedOverlayCategoryReconciliation(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    server := &Server{sessions: map[*Session]struct{}{s: {}}}
    env := &benchmarkEnv{server: server}
    qa005ResetOwnedHighwaters(env)
    s.mu.Lock()
    qa005AddOwnedLocked(s, &s.qa005OwnedInboundTransient, 23)
    s.qa005OwnedInboundTransient++ // inject silent category drift
    s.mu.Unlock()
    if _, valid := qa005SampleOwnedBuffers(env); valid {
        t.Fatal("inconsistent category sample accepted")
    }
    if _, valid := qa005OwnedPeakUpper(env); valid {
        t.Fatal("inconsistent category HWM upper accepted")
    }
    s.mu.Lock()
    s.qa005OwnedInboundTransient--
    s.mu.Unlock()
    observed, valid := qa005SampleOwnedBuffers(env)
    upper, upperValid := qa005OwnedPeakUpper(env)
    if !valid || !upperValid || observed != 23 || upper != 23 {
        t.Fatalf("reconciled F5 failed: sample=%d valid=%v upper=%d upperValid=%v",
            observed, valid, upper, upperValid)
    }
    s.mu.Lock()
    qa005SubtractOwnedLocked(s, &s.qa005OwnedInboundTransient, 23)
    if s.qa005OwnedTotal != 0 || !qa005OwnedConsistentLocked(s) {
        s.mu.Unlock()
        t.Fatal("release failed to reconcile")
    }
    s.mu.Unlock()
}


// First/Recent and OnClose/Recent aliases charge one neta Stack allocation,
// independent of raw panic object size. Eviction must preserve First/OnClose.
func TestQA005OwnedOverlayD1StackTextRetention(t *testing.T) {
    cfg := defaultSessionConfig()
    cfg.callbackPanicRingCapacity = 1
    cfg.callbackPanicByteBudget = 1<<20
    s := newSession(nil, cfg, sessionIdentity{}, nil, sessionHandlers{})
    foreign := &struct{ payload []byte }{payload: make([]byte, 1<<18)}
    s.recordCallbackPanic("OnRequest", foreign)
    first, valid := qa005D1StackTextSession(s)
    if !valid || first == 0 { t.Fatal("missing First stack") }
    s.panicMu.Lock()
    if len(s.panicLog.recent)!=1 || s.panicLog.first.Sequence != s.panicLog.recent[0].record.Sequence ||
        s.panicLog.firstRaw != foreign { s.panicMu.Unlock(); t.Fatal("First/Recent alias or raw ownership") }
    firstSize := len(s.panicLog.first.Stack)
    s.panicMu.Unlock()
    if first != uint64(firstSize) { t.Fatalf("double charged First/Recent: %d", first) }
    s.recordCallbackPanic("OnClose", foreign)
    s.panicMu.Lock()
    if len(s.panicLog.recent)!=1 || s.panicLog.onCloseRaw != foreign ||
        s.panicLog.onClose.Sequence != s.panicLog.recent[0].record.Sequence {
        s.panicMu.Unlock(); t.Fatal("OnClose/Recent alias or raw ownership")
    }
    onCloseSize := len(s.panicLog.onClose.Stack)
    s.panicMu.Unlock()
    got, valid := qa005D1StackTextSession(s)
    if !valid || got != uint64(firstSize+onCloseSize) { t.Fatalf("alias sum %d valid=%v", got,valid) }
    s.recordCallbackPanic("OnRequest", "evict")
    s.panicMu.Lock()
    if len(s.panicLog.recent)!=1 { s.panicMu.Unlock(); t.Fatal("Recent ring missing") }
    recent := s.panicLog.recent[0].record
    s.panicLog.recent[0].record.Sequence = s.panicLog.first.Sequence
    s.panicLog.recent[0].record.Stack = "invalid-alias"
    s.panicMu.Unlock()
    if _,valid := qa005D1StackTextSession(s); valid { t.Fatal("conflicting alias accepted") }
    s.panicMu.Lock()
    s.panicLog.recent[0].record = recent
    s.panicMu.Unlock()
    got, valid = qa005D1StackTextSession(s)
    want := uint64(firstSize+onCloseSize+len(recent.Stack))
    if !valid || got != want { t.Fatalf("eviction retained %d, want %d, valid=%v",got,want,valid) }
    server := &Server{sessions: map[*Session]struct{}{s: {}}}
    env := &benchmarkEnv{server:server}
    qa005ResetOwnedHighwaters(env)
    sampled,valid := qa005D1StackTextSample(env)
    if !valid || sampled!=want || sampled>=uint64(len(foreign.payload)) {
        t.Fatalf("external graph wrongly included or alias wrong: %d valid=%v",sampled,valid)
    }
    limited := defaultSessionConfig()
    limited.callbackPanicRingCapacity = 1
    limited.callbackPanicByteBudget = 1
    small := newSession(nil,limited,sessionIdentity{},nil,sessionHandlers{})
    small.recordCallbackPanic("OnRequest",foreign)
    small.panicMu.Lock()
    firstOnly := uint64(len(small.panicLog.first.Stack))
    hasRecent := len(small.panicLog.recent) > 0
    small.panicMu.Unlock()
    measured,valid := qa005D1StackTextSession(small)
    if hasRecent || !valid || measured != firstOnly { t.Fatal("First must survive Recent budget rejection") }
}


// Map removal (e.g. Done) does not end the lifetime of a pendingRequest
// still owned by a Completion closure. Distinct identity counted once.
func TestQA005OwnedOverlayM1PendingIdentityLifetime(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    p := &pendingRequest{}
    s.mu.Lock()
    s.pending[41] = p
    qa005RegisterPendingLocked(s,p)
    s.mu.Unlock()
    server := &Server{sessions: map[*Session]struct{}{s: {}}}
    env := &benchmarkEnv{server:server}
    qa005ResetOwnedHighwaters(env)
    count, valid := qa005M1PendingCount(env)
    if !valid || count != 1 { t.Fatalf("admitted pending identity: %d valid=%v",count,valid) }
    // Synthetic Done-like map reset. Completion still owns p.
    s.mu.Lock()
    s.pending = make(map[uint32]*pendingRequest)
    s.mu.Unlock()
    count, valid = qa005M1PendingCount(env)
    if !valid || count != 1 { t.Fatalf("post-Done retained pending missing: %d valid=%v",count,valid) }
    // Completion return: releasePending uses the actual normal release hook.
    s.releasePending(41,p)
    count, valid = qa005M1PendingCount(env)
    if !valid || count != 0 { t.Fatalf("Completion release not accounted: %d valid=%v",count,valid) }
    s.mu.Lock()
    qa005ReleasePendingLocked(s,p) // injected duplicate must fail closed
    fault := s.qa005M1PendingFault
    s.mu.Unlock()
    if !fault { t.Fatal("duplicate pending release not detected") }
    if _,ok := qa005M1PendingCount(env); ok { t.Fatal("faulty pending identity accepted") }
    other := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    other.mu.Lock()
    other.pending[7] = &pendingRequest{} // synthetic missing admission registration
    other.mu.Unlock()
    env2 := &benchmarkEnv{server:&Server{sessions:map[*Session]struct{}{other:{}}}}
    qa005ResetOwnedHighwaters(env2)
    if _,ok := qa005M1PendingCount(env2); ok { t.Fatal("unregistered pending owner accepted") }
}


// Only the known static Go object payload is counted; no map or callback heap.
// Check arithmetic overflow fails closed instead of wrapping.
func TestQA005OwnedOverlayM1PendingStructFootprint(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pending := &pendingRequest{}
    s.mu.Lock()
    s.pending[7] = pending
    qa005RegisterPendingLocked(s, pending)
    s.mu.Unlock()
    env := &benchmarkEnv{server:&Server{sessions:map[*Session]struct{}{s:{}}}}
    qa005ResetOwnedHighwaters(env)
    count, valid := qa005M1PendingCount(env)
    if !valid || count != 1 { t.Fatalf("identity mismatch: %d valid=%v",count,valid) }
    bytes, valid := qa005M1PendingStructFootprint(count)
    expected := uint64(unsafe.Sizeof(pendingRequest{}))
    if !valid || bytes != expected || bytes == 0 {
        t.Fatalf("wrong logical Go struct footprint: %d want %d valid=%v",bytes,expected,valid)
    }
    if _, ok := qa005M1PendingStructFootprint(^uint64(0)); ok { t.Fatal("overflow accepted") }
    s.releasePending(7,pending)
    count, valid = qa005M1PendingCount(env)
    bytes, ok := qa005M1PendingStructFootprint(count)
    if !valid || !ok || bytes != 0 { t.Fatal("logical object bytes survived Completion release") }
}


// A queue retains the *capacity* of the callbackTask backing slice while
// head advances. Shared owner and duplicate Client entries are counted once.
// Queue struct survives even with zero queued tasks while callback is active.
// Cross-queue shared backing aliases are rejected (not summed twice).
func TestQA005OwnedOverlayM1WorkerQueueBackingLifetime(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool := newCallbackWorkerPool(callbackApplication, 0, time.Hour)
    tasks := make([]callbackTask, 4, 8)
    lane := &callbackSessionQueue{session:s, tasks:tasks, head:3, active:1}
    pool.sessions[s] = lane
    owner := &ownerCallbackDispatcher{application:pool}
    server := &Server{sessions:map[*Session]struct{}{s:{}}, callbacks:owner}
    client := &Client{callbacks:owner} // same pool, NOT a second allocation
    env := &benchmarkEnv{server:server, clients:[]*Client{client,client}}
    qa005ResetOwnedHighwaters(env)
    slotSize := uint64(unsafe.Sizeof(callbackTask{}))
    laneSize := uint64(unsafe.Sizeof(callbackSessionQueue{}))
    slots, structB, workers, lanes, valid := qa005M1WorkerQueueSample(env)
    if !valid || slots != 8*slotSize || structB != laneSize || lanes != 1 || workers != 0 {
        t.Fatalf("queue backing, owner alias or head count wrong: slots=%d laneBytes=%d lanes=%d workers=%d valid=%v",
            slots,structB,lanes,workers,valid)
    }
    // The actual library's callbackTask.pop clears q.tasks when all tasks
    // have been claimed, but the Session lane remains while a callback runs.
    pool.mu.Lock()
    lane.tasks = nil
    lane.head = 0
    pool.mu.Unlock()
    slots, structB, _, lanes, valid = qa005M1WorkerQueueSample(env)
    if !valid || slots != 0 || structB != laneSize || lanes != 1 {
        t.Fatalf("active worker lane should retain queue struct, not slots: slots=%d lane=%d count=%d valid=%v",slots,structB,lanes,valid)
    }
    pool.mu.Lock()
    delete(pool.sessions,s) // last callback finished: cleanupSessionQueueLocked
    pool.mu.Unlock()
    slots, structB, _, lanes, valid = qa005M1WorkerQueueSample(env)
    if !valid || slots != 0 || structB != 0 || lanes != 0 {
        t.Fatalf("removed lane still attributed: slots=%d struct=%d lanes=%d valid=%v",slots,structB,lanes,valid)
    }
    // Restore and inject conflicting ownership for exactly one backing array.
    pool.mu.Lock()
    lane.tasks = tasks
    lane.head = 1
    pool.sessions[s] = lane
    pool.mu.Unlock()
    completion := newCallbackWorkerPool(callbackCompletion, 0, time.Hour)
    alias := &callbackSessionQueue{session:s,tasks:tasks}
    completion.sessions[s] = alias
    owner.completion = completion
    if _,_,_,_,valid := qa005M1WorkerQueueSample(env); valid {
        t.Fatal("shared task backing across two owner queues must fail closed")
    }
    completion.mu.Lock()
    delete(completion.sessions,s)
    completion.mu.Unlock()
    slots, structB, _, lanes, valid = qa005M1WorkerQueueSample(env)
    if !valid || slots != 8*slotSize || structB != laneSize || lanes != 1 {
        t.Fatal("removing alias must restore unique ownership")
    }
    // A corrupt head is not safe to use for memory qualification.
    pool.mu.Lock()
    lane.head = len(lane.tasks)+1
    pool.mu.Unlock()
    if _,_,_,_,valid := qa005M1WorkerQueueSample(env); valid {
        t.Fatal("corrupt queue head accepted")
    }
}


// workerCount records logical worker object responsibility but NOT the
// goroutine stack, wake channel capacity or timer allocations.
func TestQA005OwnedOverlayM1WorkerStructFootprint(t *testing.T) {
    unit := uint64(unsafe.Sizeof(callbackWorker{}))
    if unit == 0 { t.Fatal("empty worker struct") }
    for _, count := range []uint64{0, 1, 2, 17} {
        got, ok := qa005M1WorkerStructFootprint(count)
        if !ok || got != count*unit {
            t.Fatalf("count=%d got=%d expected=%d ok=%v",count,got,count*unit,ok)
        }
    }
    if _, valid := qa005M1WorkerStructFootprint(^uint64(0)); valid {
        t.Fatal("worker static footprint overflow accepted")
    }
    // Verify dedup is applied to worker count BEFORE computing the footprint:
    // repeated Client/Server owner references are not extra worker objects.
    session := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool := newCallbackWorkerPool(callbackApplication, 0, time.Hour)
    pool.mu.Lock()
    pool.workerCount = 2 // synthetic worker accounting fixture; no goroutine
    pool.mu.Unlock()
    owner := &ownerCallbackDispatcher{application:pool}
    env := &benchmarkEnv{
        server:&Server{callbacks:owner,sessions:map[*Session]struct{}{session:{}}},
        clients:[]*Client{{callbacks:owner}},
    }
    qa005ResetOwnedHighwaters(env)
    _,_,workerCount,_,ok := qa005M1WorkerQueueSample(env)
    if !ok || workerCount != 2 { t.Fatalf("duplicate owner count=%d valid=%v",workerCount,ok) }
    measured,ok := qa005M1WorkerStructFootprint(workerCount)
    if !ok || measured != 2*unit { t.Fatal("logical worker bytes double counted") }
}


// Verify the actual worker_scheduler implementation, not only synthetic
// queue structs. A running callback holds the only worker; the next queued
// callback owns real task-slice storage. Both lane+backing disappear after
// callback completion, and the worker retires after its idle grace.
func TestQA005OwnedOverlayM1RealWorkerQueueLifecycle(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool := newCallbackWorkerPool(callbackApplication, 1, 25*time.Millisecond)
    owner := &ownerCallbackDispatcher{application:pool}
    env := &benchmarkEnv{server:&Server{
        sessions:map[*Session]struct{}{s:{}},callbacks:owner,
    }}
    qa005ResetOwnedHighwaters(env)
    started := make(chan struct{})
    release := make(chan struct{})
    done := make(chan struct{})
    defer func() {
        select { case <-release: default: close(release) }
    }()
    if !pool.enqueue(callbackTask{session:s,run:func(){close(started); <-release}}) {
        t.Fatal("worker initial enqueue rejected")
    }
    select {
    case <-started:
    case <-time.After(3*time.Second): t.Fatal("worker failed to start callback")
    }
    if !pool.enqueue(callbackTask{session:s,run:func(){close(done)}}) {
        t.Fatal("worker queued callback rejected")
    }
    slots, queueBytes, live, lanes, valid := qa005M1WorkerQueueSample(env)
    if !valid || slots < uint64(unsafe.Sizeof(callbackTask{})) ||
        queueBytes != uint64(unsafe.Sizeof(callbackSessionQueue{})) || live!=1 || lanes!=1 {
        t.Fatalf("blocked worker queue not retained: slots=%d queue=%d workers=%d lanes=%d valid=%v",
            slots,queueBytes,live,lanes,valid)
    }
    close(release)
    select {
    case <-done:
    case <-time.After(3*time.Second): t.Fatal("queued callback remained stranded")
    }
    deadline := time.Now().Add(3*time.Second)
    for {
        slots,queueBytes,_,lanes,valid = qa005M1WorkerQueueSample(env)
        if !valid { t.Fatal("worker queue snapshot invalid after completion") }
        if slots==0 && queueBytes==0 && lanes==0 { break }
        if time.Now().After(deadline) {
            t.Fatalf("lane/backing retained after completion slots=%d queue=%d lanes=%d",slots,queueBytes,lanes)
        }
        time.Sleep(time.Millisecond)
    }
    for {
        _,_,live,_,valid = qa005M1WorkerQueueSample(env)
        if !valid { t.Fatal("worker snapshot invalid while retiring") }
        if live==0 { break }
        if time.Now().After(deadline) {
            t.Fatalf("idle worker did not retire: count=%d",live)
        }
        time.Sleep(time.Millisecond)
    }
}


// Baseline freezes Client generation and current Session under Client.mu.
// An ephemeral attempt that disappears between observations is caught by
// the existing monotonically increased Client.generation. No new hot-path
// counter or change to the production connect lifecycle is necessary.
func TestQA005OwnedOverlayClientTransientGenerationChurn(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    client := &Client{generation:7, current:s}
    env := &benchmarkEnv{
        server:&Server{sessions:map[*Session]struct{}{}},
        clients:[]*Client{client,client},
    }
    qa005ResetOwnedHighwaters(env)
    if len(env.qa005OwnedRegistry) != 1 || len(env.qa005OwnedClientEpoch) != 1 ||
        !qa005OwnedRegistryComplete(env) { t.Fatal("frozen Client identity invalid") }
    s.mu.Lock()
    qa005AddOwnedLocked(s,&s.qa005OwnedOutgoingApp,19)
    s.mu.Unlock()
    sample,ok := qa005SampleOwnedBuffers(env)
    if !ok || sample != 19 { t.Fatalf("frozen client sample=%d valid=%v",sample,ok) }
    transient := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    client.mu.Lock()
    client.generation++
    client.current=transient
    client.current=s // temporary generation has disappeared before next tick
    client.mu.Unlock()
    if qa005OwnedRegistryComplete(env) { t.Fatal("ephemeral Client generation went unnoticed") }
    if _,ok := qa005SampleOwnedBuffers(env); ok { t.Fatal("client churn was sampled as valid") }
    if _,ok := qa005OwnedPeakUpper(env); ok { t.Fatal("client churn HWM was accepted") }
    // Existing window cannot be silently rebaselined.
    next := &benchmarkEnv{server:env.server,clients:[]*Client{client}}
    qa005ResetOwnedHighwaters(next)
    if !qa005OwnedRegistryComplete(next) { t.Fatal("fresh window should be complete") }
    s.mu.Lock()
    qa005SubtractOwnedLocked(s,&s.qa005OwnedOutgoingApp,19)
    s.mu.Unlock()
}

func TestQA005OwnedOverlayClientCurrentAndInFlightInvalidation(t *testing.T) {
    s := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    client := &Client{generation:3,current:s}
    server := &Server{sessions:map[*Session]struct{}{}}
    env := &benchmarkEnv{server:server,clients:[]*Client{client}}
    qa005ResetOwnedHighwaters(env)
    if !qa005OwnedRegistryComplete(env) { t.Fatal("baseline current identity lost") }
    client.mu.Lock()
    client.current = nil // Done cleared current, even without new generation
    client.mu.Unlock()
    if qa005OwnedRegistryComplete(env) { t.Fatal("Client current swap was accepted") }
    client.mu.Lock()
    client.current=s
    client.mu.Unlock()
    inFlight := make(chan struct{})
    client.mu.Lock()
    client.connectDone = inFlight
    client.mu.Unlock()
    if qa005OwnedRegistryComplete(env) { t.Fatal("connect in progress accepted") }
    unsafeFreeze := &benchmarkEnv{server:server,clients:[]*Client{client}}
    qa005ResetOwnedHighwaters(unsafeFreeze)
    client.mu.Lock()
    client.connectDone=nil
    client.mu.Unlock()
    if qa005OwnedRegistryComplete(unsafeFreeze) {
        t.Fatal("in-flight freeze incorrectly became valid after Connect ended")
    }
    clean := &benchmarkEnv{server:server,clients:[]*Client{client}}
    qa005ResetOwnedHighwaters(clean)
    if !qa005OwnedRegistryComplete(clean) { t.Fatal("fresh post-Connect window rejected") }
    client.mu.Lock()
    client.stopped=true
    client.mu.Unlock()
    if qa005OwnedRegistryComplete(clean) { t.Fatal("stopped Client accepted") }
}


// Integration proof for the immutable Client source. A real accepted Session
// closes and its Client manually reconnects to the real benchmark Server.
// The previous observation window must reject the new generation without
// relying on currently-live Session map membership or sampled timing.
func TestQA005OwnedOverlayClientRealReconnectInvalidatesWindow(t *testing.T) {
    env := newBenchmarkEnv(t, 1, 1, 1, true, false)
    qa005ResetOwnedHighwaters(env)
    if len(env.clients) != 1 || len(env.sessions) != 1 ||
        !qa005OwnedRegistryComplete(env) {
        t.Fatal("real bound Client cannot establish frozen window")
    }
    old := env.sessions[0]
    old.Close()
    select {
    case <-old.Done():
    case <-time.After(4*time.Second):
        t.Fatal("first Client generation did not finish")
    }
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    if err := env.clients[0].Connect(ctx); err != nil {
        t.Fatalf("real manual Client reconnection failed: %v", err)
    }
    replacement, bound := env.clients[0].CurrentSession()
    if !bound || replacement == old {
        t.Fatal("second Client generation not installed")
    }
    if qa005OwnedRegistryComplete(env) {
        t.Fatal("old frozen Client generation accepted after real reconnect")
    }
    if _,valid := qa005SampleOwnedBuffers(env); valid {
        t.Fatal("real reconnect yielded a qualified old Session sample")
    }
    if _,valid := qa005OwnedPeakUpper(env); valid {
        t.Fatal("real reconnect yielded an old Session HWM upper")
    }
}
    
// A retired Client generation can be absent from Client.current and the
// benchmark's initial Session list while an active callback still owns it.
// The observer must reject this window rather than report an incomplete zero.
func TestQA005OwnedOverlayRetiredClientCallbackSessionFailsClosed(t *testing.T) {
    retired := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool := newCallbackWorkerPool(callbackApplication, 1, time.Hour)
    pool.sessions[retired] = &callbackSessionQueue{session: retired, active: 1}
    client := &Client{
        generation: 11,
        callbacks: &ownerCallbackDispatcher{application: pool},
    }
    env := &benchmarkEnv{
        server: &Server{sessions: map[*Session]struct{}{}},
        clients: []*Client{client},
    }
    qa005ResetOwnedHighwaters(env)
    if env.qa005OwnedCallbackRegistryValid {
        t.Fatal("retired callback Session missing from frozen owner set was accepted")
    }
    if qa005OwnedRegistryComplete(env) {
        t.Fatal("retired callback Session yielded a complete registry")
    }
    if _, valid := qa005SampleOwnedBuffers(env); valid {
        t.Fatal("retired callback Session was silently omitted from memory sample")
    }
    if _, valid := qa005OwnedPeakUpper(env); valid {
        t.Fatal("retired callback Session was silently omitted from HWM upper")
    }
}

// A callback queue for a Session already present in the frozen owner set is
// allowed and must not duplicate that Session identity.
func TestQA005OwnedOverlayLateRetiredCallbackSessionInvalidatesWindow(t *testing.T) {
    known := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool := newCallbackWorkerPool(callbackApplication, 1, time.Hour)
    owner := &ownerCallbackDispatcher{application: pool}
    client := &Client{generation: 12, current: known, callbacks: owner}
    env := &benchmarkEnv{
        server: &Server{sessions: map[*Session]struct{}{known: {}}},
        clients: []*Client{client},
        sessions: []*Session{known},
    }
    qa005ResetOwnedHighwaters(env)
    if !qa005OwnedRegistryComplete(env) {
        t.Fatal("initial stable window was rejected")
    }
    retired := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool.mu.Lock()
    pool.sessions[retired] = &callbackSessionQueue{session: retired, active: 1}
    pool.mu.Unlock()
    if qa005OwnedRegistryComplete(env) {
        t.Fatal("late callback-owned retired Session was not detected")
    }
    if _, valid := qa005SampleOwnedBuffers(env); valid {
        t.Fatal("late callback-owned retired Session was sampled")
    }
    if _, valid := qa005OwnedPeakUpper(env); valid {
        t.Fatal("late callback-owned retired Session was included in HWM upper")
    }
}

func TestQA005OwnedOverlayKnownCallbackSessionIsDeduplicated(t *testing.T) {
    session := newSession(nil, defaultSessionConfig(), sessionIdentity{}, nil, sessionHandlers{})
    pool := newCallbackWorkerPool(callbackApplication, 1, time.Hour)
    pool.sessions[session] = &callbackSessionQueue{session: session, active: 1}
    owner := &ownerCallbackDispatcher{application: pool}
    client := &Client{generation: 11, current: session, callbacks: owner}
    env := &benchmarkEnv{
        server: &Server{sessions: map[*Session]struct{}{session: {}}},
        clients: []*Client{client},
        sessions: []*Session{session},
    }
    env.server.callbacks = owner // shared dispatcher must be deduplicated
    qa005ResetOwnedHighwaters(env)
    if !env.qa005OwnedCallbackRegistryValid || !qa005OwnedRegistryComplete(env) {
        t.Fatal("known active callback Session invalidated the owner registry")
    }
    if len(env.qa005OwnedRegistry) != 1 {
        t.Fatalf("Session identity count = %d, want one", len(env.qa005OwnedRegistry))
    }
}

// Sampling metrics are synthetic diagnostics: monotonic gaps and snapshot
// duration are checked, but no maximum-gap acceptance threshold is implied.
func TestQA005OwnedOverlaySamplingWindowEvidence(t *testing.T) {
    probe := &qa005ChargeProbe{}
    first := time.Unix(100, 0)
    if !qa005RecordSamplingWindow(probe, first, 10*time.Microsecond) {
        t.Fatal("first sample was rejected")
    }
    if !qa005RecordSamplingWindow(probe, first.Add(5*time.Millisecond), 20*time.Microsecond) {
        t.Fatal("second monotonic sample was rejected")
    }
    if probe.ownedMaxSampleGap != 5*time.Millisecond ||
        probe.ownedMaxSnapshotDuration != 20*time.Microsecond {
        t.Fatalf("sampling diagnostics gap=%s duration=%s",
            probe.ownedMaxSampleGap, probe.ownedMaxSnapshotDuration)
    }
    duplicate := &qa005ChargeProbe{}
    if !qa005RecordSamplingWindow(duplicate, first, time.Nanosecond) {
        t.Fatal("first sample rejected")
    }
    if qa005RecordSamplingWindow(duplicate, first, time.Nanosecond) || !duplicate.invalid {
        t.Fatal("non-monotonic sample timestamp was not rejected")
    }
    negative := &qa005ChargeProbe{}
    if qa005RecordSamplingWindow(negative, first, -time.Nanosecond) || !negative.invalid {
        t.Fatal("negative snapshot duration was not rejected")
    }
    zero := &qa005ChargeProbe{}
    if qa005RecordSamplingWindow(zero, time.Time{}, 0) || !zero.invalid {
        t.Fatal("zero timestamp was not rejected")
    }
}


"""


def patch_types(content):
    return replace_once(
        content,
        "\tsessions       map[*Session]struct{}\n",
        "\tqa005OwnedAdmissionEpoch uint64 // test overlay; Server.mu protects admission-churn evidence\n"
        "\tsessions       map[*Session]struct{}\n",
        "Server admission epoch")


def patch_server_lifecycle(content):
    return replace_once(
        content,
        "\t\ts.sessions[session] = struct{}{}\n\t\ts.preBind[session] = struct{}{}",
        "\t\ts.sessions[session] = struct{}{}\n"
        "\t\ts.qa005OwnedAdmissionEpoch++ // test overlay; Server.mu held\n"
        "\t\ts.preBind[session] = struct{}{}",
        "Server Session registration epoch")


def patch_benchmark(content):
    patched = charge.patch_benchmark(content)
    patched = replace_once(
        patched, '\t"sync/atomic"\n', '\t"sync/atomic"\n\t"unsafe"\n',
        "test-only static pendingRequest struct footprint")
    patched = replace_once(
        patched, "type benchmarkEnv struct {\n",
        "type benchmarkEnv struct {\n"
        "\tqa005OwnedClientEpoch map[*Client]uint64\n"
        "\tqa005OwnedClientIdentity map[*Client]*Session\n"
        "\tqa005OwnedClientRegistryValid bool\n"
        "\tqa005OwnedCallbackRegistryValid bool\n"
        "\tqa005OwnedBaselineAdmissionEpoch uint64\n"
        "\tqa005OwnedRegistry []*Session\n"
        "\tqa005OwnedIndex map[*Session]struct{}\n",
        "stable owned Session registry")
    patched = replace_once(
        patched, '    p := &qa005ChargeProbe{stop: make(chan struct{}), done: make(chan struct{})}',
        '    qa005ResetOwnedHighwaters(env)\n'
        '    p := &qa005ChargeProbe{stop: make(chan struct{}), done: make(chan struct{})}',
        "reset Session HWMs at traffic start")
    patched = replace_once(
        patched, "    samples uint64\n    invalid bool\n",
        "    samples uint64\n    invalid bool\n    ownedPeak uint64\n    ownedSamples uint64\n    ownedUpper uint64\n"
        "    d1StackPeak uint64\n    d1StackSamples uint64\n"
        "    m1PendingPeak uint64\n    m1PendingSamples uint64\n"
        "    m1PendingStructPeak uint64\n"
        "    m1WorkerSlotPeak uint64\n    m1WorkerLaneBytesPeak uint64\n"
        "    m1WorkerLaneCountPeak uint64\n    m1WorkerCountPeak uint64\n"
        "    m1WorkerQueueSamples uint64\n"
        "    m1WorkerStructPeak uint64\n"
        "    ownedLastSampleAt time.Time\n"
        "    ownedMaxSampleGap time.Duration\n"
        "    ownedMaxSnapshotDuration time.Duration\n",
        "sampler state")
    patched = replace_once(
        patched, "        p.samples++\n",
        "        p.samples++\n"
        "        sampleStartedAt := time.Now()\n"
        "        owned, valid := qa005SampleOwnedBuffers(env)\n"
        "        d1Text, d1OK := qa005D1StackTextSample(env)\n"
        "        pendingCount, pendingOK := qa005M1PendingCount(env)\n"
        "        pendingStructBytes, pendingStructOK := qa005M1PendingStructFootprint(pendingCount)\n"
        "        workerSlotB, workerLaneB, workers, lanes, workerOK := qa005M1WorkerQueueSample(env)\n"
        "        workerStructB, workerStructOK := qa005M1WorkerStructFootprint(workers)\n"
        "        snapshotDuration := time.Since(sampleStartedAt)\n"
        "        if !qa005RecordSamplingWindow(p, sampleStartedAt, snapshotDuration) { p.invalid = true; return }\n"
        "        if !valid || !d1OK || !pendingOK || !pendingStructOK || !workerOK || !workerStructOK { p.invalid = true; return }\n"
        "        if owned > p.ownedPeak { p.ownedPeak = owned }\n"
        "        p.ownedSamples++\n"
        "        if d1Text > p.d1StackPeak { p.d1StackPeak = d1Text }\n"
        "        p.d1StackSamples++\n"
        "        if pendingCount > p.m1PendingPeak { p.m1PendingPeak = pendingCount }\n"
        "        p.m1PendingSamples++\n"
        "        if pendingStructBytes > p.m1PendingStructPeak { p.m1PendingStructPeak = pendingStructBytes }\n"
        "        if workerSlotB > p.m1WorkerSlotPeak { p.m1WorkerSlotPeak = workerSlotB }\n"
        "        if workerLaneB > p.m1WorkerLaneBytesPeak { p.m1WorkerLaneBytesPeak = workerLaneB }\n"
        "        if lanes > p.m1WorkerLaneCountPeak { p.m1WorkerLaneCountPeak = lanes }\n"
        "        if workers > p.m1WorkerCountPeak { p.m1WorkerCountPeak = workers }\n"
        "        if workerStructB > p.m1WorkerStructPeak { p.m1WorkerStructPeak = workerStructB }\n"
        "        p.m1WorkerQueueSamples++\n",
        "sample observation")
    patched = replace_once(
        patched, "            case <-p.stop: observe(); return",
        "            case <-p.stop: observe(); upper, valid := qa005OwnedPeakUpper(env); if !valid { p.invalid = true }; p.ownedUpper = upper; return",
        "sample close peak upper")
    patched = replace_once(
        patched,
        '    b.ReportMetric(float64(p.samples), "probe-owner-charge-samples")\n',
        '    b.ReportMetric(float64(p.samples), "probe-owner-charge-samples")\n'
        '    b.ReportMetric(float64(p.ownedPeak), "probe-owned-buffer-peak-B")\n'
        '    b.ReportMetric(float64(p.ownedSamples), "probe-owned-buffer-samples")\n'
        '    b.ReportMetric(float64(p.d1StackPeak), "probe-d1-unique-stack-text-peak-B")\n'
        '    b.ReportMetric(float64(p.d1StackSamples), "probe-d1-stack-text-samples")\n'
        '    b.ReportMetric(float64(p.m1PendingPeak), "probe-m1-pending-object-peak-count")\n'
        '    b.ReportMetric(float64(p.m1PendingStructPeak), "probe-m1-pending-struct-logical-peak-B")\n'
        '    b.ReportMetric(float64(p.m1PendingSamples), "probe-m1-pending-samples")\n'
        '    b.ReportMetric(float64(p.m1WorkerSlotPeak), "probe-m1-worker-task-slots-logical-peak-B")\n'
        '    b.ReportMetric(float64(p.m1WorkerLaneBytesPeak), "probe-m1-worker-queue-struct-logical-peak-B")\n'
        '    b.ReportMetric(float64(p.m1WorkerLaneCountPeak), "probe-m1-worker-queue-peak-count")\n'
        '    b.ReportMetric(float64(p.m1WorkerCountPeak), "probe-m1-worker-live-peak-count")\n'
        '    b.ReportMetric(float64(p.m1WorkerStructPeak), "probe-m1-worker-struct-logical-peak-B")\n'
        '    b.ReportMetric(float64(p.m1WorkerQueueSamples), "probe-m1-worker-queue-samples")\n'
        '    b.ReportMetric(float64(p.ownedUpper), "probe-owned-session-hwm-upper-B")\n'
        '    b.ReportMetric(float64(p.ownedMaxSampleGap.Nanoseconds()), "probe-owned-max-sample-gap-ns")\n'
        '    b.ReportMetric(float64(p.ownedMaxSnapshotDuration.Nanoseconds()), "probe-owned-max-snapshot-ns")\n',
        "owned reporting")
    return patched.rstrip() + "\n" + BENCHMARK_HELPERS


PATCHES = {
    "benchmark_test.go": patch_benchmark,
    "session_internal.go": patch_internal,
    "session.go": patch_session,
    "session_transport.go": patch_transport,
    "session_control.go": patch_control,
    "resource_charges.go": patch_charges,
    "types.go": patch_types,
    "server_lifecycle.go": patch_server_lifecycle,
}


def prepare(source, output):
    source = source.resolve(strict=True)
    output = output.resolve()
    if source == output or source in output.parents:
        raise ValueError("overlay output must be outside source checkout")
    original = {name: (source / name).read_bytes() for name in
                (*FIXTURES, "session.go", "session_internal.go", "session_transport.go", "session_control.go", "resource_charges.go", "types.go", "server_lifecycle.go", "worker_scheduler.go", "client_connect.go", "client_lifecycle.go")}
    edited = {name: PATCHES[name](original[name].decode("utf-8")).encode("utf-8")
              for name in SOURCE_FILES}
    output.mkdir(parents=True, exist_ok=False)
    paths = {}
    for name, contents in edited.items():
        target = output / name
        target.write_bytes(contents)
        paths[str(source / name)] = str(target)
    (output / "overlay.json").write_text(json.dumps({"Replace": paths}, sort_keys=True) + "\n")
    source_fixture = charge.digest([original[name] for name in FIXTURES])
    effective_fixture = charge.digest([edited.get(name, original[name]) for name in FIXTURES])
    original_sha = {name: hashlib.sha256(original[name]).hexdigest() for name in original}
    effective_sha = {name: hashlib.sha256(edited.get(name, original[name])).hexdigest() for name in original}
    metadata = {
        "adapter_id": ADAPTER_ID,
        "source_fixture_sha256": source_fixture,
        "effective_fixture_sha256": effective_fixture,
        "source_file_sha256": original_sha,
        "effective_file_sha256": effective_sha,
        "measurement_qualifies_retained_attributed_memory": False,
        "covered_categories": [],
        "observed_partial_categories": ["F1-outbound-app", "F2-inbound-request-body",
                                        "F3-inbound-response-body", "F4-outbound-control",
                                        "F5-unreserved-inbound-body",
                                        "D1-owned-panic-stack-text-only",
                                        "M1-pending-object-identity-only",
                                        "M1-worker-queue-struct-and-task-slice-logical-only"],
        "coverage_status": "PARTIAL_INCONCLUSIVE",
        "coverage_exclusions_detail": {
            "F1": "pre-Queue build observed; allocator overhead/foreign refs excluded",
            "F2": "reserved inbound Request bodies only; unclassified reads excluded",
            "F3": "matched Completion bodies only; ignored and drained frames excluded",
            "F4": "pre-Queue for in-lock Unbind/Enquire; other Control encoding may precede Session registration",
            "F5": "unreserved, nondrained inbound Body backing allocation through read and handler; excludes wire scratch/decoded objects",
            "M1": "pendingRequest/worker queue logical structs, task slice-capacity slots and Worker static objects; Client generation/current frozen fail-closed for transient reconnect attempts. Map buckets, channel/timer/closures, allocator classes and whole M1 excluded",
            "D1": "only neta-created Stack text length observed with per-record Sequence alias dedup; other rendered strings, PanicRecord metadata, raw foreign graphs and runtime overhead excluded",
        },
        "excluded_categories": ["metadata", "callbacks", "panic-raw-graphs",
                                "goroutine-stacks", "runtime-allocator-overhead",
                                "application-references", "unclassified-heap-objects"],
        "primary_metric": "probe-owned-buffer-peak-B",
        "sampler_interval_ms": 5,
        "sampler_max_gap_policy": "NOT_APPROVED_DIAGNOSTIC_ONLY",
        "snapshot_duration_metric": "probe-owned-max-snapshot-ns",
        "source_tree_mutated": False,
        "tracks_pre_enqueue_allocated_F1": True,
        "tracks_prequeue_registered_F4_unbind_enquire": True,
        "invalidates_transient_server_admission_churn": True,
        "tracks_unreserved_inbound_body_lifetime": True,
        "reconciles_all_observed_categories_to_session_total": True,
        "observes_d1_unique_stack_text_only": True,
        "observes_m1_pending_object_identity_count_not_bytes": True,
        "m1_pending_struct_logical_footprint_is_not_allocator_bytes": True,
        "m1_worker_queue_observation_dedups_pools_lanes_and_backing": True,
        "m1_worker_queue_sizes_are_logical_not_allocator_bytes": True,
        "m1_worker_struct_footprint_excludes_stacks_channels_allocator": True,
        "worker_scheduler_source_sha_is_compatibility_dependency": True,
        "client_generation_and_current_frozen_fail_closed": True,
        "client_connection_sources_pinned_for_epoch_semantics": True,
        "client_retired_callback_sessions_fail_closed": True,
        "observer_does_not_retain_unregistered_retired_sessions": True,
        "observer_gc_liveness_bias": "NOT_MEASURED",
        "sampling_window_monotonicity_and_snapshot_duration_tested": True,
        "qualification": "DIAGNOSTIC_ONLY",
    }
    (output / "manifest.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    a = parser.parse_args()
    print(json.dumps(prepare(a.source, a.output), sort_keys=True))


if __name__ == "__main__":
    main()
