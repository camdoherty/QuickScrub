import re
from typing import List, Set
from urllib.parse import urlparse, parse_qs
from .base import Recognizer, Finding

class SensitiveUrlRecognizer(Recognizer):
    """
    Recognizes URLs that contain sensitive information in their query parameters.
    """
    # A robust regex for finding URLs. It looks for a scheme or 'www.' to reduce false positives.
    URL_REGEX = re.compile(
        r'\b(?:(?:https?|ftp)://|www\.)[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
        re.IGNORECASE
    )

    # A set of common keywords found in query parameters that indicate sensitive data.
    SENSITIVE_KEYS: Set[str] = {
        'token', 'key', 'session', 'password', 'secret', 'apikey', 'auth',
        'access_token', 'session_id', 'session_key', 'auth_token', 'client_secret'
    }

    def __init__(self):
        super().__init__(name="Sensitive URL", tag="SENSITIVE_URL")

    def analyze(self, text: str) -> List[Finding]:
        findings = []
        for match in self.URL_REGEX.finditer(text):
            url_string = match.group(0)
            try:
                # Add a scheme if missing, as urlparse requires it for proper parsing
                if not url_string.startswith(('http://', 'https://', 'ftp://')):
                    parsed_url = urlparse(f"http://{url_string}")
                else:
                    parsed_url = urlparse(url_string)

                if not parsed_url.query:
                    continue
                
                # parse_qs returns a dict where values are lists
                query_params = parse_qs(parsed_url.query)
                
                # Check if any parameter key is in our sensitive set
                for key in query_params:
                    if key.lower() in self.SENSITIVE_KEYS:
                        # If a sensitive key is found, flag the entire URL
                        findings.append(Finding(match.start(), match.end(), url_string, self.tag, self.name))
                        break # Move to the next URL match
            except Exception:
                # Ignore malformed URLs that the regex might have picked up
                continue
        return findings