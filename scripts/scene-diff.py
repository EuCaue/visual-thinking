#!/usr/bin/env python3
"""Merge two versions of a scene into one that marks what changed.

Usage: scene-diff.py before.json after.json out.json

Graph nodes and edges, and entity tables and relations, are matched by id
(edges and relations by their two ends). Each element of the result carries
`diff`: "added" (only after), "removed" (only before, kept so the reader sees
it go) or "changed" (in both, label, sub, kind, group, file or fields differ).
Every other block is taken from `after`. The runtime draws the marks and lists
them in the legend under "Changes".
"""

import copy, json, pathlib, sys

NODE_KEYS = ("label", "sub", "kind", "group", "file", "status")
EDGE_KEYS = ("label", "kind")


def fields_of(e):
    return [f if isinstance(f, dict) else {"name": f} for f in e.get("fields") or []]


def merge_list(before, after, key, keys, extra=None):
    """Return the merged list and a counter of marks."""
    b = {key(x): x for x in before}
    out, n = [], {"added": 0, "removed": 0, "changed": 0}
    for x in after:
        y = copy.deepcopy(x)
        old = b.get(key(x))
        if old is None:
            y["diff"] = "added"
        else:
            diffs = [k for k in keys if old.get(k) != x.get(k)]
            if extra:
                diffs += extra(old, x)
            if diffs:
                y["diff"] = "changed"
                y.setdefault("notes", [])
                y["notes"] = list(y["notes"]) + [f"antes: {k} = {old.get(k)!r}" if k in keys else k for k in diffs][:4]
        if y.get("diff"):
            n[y["diff"]] += 1
        out.append(y)
    seen = {key(x) for x in after}
    for x in before:
        if key(x) not in seen:
            y = copy.deepcopy(x)
            y["diff"] = "removed"
            n["removed"] += 1
            out.append(y)
    return out, n


def field_changes(old, new):
    a = {f["name"]: f for f in fields_of(old)}
    z = {f["name"]: f for f in fields_of(new)}
    msg = [f"campo novo: {k}" for k in z if k not in a]
    msg += [f"campo removido: {k}" for k in a if k not in z]
    msg += [f"campo alterado: {k}" for k in z if k in a and a[k] != z[k]]
    return msg


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__.strip())
    before = json.loads(pathlib.Path(sys.argv[1]).read_text())
    after = json.loads(pathlib.Path(sys.argv[2]).read_text())
    out = copy.deepcopy(after)
    bviews = {v.get("id"): v for v in before.get("views") or []}
    total = {"added": 0, "removed": 0, "changed": 0}
    for v in out.get("views") or []:
        bv = bviews.get(v.get("id")) or {}
        bblocks = {b.get("id"): b for b in bv.get("blocks") or []}
        for b in v.get("blocks") or []:
            ob = bblocks.get(b.get("id"))
            if not ob or ob.get("type") != b.get("type"):
                continue
            if b["type"] == "graph":
                b["nodes"], n1 = merge_list(ob.get("nodes") or [], b.get("nodes") or [], lambda x: x.get("id"), NODE_KEYS)
                b["edges"], n2 = merge_list(ob.get("edges") or [], b.get("edges") or [], lambda x: (x.get("from"), x.get("to")), EDGE_KEYS)
                gids = {g.get("id") for g in b.get("groups") or []}
                for g in ob.get("groups") or []:
                    if g.get("id") not in gids and any(n.get("group") == g.get("id") for n in b["nodes"]):
                        b.setdefault("groups", []).append(copy.deepcopy(g))
            elif b["type"] == "entity":
                b["entities"], n1 = merge_list(ob.get("entities") or [], b.get("entities") or [], lambda x: x.get("id"), ("label", "sub"), field_changes)
                b["relations"], n2 = merge_list(ob.get("relations") or [], b.get("relations") or [], lambda x: (x.get("from"), x.get("to")), ("label", "card"))
            else:
                continue
            for k in total:
                total[k] += n1[k] + n2[k]
    out["title"] = after.get("title", "")
    out["subtitle"] = f"+{total['added']} novos · {total['changed']} alterados · −{total['removed']} removidos"
    out["summary"] = after.get("summary", "")
    pathlib.Path(sys.argv[3]).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(pathlib.Path(sys.argv[3]).resolve())
    print(f"+{total['added']} added · {total['changed']} changed · −{total['removed']} removed")


if __name__ == "__main__":
    main()
