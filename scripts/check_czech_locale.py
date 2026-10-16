"""Offline Czech release gate. Never publish a partial or stale translation."""
import argparse
import hashlib
import json
from pathlib import Path


def audit(root):
    folder = root / 'content/localization'
    config = json.loads((folder / 'cs-rollout.json').read_text())
    rows = json.loads((folder / 'cs-translations.json').read_text())
    errors = []
    if config['order'][:3] != ['pl', 'en', 'cs']:
        errors.append('Czech must be third, after Polish and English')
    if len({row['id'] for row in rows}) != len(rows):
        errors.append('Duplicate translation IDs')
    pending = []
    for row in rows:
        if row['id'] != hashlib.sha256(row['source'].encode()).hexdigest()[:16]:
            errors.append('Translation source changed: ' + row['id'])
        if not row.get('reviewed') or not (row.get('translation') or '').strip():
            pending.append(row['id'])
    for name, expected in config['sourcePages'].items():
        page = root / name
        if not page.is_file() or hashlib.sha256(page.read_bytes()).hexdigest() != expected:
            errors.append('Source page changed: ' + name)
    if pending:
        errors.append(f'{len(pending)} translations still require completion and review')
    # Full content coverage alone cannot authorize publishing legal PDFs or booking claims.
    for requirement in ['legalHtmlAndPdfVerified', 'routeAndLanguageTestsPassed',
                        'externalBookingLanguageDisclosed']:
        if config.get(requirement) is not True:
            errors.append('Not verified: ' + requirement)
    return {'language': 'cs', 'thirdPosition': config['order'][2] == 'cs',
            'strings': len(rows), 'reviewed': len(rows) - len(pending),
            'pending': len(pending), 'errors': errors,
            'publicationReady': not errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(Path(__file__).resolve().parent.parent)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['publicationReady'] else 1)
