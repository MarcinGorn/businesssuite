from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import time


@dataclass
class Player:
    name: str = "Founder"
    cash: float = 100000.0
    assets_value: float = 0.0
    liabilities_value: float = 0.0
    credit_score: int = 650  # 300 - 850
    portfolio: Dict[str, int] = field(default_factory=dict)  # ticker -> shares

    def net_worth(self) -> float:
        return self.cash + self.assets_value - self.liabilities_value


@dataclass
class Business:
    id: str = ""
    sector: str = "retail"  # retail, manufacturing, real_estate, tech
    location: str = "City A"
    capacity: float = 0.0  # production or service capacity
    # Supply chain & inventory
    inputs_stock: Dict[str, float] = field(default_factory=dict)  # input_name -> qty
    finished_goods: float = 0.0
    unit_cost: float = 0.0
    unit_price: float = 0.0
    employees: int = 0
    revenue_rolling: float = 0.0
    profit_rolling: float = 0.0
    carrying_cost_rate_daily: float = 0.0003  # cost to hold inventory per day
    reorder_point: float = 50.0  # simple single-threshold for each input
    order_quantity: float = 150.0
    active_orders: List[Dict[str, Any]] = field(default_factory=list)  # {input, qty, eta_days, unit_cost}


@dataclass
class WorldClock:
    epoch_seconds: float = field(default_factory=lambda: time.time())
    tick: int = 0  # number of sim ticks
    day: int = 1
    month: int = 1
    year: int = 2025

    def advance(self, days: int = 1) -> None:
        self.day += days
        while self.day > 30:
            self.day -= 30
            self.month += 1
        while self.month > 12:
            self.month -= 12
            self.year += 1
        self.tick += 1


@dataclass
class MarketState:
    # macro
    inflation_annual: float = 0.03
    base_interest_rate: float = 0.05
    cycle_phase: str = "expansion"  # expansion, peak, recession, recovery

    # sectors: demand index (0-2), competition intensity (0-2)
    sector_demand: Dict[str, float] = field(
        default_factory=lambda: {
            "retail": 1.0,
            "manufacturing": 1.0,
            "real_estate": 1.0,
            "tech": 1.0,
        }
    )
    sector_competition: Dict[str, float] = field(
        default_factory=lambda: {
            "retail": 1.0,
            "manufacturing": 1.0,
            "real_estate": 1.0,
            "tech": 1.0,
        }
    )

    # stock prices history per ticker
    stock_prices: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    businesses: List[Business] = field(default_factory=list)
    market: MarketState = field(default_factory=MarketState)
    clock: WorldClock = field(default_factory=WorldClock)
    city_economies: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {
            "City A": {"gdp": 100.0, "cost_index": 1.0, "opportunity": 1.0},
            "City B": {"gdp": 150.0, "cost_index": 1.2, "opportunity": 1.1},
            "City C": {"gdp": 70.0, "cost_index": 0.8, "opportunity": 0.9},
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


