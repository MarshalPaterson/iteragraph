from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    task: str
    plan: List[str]
    research_data: Optional[str]
    is_complete: bool
    iterations: int
    max_iterations: int
    model: Optional[str]
    provider: Optional[str]


class ResearchRequest(BaseModel):
    task: str
    max_iterations: int = Field(default=3, ge=1, le=10)
    model: Optional[str] = None
    provider: Optional[str] = None


class ResearchResponse(BaseModel):
    task: str
    plan: List[str]
    research_data: str
    is_complete: bool
    iterations: int
    model: Optional[str] = None
    provider: Optional[str] = None