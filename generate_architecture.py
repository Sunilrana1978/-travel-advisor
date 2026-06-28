"""
Generates architecture.png in an illustrated flow-diagram style,
matching the LangGraph reference image: light background, robot agents,
thought bubbles, numbered arrows, and GCP service icons.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Wedge
from matplotlib.path import Path
import matplotlib.patheffects as pe

fig, ax = plt.subplots(figsize=(24, 14))
ax.set_xlim(0, 24)
ax.set_ylim(0, 14)
ax.axis("off")
fig.patch.set_facecolor("#F0F4F8")
ax.set_facecolor("#F0F4F8")

# ── Colour palette ────────────────────────────────────────────────────────────
BLUE      = "#1565C0"
LBLUE     = "#1E88E5"
GREEN     = "#2E7D32"
LGREEN    = "#43A047"
ORANGE    = "#E65100"
PURPLE    = "#6A1B9A"
LPURPLE   = "#AB47BC"
TEAL      = "#00695C"
GOLD      = "#F9A825"
DGRAY     = "#37474F"
MGRAY     = "#78909C"
LGRAY     = "#CFD8DC"
WHITE     = "#FFFFFF"
CREAM     = "#FFFDE7"
LRED      = "#C62828"

ARROW_MAIN   = "#2E7D32"    # green  – user↔UI
ARROW_SESS   = "#1565C0"    # blue   – session/orchestrator
ARROW_AGENT  = "#6A1B9A"    # purple – agent interactions (dashed)
ARROW_TOOL   = "#E65100"    # orange – tool calls/responses
ARROW_GCP    = "#1E88E5"    # blue   – GCP services


def box(x, y, w, h, fc=WHITE, ec=LGRAY, lw=1.5, radius=0.3, alpha=1.0, zorder=3):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={radius}",
                       fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=zorder)
    ax.add_patch(p)
    return p


def circle(cx, cy, r, fc=WHITE, ec=DGRAY, lw=2, zorder=4, alpha=1.0):
    c = Circle((cx, cy), r, fc=fc, ec=ec, lw=lw, zorder=zorder, alpha=alpha)
    ax.add_patch(c)


def txt(x, y, s, size=9, color=DGRAY, bold=False, ha="center", va="center",
        zorder=10, wrap=False, style="normal"):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=zorder,
            fontweight="bold" if bold else "normal", fontstyle=style,
            fontfamily="sans-serif")


def arrow(x1, y1, x2, y2, color=DGRAY, lw=1.8, dashed=False,
          label="", label_color=None, rad=0.0, zorder=5,
          head="->", lbl_offset=(0, 0.22)):
    ls = (0, (5, 4)) if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=head, color=color, lw=lw,
                                linestyle=ls, mutation_scale=14,
                                connectionstyle=f"arc3,rad={rad}"),
                zorder=zorder)
    if label:
        mx = (x1 + x2) / 2 + lbl_offset[0]
        my = (y1 + y2) / 2 + lbl_offset[1]
        lc = label_color or color
        txt(mx, my, label, size=7.5, color=lc, bold=True)


def step_arrow(x1, y1, x2, y2, step, color=DGRAY, lw=1.8, dashed=False,
               desc="", desc2="", rad=0.0, zorder=5, lbl_offset=(0, 0)):
    """Arrow with a numbered circle badge and description."""
    ls = (0, (5, 4)) if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                linestyle=ls, mutation_scale=15,
                                connectionstyle=f"arc3,rad={rad}"),
                zorder=zorder)
    mx = (x1 + x2) / 2 + lbl_offset[0]
    my = (y1 + y2) / 2 + lbl_offset[1]
    # Step circle
    circle(mx, my + 0.3, 0.22, fc=color, ec=color, lw=0, zorder=zorder + 2)
    txt(mx, my + 0.3, str(step), size=7, color=WHITE, bold=True, zorder=zorder + 3)
    if desc:
        txt(mx, my - 0.05, desc, size=7, color=color, bold=False)
    if desc2:
        txt(mx, my - 0.32, desc2, size=7, color=color, bold=False)


# ════════════════════════════════════════════════════════════════════════
# BACKGROUND SECTIONS
# ════════════════════════════════════════════════════════════════════════
# Main GCP cloud region (subtle)
box(5.8, 0.5, 17.8, 12.8, fc="#E8EEF8", ec="#4285F4", lw=2, radius=0.6,
    alpha=0.5, zorder=1)
txt(6.5, 13.08, "Google Cloud Platform", size=9, color="#4285F4", bold=True, ha="left")

# ADK Runtime section
box(8.2, 4.2, 4.2, 7.8, fc="#E8F5E9", ec="#34A853", lw=1.5, radius=0.4,
    alpha=0.7, zorder=1)
txt(9.2, 11.82, "Google ADK Runtime", size=8.5, color="#34A853", bold=True, ha="left")


# ════════════════════════════════════════════════════════════════════════
# TITLE
# ════════════════════════════════════════════════════════════════════════
txt(12, 13.55, "Travel Advisor AI  —  Multi-Agent Architecture",
    size=19, color=DGRAY, bold=True)
txt(12, 13.1,
    "Google ADK  ·  Gemini 2.5 Flash  ·  ParallelAgent  ·  FastAPI + SSE  ·  Cloud Run",
    size=10, color=MGRAY)


# ════════════════════════════════════════════════════════════════════════
# ROBOT HELPER  (draws a cute robot icon)
# ════════════════════════════════════════════════════════════════════════
def robot(cx, cy, scale=1.0, head_color=LBLUE, body_color="#90CAF9",
          eye_color=WHITE, label="", label_color=LBLUE, zorder=6):
    s = scale
    # Antenna
    ax.plot([cx, cx], [cy + 0.85*s, cy + 1.05*s], color=DGRAY, lw=1.5*s, zorder=zorder)
    circle(cx, cy + 1.1*s, 0.07*s, fc=GOLD, ec=DGRAY, lw=1*s, zorder=zorder+1)
    # Head
    box(cx - 0.42*s, cy + 0.35*s, 0.84*s, 0.52*s,
        fc=head_color, ec=DGRAY, lw=1.5*s, radius=0.1*s, zorder=zorder)
    # Eyes
    circle(cx - 0.15*s, cy + 0.62*s, 0.1*s, fc=eye_color, ec=DGRAY, lw=1*s, zorder=zorder+1)
    circle(cx + 0.15*s, cy + 0.62*s, 0.1*s, fc=eye_color, ec=DGRAY, lw=1*s, zorder=zorder+1)
    # Pupils
    circle(cx - 0.13*s, cy + 0.62*s, 0.05*s, fc=DGRAY, ec=DGRAY, lw=0, zorder=zorder+2)
    circle(cx + 0.17*s, cy + 0.62*s, 0.05*s, fc=DGRAY, ec=DGRAY, lw=0, zorder=zorder+2)
    # Mouth
    ax.plot([cx - 0.12*s, cx + 0.12*s], [cy + 0.42*s, cy + 0.42*s],
            color=DGRAY, lw=1.5*s, zorder=zorder+1)
    # Body
    box(cx - 0.38*s, cy - 0.38*s, 0.76*s, 0.75*s,
        fc=body_color, ec=DGRAY, lw=1.5*s, radius=0.08*s, zorder=zorder)
    # Body panel
    box(cx - 0.18*s, cy - 0.2*s, 0.36*s, 0.3*s,
        fc=WHITE, ec=MGRAY, lw=1*s, radius=0.04*s, zorder=zorder+1)
    # Legs
    box(cx - 0.3*s, cy - 0.68*s, 0.22*s, 0.3*s,
        fc=body_color, ec=DGRAY, lw=1.5*s, radius=0.05*s, zorder=zorder)
    box(cx + 0.08*s, cy - 0.68*s, 0.22*s, 0.3*s,
        fc=body_color, ec=DGRAY, lw=1.5*s, radius=0.05*s, zorder=zorder)
    # Arms
    box(cx - 0.62*s, cy - 0.15*s, 0.24*s, 0.44*s,
        fc=body_color, ec=DGRAY, lw=1.5*s, radius=0.06*s, zorder=zorder)
    box(cx + 0.38*s, cy - 0.15*s, 0.24*s, 0.44*s,
        fc=body_color, ec=DGRAY, lw=1.5*s, radius=0.06*s, zorder=zorder)
    if label:
        txt(cx, cy - 0.92*s, label, size=10*s, color=label_color, bold=True)


def thought_bubble(cx, cy, text, text2="", text3="", fc=CREAM, tc=ORANGE,
                   side="right", zorder=7):
    """Thought bubble cloud with 3 lines of text."""
    # Trail dots
    offsets = [(-0.35, -0.55), (-0.2, -0.35), (-0.08, -0.18)] if side == "left" else \
              [(0.35, -0.55),  (0.2, -0.35),  (0.08, -0.18)]
    for ox, oy in offsets:
        r = 0.04 + abs(ox) * 0.04
        circle(cx + ox, cy + oy, r, fc=MGRAY, ec=MGRAY, lw=0, zorder=zorder)

    dx = -1.5 if side == "left" else 1.5
    # Cloud (overlapping circles)
    bx, by = cx + dx, cy + 0.5
    for ox, oy, r in [
        (0, 0, 0.62), (-0.5, 0.1, 0.45), (0.5, 0.05, 0.45),
        (-0.28, 0.45, 0.38), (0.28, 0.42, 0.38), (0, 0.55, 0.38),
    ]:
        circle(bx + ox, by + oy, r, fc=fc, ec=fc, lw=0, zorder=zorder)
    # Outline circle at edges for definition
    circle(bx, by, 0.62, fc=fc, ec=LGRAY, lw=1, zorder=zorder-1)
    # Text
    txt(bx, by + 0.52, text,  size=8,   color=tc, bold=True,  zorder=zorder+2)
    txt(bx, by + 0.27, text2, size=7.5, color=tc, bold=False, zorder=zorder+2)
    txt(bx, by + 0.05, text3, size=7.5, color=tc, bold=False, zorder=zorder+2)


def gear_icon(cx, cy, r=0.55, n_teeth=8, fc="#546E7A", ec=DGRAY, lw=1.5, zorder=5):
    """Draw a gear shape."""
    outer_r = r
    inner_r = r * 0.7
    tooth_h = r * 0.22
    angles = np.linspace(0, 2*np.pi, n_teeth * 4 + 1)[:-1]
    pts = []
    for i, a in enumerate(angles):
        mod = i % 4
        if mod in (1, 2):
            rr = outer_r + tooth_h
        else:
            rr = outer_r
        pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    gear = plt.Polygon(pts, fc=fc, ec=ec, lw=lw, zorder=zorder)
    ax.add_patch(gear)
    circle(cx, cy, inner_r * 0.55, fc="#B0BEC5", ec=ec, lw=lw, zorder=zorder+1)


def person_icon(cx, cy, color=DGRAY, zorder=5):
    """Simple person silhouette."""
    # Head
    circle(cx, cy + 0.72, 0.3, fc=color, ec=color, lw=0, zorder=zorder)
    # Body
    body = plt.Polygon([
        (cx - 0.28, cy + 0.42), (cx + 0.28, cy + 0.42),
        (cx + 0.32, cy - 0.35), (cx - 0.32, cy - 0.35),
    ], fc=color, ec=color, lw=0, zorder=zorder)
    ax.add_patch(body)


def screen_icon(cx, cy, w=1.1, h=0.8, color=LBLUE, zorder=5):
    """Monitor / chat screen icon."""
    box(cx - w/2, cy - h/2, w, h, fc=color, ec=DGRAY, lw=2, radius=0.1, zorder=zorder)
    box(cx - w/2 + 0.06, cy - h/2 + 0.06, w - 0.12, h - 0.12,
        fc=WHITE, ec="none", lw=0, radius=0.06, zorder=zorder+1)
    # Stand
    ax.plot([cx, cx], [cy - h/2, cy - h/2 - 0.2], color=DGRAY, lw=3, zorder=zorder)
    box(cx - 0.22, cy - h/2 - 0.28, 0.44, 0.1,
        fc=DGRAY, ec=DGRAY, lw=0, radius=0.04, zorder=zorder)
    # Chat bubble dots
    for dx in [-0.18, 0, 0.18]:
        circle(cx + dx, cy + 0.05, 0.065, fc=color, ec=color, lw=0, zorder=zorder+2)


def gcp_service_box(x, y, w, h, title, subtitle, subtitle2="",
                    badge_color=LBLUE, zorder=4):
    box(x, y, w, h, fc=WHITE, ec=badge_color, lw=2, radius=0.25, zorder=zorder)
    # Top badge
    box(x, y + h - 0.45, w, 0.45, fc=badge_color, ec=badge_color,
        lw=0, radius=0.25, zorder=zorder+1)
    # Fix bottom corners of badge
    ax.add_patch(plt.Rectangle((x, y + h - 0.45), w, 0.22,
                                fc=badge_color, ec=badge_color, lw=0, zorder=zorder+1))
    txt(x + w/2, y + h - 0.22, title, size=8, color=WHITE, bold=True, zorder=zorder+2)
    txt(x + w/2, y + h * 0.55, subtitle,  size=7.5, color=DGRAY, zorder=zorder+2)
    txt(x + w/2, y + h * 0.28, subtitle2, size=7,   color=MGRAY, zorder=zorder+2)


# ════════════════════════════════════════════════════════════════════════
# 1. USER
# ════════════════════════════════════════════════════════════════════════
person_icon(1.5, 7.5, color=DGRAY)
txt(1.5, 6.85, "User", size=13, color=DGRAY, bold=True)


# ════════════════════════════════════════════════════════════════════════
# 2. REACT UI  (FastAPI backend + SSE)
# ════════════════════════════════════════════════════════════════════════
screen_icon(4.2, 7.5, color=LBLUE)
txt(4.2, 6.85, "React UI", size=11, color=LBLUE, bold=True)
txt(4.2, 6.52, "+ FastAPI Backend", size=8, color=MGRAY)


# ════════════════════════════════════════════════════════════════════════
# 3. ADK ORCHESTRATOR
# ════════════════════════════════════════════════════════════════════════
box(8.4, 4.5, 3.8, 7.2, fc=WHITE, ec="#34A853", lw=2.5, radius=0.35, zorder=3)
txt(10.3, 11.45, "ADK Orchestrator", size=12, color="#34A853", bold=True)

# ADK logo ring
circle(10.3, 10.55, 0.52, fc="#34A853", ec="#34A853", lw=0, zorder=5)
circle(10.3, 10.55, 0.38, fc=WHITE, ec=WHITE, lw=0, zorder=6)
circle(10.3, 10.55, 0.22, fc="#34A853", ec="#34A853", lw=0, zorder=7)
txt(10.3, 10.55, "G", size=13, color=WHITE, bold=True, zorder=8)

# Flow steps inside
stages = [
    ("Pre-Processing",  9.2, 9.45, "#E3F2FD", LBLUE),
    ("Intent Routing",  9.2, 8.55, "#E8F5E9", LGREEN),
    ("Agent Delegation",9.2, 7.65, "#FFF3E0", ORANGE),
    ("Aggregation",     9.2, 6.75, "#F3E5F5", LPURPLE),
    ("SSE Streaming",   9.2, 5.85, "#E0F7FA", TEAL),
]
for label_s, sx, sy, fc_s, ec_s in stages:
    box(sx, sy, 2.2, 0.72, fc=fc_s, ec=ec_s, lw=1.5, radius=0.18, zorder=5)
    txt(sx + 1.1, sy + 0.36, label_s, size=8, color=ec_s, bold=True, zorder=6)

# Connectors between stages
for i in range(len(stages) - 1):
    _, _, sy, _, ec_s = stages[i]
    ax.annotate("", xy=(10.3, stages[i+1][2] + 0.72),
                xytext=(10.3, sy),
                arrowprops=dict(arrowstyle="-|>", color=MGRAY, lw=1.2,
                                mutation_scale=10), zorder=4)


# ════════════════════════════════════════════════════════════════════════
# 4. ROOT AGENT  (Primary Agent)
# ════════════════════════════════════════════════════════════════════════
robot(13.8, 8.0, scale=1.15, head_color=BLUE, body_color="#90CAF9",
      label="Root Agent\n(travel_concierge)", label_color=BLUE, zorder=6)
thought_bubble(13.8, 9.15, "Route to", "parallel_research", "agent?",
               fc=CREAM, tc=ORANGE, side="left")


# ════════════════════════════════════════════════════════════════════════
# 5. WEATHER AGENT
# ════════════════════════════════════════════════════════════════════════
robot(17.2, 11.2, scale=1.0, head_color=LGREEN, body_color="#C8E6C9",
      label="Weather Agent", label_color=LGREEN, zorder=6)
thought_bubble(17.2, 12.1, "Call Open-", "Meteo API?", "",
               fc="#E8F5E9", tc=LGREEN, side="right")


# ════════════════════════════════════════════════════════════════════════
# 6. FX AGENT
# ════════════════════════════════════════════════════════════════════════
robot(17.2, 6.5, scale=1.0, head_color=GOLD, body_color="#FFF9C4",
      label="FX Agent", label_color="#E65100", zorder=6)
thought_bubble(17.2, 7.5, "Call ExRate", "API?", "",
               fc=CREAM, tc="#E65100", side="right")


# ════════════════════════════════════════════════════════════════════════
# 7. PARALLEL AGENT label
# ════════════════════════════════════════════════════════════════════════
box(15.4, 8.55, 3.6, 0.62, fc="#E8F5E9", ec="#34A853", lw=1.5, radius=0.18, zorder=4)
txt(17.2, 8.86, "ParallelAgent  —  concurrent fan-out", size=8, color="#34A853", bold=True)


# ════════════════════════════════════════════════════════════════════════
# 8. TOOLS  (gear icons)
# ════════════════════════════════════════════════════════════════════════
# Open-Meteo gear
gear_icon(13.5, 3.8, r=0.52, fc="#0277BD", ec=DGRAY, zorder=5)
txt(13.5, 3.03, "Open-Meteo", size=9, color="#0277BD", bold=True)
txt(13.5, 2.72, "get_current_weather()", size=7.5, color=MGRAY)
txt(13.5, 2.45, "18 cities  |  Free API", size=7, color=MGRAY)

# ExchangeRate gear
gear_icon(16.8, 3.8, r=0.52, fc=PURPLE, ec=DGRAY, zorder=5)
txt(16.8, 3.03, "ExchangeRate API", size=9, color=PURPLE, bold=True)
txt(16.8, 2.72, "get_exchange_rate()", size=7.5, color=MGRAY)
txt(16.8, 2.45, "open.er-api.com  |  Free", size=7, color=MGRAY)

txt(15.15, 4.38, "Tools (FunctionTool)", size=9.5, color=DGRAY, bold=True)


# ════════════════════════════════════════════════════════════════════════
# 9. GCP SERVICES  (right column)
# ════════════════════════════════════════════════════════════════════════
gcp_service_box(20.5, 10.5, 3.2, 2.0,
                "Cloud Run",
                "Backend  (FastAPI+ADK)",
                "min=0  max=10  1Gi",
                badge_color=LBLUE)

gcp_service_box(20.5, 8.0, 3.2, 2.0,
                "Cloud Build",
                "CI/CD  cloudbuild.yaml",
                "E2_HIGHCPU_8  |  gcr.io",
                badge_color=LGREEN)

gcp_service_box(20.5, 5.5, 3.2, 2.0,
                "Secret Manager",
                "GOOGLE_API_KEY",
                "Injected via --set-secrets",
                badge_color=ORANGE)

gcp_service_box(20.5, 3.0, 3.2, 2.0,
                "Cloud Run",
                "Frontend  (React+nginx)",
                "min=0  max=5  256Mi",
                badge_color=TEAL)

# Gemini badge
box(20.5, 1.0, 3.2, 1.65, fc="#FFF8E1", ec=GOLD, lw=2, radius=0.25, zorder=4)
circle(21.0, 1.83, 0.28, fc=GOLD, ec="#E65100", lw=1.5, zorder=5)
txt(21.0, 1.83, "G", size=11, color=WHITE, bold=True, zorder=6)
txt(22.1, 1.95, "Gemini 2.5 Flash", size=9, color=DGRAY, bold=True)
txt(22.1, 1.65, "LLM  |  Tool calling", size=7.5, color=MGRAY)
txt(22.1, 1.35, "All three LlmAgents", size=7.5, color=MGRAY)
txt(22.1, 1.1,  "Intent routing + synthesis", size=7, color=MGRAY)


# ════════════════════════════════════════════════════════════════════════
# ARROWS — numbered flow
# ════════════════════════════════════════════════════════════════════════

# 1. User → React UI
step_arrow(1.85, 7.8, 3.55, 7.8, "1", ARROW_MAIN, lw=2.2,
           desc="Multi-turn", desc2="Prompt", lbl_offset=(0, 0.08))

# 2. React UI → ADK Orchestrator
step_arrow(4.85, 7.8, 8.4, 7.8, "2", ARROW_SESS, lw=2.2,
           desc="Session / SSE", desc2="Request", lbl_offset=(0, 0.08))

# 3. ADK → Root Agent
step_arrow(12.2, 7.8, 13.05, 8.3, "3", ARROW_AGENT, lw=2, dashed=False,
           desc="Direct", desc2="Routing", lbl_offset=(0.1, 0.08))

# 4.1 Root → ParallelAgent → Weather
ax.annotate("", xy=(16.55, 11.35), xytext=(14.35, 9.05),
            arrowprops=dict(arrowstyle="-|>", color=ARROW_AGENT, lw=1.8,
                            linestyle=(0, (5, 4)), mutation_scale=13,
                            connectionstyle="arc3,rad=-0.15"), zorder=5)
circle(15.3, 10.4, 0.22, fc=ARROW_AGENT, ec=ARROW_AGENT, lw=0, zorder=6)
txt(15.3, 10.4, "4.1", size=6.5, color=WHITE, bold=True, zorder=7)
txt(15.05, 10.85, "Parallel", size=7, color=ARROW_AGENT, bold=True)
txt(15.05, 10.58, "Fan-out", size=7, color=ARROW_AGENT)

# 4.1 Root → FX
ax.annotate("", xy=(16.55, 6.9), xytext=(14.35, 7.8),
            arrowprops=dict(arrowstyle="-|>", color=ARROW_AGENT, lw=1.8,
                            linestyle=(0, (5, 4)), mutation_scale=13,
                            connectionstyle="arc3,rad=0.15"), zorder=5)

# 4.2 Weather Agent → Open-Meteo tool call
step_arrow(17.2, 10.3, 13.9, 4.32, "4.2", ARROW_TOOL, lw=1.6, dashed=True,
           desc="Tool Call", desc2="(weather)", lbl_offset=(-0.4, 0))

# 4.2 FX Agent → ExRate tool call
step_arrow(17.2, 5.55, 16.8, 4.32, "4.2", ARROW_TOOL, lw=1.6, dashed=True,
           desc="Tool Call", desc2="(fx)", lbl_offset=(0.55, 0))

# 4.3 Open-Meteo → response (back up, green)
ax.annotate("", xy=(14.2, 9.8), xytext=(13.8, 4.32),
            arrowprops=dict(arrowstyle="-|>", color=LGREEN, lw=1.5,
                            linestyle=(0, (5, 4)), mutation_scale=12,
                            connectionstyle="arc3,rad=0.25"), zorder=5)
circle(13.4, 7.1, 0.22, fc=LGREEN, ec=LGREEN, lw=0, zorder=6)
txt(13.4, 7.1, "4.3", size=6.5, color=WHITE, bold=True, zorder=7)
txt(13.05, 7.45, "Tool", size=7, color=LGREEN, bold=True)
txt(13.05, 7.18, "Response", size=7, color=LGREEN)

# 4.3 ExRate → fx response (back up)
ax.annotate("", xy=(17.5, 5.55), xytext=(16.8, 4.32),
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.5,
                            linestyle=(0, (5, 4)), mutation_scale=12,
                            connectionstyle="arc3,rad=-0.2"), zorder=5)

# 5. Agents gather → root_agent
ax.annotate("", xy=(14.35, 8.55), xytext=(16.55, 10.3),
            arrowprops=dict(arrowstyle="-|>", color=ARROW_AGENT, lw=1.8,
                            linestyle=(0, (5, 4)), mutation_scale=13,
                            connectionstyle="arc3,rad=0.15"), zorder=5)
ax.annotate("", xy=(14.35, 7.8), xytext=(16.55, 6.5),
            arrowprops=dict(arrowstyle="-|>", color=ARROW_AGENT, lw=1.8,
                            linestyle=(0, (5, 4)), mutation_scale=13,
                            connectionstyle="arc3,rad=-0.15"), zorder=5)
circle(15.55, 9.35, 0.22, fc=PURPLE, ec=PURPLE, lw=0, zorder=6)
txt(15.55, 9.35, "5", size=6.5, color=WHITE, bold=True, zorder=7)
txt(15.8, 9.65, "Gather &", size=7, color=PURPLE, bold=True)
txt(15.8, 9.38, "Aggregate", size=7, color=PURPLE)

# 6. ADK → root agent synthesise → ADK aggregation
step_arrow(13.05, 7.6, 12.2, 7.2, "6", ARROW_AGENT, lw=1.8, dashed=True,
           desc="State Update", desc2="& Synthesis", lbl_offset=(0.1, 0.08))

# 7. ADK → React UI (draft/response)
step_arrow(8.4, 6.6, 4.85, 7.0, "7", ARROW_SESS, lw=2.2,
           desc="SSE Stream", desc2="Response", lbl_offset=(0, 0.1))

# 8. React UI → User
step_arrow(3.55, 7.0, 1.85, 7.0, "8", ARROW_MAIN, lw=2.2,
           desc="Final", desc2="Response", lbl_offset=(0, 0.08))

# GCP service arrows (right side)
arrow(20.5, 11.5, 19.55, 11.5, ARROW_GCP, lw=1.5, dashed=True,
      label="hosts", lbl_offset=(0, 0.18))
arrow(20.5, 9.0, 19.55, 8.8, ARROW_GCP, lw=1.5, dashed=True,
      label="builds &\ndeploys", lbl_offset=(0.05, 0.08))
arrow(20.5, 6.5, 19.55, 6.8, ARROW_GCP, lw=1.5, dashed=True,
      label="injects\nAPI key", lbl_offset=(0.05, 0.08))
arrow(20.5, 4.0, 19.55, 10.5, ARROW_TEAL if False else TEAL, lw=1.5, dashed=True,
      label="frontend\nCloud Run", lbl_offset=(0.2, 0))

# Backend Cloud Run bracket
ax.plot([19.55, 19.55], [6.8, 11.5], color=LBLUE, lw=1.5, ls="--", zorder=4)
ax.plot([19.55, 20.5], [11.5, 11.5], color=LBLUE, lw=1.5, ls="--", zorder=4)
ax.plot([19.55, 20.5], [6.8, 6.8], color=LBLUE, lw=1.5, ls="--", zorder=4)


# ════════════════════════════════════════════════════════════════════════
# LEGEND
# ════════════════════════════════════════════════════════════════════════
box(0.3, 0.3, 19.8, 1.1, fc=WHITE, ec=LGRAY, lw=1, radius=0.3, zorder=3)
txt(0.7, 1.12, "Legend:", size=8.5, color=DGRAY, bold=True, ha="left")

legend_items = [
    (ARROW_MAIN,  False, "User / UI flow"),
    (ARROW_SESS,  False, "Session / SSE stream"),
    (ARROW_AGENT, True,  "ADK agent delegation"),
    (ARROW_TOOL,  True,  "Tool call / response"),
    (LGREEN,      True,  "Tool response (weather)"),
    (LBLUE,       False, "GCP service interaction"),
]
for i, (color, dashed, label_s) in enumerate(legend_items):
    lx = 2.5 + i * 3.1
    ly = 0.75
    ls = (0, (5, 3)) if dashed else "solid"
    ax.plot([lx, lx + 0.55], [ly, ly], color=color, lw=2.5, ls=ls, zorder=6)
    ax.annotate("", xy=(lx + 0.55, ly), xytext=(lx + 0.4, ly),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2,
                                mutation_scale=10), zorder=7)
    txt(lx + 0.7, ly, label_s, size=8, color=color, ha="left", bold=True)
    txt(lx + 0.7, ly - 0.28, "", size=7, color=MGRAY, ha="left")

plt.tight_layout(pad=0.2)
plt.savefig("architecture.png", dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("architecture.png saved")
