from .stress_sources import (
    stress_from_conflict,
    stress_from_grid_attack,
    stress_from_econ_shock,
    stress_from_news
)

def update_stress(stress_state, event):
    if event.__class__.__name__ == "ConflictEvent":
        amount = stress_from_conflict(event)
    elif event.__class__.__name__ == "GridAttack":
        amount = stress_from_grid_attack(event)
    elif event.__class__.__name__ == "ShockEvent":
        amount = stress_from_econ_shock(event)
    elif event.__class__.__name__ == "NewsEvent":
        amount = stress_from_news(event)
    else:
        amount = 0

    stress_state.apply(amount, event)
