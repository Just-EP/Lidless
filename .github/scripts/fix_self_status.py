#!/usr/bin/env python3
from pathlib import Path

p = Path('Sources/Lidless/MenuContent.swift')
s = p.read_text(encoding='utf-8')
old = '''            HStack(spacing: 6) {
                Image(systemName: state.usingHelper ? "checkmark.circle.fill" : "exclamationmark.circle.fill")
                    .foregroundStyle(state.usingHelper ? .green : .orange)
                Text(L10n.tr(state.usingHelper ? "Helper active" : "Helper inactive"))
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel(state.usingHelper ? "Background helper active" : "Background helper inactive")
'''
new = '''            HStack(spacing: 6) {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundStyle(.green)
                Text("自用模式已启用")
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("自用模式已启用")
'''
if old not in s:
    raise SystemExit('status row patch anchor not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('self-use status row patched')
