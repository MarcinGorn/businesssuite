import os
import sys
import time
import pygame

from game.core.controller import GameController
from game.systems.save_manager import SaveManager


def load_settings(config_dir: str) -> dict:
    import json
    settings_path = os.path.join(config_dir, "settings.json")
    if not os.path.exists(settings_path):
        return {
            "window": {"width": 1280, "height": 720},
            "fps": 60,
            "autosave_seconds": 300,
            "default_save_slot": 1,
        }
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base_dir, "config")
    saves_dir = os.path.join(base_dir, "saves")
    os.makedirs(saves_dir, exist_ok=True)

    settings = load_settings(config_dir)

    pygame.init()
    pygame.display.set_caption("BizSim - Business Strategy Simulator")
    window_size = (
        settings.get("window", {}).get("width", 1280),
        settings.get("window", {}).get("height", 720),
    )
    screen = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()

    save_manager = SaveManager(saves_dir=saves_dir)
    controller = GameController(screen=screen, config_dir=config_dir, save_manager=save_manager)

    last_autosave = time.time()
    autosave_interval = int(settings.get("autosave_seconds", 300))

    running = True
    while running:
        dt_seconds = clock.tick(settings.get("fps", 60)) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controller.handle_pygame_event(event)

        controller.update(dt_seconds)
        controller.render()
        pygame.display.flip()

        if time.time() - last_autosave >= autosave_interval:
            save_slot = settings.get("default_save_slot", 1)
            controller.autosave(slot=save_slot)
            last_autosave = time.time()

    # On exit, attempt a final save
    try:
        controller.autosave(slot=settings.get("default_save_slot", 1))
    except Exception:
        pass

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())


