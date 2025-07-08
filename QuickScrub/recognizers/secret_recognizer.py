import re
import math
from typing import List, Set
from .base import Recognizer, Finding

class SecretRecognizer(Recognizer):
    """
    Recognizes secrets and keys using a multi-pass approach.

    1.  Finds high-confidence keys based on common prefixes.
    2.  Finds medium-confidence keys based on variable names.
    3.  Finds lower-confidence generic keys based on high Shannon entropy.
    """
    # Common prefixes for API keys from various services (e.g., Stripe, GitHub)
    PREFIX_REGEX = re.compile(r'\b((?:sk|pk|rk)_(?:live|test)_[a-zA-Z0-9]{20,}|gh[pousr]_[a-zA-Z0-9]{30,})\b')

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
        # Calculate frequency of each character
        char_counts = {c: text.count(c) for c in set(text)}
        # Calculate Shannon entropy
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
            # The actual secret is in group 2. We need its start position.
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
            # Check for sufficient character variety to be a plausible key
            has_digit = any(c.isdigit() for c in value)
            has_lower = any(c.islower() for c in value)
            has_upper = any(c.isupper() for c in value)

            if (has_digit and has_lower and has_upper) or self._calculate_entropy(value) > self.ENTROPY_THRESHOLD:
                findings.append(Finding(match.start(), match.end(), value, self.tag, self.name))
                claimed_indices.update(range(match.start(), match.end()))
        
        return findings