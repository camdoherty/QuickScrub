# FILE: QuickScrub/recognizers/phone_recognizer.py

"""QuickScrub phone‐number recognizer.

This version switches the underlying *phonenumbers* matcher to
``Leniency.POSSIBLE`` so that fictitious but well‑formed prefixes such
as the North‑American testing code **555** are still caught.  We also
remove the redundant ``is_possible_number`` guard – the matcher already
performs that check when running in POSSIBLE mode.

The rest of the logic (digit‑count pre‑filter, span deduplication, line‑
by‑line iteration) is unchanged, so no other recognizers are affected.
"""

from typing import List

import phonenumbers
from phonenumbers import Leniency  # NEW – explicit import for clarity

from .base import Finding, Recognizer


class PhoneRecognizer(Recognizer):
    """Recognize phone numbers using *phonenumbers* in POSSIBLE mode."""

    def __init__(self) -> None:
        super().__init__(name="Phone Number", tag="PHONE")

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def analyze(self, text: str) -> List[Finding]:
        """Return a list of phone‑number findings in *text*."""

        findings: List[Finding] = []
        found_spans: set[tuple[int, int]] = set()  # avoid duplicates
        line_start_offset = 0  # running character offset while we iterate

        for line in text.splitlines(True):  # True keeps the newline chars
            # ----------------------------------------------------------
            # 1. Cheap pre‑filter – skip lines that clearly cannot hold a
            #    phone number (too few or too many digits).
            # ----------------------------------------------------------
            digit_count = sum(ch.isdigit() for ch in line)
            if not (7 <= digit_count <= 18):
                line_start_offset += len(line)
                continue

            # ----------------------------------------------------------
            # 2. Run the libphonenumber matcher at *POSSIBLE* leniency –
            #    this still enforces length & basic structure but does
            #    not require the number to be actually diallable.
            # ----------------------------------------------------------
            try:
                for match in phonenumbers.PhoneNumberMatcher(
                    line, "US", leniency=Leniency.POSSIBLE
                ):
                    abs_start = line_start_offset + match.start
                    abs_end = line_start_offset + match.end
                    span = (abs_start, abs_end)
                    if span in found_spans:
                        continue

                    findings.append(
                        Finding(
                            start=abs_start,
                            end=abs_end,
                            value=match.raw_string,
                            type=self.tag,
                            recognizer_name=self.name,
                        )
                    )
                    found_spans.add(span)
            except Exception:
                # The library occasionally raises on malformed fragments.
                # We swallow the error because false negatives are better
                # than a crash in the middle of scrubbing.
                pass

            line_start_offset += len(line)  # advance offset for next line

        return findings
