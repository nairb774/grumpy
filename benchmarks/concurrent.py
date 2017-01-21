# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Benchmarks for simple parallel calculations."""

import threading

import weetest

try:
  from __go__.runtime import GOMAXPROCS
except:
  GOMAXPROCS = lambda _: 13


def Arithmetic(n):
  return n * 3 + 2


def Fib(n):
  if n < 2:
    return 1
  return Fib(n - 1) + Fib(n - 2)


_WORKLOADS = [
    (Arithmetic, 1001),
    (Fib, 10),
]


def _MakeParallelBenchmark(p, work_func, *args):
  """Create and return a benchmark that runs work_func p times in parallel."""
  def Benchmark(b):  # pylint: disable=missing-docstring
    b.SetParallelism(p)
    def Target(pb):
      while pb.Next():
        work_func(*args)
    b.RunParallel(Target)
  return Benchmark


def _RegisterBenchmarks():
  for p in xrange(1, GOMAXPROCS(0)+1):
    for work_func, arg in _WORKLOADS:
      name = 'Benchmark' + work_func.__name__
      if p > 1:
        name += 'Parallel%s' % p
      globals()[name] = _MakeParallelBenchmark(p, work_func, arg)
_RegisterBenchmarks()


if __name__ == '__main__':
  weetest.RunBenchmarks()
