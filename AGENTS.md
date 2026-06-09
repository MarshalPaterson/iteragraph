# iteragraph Multi-Agent System - AI Concepts

## Overview
iteragraph is a Multi-Agent Research & Automation Engine that implements a sophisticated agent workflow using LangGraph for iterative research tasks.

## Key AI Components

### 1. Agent Architecture
- **LangGraph StateGraph**: Implements a directed graph workflow with nodes representing agent functions
- **Iterative Processing**: Uses conditional edges to loop between planner, executor, and evaluator until completion criteria are met
- **State Management**: Maintains agent state through TypedDict with fields for task, plan, research_data, completion status, iteration counters, and selected model

### 2. Specialized Agents
- **Research Planner**: 
  - Role: Breaks down high-level tasks into specific, actionable research steps
  - Implementation: Uses LLM (configurable — GPT-4o or any OpenRouter model) to generate JSON array of research steps
  - Prompt Engineering: Structured prompt that defines expected output format

- **n8n Executor**:
  - Role: Executes research steps via external automation (n8n) or local fallback
  - Implementation: Makes HTTP POST requests to n8n webhook with research steps
  - Fallback Mechanism: Provides local research simulation when n8n is unavailable

- **Evaluator**:
  - Role: Assesses whether research data sufficiently addresses the original task
  - Implementation: Uses LLM to evaluate research completeness with JSON output expectation
  - Decision Logic: Returns boolean completion status with reasoning

### 3. AI/ML Technologies
- **Language Model**: ChatOpenAI with GPT-4o model (temperature 0.7 for balanced creativity/consistency). Model can be overridden via API — supports any OpenRouter model (including free open models).
- **Structured Output**: JSON parsing with fallback handling for LLM responses
- **Prompt Engineering**: Carefully crafted prompts for each agent role with clear instructions and examples

### 4. Workflow Patterns
- **Conditional Looping**: Evaluator decides whether to continue planning or end based on:
  - Completion flag from evaluation
  - Iteration count vs. max_iterations threshold
- **Error Handling**: Graceful degradation with fallback mechanisms (local research simulation)
- **Logging**: Comprehensive logging for monitoring agent decisions and workflow progression

### 5. Data Structures
- **AgentState TypedDict**: Defines the schema for state persistence between workflow steps (includes optional `model` field for model selection)
- **Pydantic Models**: ResearchRequest and ResearchResponse for API validation and serialization
- **Type Safety**: Strong typing throughout for reliable state transitions

## Implementation Details
- **Modular Design**: Separation of concerns with distinct files for state, core logic, and API
- **Environment Configuration**: Uses dotenv for configuration management
- **Extensibility**: Easy to add new agent types or modify workflow connections
- **Production Ready**: Includes proper error handling, timeouts, and logging

## Usage Pattern
1. User submits a research task
2. Planner breaks task into steps
3. Executor performs research (via n8n or fallback)
4. Evaluator checks if research is sufficient
5. If not sufficient and iterations remain, loop back to planner
6. If sufficient or max iterations reached, return results

This creates an intelligent, self-improving research pipeline that adapts based on evaluation feedback.