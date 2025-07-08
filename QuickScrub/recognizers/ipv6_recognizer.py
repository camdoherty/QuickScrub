# FILE: QuickScrub/recognizers/ipv6_recognizer.py

import re
import ipaddress
from typing import List
from .base import Recognizer, Finding

class Ipv6Recognizer(Recognizer):
    """
    Recognizes IPv6 addresses by finding potential candidates with a simple regex
    and then using the robust 'ipaddress' module for validation.
    """
    # This regex is intentionally broad. It finds sequences of characters that
    # could plausibly be an IPv6 address, including colons and hex characters.
    # The goal is to cast a wide net and let the ipaddress library do the real work.
    IPV6_CANDIDATE_REGEX = re.compile(r'\b([0-9a-fA-F:]+:+[0-9a-fA-F:]+)\b')

    def __init__(self):
        super().__init__(name="IPv6 Address", tag="IPV6_ADDRESS")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.IPV6_CANDIDATE_REGEX.finditer(text):
            potential_ip = match.group(0)
            try:
                # The ipaddress module is the source of truth for validation.
                addr = ipaddress.ip_address(potential_ip)
                # We only care about IPv6 addresses in this recognizer.
                if addr.version == 6:
                    findings.append(Finding(
                        start=match.start(),
                        end=match.end(),
                        value=potential_ip,
                        type=self.tag,
                        recognizer_name=self.name
                    ))
            except ValueError:
                # This is expected for any candidate that isn't a valid IP address.
                continue
        return findings
