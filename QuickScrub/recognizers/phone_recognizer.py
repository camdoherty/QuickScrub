from typing import List
import phonenumbers
from .base import Recognizer, Finding


class PhoneRecognizer(Recognizer):
    """Recognizes phone numbers using the 'phonenumbers' library."""

    def __init__(self):
        super().__init__(name="Phone Number", tag="PHONE")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        try:
            # The region hint "US" helps resolve ambiguity for numbers without a
            # country code, but the library can find numbers with any country code
            # regardless of the hint.
            for match in phonenumbers.PhoneNumberMatcher(text, "US"):
                # We can add further validation if needed, for example:
                if phonenumbers.is_valid_number(match.number):
                    findings.append(
                        Finding(
                            start=match.start,
                            end=match.end,
                            value=match.raw_string,
                            type=self.tag,
                            recognizer_name=self.name,
                        )
                    )
        except Exception:
            # The library can sometimes raise errors on malformed large inputs.
            # We'll ignore these and return any findings we have so far.
            pass
        return findings
