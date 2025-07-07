import re
from typing import List
from .base import Recognizer, Finding

class MacAddressRecognizer(Recognizer):
    """Recognizes MAC addresses in common formats."""
    # Formats: 00-1A-2B-3C-4D-5E, 00:1A:2B:3C:4D:5E, 001A.2B3C.4D5E
    MAC_REGEX = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b|\b(?:[0-9A-Fa-f]{4}\.){2}(?:[0-9A-Fa-f]{4})\b')

    def __init__(self):
        super().__init__(name="MAC Address", tag="MAC_ADDRESS")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.MAC_REGEX.finditer(text):
            findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
        return findings
