# FILE: QuickScrub/recognizers/phone_recognizer.py

import re
from typing import List
import phonenumbers
from .base import Recognizer, Finding

class PhoneRecognizer(Recognizer):
    """
    Recognizes phone numbers using a robust two-step process:
    1. A broad regex finds candidate strings that might be phone numbers.
    2. The 'phonenumbers' library validates each clean candidate.
    This handles both international and US-style numbers in noisy text.
    """
    
    # This regex is intentionally broad. It looks for strings containing at least 7 digits,
    # allowing for common separators, parentheses, and an optional country code.
    CANDIDATE_REGEX = re.compile(r'((?:\+\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s\d-]{7,15})')

    def __init__(self):
        super().__init__(name="Phone Number", tag="PHONE")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        found_spans = set()

        # Step 1: Find all potential candidates in the text.
        for candidate_match in self.CANDIDATE_REGEX.finditer(text):
            candidate_text = candidate_match.group(1).strip()
            
            try:
                # Step 2: Use the phonenumbers library on the *clean candidate*.
                for match in phonenumbers.PhoneNumberMatcher(candidate_text, "US"):
                    if phonenumbers.is_valid_number(match.number):
                        
                        # The match object's start/end are relative to the candidate string.
                        # We must add the candidate's start index to get the true position in the original text.
                        original_start = candidate_match.start(1) + match.start
                        original_end = candidate_match.start(1) + match.end
                        
                        span = (original_start, original_end)
                        if span not in found_spans:
                            findings.append(Finding(
                                start=original_start,
                                end=original_end,
                                value=text[original_start:original_end], # Get the exact value from the original text
                                type=self.tag,
                                recognizer_name=self.name
                            ))
                            found_spans.add(span)
            except Exception:
                # The library can throw errors; ignore and continue.
                continue

        return findings