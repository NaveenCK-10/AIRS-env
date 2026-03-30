
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Observation(BaseModel):
    incident_id: str
    alert: str
    logs: List[str]
    system_status: Dict[str, str]
    step: int
    version: str
    hint: Optional[str] = None

class Action(BaseModel):
    diagnosis: Optional[str] = None
    action: str
    reason: Optional[str] = ""

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]


class GradeRequest(BaseModel):
    diagnosis: str
    action: str
    reason: str
