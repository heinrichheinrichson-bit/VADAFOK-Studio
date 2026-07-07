from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class OBSWorkflowState:
    def __init__(self) -> None:
        self.connected: bool = False
        self.connected_since: str = ""
        self.last_error: str = ""
        self.last_command: str = ""
        self.last_command_time: str = ""
        self.last_banner_text: str = ""
        self.last_banner_action: str = ""
        self.banner_count: int = 0
        self.scenes: List[str] = []
        self.current_scene: str = ""
        self.sources: List[str] = []
        self.banner_history: List[str] = []
        self.obs_events: List[str] = []
        self.log: List[str] = []

    def now(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def add_log(self, message: str) -> None:
        self.log.append(f"{self.now()}  {message}")
        self.log = self.log[-100:]

    def add_event(self, message: str) -> None:
        self.obs_events.append(f"{self.now()}  {message}")
        self.obs_events = self.obs_events[-60:]
        self.add_log(message)

    def command(self, message: str) -> None:
        self.last_command = message
        self.last_command_time = self.now()
        self.add_log(message)

    def set_connected(self, value: bool) -> None:
        if value and not self.connected_since:
            self.connected_since = self.now()
        if not value:
            self.connected_since = ""
        self.connected = value

    def banner(self, action: str, text: str = "") -> None:
        self.last_banner_action = action
        self.last_banner_text = text
        self.banner_count += 1
        entry = f"{self.now()}  {action}"
        if text:
            entry += f"  —  {text[:120]}"
        self.banner_history.append(entry)
        self.banner_history = self.banner_history[-60:]
        if text:
            self.command(f"{action}: {text[:80]}")
        else:
            self.command(action)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "connected": self.connected,
            "connected_since": self.connected_since,
            "last_error": self.last_error,
            "last_command": self.last_command,
            "last_command_time": self.last_command_time,
            "last_banner_text": self.last_banner_text,
            "last_banner_action": self.last_banner_action,
            "banner_count": self.banner_count,
            "scenes": list(self.scenes),
            "current_scene": self.current_scene,
            "sources": list(self.sources),
            "banner_history": list(self.banner_history),
            "obs_events": list(self.obs_events),
            "log": list(self.log),
        }
