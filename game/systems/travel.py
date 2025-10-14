from __future__ import annotations

from dataclasses import dataclass

from game.core.models import GameState


@dataclass
class TravelCost:
    base_cost: float = 500.0
    time_days: int = 1


class TravelManager:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.cost = TravelCost()

    def travel(self, from_city: str, to_city: str) -> bool:
        if from_city == to_city:
            return False
        cost = self.cost.base_cost
        if self.state.player.cash < cost:
            return False
        self.state.player.cash -= cost
        # Travel time passage
        for _ in range(self.cost.time_days):
            self.state.clock.advance(1)
        return True


