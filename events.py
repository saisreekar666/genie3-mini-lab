
from dataclasses import dataclass
from typing import List, Callable, Tuple

@dataclass
class ScheduledEvent:
    step: int
    kind: str              # 'toggle_rain' | 'spawn_obstacles' | 'spawn_enemy'

class EventScheduler:
    def __init__(self, events: List[ScheduledEvent] = None):
        self.events = sorted(events or [], key=lambda e: e.step)
        self._idx = 0

    def reset(self):
        self._idx = 0

    def maybe_fire(self, world, t: int, on_fire: Callable[[str], None] = None):
        while self._idx < len(self.events) and self.events[self._idx].step == t:
            ev = self.events[self._idx]
            world.apply_event(ev.kind)
            if on_fire: on_fire(ev.kind)
            self._idx += 1
