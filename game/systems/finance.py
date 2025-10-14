from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from game.core.models import GameState, Business


@dataclass
class FinanceTotals:
    revenue: float = 0.0
    cogs: float = 0.0
    opex: float = 0.0
    interest: float = 0.0
    taxes: float = 0.0


class Finance:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.totals = FinanceTotals()
        self.ledger: List[Dict] = []  # simple list of transactions for display

    # --- Recorders ---
    def record_revenue(self, amount: float, note: str = "") -> None:
        if amount <= 0:
            return
        self.totals.revenue += amount
        self._log("revenue", amount, note)

    def record_cogs(self, amount: float, note: str = "") -> None:
        if amount <= 0:
            return
        self.totals.cogs += amount
        self._log("cogs", -amount, note)

    def record_opex(self, amount: float, note: str = "") -> None:
        if amount <= 0:
            return
        self.totals.opex += amount
        self._log("opex", -amount, note)

    def record_interest(self, amount: float, note: str = "") -> None:
        if amount <= 0:
            return
        self.totals.interest += amount
        self._log("interest", -amount, note)

    def record_tax(self, amount: float, note: str = "") -> None:
        if amount <= 0:
            return
        self.totals.taxes += amount
        self._log("tax", -amount, note)

    def _log(self, kind: str, amount: float, note: str) -> None:
        self.ledger.append({
            "day": self.state.clock.day,
            "month": self.state.clock.month,
            "year": self.state.clock.year,
            "kind": kind,
            "amount": amount,
            "cash": self.state.player.cash,
            "note": note,
        })

    # --- Statements ---
    def get_pnl(self) -> Dict[str, float]:
        gross_profit = self.totals.revenue - self.totals.cogs
        operating_income = gross_profit - self.totals.opex
        pre_tax = operating_income - self.totals.interest
        net_income = pre_tax - self.totals.taxes
        return {
            "revenue": self.totals.revenue,
            "cogs": self.totals.cogs,
            "gross_profit": gross_profit,
            "opex": self.totals.opex,
            "operating_income": operating_income,
            "interest": self.totals.interest,
            "pre_tax": pre_tax,
            "taxes": self.totals.taxes,
            "net_income": net_income,
        }

    def _inventory_valuation(self, biz: Business, input_unit_costs: Dict[str, float]) -> float:
        inputs_val = sum(qty * float(input_unit_costs.get(name, 1.0)) for name, qty in biz.inputs_stock.items())
        finished_val = biz.finished_goods * max(0.0, biz.unit_cost)
        return inputs_val + finished_val

    def get_balance_sheet(self, bank_loans_remaining: float, input_unit_costs: Dict[str, float]) -> Dict[str, float]:
        assets_cash = self.state.player.cash
        assets_inventory = sum(self._inventory_valuation(b, input_unit_costs) for b in self.state.businesses)
        other_assets = self.state.player.assets_value
        total_assets = assets_cash + assets_inventory + other_assets

        liabilities_loans = bank_loans_remaining
        other_liabilities = self.state.player.liabilities_value
        total_liabilities = liabilities_loans + other_liabilities

        equity = total_assets - total_liabilities
        return {
            "assets_cash": assets_cash,
            "assets_inventory": assets_inventory,
            "other_assets": other_assets,
            "total_assets": total_assets,
            "liabilities_loans": liabilities_loans,
            "other_liabilities": other_liabilities,
            "total_liabilities": total_liabilities,
            "equity": equity,
        }


