import { useState, useRef, useEffect, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";

// ── Markdown-lite renderer (bold, bullets) ────────────────────────────────────
function renderText(text) {
  if (!text) return null;
  return text.split("\n").map((line, i) => {
    const bold = line.replace(/\*\*(.*?)\*\*/g, (_, m) => `<strong>${m}</strong>`);
    const bullet = bold.startsWith("- ") || bold.startsWith("• ");
    return bullet ? (
      <li key={i} dangerouslySetInnerHTML={{ __html: bold.replace(/^[-•]\s*/, "") }} />
    ) : (
      <p key={i} dangerouslySetInnerHTML={{ __html: bold }} />
    );
  });
}

// ── Agent step indicator ──────────────────────────────────────────────────────
function AgentTrace({ steps }) {
  if (!steps?.length) return null;
  return (
    <div className="agent-trace">
      {steps.map((s, i) => (
        <span key={i} className="trace-chip">{s}</span>
      ))}
    </div>
  );
}

// ── Message bubble ────────────────────────────────────────────────────────────
function Message({ msg }) {
  if (msg.role === "user") {
    return (
      <div className="msg-row user-row">
        <div className="bubble user-bubble">{msg.content}</div>
        <div className="avatar user-av">You</div>
      </div>
    );
  }

  return (
    <div className="msg-row bot-row">
      <div className="avatar bot-av">✈️</div>
      <div className="bubble bot-bubble">
        {msg.loading && !msg.content ? (
          <div className="loading-dots">
            <span /><span /><span />
          </div>
        ) : (
          <>
            <AgentTrace steps={msg.agentSteps} />
            <div className="response-text">
              {renderText(msg.content)}
            </div>
            {msg.streaming && <span className="cursor">▊</span>}
          </>
        )}
      </div>
    </div>
  );
}

// ── Suggestion chips ──────────────────────────────────────────────────────────
const SUGGESTIONS = [
  "I'm visiting Tokyo next week — what's the weather and how far will USD go in JPY?",
  "What should I pack for Paris right now? Also EUR to GBP rate?",
  "Is it a good time to visit Dubai weather-wise? I'm spending USD.",
  "Compare London weather with what I should know about GBP exchange for my trip.",
  "What's the current weather in Singapore and AUD to SGD conversion?",
  "Planning a Rome trip — weather conditions and USD to EUR please.",
];

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages]     = useState([
    {
      id: 0, role: "bot",
      content: "Hi! I'm your AI Travel Concierge 🌍 — powered by **Google ADK** and **Gemini**.\n\nAsk me about weather at your destination, what to pack, or how your currency converts. I use specialist sub-agents running in parallel to fetch live data for you.",
    },
  ]);
  const [input, setInput]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [sessionId, setSessionId]   = useState(null);
  const [agentStatus, setAgentStatus] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialise ADK session on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/session/new`)
      .then(r => r.json())
      .then(d => setSessionId(d.session_id))
      .catch(() => {}); // session auto-created on first chat if this fails
  }, []);

  const detectAgentSteps = (text) => {
    const steps = [];
    if (/weather|temperature|rain|snow|wind|cloud/i.test(text)) steps.push("🌤 Weather Agent");
    if (/exchange|rate|currency|convert|usd|eur|gbp|jpy/i.test(text)) steps.push("💱 FX Agent");
    if (steps.length > 1) steps.unshift("🧠 Root Planner → ParallelAgent");
    else if (steps.length === 1) steps.unshift("🧠 Root Planner");
    return steps;
  };

  const sendMessage = useCallback(async (text) => {
    const userMsg = (text || input).trim();
    if (!userMsg || loading) return;
    setInput("");
    setLoading(true);
    setAgentStatus("Routing to agents…");

    const uid = Date.now();
    const bid = uid + 1;

    setMessages(prev => [
      ...prev,
      { id: uid, role: "user", content: userMsg },
      { id: bid, role: "bot", content: "", loading: true, streaming: true },
    ]);

    try {
      const res = await fetch(`${API_BASE}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(`Server error ${res.status}`);

      // Capture session from response header if we didn't have one
      const newSid = res.headers.get("X-Session-Id");
      if (newSid && !sessionId) setSessionId(newSid);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";

      setAgentStatus("Agents working…");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n").filter(l => l.startsWith("data: "));

        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.token) {
              accumulated += data.token;
              setMessages(prev =>
                prev.map(m => m.id === bid
                  ? { ...m, content: accumulated, loading: false }
                  : m
                )
              );
            }
          } catch { /* skip malformed SSE lines */ }
        }
      }

      const steps = detectAgentSteps(accumulated);
      setMessages(prev =>
        prev.map(m => m.id === bid
          ? { ...m, streaming: false, agentSteps: steps }
          : m
        )
      );
      setAgentStatus("");

    } catch (err) {
      setMessages(prev =>
        prev.map(m => m.id === bid
          ? { ...m, content: `Sorry, I couldn't reach the travel advisor: ${err.message}`, loading: false, streaming: false }
          : m
        )
      );
      setAgentStatus("");
    } finally {
      setLoading(false);
    }
  }, [input, loading, sessionId]);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">✈</span>
            <div>
              <div className="logo-title">Travel Advisor AI</div>
              <div className="logo-sub">Google ADK · Gemini · ParallelAgent</div>
            </div>
          </div>
          <div className="agent-pills">
            <span className="pill pill-blue">🌤 Weather Agent</span>
            <span className="pill pill-green">💱 FX Agent</span>
            <span className="pill pill-purple">⚡ ParallelAgent</span>
            <span className="pill pill-gold">🧠 Gemini Planner</span>
          </div>
        </div>
      </header>

      {/* Chat */}
      <main className="chat-window">
        <div className="messages">
          {messages.map(m => <Message key={m.id} msg={m} />)}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Suggestions — visible until 3rd message */}
      {messages.length <= 2 && (
        <div className="suggestions">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} className="suggestion-chip" onClick={() => sendMessage(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Status bar */}
      {agentStatus && (
        <div className="status-bar">
          <span className="status-dot" />
          {agentStatus}
        </div>
      )}

      {/* Input */}
      <div className="input-bar">
        <div className="input-inner">
          <input
            className="text-input"
            placeholder="Ask about weather, packing, or currency conversions…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage()}
            disabled={loading}
          />
          <button
            className={`send-btn ${loading ? "send-loading" : ""}`}
            onClick={() => sendMessage()}
            disabled={loading}
          >
            {loading ? "…" : "Send ↑"}
          </button>
        </div>
        <p className="disclaimer">
          Powered by Google ADK · Gemini 2.0 Flash · Open-Meteo · CoinCap
          {sessionId && <span className="session-id"> · Session: {sessionId.slice(0, 8)}</span>}
        </p>
      </div>
    </div>
  );
}
