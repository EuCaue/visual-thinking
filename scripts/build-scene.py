#!/usr/bin/env python3
"""Inject a scene JSON into templates/canvas.html.

Usage: build-scene.py scene.json out.html [title] [--fragment]

Default output is a complete standalone HTML document (doctype, html, head, body) that opens from a file
or any static host. --fragment keeps the template as it is (no document wrapper) for publish tools that
wrap the page in their own skeleton.
"""
import json, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]
fragment = '--fragment' in sys.argv
src, out = pathlib.Path(args[0]), pathlib.Path(args[1])
scene = json.loads(src.read_text())
title = args[2] if len(args) > 2 else scene.get("title", "Canvas")
tpl = (root / "templates" / "canvas.html").read_text()
page = re.sub(r'<script id="scene" type="application/json">.*?</script>', lambda m: '<script id="scene" type="application/json">\n' + json.dumps(scene, ensure_ascii=False, indent=2) + '\n</script>', tpl, flags=re.S)
page = re.sub(r'<title>.*?</title>', '<title>' + title.replace('<', '&lt;') + '</title>', page, count=1)
if not fragment:
    head, body = page.split('</style>', 1)
    page = '<!doctype html>\n<html lang="pt-BR">\n<head>\n' + head + '</style>\n</head>\n<body>' + body + '\n</body>\n</html>\n'
out.write_text(page)
print("built", out, "views:", [v["id"] for v in scene.get("views", [scene])], "(fragment)" if fragment else "(standalone)")
