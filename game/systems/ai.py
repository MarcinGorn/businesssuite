from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random

from game.core.models import GameState, Business


@dataclass
class Competitor:
    name: str
    sector: str
    location: str
    aggressiveness: float  # 0-1


class AIManager:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.competitors: List[Competitor] = [
            Competitor("ShopCo", "retail", "City A", 0.5),
            Competitor("BuildWorks", "manufacturing", "City B", 0.6),
            Competitor("EstateOne", "real_estate", "City C", 0.4),
            Competitor("TechNova", "tech", "City A", 0.7),
        ]

    def tick_daily(self) -> None:
        # Adjust competition pressure based on AI actions
        sector_pressure = {s: 0.0 for s in ["retail", "manufacturing", "real_estate", "tech"]}
        for comp in self.competitors:
            demand = self.state.market.sector_demand.get(comp.sector, 1.0)
            if demand > 1.0 and random.random() < comp.aggressiveness * 0.3:
                # expand
                sector_pressure[comp.sector] += 0.02
            else:
                # maintain or contract slightly
                sector_pressure[comp.sector] += 0.0
        for s, p in sector_pressure.items():
            self.state.market.sector_competition[s] = max(0.7, min(1.5, self.state.market.sector_competition.get(s, 1.0) + p - 0.01))


