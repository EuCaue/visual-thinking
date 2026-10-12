"""Runtime checks via agent-browser when the CLI exists; skips otherwise.

Opens its own tab (tab new) so it never disturbs the focused one.
"""

import shutil, subprocess


def _run(cmd):
    return subprocess.run(["agent-browser"] + cmd, capture_output=True, text=True)


def _open_and_eval(page, js):
    _run(["tab", "new"])
    _run(["open", "file://" + page])
    subprocess.run(["sleep", "4"])
    r = _run(["eval", js])
    out = r.stdout.strip().strip('"')
    _run(["tab", "close"])
    return out


def motion(off, on, kinds):
    if not shutil.which("agent-browser"):
        print("(agent-browser ausente, verificação de DOM pulada)")
        return
    js = "document.querySelectorAll('#canvas animateMotion').length"
    n = _open_and_eval(off, js)
    assert n == "0", f"motion off: animateMotion={n}, esperado 0"
    n = _open_and_eval(on, js)
    assert n == "2", f"motion on: animateMotion={n}, esperado 2"
    n = _open_and_eval(kinds, js)
    assert n == "2", f"kinds: animateMotion={n}, esperado 2 (data e event only)"
