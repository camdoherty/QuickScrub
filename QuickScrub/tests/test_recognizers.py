import unittest
from ..recognizers.ip_recognizer import IpRecognizer
from ..recognizers.email_recognizer import EmailRecognizer
from ..recognizers.mac_recognizer import MacAddressRecognizer
from ..recognizers.phone_recognizer import PhoneRecognizer
from ..recognizers.credit_card_recognizer import CreditCardRecognizer

class TestRecognizers(unittest.TestCase):
    def test_ip_recognizer(self):
        recognizer = IpRecognizer()
        findings = recognizer.analyze("IPs: 192.168.1.1 and 300.0.0.1")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].value, "192.168.1.1")

    def test_email_recognizer(self):
        recognizer = EmailRecognizer()
        findings = recognizer.analyze("Contact test@example.com for info.")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].value, "test@example.com")

    def test_mac_recognizer(self):
        recognizer = MacAddressRecognizer()
        text = "MACs are 00-1A-2B-3C-4D-5E and 00:1A:2B:3C:4D:5F."
        findings = recognizer.analyze(text)
        self.assertEqual(len(findings), 2)

    def test_phone_recognizer(self):
        recognizer = PhoneRecognizer()
        findings = recognizer.analyze("Call (123) 456-7890 or 9876543210.")
        self.assertEqual(len(findings), 2)
        findings = recognizer.analyze("Number is 123456.") # Should not match
        self.assertEqual(len(findings), 0)

    def test_credit_card_recognizer(self):
        recognizer = CreditCardRecognizer()
        # Valid Luhn number
        findings = recognizer.analyze("Card: 4992-7398-716-9822")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].value, "4992-7398-716-9822")
        # Invalid Luhn number
        findings = recognizer.analyze("Card: 1234-5678-1234-5678")
        self.assertEqual(len(findings), 0)
