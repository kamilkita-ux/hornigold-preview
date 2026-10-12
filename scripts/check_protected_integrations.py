"""Local-only integrity gate for explicitly identified protected integration files.

Never discovers credentials, modifies integrations or claims functional acceptance.
Keep the manifest outside the source tree; it contains hashes, not file contents.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys


def safe_path(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or str(rel) in ('', '.'):
        raise ValueError('Protected paths must be explicit relative paths, not the root.')
    path = root / rel
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Symlink in protected path; resolve ownership manually.')
    if not path.resolve().is_relative_to(root):
        raise ValueError('Protected path escapes root.')
    return path


def snapshot(root, selections):
    files = {}
    for entry in selections:
        path = safe_path(root, entry['path'])
        if entry['kind'] == 'file':
            if not path.is_file():
                raise ValueError('Missing protected file: ' + entry['path'])
            candidates = [path]
        elif entry['kind'] == 'directory':
            if not path.is_dir():
                raise ValueError('Missing protected directory: ' + entry['path'])
            candidates = list(path.rglob('*'))
        else:
            raise ValueError('Unknown protected path kind.')
        for candidate in candidates:
            safe_path(root, str(candidate.relative_to(root)))
            if candidate.is_file():
                files[candidate.relative_to(root).as_posix()] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    return dict(sorted(files.items()))


def capture(root, paths):
    selections = []
    for relative in paths:
        path = safe_path(root, relative)
        if not path.exists() or not (path.is_file() or path.is_dir()):
            raise ValueError('Protected selection does not exist: ' + relative)
        selections.append({'path': path.relative_to(root).as_posix(), 'kind': 'directory' if path.is_dir() else 'file'})
    if not selections:
        raise ValueError('No protected selections; refusing an empty protection claim.')
    files = snapshot(root, selections)
    if not files:
        raise ValueError('No protected files; refusing an empty protection claim.')
    return {'format': 1, 'selections': selections, 'files': files}


def compare(root, manifest):
    if manifest.get('format') != 1 or not manifest.get('selections') or not manifest.get('files'):
        raise ValueError('Invalid or empty baseline.')
    for relative, digest in manifest['files'].items():
        safe_path(root, relative)
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid baseline digest.')
    actual = snapshot(root, manifest['selections'])
    before = manifest['files']
    return {
        'changed': sorted(p for p in before.keys() & actual.keys() if before[p] != actual[p]),
        'removed': sorted(before.keys() - actual.keys()),
        'added': sorted(actual.keys() - before.keys()),
        'filesChecked': len(actual),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['capture', 'check'])
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--protect', action='append', default=[])
    opts = parser.parse_args()
    root = opts.root.resolve(strict=True)
    manifest = opts.manifest.absolute()
    if manifest.is_symlink() or manifest.resolve().is_relative_to(root):
        raise ValueError('Baseline must be outside the source tree and must not be a symlink.')
    if opts.mode == 'capture':
        data = capture(root, opts.protect)
        # Exclusive creation prevents replacing the trusted before-state after a change.
        with manifest.open('x', encoding='utf-8') as handle:
            os.chmod(manifest, 0o600)
            json.dump(data, handle, indent=2)
            handle.write('\n')
        if json.loads(manifest.read_text()) != data:
            raise ValueError('Baseline readback mismatch.')
        print(json.dumps({'captured': len(data['files']), 'modifiedIntegrationFiles': 0}))
        return 0
    if opts.protect:
        raise ValueError('Check uses the original baseline selections, not replacement selections.')
    result = compare(root, json.loads(manifest.read_text()))
    result['passed'] = not any(result[k] for k in ['changed', 'removed', 'added'])
    result['scope'] = 'Selected file bytes only; not remote configuration, PMS or payment acceptance.'
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}))
        sys.exit(1)
