import re
from typing import List
from .base import Recognizer, Finding

class CreditCardRecognizer(Recognizer):
    # This regex is more general. It finds sequences of 13 to 19 digits that may
    # be interrupted by single spaces or dashes, but ensures it starts and ends
    # with a digit. This is a common pattern.
    CC_REGEX = re.compile(r'\b\d(?:[ -]?\d){12,18}\b')

    def __init__(self):
        super().__init__(name="Credit Card", tag="CREDIT_CARD")

    def _is_luhn_valid(self, number: str) -> bool:
        try:
            digits = [int(d) for d in reversed(number)]
            checksum = sum(digits[::2]) + sum(sum(divmod(d * 2, 10)) for d in digits[1::2])
            return checksum % 10 == 0
        except (ValueError, TypeError):
            return False

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.CC_REGEX.finditer(text):
            cc_digits = re.sub(r'\D', '', match.group(0))
            if 13 <= len(cc_digits) <= 19 and self._is_luhn_valid(cc_digits):
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
        return findings
