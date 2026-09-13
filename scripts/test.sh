#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TESTSDIR="$ROOT_DIR/tests"
TESTFILE="$TESTSDIR/results.txt"

blender \
    -noaudio \
    --factory-startup \
    --background "$TESTSDIR/integration/test.blend" \
    --python-use-system-env \
    --python-exit-code 1 \
    --python "$TESTSDIR/register_addon.py" \
    --python "$TESTSDIR/test.py"

cat "$TESTFILE"

last_line=$(tail -n 1 "$TESTFILE")

if [[ "$last_line" == OK* ]]; then
    exit 0
else
    exit 1
fi
