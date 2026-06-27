"""
server.py — FastAPI server wrapping the ADK multi-agent system.

Exposes:
  POST /api/chat          — single-turn chat (returns JSON)
  POST /api/chat/stream   — streaming chat (Server-Sent Events)
  GET  /api/session/new   — create a new ADK session (for multi-turn memory)
  GET  /health            — health check
  GET  /docs              — auto-generated Swagger UI (FastAPI built-in)

The ADK Runner manages session state so follow-up messages remember
the city/currency context from earlier in the conversation.
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ADK runtime imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Our agent
from travel_agent.agent import root_agent

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Travel Advisor AI — Google ADK",
    description="Multi-agent travel concierge powered by Google ADK + Gemini",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ADK session service (in-memory; swap for VertexAI session service in prod) ─
session_service = InMemorySessionService()

APP_NAME = "travel_advisor"
USER_ID = "web_user"  # In production, derive from auth token


def _make_runner() -> Runner:
    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )


# ── Request / Response models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # omit to start a new conversation


class NewSessionResponse(BaseModel):
    session_id: str


# ── Helpers ───────────────────────────────────────────────────────────────────
async def _run_agent(session_id: str, message: str) -> str:
    """Run the ADK agent and collect the full text response."""
    runner = _make_runner()
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )
    full_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    full_text += part.text
    return full_text or "I'm sorry, I couldn't generate a response. Please try again."


async def _stream_agent(session_id: str, message: str) -> AsyncGenerator[str, None]:
    """Stream ADK agent tokens as SSE events."""
    runner = _make_runner()
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    payload = json.dumps({"token": part.text, "done": event.is_final_response()})
                    yield f"data: {payload}\n\n"
    yield "data: {\"token\": \"\", \"done\": true}\n\n"


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "agent": root_agent.name, "framework": "google-adk"}


@app.get("/api/session/new", response_model=NewSessionResponse)
async def new_session():
    """Create a fresh ADK session. Pass the returned session_id in subsequent /api/chat calls."""
    sid = str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=sid,
    )
    return {"session_id": sid}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Single-turn (or multi-turn if session_id is supplied) chat with the ADK agent.
    Returns the full response as JSON once the agent finishes.
    """
    if not req.message.strip():
        raise HTTPException(400, "message cannot be empty")

    # Auto-create session if not provided
    session_id = req.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )

    try:
        response_text = await _run_agent(session_id, req.message)
    except Exception as exc:
        raise HTTPException(500, f"Agent error: {exc}") from exc

    return {
        "session_id": session_id,
        "response": response_text,
        "agent": root_agent.name,
    }


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Streaming chat — returns Server-Sent Events so the frontend can render
    tokens progressively as Gemini generates them.
    """
    if not req.message.strip():
        raise HTTPException(400, "message cannot be empty")

    session_id = req.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )

    return StreamingResponse(
        _stream_agent(session_id, req.message),
        media_type="text/event-stream",
        headers={
            "X-Session-Id": session_id,
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
