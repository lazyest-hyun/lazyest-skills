#!/usr/bin/env python3
"""Scan every reachable Git blob; report paths/object IDs without secret values."""
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
patterns = [
    re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(rb'github_pat_[A-Za-z0-9_]{40,}'),
    re.compile(rb'AKIA[A-Z0-9]{16}'),
    re.compile(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    re.compile(rb'sk-[A-Za-z0-9_-]{30,}'),
    re.compile(rb'https?://[^\s/]+:[^\s/]+@'),
]
objects = subprocess.check_output(
    ['git', '-C', str(root), 'rev-list', '--objects', '--all'], text=True).splitlines()
count = 0
failures = []
for entry in objects:
    object_id, _, path = entry.partition(' ')
    kind = subprocess.check_output(
        ['git', '-C', str(root), 'cat-file', '-t', object_id], text=True).strip()
    if kind != 'blob':
        continue
    count += 1
    data = subprocess.check_output(['git', '-C', str(root), 'cat-file', 'blob', object_id])
    name = Path(path).name
    if (name.startswith('.env') or Path(path).suffix.lower() in {'.pdf', '.pem', '.key', '.p12', '.sqlite', '.db'}
            or any(pattern.search(data) for pattern in patterns)):
        failures.append((object_id, path))
if not count:
    raise SystemExit('FAIL: no committed blobs scanned')
for object_id, path in failures:
    print(f'REVIEW: {object_id} {path}')
if failures:
    raise SystemExit(1)
print(f'PASS: {count} reachable Git blobs; no configured secret patterns or forbidden file types')
print('Manual privacy review is still required; pattern scanning cannot prove absence of every secret.')
