from __future__ import annotations

import pygame

from game.ui.theme import Theme
from game.systems.objectives import Objectives


class ObjectivesView:
    def __init__(self, screen: pygame.Surface, objectives: Objectives) -> None:
        self.screen = screen
        self.objectives = objectives

    def render(self) -> None:
        w, h = self.screen.get_size()
        self.screen.fill(Theme.BG)
        title = Theme.font(24).render("Objectives", True, Theme.TEXT_PRIMARY)
        self.screen.blit(title, (20, 12))

        box = pygame.Rect(20, 50, w - 40, h - 70)
        pygame.draw.rect(self.screen, Theme.PANEL, box, border_radius=8)
        y = box.y + 12
        for obj in self.objectives.objectives:
            status = "Done" if obj.completed else "In Progress"
            line = Theme.font(16).render(f"{obj.name} - {status}", True, Theme.TEXT_PRIMARY)
            self.screen.blit(line, (box.x + 12, y))
            y += 22
            desc = Theme.font(14).render(obj.description, True, Theme.TEXT_MUTED)
            self.screen.blit(desc, (box.x + 12, y))
            y += 22
        note = Theme.font(14).render("Progress updates daily. Achieve targets to complete objectives.", True, Theme.TEXT_MUTED)
        self.screen.blit(note, (box.x + 12, box.bottom - 28))


