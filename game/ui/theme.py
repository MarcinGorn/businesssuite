from __future__ import annotations

import pygame


class Theme:
    BG = (18, 18, 20)
    PANEL = (28, 28, 32)
    TEXT_PRIMARY = (230, 230, 235)
    TEXT_MUTED = (170, 170, 180)
    ACCENT = (64, 156, 255)
    POSITIVE = (46, 204, 113)
    NEGATIVE = (231, 76, 60)

    @staticmethod
    def font(size: int) -> pygame.font.Font:
        return pygame.font.SysFont("Menlo", size)


