#!/usr/bin/env python3
"""Copy one public skill into a project's Codex discovery directory."""
import argparse
from pathlib import Path
import shutil

GUIDE = '''<!-- lazyest-skill-discovery:start -->
For substantial implementation under a deadline, inspect only the name/description frontmatter of project skills in `.agents/skills/*/SKILL.md` and select the relevant skill. For trivial local text edits, work directly. Read the selected body and only conditionally needed references. Preserve other project instructions and assessment restrictions.
<!-- lazyest-skill-discovery:end -->
'''

def install(project, project_guide=True):
    source = Path(__file__).resolve().parents[1] / 'skills' / 'ship-small'
    target = Path(project).resolve() / '.agents' / 'skills' / source.name
    for parent in (target.parent.parent, target.parent):
        if parent.is_symlink():
            raise ValueError(f'Refusing symlinked install parent: {parent}')
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'Refusing to overwrite: {target}')
    guide_path = Path(project).resolve() / 'AGENTS.md'
    guide_text = ''
    if project_guide:
        if guide_path.is_symlink() or (guide_path.exists() and not guide_path.is_file()):
            raise ValueError(f'Refusing nonregular project guide: {guide_path}')
        guide_text = guide_path.read_text() if guide_path.exists() else ''
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    if project_guide and '<!-- lazyest-skill-discovery:start -->' not in guide_text:
        guide_path.write_text(guide_text + ('\n\n' if guide_text else '') + GUIDE)
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--no-project-guide', action='store_true', help='Skip the small discovery hint in AGENTS.md')
    args = parser.parse_args()
    print(install(args.project, project_guide=not args.no_project_guide))
