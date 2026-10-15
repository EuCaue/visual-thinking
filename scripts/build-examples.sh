#!/bin/sh
# Rebuild every example page from its scene JSON. --cdn keeps the repo light; a built page for a user is offline by default.
cd "$(dirname "$0")/.." || exit 1
for f in examples/*.json; do python3 scripts/build-scene.py "$f" "${f%.json}.html" --cdn || exit 1; done
