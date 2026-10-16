#!/bin/sh
# Package the skill for a release: dist/visual-thinking-<version>.zip holds one visual-thinking/
# folder with what an agent needs (instructions, templates, scripts, example scenes), without
# tests, docs or built pages. Unzip it into a skills folder to install.
cd "$(dirname "$0")/.." || exit 1
version=$(sed -n 's/^ *version: *"\{0,1\}\([0-9][0-9.]*\)"\{0,1\}$/\1/p' SKILL.md | head -1)
[ -n "$version" ] || { echo "no version in SKILL.md metadata" >&2; exit 1; }
out="dist/visual-thinking-$version.zip"
stage=$(mktemp -d) || exit 1
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/visual-thinking/examples" dist
cp SKILL.md strategy.md formats.md design.md examples.md README.md LICENSE "$stage/visual-thinking/"
cp -r templates scripts "$stage/visual-thinking/"
cp examples/*.json "$stage/visual-thinking/examples/"
find "$stage" -name __pycache__ -prune -exec rm -rf {} +
rm -f "$out"
(cd "$stage" && zip -qr -X "$OLDPWD/$out" visual-thinking) || exit 1
echo "$PWD/$out"
sha256sum "$out" | cut -d' ' -f1
