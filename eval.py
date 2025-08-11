
from typing import Dict, List
from world import World
from agent import bfs_plan, path_to_actions
from events import EventScheduler, ScheduledEvent

def evaluate(world_cfg: Dict, trials: int = 20) -> Dict:
    """Run a batch of trials with scheduled events and return simple metrics."""
    succ, steps, failures = 0, [], 0
    for i in range(trials):
        w = World.random(world_cfg['width'], world_cfg['height'], world_cfg)
        sched = EventScheduler([
            ScheduledEvent(step=w.width//2, kind='toggle_rain'),
            ScheduledEvent(step=3*w.width//4, kind='spawn_obstacles'),
        ])
        path = bfs_plan(w)
        if not path:
            failures += 1
            continue
        actions = path_to_actions(w, path)
        t = 0
        for a in actions:
            sched.maybe_fire(w, t)
            info = w.step(a)
            t += 1
            if info['done'] and info['reason'] == 'reached':
                succ += 1
                steps.append(t)
                break
        else:
            failures += 1
    total = trials
    return {
        "trials": total,
        "success_rate": succ/total if total else 0.0,
        "avg_steps_success": (sum(steps)/len(steps)) if steps else None,
        "failures": failures
    }
