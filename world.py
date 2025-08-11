
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
import random
from PIL import Image, ImageDraw

class TileType(str, Enum):
    GRASS = "G"
    WATER = "W"
    ROCK  = "R"
    SAND  = "S"
    LAVA  = "L"

TILE_COLORS = {
    TileType.GRASS: (90, 170, 90),
    TileType.WATER: (70, 120, 200),
    TileType.ROCK:  (120, 120, 120),
    TileType.SAND:  (210, 190, 120),
    TileType.LAVA:  (220, 70, 40),
}

BASE_COST = {
    TileType.GRASS: 1.0,
    TileType.SAND:  1.4,
    TileType.WATER: 3.0,  # high friction when 'rain' true, else 2.0
    TileType.ROCK:  float('inf'),  # impassable
    TileType.LAVA:  float('inf'),  # lethal
}

@dataclass
class World:
    width: int
    height: int
    tiles: List[List[TileType]]
    start: Tuple[int,int]
    goal: Tuple[int,int]
    player: Tuple[int,int]
    enemies: List[Tuple[int,int]] = field(default_factory=list)
    raining: bool = False

    @classmethod
    def random(cls, width: int, height: int, cfg: Dict) -> 'World':
        rng = random.Random(42)
        tiles = [[TileType.GRASS for _ in range(width)] for _ in range(height)]

        # Add river (vertical meander)
        if cfg.get("river"):
            x = rng.randint(width//3, 2*width//3)
            for y in range(height):
                tiles[y][x] = TileType.WATER
                if rng.random() < 0.4 and 0 < x < width-1:
                    x += rng.choice([-1,1])

        # Scatter rocks / sand / lava
        density = cfg.get("obstacle_density", 0.12)
        for y in range(height):
            for x in range(width):
                r = rng.random()
                if r < density and (tiles[y][x] == TileType.GRASS):
                    if cfg.get("rocks") and rng.random() < 0.5:
                        tiles[y][x] = TileType.ROCK
                    elif cfg.get("sand") and rng.random() < 0.5:
                        tiles[y][x] = TileType.SAND
                    elif cfg.get("lava") and rng.random() < 0.2:
                        tiles[y][x] = TileType.LAVA

        # start/goal
        start_side = cfg.get("start_side", "west")
        goal_side  = cfg.get("goal_side", "east")
        sy = height//2
        gy = height//2
        sx = 1 if start_side == "west" else width-2
        gx = width-2 if goal_side == "east" else 1

        # Ensure passable start/goal
        tiles[sy][sx] = TileType.GRASS
        tiles[gy][gx] = TileType.GRASS

        enemies = []
        if cfg.get("enemy"):
            enemies.append((width//2, height//2))

        w = cls(width, height, tiles, (sx,sy), (gx,gy), (sx,sy), enemies, cfg.get("rain", False))
        return w

    @classmethod
    def from_generated(cls, gen: Dict) -> 'World':
        # Accepts structure similar to genie_client.GeneratedWorld
        tiles = [[TileType(cell) for cell in row] for row in gen["tiles"]]
        w = cls(gen["width"], gen["height"], tiles, tuple(gen["start"]), tuple(gen["goal"]), tuple(gen["start"]), gen.get("enemies", []), False)
        return w

    def tile_cost(self, x:int, y:int) -> float:
        t = self.tiles[y][x]
        if t == TileType.WATER:
            return 3.0 if self.raining else 2.0
        return BASE_COST[t]

    def passable(self, x:int, y:int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tile_cost(x,y) < float('inf')

    def lethal(self, x:int, y:int) -> bool:
        return self.tiles[y][x] == TileType.LAVA

    def neighbors(self, x:int, y:int):
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if self.passable(nx, ny):
                yield nx, ny

    def step(self, action: str) -> Dict:
        ax = {"right":1,"left":-1}.get(action,0)
        ay = {"down":1,"up":-1}.get(action,0)
        nx, ny = self.player[0]+ax, self.player[1]+ay
        if self.passable(nx, ny):
            self.player = (nx, ny)
        info = {"done": False, "reason": None}
        if self.lethal(*self.player):
            # reset to start
            self.player = self.start
            info["done"] = False
            info["reason"] = "lethal"
        if self.player == self.goal:
            info["done"] = True
            info["reason"] = "reached"
        return info

    def apply_event(self, kind: str):
        if kind == "toggle_rain":
            self.raining = not self.raining
        elif kind == "spawn_obstacles":
            rng = random.Random(123)
            for _ in range(max(1, (self.width*self.height)//40)):
                x, y = rng.randint(0,self.width-1), rng.randint(0,self.height-1)
                if (x,y) not in [self.player, self.goal] and self.tiles[y][x] == TileType.GRASS:
                    self.tiles[y][x] = TileType.ROCK
        elif kind == "spawn_enemy":
            self.enemies.append((self.width//2, self.height//2))

    def render(self, scale:int=20) -> Image.Image:
        img = Image.new("RGB", (self.width*scale, self.height*scale), (0,0,0))
        drw = ImageDraw.Draw(img)
        # tiles
        for y in range(self.height):
            for x in range(self.width):
                c = TILE_COLORS[self.tiles[y][x]]
                drw.rectangle([x*scale, y*scale, (x+1)*scale-1, (y+1)*scale-1], fill=c)
        # goal
        gx, gy = self.goal
        drw.rectangle([gx*scale+4, gy*scale+4, (gx+1)*scale-5, (gy+1)*scale-5], outline=(250,220,60), width=3)
        # player
        px, py = self.player
        drw.ellipse([px*scale+4, py*scale+4, (px+1)*scale-4, (py+1)*scale-4], fill=(60,120,255))
        # enemies
        for ex,ey in self.enemies:
            drw.ellipse([ex*scale+6, ey*scale+6, (ex+1)*scale-6, (ey+1)*scale-6], outline=(30,30,30), width=2)
        # rain overlay
        if self.raining:
            for y in range(0, self.height*scale, 8):
                for x in range(0, self.width*scale, 16):
                    drw.line([(x, y), (x+2, y+6)], fill=(180,180,255))
        return img
