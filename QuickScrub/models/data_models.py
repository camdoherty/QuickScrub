from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# --- Pydantic Models (External API Contract) ---

class ScrubRequest(BaseModel):
    """The request model for the /api/scrub endpoint."""
    text: str = Field(..., description="The input text to be scrubbed.")
    types: List[str] = Field(..., description="A list of PII type tags to scrub (e.g., ['IP_ADDRESS', 'EMAIL']).")
    allow_list: Optional[List[str]] = Field(default_factory=list, description="A list of values to ignore during scrubbing.")

class LegendItem(BaseModel):
    """Represents a single entry in the response legend."""
    original: str
    mock: str
    type: str

class ScrubResponse(BaseModel):
    """The response model for the /api/scrub endpoint."""
    scrubbed_text: str
    legend: List[LegendItem]

# --- Internal Dataclasses (Core Engine Contract) ---

@dataclass(frozen=True)
class ScrubTask:
    """Internal data structure for passing a scrub job to the Core Engine."""
    text: str
    types: List[str]
    allow_list: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ScrubResult:
    """Internal data structure for returning a result from the Core Engine."""
    scrubbed_text: str
    legend: List[Dict[str, str]]
