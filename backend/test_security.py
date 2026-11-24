import unittest
from unittest.mock import patch

from fastapi import HTTPException

import api.index as api


class CloudAccessTests(unittest.TestCase):
    def setUp(self):
        api._rate_limit.update({"count": 0, "reset_at": 0.0})

    def test_missing_server_token_fails_closed(self):
        with patch.object(api, "ACCESS_TOKEN", ""):
            with self.assertRaises(HTTPException) as raised:
                api.verify_cloud_access("Bearer " + "x" * 40)
        self.assertEqual(raised.exception.status_code, 503)

    def test_short_server_token_fails_closed(self):
        with patch.object(api, "ACCESS_TOKEN", "short"):
            with self.assertRaises(HTTPException) as raised:
                api.verify_cloud_access("Bearer short")
        self.assertEqual(raised.exception.status_code, 503)

    def test_missing_or_invalid_client_token_is_rejected(self):
        with patch.object(api, "ACCESS_TOKEN", "s" * 40):
            for supplied in (None, "Bearer " + "x" * 40):
                with self.subTest(supplied=supplied):
                    with self.assertRaises(HTTPException) as raised:
                        api.verify_cloud_access(supplied)
                    self.assertEqual(raised.exception.status_code, 401)

    def test_valid_token_is_accepted(self):
        secret = "s" * 40
        with patch.object(api, "ACCESS_TOKEN", secret):
            api.verify_cloud_access("Bearer " + secret)

    def test_request_limit_is_enforced(self):
        secret = "s" * 40
        with patch.object(api, "ACCESS_TOKEN", secret), patch.object(api, "RATE_LIMIT_MAX_REQUESTS", 1):
            api.verify_cloud_access("Bearer " + secret)
            with self.assertRaises(HTTPException) as raised:
                api.verify_cloud_access("Bearer " + secret)
        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("Retry-After", raised.exception.headers)


if __name__ == "__main__":
    unittest.main()
