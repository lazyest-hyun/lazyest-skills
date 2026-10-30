#!/usr/bin/env python3
"""Copy one public skill into a project's Codex discovery directory."""
import argparse
import os
from pathlib import Path
import shutil
import tempfile

GUIDE = '''<!-- lazyest-skill-discovery:start -->
For substantial implementation under a deadline, inspect only the name/description frontmatter of project skills in `.agents/skills/*/SKILL.md` and select the relevant skill. For trivial local text edits, work directly. Read the selected body and only conditionally needed references. Preserve other project instructions and assessment restrictions.
<!-- lazyest-skill-discovery:end -->
'''

def write_guide_atomic(path, content):
    mode = path.stat().st_mode & 0o777 if path.exists() else None
    if mode is not None and (not mode & 0o222 or not os.access(path, os.W_OK)):
        raise PermissionError(f'Project guide is not writable: {path}')
    descriptor, temporary = tempfile.mkstemp(prefix='.lazyest-guide-', dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(content)
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)

def install(project, project_guide=True):
    source = Path(__file__).resolve().parents[1] / 'skills' / 'ship-small'
    target = Path(project).resolve() / '.agents' / 'skills' / source.name
    for parent in (target.parent.parent, target.parent):
        if parent.is_symlink():
            raise ValueError(f'Refusing symlinked install parent: {parent}')
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'Refusing to overwrite existing installation: {target}. Inspect it or use a fresh project; no files were changed.')
    guide_path = Path(project).resolve() / 'AGENTS.md'
    guide_text = ''
    if project_guide:
        if guide_path.is_symlink() or (guide_path.exists() and not guide_path.is_file()):
            raise ValueError(f'Refusing nonregular project guide: {guide_path}')
        guide_text = guide_path.read_text() if guide_path.exists() else ''
    target.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        target.mkdir()  # Exclusive creation: rollback never removes a pre-existing install.
        created = True
        shutil.copytree(source, target, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if project_guide and '<!-- lazyest-skill-discovery:start -->' not in guide_text:
            current = guide_path.read_text() if guide_path.exists() else ''
            if current != guide_text:
                raise RuntimeError(f'Project guide changed during installation: {guide_path}')
            write_guide_atomic(guide_path, guide_text + ('\n\n' if guide_text else '') + GUIDE)
    except Exception as error:
        if created:
            try:
                shutil.rmtree(target)
            except OSError as rollback_error:
                raise RuntimeError(f'Installation failed; partial installation remains at {target}. '
                                   f'Rollback failed: {rollback_error}. Original error: {error}') from error
        raise
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--no-project-guide', action='store_true', help='Skip the small discovery hint in AGENTS.md')
    args = parser.parse_args()
    print(install(args.project, project_guide=not args.no_project_guide))
