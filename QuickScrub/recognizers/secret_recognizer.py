# FILE: QuickScrub/recognizers/secret_recognizer.py

import re
import math
from typing import List, Set
from .base import Recognizer, Finding

class SecretRecognizer(Recognizer):
    """
    Recognizes secrets and keys using a multi-pass, high-confidence approach.
    It prioritizes known patterns and uses entropy as a final, stricter filter.
    """
    # High-confidence prefixes for services like Stripe, GitHub, and AWS.
    # Lengths are specified to match real-world token formats.
    PREFIX_REGEX = re.compile(
        r'\b('
        r'(?:sk|pk|rk)_(?:live|test)_[0-9a-zA-Z]{24}|'  # Stripe-like keys
        r'ghp_[0-9a-zA-Z]{36}|'                         # GitHub tokens
        r'AKIA[0-9A-Z]{16}'                             # AWS Access Key ID
        r')\b'
    )

    # Finds common variable names assigned to potential secrets.
    KEYWORD_REGEX = re.compile(r"""
        \b(key|secret|token|password|auth|api_key|secret_key|auth_token)\b # Keywords
        \s*[:=]\s*                                                       # Delimiter
        ['"]?                                                            # Optional quote
        ([a-zA-Z0-9\-_/+]{16,64})                                         # The secret value
        ['"]?                                                            # Optional quote
    """, re.IGNORECASE | re.VERBOSE)

    # General pattern for finding potential raw tokens.
    # The dot character '.' is now included to handle JWTs correctly.
    GENERIC_REGEX = re.compile(r'\b[a-zA-Z0-9\-_/+.]{20,128}\b')
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

        # Pass 1: High-confidence prefixes (most reliable)
        for match in self.PREFIX_REGEX.finditer(text):
            if not set(range(match.start(), match.end())).intersection(claimed_indices):
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
                claimed_indices.update(range(match.start(), match.end()))

        # Pass 2: High-confidence keywords
        for match in self.KEYWORD_REGEX.finditer(text):
            # The actual secret is in group 2. We need its specific start/end position.
            secret_val = match.group(2)
            start_pos = match.start(2)
            end_pos = match.end(2)
            if not set(range(start_pos, end_pos)).intersection(claimed_indices):
                findings.append(Finding(start_pos, end_pos, secret_val, self.tag, self.name))
                claimed_indices.update(range(start_pos, end_pos))

        # Pass 3: Generic high-entropy strings (strictest filter)
        for match in self.GENERIC_REGEX.finditer(text):
            if set(range(match.start(), match.end())).intersection(claimed_indices):
                continue
            
            value = match.group(0)
            
            # To qualify as a generic secret, a string must have BOTH high
            # character variety AND high entropy. This prevents flagging
            # long variable names or simple strings.
            has_digit = any(c.isdigit() for c in value)
            has_lower = any(c.islower() for c in value)
            has_upper = any(c.isupper() for c in value)
            
            # Using 'and' is a critical change to reduce false positives.
            if (has_digit and has_lower and has_upper) and self._calculate_entropy(value) > self.ENTROPY_THRESHOLD:
                findings.append(Finding(match.start(), match.end(), value, self.tag, self.name))
                # The claimed_indices logic is now correctly applied in all passes.
                claimed_indices.update(range(match.start(), match.end()))
        
        return findings