#!/usr/bin/env python3
"""WCAG contrast check for the token pairs that matter, light and dark. Exit 1 on failure."""
import re, pathlib, sys

css = (pathlib.Path(__file__).resolve().parent.parent / "templates" / "_tokens.css").read_text()

def block(selector_regex):
    m = re.search(selector_regex + r"\s*\{(.*?)\n\}", css, re.S | re.M)
    if not m:
        raise SystemExit("selector not found: " + selector_regex)
    return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", m.group(1)))

light = block(r"^:root")
dark = dict(light); dark.update(block(r"^:root\[data-theme=\"dark\"\]"))

def lum(h):
    r, g, b = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

pairs = [  # (fg, bg, minimum)
    ("fg", "bg", 4.5), ("fg", "bg-elev", 4.5), ("fg", "bg-inset", 4.5),
    ("fg-muted", "bg", 4.5), ("fg-muted", "bg-elev", 4.5), ("fg-muted", "bg-inset", 4.5),
    ("fg-faint", "bg-elev", 3.0),
    ("accent", "bg-elev", 4.5), ("ok", "bg-elev", 4.5), ("warn", "bg-elev", 4.5), ("danger", "bg-elev", 4.5),
    ("accent", "accent-soft", 3.0), ("ok", "ok-soft", 3.0), ("warn", "warn-soft", 3.0), ("danger", "danger-soft", 3.0),
    ("fg", "accent-soft", 4.5), ("fg", "ok-soft", 4.5), ("fg", "warn-soft", 4.5), ("fg", "danger-soft", 4.5),
    ("accent-fg", "accent", 4.5), ("line-strong", "bg-elev", 1.5),
]
fail = False
for name, pal in (("light", light), ("dark", dark)):
    for fg, bg, mn in pairs:
        r = ratio(pal[fg], pal[bg])
        ok = r >= mn
        fail |= not ok
        print(f"{name:5} {fg:12} on {bg:12} {r:5.2f} {'ok' if ok else 'FAIL (min %.1f)' % mn}")
sys.exit(1 if fail else 0)
