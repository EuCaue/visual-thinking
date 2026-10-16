# Contributing

## The gates

Every change passes three checks before a commit:

```bash
sh scripts/build-examples.sh      # every scene builds, exit 0
for t in tests/test_*.py; do python3 "$t"; done   # every test prints PASS
python3 scripts/contrast.py       # every line ends in ok
```

If you touched `templates/_tokens.css`, run `python3 scripts/sync-tokens.py` first so the templates pick it up, then `--check` to confirm no drift.

## Adding an example

An example is a scene JSON plus its built HTML. Start from an existing scene, keep one idea per scene, and make the title state the finding ("Svelte troca runtime por build", not "Comparação"). The build warns about missing titles, summaries and labels; fix them rather than silencing the warning. Then rebuild:

```bash
sh scripts/build-examples.sh
```

Open the page in a browser in both themes before committing. Anything you cannot explain why it is on the page gets deleted.

## Writing docs

Every claim in the README, SKILL.md, strategy.md, formats.md and design.md has to be true against the code: a command that runs, a file that exists, a count that matches `ls`. If you find a doc that contradicts the implementation, say which is wrong before changing either.

## Reporting a problem

Open an issue with the bug template: the smallest scene JSON that shows it, what you expected, and the theme and window width. A scene is worth a thousand descriptions.

## Releasing

Bump `metadata.version` in `SKILL.md`, then run `sh scripts/package-skill.sh`. It writes `dist/visual-thinking-<version>.zip` (one `visual-thinking/` folder with the instructions, templates, scripts and example scenes) and prints its SHA-256 for the release notes. Tag the commit `v<version>` and attach the zip to the GitHub release.
