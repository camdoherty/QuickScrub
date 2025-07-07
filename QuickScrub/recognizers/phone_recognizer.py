import re
from typing import List
from .base import Recognizer, Finding

class PhoneRecognizer(Recognizer):
    # This robust regex uses negative lookarounds instead of word boundaries.
    # (?<!\d) ensures the match is not preceded by a digit.
    # (?!\d) ensures the match is not followed by a digit.
    # This correctly handles phone numbers next to punctuation like '|'.
    PHONE_REGEX = re.compile(
        r'(?<!\d)'          # Negative lookbehind: not preceded by a digit
        r'\(?\d{3}\)?'      # Optional area code in parentheses
        r'[-.\s]?'          # Optional separator
        r'\d{3}'            # First 3 digits
        r'[-.\s]?'          # Optional separator
        r'\d{4}'            # Last 4 digits
        r'(?!\d)'           # Negative lookahead: not followed by a digit
    )

    def __init__(self):
        super().__init__(name="Phone Number", tag="PHONE")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.PHONE_REGEX.finditer(text):
            # We use match.group(0) to get the ENTIRE matched string.
            # We also strip leading/trailing whitespace that the pattern might catch.
            matched_value = match.group(0).strip()
            
            # Final validation: ensure it contains at least 10 digits.
            if len(re.sub(r'\D', '', matched_value)) >= 10:
                # To get the correct start index after stripping whitespace
                start_index = text.find(matched_value, match.start())
                
                findings.append(Finding(
                    start=start_index,
                    end=start_index + len(matched_value),
                    value=matched_value,
                    type=self.tag,
                    recognizer_name=self.name
                ))
        return findings