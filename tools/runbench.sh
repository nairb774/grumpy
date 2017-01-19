#!/bin/bash

set -ex

cd "${0%/*}/.."

function run1() {
  echo "Starting run for $1"
  for f in "$PWD/build/benchmarks.$1/"*; do
    "$f"
  done | tee >(gzip -9 - > "$PWD/build/bench.$1.tmp")
  echo "Finished run for $1"
  cat "$PWD/build/bench.$1.tmp" >> "$PWD/build/bench.$1"
  rm "$PWD/build/bench.$1.tmp"
}

A="$(git rev-parse --short --verify "$1")"
B="$(git rev-parse --short --verify "$2")"

for I in $(seq 1 3); do
  run1 "$A"
  run1 "$B"
done

~/gocode/bin/benchcmp -best -changed \
    <(gzip -cd "$PWD/build/bench.$A") \
    <(gzip -cd "$PWD/build/bench.$B")
