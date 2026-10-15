import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import burst_sentry as b


def observation(ok=True, status=200, error=None):
    probe = {'schema': 'endpoint-sentry/v1', 'ok': ok,
             'hops': [{'status': status, 'body_sha256': 'a' * 64}],
             'checks': [{'name': 'status', 'ok': status == 200}]}
    if error:
        probe['error'] = {'kind': error}
    return {'ok': ok, 'probe': probe}, 0 if ok else 1


class BurstTests(unittest.TestCase):
    def run_burst(self, results, count=3):
        calls = []
        def supervise(command, allowance):
            calls.append((list(command), allowance))
            return copy.deepcopy(results[len(calls) - 1])
        report = b.burst(['fixed', 'command'], {'status': 200}, count, 12, 3, supervise)
        return report, calls

    def test_mixed_retains_all_attempts_same_command(self):
        report, calls = self.run_burst([observation(), observation(False, 503), observation()])
        self.assertFalse(report['ok'])
        self.assertEqual(report['summary']['verdict'], 'mixed')
        self.assertEqual(report['summary']['health_transitions'], 2)
        self.assertEqual(report['summary']['failure_kind_counts'], {'check:status': 1})
        self.assertEqual(report['summary']['last_hop_status_counts'], {'200': 2, '503': 1})
        self.assertEqual([c[0] for c in calls], [['fixed', 'command']] * 3)
        self.assertEqual([s['number'] for s in report['samples']], [1, 2, 3])

    def test_body_hash_changes_are_not_failures(self):
        observations = [observation(), observation(), observation()]
        observations[1][0]['probe']['hops'][0]['body_sha256'] = 'b' * 64
        report, _ = self.run_burst(observations)
        self.assertTrue(report['ok'])
        self.assertEqual(report['summary']['verdict'], 'all_passed')

    def test_all_failed_distinct_causes(self):
        report, _ = self.run_burst([observation(False, 503), observation(False, error='dns'),
                                   ({'ok': False, 'error': {'kind': 'deadline'}}, 1)])
        self.assertEqual(report['summary']['verdict'], 'all_failed')
        self.assertEqual(report['summary']['failure_kind_counts'],
                         {'check:status': 1, 'dns': 1, 'deadline': 1})

    def test_budget_caps_last_attempt_and_keeps_missing_count(self):
        clock = [0.0]
        allowances = []
        def supervise(command, allowance):
            allowances.append(allowance)
            clock[0] += allowance
            return {'ok': False, 'error': {'kind': 'deadline'}}, 1
        report = b.burst([], {}, 3, 1, .75, supervise, clock=lambda: clock[0])
        self.assertEqual(allowances, [.75, .25])
        self.assertEqual(report['summary']['verdict'], 'incomplete')
        self.assertEqual(report['summary']['not_attempted'], 1)
        self.assertEqual(report['stop_reason'], 'total_budget_exhausted')
        self.assertFalse(report['ok'])

    def test_zero_attempts_cannot_pass(self):
        times = iter([0, 2, 2])
        report = b.burst([], {}, 3, 1, 1, lambda *_: self.fail('must not start'),
                         clock=lambda: next(times))
        self.assertEqual(report['summary']['attempted'], 0)
        self.assertFalse(report['ok'])

    def test_worker_error_stops_without_repeating(self):
        for kind, code in [('arguments', 2), ('worker_protocol', 1), ('worker_start', 1)]:
            report, calls = self.run_burst([({'ok': False, 'error': {'kind': kind}}, code)])
            self.assertEqual(len(calls), 1)
            self.assertEqual(report['stop_reason'], 'worker_error')
            self.assertFalse(report['ok'])

    def test_real_stalled_process_killed_for_each_attempt(self):
        watchdog = b.sibling('deadline-sentry', 'deadline_sentry.py')
        command = [sys.executable, '-I', '-B', '-c',
                   'import time; print(\'{"ok":true}\', flush=True); time.sleep(30)']
        report = b.burst(command, {}, 2, 2, .08, watchdog.supervise)
        self.assertEqual(report['summary']['failed'], 2)
        self.assertEqual(report['summary']['failure_kind_counts'], {'deadline': 2})
        self.assertTrue(all(s['partial_report_discarded'] for s in report['samples']))
        self.assertTrue(all(s['worker_returncode'] is not None for s in report['samples']))

    def test_cli_validation_before_network(self):
        invalid = [['https://example.com:0/'], ['http://example.com'],
                   ['https://example.com', '--samples', '1'],
                   ['https://example.com', '--samples', '11'],
                   ['https://example.com', '--budget', 'nan'],
                   ['https://example.com', '--budget', '121'],
                   ['https://example.com', '--per-probe', '0'],
                   ['https://example.com', '--timeout', 'inf'],
                   ['https://example.com', '--max-bytes', '1048577'],
                   ['https://example.com', '--max-redirects', '-1'],
                   ['https://example.com', '--status', '600'],
                   ['https://example.com', '--expect-value', 'null'],
                   ['https://example.com', '--expect-path', 'items'],
                   ['https://example.com', '--expect-path', '/~2'],
                   ['https://example.com', '--expect-path', '', '--expect-value', 'NaN'],
                   ['https://example.com', '--expect-path', '', '--expect-value', '{"a":1,"a":2}']]
        for args in invalid:
            with self.subTest(args=args), patch.object(b, 'burst', side_effect=AssertionError('network')):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                    b.main(args)
                self.assertEqual(caught.exception.code, 2)

    def test_cli_exact_expectations_and_exit_codes(self):
        for ok, code in [(True, 0), (False, 1)]:
            calls = []
            class Watchdog:
                @staticmethod
                def supervise(command, allowance):
                    calls.append(command)
                    return observation(ok, 200 if ok else 503)
            original = b.sibling
            def sibling(folder, filename):
                return Watchdog if folder == 'deadline-sentry' else original(folder, filename)
            output = io.StringIO()
            with patch.object(b, 'sibling', side_effect=sibling), contextlib.redirect_stdout(output):
                actual = b.main(['https://example.com', '--samples', '2', '--json',
                                 '--expect-path', '', '--expect-value', 'false'])
            self.assertEqual(actual, code)
            report = json.loads(output.getvalue())
            self.assertIs(report['expectations']['value'], False)
            self.assertTrue(report['expectations']['compare_value'])
            self.assertEqual(calls[0], calls[1])
            self.assertEqual(calls[0][-4:], ['--expect-path', '', '--expect-value', 'false'])

    def test_cli_real_process_invalid_input(self):
        result = subprocess.run([sys.executable, '-I', '-B', str(Path(b.__file__)),
                                 'https://example.com:0'], capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('invalid port', result.stderr)


if __name__ == '__main__':
    unittest.main()
