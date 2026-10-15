#!/usr/bin/env python3
"""Find text that leaves its box or sits on other text, in every view of every example.

Usage: tests/audit_layout.py [example.json ...] [--width 375,1280] [--shots DIR] [--json]

Builds each scene offline, opens it in headless Chrome, walks every view and
measures in screen coordinates:
  - spill: a text inside a shape (node, card, step, bar, cell...) reaching past
    that shape's edge;
  - overlap: two texts of different elements whose boxes intersect.
With --shots, also saves one PNG per view and width for a human (or agent) look.
Exit 1 when anything is found.
"""

import glob, json, pathlib, re, subprocess, sys, tempfile, html as H

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _headless import build, CHROME

PROBE = r"""<script>
(function () {
  var results = [], views = Array.prototype.map.call(document.querySelectorAll('#views button'), function (b) { return b.dataset.view; });
  if (!views.length) views = [null];
  var SHAPE = 'rect:not(.hit):not(.item-hit):not(.sel-ring):not(.blk-hit):not(.grp-hit):not(.row-hit):not(.col-hit):not(.er-row), ellipse, circle.mk-arc';
  function box(e) { var r = e.getBoundingClientRect(); return { x: r.left, y: r.top, r: r.right, b: r.bottom, w: r.width, h: r.height }; }
  function shapeOf(t) { var g = t.parentNode; while (g && g.id !== 'world') { if (g.matches && g.matches('.nd, .el, .item, .grp')) { var s = g.querySelector(':scope > ' + SHAPE.split(', ').join(', :scope > ')); if (s) return { g: g, s: s }; } g = g.parentNode; } return null; }
  function audit(view) {
    var out = [], texts = Array.prototype.filter.call(document.querySelectorAll('#world text'), function (t) { return t.textContent.trim() && t.getBoundingClientRect().width > 0 && !t.closest('.rough') && getComputedStyle(t).opacity !== '0' && !t.closest('.lod') ; });
    var scale = +(/scale\(([\d.]+)\)/.exec(document.getElementById('world').getAttribute('transform') || '') || [0, 1])[1];
    var tol = 1.5 * scale;
    texts.forEach(function (t) { var sh = shapeOf(t); if (!sh) return; var a = box(t), b = box(sh.s); if (b.w < 24 || b.h < a.h * 1.2) return;  // swatches and markers are not containers
      var dx = Math.max(b.x - a.x, a.r - b.r), dy = Math.max(b.y - a.y, a.b - b.b);
      if (dx > tol || dy > tol) out.push({ kind: 'spill', view: view, block: (t.closest('.blk') || {}).dataset ? t.closest('.blk').dataset.block : '', text: t.textContent.slice(0, 60), by: Math.round(Math.max(dx, dy) / scale) }); });
    for (var i = 0; i < texts.length; i++) for (var j = i + 1; j < texts.length; j++) { var p = texts[i], q = texts[j], gp = p.closest('.nd, .el, .item, .grp, .blk'), gq = q.closest('.nd, .el, .item, .grp, .blk'); if (gp === gq && gp && !gp.classList.contains('blk')) continue;
      var A = box(p), B = box(q), ox = Math.min(A.r, B.r) - Math.max(A.x, B.x), oy = Math.min(A.b, B.b) - Math.max(A.y, B.y);
      if (ox > 2 * scale && oy > 3 * scale) out.push({ kind: 'overlap', view: view, block: (p.closest('.blk') || {}).dataset ? p.closest('.blk').dataset.block : '', text: p.textContent.slice(0, 40) + ' | ' + q.textContent.slice(0, 40) }); }
    return out;
  }
  var i = 0;
  (function next() {
    if (i >= views.length) { var pre = document.createElement('pre'); pre.id = 'vt-audit'; pre.textContent = JSON.stringify(results); document.body.appendChild(pre); return; }
    var v = views[i++], b = v && document.querySelector('#views [data-view="' + v + '"]'); if (b) b.click();
    setTimeout(function () { results = results.concat(audit(v)); next(); }, 900);
  })();
})();
</script>"""


def audit(scene_path, widths, shots=None):
    scene = json.loads(pathlib.Path(scene_path).read_text())
    name = pathlib.Path(scene_path).stem
    found = []
    with tempfile.TemporaryDirectory() as t:
        page = build(scene, t, name)
        base = page.read_text()
        audited = pathlib.Path(t) / (name + "-audit.html")
        audited.write_text(base.replace("</body>", PROBE + "</body>", 1))
        for w in widths:
            out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={w},900", "--virtual-time-budget=40000", "--dump-dom", audited.resolve().as_uri() + "?mode=draw"], capture_output=True, text=True, timeout=180).stdout
            m = re.search(r'<pre id="vt-audit">(.*?)</pre>', out, re.S)
            if not m:
                found.append({"kind": "error", "example": name, "width": w, "text": "auditoria não respondeu"})
                continue
            for r in json.loads(H.unescape(m.group(1))):
                r.update({"example": name, "width": w})
                found.append(r)
            if shots:
                pathlib.Path(shots).mkdir(parents=True, exist_ok=True)
                for v in [v.get("id") for v in scene.get("views", [])] or [None]:
                    png = pathlib.Path(shots) / f"{name}-{v}-{w}.png"
                    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--window-size={w},900", "--virtual-time-budget=15000", f"--screenshot={png}", page.resolve().as_uri() + f"?mode=draw#v={v}"], capture_output=True, timeout=120)
    return found


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    widths = [int(x) for x in (sys.argv[sys.argv.index("--width") + 1] if "--width" in sys.argv else "375,1280").split(",")]
    shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
    if shots in args:
        args.remove(shots)
    if "--width" in sys.argv:
        args = [a for a in args if a != sys.argv[sys.argv.index("--width") + 1]]
    files = args or sorted(glob.glob("examples/*.json"))
    allf = []
    for f in files:
        r = audit(f, widths, shots)
        allf += r
        if "--json" not in sys.argv:
            print(f"{pathlib.Path(f).stem}: {len(r)}")
            for x in r[:40]:
                print(f"  {x['width']}px {x.get('view')} · {x.get('block')} · {x['kind']}{' +' + str(x['by']) + 'px' if 'by' in x else ''}: {x['text']}")
    if "--json" in sys.argv:
        print(json.dumps(allf, ensure_ascii=False, indent=1))
    sys.exit(1 if allf else 0)


if __name__ == "__main__":
    main()
