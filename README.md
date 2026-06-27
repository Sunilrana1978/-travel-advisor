# ✈️ Travel Advisor AI — Google ADK Edition

A production-ready multi-agent travel concierge built with **Google Agent Development Kit (ADK)** and **Gemini 2.0 Flash**. Uses real ADK agent classes, `ParallelAgent` orchestration, `FunctionTool` API calls, and session memory — deployed to **GCP Cloud Run**.

---

## Architecture

```
User Message
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│  root_agent  (LlmAgent — Gemini 2.0 Flash)              │
│  "travel_concierge"                                      │
│                                                          │
│  Understands intent, decides which agent(s) to invoke   │
│  via AgentTool delegation                                │
└──────────┬──────────────────┬───────────────────────────┘
           │                  │
    (AgentTool)         (AgentTool)
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌────────────────────────────────┐
│  weather_agent   │  │  parallel_research_agent        │
│  (LlmAgent)      │  │  (ParallelAgent — ADK native)   │
│                  │  │                                  │
│  FunctionTool:   │  │  ┌──────────────┐  ┌─────────┐ │
│  get_current_    │  │  │weather_agent │  │fx_agent │ │
│  weather()       │  │  │(concurrent)  │  │(concurr)│ │
└──────────────────┘  │  └──────────────┘  └─────────┘ │
                      └────────────────────────────────┘
           │
    (AgentTool)
           │
           ▼
┌──────────────────┐
│  fx_agent        │
│  (LlmAgent)      │
│                  │
│  FunctionTool:   │
│  get_exchange_   │
│  rate()          │
└──────────────────┘
```

### ADK Components Used

| ADK Concept | What it does in this project |
|---|---|
| `LlmAgent` | `root_agent`, `weather_agent`, `fx_agent` — Gemini-powered reasoning |
| `ParallelAgent` | `parallel_research_agent` — runs Weather + FX agents concurrently |
| `FunctionTool` | `get_current_weather()`, `get_exchange_rate()` — live API calls |
| `AgentTool` | Root agent delegates to sub-agents dynamically |
| `Runner` | Executes agents with session management |
| `InMemorySessionService` | Multi-turn conversation memory |
| `adk run` / `adk web` | Local development CLI and UI |

---

## Project Structure

```
travel-advisor-adk/
├── travel_agent/
│   ├── __init__.py        # Exposes root_agent for `adk run`
│   ├── agent.py           # All ADK agent definitions
│   └── tools.py           # FunctionTools (Open-Meteo + CoinCap)
├── server.py              # FastAPI wrapper (REST + SSE streaming)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── cloudbuild.yaml        # GCP CI/CD pipeline
├── deploy-gcp.sh          # One-command GCP deploy
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # React chat UI with streaming + session
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
└── travel-advisor-adk.code-workspace
```

---

## Quick Start — Local Development

### Prerequisites
- Python 3.10+
- Node 20+
- A Google API Key (free): https://aistudio.google.com/app/apikey

### 1. Set up Python environment

```bash
cd travel-advisor-adk
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your_key_here
```

### 3a. Run with ADK CLI (recommended for testing agents)

```bash
# Interactive terminal chat
adk run travel_agent

# Built-in browser UI with agent trace visualization
adk web .
# Open http://localhost:8000
```

### 3b. Run as REST API + React frontend

```bash
# Terminal 1 — backend
uvicorn server:app --reload --port 8080

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 3c. Docker Compose (full stack)

```bash
docker compose up --build
# Frontend → http://localhost:3000
# Backend  → http://localhost:8080
# API Docs → http://localhost:8080/docs
```

---

## GCP Deployment

### Prerequisites
- `gcloud` CLI installed and authenticated
- A GCP project with billing enabled

### Deploy (one command)

```bash
chmod +x deploy-gcp.sh

./deploy-gcp.sh \
  --project YOUR_GCP_PROJECT_ID \
  --api-key YOUR_GOOGLE_API_KEY
```

This script:
1. Enables Cloud Run, Cloud Build, Container Registry, Secret Manager APIs
2. Stores `GOOGLE_API_KEY` in Secret Manager (never in code or env file)
3. Grants IAM roles for Cloud Build and Cloud Run
4. Builds and pushes both Docker images via Cloud Build
5. Deploys backend (API key injected from Secret Manager at runtime)
6. Deploys frontend (backend URL baked in at build time)
7. Prints live URLs

### Expected output

```
✅  DEPLOYMENT COMPLETE

  🌐 Frontend  : https://travel-advisor-frontend-xxxx-uc.a.run.app
  ⚙️  Backend   : https://travel-advisor-backend-xxxx-uc.a.run.app
  📖 API Docs  : https://travel-advisor-backend-xxxx-uc.a.run.app/docs
  🩺 Health    : https://travel-advisor-backend-xxxx-uc.a.run.app/health
```

---

## API Reference

### `POST /api/chat`
Multi-turn chat. Omit `session_id` to auto-create a new session.
```json
{ "message": "Weather in Tokyo and USD to JPY?", "session_id": "optional-uuid" }
```
Response:
```json
{ "session_id": "uuid", "response": "...", "agent": "travel_concierge" }
```

### `POST /api/chat/stream`
Same as above but returns Server-Sent Events for token-by-token streaming.
Response header: `X-Session-Id: uuid`
SSE format: `data: {"token": "...", "done": false}`

### `GET /api/session/new`
Creates a fresh ADK session for a new conversation.
```json
{ "session_id": "uuid" }
```

---

## Key Differences vs. v1 (no ADK)

| Feature | v1 (plain Python) | v2 (Google ADK) |
|---|---|---|
| Intent routing | Regex keyword matching | Gemini LLM reasoning |
| Agent orchestration | `asyncio.gather()` | `ParallelAgent` (ADK native) |
| Tool calling | Direct function calls | ADK `FunctionTool` with docstring schema |
| Memory | Stateless | ADK session state (multi-turn) |
| Dev UI | None | `adk web` — built-in agent trace viewer |
| Follow-up questions | Not supported | ✅ Session memory persists context |
| Model | None | Gemini 2.0 Flash |

---

## Extending

### Add a new city
Edit `CITY_COORDS` in `travel_agent/tools.py`.

### Add a new sub-agent (e.g., hotel recommendations)
```python
# agent.py
hotel_agent = LlmAgent(
    name="hotel_agent",
    model="gemini-2.0-flash",
    instruction="You find hotel recommendations...",
    tools=[search_hotels],  # your FunctionTool
)

# Add to parallel_research_agent.sub_agents and root_agent.tools
```

### Switch to Vertex AI (enterprise)
In `.env`:
```
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
```
Remove `GOOGLE_API_KEY`. The ADK picks this up automatically.
