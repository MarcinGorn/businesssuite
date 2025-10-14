from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

from game.core.models import GameState


@dataclass
class EconomicEvent:
    name: str
    description: str
    severity: float  # 0-1
    duration_days: int
    kind: str  # crash, boom, regulation, rate_shock


class EventSystem:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.active: List[EconomicEvent] = []

    def tick_daily(self) -> None:
        # Resolve active events
        still_active = []
        for ev in self.active:
            self._apply_effect(ev)
            ev.duration_days -= 1
            if ev.duration_days > 0:
                still_active.append(ev)
        self.active = still_active

        # Randomly spawn new event with low probability
        if random.random() < 0.05:  # ~5% chance per day
            self._maybe_spawn_event()

    def _apply_effect(self, ev: EconomicEvent) -> None:
        m = self.state.market
        s = ev.severity
        if ev.kind == "crash":
            m.base_interest_rate = max(0.01, m.base_interest_rate - 0.002 * s)
            # reduce sector demand broadly
            for k in list(m.sector_demand.keys()):
                m.sector_demand[k] = max(0.3, m.sector_demand[k] - 0.05 * s)
        elif ev.kind == "boom":
            for k in list(m.sector_demand.keys()):
                m.sector_demand[k] = min(1.8, m.sector_demand[k] + 0.05 * s)
        elif ev.kind == "regulation":
            # increase competition pressure in targeted sector
            target = random.choice(list(m.sector_competition.keys()))
            m.sector_competition[target] = min(1.6, m.sector_competition[target] + 0.05 * s)
        elif ev.kind == "rate_shock":
            m.base_interest_rate = min(0.25, m.base_interest_rate + 0.01 * s)

    def _maybe_spawn_event(self) -> None:
        roll = random.random()
        if roll < 0.25:
            self.active.append(EconomicEvent("Market Crash", "Broad correction", 0.7, random.randint(5, 20), "crash"))
        elif roll < 0.5:
            self.active.append(EconomicEvent("Tech Boom", "Innovation surge", 0.6, random.randint(5, 20), "boom"))
        elif roll < 0.75:
            self.active.append(EconomicEvent("New Regulation", "Compliance costs rise", 0.5, random.randint(10, 30), "regulation"))
        else:
            self.active.append(EconomicEvent("Rate Hike", "Central bank raises rates", 0.8, random.randint(3, 10), "rate_shock"))


