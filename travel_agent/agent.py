"""
agent.py — Google ADK multi-agent system for the Smart Travel Advisor.

Architecture (ADK native):
  root_agent (LlmAgent — Gemini coordinator)
      └── parallel_research_agent (ParallelAgent — fan-out/gather)
              ├── weather_agent  (LlmAgent — calls get_current_weather)
              └── fx_agent       (LlmAgent — calls get_exchange_rate)

Flow:
  1. User message → root_agent (Gemini) understands intent.
  2. root_agent delegates to parallel_research_agent via AgentTool.
  3. ParallelAgent fans out: weather_agent and fx_agent run concurrently.
  4. Both agents call their respective FunctionTools (live APIs).
  5. Results gather back, root_agent synthesizes a final travel briefing.
"""

from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.tools import agent_tool

from travel_agent.tools import (
    get_current_weather,
    get_exchange_rate,
    list_supported_cities,
)

# ── Sub-Agent 1: Weather Specialist ──────────────────────────────────────────
weather_agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description=(
        "A specialist weather analyst. Given a city name, fetches live weather "
        "conditions from Open-Meteo and provides temperature, conditions, and "
        "clothing/packing recommendations."
    ),
    instruction="""You are a specialist Travel Weather Analyst.

Your job:
1. Call `get_current_weather` with the city the user wants to visit.
2. If the city is not supported, call `list_supported_cities` and suggest alternatives.
3. Return a clear, friendly summary including:
   - Current temperature (°C and °F)
   - Weather conditions
   - Wind speed
   - Precipitation chance
   - Specific outfit and packing advice

Always be concise and practical. Focus on what the traveler needs to know to pack correctly.
""",
    tools=[get_current_weather, list_supported_cities],
)

# ── Sub-Agent 2: FX / Currency Specialist ────────────────────────────────────
fx_agent = LlmAgent(
    name="fx_agent",
    model="gemini-2.0-flash",
    description=(
        "A specialist foreign exchange broker. Given two currency codes, fetches "
        "live exchange rates from CoinCap and provides conversion tables and "
        "spending power advice for travelers."
    ),
    instruction="""You are an International Foreign Exchange Advisor for travelers.

Your job:
1. Call `get_exchange_rate` with the base and target currency codes.
2. Return a practical summary including:
   - The current exchange rate (1 unit of base = X target)
   - The inverse rate
   - A conversion table for common amounts (10, 50, 100, 500, 1000)
   - Practical advice on spending power and budgeting at the destination

Common currency codes: USD, EUR, GBP, JPY, AED, AUD, CAD, SGD, THB, TRY, MXN, ZAR, INR, KRW.
Always be clear and give actionable financial context for the traveler.
""",
    tools=[get_exchange_rate],
)

# ── Parallel Orchestrator: runs both sub-agents concurrently ──────────────────
parallel_research_agent = ParallelAgent(
    name="parallel_research_agent",
    description=(
        "Orchestrates weather and FX sub-agents in parallel. "
        "Use this when the user needs both weather and currency information."
    ),
    sub_agents=[weather_agent, fx_agent],
)

# ── Root Planner: Gemini LLM coordinator — the user-facing entry point ────────
root_agent = LlmAgent(
    name="travel_concierge",
    model="gemini-2.0-flash",
    description="A luxury travel concierge that provides live weather and currency advice.",
    instruction="""You are an expert Luxury Travel Concierge powered by Google ADK.

You help travelers with two specialist capabilities:
- **Weather intelligence**: Live conditions, temperatures, packing and outfit advice.
- **Currency exchange**: Live FX rates, conversion tables, and spending power guidance.

## How to handle requests

**Weather only** (e.g., "What's the weather in Tokyo?", "What should I pack for Paris?"):
→ Delegate to `weather_agent` using agent_tool.

**Currency only** (e.g., "Convert USD to EUR", "How far will my GBP go in Japan?"):
→ Delegate to `fx_agent` using agent_tool.

**Both weather and currency** (e.g., "I'm visiting London — weather and USD to GBP?"):
→ Delegate to `parallel_research_agent` to run both agents concurrently.

## Response style
- Greet the user warmly and professionally.
- After receiving results from sub-agents, synthesize them into a cohesive travel briefing.
- Be specific, practical, and friendly.
- If follow-up questions arise, answer conversationally using context from previous turns.
- For unsupported cities, suggest nearby supported alternatives.

## Session memory
Use the conversation history to remember:
- The user's destination city
- Their home/spending currency
- Any previous preferences they mentioned

You are the primary interface. Always respond in natural language after delegating to sub-agents.
""",
    tools=[
        agent_tool.AgentTool(agent=weather_agent),
        agent_tool.AgentTool(agent=fx_agent),
        agent_tool.AgentTool(agent=parallel_research_agent),
    ],
)
