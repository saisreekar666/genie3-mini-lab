
from typing import List, Tuple, Optional
from collections import deque
import math

def bfs_plan(world) -> Optional[List[Tuple[int,int]]]:
    start = world.player
    goal = world.goal
    W, H = world.width, world.height
    q = deque([start])
    prev = {start: None}
    while q:
        x,y = q.popleft()
        if (x,y) == goal:
            break
        for nx,ny in world.neighbors(x,y):
            if (nx,ny) not in prev:
                prev[(nx,ny)] = (x,y)
                q.append((nx,ny))
    if goal not in prev:
        return None
    # reconstruct
    path = []
    cur = goal
    while cur:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

def path_to_actions(world, path: List[Tuple[int,int]]) -> List[str]:
    if not path or len(path) < 2:
        return []
    actions = []
    px, py = path[0]
    for x,y in path[1:]:
        dx, dy = x-px, y-py
        if dx == 1: actions.append("right")
        elif dx == -1: actions.append("left")
        elif dy == 1: actions.append("down")
        elif dy == -1: actions.append("up")
        px, py = x, y
    return actions
