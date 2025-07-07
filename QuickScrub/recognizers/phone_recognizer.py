import re
from typing import List
from .base import Recognizer, Finding

class PhoneRecognizer(Recognizer):
    PHONE_REGEX = re.compile(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    def __init__(self): super().__init__(name="Phone Number", tag="PHONE")
    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.PHONE_REGEX.finditer(text):
            if len(re.sub(r'\D', '', match.group(0))) >= 10:
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
        return findings
