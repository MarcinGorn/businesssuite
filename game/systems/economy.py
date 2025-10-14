from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import math
import random

from game.core.models import GameState
from game.systems.supply_chain import SupplyChain
from typing import Optional
try:
    from game.systems.finance import Finance
except Exception:
    Finance = None  # type: ignore
try:
    from game.systems.objectives import Objectives
except Exception:
    Objectives = None  # type: ignore


@dataclass
class EconomyConfig:
    demand_sensitivity: float = 0.6
    competition_pressure: float = 0.4
    inflation_drift: float = 0.0005  # per day
    interest_reversion: float = 0.01
    cycle_speed: float = 0.03


class EconomyEngine:
    def __init__(self, state: GameState, config: EconomyConfig | None = None) -> None:
        self.state = state
        self.config = config or EconomyConfig()
        self._cycle_angle = 0.0
        self.supply = SupplyChain(self.state)
        self.finance: Optional[Finance] = None  # injected
        self.objectives: Optional[Objectives] = None  # injected

    def simulate_day(self) -> None:
        self._update_macro()
        self._update_sectors()
        self._simulate_businesses()
        self.state.clock.advance(1)

    def _update_macro(self) -> None:
        # Business cycles via sine; map to phases
        self._cycle_angle = (self._cycle_angle + self.config.cycle_speed) % (2 * math.pi)
        cycle_value = math.sin(self._cycle_angle)
        if cycle_value > 0.5:
            self.state.market.cycle_phase = "peak"
        elif cycle_value > 0:
            self.state.market.cycle_phase = "expansion"
        elif cycle_value > -0.5:
            self.state.market.cycle_phase = "recovery"
        else:
            self.state.market.cycle_phase = "recession"

        # Inflation random walk with slight drift
        infl = self.state.market.inflation_annual
        infl += random.uniform(-self.config.inflation_drift, self.config.inflation_drift) + self.config.inflation_drift
        self.state.market.inflation_annual = max(0.0, min(0.15, infl))

        # Interest mean reversion around 5%
        r = self.state.market.base_interest_rate
        r += (0.05 - r) * self.config.interest_reversion + random.uniform(-0.001, 0.001)
        self.state.market.base_interest_rate = max(0.01, min(0.2, r))

    def _update_sectors(self) -> None:
        for sector, demand in list(self.state.market.sector_demand.items()):
            competition = self.state.market.sector_competition.get(sector, 1.0)
            # Demand pulled down by competition, modulated by cycle
            cycle_multiplier = 1.0
            if self.state.market.cycle_phase == "peak":
                cycle_multiplier = 1.1
            elif self.state.market.cycle_phase == "expansion":
                cycle_multiplier = 1.05
            elif self.state.market.cycle_phase == "recession":
                cycle_multiplier = 0.9
            elif self.state.market.cycle_phase == "recovery":
                cycle_multiplier = 1.0

            demand += self.config.demand_sensitivity * (cycle_multiplier - 1.0)
            demand -= self.config.competition_pressure * (competition - 1.0)
            demand += random.uniform(-0.02, 0.02)
            self.state.market.sector_demand[sector] = max(0.3, min(1.7, demand))

    def _simulate_businesses(self) -> None:
        # Simple pricing power: higher demand and lower competition allow higher margin
        for biz in self.state.businesses:
            # Supply chain step: advance orders, maybe reorder, produce
            self.supply.advance_orders(biz)
            self.supply.maybe_reorder(biz)
            carrying_cost = self.supply.produce(biz)
            if self.finance and carrying_cost > 0:
                self.finance.record_opex(carrying_cost, note=f"Carrying cost {biz.id}")
            demand_idx = self.state.market.sector_demand.get(biz.sector, 1.0)
            competition_idx = self.state.market.sector_competition.get(biz.sector, 1.0)
            pricing_power = demand_idx / max(0.5, competition_idx)

            # Adjust unit price with inflation and pricing power
            inflation_daily = (1 + self.state.market.inflation_annual) ** (1 / 365) - 1
            biz.unit_price *= 1 + inflation_daily
            target_margin = 0.1 * pricing_power
            target_price = biz.unit_cost * (1 + max(0.05, min(0.6, target_margin)))
            biz.unit_price = 0.5 * biz.unit_price + 0.5 * target_price

            # Sales volume driven by demand and capacity
            base_sales = biz.capacity * demand_idx
            realized_sales = min(base_sales, biz.finished_goods)
            revenue = realized_sales * biz.unit_price
            cost = realized_sales * biz.unit_cost
            profit = revenue - cost
            biz.revenue_rolling = 0.9 * biz.revenue_rolling + 0.1 * revenue
            biz.profit_rolling = 0.9 * biz.profit_rolling + 0.1 * profit

            # Update player aggregates
            self.state.player.cash += profit
            self.state.player.assets_value += max(0.0, profit) * 0.2
            # Reduce finished goods by sales
            biz.finished_goods = max(0.0, biz.finished_goods - realized_sales)

            # Record finance and objectives
            if self.finance:
                if revenue > 0:
                    self.finance.record_revenue(revenue, note=f"Sales {biz.id}")
                if cost > 0:
                    self.finance.record_cogs(cost, note=f"COGS {biz.id}")
            if self.objectives and revenue > 0:
                try:
                    self.objectives.record_revenue(revenue)
                except Exception:
                    pass


