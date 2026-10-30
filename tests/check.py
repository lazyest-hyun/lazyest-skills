#!/usr/bin/env python3
"""Offline structural and install checks; no model/API calls."""
import importlib.util
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True

root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'ship-small'
body = (skill / 'SKILL.md').read_text()
assert body.startswith('---\nname: ship-small\ndescription: ')
assert len(body.encode()) < 6500
for document in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)', document.read_text()):
        if not link.startswith(('https://', 'http://', '#')):
            assert (document.parent / link.split('#')[0]).is_file(), (document, link)
for path in root.rglob('*'):
    if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
        continue
    assert path.suffix not in {'.pem', '.key', '.pdf'}
    assert not path.name.startswith('.env')
    text = path.read_text()
    assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)', text), path
spec = importlib.util.spec_from_file_location('install', root / 'scripts' / 'install.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as directory:
    original = '# Existing project instruction\nPreserve this exact content.\n'
    (Path(directory) / 'AGENTS.md').write_text(original)
    installed = module.install(directory)
    guide = (Path(directory) / 'AGENTS.md').read_text()
    assert guide.startswith(original)
    assert guide.count('<!-- lazyest-skill-discovery:start -->') == 1
    assert (installed / 'SKILL.md').read_bytes() == (skill / 'SKILL.md').read_bytes()
    assert len(list(installed.rglob('*.md'))) == len(list(skill.rglob('*.md')))
    try:
        module.install(directory)
    except FileExistsError:
        pass
    else:
        raise AssertionError('Existing install was overwritten')
with tempfile.TemporaryDirectory() as directory:
    project = Path(directory) / 'project'
    outside = Path(directory) / 'outside'
    project.mkdir()
    outside.mkdir()
    (project / '.agents').symlink_to(outside, target_is_directory=True)
    try:
        module.install(project)
    except ValueError:
        pass
    else:
        raise AssertionError('Symlinked parent accepted')
    assert not list(outside.iterdir())
with tempfile.TemporaryDirectory() as directory:
    module.install(directory, project_guide=False)
    assert not (Path(directory) / 'AGENTS.md').exists()
print('PASS: structure, relative links, bounded core, secret-pattern scan, install and overwrite refusal')
