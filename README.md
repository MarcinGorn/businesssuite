BizSim - Business Strategy Simulator (Python + Pygame)

Setup
1) Python 3.11+ recommended
2) Create a venv (optional) and install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run
```
python main.py
```

Gameplay (foundation)
- Dashboard shows cash, assets, liabilities, net worth, macro indicators.
- Daily simulation runs roughly every real-time second.
- Press Ctrl+S to save to slot 1, Ctrl+L to load slot 1, B to request a small loan.
- Autosave runs every 5 minutes by default (configurable).

Controls
- H: toggle tutorial overlay; Enter/Backspace: next/previous tip
- 1/2/3/4: select stock ticker (RETL/MANU/REAL/TECH)
- , (comma): buy 1 share of selected ticker
- . (period): sell 1 share of selected ticker
- T: travel between cities (cycles A -> B -> C)
- N: create a new retail business (starter)
- U: upgrade the first business
- Procurement: R/F = reorder point +/-; O/P = order qty +/-; M = manual order
- Views: F1 Dashboard, F2 Finance (P&L), F3 Objectives

Architecture
- game/core: controller, models, events
- game/systems: economy, stock_market, banking, ai, save_manager
- game/ui: views (dashboard), charts, theme
- config: settings.json (window, autosave), balance.json (tunables)
- saves: JSON save slots (slot_1.json ... slot_5.json)

Notes
- This is a foundation emphasizing economic realism and robust save/load.
- Extend with more sectors, cities, trade routes, taxes, tutorials, and deeper UI.

