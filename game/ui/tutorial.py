from __future__ import annotations

import pygame
from dataclasses import dataclass
from typing import List

from game.ui.theme import Theme


@dataclass
class TutorialStep:
    title: str
    body: str


class Tutorial:
    def __init__(self) -> None:
        self.steps: List[TutorialStep] = [
            TutorialStep("Welcome", "Use B to request a bank loan. Ctrl+S to save, Ctrl+L to load."),
            TutorialStep("Time", "The simulation advances daily each real-time second."),
            TutorialStep("Stocks", "View the chart. Use 1-4 to select tickers. ,/. to buy/sell."),
            TutorialStep("Travel", "Press T to travel between cities and explore opportunities."),
            TutorialStep("Businesses", "Press N to start a new business. U to upgrade capacity."),
            TutorialStep("Help", "Press H anytime to toggle tutorial visibility."),
        ]
        self.index = 0
        self.visible = True

    def next(self) -> None:
        if self.index < len(self.steps) - 1:
            self.index += 1
        else:
            self.visible = False

    def prev(self) -> None:
        if self.index > 0:
            self.index -= 1

    def toggle(self) -> None:
        self.visible = not self.visible

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        box_w, box_h = min(640, w - 80), 200
        rect = pygame.Rect((w - box_w) // 2, (h - box_h) // 2, box_w, box_h)
        pygame.draw.rect(surface, Theme.PANEL, rect, border_radius=10)
        pygame.draw.rect(surface, Theme.ACCENT, rect, 2, border_radius=10)

        title = Theme.font(22).render(self.steps[self.index].title, True, Theme.TEXT_PRIMARY)
        body = Theme.font(16).render(self.steps[self.index].body, True, Theme.TEXT_PRIMARY)
        surface.blit(title, (rect.x + 16, rect.y + 16))
        surface.blit(body, (rect.x + 16, rect.y + 60))
        hint = Theme.font(14).render("[Enter] Next  [Backspace] Prev  [H] Hide", True, Theme.TEXT_MUTED)
        surface.blit(hint, (rect.x + 16, rect.bottom - 28))


