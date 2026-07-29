import Foundation

/// Tracks the one system write auto mode is allowed to have outstanding.
///
/// Auto mode writes from places that can fire while an earlier write is still
/// resolving: the poll tick, and adopting a state observed from outside. On the
/// privileged-helper path `setEnabled` only *dispatches* the write — the reply,
/// the read-back, and any mismatch all land later, in a separate turn. A claim
/// scoped to the call that issued the write is therefore worthless: it is
/// already released by the time the reply arrives, so a write that reads back
/// wrong immediately asks for another, recursing through the mismatch path and
/// queueing XPC retries that supersede each other's callbacks.
///
/// So the claim spans the whole write — `issued` until `resolved` — and a
/// resolution does *not* reopen writing in the same turn. Only `clear()` does,
/// and every poll tick calls it, as does every reconcile the user just drove.
/// Two properties fall out, and both are what make this safe to hold across an
/// async boundary:
///
/// - A retry is never more than one tick away, so a resolution that defers is
///   never a resolution that gives up.
/// - A claim that never resolves cannot wedge the feature. A superseded helper
///   reply is simply dropped — it never resolves anything — and the next tick
///   clears the claim regardless.
public struct AutoWriteCoordinator: Equatable {
    public enum State: Equatable {
        /// Nothing outstanding — auto mode may write.
        case idle
        /// A write was dispatched and hasn't resolved yet. On the helper path
        /// this spans the XPC round trip and the read-back that follows it.
        case inFlight(target: Bool)
        /// A write resolved this turn, whatever its outcome. Another attempt
        /// waits for the next tick rather than chasing the result immediately.
        case deferred
    }

    public private(set) var state: State

    public init(state: State = .idle) {
        self.state = state
    }

    /// Whether auto mode may dispatch a write right now.
    public var mayWrite: Bool { state == .idle }

    /// The target of the write currently outstanding, if there is one.
    public var inFlightTarget: Bool? {
        guard case .inFlight(let target) = state else { return nil }
        return target
    }

    /// Auto mode dispatched a write.
    public mutating func issued(target: Bool) {
        state = .inFlight(target: target)
    }

    /// The outstanding write reached a conclusion — confirmed, contradicted by
    /// the read-back, unverifiable, or failed outright. All of them defer the
    /// next attempt to the following tick; the distinction between them is the
    /// caller's business, not this type's.
    ///
    /// Ignored unless a write is actually outstanding, so a late reply that lost
    /// its claim to `clear()` can't retroactively defer a fresh one.
    public mutating func resolved() {
        guard case .inFlight = state else { return }
        state = .deferred
    }

    /// Drop any claim and allow a write immediately. Called at the top of every
    /// poll tick, by the reconcile paths the user just drove (where waiting a
    /// tick would read as broken), and when a write from another origin takes
    /// over — that write owns the flag now, and auto mode's pending reply, if one
    /// is still in flight, will be rejected as superseded.
    public mutating func clear() {
        state = .idle
    }
}
