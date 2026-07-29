import XCTest

/// The claim auto mode holds on its outstanding system write.
///
/// These pin the four sequences that matter, each written as the turn-by-turn
/// order the app actually runs them in. The helper path is the reason this type
/// exists: `setEnabled` only dispatches there, so every step after "issued" can
/// land in a later turn, and a claim released when the dispatching call returned
/// would be no claim at all.
final class AutoWriteCoordinatorTests: XCTestCase {

    // MARK: A write in flight blocks a second one

    /// The poll refreshes state and adopts what it observes while the helper is
    /// still round-tripping. Adopting reconciles — and must not dispatch again.
    func testInFlightWriteBlocksASecondWrite() {
        var c = AutoWriteCoordinator()
        XCTAssertTrue(c.mayWrite)

        c.issued(target: true)                  // dispatched to the helper
        XCTAssertFalse(c.mayWrite, "a refresh/adopt mid-flight must not dispatch again")
        XCTAssertEqual(c.inFlightTarget, true)
    }

    /// The claim survives arbitrarily many observations, because on the helper
    /// path there is no bound on how long the reply takes.
    func testClaimSurvivesRepeatedObservationsWithinTheTurn() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)
        for _ in 0..<5 {
            XCTAssertFalse(c.mayWrite)
        }
        XCTAssertEqual(c.state, .inFlight(target: true))
    }

    // MARK: A mismatch does not retry in the same turn

    /// Read-back contradicts the write → resolve, adopt, reconcile. That
    /// reconcile must find the door shut, or the mismatch can recur with nothing
    /// bounding it but the stack.
    func testMismatchDoesNotRetryInTheSameTurn() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)

        c.resolved()                            // applyVerification, before adopting
        XCTAssertEqual(c.state, .deferred)
        XCTAssertFalse(c.mayWrite, "adopt→reconcile must not dispatch a fresh write")
    }

    /// Resolving repeatedly — a verification and a later poll both concluding —
    /// still can't reopen writing.
    func testRepeatedResolutionCannotReopenWriting() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)
        c.resolved()
        c.resolved()
        XCTAssertEqual(c.state, .deferred)
        XCTAssertFalse(c.mayWrite)
    }

    /// A late reply that lost its claim to `clear()` must not retroactively
    /// defer the tick that replaced it.
    func testResolutionWithoutAClaimIsIgnored() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)
        c.clear()                               // next tick took over
        c.resolved()                            // superseded reply, arriving late
        XCTAssertTrue(c.mayWrite, "a stale reply must not close a fresh tick's door")
    }

    // MARK: Failure and unverified retry on the next tick

    /// `.unverified` keeps the pending verification but ends the write; the retry
    /// belongs to the next tick, not to this turn.
    func testUnverifiedWriteRetriesOnTheNextTick() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)
        c.resolved()
        XCTAssertFalse(c.mayWrite)

        c.clear()                               // tick
        XCTAssertTrue(c.mayWrite, "a deferred write must get another attempt")
    }

    /// The helper reported failure: `recoverStateAfterFailedWrite` resolves, then
    /// re-reads — and that read's adopt must not immediately re-attempt.
    func testFailedWriteDefersUntilTheNextTick() {
        var c = AutoWriteCoordinator()
        c.issued(target: false)

        c.resolved()                            // before the recovery re-read
        XCTAssertFalse(c.mayWrite, "the recovery read's adopt must not re-attempt")

        c.clear()
        XCTAssertTrue(c.mayWrite)
    }

    /// The recovery guarantee: whatever state the claim is in, a tick reopens it.
    /// This is what makes the claim safe to hold across an async boundary — no
    /// outcome, and no missing outcome, can wedge the feature.
    func testEveryStateIsClearedByATick() {
        for state in [AutoWriteCoordinator.State.idle,
                      .inFlight(target: true),
                      .inFlight(target: false),
                      .deferred] {
            var c = AutoWriteCoordinator(state: state)
            c.clear()
            XCTAssertTrue(c.mayWrite, "a tick must reopen writing from \(state)")
        }
    }

    // MARK: A user write supersedes an auto write

    /// The user flips the toggle while auto mode's write is in flight. That write
    /// loses the flag, and its reply will be rejected as superseded — so the claim
    /// must go, or auto mode waits a tick on a reply that never resolves anything.
    func testUserWriteSupersedesAnInFlightAutoWrite() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)

        c.clear()                               // setEnabled with a non-auto origin
        XCTAssertTrue(c.mayWrite)
        XCTAssertNil(c.inFlightTarget)
    }

    /// And the superseded auto reply, arriving afterwards, changes nothing.
    func testSupersededAutoReplyDoesNotDisturbTheUserWrite() {
        var c = AutoWriteCoordinator()
        c.issued(target: true)
        c.clear()                               // user write took over

        c.resolved()                            // the old auto reply, finally landing
        XCTAssertTrue(c.mayWrite)
        XCTAssertEqual(c.state, .idle)
    }
}
