from __future__ import annotations

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from game.core.models import GameState


class SaveManager:
    def __init__(self, saves_dir: str) -> None:
        self.saves_dir = saves_dir
        os.makedirs(self.saves_dir, exist_ok=True)

    def _slot_path(self, slot: int) -> str:
        return os.path.join(self.saves_dir, f"slot_{int(slot)}.json")

    def save(self, state: GameState, slot: int, autosave: bool = False) -> None:
        payload: Dict[str, Any] = {
            "meta": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "autosave": autosave,
                "version": 1,
            },
            "state": state.to_dict(),
        }
        with open(self._slot_path(slot), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self, slot: int) -> Optional[GameState]:
        path = self._slot_path(slot)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        state_dict = data.get("state", {})
        # Simple reconstruction; in a larger project use a schema/serializer
        from game.core.models import GameState as GS, Player, Business, MarketState, WorldClock

        player = Player(**state_dict.get("player", {}))
        businesses = [Business(**b) for b in state_dict.get("businesses", [])]
        market = MarketState(**state_dict.get("market", {}))
        clock = WorldClock(**state_dict.get("clock", {}))
        city_economies = state_dict.get("city_economies", {})
        return GS(player=player, businesses=businesses, market=market, clock=clock, city_economies=city_economies)

    def list_slots(self, max_slots: int = 5) -> Dict[int, bool]:
        return {i: os.path.exists(self._slot_path(i)) for i in range(1, max_slots + 1)}


