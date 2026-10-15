"""Build a scene, open it in headless Chrome at a given size, return what a probe measured.

No test dependency beyond Chrome itself: the probe is a script appended to the page that
waits for the render, measures, and writes JSON into <pre id="vt-probe">; Chrome's
--dump-dom hands the DOM back. Pages are built offline (the default) so no network is needed
after the first build fills .vt-libs/.
"""

import json, os, pathlib, re, shutil, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
# headless shell first: full Chrome's new headless mode clamps windows to 500px wide, so phones cannot be measured with it
_SHELLS = sorted(pathlib.Path.home().glob(".cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell"))
CHROME = os.environ.get("VT_CHROME") or (str(_SHELLS[-1]) if _SHELLS else None) or next((c for c in ("chrome-headless-shell", "google-chrome", "chromium", "chromium-browser", "chrome") if shutil.which(c)), None)

PROBE = r"""
<script>
(function () {
  var t0 = Date.now();
  function done() {
    var w = document.getElementById('world'), m = /scale\(([\d.]+)\)/.exec(w.getAttribute('transform') || ''), boxes = [];
    Array.prototype.forEach.call(w.children, function (c) { var b = c.getBBox(); boxes.push({ id: c.dataset.block, w: Math.round(b.width), h: Math.round(b.height) }); });
    var out = { scale: m ? +m[1] : null, wrap: document.getElementById('wrap').clientWidth, inner: innerWidth, scrollW: document.documentElement.scrollWidth,
      reading: document.body.classList.contains('reading'), readerSections: document.querySelectorAll('#reader section').length,
      blocks: boxes, hash: location.hash, sel: (document.querySelector('.nd.sel, .item.sel') || {}).dataset || null,
      detail: (document.querySelector('#detail .name') || {}).textContent || '', btnRead: (document.querySelector('#btnRead span') || {}).textContent || '',
      level1: (document.querySelector('#levels [data-level="1"]') || {}).textContent || '', lang: document.documentElement.lang,
      svgLen: window.vtExport ? window.vtExport.svg().length : 0, svgHasStyle: window.vtExport ? window.vtExport.svg().indexOf('<style') >= 0 : false,
      fileHref: (document.querySelector('#detail a.file') || {}).href || '', count: document.getElementById('count').textContent, playDim: document.querySelectorAll('.play-dim').length, reader: (document.getElementById('reader') || {}).textContent || '', status: document.getElementById('status').textContent, errors: window.__errs || [] };
    var pre = document.createElement('pre'); pre.id = 'vt-probe'; pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
  }
  window.__errs = []; window.addEventListener('error', function (e) { window.__errs.push(String(e.message)); });
  (function wait() { var w = document.getElementById('world'); if ((w && w.children.length && w.getAttribute('transform') && !/Calculando|Computing/.test(document.getElementById('status').textContent)) || Date.now() - t0 > 6000) setTimeout(function () { if (window.__probeAct) window.__probeAct(); setTimeout(done, 300); }, 300); else setTimeout(wait, 50); })();
})();
</script>
"""


def build(scene, tmp, name="page", pre="", act=""):
    src = pathlib.Path(tmp) / (name + ".json")
    out = pathlib.Path(tmp) / (name + ".html")
    src.write_text(json.dumps(scene, ensure_ascii=False))
    r = subprocess.run(["python3", str(ROOT / "scripts/build-scene.py"), str(src), str(out), "--no-text-lint"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    page = out.read_text()
    probe = PROBE + ("<script>window.__probeAct = function () { " + act + " };</script>" if act else "")
    # `pre` runs before the runtime (e.g. to set localStorage); the probe after it
    page = page.replace('<script id="scene"', pre + '<script id="scene"', 1).replace("</body>", probe + "</body>")
    out.write_text(page)
    return out


def run(page, w, h, suffix=""):
    assert CHROME, "Chrome não encontrado"
    with tempfile.TemporaryDirectory() as prof:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", f"--user-data-dir={prof}", f"--window-size={w},{h}", "--virtual-time-budget=10000", "--allow-file-access-from-files", "--dump-dom", page.resolve().as_uri() + suffix], capture_output=True, text=True, timeout=90)
    m = re.search(r'<pre id="vt-probe">(.*?)</pre>', r.stdout, re.S)
    assert m, "probe não respondeu: " + r.stderr[-800:]
    import html
    return json.loads(html.unescape(m.group(1)))


