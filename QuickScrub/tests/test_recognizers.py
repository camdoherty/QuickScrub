import unittest
from ..recognizers.ip_recognizer import IpRecognizer
from ..recognizers.email_recognizer import EmailRecognizer
from ..recognizers.credit_card_recognizer import CreditCardRecognizer

class TestRecognizers(unittest.TestCase):
    def test_ip_recognizer(self):
        r = IpRecognizer(); f = r.analyze("IPs: 192.168.1.1 and 300.0.0.1"); self.assertEqual(len(f), 1); self.assertEqual(f[0].value, "192.168.1.1")
    def test_email_recognizer(self):
        r = EmailRecognizer(); f = r.analyze("Contact test@example.com."); self.assertEqual(len(f), 1)
    def test_credit_card_recognizer(self):
        r = CreditCardRecognizer(); self.assertEqual(len(r.analyze("Card: 499273987169822")), 1); self.assertEqual(len(r.analyze("Card: 1234567812345678")), 0)
