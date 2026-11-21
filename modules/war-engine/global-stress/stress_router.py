from core.event_bus.event_bus import subscribe, publish
from .stress_state import StressState
from .stress_update import update_stress

stress_state = StressState()

def handle_event(event):
    update_stress(stress_state, event)
    publish("global.stress", stress_state)

def init_stress_router():
    subscribe("conflict.event", handle_event)
    subscribe("grid.attack", handle_event)
    subscribe("econ.shock", handle_event)
    subscribe("news.event", handle_event)
