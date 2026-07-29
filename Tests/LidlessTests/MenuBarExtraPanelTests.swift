import AppKit
import XCTest

/// The dismissal path matches two private AppKit/SwiftUI window classes by name.
/// These tests pin the names down so a rename shows up here rather than as a
/// popover that silently stops closing.
@MainActor
final class MenuBarExtraPanelTests: XCTestCase {

    func testRecognisesTheSwiftUIPopoverWindow() {
        XCTAssertTrue(MenuBarExtraPanel.isPanelWindow(className: "SwiftUI.MenuBarExtraWindow"))
        XCTAssertFalse(MenuBarExtraPanel.isPanelWindow(className: "NSWindow"))
        XCTAssertFalse(MenuBarExtraPanel.isPanelWindow(className: "NSStatusBarWindow"))
    }

    func testRecognisesTheStatusBarWindow() {
        XCTAssertTrue(MenuBarExtraPanel.isStatusBarWindow(className: "NSStatusBarWindow"))
        XCTAssertFalse(MenuBarExtraPanel.isStatusBarWindow(className: "NSWindow"))
        XCTAssertFalse(MenuBarExtraPanel.isStatusBarWindow(className: "SwiftUI.MenuBarExtraWindow"))
    }

    /// There's no menu bar extra in the test runner, so this exercises the path
    /// where nothing matches — it must fall through quietly, not trap. The same
    /// path runs in the app if these private classes are ever renamed.
    func testDismissIsHarmlessWithNoMenuBarExtraPresent() {
        let unrelated = NSWindow(contentRect: .zero, styleMask: [.titled], backing: .buffered, defer: true)
        unrelated.orderFront(nil)
        defer { unrelated.close() }

        MenuBarExtraPanel.dismiss()

        XCTAssertTrue(unrelated.isVisible, "dismiss() must not touch unrelated windows")
    }
}
