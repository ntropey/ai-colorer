import io
import json
import os
import sys
import unittest
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import update_checker as uc


def fake_opener(payload):
    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    return lambda request, timeout=None: Response(json.dumps(payload).encode())


class UpdateCheckerTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(uc.parse_version("v2.0.10"), (2, 0, 10))
        self.assertEqual(uc.parse_version("2.1.0-beta"), (2, 1, 0))
        self.assertIsNone(uc.parse_version("latest"))

    def test_numeric_not_text_comparison(self):
        self.assertTrue(uc.is_newer("v2.0.10", "2.0.9"))
        self.assertFalse(uc.is_newer("v2.0.2", "2.0.2"))
        self.assertFalse(uc.is_newer("v2.0.1", "2.0.2"))

    def test_update_available(self):
        opener = fake_opener({"tag_name": "v2.0.3", "html_url": "https://github.com/ntropey/ai-colorer/releases/tag/v2.0.3", "body": "Notes"})
        r = uc.check_for_update("2.0.2", opener)
        self.assertTrue(r["update_available"])
        self.assertEqual(r["latest"], "2.0.3")
        self.assertEqual(r["notes"], "Notes")

    def test_up_to_date(self):
        opener = fake_opener({"tag_name": "v2.0.2", "html_url": "https://github.com/ntropey/ai-colorer/releases/tag/v2.0.2"})
        self.assertFalse(uc.check_for_update("2.0.2", opener)["update_available"])

    def test_foreign_release_url_is_replaced(self):
        opener = fake_opener({"tag_name": "v9.0.0", "html_url": "https://evil.example/x"})
        self.assertTrue(uc.check_for_update("2.0.2", opener)["release_url"].startswith(uc.RELEASE_PAGE_PREFIX))

    def test_offline(self):
        def boom(request, timeout=None):
            raise urllib.error.URLError("no network")

        self.assertEqual(uc.check_for_update("2.0.2", boom)["error"], "unreachable")

    def test_garbage_tag(self):
        self.assertEqual(uc.check_for_update("2.0.2", fake_opener({"tag_name": "nightly"}))["error"], "unreadable")


if __name__ == "__main__":
    unittest.main()
