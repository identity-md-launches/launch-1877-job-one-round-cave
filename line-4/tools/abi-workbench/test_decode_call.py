"""Independent calldata fixtures for offline selector and layout inspection."""
import contextlib
import io
import json
import unittest
from unittest.mock import patch

import abi_workbench as abi


def word(n):
    return n.to_bytes(32, 'big')


class DecodeCallTests(unittest.TestCase):
    def setUp(self):
        self.zto = '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'
        self.transfer = {'inputs': [{'name': 'to', 'type': 'address'},
                                    {'name': 'value', 'type': 'uint256'}]}
        self.payload = bytes.fromhex('a9059cbb') + bytes.fromhex(self.zto[2:]).rjust(32, b'\0') + word(12)

    def test_known_erc20_transfer_vector(self):
        args = abi.decode_call(self.transfer, 'transfer(address,uint256)', self.payload)
        self.assertEqual(args, [
            {'name': 'to', 'type': 'address', 'value': self.zto},
            {'name': 'value', 'type': 'uint256', 'value': 12},
        ])

    def test_rejects_wrong_or_missing_selector(self):
        for data in (self.payload[4:], bytes.fromhex('70a08231') + self.payload[4:], b''):
            with self.subTest(data=data[:4].hex()), self.assertRaisesRegex(ValueError, 'selector does not match'):
                abi.decode_call(self.transfer, 'transfer(address,uint256)', data)

    def test_rejects_surplus_and_truncated_argument_words(self):
        for data in (self.payload + word(0), self.payload[:-32]):
            with self.subTest(length=len(data)), self.assertRaises(ValueError):
                abi.decode_call(self.transfer, 'transfer(address,uint256)', data)

    def test_rejects_noncanonical_dynamic_offset(self):
        fn = {'inputs': [{'name': 'message', 'type': 'string'}]}
        selector = abi.keccak256(b'f(string)')[:4]
        # A gap before the string is readable in permissive mode, but not a
        # canonical call. The first offset must be one word (32 bytes).
        noncanonical = selector + word(64) + word(0) + word(1) + b'x'.ljust(32, b'\0')
        with self.assertRaisesRegex(ValueError, 'noncanonical calldata'):
            abi.decode_call(fn, 'f(string)', noncanonical)

    def test_cli_reads_known_calldata(self):
        raw = b'[{"type":"function","name":"transfer","inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"outputs":[{"type":"bool"}]}]'
        out, err = io.StringIO(), io.StringIO()
        argv = ['abi_workbench', 'decode-call', '--abi', 'fixture.json',
                '--function', 'transfer', '--data', '0x' + self.payload.hex()]
        with patch.object(abi.Path, 'open', return_value=io.BytesIO(raw)), \
             patch('sys.argv', argv), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(abi.main(), 0)
        result = json.loads(out.getvalue())
        self.assertEqual(result['selector'], '0xa9059cbb')
        self.assertEqual(result['arguments'][1]['value'], 12)
        self.assertEqual(err.getvalue(), '')

    def test_cli_rejects_bad_selector_without_success_output(self):
        raw = b'[{"type":"function","name":"transfer","inputs":[{"type":"address"},{"type":"uint256"}]}]'
        out, err = io.StringIO(), io.StringIO()
        argv = ['abi_workbench', 'decode-call', '--abi', 'fixture.json',
                '--function', 'transfer', '--data', '0x' + (b'nope' + self.payload[4:]).hex()]
        with patch.object(abi.Path, 'open', return_value=io.BytesIO(raw)), \
             patch('sys.argv', argv), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(abi.main(), 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('selector does not match', err.getvalue())


if __name__ == '__main__':
    unittest.main()
