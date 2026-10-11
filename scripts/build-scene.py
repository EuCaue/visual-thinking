#!/usr/bin/env python3
"""Inject a scene JSON into templates/canvas.html.  Usage: build-scene.py scene.json out.html [title]"""
import json, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
scene = json.loads(src.read_text())
title = sys.argv[3] if len(sys.argv) > 3 else scene.get("title", "Canvas")
tpl = (root / "templates" / "canvas.html").read_text()
page = re.sub(r'<script id="scene" type="application/json">.*?</script>', lambda m: '<script id="scene" type="application/json">\n' + json.dumps(scene, ensure_ascii=False, indent=2) + '\n</script>', tpl, flags=re.S)
page = re.sub(r'<title>.*?</title>', '<title>' + title + '</title>', page, count=1)
out.write_text(page); print("built", out, "views:", [v["id"] for v in scene.get("views", [scene])])
