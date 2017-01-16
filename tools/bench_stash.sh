#!/bin/bash

set -ex

cd "${0%/*}/.."

make -j12 -k benchmarks

OUT="$PWD/build/benchmarks.$(git rev-parse --short --verify HEAD)"
rm -rf "$OUT"
mkdir "$OUT"
find "$PWD/build/benchmarks/" -executable -type f -exec cp '{}' "$OUT" ';'
