from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import random

from game.core.models import GameState, Business


@dataclass
class Recipe:
    # inputs: name -> qty per unit output
    inputs: Dict[str, float]
    output_per_day_per_capacity: float  # units/day per 1.0 capacity


@dataclass
class SupplyConfig:
    lead_time_min_days: int = 3
    lead_time_max_days: int = 8
    input_unit_costs: Dict[str, float] = None  # set at runtime


class SupplyChain:
    def __init__(self, state: GameState, config: SupplyConfig | None = None) -> None:
        self.state = state
        self.config = config or SupplyConfig()
        if self.config.input_unit_costs is None:
            self.config.input_unit_costs = {"parts": 4.0, "materials": 2.5}
        # Simple recipes per sector
        self.recipes: Dict[str, Recipe] = {
            "retail": Recipe(inputs={}, output_per_day_per_capacity=1.0),
            "manufacturing": Recipe(inputs={"parts": 1.0, "materials": 0.5}, output_per_day_per_capacity=1.0),
            "real_estate": Recipe(inputs={}, output_per_day_per_capacity=0.1),
            "tech": Recipe(inputs={"parts": 0.2}, output_per_day_per_capacity=0.8),
        }

    def apply_balance_config(self, balance: dict) -> None:
        sc = balance.get("supply_chain", {})
        input_costs = sc.get("input_unit_costs")
        if isinstance(input_costs, dict):
            self.config.input_unit_costs.update(input_costs)
        lt = sc.get("lead_time_days")
        if isinstance(lt, list) and len(lt) == 2:
            self.config.lead_time_min_days = int(lt[0])
            self.config.lead_time_max_days = int(lt[1])
        recipes_cfg = sc.get("recipes")
        if isinstance(recipes_cfg, dict):
            # Optional recipe overrides
            for sector, r in recipes_cfg.items():
                inputs = r.get("inputs", {})
                opd = r.get("output_per_day_per_capacity", 1.0)
                if isinstance(inputs, dict):
                    self.recipes[sector] = Recipe(inputs=dict(inputs), output_per_day_per_capacity=float(opd))

    # --- Procurement ---
    def maybe_reorder(self, biz: Business) -> None:
        recipe = self.recipes.get(biz.sector)
        if not recipe or not recipe.inputs:
            return
        for input_name, _ in recipe.inputs.items():
            stock = biz.inputs_stock.get(input_name, 0.0)
            if stock <= biz.reorder_point:
                qty = biz.order_quantity
                eta = random.randint(self.config.lead_time_min_days, self.config.lead_time_max_days)
                unit_cost = self.config.input_unit_costs.get(input_name, 1.0)
                total_cost = qty * unit_cost
                if self.state.player.cash >= total_cost:
                    self.state.player.cash -= total_cost
                    biz.active_orders.append({
                        "input": input_name,
                        "qty": qty,
                        "eta_days": eta,
                        "unit_cost": unit_cost,
                    })

    def advance_orders(self, biz: Business) -> None:
        remaining = []
        for order in biz.active_orders:
            order["eta_days"] -= 1
            if order["eta_days"] <= 0:
                name = order["input"]
                biz.inputs_stock[name] = biz.inputs_stock.get(name, 0.0) + order["qty"]
            else:
                remaining.append(order)
        biz.active_orders = remaining

    def place_order(self, biz: Business, input_name: str, qty: float) -> bool:
        unit_cost = self.config.input_unit_costs.get(input_name, 1.0)
        total_cost = qty * unit_cost
        if self.state.player.cash < total_cost:
            return False
        eta = random.randint(self.config.lead_time_min_days, self.config.lead_time_max_days)
        self.state.player.cash -= total_cost
        biz.active_orders.append({
            "input": input_name,
            "qty": qty,
            "eta_days": eta,
            "unit_cost": unit_cost,
        })
        return True

    # --- Production ---
    def produce(self, biz: Business) -> None:
        recipe = self.recipes.get(biz.sector)
        if not recipe:
            return
        # Determine max output limited by inputs
        base_output = recipe.output_per_day_per_capacity * biz.capacity
        max_output_by_inputs = base_output
        for input_name, qty_per_unit in recipe.inputs.items():
            have = biz.inputs_stock.get(input_name, 0.0)
            if qty_per_unit > 0:
                max_output_by_inputs = min(max_output_by_inputs, have / qty_per_unit)
        output_units = max(0.0, min(base_output, max_output_by_inputs))
        # Consume inputs
        for input_name, qty_per_unit in recipe.inputs.items():
            need = output_units * qty_per_unit
            biz.inputs_stock[input_name] = max(0.0, biz.inputs_stock.get(input_name, 0.0) - need)
        biz.finished_goods += output_units
        # Carrying cost for inventory
        carrying_cost = (sum(biz.inputs_stock.values()) + biz.finished_goods) * biz.carrying_cost_rate_daily
        if carrying_cost > 0:
            self.state.player.cash -= carrying_cost
        return carrying_cost


