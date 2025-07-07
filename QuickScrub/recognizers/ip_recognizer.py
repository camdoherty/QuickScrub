import re
from typing import List
from .base import Recognizer, Finding

class IpRecognizer(Recognizer):
    IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    def __init__(self): super().__init__(name="IP Address", tag="IP_ADDRESS")
    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.IP_REGEX.finditer(text):
            ip = match.group(0)
            if all(0 <= int(octet) <= 255 for octet in ip.split('.')):
                findings.append(Finding(match.start(), match.end(), ip, self.tag, self.name))
        return findings
