def stress_from_conflict(event):
    return event.impact * 0.4

def stress_from_grid_attack(attack):
    return attack.severity * 0.5

def stress_from_econ_shock(shock):
    return shock.severity * 0.6

def stress_from_news(news_event):
    return news_event.intensity * 0.3
