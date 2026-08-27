#!/usr/bin/env python3
from pathlib import Path

root = Path('.').resolve()

# Localize external-change notices.
p = root / 'Sources/Shared/StateReconciler.swift'
s = p.read_text(encoding='utf-8')
s = s.replace('case .enabledOutside:  return "Sleep prevention was turned on outside Lidless."',
              'case .enabledOutside:  return L10n.tr("Sleep prevention was turned on outside Lidless.")')
s = s.replace('case .disabledOutside: return "Sleep prevention was turned off outside Lidless."',
              'case .disabledOutside: return L10n.tr("Sleep prevention was turned off outside Lidless.")')
p.write_text(s, encoding='utf-8')

# In auto mode, an external off can be a transient event from the previous
# self-build watchdog during app replacement/relaunch. Once our corrective
# auto-enable succeeds, the event is no longer actionable, so clear it.
p = root / 'Sources/Lidless/AppState.swift'
s = p.read_text(encoding='utf-8')
old_helper = '''                    self.isEnabled = target\n                    self.lastError = resultMessage\n                    self.manageHeartbeat()\n'''
new_helper = '''                    self.isEnabled = target\n                    self.lastError = resultMessage\n                    if origin == .auto, target { self.externalNotice = nil }\n                    self.manageHeartbeat()\n'''
if old_helper in s:
    s = s.replace(old_helper, new_helper, 1)

old_fallback = '''                isEnabled = target\n                lastError = resultMessage\n                manageHeartbeat()\n'''
new_fallback = '''                isEnabled = target\n                lastError = resultMessage\n                if origin == .auto, target { externalNotice = nil }\n                manageHeartbeat()\n'''
if old_fallback not in s:
    raise SystemExit('fallback success anchor not found')
s = s.replace(old_fallback, new_fallback, 1)
p.write_text(s, encoding='utf-8')

loc = root / 'Resources/zh-Hans.lproj/Localizable.strings'
text = loc.read_text(encoding='utf-8')
extra = '''\n"Sleep prevention was turned on outside Lidless." = "检测到 Lidless 之外启用了防休眠。";\n"Sleep prevention was turned off outside Lidless." = "检测到 Lidless 之外关闭了防休眠。";\n'''
if '"Sleep prevention was turned off outside Lidless."' not in text:
    text += extra
loc.write_text(text, encoding='utf-8')

print('external notice localization/recovery patch applied')
