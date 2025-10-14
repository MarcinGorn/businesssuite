from __future__ import annotations

import pygame
from typing import List, Tuple

from game.ui.theme import Theme


def line_chart(surface: pygame.Surface, data: List[float], rect: pygame.Rect, color: Tuple[int, int, int] | None = None) -> None:
    if not data:
        return
    color = color or Theme.ACCENT
    pygame.draw.rect(surface, Theme.PANEL, rect, border_radius=6)
    n = len(data)
    if n < 2:
        return
    pad = 8
    inner = rect.inflate(-2 * pad, -2 * pad)
    min_v = min(data)
    max_v = max(data)
    rng = max(1e-6, max_v - min_v)
    points = []
    for i, v in enumerate(data[-200:]):
        t = i / max(1, min(199, n - 1))
        x = inner.left + int(t * inner.width)
        y = inner.bottom - int(((v - min_v) / rng) * inner.height)
        points.append((x, y))
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 2)


