import re
import ipaddress
from typing import List
from .base import Recognizer, Finding

class Ipv6Recognizer(Recognizer):
    """Recognizes IPv6 addresses using regex for candidate detection and the 'ipaddress' module for validation."""

    # A comprehensive regex to find strings that look like IPv6 addresses, including various compressed formats.
    # It's intentionally broad; the ipaddress module will do the strict validation.
    IPV6_REGEX = re.compile(r"""
        \b (?:                                                             # Start of non-capturing group
            (?: [0-9a-fA-F]{1,4} : ){7} [0-9a-fA-F]{1,4}                    | # 1:2:3:4:5:6:7:8
            (?: [0-9a-fA-F]{1,4} : ){1,7} :                                | # 1::                              1:2:3:4:5:6:7::
            (?: [0-9a-fA-F]{1,4} : ){1,6} : [0-9a-fA-F]{1,4}                | # 1::8             1:2:3:4:5:6::8
            (?: [0-9a-fA-F]{1,4} : ){1,5} (?: : [0-9a-fA-F]{1,4} ){1,2}      | # 1::7:8           1:2:3:4:5::7:8
            (?: [0-9a-fA-F]{1,4} : ){1,4} (?: : [0-9a-fA-F]{1,4} ){1,3}      | # 1::6:7:8         1:2:3:4::6:7:8
            (?: [0-9a-fA-F]{1,4} : ){1,3} (?: : [0-9a-fA-F]{1,4} ){1,4}      | # 1::5:6:7:8       1:2:3::5:6:7:8
            (?: [0-9a-fA-F]{1,4} : ){1,2} (?: : [0-9a-fA-F]{1,4} ){1,5}      | # 1::4:5:6:7:8     1:2::4:5:6:7:8
            [0-9a-fA-F]{1,4} : (?: (?: : [0-9a-fA-F]{1,4} ){1,6} )          | # 1::3:4:5:6:7:8
            : (?: (?: : [0-9a-fA-F]{1,4} ){1,7} | : )                       | # ::2:3:4:5:6:7:8  ::
            fe80 : (?: : [0-9a-fA-F]{0,4} ){0,4} % [0-9a-zA-Z]{1,}          | # fe80::7:8%eth0
            :: (?: ffff (?: :0{1,4} )? : )?                                  # ::ffff:0:127.0.0.1
            (?: \d{1,3} \. ){3} \d{1,3}                                    |
            (?: [0-9a-fA-F]{1,4} : ){1,4} :                                  # 2001:db8:3:4::192.0.2.33
            (?: \d{1,3} \. ){3} \d{1,3}
        ) \b
    """, re.VERBOSE | re.IGNORECASE)

    def __init__(self):
        super().__init__(name="IPv6 Address", tag="IPV6_ADDRESS")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.IPV6_REGEX.finditer(text):
            potential_ip = match.group(0)
            try:
                # Use the standard library for definitive validation
                addr = ipaddress.ip_address(potential_ip)
                if addr.version == 6:
                    findings.append(Finding(match.start(), match.end(), potential_ip, self.tag, self.name))
            except ValueError:
                # The regex match was a false positive, ignore it.
                continue
        return findings