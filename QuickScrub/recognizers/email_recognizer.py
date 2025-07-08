# FILE: QuickScrub/recognizers/email_recognizer.py

import re
from typing import List
from .base import Recognizer, Finding

class EmailRecognizer(Recognizer):
    # A simple regex to find a potential email address.
    BARE_EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')

    # A more complex regex to find a Markdown link that CONTAINS an email.
    # It looks for a mailto: link or a bare email in the text or href part.
    MARKDOWN_EMAIL_REGEX = re.compile(
        r'(\[([^\]]+)\]\((mailto:)?' + BARE_EMAIL_REGEX.pattern + r'\))',
        re.IGNORECASE
    )

    def __init__(self):
        super().__init__(name="Email Address", tag="EMAIL")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        # Keep track of text spans that have been claimed by a markdown link.
        claimed_spans = []

        # Pass 1: Find complex Markdown-style email links first.
        for match in self.MARKDOWN_EMAIL_REGEX.finditer(text):
            findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
            claimed_spans.append(range(match.start(), match.end()))

        # Pass 2: Find simple, bare email addresses, but only if they haven't been claimed.
        for match in self.BARE_EMAIL_REGEX.finditer(text):
            is_claimed = False
            for span in claimed_spans:
                if match.start() in span:
                    is_claimed = True
                    break
            if not is_claimed:
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
        
        return findings