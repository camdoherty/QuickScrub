from fastapi import APIRouter, Depends
from ..models.data_models import ScrubRequest, ScrubResponse, LegendItem, ScrubTask
from ..core.engine import ScrubberEngine
from ..core.registry import RecognizerRegistry

router = APIRouter()

# --- Singleton Instances ---
ENGINE_INSTANCE = ScrubberEngine()
REGISTRY_INSTANCE = RecognizerRegistry()

# --- Dependency Injection Functions ---
def get_engine() -> ScrubberEngine: return ENGINE_INSTANCE
def get_registry() -> RecognizerRegistry: return REGISTRY_INSTANCE

# --- API Endpoint ---
@router.post("/scrub", response_model=ScrubResponse)
async def scrub_text(
    request: ScrubRequest,
    engine: ScrubberEngine = Depends(get_engine),
    registry: RecognizerRegistry = Depends(get_registry)
):
    task = ScrubTask(text=request.text, types=request.types, allow_list=request.allow_list or [])
    all_findings = registry.get_findings(task.text, task.types)
    result = engine.scrub(task, all_findings)
    return ScrubResponse(
        scrubbed_text=result.scrubbed_text,
        legend=[LegendItem(**item) for item in result.legend]
    )
