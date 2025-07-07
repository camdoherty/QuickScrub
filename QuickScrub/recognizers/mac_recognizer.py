import re
from typing import List
from .base import Recognizer, Finding

class MacAddressRecognizer(Recognizer):
    MAC_REGEX = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b|\b(?:[0-9A-Fa-f]{4}\.){2}(?:[0-9A-Fa-f]{4})\b')
    def __init__(self): super().__init__(name="MAC Address", tag="MAC_ADDRESS")
    def analyze(self, text: str) -> List[Finding]:
        return [Finding(m.start(), m.end(), m.group(0), self.tag, self.name) for m in self.MAC_REGEX.finditer(text)]
