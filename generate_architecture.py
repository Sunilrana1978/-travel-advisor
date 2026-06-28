"""Generates architecture.png for the Travel Advisor ADK project."""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Use macOS system font stack for emoji support
matplotlib.rcParams["font.family"] = ["SF Pro Display", "Helvetica Neue", "Arial", "DejaVu Sans"]

fig, ax = plt.subplots(1, 1, figsize=(22, 15))
ax.set_xlim(0, 22)
ax.set_ylim(0, 15)
ax.axis("off")
fig.patch.set_facecolor("#0D1117")

C = {
    "gcp_bg":        "#161B22",
    "gcp_border":    "#4285F4",
    "run_bg":        "#0D1520",
    "run_border":    "#4285F4",
    "agent_bg":      "#0A1A0A",
    "agent_border":  "#34A853",
    "svc_bg":        "#1A1400",
    "svc_border":    "#FBBC05",
    "ext_bg":        "#150A20",
    "ext_border":    "#9B59B6",
    "user_bg":       "#0A1A18",
    "user_border":   "#00BCD4",
    "par_bg":        "#071207",
    "par_border":    "#34A853",
    "gem_bg":        "#1A1400",
    "gem_border":    "#FBBC05",
    "fe_border":     "#00BCD4",
    "text_w":        "#FFFFFF",
    "text_s":        "#90A4AE",
    "text_y":        "#FFD54F",
    "text_g":        "#69F0AE",
    "arrow_blue":    "#4285F4",
    "arrow_green":   "#34A853",
    "arrow_yellow":  "#FBBC05",
    "arrow_cyan":    "#00BCD4",
    "arrow_purple":  "#9B59B6",
    "arrow_gray":    "#546E7A",
}


def box(x, y, w, h, bg, border, radius=0.25, lw=2, alpha=1.0, zorder=2):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={radius}",
                       linewidth=lw, edgecolor=border,
                       facecolor=bg, alpha=alpha, zorder=zorder)
    ax.add_patch(p)


def txt(x, y, s, size=8, color="#FFFFFF", bold=False, ha="center", va="center",
        mono=False, zorder=8):
    ff = "monospace" if mono else "sans-serif"
    ax.text(x, y, s, fontsize=size, color=color,
            ha=ha, va=va, fontweight="bold" if bold else "normal",
            fontfamily=ff, zorder=zorder)


def arr(x1, y1, x2, y2, color="#8899AA", lw=1.5, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=12,
                                connectionstyle=f"arc3,rad={rad}"),
                zorder=5)


def section_tag(x, y, text, color, bg):
    ax.text(x, y, f"  {text}  ", fontsize=7.5, color=color,
            ha="left", va="center", fontweight="bold", fontfamily="monospace",
            zorder=10,
            bbox=dict(facecolor=bg, edgecolor=color,
                      boxstyle="round,pad=0.25", linewidth=1.5))


# ═══════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════
txt(11, 14.55, "Travel Advisor AI  —  GCP Architecture", 18, C["text_w"], bold=True)
txt(11, 14.1, "Google ADK  ·  Gemini 2.5 Flash  ·  ParallelAgent  ·  Cloud Run  ·  Secret Manager",
    9, C["text_s"])

# ═══════════════════════════════════════════════════════════════════
# USER  (far left)
# ═══════════════════════════════════════════════════════════════════
box(0.25, 10.0, 2.6, 3.4, C["user_bg"], C["user_border"], lw=2)
section_tag(0.45, 13.18, "USER", C["user_border"], C["user_bg"])
txt(1.55, 12.7,  "Browser", 9,   C["text_w"], bold=True)
txt(1.55, 12.35, "React + Vite SPA", 7, C["text_s"])
txt(1.55, 12.0,  "Streaming SSE", 7, C["text_s"])
txt(1.55, 11.65, "Session memory", 7, C["text_s"])
txt(1.55, 11.3,  "Multi-turn chat", 7, C["text_s"])
txt(1.55, 10.85, "Port 3000", 7, C["text_y"])

# ═══════════════════════════════════════════════════════════════════
# GCP BOUNDARY
# ═══════════════════════════════════════════════════════════════════
box(3.1, 0.3, 18.5, 13.4, C["gcp_bg"], C["gcp_border"], radius=0.5, lw=2.5, zorder=1)
section_tag(3.4, 13.48, "Google Cloud Platform  (us-central1)", C["gcp_border"], C["gcp_bg"])

# ───────────────────────────────────────────────────────────────────
# CLOUD RUN: FRONTEND
# ───────────────────────────────────────────────────────────────────
box(3.4, 10.0, 4.5, 3.4, C["run_bg"], C["fe_border"], lw=2)
section_tag(3.65, 13.18, "Cloud Run: Frontend", C["fe_border"], C["run_bg"])
txt(5.65, 12.7,  "travel-advisor-frontend", 9,  C["text_w"], bold=True)
txt(5.65, 12.35, "React SPA + nginx", 7, C["text_s"])
txt(5.65, 12.0,  "VITE_API_URL -> Backend URL", 7, C["text_s"])
txt(5.65, 11.65, "min-instances: 0", 7, C["text_s"])
txt(5.65, 11.3,  "max-instances: 5 | 256 Mi", 7, C["text_s"])
txt(5.65, 10.85, "Public · unauthenticated", 7, C["text_g"])

# ───────────────────────────────────────────────────────────────────
# CLOUD RUN: BACKEND  (large central box)
# ───────────────────────────────────────────────────────────────────
box(3.4, 0.7, 12.5, 9.0, "#0A1018", C["gcp_border"], radius=0.4, lw=2, zorder=2)
section_tag(3.65, 9.48, "Cloud Run: Backend  (travel-advisor-backend)", C["gcp_border"], "#0A1018")
txt(9.65, 9.15, "FastAPI + Google ADK  |  Python 3.11  |  min=0  max=10  1 Gi  port=8080",
    7, C["text_s"])

# FastAPI box
box(3.65, 7.4, 3.8, 1.55, "#060E18", C["arrow_blue"], radius=0.2, lw=1.5)
txt(5.55, 8.7,  "FastAPI Server", 8, C["arrow_blue"], bold=True)
txt(5.55, 8.38, "POST  /api/chat             (JSON)", 6.5, C["text_s"], mono=True)
txt(5.55, 8.1,  "POST  /api/chat/stream  (SSE)", 6.5, C["text_s"], mono=True)
txt(5.55, 7.82, "GET   /api/session/new", 6.5, C["text_s"], mono=True)
txt(5.55, 7.57, "GET   /health  |  GET  /docs", 6.5, C["text_y"], mono=True)

# ADK Runtime box
box(3.65, 5.6, 3.8, 1.6, "#060E18", C["arrow_green"], radius=0.2, lw=1.5)
txt(5.55, 6.98, "ADK Runtime", 8, C["arrow_green"], bold=True)
txt(5.55, 6.65, "Runner  (run_async)", 6.5, C["text_s"], mono=True)
txt(5.55, 6.38, "InMemorySessionService", 6.5, C["text_s"], mono=True)
txt(5.55, 6.1,  "Multi-turn conversation memory", 6.5, C["text_s"])
txt(5.55, 5.82, "APP_NAME = travel_advisor", 6.5, C["text_y"], mono=True)

# Root agent box
box(3.65, 3.55, 3.8, 1.85, "#060E18", C["arrow_blue"], radius=0.2, lw=1.5)
txt(5.55, 5.15, "root_agent  (travel_concierge)", 8.5, C["arrow_blue"], bold=True)
txt(5.55, 4.82, "LlmAgent  |  gemini-2.5-flash", 6.5, C["text_s"])
txt(5.55, 4.55, "Understands user intent", 6.5, C["text_s"])
txt(5.55, 4.28, "Routes via AgentTool", 6.5, C["text_s"])
txt(5.55, 4.01, "Synthesises final response", 6.5, C["text_s"])
txt(5.55, 3.72, "Holds session context", 6.5, C["text_y"])

# ───────────────────────────────────────────────────────────────────
# PARALLEL AGENT block
# ───────────────────────────────────────────────────────────────────
box(7.9, 3.0, 7.8, 6.2, C["par_bg"], C["par_border"], radius=0.35, lw=2, zorder=2)
section_tag(8.15, 8.98, "ParallelAgent  —  parallel_research_agent  (concurrent fan-out)", C["par_border"], C["par_bg"])

# weather_agent
box(8.15, 5.85, 3.4, 2.95, "#060E08", C["arrow_green"], radius=0.2, lw=1.5)
txt(9.85, 8.55,  "weather_agent", 9, C["arrow_green"], bold=True)
txt(9.85, 8.2,   "LlmAgent | gemini-2.5-flash", 6.5, C["text_s"])
txt(9.85, 7.92,  "─ FunctionTool ──────────────", 6, C["arrow_green"], mono=True)
txt(9.85, 7.65,  "get_current_weather(city)", 6.5, C["text_s"], mono=True)
txt(9.85, 7.38,  "list_supported_cities()", 6.5, C["text_s"], mono=True)
txt(9.85, 7.1,   "─ Features ──────────────────", 6, C["arrow_green"], mono=True)
txt(9.85, 6.83,  "18 cities  |  WMO codes", 6.5, C["text_s"])
txt(9.85, 6.55,  "Outfit & packing advice", 6.5, C["text_s"])
txt(9.85, 6.15,  "temp_c/f  wind  precip", 6.5, C["text_y"])

# fx_agent
box(11.95, 5.85, 3.4, 2.95, "#130A00", C["arrow_yellow"], radius=0.2, lw=1.5)
txt(13.65, 8.55,  "fx_agent", 9, C["arrow_yellow"], bold=True)
txt(13.65, 8.2,   "LlmAgent | gemini-2.5-flash", 6.5, C["text_s"])
txt(13.65, 7.92,  "─ FunctionTool ──────────────", 6, C["arrow_yellow"], mono=True)
txt(13.65, 7.65,  "get_exchange_rate(base, tgt)", 6.5, C["text_s"], mono=True)
txt(13.65, 7.38,  "open.er-api.com/v6/latest", 6.5, C["text_s"], mono=True)
txt(13.65, 7.1,   "─ Returns ───────────────────", 6, C["arrow_yellow"], mono=True)
txt(13.65, 6.83,  "exchange_rate + inverse", 6.5, C["text_s"])
txt(13.65, 6.55,  "example_conversions dict", 6.5, C["text_s"])
txt(13.65, 6.15,  "10 / 50 / 100 / 500 / 1000", 6.5, C["text_y"])

# weather response
box(8.15, 3.2, 3.4, 2.45, "#030A03", C["arrow_green"], radius=0.2, lw=1.2)
txt(9.85, 5.42, "Tool Response", 7.5, C["arrow_green"], bold=True)
txt(9.85, 5.12, "status | city | country", 6.5, C["text_s"], mono=True)
txt(9.85, 4.85, "temperature_c | temperature_f", 6.5, C["text_s"], mono=True)
txt(9.85, 4.58, "condition | wind_kmh", 6.5, C["text_s"], mono=True)
txt(9.85, 4.31, "precipitation_chance_pct", 6.5, C["text_s"], mono=True)
txt(9.85, 4.04, "outfit_advice", 6.5, C["text_s"], mono=True)
txt(9.85, 3.45, "JSON -> weather_agent -> root", 6, C["arrow_green"])

# fx response
box(11.95, 3.2, 3.4, 2.45, "#0D0700", C["arrow_yellow"], radius=0.2, lw=1.2)
txt(13.65, 5.42, "Tool Response", 7.5, C["arrow_yellow"], bold=True)
txt(13.65, 5.12, "status | base | target", 6.5, C["text_s"], mono=True)
txt(13.65, 4.85, "exchange_rate | inverse_rate", 6.5, C["text_s"], mono=True)
txt(13.65, 4.58, "example_conversions", 6.5, C["text_s"], mono=True)
txt(13.65, 4.31, "{'10': x, '50': x, ...}", 6.5, C["text_s"], mono=True)
txt(13.65, 4.04, "'1000': x", 6.5, C["text_s"], mono=True)
txt(13.65, 3.45, "JSON -> fx_agent -> root", 6, C["arrow_yellow"])

# ───────────────────────────────────────────────────────────────────
# GEMINI API  (bottom inside backend)
# ───────────────────────────────────────────────────────────────────
box(3.65, 0.9, 12.0, 2.35, C["gem_bg"], C["gem_border"], radius=0.25, lw=2)
section_tag(3.9, 3.04, "Gemini API  (Google AI Studio)", C["gem_border"], C["gem_bg"])
txt(9.65, 2.7,  "Model: gemini-2.5-flash", 9, C["text_w"], bold=True)
txt(9.65, 2.38, "Powers: root_agent (intent routing)  |  weather_agent (wx synthesis)  |  fx_agent (FX synthesis)", 7, C["text_y"])
txt(9.65, 2.08, "Capabilities: tool calling  |  parallel sub-agent delegation  |  natural-language synthesis  |  session context", 6.5, C["text_s"])
txt(9.65, 1.75, "GOOGLE_API_KEY injected from Secret Manager at Cloud Run startup", 6.5, C["text_s"])
txt(9.65, 1.38, "Alternative: GOOGLE_GENAI_USE_VERTEXAI=true  +  GOOGLE_CLOUD_PROJECT  (no API key needed)", 6.5, "#78909C")

# ───────────────────────────────────────────────────────────────────
# RIGHT COLUMN: Cloud Build, Container Registry, Secret Manager
# ───────────────────────────────────────────────────────────────────

# Cloud Build
box(16.3, 10.2, 4.9, 3.2, C["svc_bg"], C["svc_border"], lw=2)
section_tag(16.55, 13.18, "Cloud Build", C["svc_border"], C["svc_bg"])
txt(18.75, 12.75, "CI/CD Pipeline", 9,   C["text_w"], bold=True)
txt(18.75, 12.4,  "cloudbuild.yaml", 7,  C["text_y"], mono=True)
txt(18.75, 12.05, "Trigger: gcloud builds submit", 6.5, C["text_s"])
txt(18.75, 11.75, "Step 1: docker build backend", 6.5, C["text_s"])
txt(18.75, 11.45, "Step 2: push to gcr.io", 6.5, C["text_s"])
txt(18.75, 11.15, "Step 3: gcloud run deploy", 6.5, C["text_s"])
txt(18.75, 10.85, "Step 4: build + deploy frontend", 6.5, C["text_s"])
txt(18.75, 10.45, "machineType: E2_HIGHCPU_8", 6.5, C["text_y"], mono=True)

# Container Registry
box(16.3, 6.9, 4.9, 3.0, C["svc_bg"], C["svc_border"], lw=2)
section_tag(16.55, 9.68, "Container Registry  (gcr.io)", C["svc_border"], C["svc_bg"])
txt(18.75, 9.3,  "Docker Image Store", 9,  C["text_w"], bold=True)
txt(18.75, 8.97, "gcr.io/$PROJECT/travel-advisor-backend", 6.5, C["text_s"], mono=True)
txt(18.75, 8.68, "gcr.io/$PROJECT/travel-advisor-frontend", 6.5, C["text_s"], mono=True)
txt(18.75, 8.35, "Tagged: :latest  +  :$SHORT_SHA", 6.5, C["text_y"])
txt(18.75, 8.05, "Immutable image per commit", 6.5, C["text_s"])
txt(18.75, 7.72, "Pull-on-deploy by Cloud Run", 6.5, C["text_s"])
txt(18.75, 7.15, "Logging: CLOUD_LOGGING_ONLY", 6.5, C["text_s"])

# Secret Manager
box(16.3, 3.8, 4.9, 2.85, C["svc_bg"], C["svc_border"], lw=2)
section_tag(16.55, 6.43, "Secret Manager", C["svc_border"], C["svc_bg"])
txt(18.75, 6.05, "API Key Vault", 9,  C["text_w"], bold=True)
txt(18.75, 5.72, "Secret: GOOGLE_API_KEY", 7,  C["text_y"], mono=True)
txt(18.75, 5.42, "Stored with gcloud secrets create", 6.5, C["text_s"])
txt(18.75, 5.12, "--set-secrets flag in Cloud Run", 6.5, C["text_s"])
txt(18.75, 4.82, "Injected as env var at runtime", 6.5, C["text_s"])
txt(18.75, 4.52, "Never stored in code or .env", 6.5, C["text_g"])
txt(18.75, 4.08, "IAM: Cloud Run SA -> secretAccessor", 6.5, "#78909C", mono=True)

# ───────────────────────────────────────────────────────────────────
# EXTERNAL APIs  (left strip below GCP)
# ───────────────────────────────────────────────────────────────────
box(0.25, 1.2, 2.6, 8.4, C["ext_bg"], C["ext_border"], radius=0.3, lw=2)
section_tag(0.4, 9.38, "External APIs", C["ext_border"], C["ext_bg"])

# Open-Meteo
box(0.45, 6.05, 2.2, 2.95, "#060010", C["arrow_cyan"], radius=0.2, lw=1.5)
txt(1.55, 8.72, "Open-Meteo", 8,   C["arrow_cyan"], bold=True)
txt(1.55, 8.42, "Weather API", 7,  C["text_w"])
txt(1.55, 8.1,  "api.open-meteo.com", 5.5, C["text_s"], mono=True)
txt(1.55, 7.82, "Free  |  No API key", 6,  C["text_g"])
txt(1.55, 7.52, "Current weather + forecast", 6, C["text_s"])
txt(1.55, 7.25, "WMO weather codes", 6, C["text_s"])
txt(1.55, 6.95, "lat/lon geocoding", 6, C["text_s"])
txt(1.55, 6.35, "timeout: 10s", 6, C["text_y"], mono=True)

# ExchangeRate API
box(0.45, 2.95, 2.2, 2.9, "#0A0010", C["arrow_purple"], radius=0.2, lw=1.5)
txt(1.55, 5.57, "ExchangeRate API", 7.5, C["arrow_purple"], bold=True)
txt(1.55, 5.27, "Fiat FX Rates", 7, C["text_w"])
txt(1.55, 4.97, "open.er-api.com/v6", 5.5, C["text_s"], mono=True)
txt(1.55, 4.67, "Free  |  No API key", 6, C["text_g"])
txt(1.55, 4.37, "All major fiat currencies", 6, C["text_s"])
txt(1.55, 4.07, "USD EUR GBP JPY AED ...", 6, C["text_s"])
txt(1.55, 3.77, "Rates vs base currency", 6, C["text_s"])
txt(1.55, 3.2,  "timeout: 10s", 6, C["text_y"], mono=True)

# ═══════════════════════════════════════════════════════════════════
# ARROWS
# ═══════════════════════════════════════════════════════════════════

# User -> Frontend
arr(2.85, 11.55, 3.4, 11.55, C["arrow_cyan"], lw=2)
ax.text(3.1, 11.72, "HTTPS", fontsize=6, color=C["arrow_cyan"],
        ha="center", va="center", fontfamily="monospace", zorder=8)

# Frontend -> Backend (vertical)
arr(7.0, 11.1, 7.0, 9.68, C["arrow_blue"], lw=2)
ax.text(7.35, 10.5, "REST\n/SSE", fontsize=6, color=C["arrow_blue"],
        ha="left", va="center", fontfamily="monospace", zorder=8)

# FastAPI -> ADK Runtime
arr(5.55, 7.4, 5.55, 7.2, C["arrow_gray"], lw=1.5)

# ADK Runtime -> root_agent
arr(5.55, 5.6, 5.55, 5.4, C["arrow_gray"], lw=1.5)

# root_agent -> parallel_research_agent
arr(7.45, 4.5, 7.9, 4.5, C["arrow_green"], lw=2.5)
ax.text(7.68, 4.72, "AgentTool", fontsize=5.5, color=C["arrow_green"],
        ha="center", va="center", fontfamily="monospace", zorder=8)

# parallel -> weather_agent
arr(9.85, 5.85, 9.85, 5.55, C["arrow_green"], lw=1.8)

# parallel -> fx_agent
arr(13.65, 5.85, 13.65, 5.55, C["arrow_yellow"], lw=1.8)

# weather tool result -> back up
arr(9.85, 5.85, 9.85, 3.4, C["arrow_green"], lw=1, rad=0.0)

# fx tool result -> back up
arr(13.65, 5.85, 13.65, 3.4, C["arrow_yellow"], lw=1, rad=0.0)

# weather_agent -> Open-Meteo (left)
arr(8.15, 7.3, 2.65, 7.3, C["arrow_cyan"], lw=1.8)
ax.text(5.4, 7.5, "HTTP GET  /v1/forecast", fontsize=6, color=C["arrow_cyan"],
        ha="center", va="center", fontfamily="monospace", zorder=8)

# fx_agent -> ExchangeRate API
arr(8.15, 5.0, 2.65, 5.0, C["arrow_purple"], lw=1.8)
ax.text(5.4, 5.18, "HTTP GET  /v6/latest/{BASE}", fontsize=6, color=C["arrow_purple"],
        ha="center", va="center", fontfamily="monospace", zorder=8)

# root/agents -> Gemini API (vertical)
arr(5.55, 3.55, 5.55, 3.25, C["arrow_yellow"], lw=1.5)
arr(9.85, 5.85, 9.85, 3.25, C["arrow_yellow"], lw=1.2)
arr(13.65, 5.85, 13.65, 3.25, C["arrow_yellow"], lw=1.2)

# Cloud Build -> Container Registry
arr(18.75, 10.2, 18.75, 9.9, C["svc_border"], lw=2)
ax.text(19.15, 10.05, "push images", fontsize=5.5, color=C["svc_border"],
        ha="left", va="center", fontfamily="monospace", zorder=8)

# Container Registry -> Cloud Run Backend
arr(16.3, 8.5, 15.9, 8.5, C["svc_border"], lw=2)
ax.text(16.0, 8.65, "pull on deploy", fontsize=5.5, color=C["svc_border"],
        ha="right", va="center", fontfamily="monospace", zorder=8)

# Secret Manager -> Cloud Run Backend
arr(16.3, 5.15, 15.9, 5.15, C["svc_border"], lw=2)
ax.text(16.0, 5.3, "--set-secrets", fontsize=5.5, color=C["svc_border"],
        ha="right", va="center", fontfamily="monospace", zorder=8)

# Cloud Run Backend right side connector
ax.annotate("", xy=(15.9, 5.7), xytext=(15.9, 8.5),
            arrowprops=dict(arrowstyle="-", color=C["svc_border"], lw=1.5), zorder=4)

# ═══════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════
box(3.4, 0.3, 12.5, 0.72, "#080C10", "#333", radius=0.15, lw=1, zorder=3)
items = [
    (C["arrow_blue"],   "HTTPS / REST / SSE user flow"),
    (C["arrow_green"],  "ADK agent delegation (AgentTool)"),
    (C["arrow_yellow"], "Gemini API calls (LLM inference)"),
    (C["arrow_cyan"],   "Open-Meteo weather API"),
    (C["arrow_purple"], "ExchangeRate FX API"),
    (C["svc_border"],   "GCP service interactions"),
]
for i, (color, label) in enumerate(items):
    bx = 3.65 + i * 2.1
    ax.plot([bx, bx + 0.35], [0.67, 0.67], color=color, lw=2.5, zorder=6)
    ax.text(bx + 0.45, 0.67, label, fontsize=5.5, color=C["text_s"],
            ha="left", va="center", fontfamily="monospace", zorder=7)

plt.tight_layout(pad=0.2)
plt.savefig("architecture.png", dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("architecture.png saved")
