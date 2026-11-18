"""Drawing: Shadowra (procedural, after the logo art), tiles, backgrounds, lights."""
import math
import random

import pygame

from .settings import (TILE, SCREEN_W, SCREEN_H, ROCK, ROCK_DARK, ROCK_EDGE, ROCK_EDGE2,
                       CAVE_BG, LIGHT_COL, LAVA_COL)

# Creature models live in models.py (supersampled, smooth). Re-exported here for existing callers.
from . import tilegen, lights
from .models import (draw_dragon, draw_elf, draw_moss_runner, draw_fish, draw_owl,  # noqa: F401
                     draw_monster, draw_mafor, ground_shadow)


# ---------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------
class TileArt:
    """All map tiles, generated in high resolution by tilegen.py (smooth, rounded, several variants)."""

    def __init__(self, sprites):
        self.sprites = sprites
        self.rock = tilegen.ground_set(tilegen.ROCK_PAL, 7)
        self.grass = tilegen.ground_set(tilegen.GRASS_PAL, 11, grass=True)   # daylight sections
        self.leaves = tilegen.leaves_tile()
        self.cracked = tilegen.cracked_tile()
        self.vines = tilegen.vines_tile()
        self.gate = tilegen.gate_tile()
        self.spikes = tilegen.spike_tile()
        self.water_top, self.water_body = tilegen.water_frames()
        self.lava_top, self.lava_body = tilegen.lava_frames()
        self.snow = tilegen.ground_set(tilegen.SNOW_PAL, 13, snow=True)       # the snowlands
        self.ice = tilegen.ice_tile()
        self.lake_ice = tilegen.lake_ice_tile()
        self.deep_top, self.deep_body = tilegen.deep_water_frames()

    def draw(self, screen, level, cam, t):
        x0, y0 = int(cam[0] // TILE), int(cam[1] // TILE)
        x1, y1 = x0 + SCREEN_W // TILE + 2, y0 + SCREEN_H // TILE + 2
        wf = int(t * 8)
        from .world import SNOW
        snow_x = SNOW[0]
        for ty in range(max(0, y0), min(level.h, y1)):
            row = level.grid[ty]
            for tx in range(max(0, x0), min(level.w, x1)):
                ch = row[tx]
                if ch == " " or ch == "U":
                    continue
                X, Y = tx * TILE - cam[0], ty * TILE - cam[1]
                if ch == "#":
                    m = 0
                    if not level.solid(tx, ty - 1) and ty > 0:
                        m |= 1
                    if not level.solid(tx + 1, ty):
                        m |= 2
                    if not level.solid(tx, ty + 1):
                        m |= 4
                    if not level.solid(tx - 1, ty):
                        m |= 8
                    tiles = (self.grass if tx in level.sun_bottom else
                             self.snow if tx >= snow_x else self.rock)
                    screen.blit(tiles[m][(tx * 7349 + ty * 1931) % tilegen.VARIANTS], (X, Y))
                elif ch == "I":
                    screen.blit(self.ice, (X, Y))
                elif ch == "F":
                    screen.blit(self.lake_ice, (X, Y))
                elif ch == "w":
                    if level.tile(tx, ty - 1) not in "w~F#":
                        screen.blit(self.deep_top[(wf + tx) % len(self.deep_top)], (X, Y))
                    else:
                        screen.blit(self.deep_body, (X, Y))
                elif ch == "T":
                    screen.blit(self.leaves, (X, Y))
                elif ch == "C":
                    screen.blit(self.cracked, (X, Y))
                elif ch == "V":
                    screen.blit(self.vines, (X, Y))
                elif ch == "G":
                    screen.blit(self.gate, (X, Y))
                elif ch == "~":
                    if level.tile(tx, ty - 1) != "~":
                        screen.blit(self.water_top[(wf + tx) % len(self.water_top)], (X, Y))
                    else:
                        screen.blit(self.water_body, (X, Y))
                elif ch in "x^":
                    screen.blit(self.spikes, (X, Y))
                elif ch == "L":
                    frames = self.lava_top if level.tile(tx, ty - 1) != "L" else self.lava_body
                    screen.blit(frames[(wf // 2 + tx) % len(frames)], (X, Y))


# ---------------------------------------------------------------------------
# Background & lights
# ---------------------------------------------------------------------------
class Backdrop:
    def __init__(self, sprites):
        # the starry-night pack is bright; darken it towards the game's dusk palette
        self.sky = pygame.transform.scale(sprites.sky, (SCREEN_W, SCREEN_H))
        self.sky.fill((120, 100, 140), special_flags=pygame.BLEND_RGB_MULT)
        self.clouds = pygame.transform.scale(sprites.clouds, (SCREEN_W, SCREEN_H))
        self.clouds.fill((90, 70, 130), special_flags=pygame.BLEND_RGBA_MULT)
        m1 = pygame.transform.scale(sprites.mountains1, (1024, 512))
        m2 = pygame.transform.scale(sprites.mountains2, (1024, 512))
        self.m1 = m1.copy()
        self.m1.fill((40, 22, 50), special_flags=pygame.BLEND_RGB_MULT)
        self.m2 = m2.copy()
        self.m2.fill((70, 40, 80), special_flags=pygame.BLEND_RGB_MULT)
        self.cave = pygame.Surface((SCREEN_W, SCREEN_H))
        self.cave.fill(CAVE_BG)
        rng = random.Random(3)
        for _ in range(260):
            x, y = rng.randrange(SCREEN_W), rng.randrange(SCREEN_H)
            pygame.draw.circle(self.cave, (32, 20, 42), (x, y), rng.randint(4, 22))
        self.cave_fade = self.cave.copy()
        self.grove_fog = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for i in range(SCREEN_H // 8):
            k = i * 8 / SCREEN_H
            pygame.draw.rect(self.grove_fog, (40, 120, 120, int(20 + 40 * k)), (0, i * 8, SCREEN_W, 8))
        self.lava_glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for i in range(SCREEN_H // 8):
            k = i * 8 / SCREEN_H                           # 0 at top, 1 at bottom
            pygame.draw.rect(self.lava_glow, (255, 90, 30, int(10 + 70 * k * k)), (0, i * 8, SCREEN_W, 8))
        # Pre-blended opaque backgrounds: once fully inside the lava cave / the grove, a single
        # opaque blit replaces cave + full-screen alpha overlay (much cheaper per frame).
        self.cave_lava = self.cave.copy()
        self.cave_lava.blit(self.lava_glow, (0, 0))
        self.cave_grove = self.cave.copy()
        self.cave_grove.blit(self.grove_fog, (0, 0))
        self.pre_blended = None
        # daytime sky for the daylight sections: the Grassland background layers stacked into one image
        self.day = pygame.Surface((SCREEN_W, SCREEN_H))
        self.day.fill((96, 170, 236))
        for layer in sprites.day_layers:
            k = SCREEN_H / layer.get_height()
            img = pygame.transform.scale(layer, (int(layer.get_width() * k), SCREEN_H))
            for xx in range(0, SCREEN_W, img.get_width()):
                self.day.blit(img, (xx, 0))
        self.day.fill((255, 238, 214), special_flags=pygame.BLEND_RGB_MULT)    # a warm, harsh sun
        self.day_fade = self.day.copy()
        # snowlands: an overcast, grey-blue sky with pale mountains (no sun burns here)
        self.snow_sky = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(0, SCREEN_H, 4):
            k = y / SCREEN_H
            pygame.draw.rect(self.snow_sky, (int(122 + 40 * k), int(134 + 38 * k), int(160 + 30 * k)), (0, y, SCREEN_W, 4))
        # pale, snowy mountain silhouettes (the mountain shapes, filled with a hazy blue-white)
        self.snow_m1 = pygame.mask.from_surface(m1, 40).to_surface(setcolor=(150, 160, 188, 255),
                                                                   unsetcolor=(0, 0, 0, 0))
        self.snow_m2 = pygame.mask.from_surface(m2, 40).to_surface(setcolor=(184, 194, 218, 255),
                                                                   unsetcolor=(0, 0, 0, 0))
        self.snow_fade = pygame.Surface((SCREEN_W, SCREEN_H))

    def draw_snow(self, screen, cam, mix, t):
        """The snowlands' overcast sky (blended in with mix)."""
        target = screen if mix > 0.99 else self.snow_fade
        target.blit(self.snow_sky, (0, 0))
        for layer, f, yoff in ((self.snow_m2, 0.12, 60), (self.snow_m1, 0.25, 130)):
            w = layer.get_width()
            o = int(-cam[0] * f) % w
            y = yoff - int((cam[1] - 500) * f * 0.5)
            for xx in (o - w, o, o + w):
                target.blit(layer, (xx, y))
        if mix <= 0.99:
            self.snow_fade.set_alpha(int(255 * mix))
            screen.blit(self.snow_fade, (0, 0))

    @staticmethod
    def draw_snowfall(screen, cam, t, mix):
        """Snowflakes drifting down in front of the world (outside in the snowlands)."""
        if mix < 0.05:
            return
        n = int(90 * mix)
        for i in range(n):
            sp = 30 + (i % 7) * 9
            x = (i * 97.3 + math.sin(t * 0.8 + i) * 30 - cam[0] * (0.6 + (i % 3) * 0.2)) % SCREEN_W
            y = (i * 53.1 + t * sp - cam[1] * 0.5) % SCREEN_H
            r = 1 + (i % 3 == 0) + (i % 11 == 0)
            pygame.draw.circle(screen, (236, 242, 255), (int(x), int(y)), r)

    def draw_day(self, screen, cam, mix):
        sky = self.day
        if mix < 0.99:
            sky = self.day_fade
            sky.set_alpha(int(255 * mix))
        ox = int(-cam[0] * 0.08) % SCREEN_W
        screen.blit(sky, (ox - SCREEN_W, 0))
        screen.blit(sky, (ox, 0))

    def draw_grove(self, screen, cam, mix, t):
        """Elfenhain: teal moonlit fog and drifting spores over the cave background."""
        if self.pre_blended != "grove":
            self.grove_fog.set_alpha(int(255 * mix))
            screen.blit(self.grove_fog, (0, 0))
        for i in range(24):
            x = (i * 137 + t * (8 + i % 5) - cam[0] * 0.3) % SCREEN_W
            y = (i * 71 + math.sin(t * 0.7 + i) * 20 - cam[1] * 0.3) % SCREEN_H
            c = (120, 230, 210) if i % 3 else (200, 170, 255)
            pygame.draw.circle(screen, c, (int(x), int(y)), 2 if i % 4 else 1)

    def draw(self, screen, cam, cave_mix, lava_mix, t, grove_mix=0.0, day_mix=0.0, snow_mix=0.0):
        self.pre_blended = None
        if snow_mix > 0.01 and cave_mix < 0.99:          # outside in the snowlands
            if snow_mix < 0.99:
                self.draw(screen, cam, cave_mix, lava_mix, t, grove_mix, day_mix, 0.0)
            self.draw_snow(screen, cam, snow_mix * (1 - cave_mix), t)
            if cave_mix > 0.01:
                cave = self.cave_fade
                cave.set_alpha(int(255 * cave_mix))
                ox = int(-cam[0] * 0.2) % SCREEN_W
                screen.blit(cave, (ox - SCREEN_W, 0))
                screen.blit(cave, (ox, 0))
            return
        if day_mix > 0.99:
            self.draw_day(screen, cam, 1.0)
            return
        if day_mix > 0.01:                       # crossing into / out of daylight: blend over the night
            self.draw(screen, cam, cave_mix, lava_mix, t, grove_mix, 0.0)
            self.draw_day(screen, cam, day_mix)
            return
        if cave_mix > 0.99 and (lava_mix > 0.99 or grove_mix > 0.99):
            self.pre_blended = "lava" if lava_mix > 0.99 else "grove"
            base = self.cave_lava if self.pre_blended == "lava" else self.cave_grove
            ox = int(-cam[0] * 0.2) % SCREEN_W
            screen.blit(base, (ox - SCREEN_W, 0))
            screen.blit(base, (ox, 0))
            return
        if cave_mix < 0.99:
            screen.blit(self.sky, (0, 0))
            off = int(-cam[0] * 0.05 + t * 6) % SCREEN_W
            screen.blit(self.clouds, (off - SCREEN_W, 0))
            screen.blit(self.clouds, (off, 0))
            for layer, f, yoff in ((self.m2, 0.12, 40), (self.m1, 0.25, 110)):
                w = layer.get_width()
                o = int(-cam[0] * f) % w
                y = yoff - int((cam[1] - 700) * f * 0.5)
                for xx in (o - w, o, o + w):
                    screen.blit(layer, (xx, y))
        if cave_mix > 0:
            cave = self.cave
            if cave_mix < 0.99:
                cave = self.cave_fade
                cave.set_alpha(int(255 * cave_mix))
            ox = int(-cam[0] * 0.2) % SCREEN_W
            screen.blit(cave, (ox - SCREEN_W, 0))
            screen.blit(cave, (ox, 0))
        if lava_mix > 0.01:
            self.lava_glow.set_alpha(int(255 * lava_mix))
            screen.blit(self.lava_glow, (0, 0))


def draw_beams(screen, level, cam, t):
    for b in level.beams:
        st = level.beam_strength(b, t)
        x = b["x0"] * TILE - cam[0]
        w = (b["x1"] - b["x0"] + 1) * TILE
        if x > SCREEN_W or x + w < 0:
            continue
        bottom = (b["y1"] + 1) * TILE - cam[1]       # screen y where the beam hits the floor
        top = max(0, -cam[1])
        if bottom <= 0:
            continue
        h = int(min(bottom, SCREEN_H) - top)
        if h <= 0:
            continue
        surf = pygame.Surface((w + 24, h), pygame.SRCALPHA)
        base = int(30 + 110 * st)
        surf.fill((*LIGHT_COL, base))
        pygame.draw.rect(surf, (*LIGHT_COL, int(base * 0.4)), (0, 0, 12, h))
        pygame.draw.rect(surf, (*LIGHT_COL, int(base * 0.4)), (w + 12, 0, 12, h))
        if st < 0.1:
            surf.fill((*LIGHT_COL, 14))     # faint hint of where the beam returns
        screen.blit(surf, (x - 12, top))
        h = bottom
        if st > 0.5:
            for i in range(3):
                px = x + random.random() * w
                py = h - random.random() * 40
                pygame.draw.circle(screen, (255, 250, 200), (int(px), int(py)), 1)


def draw_lava_glow(screen, level, cam, t):
    """One blit per lit column from a pre-made strip (was one blit per tile)."""
    global _lava_strip
    if _lava_strip is None:
        _lava_strip = pygame.Surface((TILE, SCREEN_H + TILE))
        _lava_strip.fill((255, 150, 60))
    _lava_strip.set_alpha(int(40 + 10 * math.sin(t * 3)))      # surface alpha: cheap to blit
    x0, x1 = int(cam[0] // TILE), int((cam[0] + SCREEN_W) // TILE) + 1
    for x in range(x0, x1 + 1):
        run = level.lava_cols.get(x)
        if not run:
            continue
        top = max(0, run[0] * TILE - cam[1])
        bottom = min(SCREEN_H, (run[1] + 1) * TILE - cam[1])
        if bottom > top:
            screen.blit(_lava_strip, (x * TILE - cam[0], top), (0, 0, TILE, bottom - top))


_lava_strip = None
_sun_strip = None
_shade_strip = None


def draw_daylight(screen, level, cam, t, sprites):
    """Daylight sections: warm sunlight on every cell that sees the sky, darker cloud shadows
    drifting over the meadow, and the clouds themselves. Mirrors Level.sunlit exactly."""
    global _sun_strip, _shade_strip
    if _sun_strip is None:
        _sun_strip = pygame.Surface((TILE, SCREEN_H + TILE))
        _sun_strip.fill((255, 236, 170))
        _sun_strip.set_alpha(42)
        _shade_strip = pygame.Surface((TILE, SCREEN_H + TILE))
        _shade_strip.fill((20, 30, 60))
        _shade_strip.set_alpha(90)
    x0, x1 = int(cam[0] // TILE), int((cam[0] + SCREEN_W) // TILE) + 1
    top = max(0, -cam[1])
    zones_seen = {}
    for tx in range(x0, x1 + 1):
        bottom_row = level.sun_bottom.get(tx)
        if bottom_row is None:
            continue
        bottom = min(SCREEN_H, (bottom_row + 1) * TILE - cam[1])
        if bottom <= top:
            continue
        shaded = level.in_cloud_shadow(tx * TILE + TILE / 2, t)
        strip = _shade_strip if shaded else _sun_strip
        screen.blit(strip, (tx * TILE - cam[0], top), (0, 0, TILE, bottom - top))
        z = level.day_zone(tx * TILE)
        zones_seen[z["key"]] = z
    for z in zones_seen.values():                     # the clouds that cast the shadows
        for i, cx in enumerate(level.cloud_centers(z, t)):
            img = sprites.day_clouds[i % len(sprites.day_clouds)]
            screen.blit(img, (cx - cam[0] - img.get_width() / 2, 40 + (i % 2) * 30))


_glow_cache = {}


def draw_light_circle(screen, x, y, r, col=LIGHT_COL, alpha=70, shine=True):
    """A soft glow. shine=False: it lights nothing else (e.g. Shadowra's own faint aura)."""
    if shine:
        lights.add(x, y, r, col, alpha / 70)
    key = (r, col, alpha)
    surf = _glow_cache.get(key)
    if surf is None:
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            pygame.draw.circle(surf, (*col, int(alpha * (7 - i) / 6)), (r, r), int(r * i / 6))
        if len(_glow_cache) > 400:
            _glow_cache.clear()
        _glow_cache[key] = surf
    screen.blit(surf, (x - r, y - r))
