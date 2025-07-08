# Implementation instructions & updated code:

Follow these steps to implement all the fixes.

#### Step 1: Modify `pyproject.toml`

Add the new `phonenumbers` dependency.

```toml
# FILE: pyproject.toml

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "QuickScrub"
version = "1.1.0" # It's good practice to version bump after significant changes
description = "A local, modular PII scrubber with a web UI."
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.22.0",
    "pydantic>=2.0",
    "python-multipart>=0.0.9",
    "phonenumbers>=8.13.0", # <-- ADD THIS LINE
]

[project.optional-dependencies]
dev = [
    "pytest",
    "requests",
]

# Explicitly define the package to prevent auto-discovery errors.
[tool.setuptools.packages.find]
include = ["QuickScrub", "QuickScrub.*"]
```

#### Step 2: Replace the content of `QuickScrub/core/engine.py`

This new version contains the improved conflict resolution logic.

```python
# FILE: QuickScrub/core/engine.py

from typing import List, Dict
from ..models.data_models import ScrubTask, ScrubResult
from ..recognizers.base import Finding

class ScrubberEngine:
    def scrub(self, task: ScrubTask, findings: List[Finding]) -> ScrubResult:
        final_findings = self._resolve_conflicts(findings, task.allow_list)
        scrubbed_text, legend = self._scrub_text(task.text, final_findings)
        return ScrubResult(scrubbed_text=scrubbed_text, legend=legend)

    def _resolve_conflicts(self, findings: List[Finding], allow_list: List[str]) -> List[Finding]:
        """
        Resolves overlapping findings and filters out values from the allow list.
        The strategy is to sort by start index and then by length (longest first).
        This ensures that if a smaller finding is completely contained within a
        larger one (e.g., an email inside a sensitive URL), the larger finding is kept.
        """
        allow_set = {item.lower() for item in allow_list}
        allowed_findings = [f for f in findings if f.value.lower() not in allow_set]
        
        # Sort by start index, then by the negative of the end index (longest match first)
        sorted_findings = sorted(allowed_findings, key=lambda f: (f.start, -f.end))

        resolved: List[Finding] = []
        if not sorted_findings:
            return resolved

        last_accepted_finding = sorted_findings[0]
        for current_finding in sorted_findings[1:]:
            # If the current finding starts before the last one has ended, it's either
            # overlapping or fully nested. Because we sorted longest-first, we can
            # safely discard it.
            if current_finding.start < last_accepted_finding.end:
                continue
            
            resolved.append(current_finding)
            last_accepted_finding = current_finding
        
        # Add the very first finding to the list, as the loop starts from the second item.
        resolved.insert(0, sorted_findings[0])

        return resolved

    def _scrub_text(self, text: str, findings: List[Finding]) -> (str, List[Dict[str, str]]):
        scrubbed_text = text
        placeholder_counts: Dict[str, int] = {}
        value_to_placeholder_map: Dict[str, str] = {}
        legend_map: Dict[str, Dict[str, str]] = {}

        for finding in sorted(findings, key=lambda f: f.start):
            if finding.value in value_to_placeholder_map:
                continue
            pii_type = finding.type
            count = placeholder_counts.get(pii_type, 0) + 1
            placeholder_counts[pii_type] = count
            placeholder = f"[{pii_type}_{count}]"
            value_to_placeholder_map[finding.value] = placeholder
            legend_map[placeholder] = {"original": finding.value, "mock": placeholder, "type": pii_type}

        # This replacement logic now operates on a clean, non-overlapping list of findings.
        for finding in reversed(findings):
            placeholder = value_to_placeholder_map[finding.value]
            scrubbed_text = scrubbed_text[:finding.start] + placeholder + scrubbed_text[finding.end:]

        legend = sorted(legend_map.values(), key=lambda item: int(item['mock'].split('_')[-1][:-1]))
        return scrubbed_text, legend
```

#### Step 3: Replace the content of `QuickScrub/recognizers/phone_recognizer.py`

This completely overhauls the recognizer to use the `phonenumbers` library.

```python
# FILE: QuickScrub/recognizers/phone_recognizer.py

from typing import List
import phonenumbers
from .base import Recognizer, Finding

class PhoneRecognizer(Recognizer):
    """
    Recognizes phone numbers using the 'phonenumbers' library.
    This provides robust support for international formats.
    """
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
                    findings.append(Finding(
                        start=match.start,
                        end=match.end,
                        value=match.raw_string,
                        type=self.tag,
                        recognizer_name=self.name
                    ))
        except Exception:
            # The library can sometimes raise errors on malformed large inputs.
            # We'll ignore these and return any findings we have so far.
            pass
        return findings
```

#### Step 4: Replace the content of `QuickScrub/recognizers/mac_address_recognizer.py`

This version handles escaped colons.

```python
# FILE: QuickScrub/recognizers/mac_address_recognizer.py

import re
from typing import List
from .base import Recognizer, Finding

class MacAddressRecognizer(Recognizer):
    # Regex updated to optionally handle a backslash before the separator: (?:\\?[:-])
    MAC_REGEX = re.compile(
        r'\b(?:[0-9A-Fa-f]{2}(?:\\?[:-])){5}(?:[0-9A-Fa-f]{2})\b|'
        r'\b(?:[0-9A-Fa-f]{4}(?:\\?\.|-)){2}(?:[0-9A-Fa-f]{4})\b'
    )

    def __init__(self):
        super().__init__(name="MAC Address", tag="MAC_ADDRESS")

    def analyze(self, text: str) -> List[Finding]:
        return [
            Finding(m.start(), m.end(), m.group(0), self.tag, self.name)
            for m in self.MAC_REGEX.finditer(text)
        ]
```

#### Step 5: Replace the content of `QuickScrub/recognizers/ipv6_recognizer.py`

This version also handles escaped colons.

```python
# FILE: QuickScrub/recognizers/ipv6_recognizer.py

import re
import ipaddress
from typing import List
from .base import Recognizer, Finding

class Ipv6Recognizer(Recognizer):
    """Recognizes IPv6 addresses using regex for candidate detection and the 'ipaddress' module for validation."""

    # Regex updated to optionally handle a backslash before colons: (?:\\?:)
    IPV6_REGEX = re.compile(r"""
        \b (?:
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){7} [0-9a-fA-F]{1,4}                    |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,7} (?:\\?:)                         |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,6} (?:\\?:) [0-9a-fA-F]{1,4}         |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,5} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,2} |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,4} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,3} |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,3} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,4} |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,2} (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,5} |
            [0-9a-fA-F]{1,4} (?:\\?:) (?: (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,6} )     |
            (?:\\?:) (?: (?: (?:\\?:) [0-9a-fA-F]{1,4} ){1,7} | (?:\\?:) )            |
            fe80 (?:\\?:) (?: (?:\\?:) [0-9a-fA-F]{0,4} ){0,4} % [0-9a-zA-Z]{1,}     |
            (?:\\?:){2} (?: ffff (?: (?:\\?:) 0{1,4} )? (?:\\?:) )?                 |
            (?: \d{1,3} \. ){3} \d{1,3}                                       |
            (?: [0-9a-fA-F]{1,4} (?:\\?:) ){1,4} (?:\\?:)                         |
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
```

#### Step 6: Replace the content of `QuickScrub/recognizers/secret_recognizer.py`

This version has the improved prefix regex to fix the partial match bug.

```python
# FILE: QuickScrub/recognizers/secret_recognizer.py

import re
import math
from typing import List, Set
from .base import Recognizer, Finding

class SecretRecognizer(Recognizer):
    """
    Recognizes secrets and keys using a multi-pass approach.
    """
    # Expanded list of high-confidence prefixes for services like Stripe, GitHub, and AWS.
    # Note the specific lengths to reduce false positives.
    PREFIX_REGEX = re.compile(
        r'\b('
        r'(?:sk|pk|rk)_(?:live|test)_[0-9a-zA-Z]{24}|'  # Stripe
        r'ghp_[0-9a-zA-Z]{36}|'                         # GitHub
        r'AKIA[0-9A-Z]{16}'                             # AWS Access Key ID
        r')\b'
    )

    # Common variable names that might hold a secret
    KEYWORD_REGEX = re.compile(r"""
        \b(key|secret|token|password|auth|api_key|secret_key|auth_token)\b # Keywords
        \s*[:=]\s*                                                       # Delimiter
        ['"]?                                                            # Optional quote
        ([a-zA-Z0-9\-_/+]{16,})                                           # The secret value itself
        ['"]?                                                            # Optional quote
    """, re.IGNORECASE | re.VERBOSE)

    # General pattern for finding potential raw tokens (high entropy candidates)
    GENERIC_REGEX = re.compile(r'\b[a-zA-Z0-9\-_/+]{20,64}\b')
    ENTROPY_THRESHOLD = 3.5

    def __init__(self):
        super().__init__(name="API Keys & Secrets", tag="SECRET")

    def _calculate_entropy(self, text: str) -> float:
        """Calculates the Shannon entropy of a string."""
        if not text:
            return 0.0
        char_counts = {c: text.count(c) for c in set(text)}
        entropy = -sum((count / len(text)) * math.log2(count / len(text)) for count in char_counts.values())
        return entropy

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        claimed_indices: Set[int] = set()

        # Pass 1: High-confidence prefixes
        for match in self.PREFIX_REGEX.finditer(text):
            if not set(range(match.start(), match.end())).intersection(claimed_indices):
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
                claimed_indices.update(range(match.start(), match.end()))

        # Pass 2: High-confidence keywords
        for match in self.KEYWORD_REGEX.finditer(text):
            secret_val = match.group(2)
            start_pos = match.start(2)
            end_pos = match.end(2)
            if not set(range(start_pos, end_pos)).intersection(claimed_indices):
                findings.append(Finding(start_pos, end_pos, secret_val, self.tag, self.name))
                claimed_indices.update(range(start_pos, end_pos))

        # Pass 3: Generic high-entropy strings
        for match in self.GENERIC_REGEX.finditer(text):
            if set(range(match.start(), match.end())).intersection(claimed_indices):
                continue
            
            value = match.group(0)
            has_digit = any(c.isdigit() for c in value)
            has_lower = any(c.islower() for c in value)
            has_upper = any(c.isupper() for c in value)

            if (has_digit and has_lower and has_upper) or self._calculate_entropy(value) > self.ENTROPY_THRESHOLD:
                findings.append(Finding(match.start(), match.end(), value, self.tag, self.name))
                claimed_indices.update(range(match.start(), match.end()))
        
        return findings
```
