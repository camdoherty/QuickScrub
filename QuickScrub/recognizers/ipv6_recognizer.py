import re
import ipaddress
from typing import List
from .base import Recognizer, Finding


class Ipv6Recognizer(Recognizer):
    """Recognizes IPv6 addresses using regex for candidate detection and the 'ipaddress' module for validation."""

    # Regex updated to optionally handle a backslash before colons: (?:\\?:)
    IPV6_REGEX = re.compile(r"""
        \b (?:
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){7} [0-9a-fA-F]{1,4}
    |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,7} (?:\\?:)
   |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,6} (?:\\?:) [0-9a-fA-F]{1,4}
   |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,5} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,2} |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,4} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,3} |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,3} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,4} |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,2} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,5} |
            [0-9a-fA-F]{1,4} (?:\\?:) (?: (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,6} )     |
            (?:\\?:) (?: (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,7} | (?:\\?:) )
      |
            fe80 (?:\\?:) (?: (?:\\?:) [0-9a-fA-F]{0,4} ){0,4} % [0-9a-zA-Z]{1,}     |
            (?:\\?:){2} (?: ffff (?: (?:\\?:) 0{1,4} )? (?:\\?:) )?
    |
            (?: \d{1,3} \. ){3} \d{1,3}                                       |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,4} (?:\\?:)
  |
            (?: \d{1,3} \. ){3} \d{1,3}
        ) \b
    """, re.VERBOSE | re.IGNORECASE)

    def __init__(self):
        super().__init__(name="IPv6 Address", tag="IPV6_ADDRESS")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.IPV6_REGEX.finditer(text):
            # Clean the value of escape characters before validation
            potential_ip = match.group(0).replace('\\', '')
            try:
                addr = ipaddress.ip_address(potential_ip)
                if addr.version == 6:
                    # Return the original, un-cleaned value in the Finding
                    findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
            except ValueError:
                continue
        return findings
