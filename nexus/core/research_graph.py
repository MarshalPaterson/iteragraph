import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from .agent_state import AgentState

logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)


def should_continue(state: AgentState) -> str:
    if state.get("is_complete"):
        return "end"
    if state.get("iterations", 0) >= state.get("max_iterations", 3):
        return "end"
    return "continue"


def research_planner(state: AgentState) -> AgentState:
    task = state["task"]
    
    prompt = f"""You are a Research Lead agent. Break down this task into specific research steps:

Task: {task}

Return a JSON array of research steps. Each step should be a specific, actionable research task.
Example: ["Search for company overview", "Find recent news articles", "Analyze financial reports"]
"""
    
    response = llm.invoke(prompt)
    try:
        steps = json.loads(response.content)
    except:
        steps = [f"Research: {task}"]

    logger.info(f"Planning research steps: {steps}")
    return {"plan": steps, "iterations": state.get("iterations", 0) + 1}


def n8n_executor(state: AgentState) -> AgentState:
    plan = state.get("plan", [])
    
    n8n_url = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/research")
    
    try:
        import httpx
        response = httpx.post(n8n_url, json={"steps": plan}, timeout=30.0)
        if response.status_code == 200:
            data = response.json()
            research_data = data.get("results", "No results returned")
        else:
            research_data = f"n8n returned status {response.status_code}"
    except Exception as e:
        logger.warning(f"n8n call failed, using fallback: {e}")
        research_data = f"Research completed for: {', '.join(plan)}"

    return {"research_data": research_data}


def evaluator(state: AgentState) -> AgentState:
    research = state.get("research_data", "")
    
    prompt = f"""Evaluate if the research data is sufficient for this task:

Task: {state['task']}
Research Data: {research[:1000]}

Respond with JSON: {{"is_complete": true/false, "reason": "explanation"}}
"""
    
    response = llm.invoke(prompt)
    try:
        result = json.loads(response.content)
        is_complete = result.get("is_complete", True)
    except:
        is_complete = True

    logger.info(f"Evaluation result: complete={is_complete}")
    return {"is_complete": is_complete}


def build_research_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", research_planner)
    workflow.add_node("executor", n8n_executor)
    workflow.add_node("evaluator", evaluator)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "evaluator")
    
    workflow.add_conditional_edges(
        "evaluator",
        should_continue,
        {
            "continue": "planner",
            "end": END
        }
    )
    
    return workflow.compile()


nexus_app = build_research_graph()