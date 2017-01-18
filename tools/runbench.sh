#!/bin/bash

# set -ex

cd "${0%/*}/.."

function run1() {
  echo "Starting run for $1"
  for f in "$PWD/build/benchmarks.$1/"*; do
    "$f" || exit
  done | tee >(gzip -9 - > "$PWD/build/bench.$1.tmp")
  echo "Finished run for $1"
  cat "$PWD/build/bench.$1.tmp" >> "$PWD/build/bench.$1"
}

A="$(git rev-parse --short --verify "$1")"
B="$(git rev-parse --short --verify "$2")"

for I in $(seq 1 3); do
  run1 "$A"
  run1 "$B"
done

~/gocode/bin/benchcmp -best \
    <(gzip -d "$PWD/build/bench.$A") \
    <(gzip -d "$PWD/build/bench.$B")
