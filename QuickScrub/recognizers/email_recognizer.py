import re
from typing import List
from .base import Recognizer, Finding

class EmailRecognizer(Recognizer):
    """A simple regex-based recognizer for email addresses."""
    # A widely used and generally effective regex for emails.
    EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')

    def __init__(self):
        super().__init__(name="Email Address", tag="EMAIL")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.EMAIL_REGEX.finditer(text):
            findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
        return findings
