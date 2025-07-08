# FILE: QuickScrub/recognizers/sensitive_url_recognizer.py

import re
from typing import List, Set
from urllib.parse import urlparse, parse_qs
from .base import Recognizer, Finding

class SensitiveUrlRecognizer(Recognizer):
    """
    Recognizes URLs containing sensitive info, with special handling for Markdown links.
    """
    # Regex to find a URL that might be sensitive.
    BARE_URL_REGEX = re.compile(
        r'\b(?:(?:https?|ftp)://|www\.)[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
        re.IGNORECASE
    )
    
    # Regex to find a Markdown link where the href part is a potentially sensitive URL.
    MARKDOWN_URL_REGEX = re.compile(r'(\[[^\]]*\]\(' + BARE_URL_REGEX.pattern + r'\))')

    SENSITIVE_KEYS: Set[str] = {
        'token', 'key', 'session', 'password', 'secret', 'apikey', 'auth',
        'access_token', 'session_id', 'session_key', 'auth_token', 'client_secret',
        'code'  # Added to catch password reset codes, etc.
    }

    def __init__(self):
        super().__init__(name="Sensitive URL", tag="SENSITIVE_URL")

    def _is_sensitive(self, url_string: str) -> bool:
        """Checks if a given URL string contains sensitive query parameters."""
        try:
            if not url_string.startswith(('http://', 'https://', 'ftp://')):
                parsed_url = urlparse(f"http://{url_string}")
            else:
                parsed_url = urlparse(url_string)
            
            if not parsed_url.query:
                return False
            
            query_params = parse_qs(parsed_url.query)
            return any(key.lower() in self.SENSITIVE_KEYS for key in query_params)
        except Exception:
            return False

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        claimed_spans = []

        # Pass 1: Find sensitive URLs within Markdown links.
        for match in self.MARKDOWN_URL_REGEX.finditer(text):
            # The URL part is inside the main match group.
            # We need to extract it to check for sensitivity.
            url_part_match = self.BARE_URL_REGEX.search(match.group(0))
            if url_part_match and self._is_sensitive(url_part_match.group(0)):
                # If sensitive, claim the ENTIRE markdown link.
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))
                claimed_spans.append(range(match.start(), match.end()))

        # Pass 2: Find bare sensitive URLs, avoiding those already claimed.
        for match in self.BARE_URL_REGEX.finditer(text):
            is_claimed = False
            for span in claimed_spans:
                if match.start() in span:
                    is_claimed = True
                    break
            if not is_claimed and self._is_sensitive(match.group(0)):
                findings.append(Finding(match.start(), match.end(), match.group(0), self.tag, self.name))

        return findings
