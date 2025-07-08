import unittest
from QuickScrub.recognizers.secret_recognizer import SecretRecognizer
from QuickScrub.recognizers.ipv6_recognizer import Ipv6Recognizer
from QuickScrub.recognizers.sensitive_url_recognizer import SensitiveUrlRecognizer

class TestNewRecognizers(unittest.TestCase):
    """Unit tests for the new set of PII recognizers."""

    def test_secret_recognizer(self):
        recognizer = SecretRecognizer()
        text = (
            "High-confidence key: sk_live_abcdefghijklmnopqrstuvwx "
            "Another one: ghp_1234567890abcdef1234567890abcdef. "
            "Keyword assignment: api_key = 'a_very_long_and_secure_key_123'. "
            "A generic high-entropy token: aT5vG7hJkLpW2sFqE9rY3zXcVbNmMpA8. "
            "This is just a normal sentence with a UUID-like-string 123e4567-e89b-12d3-a456-426614174000 which should not match."
        )
        
        findings = recognizer.analyze(text)
        self.assertEqual(len(findings), 4)
        
        values = {f.value for f in findings}
        self.assertIn("sk_live_abcdefghijklmnopqrstuvwx", values)
        self.assertIn("ghp_1234567890abcdef1234567890abcdef", values)
        self.assertIn("a_very_long_and_secure_key_123", values)
        self.assertIn("aT5vG7hJkLpW2sFqE9rY3zXcVbNmMpA8", values)

    def test_ipv6_recognizer(self):
        recognizer = Ipv6Recognizer()
        text = (
            "Valid full: 2001:0db8:85a3:0000:0000:8a2e:0370:7334. "
            "Valid compressed: 2001:db8::8a2e:370:7334. "
            "Another one: ::1. "
            "Invalid: 2001:db8::g. Not an IP: 1234:5678. "
            "IPv4-mapped: ::ffff:192.0.2.128."
        )

        findings = recognizer.analyze(text)
        self.assertEqual(len(findings), 4)
        values = {f.value for f in findings}
        self.assertIn("2001:0db8:85a3:0000:0000:8a2e:0370:7334", values)
        self.assertIn("2001:db8::8a2e:370:7334", values)
        self.assertIn("::1", values)
        self.assertIn("::ffff:192.0.2.128", values)

    def test_sensitive_url_recognizer(self):
        recognizer = SensitiveUrlRecognizer()
        text = (
            "A benign URL: https://example.com/some/path. "
            "A sensitive URL: http://dev.local/auth?access_token=abcdef123456. "
            "Another one: www.api.com/v2/user?session_id=zyxw9876. "
            "URL with no sensitive params: https://google.com/search?q=hello. "
            "URL with multiple params, one sensitive: ftp://files.server/get?file=1&key=fedcba."
        )
        
        findings = recognizer.analyze(text)
        self.assertEqual(len(findings), 3)
        values = {f.value for f in findings}
        self.assertIn("http://dev.local/auth?access_token=abcdef123456", values)
        self.assertIn("www.api.com/v2/user?session_id=zyxw9876", values)
        self.assertIn("ftp://files.server/get?file=1&key=fedcba", values)