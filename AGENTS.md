### **Instructions for Codex/ChatGPT**

Please apply the following corrections to the codebase.

#### **1. (CRITICAL) Update `QuickScrub/tests/test_recognizers.py`**

*   **Action:** Overwrite the file `QuickScrub/tests/test_recognizers.py` with the following content. This version adds the missing tests for Phone and MAC recognizers and improves the readability of all tests.

```python
# FILE: QuickScrub/tests/test_recognizers.py

import unittest
from ..recognizers.ip_recognizer import IpRecognizer
from ..recognizers.email_recognizer import EmailRecognizer
from ..recognizers.mac_recognizer import MacAddressRecognizer
from ..recognizers.phone_recognizer import PhoneRecognizer
from ..recognizers.credit_card_recognizer import CreditCardRecognizer

class TestRecognizers(unittest.TestCase):
    """
    Unit tests for all PII recognizers.
    """
    def test_ip_recognizer(self):
        recognizer = IpRecognizer()
        findings = recognizer.analyze("Valid IPs: 192.168.1.1 and invalid: 300.0.0.1")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].value, "192.168.1.1")

    def test_email_recognizer(self):
        recognizer = EmailRecognizer()
        findings = recognizer.analyze("Contact test@example.com for info.")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].value, "test@example.com")

    def test_mac_address_recognizer(self):
        recognizer = MacAddressRecognizer()
        text = "MACs are 00-1A-2B-3C-4D-5E and 00:1A:2B:3C:4D:5F."
        findings = recognizer.analyze(text)
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0].value, "00-1A-2B-3C-4D-5E")
        self.assertEqual(findings[1].value, "00:1A:2B:3C:4D:5F")

    def test_phone_recognizer(self):
        recognizer = PhoneRecognizer()
        findings = recognizer.analyze("Call (123) 456-7890 or 987.654.3210.")
        self.assertEqual(len(findings), 2)
        
        # Should not match numbers with too few digits
        findings_invalid = recognizer.analyze("Number is 123456.")
        self.assertEqual(len(findings_invalid), 0)

    def test_credit_card_recognizer(self):
        recognizer = CreditCardRecognizer()
        
        # Valid Luhn number
        findings_valid = recognizer.analyze("Card: 4992-7398-716-9822")
        self.assertEqual(len(findings_valid), 1)
        self.assertEqual(findings_valid[0].value, "4992-7398-716-9822")
        
        # Invalid Luhn number
        findings_invalid = recognizer.analyze("Card: 1234-5678-1234-5678")
        self.assertEqual(len(findings_invalid), 0)
```

---

#### **2. (RECOMMENDED) Update `pyproject.toml`**

*   **Action:** Overwrite the file `pyproject.toml` with the following content to make the packaging more robust.

```toml
# FILE: pyproject.toml

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "QuickScrub"
version = "1.0.0"
description = "A local, modular PII scrubber with a web UI."
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.22.0",
    "pydantic>=2.0",
    "python-multipart>=0.0.9"
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

---

#### **3. (RECOMMENDED) Update Recognizers for Readability**

*   **Action:** Overwrite the five recognizer files with their expanded, more readable versions.

*   **File 1: `QuickScrub/recognizers/ip_recognizer.py`**
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class IpRecognizer(Recognizer):
        IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

        def __init__(self):
            super().__init__(name="IP Address", tag="IP_ADDRESS")

        def analyze(self, text: str) -> List[Finding]:
            findings = []
            for match in self.IP_REGEX.finditer(text):
                ip = match.group(0)
                if all(0 <= int(octet) <= 255 for octet in ip.split('.')):
                    findings.append(Finding(match.start(), match.end(), ip, self.tag, self.name))
            return findings
    ```

*   **File 2: `QuickScrub/recognizers/email_recognizer.py`**
    ```python
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
    ```

*   **File 3: `QuickScrub/recognizers/phone_recognizer.py`**
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class PhoneRecognizer(Recognizer):
        PHONE_REGEX = re.compile(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        
        def __init__(self):
            super().__init__(name="Phone Number", tag="PHONE")
        
        def analyze(self, text: str) -> List[Finding]:
            findings = []
            for match in self.PHONE_REGEX.finditer(text):
                if len(re.sub(r'\D', '', match.group(0))) >= 10:
                    findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
            return findings
    ```

*   **File 4: `QuickScrub/recognizers/mac_recognizer.py`**
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class MacAddressRecognizer(Recognizer):
        MAC_REGEX = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b|\b(?:[0-9A-Fa-f]{4}\.){2}(?:[0-9A-Fa-f]{4})\b')
        
        def __init__(self):
            super().__init__(name="MAC Address", tag="MAC_ADDRESS")
        
        def analyze(self, text: str) -> List[Finding]:
            return [
                Finding(m.start(), m.end(), m.group(0), self.tag, self.name)
                for m in self.MAC_REGEX.finditer(text)
            ]
    ```

*   **File 5: `QuickScrub/recognizers/credit_card_recognizer.py`**
    ```python
    import re
    from typing import List
    from .base import Recognizer, Finding

    class CreditCardRecognizer(Recognizer):
        CC_REGEX = re.compile(r'\b(?:\d[ -]?){12,18}\d\b')
        
        def __init__(self):
            super().__init__(name="Credit Card", tag="CREDIT_CARD")
        
        def _is_luhn_valid(self, number: str) -> bool:
            try:
                digits = [int(d) for d in reversed(number)]
                checksum = sum(digits[::2]) + sum(sum(divmod(d * 2, 10)) for d in digits[1::2])
                return checksum % 10 == 0
            except (ValueError, TypeError):
                return False

        def analyze(self, text: str) -> List[Finding]:
            findings = []
            for match in self.CC_REGEX.finditer(text):
                cc_digits = re.sub(r'\D', '', match.group(0))
                if 13 <= len(cc_digits) <= 19 and self._is_luhn_valid(cc_digits):
                    findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
            return findings
    ```