from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class OBSWorkflowState:
    def __init__(self) -> None:
        self.connected: bool = False
        self.last_error: str = ""
        self.last_command: str = ""
        self.last_command_time: str = ""
        self.last_banner_text: str = ""
        self.last_banner_action: str = ""
        self.scenes: List[str] = []
        self.sources: List[str] = []
        self.log: List[str] = []

    def add_log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"{stamp}  {message}")
        self.log = self.log[-100:]

    def command(self, message: str) -> None:
        self.last_command = message
        self.last_command_time = datetime.now().strftime("%H:%M:%S")
        self.add_log(message)

    def banner(self, action: str, text: str = "") -> None:
        self.last_banner_action = action
        self.last_banner_text = text
        if text:
            self.command(f"{action}: {text[:80]}")
        else:
            self.command(action)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "connected": self.connected,
            "last_error": self.last_error,
            "last_command": self.last_command,
            "last_command_time": self.last_command_time,
            "last_banner_text": self.last_banner_text,
            "last_banner_action": self.last_banner_action,
            "scenes": list(self.scenes),
            "sources": list(self.sources),
            "log": list(self.log),
        }
