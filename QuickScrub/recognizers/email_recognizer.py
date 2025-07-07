import re
from typing import List
from .base import Recognizer, Finding

class EmailRecognizer(Recognizer):
    EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')

    def __init__(self):
        super().__init__(name="Email Address", tag="EMAIL")

    def analyze(self, text: str) -> List[Finding]:
        return [
            Finding(m.start(), m.end(), m.group(0), self.tag, self.name)
            for m in self.EMAIL_REGEX.finditer(text)
        ]