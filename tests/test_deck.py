"""Deck mode: a scene with deck:true is one 16:9 slide per view, with a cover, notes and an overview."""

import json, pathlib, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _headless import build, run

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "22-presentation.json"

DECK_PROBE = r"""
<script>
(function () {
  window.__errs = [];
  window.addEventListener('error', function (e) { window.__errs.push(String(e.message)); });
  function done() {
    var w = document.getElementById('world'), wrap = document.getElementById('wrap'), canvas = document.getElementById('canvas'), boxes = [];
    if (w) Array.prototype.forEach.call(w.children, function (c) { var b = c.getBBox(); boxes.push({ id: c.dataset.block, w: Math.round(b.width), h: Math.round(b.height) }); });
    var sc = /scale\(([\d.]+)\)/.exec((w && w.getAttribute('transform')) || '');
    var out = {
      deck: document.body.classList.contains('deck'),
      count: (document.getElementById('deckCount') || {}).textContent || '',
      title: (document.getElementById('deckSlideTitle') || {}).textContent || '',
      lead: (document.getElementById('deckSlideLead') || {}).textContent || '',
      stage: wrap ? { w: Math.round(wrap.getBoundingClientRect().width), h: Math.round(wrap.getBoundingClientRect().height) } : null,
      canvas: canvas ? { w: Math.round(canvas.getBoundingClientRect().width), h: Math.round(canvas.getBoundingClientRect().height) } : null,
      blocks: boxes,
      scale: sc ? +sc[1] : null,
      reading: document.body.classList.contains('reading'),
      special: (document.getElementById('deckSpecial') || {}).hidden === false,
      specialHidden: (document.getElementById('deckSpecial') || {}).hidden === true,
      specialTitle: (document.querySelector('#deckSpecial .cover-title') || {}).textContent || '',
      canvasDisplay: canvas ? getComputedStyle(canvas).display : '',
      notesExpanded: document.getElementById('deckNotesBtn') ? document.getElementById('deckNotesBtn').getAttribute('aria-expanded') : '',
      overviewExpanded: document.getElementById('deckOverviewBtn') ? document.getElementById('deckOverviewBtn').getAttribute('aria-expanded') : '',
      focus: (document.activeElement && document.activeElement.id) || '',
      focusTag: (document.activeElement && document.activeElement.tagName) || '',
      focusClass: (document.activeElement && document.activeElement.getAttribute && document.activeElement.getAttribute('class')) || '',
      asidePosition: document.getElementById('aside') ? getComputedStyle(document.getElementById('aside')).position : '',
      panelOff: document.body.classList.contains('panel-off'),
      detailTitle: (document.querySelector('#detail .name') || {}).textContent || '',
      extCount: document.querySelectorAll('.ext').length,
      extPointer: document.querySelector('.ext') ? getComputedStyle(document.querySelector('.ext')).pointerEvents : '',
      extButtonPointer: document.querySelector('.ext button') ? getComputedStyle(document.querySelector('.ext button')).pointerEvents : '',
      extButtonTab: document.querySelector('.ext button') ? document.querySelector('.ext button').getAttribute('tabindex') : '',
      extHits: document.querySelectorAll('.ext .blk-hit').length,
      extLinkHref: document.getElementById('extA') ? document.getElementById('extA').getAttribute('href') : '',
      extSummaryTab: document.querySelector('.ext summary') ? document.querySelector('.ext summary').getAttribute('tabindex') : '',
      overview: (document.getElementById('deckOverview') || {}).open === true,
      overviewCount: document.querySelectorAll('#deckGrid button').length,
      notes: (document.getElementById('deckNotes') || {}).hidden === false,
      notesText: (document.getElementById('deckNotesBody') || {}).textContent || '',
      reader: (document.getElementById('reader') || {}).textContent || '',
      hash: location.hash,
      errors: window.__errs
    };
    var pre = document.createElement('pre'); pre.id = 'vt-probe'; pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
  }
  function ready() {
    var c = document.getElementById('deckCount'), s = document.getElementById('status');
    if (document.body.classList.contains('deck') && c && c.textContent && !/Calculando|Computing/.test((s || {}).textContent || '')) {
      if (window.__probeAct) { window.__probeAct(); setTimeout(done, 2400); } else setTimeout(done, 600);
    } else setTimeout(ready, 80);
  }
  setTimeout(ready, 50);
})();
</script>
"""


def validate(scene):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(scene, f)
        path = f.name
    return subprocess.run(
        ["python3", "scripts/build-scene.py", path, "--validate-only"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_deck_build_and_runtime():
    scene = json.loads(EXAMPLE.read_text())
    with tempfile.TemporaryDirectory() as t:
        page = build(scene, t, "deck", probe=DECK_PROBE)
        html = page.read_text()
        for needle in (
            '"deck": true',
            "body.deck",
            'id="deckBar"',
            'id="deckSpecial"',
            'id="deckOverview"',
        ):
            assert needle in html, needle

        first = run(page, 1440, 900, "#v=cover")
        assert first["deck"] and first["count"] == "1 / 6", first
        assert first["special"] and first["canvasDisplay"] == "none", first
        assert not first["errors"], first["errors"]

        flow = run(page, 1440, 900, "#v=flow")
        assert flow["count"] == "3 / 6", flow
        assert flow["title"].startswith("Synchronous sending"), flow["title"]
        assert flow["specialHidden"] and flow["canvasDisplay"] != "none", flow
        assert flow["blocks"] and all(
            b["w"] > 0 and b["h"] > 0 for b in flow["blocks"]
        ), flow["blocks"]
        assert abs(flow["stage"]["w"] / flow["stage"]["h"] - 16 / 9) < 0.03, flow[
            "stage"
        ]
        assert flow["scale"] >= 0.7, "o desenho cabe e continua legível no slide"
        assert flow["panelOff"], "o inspector começa fechado"
        assert not flow["errors"], flow["errors"]

        node = run(
            build(
                scene,
                t,
                "deck-node",
                probe=DECK_PROBE,
                act="document.querySelector('.nd[data-id=\"stripe\"]').dispatchEvent(new MouseEvent('click', { bubbles: true }));",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert not node["panelOff"], node
        assert node["detailTitle"] == "Stripe", node
        assert node["asidePosition"] == "fixed", node
        assert node["focus"] == "deckInspectorClose", node
        assert node["scale"] == flow["scale"], (
            "abrir o inspector não reenquadra o slide"
        )
        assert not node["errors"], node["errors"]

        block = run(
            build(
                scene,
                t,
                "deck-block",
                probe=DECK_PROBE,
                act="var h=document.querySelector('.blk[data-block=\"sync\"] .blk-hit'); h.focus(); h.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert not block["panelOff"] and block["detailTitle"] == "The synchronous path", (
            block
        )
        assert block["focus"] == "deckInspectorClose", block
        assert not block["errors"], block["errors"]

        inspector_close = run(
            build(
                scene,
                t,
                "deck-inspector-close",
                probe=DECK_PROBE,
                act="document.querySelector('.nd[data-id=\"stripe\"]').dispatchEvent(new MouseEvent('click', { bubbles: true })); setTimeout(function(){ document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); }, 700);",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert inspector_close["panelOff"], inspector_close
        assert "nd" in inspector_close["focusClass"], (
            "o foco volta ao elemento selecionado"
        )
        assert inspector_close["scale"] == flow["scale"], inspector_close
        assert not inspector_close["errors"], inspector_close["errors"]

        forward = run(
            build(
                scene,
                t,
                "deck-forward",
                probe=DECK_PROBE,
                act="setTimeout(function(){ document.getElementById('deckNext').click(); }, 200); setTimeout(function(){ document.getElementById('deckNext').click(); }, 1000);",
            ),
            1440,
            900,
            "#v=cover",
        )
        assert forward["count"] == "3 / 6" and forward["blocks"], forward
        assert forward["canvasDisplay"] != "none" and forward["specialHidden"], forward
        assert not forward["errors"], forward["errors"]

        back = run(
            build(
                scene,
                t,
                "deck-back",
                probe=DECK_PROBE,
                act="setTimeout(function(){ document.getElementById('deckPrev').click(); }, 200); setTimeout(function(){ document.getElementById('deckPrev').click(); }, 1000);",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert back["count"] == "1 / 6" and back["special"], back
        assert back["canvasDisplay"] == "none", (
            "the cover does not leave the previous drawing visible"
        )
        assert back["panelOff"], "the cover closes the inspector"
        assert not back["errors"], back["errors"]

        act = "document.getElementById('deckNext').click(); setTimeout(function(){ document.getElementById('deckNotesBtn').click(); }, 1200);"
        nxt = run(
            build(scene, t, "deck-next", probe=DECK_PROBE, act=act),
            1440,
            900,
            "#v=flow",
        )
        assert nxt["count"] == "4 / 6", nxt
        assert nxt["title"] == "p95 fell from 2.4 s to 180 ms", nxt["title"]
        assert nxt["notes"] and "deploy" in nxt["notesText"], nxt
        assert not nxt["errors"], nxt["errors"]

        key = "document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));"
        kb = run(
            build(scene, t, "deck-key", probe=DECK_PROBE, act=key),
            1440,
            900,
            "#v=flow",
        )
        assert kb["count"] == "4 / 6", kb
        assert not kb["errors"], kb["errors"]

        end = run(
            build(
                scene,
                t,
                "deck-end",
                probe=DECK_PROBE,
                act="document.dispatchEvent(new KeyboardEvent('keydown', { key: 'End', bubbles: true }));",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert end["count"] == "6 / 6" and end["special"], end
        assert end["specialTitle"] == "The API answers before the email", end
        assert end["canvasDisplay"] == "none", end
        assert not end["errors"], end["errors"]

        closers = run(
            build(
                scene,
                t,
                "deck-closers",
                probe=DECK_PROBE,
                act="document.getElementById('deckNotesBtn').click(); setTimeout(function(){ document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); }, 500); setTimeout(function(){ document.getElementById('deckOverviewBtn').click(); }, 1000); setTimeout(function(){ document.getElementById('deckOverviewClose').click(); }, 1600);",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert not closers["notes"] and not closers["overview"], closers
        assert closers["notesExpanded"] == "false", closers
        assert closers["overviewExpanded"] == "false", closers
        assert closers["focus"] == "deckOverviewBtn", closers
        assert not closers["errors"], closers["errors"]

        readkeys = run(
            build(
                scene,
                t,
                "deck-readkeys",
                probe=DECK_PROBE,
                act="document.dispatchEvent(new KeyboardEvent('keydown', { key: 'PageDown', bubbles: true })); setTimeout(function(){ document.dispatchEvent(new KeyboardEvent('keydown', { key: 'o', bubbles: true })); }, 300);",
            ),
            1440,
            900,
            "?mode=read#v=flow",
        )
        assert readkeys["reading"] and readkeys["count"] == "3 / 6", readkeys
        assert readkeys["overview"], "o abre a visão geral também no modo texto"
        assert not readkeys["errors"], readkeys["errors"]

        overview = run(
            build(
                scene,
                t,
                "deck-overview",
                probe=DECK_PROBE,
                act="document.getElementById('deckOverviewBtn').click();",
            ),
            1440,
            900,
            "#v=flow",
        )
        assert overview["overview"] and overview["overviewCount"] == 6, overview
        assert not overview["errors"], overview["errors"]

        phone = run(page, 390, 844, "#v=flow")
        assert phone["reading"], phone
        assert "Synchronous sending couples three failures" in phone["reader"], phone[
            "reader"
        ][:120]
        assert "Notes" in phone["reader"], "notes appear in text mode"


def test_deck_external_is_inert():
    external = {
        "title": "Externo",
        "summary": "S",
        "deck": True,
        "views": [
            {
                "id": "a",
                "title": "O que veio de fora",
                "blocks": [
                    {
                        "type": "custom",
                        "id": "c",
                        "title": "HTML externo",
                        "alt": "Um botão externo",
                        "html": "<button id='extBtn'>não clique</button><a id='extA' href='https://example.com'>link</a><details><summary>mais</summary>detalhe</details>",
                        "width": 200,
                        "height": 80,
                    },
                    {
                        "type": "free",
                        "id": "f",
                        "title": "Imagem externa",
                        "elements": [
                            {
                                "type": "image",
                                "id": "img",
                                "x": 0,
                                "y": 0,
                                "w": 120,
                                "h": 80,
                                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10'%3E%3Crect width='10' height='10' fill='%23ccc'/%3E%3C/svg%3E",
                                "alt": "Imagem externa",
                            }
                        ],
                    },
                ],
            }
        ],
    }
    with tempfile.TemporaryDirectory() as t:
        page = build(external, t, "deck-external", probe=DECK_PROBE)
        r = run(page, 1440, 900, "?mode=draw#v=a")
        assert r["extCount"] >= 2, r
        assert r["extPointer"] == "none", r
        assert r["extButtonPointer"] == "none", r
        assert r["extButtonTab"] == "-1", r
        assert r["extHits"] == 0, "o título do bloco externo não abre o inspector"
        assert not r["extLinkHref"], "links externos perdem o href no deck"
        assert r["extSummaryTab"] == "-1", r
        assert not r["errors"], r["errors"]


def test_deck_validation():
    invalid = {
        "title": "Deck",
        "summary": "S",
        "deck": True,
        "views": [
            {
                "id": "a",
                "title": "A",
                "cover": "sim",
                "section": 1,
                "notes": 123,
                "blocks": [{"type": "text", "id": "t", "text": "um fato"}],
            },
            {"id": "a", "title": "B", "blocks": []},
        ],
    }
    r = validate(invalid)
    assert r.returncode == 1, r.stdout
    for needle in (
        "cover must be true or false",
        "section must be true or false",
        "both cover and section",
        "notes must be a string or a list of strings",
        "duplicate view ids",
        "blocks are ignored",
    ):
        assert needle in r.stdout, (needle, r.stdout)

    dense = {
        "title": "Deck",
        "summary": "S",
        "deck": True,
        "views": [
            {
                "id": "a",
                "title": "A",
                "blocks": [
                    {"type": "text", "id": f"t{i}", "text": "um fato"} for i in range(5)
                ],
            }
        ],
    }
    r = validate(dense)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "5 blocks" in r.stdout and "no speaker notes" in r.stdout, r.stdout

    nodeck = {
        "title": "Canvas",
        "summary": "S",
        "views": [{"id": "a", "title": "A", "notes": "só no deck"}],
    }
    r = validate(nodeck)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "notes only render in deck mode" in r.stdout, r.stdout


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("PASS")
