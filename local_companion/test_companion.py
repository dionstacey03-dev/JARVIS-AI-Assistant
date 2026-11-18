import unittest
from unittest.mock import patch

import app as companion
from fastapi import HTTPException

class CompanionSecurityTests(unittest.TestCase):
    def test_missing_token_fails_closed(self):
        with patch.object(companion, "TOKEN", ""):
            with self.assertRaises(HTTPException) as raised:
                companion.require_token(None)
            self.assertEqual(raised.exception.status_code, 503)

    def test_short_token_fails_closed(self):
        with patch.object(companion, "TOKEN", "short"):
            with self.assertRaises(HTTPException) as raised:
                companion.require_token("Bearer short")
            self.assertEqual(raised.exception.status_code, 503)

    def test_valid_token_is_accepted(self):
        secret = "x" * 48
        with patch.object(companion, "TOKEN", secret):
            companion.require_token("Bearer " + secret)

    def test_invalid_token_is_rejected(self):
        with patch.object(companion, "TOKEN", "x" * 48):
            with self.assertRaises(HTTPException) as raised:
                companion.require_token("Bearer " + "y" * 48)
            self.assertEqual(raised.exception.status_code, 401)

if __name__ == "__main__":
    unittest.main()
