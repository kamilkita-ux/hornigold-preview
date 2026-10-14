"""Read aggregate page views with GET only; never generate analytics test events."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = next((parent for parent in Path(__file__).resolve().parents
             if (parent / 'release.json').is_file() and (parent / 'site').is_dir()), None)


def compare(current, previous=None):
    if current.get('metric') != 'pageviews':
        raise ValueError('Unexpected counter metric')
    if type(current.get('total')) is not int or current['total'] < 0:
        raise ValueError('Invalid aggregate total')
    datetime.date.fromisoformat(current['startedAt'])
    if previous is None:
        return {'state': 'baseline', 'pageviewsSincePreviousCheck': None}
    if previous['counter']['startedAt'] != current['startedAt']:
        return {'state': 'counter_period_changed', 'pageviewsSincePreviousCheck': None}
    difference = current['total'] - previous['counter']['total']
    if difference < 0:
        return {'state': 'counter_decreased', 'pageviewsSincePreviousCheck': None}
    return {'state': 'observed', 'pageviewsSincePreviousCheck': difference,
            'previousCheckedAt': previous['checkedAt']}


def get_json(path):
    # No cookie jar, consent, client JS, POST, booking or payment request.
    result = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--max-time', '25',
                             'https://hornigold.pl/' + path], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    folder = args.output_directory.resolve()
    if ROOT is not None and (folder == ROOT or ROOT in folder.parents):
        raise SystemExit('Traffic snapshots must stay outside the public source repository')
    folder.mkdir(parents=True, exist_ok=True)
    latest = folder / 'latest.json'
    previous = json.loads(latest.read_text()) if latest.exists() else None
    raw_counter, release = get_json('api/site-stats'), get_json('release.json')
    counter = {key: raw_counter.get(key) for key in ['total', 'startedAt', 'metric']}
    now = datetime.datetime.now(datetime.timezone.utc)
    report = {'checkedAt': now.isoformat(), 'checkedAtWarsaw': now.astimezone(ZoneInfo('Europe/Warsaw')).isoformat(),
              'source': 'https://hornigold.pl/api/site-stats', 'counter': counter,
              'release': {key: release.get(key) for key in ['revision', 'commit']},
              **compare(counter, previous),
              'limits': ['Page views, not unique visitors, customers or reservations.',
                         'Reloads and QA visits may increase this counter.',
                         'GA4 covers consented measured traffic; counter and GA4 totals are not equivalent.',
                         'Revenue and confirmed bookings are not inferred.']}
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    snapshot = folder / (now.strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    snapshot.write_text(text)
    latest.write_text(text)
    if json.loads(latest.read_text()) != report:
        raise RuntimeError('Saved traffic snapshot could not be verified')
    print(json.dumps({'state': report['state'], 'totalPageviews': counter['total'],
                      'pageviewsSincePreviousCheck': report['pageviewsSincePreviousCheck'],
                      'report': str(snapshot)}))
    return 1 if report['state'] in ['counter_period_changed', 'counter_decreased'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
