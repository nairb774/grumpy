#!/bin/bash

set -ex

cd "${0%/*}/.."

make -j12 -k build/runtime.pass
mkdir -p "$PWD/build/disasm"

OUT="$PWD/build/disasm/$(git rev-parse --short --verify HEAD)"
GOPATH=$PWD/build go build -gcflags=-S grumpy > "$OUT" 2>&1
