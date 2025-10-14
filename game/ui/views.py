from __future__ import annotations

import pygame
from typing import Tuple

from game.ui.theme import Theme
from game.ui.charts import line_chart
from game.core.models import GameState


class DashboardView:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def render(self, state: GameState) -> None:
        self.screen.fill(Theme.BG)
        width, height = self.screen.get_size()

        # Header
        title_font = Theme.font(24)
        title = title_font.render("BizSim Dashboard", True, Theme.TEXT_PRIMARY)
        self.screen.blit(title, (20, 12))

        # Panels
        panel_rect = pygame.Rect(20, 50, width - 40, 160)
        pygame.draw.rect(self.screen, Theme.PANEL, panel_rect, border_radius=8)

        # Key metrics
        metrics = [
            ("Cash", state.player.cash),
            ("Assets", state.player.assets_value),
            ("Liabilities", state.player.liabilities_value),
            ("Net Worth", state.player.net_worth()),
            ("Credit", state.player.credit_score),
            ("Inflation", state.market.inflation_annual * 100),
            ("Base Rate", state.market.base_interest_rate * 100),
            ("Phase", state.market.cycle_phase),
        ]

        label_font = Theme.font(16)
        value_font = Theme.font(18)
        x = 30
        y = 65
        for label, value in metrics:
            text = f"{label}: {value:.2f}" if isinstance(value, (int, float)) else f"{label}: {value}"
            label_surf = label_font.render(text, True, Theme.TEXT_PRIMARY)
            self.screen.blit(label_surf, (x, y))
            y += 24
            if y > 180:
                y = 65
                x += 260

        # Portfolio panel and stock chart
        chart_rect = pygame.Rect(20, 220, width - 40, height - 320)
        ticker = getattr(self, "selected_ticker", "TECH")
        history = state.market.stock_prices.get(ticker, [])
        line_chart(self.screen, history, chart_rect, Theme.ACCENT)

        bottom_panel = pygame.Rect(20, height - 90, width - 40, 70)
        pygame.draw.rect(self.screen, Theme.PANEL, bottom_panel, border_radius=8)
        last_price = history[-1] if history else 0.0
        position = state.player.portfolio.get(ticker, 0)
        info = f"Ticker: {ticker} | Price: {last_price:.2f} | Shares: {position}  [1-4 switch, ,/. buy/sell]"
        info_surf = label_font.render(info, True, Theme.TEXT_PRIMARY)
        self.screen.blit(info_surf, (bottom_panel.x + 12, bottom_panel.y + 22))


