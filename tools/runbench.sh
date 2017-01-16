#!/bin/bash

set -ex

cd "${0%/*}/.."

A="$PWD/build/benchmarks.$(git rev-parse --short --verify "$1")"
B="$PWD/build/benchmarks.$(git rev-parse --short --verify "$2")"

for f in "$A/"*; do
  "$PWD/tools/benchcmp" "$f" "$B/$(basename "$f")"
done
