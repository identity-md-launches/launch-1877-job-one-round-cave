"""Exercise review validation against real handoffs and hostile/stale input."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch as mock

import patch
import patch_review
import drift


class PatchReviewTests(unittest.TestCase):
    def setUp(self):
        root = Path('test/scratch')
        root.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def csv(self, name, text):
        p = self.root / name
        p.write_text(text, encoding='utf-8', newline='')
        return p

    def test_import_snapshot_handoff(self):
        before = Path('shared/import-drift/observed-sentry.csv')
        after = Path('shared/import-drift/observed-sentry23.csv')
        plan = patch.plan(before, after, ['module'])
        self.assertEqual(len(plan['operations']), 1)
        output = self.csv('applied.csv', patch.apply(before, plan).decode())
        self.assertTrue(drift.compare(output, after)['equal'])
        page = patch_review.render(before, plan)
        self.assertIn('unittest import mock', page)
        self.assertIn(plan['result_sha256'], page)

    def test_real_token_snapshot_exact_integer_change(self):
        before = Path('shared/token-read-plan/observed.csv')
        raw = before.read_text()
        # This scratch-only edit is an illustrative one-base-unit change.
        old = '1000000000000000000000000000'
        self.assertIn(old, raw)
        after = self.csv('token.csv', raw.replace(old, str(int(old) + 1)))
        plan = patch.plan(before, after, ['chain_id', 'token_address', 'field'])
        self.assertEqual(len(plan['operations']), 1)
        page = patch_review.render(before, plan)
        self.assertIn(str(int(old) + 1), page)
        self.assertIn('0xd782bdea4ef02a0bd391eb9089470c8080f0a68e', page)

    def test_stale_baseline_and_tampered_patch_refused(self):
        a = self.csv('a.csv', 'id,v\na,1\n')
        b = self.csv('b.csv', 'id,v\na,2\n')
        plan = patch.plan(a, b, ['id'])
        bad = copy.deepcopy(plan)
        bad['operations'][0]['after']['v'] = '3'
        with self.assertRaisesRegex(ValueError, 'result digest'):
            patch_review.render(a, bad)
        a.write_bytes(a.read_bytes().replace(b'\n', b'\r\n'))
        with self.assertRaisesRegex(ValueError, 'baseline changed'):
            patch_review.render(a, plan)

    def test_inert_html_and_absent_rows(self):
        a = self.csv('a.csv', 'id,v\na,old\nb,remove\n')
        b = self.csv('b.csv', 'id,v\na,<script>alert(1)</script>\nc,add\n')
        page = patch_review.render(a, patch.plan(a, b, ['id']))
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('Row absent', page)
        self.assertIn('Add ·', page)
        self.assertIn('Remove ·', page)
        self.assertIn('Change ·', page)

    def test_cli_no_partial_output_on_error_or_duplicate_json(self):
        a = self.csv('a.csv', 'id,v\na,1\n')
        b = self.csv('b.csv', 'id,v\na,2\n')
        plan = patch.plan(a, b, ['id'])
        p = self.csv('plan.json', json.dumps(plan))
        for text, status in [(json.dumps(plan), 0), ('{"format":1,"format":2}', 2), ('{}', 2)]:
            p.write_text(text)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(patch_review.main([str(a), str(p)]), status)
            if status == 0:
                self.assertTrue(out.getvalue().startswith('<!doctype html>'))
                self.assertEqual(err.getvalue(), '')
            else:
                self.assertEqual(out.getvalue(), '')
                self.assertIn('error', json.loads(err.getvalue()))

    def test_noop_header_only_and_output_limit(self):
        a = self.csv('empty.csv', 'id,v\n')
        plan = patch.plan(a, a, ['id'])
        self.assertIn('No row changes', patch_review.render(a, plan))
        with mock.object(patch_review, 'MAX_HTML_BYTES', 100):
            with self.assertRaisesRegex(ValueError, 'HTML limit'):
                patch_review.render(a, plan)


if __name__ == '__main__':
    unittest.main()
