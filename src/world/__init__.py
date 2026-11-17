"""The world map: built in code from rectangles so every gap and ledge has a known, tested size.

Every place has its own folder (by biome and area) with the code that builds it and an
`abilities.json` listing what Shadowra can learn there:

    scave/        Das Nest, Flusstal                         (dark start caves, hatchling/juvenile)
    sunnyforest/  Sonnenwiesen, Tal der Schattensteine       (daylight)
    lowrow/       Aufwindschlucht, Klippe der Stürme, Ruinen des Lichts, Gleißende Hochebene
    elfvillage/   Elfenhain + Elfendorf                      (optional, below the cliff and the ruins)
    lavacave/     Lavameer, Mafors Gipfel                    (adult flight, the boss, Fira)
    snowylands/   Schneelande: Schneefelder, icecave/ (Eishöhle), snowyvillage/ (Menschendorf)
                  – the story after Fira, reached through the Frostpass at the Letzte Rast
    underwater/   Unter dem Frostsee (deep water, needs Tauchen)

Tile legend
  '#' rock            'C' cracked wall (Obsidian-Klauen)    'V' thorn vines (Finsternis-Flamme)
  ' ' air             '~' water                              'L' lava (deadly)
  'x' abyss spikes    '^' thorns (hurt)                      'U' updraft (air)
  '*' sunbeam (air, light that comes and goes with the clouds)
  'T' leaf canopy (air you can pass, but it casts shade in daylight)
  'G' Schattentor (opens when the three shadow stones wake)
  'I' ice wall (solid – the Finsternis-Flamme melts it)
  'F' frozen lake ice (solid floor)
  'w' deep, ice-cold water (only with Tauchen she can dive into it; breath runs out)

Layout (west -> east):
  Nest | Flusstal | SONNENWIESEN (day) | TAL DER SCHATTENSTEINE (day) | Aufwindschlucht | Klippe
       | Ruinen (+ Elfenhain below) | GLEISSENDE HOCHEBENE (day) | Lavameer | Mafors Gipfel | SCHNEELANDE

The original areas are written in their original coordinates and shifted with X() to make room for
the daylight sections. X() is also used by the rest of the game for any hard-coded tile position.
"""
from ..settings import TILE

MEADOW_W = 80                     # Sonnenwiesen, inserted after the river
VALE_W = 120                      # Tal der Schattensteine, right after the meadow
PLATEAU_W = 70                    # Gleißende Hochebene, inserted after the ruins
SNOW_W = 180                      # Schneelande, east of Mafors Gipfel
W, H = 350 + MEADOW_W + VALE_W + PLATEAU_W + SNOW_W, 50
SOLID = frozenset("#CVGIF")       # G = Schattentor, I = ice wall, F = frozen lake ice
WATER = frozenset("~w")           # w = deep ice water (Tauchen)
SUN_AIR = frozenset(" U")         # what sunlight passes through (canopy 'T', water and rock block it)


def X(x):
    """Original tile x -> tile x in the enlarged world."""
    return x + ((MEADOW_W + VALE_W) if x >= 119 else 0) + (PLATEAU_W if x >= 226 else 0)


MEADOW = (119, 119 + MEADOW_W - 1)
VALE = (MEADOW[1] + 1, MEADOW[1] + VALE_W)
PLATEAU = (X(225) + 1, X(226) - 1)
SNOW = (X(350), X(350) + SNOW_W - 1)          # the snowlands start right behind the summit
SNOW_GROUND = 30                               # snowfield ground row
# daylight sections: sunlight falls on every cell that can see the sky (the snowlands are overcast)
DAY_ZONES = [
    dict(key="meadow", x0=MEADOW[0], x1=MEADOW[1], clouds=True),
    dict(key="vale", x0=VALE[0], x1=VALE[1], clouds=True),
    dict(key="plateau", x0=PLATEAU[0], x1=PLATEAU[1], clouds=False),
]
SHADOW_STONES = ("stone_cave", "stone_lake", "stone_mesa")
CLOUDS = dict(count=3, width=7, speed=38.0)       # cloud shadows drifting over the meadow (tiles, px/s)
GROVE = (X(151), X(224))

# Growth gates used in the regions (tile heights):  hatchling jumps ~2.4, juvenile ~4.5, adult ~5.


class Builder:
    """The grid and objects the regions write into."""

    def __init__(self):
        self.g = [["#"] * W for _ in range(H)]
        self.objects = []

    def carve_at(self, x0, y0, x1, y1, ch=" "):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.g[y][x] = ch

    def obj_at(self, kind, x, y, oid=None, **kw):
        d = dict(kind=kind, x=x, y=y, id=oid or f"{kind}_{x}_{y}")
        d.update(kw)
        self.objects.append(d)

    # the original areas: written in original coordinates, shifted by X()
    def carve(self, x0, y0, x1, y1, ch=" "):
        self.carve_at(X(x0), y0, X(x1), y1, ch)

    def obj(self, kind, x, y, oid=None, **kw):
        self.obj_at(kind, X(x), y, oid, **kw)


def build():
    from . import scave, sunnyforest, lowrow, elfvillage, lavacave, snowylands, underwater
    b = Builder()
    for region in (scave, lowrow, elfvillage, lavacave, sunnyforest, snowylands, underwater):
        region.build(b)
    g = b.g
    for x in range(W):                  # map border
        g[H - 1][x] = "#"
    for y in range(H):
        g[y][0] = "#"
        g[y][W - 1] = "#"
    return g, b.objects


class Level:
    def __init__(self, broken=(), burned=()):
        self.grid, self.objects = build()
        self.w, self.h = W, H
        self.pw, self.ph = W * TILE, H * TILE
        self._find_beams()
        for (x, y) in broken:
            if self.grid[y][x] == "C":
                self.grid[y][x] = " "
        for (x, y) in burned:
            if self.grid[y][x] in "VI":       # burned vines and melted ice walls
                self.grid[y][x] = " "
        self._compute_lava_light()
        self._compute_sun()
        self.version = 0          # bumped whenever tiles change (renderer cache key)
        self.X = X

    # ---- daylight -----------------------------------------------------------
    def _compute_sun(self):
        """For every daylight column: the lowest row that still sees the open sky."""
        self.sun_bottom = {}
        for z in DAY_ZONES:
            for x in range(z["x0"], z["x1"] + 1):
                y = 0
                while y < H and self.grid[y][x] in SUN_AIR:
                    y += 1
                self.sun_bottom[x] = y - 1

    @staticmethod
    def day_zone(px):
        tx = px // TILE
        for z in DAY_ZONES:
            if z["x0"] <= tx <= z["x1"]:
                return z
        return None

    def cloud_centers(self, z, t):
        """x positions (px) of the cloud shadows drifting over a daylight zone."""
        if not z["clouds"]:
            return []
        margin = 10 * TILE
        span = (z["x1"] - z["x0"] + 1) * TILE + 2 * margin
        n = CLOUDS["count"]
        return [z["x0"] * TILE - margin + ((t * CLOUDS["speed"] + k * span / n) % span) for k in range(n)]

    def in_cloud_shadow(self, px, t):
        z = self.day_zone(px)
        if not z:
            return False
        half = CLOUDS["width"] * TILE / 2
        return any(abs(px - c) < half for c in self.cloud_centers(z, t))

    def sunlit(self, px, py, t):
        """Is this point in direct daylight (open sky above, no canopy, no cloud shadow)?"""
        tx, ty = int(px // TILE), int(py // TILE)
        bottom = self.sun_bottom.get(tx)
        if bottom is None or ty > bottom:
            return False
        return not self.in_cloud_shadow(px, t)

    # ---- tile queries -----------------------------------------------------
    def tile(self, tx, ty):
        if tx < 0 or tx >= self.w or ty >= self.h:
            return "#"
        if ty < 0:
            return " "
        return self.grid[ty][tx]

    def solid(self, tx, ty):
        if ty < 0:
            return True                 # the sky has a ceiling: nobody flies over walls like the Schattentor
        return self.tile(tx, ty) in SOLID

    def tile_at(self, px, py):
        return self.tile(int(px // TILE), int(py // TILE))

    def rect_has(self, x, y, w, h, chars):
        for ty in range(int(y // TILE), int((y + h - 0.01) // TILE) + 1):
            for tx in range(int(x // TILE), int((x + w - 0.01) // TILE) + 1):
                if self.tile(tx, ty) in chars:
                    return True
        return False

    def rect_solid(self, x, y, w, h):
        return self.rect_has(x, y, w, h, SOLID)

    # ---- movement ---------------------------------------------------------
    def move_x(self, x, y, w, h, dx):
        nx = x + dx
        y0, y1 = int(y // TILE), int((y + h - 0.01) // TILE)
        if dx > 0:
            tx = int((nx + w - 0.01) // TILE)
            if any(self.solid(tx, ty) for ty in range(y0, y1 + 1)):
                return tx * TILE - w, True
        elif dx < 0:
            tx = int(nx // TILE)
            if any(self.solid(tx, ty) for ty in range(y0, y1 + 1)):
                return (tx + 1) * TILE, True
        return nx, False

    def move_y(self, x, y, w, h, dy):
        ny = y + dy
        x0, x1 = int(x // TILE), int((x + w - 0.01) // TILE)
        if dy > 0:
            ty = int((ny + h - 0.01) // TILE)
            if any(self.solid(tx, ty) for tx in range(x0, x1 + 1)):
                return ty * TILE - h, True
        elif dy < 0:
            ty = int(ny // TILE)
            if any(self.solid(tx, ty) for tx in range(x0, x1 + 1)):
                return (ty + 1) * TILE, True
        return ny, False

    # ---- light ------------------------------------------------------------
    def _find_beams(self):
        """Group sunbeam columns; each beam fades in and out as clouds pass."""
        self.beams = []
        seen = set()
        for x in range(W):
            for y in range(H):
                if self.grid[y][x] == "*" and x not in seen:
                    xs = [x]
                    while x + len(xs) < W and any(self.grid[yy][x + len(xs)] == "*" for yy in range(H)):
                        xs.append(x + len(xs))
                    seen.update(xs)
                    ys = [yy for yy in range(H) if self.grid[yy][x] == "*"]
                    i = len(self.beams)
                    self.beams.append(dict(x0=xs[0], x1=xs[-1], y0=0, y1=max(ys),
                                           period=5.0 + i * 0.7, on=2.8, phase=i * 1.9))
                    for xx in xs:
                        for yy in ys:
                            self.grid[yy][xx] = " "
        self.beam_cells = {}

    def beam_strength(self, b, t):
        """0..1 – how bright a sunbeam is right now (soft fade so players can read the timing)."""
        c = (t + b["phase"]) % b["period"]
        if c >= b["on"]:
            return 0.0
        return max(0.0, min(1.0, c / 0.4, (b["on"] - c) / 0.4))

    def sun_at(self, px, py, t):
        tx, ty = int(px // TILE), int(py // TILE)
        for b in self.beams:
            if b["x0"] <= tx <= b["x1"] and ty <= b["y1"]:
                if self.beam_strength(b, t) > 0.5:
                    return True
        return False

    def _compute_lava_light(self):
        self.lava_light = set()
        self.lava_cols = {}          # x -> (top row, bottom row) of the lit air column, for fast drawing
        for x in range(W):
            top_lava = None
            for y in range(H):
                if self.grid[y][x] == "L":
                    top_lava = y
                    break
            if top_lava is None:
                continue
            y = top_lava - 1
            while y >= 0 and self.grid[y][x] not in SOLID:
                self.lava_light.add((x, y))
                y -= 1
            if y + 1 <= top_lava - 1:
                self.lava_cols[x] = (y + 1, top_lava - 1)

    def lava_light_at(self, px, py):
        return (int(px // TILE), int(py // TILE)) in self.lava_light

    # ---- world changes ----------------------------------------------------
    def _flood_remove(self, tx, ty, ch):
        removed = []
        stack = [(tx, ty)]
        while stack:
            x, y = stack.pop()
            if self.tile(x, y) != ch or not (0 <= x < W and 0 <= y < H):
                continue
            self.grid[y][x] = " "
            removed.append((x, y))
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        if removed:
            self.version += 1
            self._compute_lava_light()
            self._compute_sun()
        return removed

    def break_wall(self, tx, ty):
        return self._flood_remove(tx, ty, "C")

    def open_vale_gate(self):
        """The three Schattensteine are awake: the Schattentor sinks into the ground."""
        for y in range(H):
            for x in range(VALE[0], VALE[1] + 1):
                if self.grid[y][x] == "G":
                    return self._flood_remove(x, y, "G")
        return []

    def burn_vines(self, tx, ty):
        return self._flood_remove(tx, ty, "V")

    def melt_ice(self, tx, ty):
        """The Finsternis-Flamme melts an ice wall (Eishöhle)."""
        return self._flood_remove(tx, ty, "I")

    @staticmethod
    def in_grove(px, py):
        return GROVE[0] <= px // TILE <= GROVE[1] and py // TILE >= 24

    @staticmethod
    def in_snow(px):
        return SNOW[0] <= px // TILE <= SNOW[1]

    def zone_key(self, px, py=0):
        if self.in_grove(px, py):
            return "grove"
        tx, ty = px // TILE, py // TILE
        if self.in_snow(px):
            from . import snowylands, underwater
            return underwater.zone_at(tx, ty) or snowylands.zone_at(tx, ty)
        from . import lavacave
        under = lavacave.zone_at(tx, ty)
        if under:
            return under
        for x0, x1, key in ZONES:
            if x0 <= tx <= x1:
                return key
        return ""

    def zone_name(self, px, py=0):
        from ..texts import ZONE_NAMES
        return ZONE_NAMES.get(self.zone_key(px, py), "")

    def is_cave(self, px, py=0):
        return self.zone_key(px, py) in ("nest", "ruins", "lava", "grove", "frostpass", "icecave", "underwater")

    COLD_ZONES = frozenset(("frostpass", "snowfield", "icecave", "snowvillage", "frozenlake", "underwater",
                            "northcliff"))

    def is_cold(self, px, py):
        """Ice-cold places: the Frostpass and the snowlands (a hearth's warmth is checked by the game)."""
        return self.zone_key(px, py) in self.COLD_ZONES


# zone table in world coordinates (the grove overlays the cliff/ruins columns below row 24;
# the snowlands decide their sub-zones in snowylands.zone_at / underwater.zone_at)
ZONES = [
    (0, 62, "nest"), (63, 118, "river"), (MEADOW[0], MEADOW[1], "meadow"), (VALE[0], VALE[1], "vale"),
    (X(119), X(150), "canyon"), (X(151), X(166), "cliff"), (X(167), X(225), "ruins"),
    (PLATEAU[0], PLATEAU[1], "plateau"), (X(226), X(299), "lava"), (X(300), X(349), "summit"),
]
LAVA = (X(226), X(300))
