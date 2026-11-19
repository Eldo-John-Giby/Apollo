"""Verify an extracted Apollo bundle using only Python's standard library."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def safe_name(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Invalid bundle path')
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('Unsafe bundle path')
    reserved = {'con', 'prn', 'aux', 'nul', *('com'+str(n) for n in range(1,10)),
                *('lpt'+str(n) for n in range(1,10))}
    if any(ord(c)<32 or c in '<>"|?*' for c in name):
        raise ValueError('Nonportable bundle path')
    if any(part.endswith((' ', '.')) or part.split('.')[0].casefold() in reserved for part in path.parts):
        raise ValueError('Nonportable bundle path')
    return name


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def payload(root, name):
    name = safe_name(name)
    root = Path(root).resolve()
    path = root.joinpath(*name.split('/'))
    if not path.resolve().is_relative_to(root):
        raise ValueError('Bundle path escapes its root: ' + name)
    if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root):
        raise ValueError('Symbolic links are not bundle payloads: ' + name)
    if not path.is_file():
        raise ValueError('Missing bundle payload: ' + name)
    return path


def verify(root, reject_extra=False):
    root = Path(root).resolve()
    manifest = json.loads(payload(root, 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 1 or not isinstance(manifest.get('sha256'), dict) or not manifest['sha256']:
        raise ValueError('Invalid bundle manifest')
    entries = manifest['sha256']
    if 'manifest.json' in entries:
        raise ValueError('Manifest cannot hash itself')
    folded = set()
    for name, expected in entries.items():
        safe_name(name)
        if name.casefold() in folded:
            raise ValueError('Case-colliding bundle paths')
        folded.add(name.casefold())
        if (not isinstance(expected, str) or len(expected) != 64
                or any(c not in '0123456789abcdef' for c in expected)):
            raise ValueError('Invalid SHA-256: ' + name)
        if sha(payload(root, name)) != expected:
            raise ValueError('Changed bundle payload: ' + name)
    if reject_extra:
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
        if actual != set(entries) | {'manifest.json'}:
            raise ValueError('Unexpected bundle files')
    return dict(status='passed_bundle_file_integrity', files=len(entries),
                manifest_sha256=sha(root/'manifest.json'),
                qualification=manifest.get('qualification'),
                release_ready=manifest.get('release_ready') is True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--reject-extra', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.reject_extra), indent=2))
