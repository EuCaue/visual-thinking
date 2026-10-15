"""Legibility at phone, tablet and desktop widths, measured in headless Chrome.

Pass: the canvas never goes below the legibility floor (scale 0.75), no horizontal page
scroll, wide blocks reflow to the legible width, phones open in reading mode with one
section per block.
"""

import sys, tempfile, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _headless import build, run

MIN_S = 0.75
SCENE = {
    "title": "Seis blocos largos",
    "basis": "docs",
    "views": [{
        "id": "m",
        "title": "V",
        "blocks": [
            {"type": "graph", "id": "g", "title": "Cadeia", "direction": "RIGHT",
             "nodes": [{"id": f"n{i}", "label": f"Serviço número {i}", "sub": "faz uma coisa"} for i in range(6)],
             "edges": [{"from": f"n{i}", "to": f"n{i+1}", "label": "chama"} for i in range(5)]},
            {"type": "cards", "id": "c", "title": "Seis cartões", "items": [{"title": f"Cartão {i}", "points": [{"kind": "pro", "text": "um ponto a favor"}]} for i in range(6)]},
            {"type": "matrix", "id": "x", "title": "Cinco opções", "columns": [f"Opção {i}" for i in range(5)],
             "rows": [{"label": "Custo mensal", "cells": [100, 200, 300, 400, 500], "best": "min", "unit": " R$"}, {"label": "Suporte", "cells": [True, False, True, True, False]}]},
            {"type": "steps", "id": "s", "title": "Sete etapas", "items": [{"title": f"Etapa {i}", "text": "faz algo"} for i in range(7)]},
            {"type": "kpi", "id": "k", "title": "Cinco números", "items": [{"label": f"Métrica {i}", "value": 12345 * (i + 1)} for i in range(5)]},
            {"type": "chart", "id": "ch", "title": "Série", "kind": "line", "width": 720, "series": [{"name": "a", "data": [["jan", 1], ["fev", 2], ["mar", 3]]}]},
        ],
    }],
}
SIZES = [(375, 812), (768, 1024), (1440, 900)]


def check(tmp):
    page = build(SCENE, tmp, "draw")
    for w, h in SIZES:
        r = run(page, w, h, "?mode=draw")
        assert not r["reading"], "?mode=draw abre o desenho"
        assert all(b["w"] > 0 for b in r["blocks"]), f"{w}px: bloco sem tamanho {r['blocks']}"
        assert not r["errors"], r["errors"]
        assert r["scrollW"] <= r["inner"], f"{w}px: scroll horizontal na página ({r['scrollW']} > {r['inner']})"
        assert r["scale"] is not None and r["scale"] >= MIN_S - 0.01, f"{w}px: escala {r['scale']} abaixo do piso {MIN_S}"
        legible_w = (r["wrap"] * 0.92 - (32 if r["wrap"] < 700 else 96)) / MIN_S
        for b in r["blocks"]:
            if b["id"] in ("c", "x", "s", "k", "ch"):
                assert b["w"] <= max(300, legible_w) * 1.08, f"{w}px: bloco {b['id']} com {b['w']}px passa da largura legível {legible_w:.0f}"
        if r["inner"] != w:
            print(f"  aviso: o navegador abriu com {r['inner']}px em vez de {w}px (use chrome-headless-shell ou VT_CHROME)")
        print(f"  {w}x{h}: escala {r['scale']}, blocos {[(b['id'], b['w']) for b in r['blocks']]}")
    phone = run(build(SCENE, tmp, "read"), 375, 812)
    assert phone["reading"], "celular sem preferência abre em modo leitura"
    assert phone["readerSections"] == len(SCENE["views"][0]["blocks"]), phone["readerSections"]
    desk = run(build(SCENE, tmp, "read"), 1440, 900)
    assert not desk["reading"], "desktop abre no desenho"
    assert desk["readerSections"] == len(SCENE["views"][0]["blocks"]), "o texto acessível existe também no desktop"


def test_responsive():
    with tempfile.TemporaryDirectory() as t:
        check(t)


if __name__ == "__main__":
    test_responsive()
    print("PASS")
