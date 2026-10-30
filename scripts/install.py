#!/usr/bin/env python3
"""Copy one public skill into a project's Codex discovery directory."""
import argparse
from pathlib import Path
import shutil

def install(project):
    source = Path(__file__).resolve().parents[1] / 'skills' / 'ship-small'
    target = Path(project).resolve() / '.agents' / 'skills' / source.name
    for parent in (target.parent.parent, target.parent):
        if parent.is_symlink():
            raise ValueError(f'Refusing symlinked install parent: {parent}')
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'Refusing to overwrite: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    args = parser.parse_args()
    print(install(args.project))
