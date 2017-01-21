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

for I in $(seq 1 "$1"); do
  for H in $(git rev-list "$2"); do
    run1 "$(git rev-parse --short --verify "$H")"
  done
done
