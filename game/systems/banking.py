from __future__ import annotations

from dataclasses import dataclass
from typing import List

from game.core.models import GameState
try:
    from game.systems.finance import Finance
except Exception:
    Finance = None  # type: ignore


@dataclass
class Loan:
    principal: float
    annual_rate: float
    remaining: float
    term_days: int


def rate_from_credit(credit_score: int, base_rate: float) -> float:
    # 300-850 -> 15%-3% over base spread
    normalized = max(300, min(850, credit_score))
    t = (normalized - 300) / (850 - 300)
    # interpolate from 0.15 to 0.03
    raw = 0.15 * (1 - t) + 0.03 * t
    # anchor around base
    return max(0.03, min(0.15, base_rate + (raw - 0.05)))


class Bank:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.loans: List[Loan] = []
        self.finance: Finance | None = None

    def request_loan(self, amount: float, term_days: int = 365) -> bool:
        if amount <= 0:
            return False
        rate = rate_from_credit(self.state.player.credit_score, self.state.market.base_interest_rate)
        # Simple underwriting: debt service coverage using net worth
        max_allowed = max(0.0, self.state.player.net_worth()) * 0.5 + self.state.player.cash * 0.5
        if amount > max_allowed:
            return False
        self.loans.append(Loan(principal=amount, annual_rate=rate, remaining=amount, term_days=term_days))
        self.state.player.cash += amount
        self.state.player.liabilities_value += amount
        return True

    def accrue_daily(self) -> None:
        to_remove = []
        for loan in self.loans:
            daily_rate = (1 + loan.annual_rate) ** (1 / 365) - 1
            interest = loan.remaining * daily_rate
            loan.remaining += interest
            loan.term_days -= 1
            if self.finance and interest > 0:
                self.finance.record_interest(interest, note="Loan interest")
            # Auto minimum payment if possible
            min_payment = loan.principal / 365
            payment = min(min_payment + interest, loan.remaining)
            if self.state.player.cash >= payment:
                self.state.player.cash -= payment
                loan.remaining -= payment
                if loan.remaining <= 0.01:
                    to_remove.append(loan)
            # If term ends and unpaid, negative impact to credit
            if loan.term_days <= 0 and loan.remaining > 0:
                self.state.player.credit_score = max(300, self.state.player.credit_score - 20)
        for l in to_remove:
            self.loans.remove(l)
            self.state.player.liabilities_value -= l.principal


