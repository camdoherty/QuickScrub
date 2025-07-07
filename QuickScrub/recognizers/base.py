from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True, order=True)
class Finding:
    """An immutable data object representing a single piece of PII found in text.
    'order=True' automatically makes this class comparable, first by 'start'
    index, then by 'end' index, critical for conflict resolution."""
    start: int
    end: int
    value: str
    type: str
    recognizer_name: str

class Recognizer(ABC):
    """The abstract base class for all PII recognizer plugins."""
    def __init__(self, name: str, tag: str):
        if not name or not tag:
            raise ValueError("Recognizer name and tag cannot be empty.")
        self.name = name
        self.tag = tag

    @abstractmethod
    def analyze(self, text: str) -> List[Finding]:
        """Scans the input text and returns a list of all findings."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', tag='{self.tag}')>"
