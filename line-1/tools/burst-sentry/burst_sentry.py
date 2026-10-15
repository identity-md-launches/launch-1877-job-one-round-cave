#!/usr/bin/env python3
"""Diagnose intermittent public HTTPS failures with a bounded burst of GETs."""
import argparse
import datetime
import importlib.util
import json
import math
from pathlib import Path
import sys
import time


def sibling(folder, filename):
    path = Path(__file__).resolve().parent.parent / folder / filename
    spec = importlib.util.spec_from_file_location(folder.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summarize(samples, requested):
    """Failures include killed workers; absent attempts are never successes."""
    passed = sum(sample['ok'] for sample in samples)
    failed = len(samples) - passed
    complete = len(samples) == requested
    verdict = ('incomplete' if not complete else 'mixed' if passed and failed
               else 'all_passed' if passed else 'all_failed')
    kinds = {}
    statuses = {}
    for sample in samples:
        observation = sample.get('probe', sample)
        hops = observation.get('hops', [])
        if hops:
            status = str(hops[-1]['status'])
            statuses[status] = statuses.get(status, 0) + 1
        if not sample['ok']:
            kind = observation.get('error', {}).get('kind')
            labels = ([kind] if kind else
                      ['check:' + check['name'] for check in observation.get('checks', [])
                       if not check['ok']]) or ['unknown']
            for label in labels:
                kinds[label] = kinds.get(label, 0) + 1
    return {'verdict': verdict, 'complete': complete, 'requested': requested,
            'attempted': len(samples), 'passed': passed, 'failed': failed,
            'not_attempted': requested - len(samples),
            'health_transitions': sum(a['ok'] != b['ok'] for a, b in zip(samples, samples[1:])),
            'last_hop_status_counts': statuses, 'failure_kind_counts': kinds}


def burst(command, expectations, count, budget, per_probe, supervise, clock=time.monotonic):
    started = clock()
    samples = []
    stop_reason = 'requested_count_reached'
    for index in range(count):
        remaining = budget - (clock() - started)
        if remaining <= 0:
            stop_reason = 'total_budget_exhausted'
            break
        allowance = min(remaining, per_probe)
        result, code = supervise(command, allowance)
        result = dict(result)
        result.update(number=index + 1, budget_seconds=allowance, exit_code=code)
        samples.append(result)
        # Local argument/protocol errors cannot establish endpoint availability.
        if code == 2 or result.get('error', {}).get('kind') in ('worker_start', 'worker_protocol'):
            stop_reason = 'worker_error'
            break
    summary = summarize(samples, count)
    ok = summary['verdict'] == 'all_passed' and stop_reason != 'worker_error'
    return {'schema': 'burst-sentry/v1',
            'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'ok': ok, 'expectations': expectations,
            'limits': {'samples': count, 'total_seconds': budget, 'per_probe_seconds': per_probe},
            'elapsed_ms': round((clock() - started) * 1000, 3),
            'stop_reason': stop_reason, 'summary': summary, 'samples': samples}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('url', help='trusted public non-secret HTTPS GET URL')
    parser.add_argument('--samples', type=int, default=3, help='2..10 sequential observations (default 3)')
    parser.add_argument('--budget', type=float, default=12, help='total seconds, 0 < n <= 120')
    parser.add_argument('--per-probe', type=float, default=3, help='watchdog seconds per sample, 0 < n <= 15')
    parser.add_argument('--timeout', type=float, default=2, help='child socket/body seconds, 0 < n <= 15')
    parser.add_argument('--max-bytes', type=int, default=262144)
    parser.add_argument('--max-redirects', type=int, default=3)
    parser.add_argument('--status', type=int, default=200)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--expect-path')
    parser.add_argument('--expect-value', help='strict JSON value; requires --expect-path')
    args = parser.parse_args(argv)
    sentry = sibling('endpoint-sentry', 'sentry.py')
    watchdog = sibling('deadline-sentry', 'deadline_sentry.py')
    try:
        sentry.https_url(args.url)
        if not 2 <= args.samples <= 10:
            raise ValueError('samples must be between 2 and 10')
        for label, value, maximum in [('budget', args.budget, 120),
                                      ('per-probe', args.per_probe, 15),
                                      ('timeout', args.timeout, 15)]:
            if not math.isfinite(value) or not 0 < value <= maximum:
                raise ValueError(label + ' must be finite, positive and at most ' + str(maximum))
        if not 1 <= args.max_bytes <= 1048576:
            raise ValueError('max-bytes must be between 1 and 1048576')
        if not 0 <= args.max_redirects <= 10:
            raise ValueError('max-redirects must be between 0 and 10')
        if not 100 <= args.status <= 599:
            raise ValueError('status must be between 100 and 599')
        if args.expect_value is not None and args.expect_path is None:
            raise ValueError('--expect-value requires --expect-path')
        expected = (sentry.strict_json(args.expect_value.encode())
                    if args.expect_value is not None else None)
        if args.expect_path is not None:
            if args.expect_path and not args.expect_path.startswith('/'):
                raise ValueError('JSON pointer must be empty or start with /')
            for token in args.expect_path.split('/')[1:]:
                sentry.pointer({token.replace('~1', '/').replace('~0', '~'): None}, '/' + token)
    except (ValueError, UnicodeError, RecursionError) as error:
        parser.error(str(error))
    expectations = {'url': args.url, 'status': args.status,
                    'json': args.json or args.expect_path is not None,
                    'path': args.expect_path, 'compare_value': args.expect_value is not None,
                    'value': expected, 'timeout_seconds': args.timeout,
                    'max_bytes': args.max_bytes, 'max_redirects': args.max_redirects}
    command = [sys.executable, '-I', '-B', str(Path(sentry.__file__)), args.url,
               '--timeout', str(args.timeout), '--max-bytes', str(args.max_bytes),
               '--max-redirects', str(args.max_redirects), '--status', str(args.status)]
    if args.json:
        command.append('--json')
    if args.expect_path is not None:
        command += ['--expect-path', args.expect_path]
    if args.expect_value is not None:
        command += ['--expect-value', args.expect_value]
    report = burst(command, expectations, args.samples, args.budget, args.per_probe,
                   watchdog.supervise)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 2 if report['stop_reason'] == 'worker_error' else 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
