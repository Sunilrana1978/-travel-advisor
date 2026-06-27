# travel_agent/__init__.py
# Exposes root_agent so `adk run travel_agent` and `adk web .` work out of the box.
from travel_agent.agent import root_agent

__all__ = ["root_agent"]
