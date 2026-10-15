#!/usr/bin/env python3
"""Validate a saved CSV patch against its baseline before rendering offline HTML."""
import argparse
import html
import json
import sys

import patch

MAX_HTML_BYTES = 16 * 1024 * 1024


def render(baseline, plan):
    # This verifies baseline bytes, every before-row and the complete result digest.
    # No CSV is written; the same saved plan can later be passed to patch.py apply.
    result = patch.apply(baseline, plan)
    esc = lambda value: html.escape(str(value), quote=True)
    parts = []
    size = 0

    def add(text):
        nonlocal size
        size += len(text.encode('utf-8'))
        if size > MAX_HTML_BYTES:
            raise ValueError('review exceeds 16 MiB HTML limit')
        parts.append(text)

    add('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Validated CSV patch</title><style>body{font:16px/1.5 system-ui;margin:2rem;max-width:100ch}pre{white-space:pre-wrap;overflow-wrap:anywhere}section{border-top:1px solid #888;padding:1rem 0}dt{font-weight:bold}dd{margin:0 0 1rem;overflow-wrap:anywhere}</style></head><body>
<h1>Validated CSV patch</h1><p>The supplied baseline and complete result match the saved patch fingerprints. This page prepares no files and sends nothing.</p><dl>''')
    for label, value in [('Baseline SHA-256', plan['baseline_sha256']),
                         ('Result SHA-256', plan['result_sha256']),
                         ('Key columns', json.dumps(plan['keys'], ensure_ascii=False)),
                         ('Operations', len(plan['operations'])), ('Result bytes', len(result))]:
        add('<dt>' + label + '</dt><dd>' + esc(value) + '</dd>')
    add('</dl><p>Fingerprints detect stale or inconsistent content; they do not authenticate a reviewer. Apply the same saved JSON against the same baseline after review. Values are literal strings.</p>')
    if not plan['operations']:
        add('<p>No row changes. Output formatting may still be normalized.</p>')
    for index, op in enumerate(plan['operations'], 1):
        kind = 'Add' if op['before'] is None else 'Remove' if op['after'] is None else 'Change'
        add(f'<section><h2>{kind} · {index}</h2>')
        for label in ('before', 'after'):
            value = 'Row absent' if op[label] is None else json.dumps(op[label], ensure_ascii=False, indent=2)
            add('<h3>' + label.title() + '</h3><pre>' + esc(value) + '</pre>')
        add('</section>')
    add('</body></html>\n')
    return ''.join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('baseline', help='workspace CSV whose exact bytes were reviewed')
    parser.add_argument('plan', help='saved csv-patch/v1 JSON inside the workspace')
    args = parser.parse_args(argv)
    try:
        plan = json.loads(patch.read_local(args.plan, patch.MAX_PLAN_BYTES),
                          object_pairs_hook=patch.unique_object)
        output = render(args.baseline, plan)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2
    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
