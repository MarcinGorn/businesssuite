from __future__ import annotations

import os
from typing import Optional
import pygame

from game.core.models import GameState, Business
from game.core.events import EventBus
from game.systems.economy import EconomyEngine
from game.systems.stock_market import StockMarket
from game.systems.banking import Bank
from game.systems.ai import AIManager
from game.systems.save_manager import SaveManager
from game.systems.events import EventSystem
from game.systems.taxes import TaxAuthority
from game.systems.travel import TravelManager
from game.ui.views import DashboardView
from game.ui.charts import line_chart
from game.ui.theme import Theme
from game.ui.tutorial import Tutorial
from game.systems.finance import Finance
from game.systems.objectives import Objectives
from game.ui.finance_view import FinanceView
from game.ui.objectives_view import ObjectivesView


class GameController:
    def __init__(self, screen: pygame.Surface, config_dir: str, save_manager: SaveManager) -> None:
        self.screen = screen
        self.config_dir = config_dir
        self.save_manager = save_manager
        self.events = EventBus()
        self.state = GameState()

        # Systems
        self.economy = EconomyEngine(self.state)
        self.stocks = StockMarket(self.state)
        self.bank = Bank(self.state)
        self.ai = AIManager(self.state)
        self.events_sys = EventSystem(self.state)
        self.tax = TaxAuthority(self.state)
        self.travel_mgr = TravelManager(self.state)
        # Load balance for supply chain
        self._load_balance()
        self.economy.supply.apply_balance_config(self._balance)

        # UI
        self.view = DashboardView(self.screen)
        self.tutorial = Tutorial()
        self.finance = Finance(self.state)
        self.objectives = Objectives(self.state)
        self.finance_view = FinanceView(self.screen, self.finance, self.bank, self.economy.supply)
        self.objectives_view = ObjectivesView(self.screen, self.objectives)
        # Inject finance/objectives into systems
        self.economy.finance = self.finance
        self.economy.objectives = self.objectives
        self.bank.finance = self.finance
        self.tax.finance = self.finance

        # Ensure starting business
        if not self.state.businesses:
            self.state.businesses.append(
                Business(
                    id="BIZ-1",
                    sector="retail",
                    location="City A",
                    capacity=100.0,
                    finished_goods=30.0,
                    unit_cost=8.0,
                    unit_price=12.0,
                    employees=5,
                )
            )

    def handle_pygame_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.save(slot=1)
            if event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.load(slot=1)
            if event.key == pygame.K_b:
                # request small loan
                self.bank.request_loan(10000.0, term_days=180)
            if event.key == pygame.K_t:
                # travel City A -> City B -> City C cycle
                current = self.state.businesses[0].location
                dest = "City B" if current == "City A" else ("City C" if current == "City B" else "City A")
                self.travel_mgr.travel(current, dest)
                self.state.businesses[0].location = dest
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                mapping = {pygame.K_1: "RETL", pygame.K_2: "MANU", pygame.K_3: "REAL", pygame.K_4: "TECH"}
                self.view.selected_ticker = mapping[event.key]
            if event.key == pygame.K_COMMA:  # buy 1 share
                self._buy_selected(1)
            if event.key == pygame.K_PERIOD:  # sell 1 share
                self._sell_selected(1)
            if event.key == pygame.K_RETURN:
                self.tutorial.next()
            if event.key == pygame.K_BACKSPACE:
                self.tutorial.prev()
            if event.key == pygame.K_h:
                self.tutorial.toggle()
            if event.key == pygame.K_n:
                self._create_business()
            if event.key == pygame.K_u:
                self._upgrade_business()
            # Procurement UI
            if event.key == pygame.K_r:  # adjust reorder point +10
                if self.state.businesses:
                    self.state.businesses[0].reorder_point += 10
            if event.key == pygame.K_f:  # adjust reorder point -10
                if self.state.businesses:
                    self.state.businesses[0].reorder_point = max(0, self.state.businesses[0].reorder_point - 10)
            if event.key == pygame.K_o:  # adjust order qty +25
                if self.state.businesses:
                    self.state.businesses[0].order_quantity += 25
            if event.key == pygame.K_p:  # adjust order qty -25
                if self.state.businesses:
                    self.state.businesses[0].order_quantity = max(0, self.state.businesses[0].order_quantity - 25)
            if event.key == pygame.K_m:  # manual order for first input type
                if self.state.businesses:
                    biz = self.state.businesses[0]
                    inputs = list(self.economy.supply.recipes.get(biz.sector, self.economy.supply.recipes["retail"]).inputs.keys())
                    if inputs:
                        self.economy.supply.place_order(biz, inputs[0], max(1.0, biz.order_quantity))
            # View toggles
            if event.key == pygame.K_F1:
                self.view.mode = "dashboard"
            if event.key == pygame.K_F2:
                self.view.mode = "finance"
            if event.key == pygame.K_F3:
                self.view.mode = "objectives"

    def update(self, dt_seconds: float) -> None:
        # Accumulate time and simulate daily steps approx every second for demo
        # In a more refined sim, time scaling and calendar would be more precise
        if not hasattr(self, "_accum"):
            self._accum = 0.0
        self._accum += dt_seconds
        while self._accum >= 1.0:
            self.economy.simulate_day()
            self.stocks.tick_daily()
            self.bank.accrue_daily()
            self.ai.tick_daily()
            self.events_sys.tick_daily()
            self.tax.accrue_daily()
            # Update objectives daily
            self.objectives.tick_daily()
            self._accum -= 1.0

    def render(self) -> None:
        mode = getattr(self.view, "mode", "dashboard")
        if mode == "finance":
            self.finance_view.render()
        elif mode == "objectives":
            self.objectives_view.render()
        else:
            self.view.render(self.state)
        # Simple chart panel for TECH ticker
        w, h = self.screen.get_size()
        rect = pygame.Rect(20, 220, w - 40, h - 240)
        tech_history = self.state.market.stock_prices.get("TECH", [])
        line_chart(self.screen, tech_history, rect)
        self.tutorial.render(self.screen)
        # Procurement hints
        w, h = self.screen.get_size()
        help_rect = pygame.Rect(400, 220, w - 420, 160)
        pygame.draw.rect(self.screen, Theme.PANEL, help_rect, border_radius=8)
        label = Theme.font(14).render("Procurement: [R/F] Reorder +/-  [O/P] OrderQty +/-  [M] Manual Order", True, Theme.TEXT_MUTED)
        self.screen.blit(label, (help_rect.x + 12, help_rect.y + 12))

    def save(self, slot: int) -> None:
        self.save_manager.save(self.state, slot=slot, autosave=False)

    def autosave(self, slot: int) -> None:
        self.save_manager.save(self.state, slot=slot, autosave=True)

    def load(self, slot: int) -> None:
        loaded = self.save_manager.load(slot)
        if loaded is not None:
            self.state = loaded
            # Re-wire systems to the loaded state
            self.economy.state = self.state
            self.stocks.state = self.state
            self.bank.state = self.state
            self.ai.state = self.state
            self.events_sys.state = self.state
            self.tax.state = self.state
            self.travel_mgr.state = self.state

    # --- Portfolio helpers ---
    def _current_ticker(self) -> str:
        return getattr(self.view, "selected_ticker", "TECH")

    def _current_price(self) -> float:
        ticker = self._current_ticker()
        history = self.state.market.stock_prices.get(ticker, [100.0])
        return history[-1]

    def _buy_selected(self, qty: int) -> None:
        price = self._current_price()
        cost = price * qty
        if self.state.player.cash >= cost:
            self.state.player.cash -= cost
            t = self._current_ticker()
            self.state.player.portfolio[t] = self.state.player.portfolio.get(t, 0) + qty

    def _sell_selected(self, qty: int) -> None:
        t = self._current_ticker()
        owned = self.state.player.portfolio.get(t, 0)
        if owned <= 0:
            return
        sell_qty = min(qty, owned)
        price = self._current_price()
        self.state.player.cash += price * sell_qty
        self.state.player.portfolio[t] = owned - sell_qty

    # --- Business management ---
    def _create_business(self) -> None:
        # Flat startup cost, small capacity
        cost = 20000.0
        if self.state.player.cash < cost:
            return
        self.state.player.cash -= cost
        new_id = f"BIZ-{len(self.state.businesses) + 1}"
        self.state.businesses.append(
            Business(
                id=new_id,
                sector="retail",
                location="City A",
                capacity=60.0,
                inventory=20.0,
                unit_cost=7.0,
                unit_price=10.0,
                employees=3,
            )
        )

    def _upgrade_business(self) -> None:
        if not self.state.businesses:
            return
        biz = self.state.businesses[0]
        upgrade_cost = 5000.0
        if self.state.player.cash < upgrade_cost:
            return
        self.state.player.cash -= upgrade_cost
        biz.capacity *= 1.15
        biz.unit_cost *= 0.98

    # --- Config loading ---
    def _load_balance(self) -> None:
        import json, os
        path = os.path.join(self.config_dir, "balance.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._balance = json.load(f)
        except Exception:
            self._balance = {}


