import AppKit

/// Dismisses the popover SwiftUI presents for `MenuBarExtra(.window)`.
///
/// SwiftUI gives a view inside that popover no way to close it: there's no
/// `isPresented` binding on `MenuBarExtra`, and the `dismiss` environment action
/// doesn't reach the panel, since the popover is its own scene (FB11984872).
///
/// So we do what the user would: click the status item. That lets SwiftUI close
/// the panel through its own path and reset its presentation state, instead of
/// leaving the menu-bar icon stuck highlighted.
///
/// Both window classes involved are private AppKit/SwiftUI types matched by
/// name, so every step degrades to doing nothing rather than crashing if those
/// internals change.
@MainActor
enum MenuBarExtraPanel {
    /// SwiftUI hosts the popover in a private `NSWindow` subclass.
    static func isPanelWindow(className: String) -> Bool {
        className.contains("MenuBarExtraWindow")
    }

    /// The status bar hosts its items in a different private subclass — one per
    /// screen when "Displays have Separate Spaces" is on.
    static func isStatusBarWindow(className: String) -> Bool {
        className.contains("NSStatusBarWindow")
    }

    /// Close the popover if it's open. No-op when it isn't.
    static func dismiss() {
        for window in NSApp.windows where isStatusBarWindow(className: window.className) {
            // `statusItem` is a private property. Ask before reading it: a bare
            // value(forKey:) raises an uncatchable ObjC exception if it's gone.
            guard window.responds(to: NSSelectorFromString("statusItem")),
                  let item = window.value(forKey: "statusItem") as? NSStatusItem,
                  let button = item.button,
                  button.state != .off  // clicking a closed popover would open it
            else { continue }

            button.performClick(button)
            button.isHighlighted = button.state != .off
            return
        }

        // If that shape ever changes, close the panel directly. The icon stays
        // highlighted until the next click, which beats a popover that won't go.
        NSApp.windows.first { isPanelWindow(className: $0.className) }?.close()
    }
}
