from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import random

from game.core.models import GameState


@dataclass
class StockConfig:
    volatility: float = 0.02
    trend_strength: float = 0.001


class StockMarket:
    def __init__(self, state: GameState, config: StockConfig | None = None) -> None:
        self.state = state
        self.config = config or StockConfig()
        if not self.state.market.stock_prices:
            # seed a few tickers with initial prices
            self.state.market.stock_prices = {
                "RETL": [50.0],
                "MANU": [40.0],
                "REAL": [60.0],
                "TECH": [80.0],
            }

    def tick_daily(self) -> None:
        phase = self.state.market.cycle_phase
        inflation = self.state.market.inflation_annual
        macro_trend = 0.0
        if phase == "peak":
            macro_trend = -0.001
        elif phase == "expansion":
            macro_trend = 0.001
        elif phase == "recovery":
            macro_trend = 0.0005
        elif phase == "recession":
            macro_trend = -0.0015

        for ticker, history in self.state.market.stock_prices.items():
            last = history[-1]
            sector = {
                "RETL": "retail",
                "MANU": "manufacturing",
                "REAL": "real_estate",
                "TECH": "tech",
            }[ticker]
            demand = self.state.market.sector_demand.get(sector, 1.0)
            comp = self.state.market.sector_competition.get(sector, 1.0)
            sector_signal = (demand - 1.0) - (comp - 1.0)
            drift = self.config.trend_strength * (sector_signal + macro_trend)
            shock = random.gauss(0.0, self.config.volatility)
            daily_return = drift + shock - inflation / 365 * 0.3
            new_price = max(1.0, last * (1.0 + daily_return))
            history.append(new_price)


