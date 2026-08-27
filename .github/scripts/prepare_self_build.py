#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()

def rw(rel, old, new):
    p = root / rel
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing patch anchor in {rel}: {old[:80]!r}')
    p.write_text(s.replace(old, new, 1), encoding='utf-8')

# ---------- resources / build identity ----------
(root/'Sources/Shared/L10n.swift').write_text('''import Foundation

enum L10n {
    static func tr(_ key: String, _ args: CVarArg...) -> String {
        let format = Bundle.main.localizedString(forKey: key, value: key, table: nil)
        return args.isEmpty ? format : String(format: format, locale: Locale.current, arguments: args)
    }
}
''', encoding='utf-8')

strings = r'''"Keep your Mac awake when the lid is closed." = "合上盖子后仍让 Mac 保持运行。";
"Keep awake with lid closed" = "合盖保持唤醒";
"Keep awake for" = "保持唤醒时长";
"Turning off in %@" = "%@ 后自动关闭";
"Not used while “Automatically enable when charging” is on." = "开启“充电时自动启用”后不使用定时关闭。";
"Helper active" = "辅助程序已启用";
"Helper inactive" = "辅助程序未启用";
"Background helper active" = "后台辅助程序已启用";
"Background helper inactive" = "后台辅助程序未启用";
"Battery %d%%" = "电池 %d%%";
"Battery %d percent" = "电池电量 %d%%";
"Battery %d percent, on power" = "电池电量 %d%%，已接电源";
"Safety" = "安全";
"Only while charging" = "仅充电时启用";
"Pause when running hot" = "温度过高时暂停";
"Low-battery cutoff" = "低电量阈值";
"Never" = "从不";
"Automatic mode is on, but keep-awake isn’t active right now." = "自动模式已开启，但当前未启用保持唤醒。";
"Temporarily disabled because the following check(s) failed:" = "由于以下条件未满足，当前已暂时停用：";
"Automatic" = "自动";
"Automatically enable when charging" = "充电时自动启用";
"Quit Lidless" = "退出 Lidless";
"Settings…" = "设置…";
"No limit" = "不限时";
"%d min" = "%d 分钟";
"1 hour" = "1 小时";
"%d hours" = "%d 小时";
"General" = "常规";
"Launch at login" = "登录时启动";
"Show Setup Guide…" = "显示设置向导…";
"Status" = "状态";
"Active" = "已启用";
"Using admin prompt" = "一次性管理员授权";
"Install the background helper once so toggling never asks for your password and the watchdog can protect against a stuck-awake Mac." = "此自用构建不使用上游签名的后台辅助程序。第一次开启合盖保持唤醒时会要求管理员授权一次，之后即可免密切换；独立看门狗会在应用异常退出后恢复正常睡眠。";
"Install background helper…" = "自用构建无需安装上游辅助程序";
"Open Login Items to approve…" = "自用构建无需批准上游辅助程序";
"Background helper" = "自用构建授权";
"Updates" = "更新";
"Automatic updates are disabled in this self-build." = "此自用构建已关闭上游自动更新。";
"About" = "关于";
"Version %@" = "版本 %@";
"Created by Nghia Luong" = "作者：Nghia Luong";
"View on GitHub" = "在 GitHub 上查看";
"Lidless Settings" = "Lidless 设置";
"Auto-paused: the Mac is running hot." = "已自动暂停：Mac 温度过高。";
"Auto-paused: not on charger." = "已自动暂停：未连接电源。";
"Auto-paused: battery %d%% on battery power." = "已自动暂停：当前使用电池供电，电量为 %d%%。";
"Auto-paused: not connected to power." = "已自动暂停：未连接电源。";
"Your Mac is running hot, so keep-awake is paused. It'll be available again once the Mac cools down." = "Mac 当前温度较高，保持唤醒已暂停。温度下降后即可再次启用。";
"“Only while charging” is on, so connect your Mac to power to keep it awake." = "已开启“仅充电时启用”，请连接电源后再启用保持唤醒。";
"Battery is at %d%%. Charge above the low-battery cutoff to keep your Mac awake." = "当前电量为 %d%%。请将电量充至低电量阈值以上后再启用保持唤醒。";
"Connect your Mac to power to keep it awake." = "请连接电源后再启用保持唤醒。";
"Running hot" = "温度过高";
"Not on charger" = "未连接充电器";
"Battery %d%% is at or below the cutoff" = "电量 %d%%，已达到或低于阈值";
"Not connected to power" = "未连接电源";
"The upstream background helper is disabled in this self-build." = "此自用构建已禁用上游签名后台辅助程序。";
"The sleep setting could not be changed after authorization." = "管理员授权完成后仍无法修改睡眠设置。";
"Unknown error" = "未知错误";
"Authorization cancelled." = "已取消管理员授权。";
'''
loc = root/'Resources/zh-Hans.lproj'
loc.mkdir(parents=True, exist_ok=True)
(loc/'Localizable.strings').write_text(strings, encoding='utf-8')

p = root/'project.yml'
s = p.read_text(encoding='utf-8')
s = s.replace('      - Resources/Assets.xcassets\n', '      - Resources/Assets.xcassets\n      - Resources/zh-Hans.lproj\n', 1)
s = s.replace('SUFeedURL: https://raw.githubusercontent.com/nghialuong/Lidless/main/docs/appcast.xml', 'SUFeedURL: https://raw.githubusercontent.com/Just-EP/Lidless/main/docs/appcast-self.xml')
s = s.replace('SUEnableAutomaticChecks: true', 'SUEnableAutomaticChecks: false')
s = s.replace('PRODUCT_BUNDLE_IDENTIFIER: com.nghialuong.lidless\n', 'PRODUCT_BUNDLE_IDENTIFIER: com.justep.lidless.self\n', 1)
s = s.replace('      - target: LidlessHelper\n        copy:\n          destination: executables\n', '', 1)
a = s.find('    postBuildScripts:\n'); b = s.find('\n  LidlessHelper:\n')
if a >= 0 and b > a: s = s[:a] + s[b:]
s = s.replace('        LidlessHelper: all\n', '', 1)
p.write_text(s, encoding='utf-8')

# ---------- no upstream privileged helper in ad-hoc build ----------
(root/'Sources/Lidless/HelperManager.swift').write_text(r'''import Foundation

final class HelperManager {
    var isEnabled: Bool { false }
    var requiresApproval: Bool { false }
    func register() throws { throw NSError(domain: "Lidless.SelfBuild", code: 1, userInfo: [NSLocalizedDescriptionKey: L10n.tr("The upstream background helper is disabled in this self-build.")]) }
    func unregister() throws {}
    func reregister(completion: @escaping (Error?) -> Void) { completion(NSError(domain: "Lidless.SelfBuild", code: 1, userInfo: [NSLocalizedDescriptionKey: L10n.tr("The upstream background helper is disabled in this self-build.")])) }
    func openLoginItemsSettings() {}
    func setKeepAwake(_ enabled: Bool, completion: @escaping (Bool, String?) -> Void) { completion(false, L10n.tr("The upstream background helper is disabled in this self-build.")) }
    func heartbeat() {}
    func checkReachable(completion: @escaping (Bool) -> Void) { completion(false) }
}
''', encoding='utf-8')

# ---------- first-use sudoers + exact pmset permission ----------
(root/'Sources/Lidless/PowerManager.swift').write_text(r'''import Foundation

struct PowerManager {
    private static let sudoersPath = "/etc/sudoers.d/lidless-self"

    func isSleepDisabled() -> Bool? {
        guard let out = Shell.capture("/usr/bin/pmset", ["-g"]) else { return nil }
        return PowerParsers.sleepDisabled(pmsetG: out)
    }

    func setSleepDisabled(_ enabled: Bool) throws {
        let value = enabled ? "1" : "0"
        if runPmset(value) { return }
        try installRule()
        guard runPmset(value) else {
            throw NSError(domain: "Lidless.PowerManager", code: 1, userInfo: [NSLocalizedDescriptionKey: L10n.tr("The sleep setting could not be changed after authorization.")])
        }
    }

    private func runPmset(_ value: String) -> Bool {
        let p = Process(); p.executableURL = URL(fileURLWithPath: "/usr/bin/sudo")
        p.arguments = ["-n", "/usr/bin/pmset", "-a", "disablesleep", value]
        p.standardOutput = Pipe(); p.standardError = Pipe()
        do { try p.run(); p.waitUntilExit(); return p.terminationStatus == 0 } catch { return false }
    }

    private func installRule() throws {
        let u = NSUserName().replacingOccurrences(of: "'", with: "'\\''")
        let rule = "\(u) ALL=(root) NOPASSWD: /usr/bin/pmset -a disablesleep 1, /usr/bin/pmset -a disablesleep 0"
        let qr = rule.replacingOccurrences(of: "'", with: "'\\''")
        let cmd = "set -e; tmp=$(/usr/bin/mktemp /private/var/tmp/lidless-self.XXXXXX); trap '/bin/rm -f \"$tmp\"' EXIT; /usr/bin/printf '%s\\n' '\(qr)' > \"$tmp\"; /usr/sbin/visudo -cf \"$tmp\" >/dev/null; /usr/bin/install -o root -g wheel -m 0440 \"$tmp\" \(Self.sudoersPath)"
        let e = cmd.replacingOccurrences(of: "\\", with: "\\\\").replacingOccurrences(of: "\"", with: "\\\"")
        let p = Process(); p.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
        p.arguments = ["-e", "do shell script \"\(e)\" with administrator privileges"]
        let err = Pipe(); p.standardError = err; p.standardOutput = Pipe()
        try p.run(); p.waitUntilExit()
        guard p.terminationStatus == 0 else {
            let d = err.fileHandleForReading.readDataToEndOfFile()
            let m = String(data: d, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? L10n.tr("Unknown error")
            throw NSError(domain: "Lidless.PowerManager", code: Int(p.terminationStatus), userInfo: [NSLocalizedDescriptionKey: m.isEmpty ? L10n.tr("Authorization cancelled.") : m])
        }
    }
}
''', encoding='utf-8')

(root/'Sources/Lidless/LocalWatchdog.swift').write_text(r'''import Foundation

final class LocalWatchdog {
    private var process: Process?
    func start(parentPID: Int32) {
        if process?.isRunning == true { return }
        stop()
        let p = Process(); p.executableURL = URL(fileURLWithPath: "/bin/sh")
        p.arguments = ["-c", "while /bin/kill -0 \(parentPID) >/dev/null 2>&1; do /bin/sleep 5; done; /usr/bin/sudo -n /usr/bin/pmset -a disablesleep 0 >/dev/null 2>&1 || true"]
        p.standardOutput = Pipe(); p.standardError = Pipe()
        do { try p.run(); process = p } catch { process = nil }
    }
    func stop() { if let p = process, p.isRunning { p.terminate() }; process = nil }
    deinit { stop() }
}
''', encoding='utf-8')

# ---------- app state / watchdog ----------
rw('Sources/Lidless/AppState.swift', '    private let loginItem = LoginItemManager()\n', '    private let loginItem = LoginItemManager()\n    private let localWatchdog = LocalWatchdog()\n')
rw('Sources/Lidless/AppState.swift', '''        } else if !onboardingComplete {\n            onboardingComplete = true\n            store.saveOnboardingComplete(true)\n            DispatchQueue.main.async { [weak self] in self?.showOnboarding() }\n        }\n''', '''        } else if !onboardingComplete {\n            onboardingComplete = true\n            store.saveOnboardingComplete(true)\n        }\n''')
rw('Sources/Lidless/AppState.swift', '''    private func manageHeartbeat() {\n        heartbeatTimer?.invalidate()\n        heartbeatTimer = nil\n        guard isEnabled, helperInstalled else { return }\n        helper.heartbeat()\n        heartbeatTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in\n            Task { @MainActor in self?.helper.heartbeat() }\n        }\n    }\n''', '''    private func manageHeartbeat() {\n        heartbeatTimer?.invalidate()\n        heartbeatTimer = nil\n        guard isEnabled else { localWatchdog.stop(); return }\n        if helperInstalled {\n            localWatchdog.stop(); helper.heartbeat()\n            heartbeatTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in\n                Task { @MainActor in self?.helper.heartbeat() }\n            }\n        } else {\n            localWatchdog.start(parentPID: ProcessInfo.processInfo.processIdentifier)\n        }\n    }\n''')
rw('Sources/Lidless/AppState.swift', '''                try power.setSleepDisabled(target)\n                isEnabled = target\n                lastError = resultMessage\n                updateAutoOff(for: target)\n''', '''                try power.setSleepDisabled(target)\n                isEnabled = target\n                lastError = resultMessage\n                manageHeartbeat()\n                updateAutoOff(for: target)\n''')

# ---------- dynamic localization ----------
rw('Sources/Lidless/MenuContent.swift', '            Text(title)\n', '            Text(L10n.tr(title))\n')
rw('Sources/Lidless/MenuContent.swift', '                Text(state.usingHelper ? "Helper active" : "Helper inactive")\n', '                Text(L10n.tr(state.usingHelper ? "Helper active" : "Helper inactive"))\n')
rw('Sources/Lidless/MenuContent.swift', '                Text("Battery \\(state.batteryPercent)%")\n', '                Text(L10n.tr("Battery %d%%", state.batteryPercent))\n')
rw('Sources/Lidless/MenuContent.swift', '                Text(shown == 0 ? "Never" : "\\(shown)%")\n', '                Text(shown == 0 ? L10n.tr("Never") : "\\(shown)%")\n')

rw('Sources/Lidless/SettingsView.swift', '                        Text(state.usingHelper ? "Active" : "Using admin prompt")\n', '                        Text(L10n.tr(state.usingHelper ? "Active" : "Using admin prompt"))\n')
rw('Sources/Lidless/SettingsView.swift', '''                    Button(state.helperNeedsApproval ? "Open Login Items to approve…" : "Install background helper…") {\n                        state.installHelper()\n                    }\n''', '''                    Button(L10n.tr("Install background helper…")) {}\n                        .disabled(true)\n''')
rw('Sources/Lidless/SettingsView.swift', '                        Text("Version \\(state.appVersion)")\n', '                        Text(L10n.tr("Version %@", state.appVersion))\n')
rw('Sources/Lidless/SettingsView.swift', '''            Section("Updates") {\n                Toggle("Check for updates automatically", isOn: $updater.automaticallyChecksForUpdates)\n                Button("Check for Updates…") { updater.checkForUpdates() }\n                    .disabled(!updater.canCheckForUpdates)\n            }\n''', '''            Section("Updates") {\n                Text("Automatic updates are disabled in this self-build.")\n                    .foregroundStyle(.secondary)\n            }\n''')
rw('Sources/Lidless/SettingsWindowController.swift', '    init(title: String = "Lidless Settings",\n', '    init(title: String = L10n.tr("Lidless Settings"),\n')

rw('Sources/Shared/AutoOff.swift', '        minutes > 0 ? optionLabel(minutes: minutes) : "No limit"\n', '        minutes > 0 ? optionLabel(minutes: minutes) : L10n.tr("No limit")\n')
rw('Sources/Shared/AutoOff.swift', '''        guard minutes % 60 == 0 else { return "\\(minutes) min" }\n        let h = minutes / 60\n        return h == 1 ? "1 hour" : "\\(h) hours"\n''', '''        guard minutes % 60 == 0 else { return L10n.tr("%d min", minutes) }\n        let h = minutes / 60\n        return h == 1 ? L10n.tr("1 hour") : L10n.tr("%d hours", h)\n''')

for old,new in [
('        case .highThermal:        return "Auto-paused: the Mac is running hot."\n','        case .highThermal:        return L10n.tr("Auto-paused: the Mac is running hot.")\n'),
('        case .notCharging:        return "Auto-paused: not on charger."\n','        case .notCharging:        return L10n.tr("Auto-paused: not on charger.")\n'),
('        case .lowBattery(let p):  return "Auto-paused: battery \\(p)% on battery power."\n','        case .lowBattery(let p):  return L10n.tr("Auto-paused: battery %d%% on battery power.", p)\n'),
('        case .notOnPower:         return "Auto-paused: not connected to power."\n','        case .notOnPower:         return L10n.tr("Auto-paused: not connected to power.")\n'),
('        case .highThermal:        return "Running hot"\n','        case .highThermal:        return L10n.tr("Running hot")\n'),
('        case .notCharging:        return "Not on charger"\n','        case .notCharging:        return L10n.tr("Not on charger")\n'),
('        case .lowBattery(let p):  return "Battery \\(p)% is at or below the cutoff"\n','        case .lowBattery(let p):  return L10n.tr("Battery %d%% is at or below the cutoff", p)\n'),
('        case .notOnPower:         return "Not connected to power"\n','        case .notOnPower:         return L10n.tr("Not connected to power")\n')]: rw('Sources/Shared/SafetySettings.swift', old, new)

print('self-build patch applied')
