#!/bin/bash

set -ex

cd "${0%/*}/.."

function run() {
  echo "Starting run for $1"
  if [ ! -e "$PWD/build/bench.$1" ]; then
    rm "$PWD/build/bench.$1.tmp" || true
    for I in $(seq 1 3); do
      for f in "$PWD/build/benchmarks.$1/"*; do
        "$f"
      done
    done | tee "$PWD/build/bench.$1.tmp"
    mv "$PWD/build/bench.$1.tmp" "$PWD/build/bench.$1"
  fi
  echo "Finished run for $1"
}

A="$(git rev-parse --short --verify "$1")"
B="$(git rev-parse --short --verify "$2")"

run "$A"
run "$B"

~/gocode/bin/benchcmp -best "$PWD/build/bench.$A" "$PWD/build/bench.$B"
