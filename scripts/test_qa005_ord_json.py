"""Strict JSON evidence parser tests: duplicate keys and NaN/Infinity fail closed."""
import unittest

from qa005_ord_json import loads


class StrictJSONTests(unittest.TestCase):
    def test_valid_nested_json_is_preserved(self):
        self.assertEqual(
            loads('{"outer":{"count":3,"name":"fixture"},"items":[true,null]}'),
            {"outer": {"count": 3, "name": "fixture"}, "items": [True, None]},
        )

    def test_duplicate_top_level_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON object key: pair"):
            loads('{"pair":1,"pair":2}')

    def test_duplicate_nested_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON object key: sample"):
            loads('{"trace":{"sample":1,"sample":2}}')

    def test_nonstandard_numeric_constants_are_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaisesRegex(ValueError, "Non-standard JSON numeric constant"):
                    loads('{"value":' + token + '}')

    def test_malformed_json_is_rejected(self):
        with self.assertRaises(ValueError):
            loads('{"unterminated":')


if __name__ == "__main__":
    unittest.main()
