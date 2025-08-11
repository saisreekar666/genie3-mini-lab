
"""
Genie 3 client interface (placeholder).

If you gain access to Genie 3 or another world model, replace `generate_world`
with a call to that API and adapt the returned structure to `World.from_generated(...)`.
"""
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class GeneratedWorld:
    width: int
    height: int
    tiles: List[List[str]]
    start: Tuple[int, int]
    goal: Tuple[int, int]
    enemies: Optional[list] = None

def generate_world(prompt: str) -> GeneratedWorld:
    """Placeholder: returns None to signal 'not implemented'.
    The app will fall back to its procedural generator.
    """
    return None
