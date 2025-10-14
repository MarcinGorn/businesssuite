from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Any


@dataclass
class Event:
    type: str
    payload: Dict[str, Any]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        for handler in self._subscribers.get(event_type, []):
            handler(Event(event_type, payload))


