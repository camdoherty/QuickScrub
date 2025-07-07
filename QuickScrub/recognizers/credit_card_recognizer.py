import re
from typing import List
from .base import Recognizer, Finding

class CreditCardRecognizer(Recognizer):
    CC_REGEX = re.compile(r'\b(?:\d[ -]?){12,18}\d\b')
    def __init__(self): super().__init__(name="Credit Card", tag="CREDIT_CARD")
    def _is_luhn_valid(self, n: str) -> bool:
        try:
            d = [int(x) for x in reversed(n)]; c = sum(d[::2]) + sum(sum(divmod(i * 2, 10)) for i in d[1::2])
            return c % 10 == 0
        except (ValueError, TypeError): return False
    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.CC_REGEX.finditer(text):
            cc_digits = re.sub(r'\D', '', match.group(0))
            if 13 <= len(cc_digits) <= 19 and self._is_luhn_valid(cc_digits):
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
        return findings
