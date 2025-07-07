import pkgutil
import inspect
import logging
from typing import List, Dict
from ..recognizers.base import Recognizer, Finding
from .. import recognizers as recognizers_package

class RecognizerRegistry:
    """Discovers, loads, and manages all available Recognizer plugins."""
    def __init__(self):
        self.recognizers: Dict[str, Recognizer] = {}
        self._discover_recognizers()

    def _discover_recognizers(self):
        """Dynamically imports and instantiates all Recognizer classes."""
        for _, name, _ in pkgutil.iter_modules(recognizers_package.__path__):
            try:
                module = __import__(f"{recognizers_package.__name__}.{name}", fromlist=[""])
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, Recognizer) and cls is not Recognizer:
                        instance = cls()
                        if instance.tag in self.recognizers:
                            logging.warning(f"Duplicate recognizer tag '{instance.tag}' found. Overwriting.")
                        self.recognizers[instance.tag] = instance
            except Exception as e:
                logging.error(f"Failed to load recognizer module {name}: {e}", exc_info=True)

        logging.info(f"Discovered recognizers: {list(self.recognizers.keys())}")

    def get_findings(self, text: str, requested_types: List[str]) -> List[Finding]:
        """Runs requested recognizers and returns all findings."""
        all_findings = []
        for pii_type in requested_types:
            if recognizer := self.recognizers.get(pii_type):
                try:
                    findings = recognizer.analyze(text)
                    all_findings.extend(findings)
                except Exception as e:
                    logging.error(f"Error running recognizer '{recognizer.name}': {e}", exc_info=True)
        return all_findings
