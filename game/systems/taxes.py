from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal

from game.core.models import GameState
try:
    from game.systems.finance import Finance
except Exception:
    Finance = None  # type: ignore


@dataclass
class TaxConfig:
    corporate_rate: float = 0.21
    personal_rate: float = 0.24
    cadence_days: int = 30  # simple monthly settlement


class TaxAuthority:
    def __init__(self, state: GameState, config: TaxConfig | None = None) -> None:
        self.state = state
        self.config = config or TaxConfig()
        self._accum_profit = 0.0
        self._accum_income = 0.0
        self._days = 0
        self.ledger: List[dict] = []  # simple transaction ledger
        self.finance: Finance | None = None

    def accrue_daily(self) -> None:
        # Approximate profits as sum of business rolling profits scaled
        day_profit = sum(b.profit_rolling * 0.05 for b in self.state.businesses)
        self._accum_profit += max(0.0, day_profit)
        # Approximate personal income as max(0, change in cash)
        # For simplicity, skip exact delta tracking; use a fraction of profit as income
        self._accum_income += max(0.0, day_profit * 0.5)
        self._days += 1
        if self._days >= self.config.cadence_days:
            self._settle_taxes()
            self._days = 0
            self._accum_profit = 0.0
            self._accum_income = 0.0

    def _settle_taxes(self) -> None:
        corporate_tax = self._accum_profit * self.config.corporate_rate
        personal_tax = self._accum_income * self.config.personal_rate
        total_due = corporate_tax + personal_tax
        if self.state.player.cash >= total_due:
            self.state.player.cash -= total_due
        else:
            shortfall = total_due - self.state.player.cash
            self.state.player.cash = 0.0
            # penalize credit if unpaid fully
            self.state.player.credit_score = max(300, self.state.player.credit_score - int(shortfall / 1000))
        self._record("tax_payment", -total_due)
        if self.finance and total_due > 0:
            self.finance.record_tax(total_due, note="Monthly tax settlement")

    def _record(self, kind: str, amount: float) -> None:
        self.ledger.append({
            "day": self.state.clock.day,
            "month": self.state.clock.month,
            "year": self.state.clock.year,
            "kind": kind,
            "amount": amount,
            "cash": self.state.player.cash,
        })


