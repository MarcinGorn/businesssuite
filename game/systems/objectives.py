from __future__ import annotations

from dataclasses import dataclass
from typing import List

from game.core.models import GameState


@dataclass
class Objective:
    name: str
    description: str
    target: float
    kind: str  # net_worth, credit, revenue
    completed: bool = False


class Objectives:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.objectives: List[Objective] = [
            Objective("First Million", "Reach net worth of 1,000,000", 1_000_000, "net_worth"),
            Objective("Prime Credit", "Reach credit score of 750", 750, "credit"),
            Objective("Revenue Run", "Achieve cumulative revenue of 500,000", 500_000, "revenue"),
        ]
        self.cumulative_revenue: float = 0.0

    def record_revenue(self, amount: float) -> None:
        self.cumulative_revenue += max(0.0, amount)

    def tick_daily(self) -> None:
        for obj in self.objectives:
            if obj.completed:
                continue
            if obj.kind == "net_worth" and self.state.player.net_worth() >= obj.target:
                obj.completed = True
            elif obj.kind == "credit" and self.state.player.credit_score >= obj.target:
                obj.completed = True
            elif obj.kind == "revenue" and self.cumulative_revenue >= obj.target:
                obj.completed = True


