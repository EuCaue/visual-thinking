"""No text leaves its box and no two labels overlap, at phone and desktop width, in the catalog and the free-drawing example.

Runs tests/audit_layout.py on the scenes that hold every block; the full sweep over all examples is `python3 tests/audit_layout.py`.
"""

import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from audit_layout import audit


def test_catalog_and_free_have_no_spill_or_overlap():
    found = audit("examples/18-catalogo.json", [375, 1280]) + audit("examples/10-explicacao-livre.json", [375, 1280])
    assert not found, "\n".join(f"{f['width']}px {f.get('view')} · {f.get('block')} · {f['kind']}: {f['text']}" for f in found)


if __name__ == "__main__":
    test_catalog_and_free_have_no_spill_or_overlap()
    print("PASS")
