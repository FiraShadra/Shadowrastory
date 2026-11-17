"""High-resolution, smooth map tiles – generated once at start-up.

Every tile is painted at TS = TILE * SS pixels (4x) and smoothly scaled down, so edges are
anti-aliased. Ground tiles know which neighbours are air (mask: up/right/down/left) and get
rounded outer corners, a glowing rim on exposed sides, gradient shading and soft texture.
Several random variants per mask keep large walls from looking repetitive.
"""
import math
import random

import pygame

from .settings import TILE

SS = 4
TS = TILE * SS
UP, RIGHT, DOWN, LEFT = 1, 2, 4, 8
VARIANTS = 3


def _lerp(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _down(surf):
    return pygame.transform.smoothscale(surf, (TILE, TILE))


def _shape_mask(mask, radius):
    """White rounded rectangle: outer corners round off where both touching sides are open air."""
    m = pygame.Surface((TS, TS), pygame.SRCALPHA)
    r = lambda a, b: radius if (mask & a and mask & b) else 0
    pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, TS, TS),
                     border_top_left_radius=r(UP, LEFT), border_top_right_radius=r(UP, RIGHT),
                     border_bottom_left_radius=r(DOWN, LEFT), border_bottom_right_radius=r(DOWN, RIGHT))
    return m


def _clip(surf, mask_surf):
    surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf


def _gradient(top, bottom):
    g = pygame.Surface((TS, TS), pygame.SRCALPHA)
    for y in range(TS):
        pygame.draw.line(g, (*_lerp(top, bottom, y / TS), 255), (0, y), (TS, y))
    return g


def ground_tile(mask, pal, rng, grass=False, snow=False):
    """pal: dict(top, bottom, blob_dark, blob_light, rim, rim_light, crack). snow: a thick white cap."""
    if snow:
        return _snow_tile(mask, pal, rng)
    radius = int(TS * 0.32)
    shape = _shape_mask(mask, radius)
    s = _gradient(pal["top"], pal["bottom"])
    # soft texture: overlapping blobs and pebbles
    for _ in range(26):
        c = pal["blob_dark"] if rng.random() < 0.6 else pal["blob_light"]
        pygame.draw.circle(s, c, (rng.randrange(TS), rng.randrange(TS)), rng.randint(5, 18))
    for _ in range(10):
        x, y = rng.randrange(TS), rng.randrange(TS)
        pygame.draw.ellipse(s, pal["blob_light"], (x, y, rng.randint(6, 14), rng.randint(4, 9)))
        pygame.draw.ellipse(s, pal["blob_dark"], (x + 2, y + 3, rng.randint(6, 12), rng.randint(3, 6)), 2)
    if not grass:                                         # hairline cracks in the rock
        for _ in range(2):
            x, y = rng.randrange(TS), rng.randrange(TS)
            pts = [(x, y)]
            for _ in range(4):
                x += rng.randint(-14, 14)
                y += rng.randint(4, 16)
                pts.append((x, y))
            pygame.draw.aalines(s, pal["crack"], False, pts)
    # Rim along exposed sides: a full rounded ring (with a lighter bevel line), then keep only the
    # bands of the open sides. Each band runs the full tile length so rims join seamlessly.
    rim_w = int(TS * (0.2 if grass else 0.16))
    r = lambda a, b: radius if (mask & a and mask & b) else 0
    corners = dict(border_top_left_radius=r(UP, LEFT), border_top_right_radius=r(UP, RIGHT),
                   border_bottom_left_radius=r(DOWN, LEFT), border_bottom_right_radius=r(DOWN, RIGHT))
    rim = pygame.Surface((TS, TS), pygame.SRCALPHA)
    pygame.draw.rect(rim, (*pal["rim"], 255), (0, 0, TS, TS), rim_w, **corners)
    bev = rim_w // 3
    pygame.draw.rect(rim, (*pal["rim_light"], 255), (bev, bev, TS - 2 * bev, TS - 2 * bev), max(2, bev), **corners)
    keep = pygame.Surface((TS, TS), pygame.SRCALPHA)
    white = (255, 255, 255, 255)
    if mask & UP:
        keep.fill(white, (0, 0, TS, rim_w))
    if mask & DOWN:
        keep.fill(white, (0, TS - rim_w, TS, rim_w))
    if mask & LEFT:
        keep.fill(white, (0, 0, rim_w, TS))
    if mask & RIGHT:
        keep.fill(white, (TS - rim_w, 0, rim_w, TS))
    rim.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(rim, (0, 0))
    if mask & UP:
        if grass:                                             # grass blades along the top
            for _ in range(22):
                x = rng.randrange(TS)
                h = rng.randint(8, 20)
                col = _lerp(pal["rim"], pal["rim_light"], rng.random())
                pygame.draw.line(s, col, (x, rim_w + 2), (x + rng.randint(-5, 5), max(0, rim_w - h)), 3)
            for _ in range(5):                                # dark soil shadow under the turf
                x = rng.randrange(TS)
                pygame.draw.ellipse(s, pal["blob_dark"], (x - 8, rim_w, 16, 7))
        else:                                                 # glowing drips under a rock rim
            for _ in range(4):
                x = rng.randrange(8, TS - 8)
                h = rng.randint(6, 18)
                pygame.draw.line(s, pal["rim"], (x, rim_w), (x, rim_w + h), 4)
                pygame.draw.circle(s, pal["rim"], (x, rim_w + h), 3)
        for _ in range(8):                                    # sparkles on the rim
            x = rng.randrange(TS)
            pygame.draw.circle(s, pal["rim_light"], (x, rng.randint(2, rim_w - 2)), rng.randint(1, 3))
    _clip(s, shape)
    return _down(s)


ROCK_PAL = dict(top=(56, 32, 70), bottom=(38, 20, 50), blob_dark=(32, 17, 42), blob_light=(66, 40, 80),
                rim=(222, 112, 88), rim_light=(255, 184, 120), crack=(22, 10, 30))
GRASS_PAL = dict(top=(118, 82, 56), bottom=(86, 58, 40), blob_dark=(74, 50, 34), blob_light=(132, 96, 66),
                 rim=(70, 158, 64), rim_light=(150, 214, 94), crack=(60, 40, 28))


SNOW_PAL = dict(top=(70, 74, 96), bottom=(46, 48, 70), blob_dark=(40, 42, 62), blob_light=(84, 90, 112),
                rim=(226, 236, 248), rim_light=(255, 255, 255), crack=(30, 32, 48))


def _snow_tile(mask, pal, rng):
    """Cold blue-grey rock; open sides get a soft, lumpy snow cap (top) or frost (sides / below)."""
    radius = int(TS * 0.32)
    shape = _shape_mask(mask, radius)
    s = _gradient(pal["top"], pal["bottom"])
    for _ in range(24):
        c = pal["blob_dark"] if rng.random() < 0.6 else pal["blob_light"]
        pygame.draw.circle(s, c, (rng.randrange(TS), rng.randrange(TS)), rng.randint(5, 18))
    for _ in range(2):
        x, y = rng.randrange(TS), rng.randrange(TS)
        pts = [(x, y)]
        for _ in range(4):
            x += rng.randint(-14, 14)
            y += rng.randint(4, 16)
            pts.append((x, y))
        pygame.draw.aalines(s, pal["crack"], False, pts)
    frost = int(TS * 0.1)
    for side, rect in ((RIGHT, (TS - frost, 0, frost, TS)), (LEFT, (0, 0, frost, TS)),
                       (DOWN, (0, TS - frost, TS, frost))):
        if mask & side:                                        # thin frost on the other open sides
            f = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
            f.fill((200, 220, 245, 150))
            s.blit(f, rect[:2])
    if mask & UP:                                              # the snow cap: lumps that overlap
        cap = int(TS * 0.3)
        pygame.draw.rect(s, pal["rim"], (0, 0, TS, cap))
        for i in range(7):
            x = i * TS / 6 + rng.randint(-6, 6)
            r = rng.randint(10, 16)
            pygame.draw.circle(s, pal["rim"], (int(x), cap - 2), r)
            pygame.draw.circle(s, pal["rim_light"], (int(x) - 3, cap - 7), r // 2)
        for _ in range(10):                                    # glittering crystals
            pygame.draw.circle(s, (190, 220, 255), (rng.randrange(TS), rng.randint(3, cap)), 2)
    _clip(s, shape)
    return _down(s)


def ground_set(pal, seed, grass=False, snow=False):
    """{mask: [variant surfaces]}"""
    out = {}
    for mask in range(16):
        out[mask] = [ground_tile(mask, pal, random.Random(seed * 1000 + mask * 10 + v), grass, snow)
                     for v in range(VARIANTS)]
    return out


def ice_tile(seed=8):
    """An ice wall: clear blue ice with inner cracks and a bright shine (the Finsternis-Flamme melts it)."""
    rng = random.Random(seed)
    s = _gradient((150, 206, 240), (90, 150, 210))
    for _ in range(6):
        x, y = rng.randrange(TS), rng.randrange(TS)
        pygame.draw.circle(s, (170, 222, 250), (x, y), rng.randint(8, 20))
    for _ in range(4):
        x, y = rng.randrange(TS), rng.randrange(TS)
        pts = [(x, y)]
        for _ in range(4):
            x += rng.randint(-20, 20)
            y += rng.randint(-20, 20)
            pts.append((max(0, min(TS, x)), max(0, min(TS, y))))
        pygame.draw.aalines(s, (235, 248, 255), False, pts)
    pygame.draw.line(s, (255, 255, 255), (16, 12), (TS - 30, 26), 5)          # shine
    pygame.draw.rect(s, (200, 236, 255), (0, 0, TS, TS), 4, border_radius=10)
    return _down(s)


def lake_ice_tile(seed=9):
    """The frozen lake: a flat sheet of ice with a snowy edge on top and dark water below."""
    rng = random.Random(seed)
    s = _gradient((176, 214, 238), (70, 110, 160))
    pygame.draw.rect(s, (236, 244, 252), (0, 0, TS, 12))
    for _ in range(3):
        x = rng.randrange(TS)
        pygame.draw.aaline(s, (255, 255, 255), (x, 16), (x + rng.randint(-30, 30), TS - 10))
    for _ in range(6):
        pygame.draw.circle(s, (255, 255, 255), (rng.randrange(TS), rng.randint(2, 10)), 2)
    return _down(s)


def deep_water_frames(n=8):
    """Deep ice water ('w'): darker and bluer than a river, with a crest only at an open surface."""
    body = pygame.transform.smoothscale(_gradient((16, 40, 84), (8, 20, 52)), (TILE, TILE))
    tops = []
    for f in range(n):
        s = _gradient((40, 86, 140), (16, 40, 84))
        ph = f / n * math.tau
        pts = [(x, 12 + math.sin(x / TS * math.tau * 2 + ph) * 4) for x in range(0, TS + 1, 4)]
        pygame.draw.polygon(s, (0, 0, 0, 0), [(0, 0)] + pts + [(TS, 0)])
        pygame.draw.lines(s, (180, 230, 255), False, pts, 5)
        tops.append(_down(s))
    return tops, body


def cracked_tile(seed=3):
    rng = random.Random(seed)
    s = _gradient((74, 56, 70), (52, 38, 50))
    for _ in range(14):
        pygame.draw.circle(s, (64, 46, 60), (rng.randrange(TS), rng.randrange(TS)), rng.randint(6, 16))
    for _ in range(5):                                        # deep cracks with a light edge
        x, y = rng.randrange(TS), rng.randrange(TS)
        pts = [(x, y)]
        for _ in range(5):
            x += rng.randint(-22, 22)
            y += rng.randint(-22, 22)
            pts.append((max(0, min(TS, x)), max(0, min(TS, y))))
        pygame.draw.lines(s, (14, 6, 16), False, pts, 6)
        pygame.draw.aalines(s, (150, 120, 130), False, [(px + 3, py + 2) for px, py in pts])
    pygame.draw.rect(s, (120, 96, 110), (0, 0, TS, TS), 4, border_radius=10)
    return _down(s)


def gate_tile():
    """The Schattentor: black stone with a violet rune."""
    s = _gradient((44, 30, 58), (26, 16, 36))
    pygame.draw.rect(s, (90, 64, 120), (4, 4, TS - 8, TS - 8), 6, border_radius=12)
    c = TS // 2
    pygame.draw.circle(s, (150, 100, 220), (c, c), 26, 5)
    pygame.draw.polygon(s, (190, 140, 255), [(c, c - 18), (c + 12, c + 12), (c - 12, c + 12)], 4)
    pygame.draw.circle(s, (220, 190, 255), (c, c + 2), 5)
    return _down(s)


def vines_tile(seed=4):
    rng = random.Random(seed)
    s = pygame.Surface((TS, TS), pygame.SRCALPHA)
    for i in range(5):
        x0 = rng.randrange(TS)
        pts = [(x0 + math.sin(j * 0.8 + i) * 12, j * TS / 10) for j in range(11)]
        pygame.draw.lines(s, (30, 60, 34), False, pts, 9)
        pygame.draw.lines(s, (58, 104, 54), False, pts, 5)
        for j in range(1, 10, 2):                             # thorns and leaves
            px, py = pts[j]
            d = 1 if j % 4 == 1 else -1
            pygame.draw.polygon(s, (190, 196, 160), [(px, py - 3), (px + d * 14, py - 8), (px, py + 3)])
            pygame.draw.ellipse(s, (76, 140, 66), (px - d * 16 - 6, py - 4, 16, 8))
    return _down(s)


def leaves_tile(seed=5):
    rng = random.Random(seed)
    s = pygame.Surface((TS, TS), pygame.SRCALPHA)
    for i in range(9):                                        # dense, dark foliage underneath
        cx, cy = (i % 3) * TS / 2.4 + 18, (i // 3) * TS / 2.4 + 18
        pygame.draw.circle(s, (30, 80, 38), (int(cx + rng.randint(-6, 6)), int(cy + rng.randint(-6, 6))), 34)
    greens = ((40, 98, 46), (52, 120, 54), (70, 146, 62), (96, 172, 74))
    for i in range(34):
        c = greens[min(3, i * 4 // 34)]                       # dark leaves at the back, light in front
        x, y = rng.randrange(-8, TS + 8), rng.randrange(-8, TS + 8)
        w, h = rng.randint(18, 34), rng.randint(10, 18)
        leaf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf, c, (0, 0, w, h))
        pygame.draw.line(leaf, _lerp(c, (20, 50, 20), 0.5), (2, h // 2), (w - 2, h // 2), 1)
        leaf = pygame.transform.rotate(leaf, rng.randint(0, 180))
        s.blit(leaf, (x - leaf.get_width() // 2, y - leaf.get_height() // 2))
    return _down(s)


def spike_tile(seed=6):
    rng = random.Random(seed)
    s = pygame.Surface((TS, TS), pygame.SRCALPHA)
    pygame.draw.rect(s, (24, 10, 28), (0, TS * 0.62, TS, TS * 0.38))
    for i in range(4):
        cx = TS * (i + 0.5) / 4 + rng.randint(-4, 4)
        h = TS * rng.uniform(0.6, 0.9)
        base = TS * 0.66
        pygame.draw.polygon(s, (150, 140, 170), [(cx - 13, base), (cx, base - h), (cx + 13, base)])
        pygame.draw.polygon(s, (230, 226, 240), [(cx - 3, base - 6), (cx, base - h + 4), (cx + 5, base - 6)])
        pygame.draw.aalines(s, (60, 40, 70), True, [(cx - 13, base), (cx, base - h), (cx + 13, base)])
        pygame.draw.circle(s, (200, 60, 90), (int(cx), int(base - h + 6)), 3)   # a drop of red on the tip
    return _down(s)


def water_frames(n=8):
    """(surface tile frames, body tile) – smooth gradient water with a moving wave crest."""
    body = pygame.transform.smoothscale(_gradient((32, 62, 116), (18, 36, 80)), (TILE, TILE))
    tops = []
    for f in range(n):
        s = _gradient((44, 90, 150), (24, 50, 100))
        ph = f / n * math.tau
        pts = [(x, 12 + math.sin(x / TS * math.tau * 2 + ph) * 5) for x in range(0, TS + 1, 4)]
        pygame.draw.polygon(s, (0, 0, 0, 0), [(0, 0)] + pts + [(TS, 0)])        # cut out the air above
        pygame.draw.lines(s, (150, 210, 255), False, pts, 5)
        pygame.draw.lines(s, (230, 248, 255), False, [(x, y - 1) for x, y in pts[::3]], 2)
        for i in range(3):
            bx = (i * 47 + f * 9) % TS
            pygame.draw.circle(s, (120, 180, 240), (bx, 40 + i * 22), 3, 1)
        tops.append(_down(s))
    return tops, body


def lava_frames(n=8):
    tops, bodies = [], []
    for f in range(n):
        ph = f / n * math.tau
        b = _gradient((255, 140, 50), (200, 50, 20))
        for i in range(7):                                    # slow, soft glowing blobs
            x = (i * 37 + math.sin(ph + i) * 12) % TS
            y = (i * 53 + f * 6) % TS
            r = 10 + (i % 3) * 4
            for k in range(4):                                # soft edge: rings fading inwards
                c = _lerp((236, 96, 36), (255, 214, 110), (k + 1) / 4)
                pygame.draw.circle(b, c, (int(x), int(y)), int(r * (1 - k * 0.22)))
        for i in range(4):                                    # dark cooling crust streaks
            y = (i * 31 + f * 4) % TS
            pygame.draw.line(b, (170, 44, 18), (0, y), (TS, y + math.sin(ph + i) * 8), 3)
        bodies.append(_down(b))
        t = b.copy()
        pts = [(x, 10 + math.sin(x / TS * math.tau * 1.5 + ph) * 6) for x in range(0, TS + 1, 4)]
        pygame.draw.polygon(t, (0, 0, 0, 0), [(0, 0)] + pts + [(TS, 0)])
        pygame.draw.lines(t, (255, 236, 150), False, pts, 6)
        tops.append(_down(t))
    return tops, bodies
