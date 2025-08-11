
from typing import Dict
import re

def parse_prompt_to_config(prompt: str) -> Dict:
    p = prompt.lower()
    cfg = {
        "width": 24,
        "height": 16,
        "river": any(k in p for k in ["river","stream","water"]),
        "rocks": any(k in p for k in ["rock","boulder","mountain"]),
        "lava": "lava" in p,
        "sand": "sand" in p or "desert" in p,
        "rain": any(k in p for k in ["rain","rainy","storm","wet","weather"]),
        "start_side": "west" if "start west" in p or "west" in p else ("east" if "east" in p else "west"),
        "goal_side": "east" if "goal east" in p or "east" in p else ("west" if "west" in p else "east"),
        "obstacle_density": 0.08 if "sparse" in p else (0.20 if "dense" in p else 0.12),
        "enemy": any(k in p for k in ["enemy","monster","agent"]),
    }
    # simple numbers like "width 30", "height 20"
    m = re.search(r"width\s+(\d+)", p)
    if m: cfg["width"] = max(8, min(64, int(m.group(1))))
    m = re.search(r"height\s+(\d+)", p)
    if m: cfg["height"] = max(8, min(64, int(m.group(1))))
    return cfg
