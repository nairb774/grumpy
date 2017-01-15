#!/usr/bin/env python

import difflib
import itertools
import os
import re
import sys

cwd = os.getcwd()

asm_line = re.compile(
    r'\t0x(?P<hexPC>[\da-f]{4}) '
    r'(?P<decPC>\d{5}) '
    r'\((?P<lineno>[^)]+)\)\t'
    r'(?P<ins>[A-Z.]+)'
    r'(?:\t(?P<args>.+))?')

autotmp = re.compile(r'""\.autotmp_\d+(?=\+\d+\(SP\))')

dump_line = re.compile(r'\t0x[\da-f]{4}(?: [\da-f]{2}){,16}(?:   ){,15}  .+')


def maybe_int(i):
  try:
    return int(i)
  except ValueError:
    return i


class Block(object):
  def __init__(self, head, ins):
    self.name = head.partition(' t=')[0]
    self.head = head

    if ins:
      self.min_line = min_line = min(i.lineno for i in ins)
    else:
      self.min_line = min_line = 0

    targets = {maybe_int(i.args[0]) for i in ins if i.is_jump}
    self.targets = targets = {t for t in targets if isinstance(t, int)}

    all_ins = []
    for idx, i in enumerate(ins):
      i.rel_lineno = i.lineno - min_line
      if i.pc in targets and (not idx or ins[idx-1].pc != i.pc):
        j = Ins(i.pc, '%s:%d' % (i.file, i.lineno), '..IN..', '')
        j.rel_lineno = i.rel_lineno
        j.is_target = True
        all_ins.append(j)
      all_ins.append(i)
    self.ins = all_ins


class Ins(object):
  rel_lineno = 0
  is_likely_jump = -1
  is_target = False

  def __init__(self, pc, lineno, ins, args):
    self.pc = pc
    self.file, _, lineno = lineno.replace(cwd, '').rpartition(':')
    self.lineno = int(lineno)
    self.ins = ins
    self.is_jump = self.ins in (
        'JCC', 'JCS', 'JEQ', 'JGE', 'JGT', 'JHI', 'JLE', 'JLS', 'JLT', 'JMP',
        'JNE', 'JPC', 'JPS',
    )

    if args:
      args = args.split(', ')
    else:
      args = ()

    if self.is_jump and args[0] in ('$0', '$1'):
      self.is_likely_jump = int(args[0][1])
      args = args[1:]

    self.args = tuple(autotmp.sub("autotmp", a) for a in args)

    if not self.is_jump and self.ins.startswith('J'):
      try:
        int(self.args)
      except ValueError:
        pass
      else:
        raise Exception('possible jump ins: %s' % self.ins)

  def __hash__(self):
    h = hash(self.rel_lineno) ^ hash(self.ins) ^ hash(self.is_target)
    if CMP_ARGS and not self.is_jump:
      h ^= hash(self.args)
    return h

  def __eq__(self, other):
    return (
        self.ins == other.ins
        and self.rel_lineno == other.rel_lineno 
        and self.is_target == other.is_target
        and self.is_jump == other.is_jump
        and (not CMP_ARGS or self.is_jump or self.args == other.args))


CMP_ARGS = False


def parse_file(f):
  blocks = {}
  head = None
  ins = []

  def add_block():
    if not head:
      return
    b = Block(head, ins)
    if b.name in blocks:
      raise Exception(b.name)
    blocks[b.name] = b

  for l in f:
    l = l[:-1]
    if not l.startswith('\t'):
      add_block()
      head, ins = l, []
    elif not l.startswith('\trel ') and not dump_line.match(l):
      parts = asm_line.match(l)
      ins.append(Ins(
          int(parts.group('decPC')), parts.group('lineno'), parts.group('ins'),
          parts.group('args')))

  add_block()
  return blocks


def gen_matched(sm):
  izip = itertools.izip
  for a, b, size in sm.get_matching_blocks():
    for v in izip(sm.a[a:a+size], sm.b[b:b+size]):
      yield v


def print_ins(out, ins, targets):
  for idx, i in enumerate(ins):
    pc = ''
    if i.pc in targets and (not idx or ins[idx-1].pc != i.pc):
      pc = targets[i.pc]

    v = '%5s (%s:%i)\t%s' % (pc, i.file, i.rel_lineno, i.ins)

    args = i.args
    if args:
      if i.is_jump:
        to = targets.get(maybe_int(i.args[0]))
        if to is not None:
          args = (str(to),) + args[1:]
      v += '\t%s' % ', '.join(args)

    print >>out, v


def main():
  with open(sys.argv[1], 'r') as f:
    f1 = parse_file(f)
  with open(sys.argv[2], 'r') as f:
    f2 = parse_file(f)

  with open(sys.argv[3], 'w') as lf, open(sys.argv[4], 'w') as rf:
    for name in sorted(set(f1) | set(f2)):
      lBlock, rBlock = f1.get(name), f2.get(name)
      if not lBlock:
        print name, 'missing in', sys.argv[1]
        continue
      if not rBlock:
        print name, 'missing in', sys.argv[2]
        continue

      sm = difflib.SequenceMatcher(a=lBlock.ins, b=rBlock.ins, autojunk=False)
      pairs = {r.pc: l.pc for l, r in gen_matched(sm) if l.is_target}
      l_idxs = {l: idx for idx, l in enumerate(sorted(lBlock.targets))}
      r_idxs = {r: l_idxs[pairs[r]] for r in rBlock.targets if r in pairs}
      r_idxs.update(
          (r, idx) for idx, r in enumerate(sorted(
              r for r in rBlock.targets if r not in pairs), start=len(l_idxs)))

      print >>lf, lBlock.head
      print_ins(lf, lBlock.ins, l_idxs)

      print >>rf, rBlock.head
      print_ins(rf, rBlock.ins, r_idxs)


if __name__ == '__main__':
  main()
