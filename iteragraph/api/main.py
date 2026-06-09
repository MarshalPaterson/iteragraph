import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from iteragraph.core.agent_state import ResearchRequest, ResearchResponse
from iteragraph.core.research_graph import iteragraph_app
from iteragraph.core.memory import vector_store
from iteragraph.core.observability import observability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="iteragraph Research Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "iteragraph"}


@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    with observability.trace("research_task"):
        context = []
        
        if request.task:
            context = vector_store.search(request.task)
        
        initial_state: dict = {
            "task": request.task,
            "plan": [],
            "research_data": None,
            "is_complete": False,
            "iterations": 0,
            "max_iterations": request.max_iterations,
            "model": request.model,
            "provider": request.provider
        }
        
        try:
            result = iteragraph_app.invoke(initial_state)
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
        if result.get("research_data"):
            vector_store.add_memory(
                content=result["research_data"],
                metadata={"task": request.task, "iterations": result.get("iterations", 1)}
            )
        
        return ResearchResponse(
            task=result["task"],
            plan=result.get("plan", []),
            research_data=result.get("research_data", ""),
            is_complete=result.get("is_complete", True),
            iterations=result.get("iterations", 1),
            model=result.get("model"),
            provider=result.get("provider")
        )


@app.get("/memory/search")
async def search_memory(q: str, limit: int = 5):
    results = vector_store.search(q, limit)
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)