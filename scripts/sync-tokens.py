#!/usr/bin/env python3
"""Copy templates/_tokens.css into every template between the TOKENS:BEGIN / TOKENS:END markers.

Run after editing _tokens.css:  python3 scripts/sync-tokens.py
Check mode (exit 1 on drift):    python3 scripts/sync-tokens.py --check
"""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
tokens = (root / "templates" / "_tokens.css").read_text()
block = re.search(r"/\* TOKENS:BEGIN.*?/\* TOKENS:END \*/", tokens, re.S).group(0)
check = "--check" in sys.argv
drift = []
for tpl in sorted((root / "templates").glob("*.html")):
    src = tpl.read_text()
    new = re.sub(r"/\* TOKENS:BEGIN.*?/\* TOKENS:END \*/", lambda m: block, src, flags=re.S)
    if new != src:
        drift.append(tpl.name)
        if not check:
            tpl.write_text(new)
if check:
    print("drift:", drift or "none")
    sys.exit(1 if drift else 0)
print("synced:", drift or "nothing to do")
