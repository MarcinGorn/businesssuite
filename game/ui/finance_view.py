from __future__ import annotations

import pygame

from game.ui.theme import Theme
from game.systems.finance import Finance


class FinanceView:
    def __init__(self, screen: pygame.Surface, finance: Finance, bank, supply) -> None:
        self.screen = screen
        self.finance = finance
        self.bank = bank
        self.supply = supply

    def render(self) -> None:
        w, h = self.screen.get_size()
        self.screen.fill(Theme.BG)
        title = Theme.font(24).render("Finance", True, Theme.TEXT_PRIMARY)
        self.screen.blit(title, (20, 12))

        pnl = self.finance.get_pnl()
        box = pygame.Rect(20, 50, w - 40, 220)
        pygame.draw.rect(self.screen, Theme.PANEL, box, border_radius=8)
        y = box.y + 12
        for k in ["revenue", "cogs", "gross_profit", "opex", "operating_income", "interest", "pre_tax", "taxes", "net_income"]:
            line = Theme.font(16).render(f"{k.replace('_', ' ').title()}: {pnl[k]:.2f}", True, Theme.TEXT_PRIMARY)
            self.screen.blit(line, (box.x + 12, y))
            y += 20

        # Balance sheet panel
        loans_total = sum(getattr(l, "remaining", 0.0) for l in getattr(self.bank, "loans", []))
        input_costs = getattr(getattr(self.supply, "config", object()), "input_unit_costs", {}) or {}
        bs = self.finance.get_balance_sheet(loans_total, input_costs)
        bs_box = pygame.Rect(20, box.bottom + 10, w - 40, 180)
        pygame.draw.rect(self.screen, Theme.PANEL, bs_box, border_radius=8)
        y2 = bs_box.y + 12
        for k in [
            "assets_cash",
            "assets_inventory",
            "other_assets",
            "total_assets",
            "liabilities_loans",
            "other_liabilities",
            "total_liabilities",
            "equity",
        ]:
            line = Theme.font(16).render(f"{k.replace('_', ' ').title()}: {bs[k]:.2f}", True, Theme.TEXT_PRIMARY)
            self.screen.blit(line, (bs_box.x + 12, y2))
            y2 += 20


