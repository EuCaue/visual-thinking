#!/bin/sh
# Rebuild every example page from its scene JSON.
cd "$(dirname "$0")/.." || exit 1
for f in examples/*.json; do python3 scripts/build-scene.py "$f" "${f%.json}.html" || exit 1; done
