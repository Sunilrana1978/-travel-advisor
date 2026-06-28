# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install google-adk==1.3.0 && pip install -r requirements.txt
cp .env.example .env   # then set GOOGLE_API_KEY
```

## Running the project

**ADK dev UI** (agent trace visualisation, recommended for testing):
```bash
adk web .          # → http://localhost:8000
adk run travel_agent  # terminal chat
```

**REST API + React frontend** (two terminals):
```bash
uvicorn server:app --reload --port 8080   # backend → http://localhost:8080/docs
cd frontend && npm install && npm run dev  # frontend → http://localhost:3000
```

**Full Docker stack:**
```bash
docker compose up --build
```

**GCP deploy:**
```bash
./deploy-gcp.sh --project YOUR_GCP_PROJECT_ID --api-key YOUR_GOOGLE_API_KEY
```

## Architecture

The agent system lives entirely in `travel_agent/`:

- **`agent.py`** — defines the three-layer ADK hierarchy:
  - `root_agent` (`LlmAgent`, Gemini) — user-facing planner that routes intent via `AgentTool`
  - `parallel_research_agent` (`ParallelAgent`) — fans out to `weather_agent` and `fx_agent` concurrently
  - `weather_agent` / `fx_agent` (`LlmAgent`) — each calls one `FunctionTool` and returns structured results
- **`tools.py`** — three plain Python functions that become ADK `FunctionTool`s: `get_current_weather` (Open-Meteo API), `get_exchange_rate` (CoinCap API), `list_supported_cities`. No API keys needed for these tools.
- **`__init__.py`** — re-exports `root_agent` so `adk web .` and `adk run travel_agent` discover it automatically.

**`server.py`** wraps the ADK runtime in FastAPI:
- `POST /api/chat` — blocking JSON response
- `POST /api/chat/stream` — Server-Sent Events, returns `X-Session-Id` header
- `GET /api/session/new` — creates an `InMemorySessionService` session for multi-turn memory

**`frontend/src/App.jsx`** — React SPA that streams from `/api/chat/stream`, infers which agents fired from the response text, and displays trace chips. Backend URL is `VITE_API_URL` env var (defaults to `http://localhost:8080`).

## Key conventions

**Adding a new city**: edit `CITY_COORDS` in `travel_agent/tools.py`.

**Adding a new sub-agent**: define an `LlmAgent` in `agent.py`, add it to `parallel_research_agent.sub_agents`, and wrap it in an `AgentTool` for `root_agent.tools`.

**Switching to Vertex AI**: set `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=us-central1`, and `GOOGLE_GENAI_USE_VERTEXAI=true` in `.env`; remove `GOOGLE_API_KEY`. The ADK picks these up automatically.

**Session state**: currently `InMemorySessionService` — sessions are lost on restart. For production, swap for the Vertex AI session service in `server.py`.

**Tool docstrings are functional**: Gemini reads them to determine when and how to call each tool. Keep them accurate.
