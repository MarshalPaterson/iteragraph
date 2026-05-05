from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    task: str
    plan: List[str]
    research_data: Optional[str]
    is_complete: bool
    iterations: int
    max_iterations: int


class ResearchRequest(BaseModel):
    task: str
    max_iterations: int = Field(default=3, ge=1, le=10)


class ResearchResponse(BaseModel):
    task: str
    plan: List[str]
    research_data: str
    is_complete: bool
    iterations: int