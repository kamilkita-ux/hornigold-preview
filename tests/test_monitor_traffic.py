import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('traffic', Path(__file__).parents[1] / 'scripts/monitor_traffic.py')
traffic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(traffic)


class TrafficTests(unittest.TestCase):
    def test_initial_snapshot_does_not_invent_daily_traffic(self):
        result = traffic.compare({'metric': 'pageviews', 'total': 100, 'startedAt': '2026-10-05'})
        self.assertEqual(result['state'], 'baseline')
        self.assertIsNone(result['pageviewsSincePreviousCheck'])

    def test_delta_is_between_observations_not_automatically_a_day(self):
        previous = {'checkedAt': '2026-10-14T10:00:00Z', 'counter': {'total': 100, 'startedAt': '2026-10-05'}}
        result = traffic.compare({'metric': 'pageviews', 'total': 107, 'startedAt': '2026-10-05'}, previous)
        self.assertEqual(result['pageviewsSincePreviousCheck'], 7)
        self.assertEqual(result['previousCheckedAt'], previous['checkedAt'])

    def test_reset_does_not_become_negative_visitors(self):
        previous = {'counter': {'total': 100, 'startedAt': '2026-10-05'}}
        for counter, state in [({'total': 90, 'startedAt': '2026-10-05'}, 'counter_decreased'),
                               ({'total': 1, 'startedAt': '2026-10-14'}, 'counter_period_changed')]:
            result = traffic.compare({'metric': 'pageviews', **counter}, previous)
            self.assertEqual(result['state'], state)
            self.assertIsNone(result['pageviewsSincePreviousCheck'])

    def test_invalid_counter_or_wrong_metric_is_rejected(self):
        for current in [{'metric': 'users', 'total': 10, 'startedAt': '2026-10-05'},
                        {'metric': 'pageviews', 'total': True, 'startedAt': '2026-10-05'}]:
            with self.assertRaises(ValueError):
                traffic.compare(current)
