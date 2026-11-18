"""High-resolution creature models (Shadowra, Fira, the elves, Moosläufer, fish, owl).

Every model is drawn at SS× resolution on its own surface and then smoothly scaled down
(supersampling). That gives anti-aliased, smooth edges instead of jagged pygame polygons.
Shapes are built from curves: tapered "tubes" along Bézier centre lines for tails, necks,
limbs and horns, scalloped wing membranes, layered shading for bodies.

Coordinates are in *model units* relative to the feet (0, 0), facing right.
"""
import math

import pygame

from . import dragon_design

SS = 4                       # supersampling factor for normal-sized models (3 for big ones)

BODY = (86, 56, 88)          # muted plum, as in the logo (was a bluer violet)
OUTLINE = (22, 12, 26)
WING = (66, 42, 70)
HORN = (228, 208, 170)


def shade(col, d):
    return tuple(max(0, min(255, int(c + d))) for c in col[:3])


def bez(p0, p1, p2, n=12):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c = (1 - u) ** 2, 2 * (1 - u) * u, u * u
        out.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))
    return out


def taper(points, w0, w1):
    """Polygon around a centre line whose width goes from w0 to w1."""
    left, right = [], []
    n = len(points)
    for i, (x, y) in enumerate(points):
        if i < n - 1:
            dx, dy = points[i + 1][0] - x, points[i + 1][1] - y
        else:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def glow(screen, x, y, r, col, alpha):
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(5, 0, -1):
        pygame.draw.circle(surf, (*col, int(alpha * (6 - i) / 5)), (r, r), int(r * i / 5))
    screen.blit(surf, (x - r, y - r))


# ---------------------------------------------------------------------------
# Lighting & surface texture – turns flat shapes into lit, three-dimensional looking bodies
# ---------------------------------------------------------------------------
_light_cache = {}


def _texture_tile(kind, ss):
    """Small tileable multiply-pattern (255 = unchanged) for a surface type."""
    if isinstance(kind, tuple) and kind[0] == "scales":       # ("scales", scale width in px)
        return _scale_tiles(kind[1])["mult"]
    if kind == "scales":                                         # default scale size
        return _scale_tiles(4 * ss)["mult"]
    key = ("tile", kind, ss)
    if key in _light_cache:
        return _light_cache[key]
    import random as _r
    rng = _r.Random(hash(kind) & 0xffff)
    n = 16 * ss
    t = pygame.Surface((n, n))
    t.fill((255, 255, 255))
    if kind == "fur":                       # short soft strokes
        for _ in range(26):
            x, y = rng.randrange(n), rng.randrange(n)
            c = rng.randint(196, 236)
            pygame.draw.line(t, (c, c, c), (x, y), (x + rng.randint(-2, 2) * ss // 2, y + 3 * ss), max(1, ss // 2))
    elif kind == "feathers":
        r = 5 * ss
        for row in range(4):
            for col in range(4):
                cx, cy = col * r + (r // 2 if row % 2 else 0), row * r * 0.8
                pygame.draw.arc(t, (200, 190, 182), (cx - r // 2, cy - r // 2, r, r), 3.5, 5.9, max(1, ss // 2))
    elif kind == "cloth":                     # fine weave
        for i in range(0, n, max(2, ss)):
            pygame.draw.line(t, (238, 236, 240), (i, 0), (i, n), 1)
            pygame.draw.line(t, (244, 242, 246), (0, i), (n, i), 1)
    elif kind == "bone":                      # worn, pitted surface
        for _ in range(14):
            c = rng.randint(206, 236)
            pygame.draw.circle(t, (c, c - 4, c - 10), (rng.randrange(n), rng.randrange(n)), rng.randint(1, ss))
    _light_cache[key] = t
    return t


def _texture_sheet(kind, ss, w, h):
    key = ("sheet", kind, ss, w, h)
    if key not in _light_cache:
        tile = _texture_tile(kind, ss)
        sheet = pygame.Surface((w, h))
        for y in range(0, h, tile.get_height()):
            for x in range(0, w, tile.get_width()):
                sheet.blit(tile, (x, y))
        if len(_light_cache) > 120:
            _light_cache.clear()
        _light_cache[key] = sheet
    return _light_cache[key]


def _ambient(w, h):
    """Light from above: bright at the top of the model, falling off towards the feet."""
    key = ("amb", w, h)
    if key not in _light_cache:
        g = pygame.Surface((w, h))
        for y in range(h):
            k = y / max(1, h - 1)
            g.fill((int(255 - 70 * k), int(250 - 74 * k), int(246 - 62 * k)), (0, y, w, 1))
        _light_cache[key] = g
    return _light_cache[key]


def light_model(surf, ss, texture=None, plain=None):
    """Shade a flat-coloured model in place: ambient falloff, surface texture, a warm rim light on the
    lit (upper) edges and soft occlusion on the shadow (lower) edges.
    plain: optional mask (white = no texture there, e.g. horns and eyes; see Pen.plain)."""
    w, h = surf.get_size()
    mask = pygame.mask.from_surface(surf, 60)
    surf.blit(_ambient(w, h), (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    if texture:
        tex = _texture_sheet(texture, ss, w, h)
        if plain is not None:
            tex = tex.copy()
            tex.blit(plain, (0, 0), special_flags=pygame.BLEND_RGB_MAX)
        surf.blit(tex, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    for d, col in ((max(1, ss), (70, 62, 84)), (3 * ss, (26, 22, 34))):          # rim light (top edges)
        edge = mask.copy()
        edge.erase(mask, (ss // 2, d))
        surf.blit(edge.to_surface(setcolor=(*col, 255), unsetcolor=(0, 0, 0, 255)), (0, 0),
                  special_flags=pygame.BLEND_RGB_ADD)
    for d, col in ((2 * ss, (150, 138, 170)), (6 * ss, (205, 196, 216))):        # occlusion (bottom edges)
        edge = mask.copy()
        edge.erase(mask, (-ss // 2, -d))
        surf.blit(edge.to_surface(setcolor=(*col, 255), unsetcolor=(255, 255, 255, 255)), (0, 0),
                  special_flags=pygame.BLEND_RGB_MULT)
    return mask


def ground_shadow(screen, x, y, w):
    """Soft contact shadow on the ground under a creature."""
    w = max(10, int(w))
    key = ("shadow", w)
    s = _light_cache.get(key)
    if s is None:
        h = max(4, w // 4)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            a = int(16 * (7 - i))
            pygame.draw.ellipse(s, (0, 0, 0, a), (w * (6 - i) / 14, h * (6 - i) / 14, w * (1 - (6 - i) / 7), h * (1 - (6 - i) / 7)))
        _light_cache[key] = s
    screen.blit(s, (x - s.get_width() / 2, y - s.get_height() / 2))


# ---------------------------------------------------------------------------
# Dragon scales: texture + the way they catch the light
# ---------------------------------------------------------------------------
def _scale_tiles(sw):
    """Seamless tiles for egg-shaped, overlapping scales sw px wide (as drawn in the logo).

    mult    multiply pattern: thin dark crease around each scale, lighter domed centre, fine grain
    top     gloss mask (black = matte) for light from above / the side: a soft spot on each dome
    bottom  gloss mask for light from below (lava): a thin glint along each scale's free edge
    spark_a / spark_b   a few scales that glint brightly; the two sets alternate over time
    """
    sw = max(4, int(sw))
    key = ("scale_tiles", sw)
    if key in _light_cache:
        return _light_cache[key]
    import random as _r
    rng = _r.Random(sw * 7919)
    rh = max(2, round(sw * 0.62))                 # row spacing: rows overlap like roof tiles
    N = 6                                          # 6 x 6 scales per tile: the repeat is hard to spot
    W, H = N * sw, N * rh
    scales = []
    for row in range(N):
        for col in range(N):
            i = row * N + col                      # each scale is a little different (size, place, tone)
            jx, jy = rng.uniform(-0.07, 0.07) * sw, rng.uniform(-0.06, 0.06) * sw
            sz, tone, gl = rng.uniform(0.94, 1.06), rng.randint(-10, 8), rng.uniform(0.45, 1.0)
            cx, cy = col * sw + (sw / 2 if row % 2 else 0) + jx, row * rh + jy
            for dx in (-W, 0, W):
                for dy in (-H, 0, H):
                    scales.append((cx + dx, cy + dy, i, sz, tone, gl))
    scales.sort(key=lambda s: -s[1])              # lowest row first: each row overlaps the one below

    def ell(surf, col, cx, cy, w, h):
        r = pygame.Rect(0, 0, max(1, round(w)), max(1, round(h)))
        r.center = (round(cx), round(cy))
        pygame.draw.ellipse(surf, col, r)

    def grey(v, tint=(0, -3, 3)):
        return tuple(max(0, min(255, v + d)) for d in tint)

    def u_arc(surf, col, cx, cy, w, h, dy=0):        # the free (lower) edge of a scale: a U-shaped line
        r = pygame.Rect(0, 0, max(2, round(w)), max(2, round(h)))
        r.center = (round(cx), round(cy + dy))
        pygame.draw.arc(surf, col, r, math.pi * 1.04, math.pi * 1.96, 1)

    crease = 168 if sw >= 6 else 184
    tiles = {n: pygame.Surface((W, H)) for n in ("mult", "top", "bottom", "spark_a", "spark_b")}
    tiles["mult"].fill((255, 255, 255))
    for n in ("top", "bottom", "spark_a", "spark_b"):
        tiles[n].fill((0, 0, 0))
    for cx, cy, i, sz, tone, gl in scales:
        ew, eh = sw * 1.06 * sz, sw * 1.22 * sz
        m = tiles["mult"]                          # the visible part of a scale is its lower ~60 %
        u_arc(m, grey(206 + tone), cx, cy, ew, eh, dy=1)               # soft shadow it casts on the scale below
        ell(m, grey(228 + tone), cx, cy, ew, eh)
        ell(m, grey(237 + tone), cx - 0.06 * sw, cy + 0.14 * sw, ew * 0.34, eh * 0.3)    # faint dome
        u_arc(m, grey(crease + tone), cx, cy, ew, eh)
        for n in ("top", "bottom", "spark_a", "spark_b"):
            ell(tiles[n], (0, 0, 0), cx, cy, ew, eh)                 # hidden under the scale above
        g = int(255 * gl)
        ell(tiles["top"], grey(int(g * 0.3), (0, 0, 0)), cx - 0.05 * sw, cy + 0.1 * sw, ew * 0.7, eh * 0.42)
        ell(tiles["top"], grey(int(g * 0.65), (0, 0, 0)), cx - 0.07 * sw, cy + 0.09 * sw, ew * 0.46, eh * 0.26)
        ell(tiles["top"], grey(g, (0, 0, 0)), cx - 0.09 * sw, cy + 0.07 * sw, ew * 0.24, eh * 0.13)
        ell(tiles["bottom"], grey(int(g * 0.8), (0, 0, 0)), cx, cy + eh * 0.36, ew * 0.66, eh * 0.13)
        spark = (i * 7 + 3) % 6
        if spark in (0, 3):
            n = "spark_a" if spark == 0 else "spark_b"
            ell(tiles[n], (255, 255, 255), cx - 0.09 * sw, cy + 0.07 * sw, max(1.2, ew * 0.2), max(1.2, eh * 0.12))
    m = tiles["mult"]
    for _ in range(W * H // 9):                   # grain, like the logo's painted texture
        x, y = rng.randrange(W), rng.randrange(H)
        c = m.get_at((x, y))
        d = rng.randint(-12, 8)
        m.set_at((x, y), (max(0, min(255, c[0] + d)), max(0, min(255, c[1] + d)), max(0, min(255, c[2] + d))))
    _light_cache[key] = tiles
    return tiles


_sheet_cache = {}


def _tiled(name, sw, w, h, level=1.0):
    """A w x h sheet of one of the scale tiles, optionally dimmed (level < 1) – cached."""
    key = ("tiled", name, sw, w, h, level)
    sheet = _sheet_cache.get(key)
    if sheet is None:
        tile = _scale_tiles(sw)[name]
        sheet = pygame.Surface((w, h))
        for y in range(0, h, tile.get_height()):
            for x in range(0, w, tile.get_width()):
                sheet.blit(tile, (x, y))
        if level < 1.0:
            v = int(255 * level)
            sheet.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
        if len(_sheet_cache) > 120:              # ~14 sheets per model size
            _sheet_cache.clear()
        _sheet_cache[key] = sheet
    return sheet


SHEEN_AMBIENT = (16, 11, 20)          # the faintest gloss even in the dark: scales stay readable up close
SHEEN_GAIN = 0.55                     # how glossy the scales are (1 = white highlights at full light)
DIFFUSE = 0.22                        # how much nearby light also brightens/tints her body overall
SPARK_LEVELS = 6                      # glint brightness steps (each step is a cached sheet)


def apply_sheen(surf, sw, lights, t=0.0, phase=0.0, gain=1.0, ambient=SHEEN_AMBIENT, rim=True, plain=None,
                mask=None):
    """Make the scales of a finished (lit and textured) model catch nearby light.

    lights: (x, y, radius, colour, strength) in the surface's own pixel coordinates. Each scale gets a
    glossy spot tinted with the light's colour, strongest on the side facing the light; a few scales
    glint and fade in turn (t, phase) and the silhouette facing the light gets a thin rim highlight.
    plain: texture mask of the model (white = no scales there): those parts get no scale gloss.
    mask: the model's silhouette (pygame.mask), if already known.
    """
    w, h = surf.get_size()
    if w < 4 or h < 4:
        return
    G = 5                                          # light field: sampled on a 5x5 grid, smoothly scaled up
    grid = pygame.Surface((G, G))                  # gloss strength per pixel
    dgrid = pygame.Surface((G, G))                 # soft overall brightening (diffuse)
    active, total, (dir_x, dir_y), below, above = _light_summary(lights, w, h, gain)
    for gy in range(G):
        for gx in range(G):
            px, py = gx * (w - 1) / (G - 1), gy * (h - 1) / (G - 1)
            rgb = [0.0, 0.0, 0.0]
            for lx, ly, reach, col, st in active:
                f = max(0.0, 1 - math.hypot(lx - px, ly - py) / reach) ** 1.5 * st * gain
                for c in range(3):
                    rgb[c] += col[c] * f
            grid.set_at((gx, gy), tuple(min(255, int(ambient[c] + v * SHEEN_GAIN)) for c, v in enumerate(rgb)))
            dgrid.set_at((gx, gy), tuple(min(255, int(v * DIFFUSE)) for v in rgb))
    field = pygame.transform.smoothscale(grid, (w, h))

    gloss = _tiled("bottom" if below > above * 1.5 else "top", sw, w, h).copy()
    lit = max(total) / 255
    if lit > 0.05:                                 # glints come and go as she moves
        a = 0.5 + 0.5 * math.sin(t * 2.6 + phase)
        for name, k in (("spark_a", a), ("spark_b", 1 - a)):
            level = round(SPARK_LEVELS * min(1.0, k * k * min(1.0, lit * 1.4)))
            if level:
                gloss.blit(_tiled(name, sw, w, h, level / SPARK_LEVELS), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(pygame.transform.smoothscale(dgrid, (w, h)), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    gloss.blit(field, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    if plain is not None:
        gloss.blit(plain, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    surf.blit(gloss, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    if rim:
        rim_light(surf, lights, gain, mask)


def _light_summary(lights, w, h, gain=1.0):
    """Lights that reach a w x h model, their summed colour at its centre, the direction they come from
    and how much of it comes from below vs. above."""
    cx0, cy0 = w / 2, h * 0.55
    active, total = [], [0.0, 0.0, 0.0]
    dir_x = dir_y = below = above = 0.0
    for lx, ly, r, col, st in lights:
        reach = r * 1.3 + 24                   # a glow's radius is roughly how far its light carries
        d = math.hypot(lx - cx0, ly - cy0)
        if d > reach + math.hypot(w, h) / 2:
            continue
        active.append((lx, ly, reach, col, st))
        f = max(0.0, 1 - d / reach) ** 1.5 * st * gain
        if f <= 0:
            continue
        down = max(0.0, (ly - cy0) / (d or 1))
        dir_x += (lx - cx0) / (d or 1) * f
        dir_y += (ly - cy0) / (d or 1) * f
        below += f * down
        above += f * (1 - down)
        for c in range(3):
            total[c] += col[c] * f
    return active, total, (dir_x, dir_y), below, above


def rim_light(surf, lights, gain=1.0, mask=None):
    """Thin highlight along the edges of the silhouette that face the light."""
    w, h = surf.get_size()
    _, total, (dir_x, dir_y), _, _ = _light_summary(lights, w, h, gain)
    L = math.hypot(dir_x, dir_y)
    if L < 0.06:
        return
    ux, uy = dir_x / L, dir_y / L
    if mask is None:
        mask = pygame.mask.from_surface(surf, 60)
    edge = mask.copy()
    edge.erase(mask, (round(-ux * 2), round(-uy * 2)))
    k = min(1.0, L) * 0.6
    lit = max(1.0, max(total) / 255)
    col = tuple(min(255, int(c / lit * k)) for c in total)
    surf.blit(edge.to_surface(setcolor=(*col, 255), unsetcolor=(0, 0, 0, 255)), (0, 0),
              special_flags=pygame.BLEND_RGB_ADD)


def lights_for_sprite(x0, y0, w, facing, extra=()):
    """Screen-space lights (last frame's glows + extra) moved into a sprite's own pixel coordinates
    (and mirrored when the sprite is flipped, because the sheen is applied before flipping)."""
    from . import lights as _lights
    out = []
    for lx, ly, r, col, st in list(_lights.last()) + list(extra):
        x = lx - x0
        out.append((w - x if facing < 0 else x, ly - y0, r, col, st))
    return out


class Pen:
    """A supersampled canvas that draws in model units.

    Set pen.plain = True while drawing parts that must not get the surface texture (horns, eyes, wing
    membranes, belly plates). Those are tracked in a small texture mask at final size (white = plain);
    everything drawn on top of them afterwards clears the mask again, so overlaps stay correct.
    """

    def __init__(self, w_units, h_units, origin, k, ss=None):
        # big models already have many pixels: 2x supersampling is enough there and much cheaper
        self.ss = ss or (SS if k < 1.1 else 3)
        self.k = k * self.ss
        self.W = int(w_units * self.k) + 4
        self.H = int(h_units * self.k) + 4
        self.s = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.ox, self.oy = origin[0] * self.k, origin[1] * self.k
        self.ow = self.ss                  # 1 px outline after downscaling
        self.texture = None                # surface texture applied by the lighting pass
        self.plain = False
        self.m = None                      # texture mask (final size), created with the first plain shape
        self.silhouette = None             # pygame.mask of the finished model (set by finish)
        self.oc = None                     # outline colour override (design); None = OUTLINE

    def _o(self, outline):
        return self.oc if (self.oc and outline is OUTLINE) else outline

    def P(self, x, y):
        return (self.ox + x * self.k, self.oy + y * self.k)

    def _mask(self):
        """The texture mask to mark the current shape in, or None if nothing needs marking."""
        if self.plain and self.m is None:
            self.m = pygame.Surface((max(1, self.W // self.ss), max(1, self.H // self.ss)))
            self.m.fill((0, 0, 0))
        return self.m

    def _mcol(self):
        return (255, 255, 255) if self.plain else (0, 0, 0)

    def poly(self, col, pts, outline=OUTLINE):
        if len(pts) < 3:
            return
        ps = [self.P(*p) for p in pts]
        pygame.draw.polygon(self.s, col, ps)
        outline = self._o(outline)
        if outline:
            pygame.draw.polygon(self.s, outline, ps, self.ow)
        m = self._mask()
        if m is not None:
            pygame.draw.polygon(m, self._mcol(), [(x / self.ss, y / self.ss) for x, y in ps])

    def ell(self, col, cx, cy, w, h, outline=OUTLINE):
        r = pygame.Rect(0, 0, max(2, int(w * self.k)), max(2, int(h * self.k)))
        r.center = self.P(cx, cy)
        pygame.draw.ellipse(self.s, col, r)
        outline = self._o(outline)
        if outline:
            pygame.draw.ellipse(self.s, outline, r, self.ow)
        m = self._mask()
        if m is not None:
            pygame.draw.ellipse(m, self._mcol(), (r.x // self.ss, r.y // self.ss, max(1, r.w // self.ss),
                                                  max(1, r.h // self.ss)))

    def blob(self, col, ells, outline=OUTLINE):
        """Several overlapping ellipses (cx, cy, w, h) as one shape with a single outline around them."""
        if outline:
            o = 2 * self.ow / self.k
            for cx, cy, w, h in ells:
                self.ell(self._o(outline), cx, cy, w + o, h + o, outline=None)
        for cx, cy, w, h in ells:
            self.ell(col, cx, cy, w, h, outline=None)

    def circle(self, col, x, y, r, outline=None):
        c = self.P(x, y)
        rr = max(1, int(r * self.k))
        if outline:
            pygame.draw.circle(self.s, outline, c, rr + self.ow)
        pygame.draw.circle(self.s, col, c, rr)
        m = self._mask()
        if m is not None:
            pygame.draw.circle(m, self._mcol(), (c[0] / self.ss, c[1] / self.ss), max(1, rr / self.ss))

    def line(self, col, a, b, w):
        pa, pb, lw = self.P(*a), self.P(*b), max(1, int(w * self.k))
        pygame.draw.line(self.s, col, pa, pb, lw)
        m = self._mask()
        if m is not None:
            pygame.draw.line(m, self._mcol(), (pa[0] / self.ss, pa[1] / self.ss), (pb[0] / self.ss, pb[1] / self.ss),
                             max(1, round(lw / self.ss)))

    def arc(self, col, cx, cy, rx, ry, a0, a1, w):
        r = pygame.Rect(0, 0, int(rx * 2 * self.k), int(ry * 2 * self.k))
        r.center = self.P(cx, cy)
        lw = max(1, int(w * self.k))
        pygame.draw.arc(self.s, col, r, a0, a1, lw)
        m = self._mask()
        if m is not None and r.w >= self.ss and r.h >= self.ss:
            pygame.draw.arc(m, self._mcol(), (r.x // self.ss, r.y // self.ss, r.w // self.ss, r.h // self.ss),
                            a0, a1, max(1, round(lw / self.ss)))

    def tube(self, col, pts, w0, w1, outline=OUTLINE, caps=True):
        """Smooth tapered limb/tail/neck along a centre line, with rounded ends."""
        if caps and outline:
            self.circle(self._o(outline), *pts[0], w0 / 2 + self.ow / self.k)
            self.circle(self._o(outline), *pts[-1], max(0.3, w1 / 2) + self.ow / self.k)
        self.poly(col, taper(pts, w0, w1), outline)
        if caps:
            self.circle(col, *pts[0], w0 / 2)
            self.circle(col, *pts[-1], max(0.3, w1 / 2))

    def finish(self, facing=1, tint=None, flash=False, texture=None, lit=True):
        s = pygame.transform.smoothscale(self.s, (max(1, self.W // self.ss), max(1, self.H // self.ss)))
        if lit:                         # lighting at final size: same look, ~9x fewer pixels to process
            self.silhouette = light_model(s, 1, texture or self.texture, self.m)
        if tint:
            s.fill(tint, special_flags=pygame.BLEND_RGB_ADD)
        if flash:
            s.fill((110, 60, 60), special_flags=pygame.BLEND_RGB_ADD)
        if facing < 0:
            s = pygame.transform.flip(s, True, False)
        return s


# ---------------------------------------------------------------------------
# Shadowra (and Fira / the storm dragon, which reuse the same model)
# ---------------------------------------------------------------------------
WING_POSES = {
    #          elbow        finger 1      finger 2       finger 3      membrane root
    "spread": ((-4, -26), (-2, -42), (-24, -38), (-42, -20), (-22, -1)),
    "up":     ((2, -28), (6, -50), (-12, -48), (-28, -32), (-18, -2)),
    "down":   ((-6, 10), (-6, 26), (-26, 22), (-38, 8), (-20, -2)),
    "droop":  ((-8, -4), (-14, 8), (-24, 10), (-28, 4), (-8, 4)),
    "fold":   ((-6, -10), (-12, -17), (-22, -13), (-25, -4), (-8, 2)),
    "embrace": ((10, -14), (24, -16), (26, -4), (20, 4), (-4, 3)),     # wings wrapped forward (hug)
}


def _wing(pen, sx, sy, state, col, bone, dx=0.0, dy=0.0, spread_extra=0.0, scale=1.0):
    e, t1, t2, t3, r = [(x * scale + sx + dx, y * scale + sy + dy) for x, y in WING_POSES[state]]
    t1 = (t1[0] + spread_extra, t1[1])
    t2 = (t2[0] + spread_extra, t2[1])
    sh = (sx + dx, sy + dy)

    def scallop(a, b):                       # the membrane edge curves inwards between fingers
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        return bez(a, (mx + (sh[0] - mx) * 0.28, my + (sh[1] - my) * 0.28), b, 6)[1:-1]

    membrane = [sh, e, t1] + scallop(t1, t2) + [t2] + scallop(t2, t3) + [t3] + scallop(t3, r) + [r]
    pen.poly(col, membrane)
    # thin membrane: lighter where it is stretched near the trailing edge, fine veins branching off the bones
    for a, b in ((t1, t2), (t2, t3), (t3, r)):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        inner = (e[0] + (mid[0] - e[0]) * 0.55, e[1] + (mid[1] - e[1]) * 0.55)
        pen.poly(shade(col, 10), [e, inner, a], outline=None)
        for f in (0.35, 0.6):
            p0 = (e[0] + (a[0] - e[0]) * f, e[1] + (a[1] - e[1]) * f)
            pen.line(shade(col, 22), p0, (p0[0] + (mid[0] - p0[0]) * 0.5, p0[1] + (mid[1] - p0[1]) * 0.5), 0.3)
    pen.tube(bone, [sh, e], 3.2 * scale, 2.4 * scale, outline=None)
    for tip in (t1, t2, t3):
        pen.tube(bone, [e, tip], 1.5 * scale, 0.6, outline=None)
        pen.poly(shade(bone, 30), [(tip[0] - 0.8, tip[1]), (tip[0] + 0.2, tip[1] - 2.2), (tip[0] + 0.8, tip[1])],
                 outline=None)                                    # small claw at each finger tip
    pen.circle(shade(bone, 10), *e, 1.6 * scale)
    return e


def _rot(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def _custom_part(pen, part, ax, ay, unit, col, outline_col):
    """One extra part from the editor, in model units. angle 0 = pointing up, positive = clockwise."""
    kind = part["type"]
    bx, by = ax + part["x"] * unit, ay + part["y"] * unit
    s, ln = part["size"] * unit, part["length"] * unit
    ang, bend = part["angle"], part.get("bend", 0.0)

    def P(u, v):                              # local coords: u across, v along the part (v < 0 = outwards)
        x, y = _rot(u, v, ang)
        return bx + x, by + y

    if kind == "spike":
        tip = P(bend * ln * 0.4, -ln)
        mid = P(bend * ln * 0.25 - s * 0.1, -ln * 0.5)
        pen.poly(col, [P(-s / 2, 0), mid, tip, P(s / 2, 0)], outline=outline_col)
    elif kind == "horn":
        pts = bez(P(0, 0), P(bend * ln * 0.5, -ln * 0.6), P(bend * ln * 1.1, -ln), 10)
        pen.tube(col, pts, s, 0.2, outline=outline_col)
        for i in (3, 6):
            (px, py), (qx, qy) = pts[i], pts[i + 1]
            nx_, ny_ = -(qy - py), qx - px
            L = math.hypot(nx_, ny_) or 1
            w = s * (1 - i / 10) / 2
            pen.line(shade(col, -40), (px - nx_ / L * w, py - ny_ / L * w), (px + nx_ / L * w, py + ny_ / L * w),
                     0.3 * unit)
    elif kind == "fin":                       # a sail of membrane between thin spines (length = along the back)
        n = 5
        us = [-ln / 2 + ln * i / (n - 1) for i in range(n)]
        hs = [s * (0.15 + 0.85 * math.sin(math.pi * i / (n - 1))) for i in range(n)]   # sail profile
        tips = [(u + bend * h, -h) for u, h in zip(us, hs)]
        edge = []                             # membrane edge dips in between the spine tips
        for (u0, v0), (u1, v1) in zip(tips, tips[1:]):
            edge += [P(*q) for q in bez((u0, v0), ((u0 + u1) / 2, (v0 + v1) / 2 + s * 0.18), (u1, v1), 5)[:-1]]
        edge.append(P(*tips[-1]))
        pen.poly(col, [P(us[-1], 0), P(us[0], 0)] + edge, outline=outline_col)
        for u, (tu, tv) in zip(us, tips):
            pen.line(shade(col, -34), P(u, 0), P(tu, tv - s * 0.12), 0.45 * unit)
    elif kind == "oval":
        pts = [P(math.cos(a) * s / 2, math.sin(a) * ln / 2) for a in [i * math.pi / 12 for i in range(24)]]
        pen.poly(col, pts, outline=outline_col)
        pen.poly(shade(col, 18), [P(math.cos(a) * s / 4 - s * 0.08, math.sin(a) * ln / 4 - ln * 0.12)
                                  for a in [i * math.pi / 8 for i in range(16)]], outline=None)
    elif kind == "whisker":
        pts = bez(P(0, 0), P(bend * ln * 0.5, -ln * 0.5), P(bend * ln * 0.2, -ln), 10)
        pen.tube(col, pts, max(0.25, s), 0.15, outline=None)
    elif kind == "gem":                       # a glowing mark or jewel
        pen.circle(shade(col, -60), bx, by, s * 0.62, outline=outline_col)
        pen.circle(col, bx, by, s * 0.5)
        pen.circle(shade(col, 70), bx - s * 0.15, by - s * 0.18, s * 0.18)


def draw_dragon(screen, feet_x, feet_y, stage, facing, pose, t, eye=(220, 30, 40),
                obsidian=False, tint=None, flap=0.0, body=BODY, horn=HORN, scale_mult=1.0, extra_lights=(),
                design=None, info=None):
    """Shadowra (or Fira) seen from the side, styled after the logo. Her scales catch the light of every
    glow drawn last frame (see lights.py) plus extra_lights (screen space, e.g. sunbeams or lava).

    design: sizes/colours/parts (dragon_design). Default: Shadowra's design file for Shadowra, the standard
    shape for other dragons (Fira passes her own body / horn colours).
    info: optional dict, filled with anchor positions on screen (used by the editor)."""
    shadowra = body is BODY and horn is HORN
    d = design or (dragon_design.current() if shadowra else dragon_design.DEFAULT)
    S, on, cnt = d["sizes"], d["parts"], d["counts"]
    cols = dragon_design.colors(d, None if shadowra else body, None if shadowra else horn)

    k = (0.62, 1.0, 1.42)[stage] * scale_mult * S["overall"]
    hk = (1.35, 1.0, 0.95)[stage] * S["head"]     # hatchlings have big heads
    bl, bh, ll = S["body_length"], S["body_height"], S["leg_length"]
    ws, sp = S["wing"], S["spikes"]
    E = max(1.0, bl, S["tail_length"], ws, S["neck_length"] * 0.9, hk * 0.9, S["horn_length"] * 0.8, ll * 0.9)
    pen = Pen(150 * E, 122 * E, (75 * E, 122 * E - 4), k)
    pen.oc = cols["outline"] if cols["outline"] != OUTLINE else None
    scale_px = max(4, round((3.0 + 2.8 * k) * S["scales"]))       # scale size on screen grows with her
    pen.texture = ("scales", scale_px) if on["scales"] else None
    body = cols["body"]
    dark = shade(body, -24)
    darker = cols["spikes"]
    belly = cols["belly"]
    wing_col = cols["wing"]
    curl = pose == "curl_eat"                     # lying curled around her meal (cozy meal, SAffection)
    lie = pose in ("sleep", "dead") or curl
    droop = pose == "exhausted"
    hug = pose == "hug"
    nuzzle = pose in ("nuzzle", "hug")
    eat = pose in ("eat", "nuzzle", "hug")
    air = pose in ("jump", "glide", "flap", "dive")

    by = -17 * (1 + (ll - 1) * 0.6) - (bh - 1) * 4 + (8 if lie else 0) + (2 if droop else 0)
    if lie:
        by = -9 - (bh - 1) * 6
    if pose in ("walk", "run"):
        by += math.sin(t * (14 if pose == "run" else 9)) * 1.2
    elif pose == "idle":
        by += math.sin(t * 2) * 0.6
    elif droop:
        by += math.sin(t * 5) * 1.2               # heavy breathing

    wing_state = "fold"
    if air:
        wing_state = "spread"
    if pose == "flap":
        wing_state = "down" if flap < 0.18 else "up"
    if droop:
        wing_state = "droop"
    if hug:
        wing_state = "embrace"
    sx, sy = 2 * bl, by - 8 * bh

    # where things sit (for extra parts); filled in as the parts are placed
    anchors = {"back": (0.0, by - 10.5 * bh, 1.0), "chest": (12 * bl, by + 2 * bh, 1.0),
               "hips": (-12 * bl, by, 1.0)}
    custom = d.get("custom") or []

    # head and neck position (needed early: extra parts behind the body can sit on the head)
    hx, hy = 24, by - 19
    if nuzzle:
        hx, hy = 30 + math.sin(t * 4) * 2.5, by - 8 + math.cos(t * 4) * 1.5
    elif droop or eat:
        hx, hy = 26, by - 4 + (math.sin(t * 8) * 2 if eat else 0)
    if lie:
        hx, hy = 24, by + 2
    if curl:                                      # head bowed low, chewing contentedly
        hx, hy = 22, by + 3 + math.sin(t * 8) * 1.2
    if pose == "fire":
        hx, hy = 27, by - 12
    n0 = (9 * bl, by - 5 * bh)                    # neck base; neck length stretches the way to the head
    hx, hy = n0[0] + (hx - 9) * S["neck_length"], n0[1] + (hy - (by - 5)) * S["neck_length"]
    neck = bez(n0, (n0[0] + 4, n0[1] - 9 if hy < by - 6 else n0[1] + 1), (hx - 3, hy + 1), 10)
    nw0, nw1 = 12 * S["neck_thickness"], 8 * S["neck_thickness"]
    anchors["neck"] = (*neck[5], 1.0)
    anchors["head"] = (hx, hy, hk)

    def draw_custom(layer):
        for p in custom:
            if p.get("layer", "front") != layer or p["anchor"] not in anchors:
                continue
            ax, ay, unit = anchors[p["anchor"]]
            col = dragon_design.part_color(p, cols)
            pen.plain = p["type"] in ("horn", "gem", "whisker", "fin")   # smooth parts: no scale texture
            if p.get("far_copy"):                 # the same part on her far side: darker, slightly offset
                _custom_part(pen, dict(p, x=p["x"] + 3 / unit, y=p["y"] - 1 / unit), ax, ay, unit,
                             shade(col, -45), OUTLINE)
            _custom_part(pen, p, ax, ay, unit, col, OUTLINE)
            pen.plain = False

    # ---- far wing (dark and mostly hidden: left textured, so the texture mask starts late = cheaper) ----
    if on["wings"]:
        _wing(pen, sx, sy, wing_state, shade(wing_col, -14), darker, dx=5, dy=-2, spread_extra=4, scale=ws)

    # ---- tail: one smooth curve tapering to a point, a row of spines along the top (as in the logo) ----
    sway = math.sin(t * 2.2) * 4
    if pose == "tail":
        sway = 22 * math.sin(min(1.0, (t % 0.35) / 0.35) * math.pi)
    drop = 5 if lie else 10
    tl, tw = S["tail_length"], 11.5 * S["tail_thickness"]
    t0x = -15 * bl
    if curl:                                      # tail curls around the food tucked at her flank (x ≈ -28)
        tail = bez((t0x + 1, by + 1), (t0x - 41 * tl, by + 1), (t0x - 9 * tl + sway * 0.2, by + 9), 16)
    else:
        tail = bez((t0x, by + 1), (t0x - 21 * tl, by + drop + 4 + sway * 0.4), (t0x - 47 * tl, by - 1 + sway), 16)
    anchors["tail_mid"] = (*tail[8], 1.0)
    anchors["tail_tip"] = (*tail[-1], 1.0)
    pen.tube(body, tail, tw, 0.7)
    under = []                                    # paler underside of the tail
    for i in range(len(tail) - 3):
        (px, py), (qx, qy) = tail[i], tail[i + 1]
        Ls = math.hypot(qx - px, qy - py) or 1
        w = tw + (0.7 - tw) * i / (len(tail) - 1)
        under.append((px + (qy - py) / Ls * w * 0.22, py - (qx - px) / Ls * w * 0.22))
    pen.tube(shade(belly, -10), under, tw * 0.37, 0.6, outline=None)
    n = cnt["tail_spines"] if on["tail_spines"] else 0
    for j in range(n):                            # spines along the tail, smaller towards the tip
        i = min(15, round(8 if n == 1 else 2 + j * 12 / (n - 1)))
        px, py = tail[i]
        qx, qy = tail[i + 1]
        dxs, dys = qx - px, qy - py
        Ls = math.hypot(dxs, dys) or 1
        n2x, n2y = -dys / Ls, dxs / Ls            # the tail runs leftwards: this normal points up
        w = (4.4 - i * 0.22) * sp
        base = tw + (0.7 - tw) * i / 16
        bx_, by_ = px + n2x * base * 0.38, py + n2y * base * 0.38
        pen.poly(darker, [(bx_ - dxs * 0.2, by_ - dys * 0.2),
                          (bx_ + n2x * w + dxs * 0.55, by_ + n2y * w + dys * 0.55),
                          (bx_ + dxs * 0.9, by_ + dys * 0.9)])
    if on["tail_spade"]:                          # optional spade at the tip
        tx, ty = tail[-1]
        ax, ay = tail[-1][0] - tail[-3][0], tail[-1][1] - tail[-3][1]
        L = math.hypot(ax, ay) or 1
        ux, uy = ax / L, ay / L
        nx, ny = -uy, ux
        pen.poly(dark, [(tx - ux * 1, ty - uy * 1), (tx + nx * 4 * sp + ux * 2, ty + ny * 4 * sp + uy * 2),
                        (tx + ux * 8 * sp, ty + uy * 8 * sp), (tx - nx * 4 * sp + ux * 2, ty - ny * 4 * sp + uy * 2)])

    # ---- legs (far pair first) ----
    claw_col = (24, 18, 30) if obsidian else cols["claw"]
    ph = t * (14 if pose == "run" else 9) if pose in ("walk", "run") else 0
    lt = S["leg_thickness"]
    toes = cnt["toes"] if on["toes"] else 0

    def leg(lx, i, col):
        lx *= bl
        swing = math.sin(ph + i * math.pi / 2) * 4 * ll if pose in ("walk", "run") else 0
        if lie:
            pen.ell(col, lx + 3, -2.5, 8 * lt, 4 * lt)
            for c in range(toes):
                pen.poly(claw_col, [(lx + 6 + c * 0.2, -3.6 + c * 1.1), (lx + 8.4, -3.2 + c * 1.2),
                                    (lx + 6 + c * 0.2, -2.6 + c * 1.1)], outline=None)
            return
        if air:
            swing = -3 if i < 2 else 3
        hip = (lx, by + 5 * bh)
        foot_y = hip[1] + 10 * ll if air else -1.2
        foot = (lx + swing, foot_y)
        knee = ((hip[0] + foot[0]) / 2 + (-2.5 if i < 2 else 1.5) * ll, (hip[1] + foot_y) / 2)
        pen.tube(col, bez(hip, knee, foot, 6), (7.2 if i < 2 else 5.8) * lt, 3.2 * lt)
        pen.ell(col, foot[0] + 1.2, foot_y - 0.4, 5.4 * lt, 3.0 * lt)
        for c in range(toes):                     # toes, each with a pale claw (logo)
            bx_ = foot[0] + 1.0 + (c - (toes - 1) / 2 + 1) * 1.25 * lt
            tip = (bx_ + 2.2 * lt, foot_y + 0.5)
            pen.tube(col, [(bx_, foot_y - 0.5), tip], 1.7 * lt, 1.2 * lt)
            pen.poly(claw_col, [(tip[0] - 0.2, tip[1] - 0.8 * lt), (tip[0] + 1.7 * lt, tip[1] + 0.25),
                                (tip[0] - 0.1, tip[1] + 0.55)], outline=OUTLINE)

    draw_custom("behind")
    leg(-12, 0, dark)
    leg(9, 2, dark)

    # ---- body: barrel plus a deep, raised chest (the logo's proud stance) ----
    ch = S["chest"]
    pen.blob(body, [(-4 * bl, by + 0.5, 40 * bl, 19 * bh), (9 * bl, by - 2.5 * bh, 22 * ch, 20 * bh * ch)])
    pen.ell(shade(body, 12), -4 * bl, by - 5.5 * bh, 28 * bl, 5.5 * bh, outline=None)
    pen.ell(belly, 3 * bl, by + 4.5 * bh, 32 * bl, 8.5 * bh, outline=None)
    if on["belly_plates"]:
        for i in range(7):                        # belly plates
            x = (-12 + i * 4.6) * bl
            pen.arc(shade(belly, -24), x + 1.5, by + 4.5 * bh, 2.4 * bl, 4.4 * bh, 4.3, 5.2, 0.4)
    n = cnt["back_spikes"] if on["back_spikes"] else 0
    c0 = (n - 1) / 2
    for i in range(n):                            # back spikes
        x = (-16 + (i * 28.8 / (n - 1) if n > 1 else 14.4)) * bl
        top = by - 10.5 * bh * math.sqrt(max(0.0, 1 - (x / (22 * bl)) ** 2))
        h = (3.6 - 1.35 * abs(i - c0) / max(c0, 1)) * sp
        pen.poly(darker, [(x - 1.6, top + 1), (x + 0.6, top - h), (x + 1.8, top + 1)], outline=None)

    leg(-5, 1, body)
    leg(14, 3, body)
    if not lie and on["muscles"]:                 # muscle definition: shoulder and thigh
        pen.arc(shade(body, -18), -8 * bl, by + 1, 6, 6 * bh, 3.6, 5.6, 0.5)
        pen.arc(shade(body, 16), -9 * bl, by - 1, 5, 4 * bh, 2.0, 3.4, 0.4)
        pen.arc(shade(body, -18), 12 * bl, by + 1, 5, 5 * bh, 3.8, 5.8, 0.5)
        pen.arc(shade(body, 16), 11 * bl, by - 1, 4, 3.5 * bh, 2.0, 3.4, 0.4)

    # ---- neck + head ----
    # spines down the back of the neck (behind the neck itself)
    n = cnt["neck_spines"] if on["neck_spines"] else 0
    for j in range(n):
        i = min(8, round(4 if n == 1 else 1 + j * 6 / (n - 1)))
        (px, py), (qx, qy) = neck[i], neck[i + 1]
        Ls = math.hypot(qx - px, qy - py) or 1
        nx_, ny_ = (qy - py) / Ls, -(qx - px) / Ls          # points to the back/top of the neck
        if nx_ > 0:
            nx_, ny_ = -nx_, -ny_
        w = nw0 + (nw1 - nw0) * i / 10
        bx_, by_ = px + nx_ * w * 0.42, py + ny_ * w * 0.42
        s = (3.2 - i * 0.12) * sp
        pen.poly(darker, [(bx_ + (qx - px) * 0.4, by_ + (qy - py) * 0.4), (bx_ + nx_ * s - (qx - px) * 0.3,
                          by_ + ny_ * s - (qy - py) * 0.3), (bx_ - (qx - px) * 0.5, by_ - (qy - py) * 0.5)])
    pen.tube(body, neck, nw0, nw1)
    if on["throat_plates"]:                       # pale throat plates down the front of the neck (logo)
        throat = []
        for i in range(len(neck) - 1):
            (px, py), (qx, qy) = neck[i], neck[i + 1]
            Ls = math.hypot(qx - px, qy - py) or 1
            nx_, ny_ = (qy - py) / Ls, -(qx - px) / Ls
            if nx_ < 0:
                nx_, ny_ = -nx_, -ny_
            w = nw0 + (nw1 - nw0) * i / 10
            throat.append((px + nx_ * w * 0.24, py + ny_ * w * 0.24, nx_, ny_, w))
        if len(throat) > 2:
            pen.tube(belly, [(x, y) for x, y, *_ in throat], nw0 * 0.42, nw1 * 0.4, outline=None)
            for x, y, nx_, ny_, w in throat[1:-1]:
                pen.line(shade(belly, -24), (x - nx_ * w * 0.2 + ny_ * 0.4, y - ny_ * w * 0.2 - nx_ * 0.4),
                         (x + nx_ * w * 0.2 + ny_ * 0.4, y + ny_ * w * 0.2 - nx_ * 0.4), 0.35)
    horn_col = cols["horn"]
    hl = (6, 10, 14)[stage] * S["horn_length"]
    ht, ha, hc = S["horn_thickness"], S["horn_angle"], S["horn_curve"]

    def horn_pts(base, ctrl, end):                # turn the horn around its base by horn_angle
        def r(p):
            x, y = _rot(p[0] - base[0], p[1] - base[1], ha)
            return base[0] + x, base[1] + y
        mid = ((base[0] + end[0]) / 2, (base[1] + end[1]) / 2)
        ctrl = (mid[0] + (ctrl[0] - mid[0]) * hc, mid[1] + (ctrl[1] - mid[1]) * hc)
        return bez(base, r(ctrl), r(end), 12)

    if on["horns"] and on["far_horn"]:           # far horn (behind the head)
        far_horn = horn_pts((hx - 3 * hk, hy - 4 * hk), (hx - 10 * hk, hy - 11 * hk - hl * 0.3),
                            (hx - 17 * hk - hl * 0.4, hy - 6 * hk - hl * 0.7))
        pen.tube(shade(horn_col, -45), far_horn, 3.8 * hk * ht, 0.2)
    if on["ear_frills"]:                          # ear frills: long, swept back (the spiky crown in the logo)
        n, fr = cnt["ear_frills"], S["frills"]
        for i in range(n):
            u = 0.0 if n == 1 else -1 + 2 * i / (n - 1)
            fx, fy, ln = -7 + abs(u), 4 * u, (10 - (1 if u < 0 else 2.5) * abs(u)) * fr
            root = (hx + fx * hk * 0.7, hy + fy * hk)
            tip = (root[0] - ln * hk, root[1] + (-3.5 + (u + 1) * 2.6) * hk * fr)
            mid = ((root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2 - 0.8 * hk)
            pen.poly(dark, [(root[0] + 0.6, root[1] - 2.2 * hk)] + bez((root[0], root[1] - 2 * hk), mid, tip, 4)[1:] +
                     [(root[0] + 0.6, root[1] + 2.0 * hk)])
            pen.line(shade(dark, 18), root, mid, 0.3)
    pen.ell(body, hx, hy, 18 * hk, 14 * hk)
    if on["crest_spike"]:                         # crest spike on the forehead, between the horns (logo)
        pen.poly(dark, [(hx + 1.4 * hk, hy - 6.3 * hk), (hx - 1.6 * hk, hy - (6.3 + 5.3 * sp) * hk),
                        (hx - 2.6 * hk, hy - 6.0 * hk)])
    sn = S["snout"]
    snout = [(hx + 2 * hk, hy - 5 * hk)] + bez((hx + 7 * hk * sn, hy - 5.5 * hk), (hx + 15 * hk * sn, hy - 4 * hk),
                                              (hx + 16 * hk * sn, hy + 0.5 * hk), 6) + \
        [(hx + 15 * hk * sn, hy + 3 * hk), (hx + 9 * hk * sn, hy + 5 * hk), (hx + 2 * hk, hy + 5.5 * hk)]
    pen.poly(body, snout)
    pen.ell(shade(body, 12), hx + 6 * hk * sn, hy - 3.5 * hk, 9 * hk * sn, 2.5 * hk, outline=None)
    pen.ell(belly, hx + 7 * hk * sn, hy + 4.2 * hk, 10 * hk * sn, 2.2 * hk, outline=None)        # pale chin
    if pose == "fire":                             # open jaw, glowing throat
        pen.poly((40, 10, 60), [(hx + 6 * hk, hy + 2 * hk), (hx + 16 * hk * sn, hy + 1 * hk),
                                (hx + 12 * hk * sn, hy + 6 * hk)])
    else:
        if on["smile"]:                            # the little smile from the logo: corner turned up
            smile = bez((hx + 15 * hk * sn, hy + 2.2 * hk), (hx + 9 * hk * sn, hy + 3.4 * hk),
                        (hx + 4.2 * hk, hy + 1.4 * hk), 8)
            pen.tube(shade(body, -44), smile, 0.6, 0.5, outline=None)
        if on["fangs"]:
            for fx in (hx + 11.5 * hk * sn, hx + 13.5 * hk * sn):          # two little fangs over the lip
                pen.poly((246, 240, 228), [(fx - 0.5 * hk, hy + 2.6 * hk), (fx + 0.5 * hk, hy + 2.5 * hk),
                                           (fx, hy + 3.9 * hk)], outline=None)
    pen.ell(cols["outline"], hx + 13.6 * hk * sn, hy - 1.2 * hk, 1.6 * hk, 0.9 * hk, outline=None)   # nostril
    pen.line(shade(body, 18), (hx + 4 * hk, hy - 4.6 * hk), (hx + 13 * hk * sn, hy - 3.4 * hk), 0.35)  # ridge light
    es = S["eye"]
    ex, ey = hx + 4 * hk, hy - 2 * hk
    if not (lie or nuzzle) and on["brow"]:
        pen.poly(shade(body, -30), [(ex - 3 * hk * es, ey - 2.6 * hk * es), (ex + 2.8 * hk * es, ey - 3.6 * hk * es),
                                    (ex + 3.2 * hk * es, ey - 2.4 * hk * es)], outline=None)   # brow ridge

    # ---- near horn and eye: no scale texture on them ----
    pen.plain = True
    if on["horns"]:
        near_horn = horn_pts((hx - 1 * hk, hy - 5 * hk), (hx - 6 * hk, hy - 14 * hk - hl * 0.4),
                             (hx - 13 * hk - hl * 0.5, hy - 10 * hk - hl))
        pen.tube(horn_col, near_horn, 4.6 * hk * ht, 0.2)      # cream, curved backwards
        shine = [(x + 0.6 * hk, y - 0.9 * hk) for x, y in near_horn[1:9]]         # glossy highlight on the horn
        pen.tube(shade(horn_col, 26), shine, 1.3 * hk * ht, 0.3, outline=None, caps=False)
        hb = [(x - 0.5 * hk, y + 0.7 * hk) for x, y in near_horn[0:5]]             # darker horn base (logo)
        pen.tube(shade(horn_col, -34), hb, 2.4 * hk * ht, 1.0 * hk * ht, outline=None, caps=False)
        if on["horn_rings"]:
            for i in (2, 4, 6, 8, 10):                 # horn ridges (growth rings)
                px, py = near_horn[i]
                a = near_horn[i + 1]
                nx_, ny_ = -(a[1] - py), a[0] - px
                L = math.hypot(nx_, ny_) or 1
                w = (4.6 * hk * ht) * (1 - i / 12) / 2
                pen.line(shade(horn_col, -40), (px - nx_ / L * w, py - ny_ / L * w),
                         (px + nx_ / L * w, py + ny_ / L * w), 0.35)
    eh = hk * es
    if lie or nuzzle:
        pen.arc(cols["outline"], ex, ey - 0.2, 2.2 * eh, 1.2 * eh, 3.4, 6.0, 0.55)
    else:                                          # logo eye: big red iris, dark oval pupil, wet highlight
        pen.ell((236, 226, 222), ex, ey, 5.6 * eh, 4.8 * eh, outline=OUTLINE)
        pen.circle(shade(eye, -70), ex + 0.4 * eh, ey + 0.1 * eh, 2.3 * eh)
        pen.circle(eye[:3], ex + 0.4 * eh, ey + 0.1 * eh, 1.95 * eh)
        pen.circle(shade(eye, 50), ex + 0.3 * eh, ey + 0.8 * eh, 0.9 * eh)    # glow in the lower iris
        pen.ell((18, 4, 10), ex + 0.6 * eh, ey, 1.35 * eh, 2.6 * eh, outline=None)   # oval pupil
        pen.circle((255, 248, 248), ex - 0.3 * eh, ey - 0.9 * eh, 0.6 * eh)   # wet highlights
        pen.circle((255, 248, 248), ex + 1.3 * eh, ey + 0.9 * eh, 0.25 * eh)
        pen.arc(cols["outline"], ex, ey + 0.2 * eh, 3.0 * eh, 2.6 * eh, 0.3, 2.9, 0.55)  # upper lid line
    pen.plain = False
    draw_custom("front")

    # ---- near wing (smooth membrane, as in the logo) ----
    if on["wings"]:
        pen.plain = True
        _wing(pen, sx, sy, wing_state, wing_col, darker, scale=ws)
        pen.plain = False
    draw_custom("top")

    # ---- claw swipe ----
    if pose == "claw":
        swipe = (236, 220, 255) if not obsidian else (150, 70, 190)
        for i in range(3):
            pen.arc(swipe, hx + 8 + i * 1.3, by - 2, 11, 14, -1.2, 1.2, 0.9)

    surf = pen.finish(1)                           # lit + scale texture, not yet flipped
    W, H = surf.get_size()
    x_scr = feet_x - W / 2
    y_scr = feet_y - H + 2
    lit = lights_for_sprite(x_scr, y_scr, W, facing, extra_lights)
    if on["sheen"]:
        apply_sheen(surf, scale_px, lit, t, phase=feet_x * 0.031, plain=pen.m, mask=pen.silhouette,
                    gain=S["shine"])
    if tint:
        surf.fill(tint, special_flags=pygame.BLEND_RGB_ADD)
    if facing < 0:
        surf = pygame.transform.flip(surf, True, False)
    screen.blit(surf, (x_scr, y_scr))
    if info is not None:                           # model units -> screen, for the editor
        def to_screen(x, y):
            px, py = pen.P(x, y)
            px, py = px / pen.ss, py / pen.ss
            return (x_scr + (W - px if facing < 0 else px), y_scr + py)
        info.update(to_screen=to_screen, px_per_unit=k, facing=facing, anchors=dict(anchors),
                    rect=pygame.Rect(int(x_scr), int(y_scr), W, H))


# ---------------------------------------------------------------------------
# Close-up portrait of Shadowra (end of the credits): she looks straight at the player
# ---------------------------------------------------------------------------
PORTRAIT_H = 230                      # model units; origin = bottom centre


def build_portrait(height_px, stage, eye, lid_l=0.0, lid_r=0.0, mouth=0.0, blush=False, fierce=False, design=None):
    """Front view of head, neck and shoulders, drawn large and supersampled.
    lid_l / lid_r: 0 = eye open … 1 = closed. mouth: 0 = closed … 1 = open (talking).
    design: sizes/colours/parts (dragon_design), default: Shadowra's design file. Extra parts from the
    editor are side-view only and are not drawn here."""
    d = design or dragon_design.current()
    S, on = d["sizes"], d["parts"]
    cols = dragon_design.colors(d)
    k = height_px / PORTRAIT_H
    pen = Pen(260, PORTRAIT_H + 40, (130, PORTRAIT_H + 40), k, ss=2)    # headroom for the horn tips
    hk = (1.22, 1.08, 1.0)[stage] * S["head"]     # young ones: bigger eyes and head
    hl = (8, 18, 30)[stage] * S["horn_length"]    # horn length grows with her
    ht, es = S["horn_thickness"], S["eye"]
    pen.oc = cols["outline"] if cols["outline"] != OUTLINE else None
    body = cols["body"]
    dark, darker, belly = shade(body, -24), cols["spikes"], shade(cols["belly"], 4)
    HORN_C, WING_C = cols["horn"], cols["wing"]
    eye = eye[:3]

    # ---- folded wings rising behind the shoulders (smooth membranes) ----
    pen.plain = True
    for s in (-1, 1) if on["wings"] else ():
        root = (s * 50, -46)
        tips = [(s * 118, -168), (s * 128, -112), (s * 112, -58)]
        mem = [root, (s * 70, -132), tips[0]]
        for a, b in ((tips[0], tips[1]), (tips[1], tips[2])):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            mem += bez(a, (mx - s * 9, my), b, 6)[1:]
        mem += [(s * 70, -30)]
        pen.poly(shade(WING_C, -6), mem)
        pen.tube(darker, [root, (s * 70, -132), tips[0]], 7, 3, outline=None, caps=False)
        for tip in tips[1:]:
            pen.tube(darker, [(s * 70, -132), tip], 3.5, 1.2, outline=None)
        pen.poly(shade(HORN_C, -20), [(tips[0][0] - 2, tips[0][1] + 2), (tips[0][0] + s * 3, tips[0][1] - 7),
                                    (tips[0][0] + 2, tips[0][1] + 2)], outline=None)
    pen.plain = False

    # ---- shoulders and chest ----
    pen.ell(body, 0, 0, 210, 96)
    pen.ell(shade(body, 12), 0, -24, 150, 26, outline=None)
    for s in (-1, 1):                              # shoulder muscles
        pen.arc(shade(body, 16), s * 52, -22, 30, 22, 0.4 if s > 0 else 1.6, 2.6 if s > 0 else 2.9, 1.0)
    # ---- neck with belly plates: flares out into the chest ----
    left = bez((-80, 40), (-34, -30), (-30, -125), 14)
    pen.poly(body, left + [(-x, y) for x, y in left[::-1]])
    pen.ell(shade(body, 10), -20, -60, 10, 70, outline=None)                       # soft side light
    pen.plain = True                               # smooth throat plates (logo), no scales
    plate = bez((-40, 40), (-18, -30), (-15, -104), 24)
    if on["throat_plates"]:
        pen.poly(belly, plate + [(-x, y) for x, y in plate[::-1]], outline=None)
    for i in range(12 if on["throat_plates"] else 0):                            # overlapping plates, each lit from above
        y = 34 - i * 12.5
        half = abs(next(x for x, py in plate if py <= y))
        pen.arc(shade(belly, -30), 0, y - 1.5, half * 0.98, 5, 3.4, 6.0, 1.2)
        pen.arc(shade(belly, 14), 0, y - 4.5, half * 0.86, 4, 3.6, 5.8, 0.8)
    pen.plain = False
    for i in range(5 if on["neck_spines"] else 0):  # spikes down the sides of the neck
        y = -50 - i * 13
        for s in (-1, 1):
            x = s * (36 - i * 1.6)
            sp = S["spikes"]
            pen.poly(darker, [(x, y - 4), (x + s * 9 * sp, y - 9 * sp), (x, y + 4)], outline=None)

    # ---- horns: sweep up and out, curling back (smooth, ridged – no scales) ----
    hy = -150
    pen.plain = True
    for s in (-1, 1) if on["horns"] else ():
        horn = bez((s * 22 * hk, hy - 24 * hk), (s * (60 + hl * 0.6), hy - 46 - hl * 0.5),
                   (s * (44 + hl * 0.5), hy - 62 - hl * 1.3), 16)            # crescent, tips curl inwards
        col = HORN_C if s > 0 else shade(HORN_C, -14)
        pen.tube(col, horn, 13 * hk * ht, 0.6)
        shine = [(x - s * 1.2, y - 1.4) for x, y in horn[1:11]]
        pen.tube(shade(col, 24), shine, 3.2, 0.6, outline=None, caps=False)
        for i in (3, 6, 9, 12) if on["horn_rings"] else ():   # growth rings
            px, py = horn[i]
            qx, qy = horn[i + 1]
            nx, ny = -(qy - py), qx - px
            L = math.hypot(nx, ny) or 1
            w = 13 * hk * ht * (1 - i / 16) / 2
            pen.line(shade(col, -40), (px - nx / L * w, py - ny / L * w), (px + nx / L * w, py + ny / L * w), 0.9)
    pen.plain = False

    # ---- cheek frills ----
    for s in (-1, 1) if on["ear_frills"] else ():
        for i, (fy, out) in enumerate(((-6, 30), (6, 34), (18, 26))):
            out *= S["frills"]
            base = hy + fy * hk
            pen.poly(dark, [(s * 34 * hk, base - 7), (s * (34 + out) * hk, base - 2 + i * 4),
                            (s * 32 * hk, base + 7)])

    # ---- head: skull, cheeks, snout ----
    pen.ell(body, 0, hy - 4 * hk, 82 * hk, 66 * hk)
    pen.ell(body, 0, hy + 14 * hk, 74 * hk, 46 * hk, outline=None)
    pen.ell(shade(body, 14), 0, hy - 22 * hk, 44 * hk, 16 * hk, outline=None)        # forehead light
    for i in range(3):                                                             # small head scales
        pen.arc(dark, (i - 1) * 10 * hk, hy - 24 * hk, 5 * hk, 3.5 * hk, 3.4, 6.0, 0.8)
    sy = hy + 30 * hk                                                              # snout
    pen.ell(body, 0, sy, 52 * hk * S["snout"], 36 * hk)
    pen.ell(shade(body, 16), 0, sy - 8 * hk, 30 * hk, 12 * hk, outline=None)
    pen.line(shade(body, 22), (0, hy - 8 * hk), (0, sy - 10 * hk), 1.2)              # ridge highlight
    for s in (-1, 1):                                                              # nostrils
        pen.ell(OUTLINE, s * 8 * hk, sy - 1 * hk, 5 * hk, 3 * hk, outline=None)
        pen.ell(shade(body, -10), s * 8 * hk, sy - 2.2 * hk, 4 * hk, 1.4 * hk, outline=None)
    if blush:                                                                      # she likes the player
        for s in (-1, 1):
            pen.ell((150, 70, 120), s * 28 * hk, hy + 16 * hk, 15 * hk, 7 * hk, outline=None)
            pen.ell((175, 92, 140), s * 28 * hk, hy + 15 * hk, 9 * hk, 3.5 * hk, outline=None)
    # mouth: a little smile with two fangs – open when she talks
    my = sy + 13 * hk
    if mouth > 0.05:
        pen.ell((40, 10, 40), 0, my + 2 * mouth * hk, 22 * hk, (4 + 9 * mouth) * hk)
        pen.ell((150, 60, 90), 0, my + 5 * mouth * hk, 12 * hk, 4 * mouth * hk, outline=None)   # tongue
    else:
        pen.arc(OUTLINE, 0, my - 7 * hk, 13 * hk, 8 * hk, 3.6, 5.8, 1.1)
    for s in (-1, 1) if on["fangs"] else ():
        fx = s * 7 * hk
        pen.poly((246, 240, 228), [(fx - 1.6 * hk, my - 0.6 * hk), (fx + 1.6 * hk, my - 0.6 * hk),
                                   (fx, my + 4.5 * hk)], outline=None)

    # ---- eyes with brows and lids (no scale texture on the eyes) ----
    for s, lid in ((-1, lid_l), (1, lid_r)):
        ex, ey = s * 21 * hk, hy + 1 * hk
        ek = hk * es                                   # eye size from the design
        a, b = 11.5 * ek, 9 * ek
        pen.plain = True
        pen.ell((250, 242, 238), ex, ey, 2 * a, 2 * b)
        pen.circle(shade(eye, -70), ex - s * 0.6, ey + 0.4, 7.4 * ek)
        pen.circle(eye, ex - s * 0.6, ey + 0.4, 6.4 * ek)
        pen.circle(shade(eye, 60), ex - s * 0.6, ey + 3.2 * ek, 3.4 * ek)           # glow low in the iris
        for i in range(8):                                                         # iris fibres
            ang = i * math.pi / 4
            pen.line(shade(eye, -35), (ex - s * 0.6 + math.cos(ang) * 3.2 * ek, ey + 0.4 + math.sin(ang) * 3.2 * ek),
                     (ex - s * 0.6 + math.cos(ang) * 6 * ek, ey + 0.4 + math.sin(ang) * 6 * ek), 0.35)
        pen.ell((18, 4, 10), ex - s * 0.6, ey + 0.4, 3 * ek, 11 * ek, outline=None)  # slit pupil
        pen.circle((255, 250, 250), ex - 3 * ek, ey - 3.6 * ek, 2.2 * ek)          # wet highlights
        pen.circle((255, 250, 250), ex + 3 * ek, ey + 3.4 * ek, 0.9 * ek)
        pen.plain = False
        if lid > 0.02:                                                             # eyelid comes down
            top = [(ex + (a + 1.2) * math.cos(f), ey - (b + 1.2) * math.sin(f))
                   for f in [i * math.pi / 14 for i in range(15)]]                  # right → left over the top
            edge = []
            for i in range(15):
                u = -1 + 2 * i / 14
                x = ex + u * (a + 1.2)
                y = ey - b + lid * 2 * b + lid * b * 0.45 * (1 - u * u)
                y = min(y, ey + (b + 1.2) * math.sqrt(max(0.0, 1 - u * u)))
                edge.append((x, y))
            pen.poly(shade(body, 8), top + edge, outline=None)
            pen.tube(OUTLINE, edge[1:-1], 1.6, 1.6, outline=None)                  # lash line
            if lid > 0.9:                                                          # little lashes
                for u in (-0.5, 0.0, 0.5):
                    i = int((u + 1) * 7)
                    x, y = edge[i]
                    pen.line(OUTLINE, (x, y), (x + u * 3 * ek + s * 1.5, y + 3 * ek), 0.7)
        if fierce:
            brow = [(ex - s * 14 * ek, ey - 10 * ek), (ex, ey - 15 * ek), (ex + s * 13 * ek, ey - 12 * ek)]
        else:                                     # soft, friendly brows: higher on the inside
            brow = [(ex - s * 13 * ek, ey - 16 * ek), (ex, ey - 17 * ek), (ex + s * 13 * ek, ey - 12 * ek)]
        pen.tube(darker, brow, 4.5 * ek, 2.5 * ek, outline=None)

    size = (max(1, pen.W // pen.ss), max(1, pen.H // pen.ss))
    s = pygame.transform.smoothscale(pen.s, size)
    scale_px = max(6, round(8 * k))               # big, clearly visible scales up close (as in the logo)
    scale_px = max(6, round(scale_px * S["scales"]))
    silhouette = light_model(s, 2, ("scales", scale_px) if on["scales"] else None, pen.m)
    w, h = s.get_size()
    key_light = [(w * 0.12, h * 0.18, h * 0.5, (255, 232, 196), 1.0),     # soft warm key light, upper left
                 (w * 0.95, h * 0.55, h * 0.3, (170, 140, 255), 0.5)]     # faint violet bounce, right
    if on["sheen"]:
        apply_sheen(s, scale_px, key_light, t=0.6, plain=pen.m, mask=silhouette, gain=S["shine"])
    return s


# ---------------------------------------------------------------------------
# Elves
# ---------------------------------------------------------------------------
ELF_STYLE = {
    "Sera": dict(hair=(196, 86, 52), cloth=(44, 92, 62), trim=(170, 200, 120), skin=(236, 214, 196),
                 boots=(70, 50, 36), eyes=(40, 110, 60), hair_style="ponytail", outfit="ranger", weapon="bow",
                 gender="f"),
    "Erila": dict(hair=(228, 228, 242), cloth=(52, 62, 124), trim=(180, 200, 245), skin=(234, 222, 216),
                  boots=(50, 50, 80), eyes=(80, 110, 190), hair_style="long", outfit="robe", weapon="staff",
                  gender="f"),
}


def draw_elf(screen, feet_x, feet_y, facing, name, pose, t, flash=False, style=None, blush=False):
    """Any elf: Sera, Erila or a villager (style from texts.VILLAGERS). Men are broader with short hair,
    women have long hair styles; outfits: ranger, robe, dress, tunic, vest."""
    st = dict(style or ELF_STYLE[name])
    male = st.get("gender", "f") == "m"
    hs, outfit, weapon = st.get("hair_style", "long"), st.get("outfit", "tunic"), st.get("weapon")
    pen = Pen(70, 82, (35, 79), 1.0)
    pen.texture = "cloth"
    sway = math.sin(t * 2) * 0.8 if pose == "idle" else 0
    step = math.sin(t * 10) * 3 if pose == "walk" else 0
    hair, cloth, skin = st["hair"], st["cloth"], st["skin"]
    sh = 7.5 if male else 6.5                                   # shoulder half-width
    hy = -43 + sway

    # hair behind the body
    if hs == "ponytail":
        pen.tube(hair, bez((-2, hy - 3), (-12, hy - 1), (-14, hy + 13 + sway), 10), 6, 1.5)
    elif hs == "long":
        pen.poly(shade(hair, -18), [(-5, hy - 4), (-9, hy + 19), (-6, hy + 23), (-1, hy + 19), (3, hy - 3)])
    elif hs == "braid":
        pen.tube(shade(hair, -10), bez((-4, hy), (-9, hy + 10), (-7, hy + 20), 10), 3.6, 2.2)
        pen.circle(st["trim"], -7, hy + 20.5, 1.2, outline=OUTLINE)
    elif hs == "elder":
        pen.poly(shade(hair, -15), [(-5, hy - 4), (-8, hy + 12), (-3, hy + 10), (2, hy - 3)])
    # legs and boots
    leg_col = shade(cloth, -30) if outfit in ("ranger", "tunic", "vest") else shade(cloth, -10)
    for sgn, ph in ((-1, step), (1, -step)):
        hip = (sgn * (3 if male else 2.6), -20)
        foot = (sgn * 3 + ph, -1)
        pen.tube(leg_col, [hip, foot], 3.8 if male else 3.6, 3)
        pen.ell(st["boots"], foot[0] + 1.2, -1.2, 5.5, 3)
    # clothes
    if outfit == "fur":                                         # humans in the snow: a warm fur coat
        pen.poly(cloth, [(-sh - 1, -37), (sh + 1, -37), (sh + 3, -15), (-sh - 3, -15)])
        pen.ell(st["trim"], 0, -36.5, sh * 2 + 5, 6, outline=OUTLINE)        # fur collar
        for i in range(5):                                      # fur hem
            pen.circle(st["trim"], -sh - 2 + i * (sh + 2) / 2, -15.5, 1.8, outline=None)
        pen.line(shade(cloth, -25), (0, -34), (0, -16), 0.8)
    elif outfit in ("ranger", "tunic", "vest"):
        pen.poly(cloth, [(-sh, -37), (sh, -37), (sh + 2, -18), (-sh - 2, -18)])
        if outfit == "ranger":
            cape = bez((-6, -37), (-12, -28 + math.sin(t * 2) * 1.5), (-11, -14), 8)
            pen.poly(shade(cloth, -18), [(-6, -37)] + cape + [(-5, -18)])
            pen.line((110, 75, 40), (-6, -35), (6, -22), 1.0)           # quiver strap
        if outfit == "vest":
            pen.poly(shade(cloth, -28), [(-sh, -37), (-2, -37), (-3, -19), (-sh - 2, -19)])
            pen.poly(shade(cloth, -28), [(sh, -37), (2, -37), (3, -19), (sh + 2, -19)])
        pen.line(st["trim"], (-sh - 1.5, -19), (sh + 1.5, -19), 0.9)
    else:                                                       # robe / dress: long and flowing
        hem_y = 0 if outfit == "robe" else -5
        flare = 12 if outfit == "robe" else 11 + math.sin(t * 2) * 0.8
        body = [(-sh, -37), (sh, -37)] + bez((sh + 0.5, -30), (flare - 1, -12), (flare, hem_y), 6) + \
               bez((-flare, hem_y), (-flare + 1, -12), (-sh - 0.5, -30), 6)
        pen.poly(cloth, body)
        pen.line(shade(cloth, 25), (0, -34), (0, hem_y - 2), 0.7)
        pen.line(st["trim"], (-flare + 0.5, hem_y - 1), (flare - 0.5, hem_y - 1), 1.0)
    pen.line(st["trim"], (-sh, -27), (sh, -27), 1.1)               # belt
    # arm
    arm_end = (10, -31) if weapon == "bow" else (9, -30)
    if pose == "shoot":
        arm_end = (12, -36)
    pen.tube(shade(cloth, 10), [(3, -35), arm_end], 3.4 if male else 3.2, 2.4)
    pen.circle(skin, *arm_end, 1.4, outline=OUTLINE)
    # head, ears, face
    pen.circle(skin, 0, hy, 6.2, outline=OUTLINE)
    if st.get("human"):
        pen.ell(skin, 3.6, hy + 0.6, 2.4, 3.4)                                          # small round human ear
    else:
        pen.poly(skin, [(3.5, hy - 1), (15, hy - 6.5), (4.5, hy + 2)])                # long elf ear
    if hs == "short":
        pen.poly(hair, [(-6.5, hy + 1)] + bez((-6.5, hy - 6.5), (0, hy - 8.8), (6.8, hy - 3.5), 8) +
                 [(4, hy - 3), (1, hy - 5), (-3, hy - 3)])
    else:
        pen.poly(hair, [(-6.5, hy - 1)] + bez((-6, hy - 6.5), (0, hy - 8.5), (6.8, hy - 3), 8) + [(5, hy - 2.5), (-2, hy - 4)])
    if hs == "long":
        pen.poly(hair, [(-6.5, hy - 1), (-5.5, hy + 7), (-3, hy + 5), (-3.5, hy - 3)])
    if hs == "bun":
        pen.circle(shade(hair, -8), -5.5, hy - 5, 3.2, outline=OUTLINE)
    if hs == "elder":
        pen.line(st["trim"], (-6, hy - 3.5), (6.3, hy - 4.2), 0.8)                      # headband
    if blush:                                                   # red cheeks!
        pen.ell((240, 120, 140), 3.4, hy + 2.2, 3.4, 1.8, outline=None)
    pen.circle(st["eyes"], 3.3, hy - 0.4, 0.95)
    pen.circle((255, 255, 255), 3.0, hy - 0.8, 0.35)
    if blush:
        pen.arc(shade(skin, -70), 4.6, hy + 3.2, 1.2, 0.8, 0.2, 2.9, 0.35)             # embarrassed smile
    else:
        pen.line(shade(skin, -60), (4.2, hy + 3), (5.6, hy + 2.6), 0.4)                 # mouth
    # weapon
    if weapon == "bow":
        pull = 4 if pose == "shoot" else 0
        bow = bez((11, -51), (19, -34), (11, -17), 12)
        pen.tube((126, 84, 44), bow, 1.6, 1.6, outline=OUTLINE)
        pen.line((230, 228, 210), (11 - pull, -51), (11 - pull * 0.2 - pull, -34), 0.35)
        pen.line((230, 228, 210), (11 - pull, -34), (11, -17), 0.35)
        if pose == "shoot":
            pen.line((150, 120, 80), (7 - pull, -34), (22, -34), 0.6)
    elif weapon == "spear":                                     # hunters in the snow
        thrust = 7 if pose == "shoot" else 0
        pen.tube((120, 88, 56), [(6 + thrust, -6), (12 + thrust, -58)], 1.5, 1.3, outline=OUTLINE)
        tip = (12.6 + thrust, -58)
        pen.poly((205, 210, 218), [(tip[0] - 2, tip[1] + 1), (tip[0] + 0.6, tip[1] - 7), (tip[0] + 2.4, tip[1] + 1)])
    elif weapon == "staff":
        pen.tube((116, 92, 70), [(9, 0), (9, -54)], 1.6, 1.4, outline=OUTLINE)
        pen.circle((210, 230, 255), 9, -56.5, 2.6 if pose == "cast" else 2.0, outline=OUTLINE)

    surf = pen.finish(facing, flash=flash)
    if pose == "dead":
        surf = pygame.transform.rotate(surf, 90 if facing > 0 else -90)
        screen.blit(surf, (feet_x - surf.get_width() / 2, feet_y - surf.get_height() + 22))
        return
    screen.blit(surf, (feet_x - surf.get_width() / 2, feet_y - surf.get_height() + 2))
    if weapon == "staff" and name == "Erila":                  # soft moonlight on her staff (harmless)
        ox = feet_x + (9 if facing > 0 else -9)
        glow(screen, int(ox), int(feet_y - 56), 22 if pose == "cast" else 14, (170, 205, 255), 90)


# ---------------------------------------------------------------------------
# Small creatures – cached per animation frame (they are drawn many times)
# ---------------------------------------------------------------------------
_cache = {}


def _cached(key, build):
    surf = _cache.get(key)
    if surf is None:
        if len(_cache) > 600:
            _cache.clear()
        surf = _cache[key] = build()
    return surf


def _moss_runner(frame, moving, fleeing):
    pen = Pen(66, 54, (32, 52), 1.0)
    pen.texture = "fur"
    fur, dark, moss = (100, 112, 88), (70, 80, 62), (126, 156, 96)
    ph = frame / 8 * math.tau
    for i, lx in enumerate((-15, 9, -10, 14)):              # far legs first, then near legs
        sw = math.sin(ph + i * 1.6) * (5 if fleeing else 3) if moving else 0
        col = dark if i < 2 else fur
        pen.tube(col, bez((lx, -16), (lx + sw * 0.4 - 1, -9), (lx + sw, -1.5), 6), 4.2, 2.2)
        pen.ell((40, 36, 30), lx + sw + 0.6, -1, 3.4, 2)    # hooves
    pen.tube(fur, bez((-19, -20), (-24, -24), (-26, -19), 6), 3.4, 1.6)   # tail tuft
    pen.ell(fur, -2, -20, 38, 16)
    pen.ell(shade(fur, 18), -2, -16, 26, 6, outline=None)
    for i, (mx, my, r) in enumerate(((-12, -27, 4.2), (-5, -28.5, 4.8), (3, -28, 4.4), (10, -26, 3.6),
                                     (-8, -25, 3.4), (6, -25, 3.2))):
        pen.circle(shade(moss, (i % 3) * 8), mx, my, r, outline=None if i > 3 else OUTLINE)
    pen.tube(fur, bez((14, -22), (19, -28), (22, -33), 6), 8, 6)            # neck
    pen.ell(fur, 25, -35, 14, 10)
    pen.ell(shade(fur, -20), 31, -33.5, 5, 4, outline=None)                 # muzzle
    for side, off in ((-1, 0), (1, 2)):
        pen.poly(dark, [(21 + off, -39), (18 + off, -45), (24 + off, -40)])  # ears
    for ax in (22, 26):                                                       # little antlers
        pen.tube((196, 184, 150), bez((ax, -39), (ax - 2, -46), (ax - 5, -49), 6), 1.6, 0.5)
    pen.circle((20, 20, 20), 27.5, -36, 1.3)
    pen.circle((255, 255, 255), 27.1, -36.5, 0.4)
    return pen


def draw_moss_runner(screen, feet_cx, feet_y, facing, t, moving, fleeing, flash, alpha, dead):
    frame = int(t * (14 if fleeing else 7)) % 8 if moving else 0
    key = ("moss", frame, moving, fleeing)
    pen = _cached(key, lambda: _moss_runner(frame, moving, fleeing))
    surf = pen.finish(facing, flash=flash) if flash else _cached(key + (facing,), lambda: pen.finish(facing))
    if dead:
        surf = pygame.transform.flip(surf, False, True)
    if alpha < 255:
        surf = surf.copy()
        surf.set_alpha(alpha)
    screen.blit(surf, (feet_cx - surf.get_width() / 2, feet_y - surf.get_height() + (14 if dead else 2)))


def _fish():
    pen = Pen(34, 18, (17, 9), 1.0)
    pen.texture = "scales"
    top = bez((-9, 0), (0, -8), (11, -0.5), 10)
    bottom = bez((11, 0.5), (0, 7), (-9, 0), 10)
    pen.poly((156, 176, 206), top + bottom)
    pen.poly((116, 136, 176), [(-8.5, 0), (-15, -6), (-13, 0), (-15, 6)])   # tail fin
    pen.poly((130, 150, 186), [(-2, -5), (3, -9), (5, -4.2)])              # dorsal fin
    pen.ell((205, 220, 235), 1, 2, 14, 4, outline=None)                    # pale belly
    for i in range(4):
        pen.arc((120, 140, 175), -4 + i * 3, -1, 1.6, 2.4, -1.2, 1.2, 0.3)
    pen.circle((15, 15, 25), 7.5, -1.2, 1.1)
    pen.circle((255, 255, 255), 7.2, -1.6, 0.35)
    return pen


def draw_fish(screen, cx, cy, facing):
    surf = _cached(("fish", facing), lambda: _fish().finish(facing))
    screen.blit(surf, (cx - surf.get_width() / 2, cy - surf.get_height() / 2))


def _owl(blink):
    pen = Pen(48, 56, (24, 54), 1.0)
    pen.texture = "feathers"
    brown, light, dark = (112, 82, 60), (170, 138, 104), (78, 56, 40)
    pen.line((70, 48, 34), (-22, -1), (22, -1), 3.4)                        # branch
    pen.ell(brown, 0, -18, 26, 32)
    pen.ell(light, 0, -14, 16, 20, outline=None)
    for row in range(3):                                                    # chest feathers
        for c in range(3):
            pen.arc(dark, -4.5 + c * 4.5 + (row % 2) * 2, -20 + row * 4.5, 1.8, 1.4, 3.4, 6.0, 0.4)
    for side in (-1, 1):                                                    # wings
        pen.poly(dark, [(side * 11, -28), (side * 14, -16), (side * 11, -5), (side * 8, -16)])
    pen.ell(brown, 0, -36, 24, 19)
    pen.ell(light, 0, -35, 18, 13, outline=None)                            # face disc
    for side in (-1, 1):
        pen.poly(dark, [(side * 6, -43), (side * 10, -51), (side * 10.5, -42)])   # ear tufts
        if blink:
            pen.line(OUTLINE, (side * 4.5 - 2.5, -36), (side * 4.5 + 2.5, -36), 0.6)
        else:
            pen.circle((246, 204, 84), side * 4.5, -36, 3.3, outline=OUTLINE)
            pen.circle((20, 10, 10), side * 4.5, -36, 1.6)
            pen.circle((255, 255, 240), side * 4.5 - 0.7, -36.8, 0.5)
    pen.poly((224, 172, 64), [(-1.6, -33), (1.6, -33), (0, -29)])           # beak
    for side in (-1, 1):
        pen.line((224, 172, 64), (side * 3, -3), (side * 3, -1), 0.8)       # talons
    return pen


def draw_owl(screen, feet_cx, feet_y, t, flash, alpha):
    blink = int(t * 1.3) % 6 == 0 and (t * 1.3) % 1 < 0.2
    key = ("owl", blink)
    pen = _cached(key, lambda: _owl(blink))
    surf = pen.finish(1, flash=True) if flash else _cached(key + ("s",), lambda: pen.finish(1))
    if alpha < 255:
        surf = surf.copy()
        surf.set_alpha(alpha)
    screen.blit(surf, (feet_cx - surf.get_width() / 2, feet_y - surf.get_height() + 4))


# ---------------------------------------------------------------------------
# Enemies – high-resolution models replacing the 16x16 pixel sprites
# (cached per animation frame; facing / hit-flash are applied when finishing)
# ---------------------------------------------------------------------------
def _flame(pen, x, y, h, w, frame, cols=((255, 120, 30), (255, 200, 80), (255, 246, 210)), lean=0.0):
    """Layered flickering flame rising from (x, y)."""
    fl = math.sin(frame * 1.7) * 0.18 + math.sin(frame * 3.1) * 0.08
    for i, c in enumerate(cols):
        k = 1.0 - i * 0.3
        hh, ww = h * k * (1 + fl), w * k
        tip = (x + lean * hh + math.sin(frame * 2.3 + i) * ww * 0.25, y - hh)
        pts = [(x - ww / 2, y)] + bez((x - ww * 0.6, y - hh * 0.45), (x - ww * 0.2, y - hh * 0.8), tip, 5) + \
              bez(tip, (x + ww * 0.3, y - hh * 0.75), (x + ww * 0.6, y - hh * 0.4), 5) + [(x + ww / 2, y)]
        pen.poly(c, pts, outline=None)


def _skeleton(frame, moving):
    pen = Pen(48, 52, (22, 50), 1.0)
    pen.texture = "bone"
    bone, shade_c, dark = (234, 228, 208), (172, 162, 140), (70, 58, 50)
    sw = math.sin(frame / 8 * math.tau) * 5 if moving else 0
    for sgn, s, col in ((-1, -sw, shade_c), (1, sw, bone)):           # legs (far one darker)
        hip, foot = (sgn * 2.2, -20), (sgn * 2.5 + s, -1.2)
        knee = ((hip[0] + foot[0]) / 2 + 1.5, -10.5)
        pen.tube(col, bez(hip, knee, foot, 6), 2.6, 2.0)
        pen.circle(col, *knee, 1.6, outline=OUTLINE)
        pen.ell(col, foot[0] + 1.6, -0.9, 5.5, 2.4)
    pen.tube(shade_c, bez((-1, -34), (-6, -27), (-4, -21), 6), 2.2, 1.8)   # far arm
    pen.ell(bone, 0, -21, 11, 4.5)                                     # pelvis
    for i in range(6):                                                 # spine
        pen.circle(shade_c, 0, -23 - i * 2.4, 1.1, outline=OUTLINE)
    for i in range(4):                                                 # ribcage
        pen.arc(bone, 1.2, -33 + i * 2.6, 6.2 - i * 0.6, 2.2, 0, math.tau, 0.9)
    pen.ell(bone, 0.5, -36, 13, 3.4)                                   # collar bones
    hx, hy = 2, -42
    pen.circle(bone, hx, hy, 6.4, outline=OUTLINE)                     # skull
    pen.poly(bone, [(hx - 2.5, hy + 3.5), (hx + 6, hy + 3.2), (hx + 5.5, hy + 7), (hx - 1, hy + 7)])  # jaw
    for i in range(4):
        pen.line(dark, (hx + i * 1.7 - 1, hy + 4.2), (hx + i * 1.7 - 1, hy + 6), 0.35)
    for ex, r in ((hx + 3.4, 1.8), (hx - 0.4, 1.5)):                   # sockets with red sparks
        pen.circle((20, 10, 14), ex, hy - 0.8, r)
        pen.circle((240, 70, 60), ex + 0.2, hy - 0.8, 0.55)
    pen.poly((30, 20, 24), [(hx + 5.2, hy + 1.4), (hx + 6.4, hy + 2.8), (hx + 4.6, hy + 2.8)], outline=None)
    hand = (10, -26 + sw * 0.2)
    pen.tube(bone, bez((2.5, -34), (7, -30), hand, 6), 2.3, 1.8)       # near arm + rusty sword
    blade = [(hand[0] - 0.6, hand[1] - 0.6), (hand[0] + 13, hand[1] - 11), (hand[0] + 14.5, hand[1] - 12.5),
             (hand[0] + 13.5, hand[1] - 9.5), (hand[0] + 0.8, hand[1] + 0.8)]
    pen.poly((176, 170, 166), blade)
    pen.line((140, 92, 60), (hand[0] + 4, hand[1] - 3.2), (hand[0] + 10, hand[1] - 8), 0.6)     # rust
    pen.line((120, 84, 50), (hand[0] - 2.5, hand[1] + 1.2), (hand[0] + 2, hand[1] - 3), 1.1)    # cross guard
    return pen


def _skull(frame):
    pen = Pen(50, 40, (26, 38), 1.0)
    pen.texture = "bone"
    for i, c in enumerate(((40, 110, 220), (90, 180, 255), (210, 240, 255))):   # blue flame trail
        k = 1 - i * 0.3
        fl = math.sin(frame * 1.9 + i) * 2.5
        tip = (-22 * k + fl, -24 - fl * 0.5)
        pts = [(0, -30 * k + 2)] + bez((-8, -32), (-16, -30 + fl), tip, 6) + \
              bez(tip, (-14, -14 - fl), (-2, -8), 6)
        pen.poly(c, pts, outline=None)
    cx, cy = 2, -18
    pen.circle((236, 230, 214), cx, cy, 10.5, outline=OUTLINE)
    pen.ell((236, 230, 214), cx + 3, cy + 7.5, 12, 6)                       # jaw
    for i in range(5):
        pen.line((80, 70, 70), (cx - 2 + i * 2.2, cy + 5.5), (cx - 2 + i * 2.2, cy + 9.5), 0.4)
    glow = 1.2 + 0.5 * math.sin(frame * 2)
    for ex in (cx + 4.8, cx - 1.5):
        pen.circle((16, 14, 30), ex, cy - 1.5, 3)
        pen.circle((150, 210, 255), ex + 0.4, cy - 1.5, glow)
    pen.poly((40, 30, 40), [(cx + 7.8, cy + 2.5), (cx + 9.6, cy + 4.6), (cx + 6.6, cy + 4.6)], outline=None)
    pen.arc((190, 180, 160), cx - 2, cy - 5, 4, 3, 0.4, 2.4, 0.4)          # a crack
    return pen


def _priest(frame):
    pen = Pen(50, 58, (22, 56), 1.0)
    pen.texture = "cloth"
    robe, trim, hood = (236, 228, 206), (214, 176, 80), (222, 212, 188)
    sway = math.sin(frame / 8 * math.tau) * 0.8
    hem = bez((-10, 0), (0, 1.5 + sway), (10, 0), 8)
    pen.poly(robe, [(-5, -34)] + hem[::-1][::-1] + [(5.5, -34)])
    pen.poly(shade(robe, -22), [(-5, -34), (-10, 0), (-6, 0), (-2, -30)], outline=None)       # fold shadow
    pen.line(trim, (-9.6, -1.2), (9.6, -1.2), 1.1)
    pen.line(trim, (0.5, -33), (0.5, -2), 0.8)
    pen.line(trim, (-4.6, -24), (5.2, -24), 1.2)                       # sash
    pen.circle(hood, 0.5, -38, 6.2, outline=OUTLINE)                   # hood with a shadowed face
    pen.poly(hood, [(-5.5, -38), (-7, -30), (-3, -33)])
    pen.ell((40, 30, 30), 2.2, -37.5, 7.5, 6.8, outline=None)
    for ex in (1.4, 4.0):
        pen.circle((255, 230, 140), ex, -38, 0.7)
    pen.tube(robe, bez((3, -31), (7, -30), (9.5, -33), 6), 3.2, 2.6)   # arm raising the torch
    pen.circle((236, 214, 196), 9.5, -33.5, 1.4, outline=OUTLINE)
    pen.tube((112, 80, 50), [(9, -30), (12, -44)], 1.4, 1.8)           # torch
    pen.tube((80, 60, 44), [(11.6, -43), (12.4, -45.5)], 2.6, 2.6)
    _flame(pen, 12.2, -45, 9, 6, frame)
    return pen


def _vampire(frame, moving):
    pen = Pen(54, 58, (26, 56), 1.0)
    pen.texture = "cloth"
    sw = math.sin(frame / 8 * math.tau) * 4.5 if moving else 0
    flutter = math.sin(frame / 8 * math.tau * 2) * 1.5
    cape = [(-3, -36), (-14 + flutter, -14), (-17 + flutter, -2), (-10, -5 + flutter * 0.5), (-6, -1), (2, -30)]
    pen.poly((24, 16, 28), cape)                                       # cape outside
    pen.poly((150, 20, 40), [(-3, -34), (-12 + flutter, -14), (-10, -6), (-5, -3), (0, -28)], outline=None)
    for sgn, s in ((-1, -sw), (1, sw)):                                 # legs and boots
        pen.tube((40, 30, 42), [(sgn * 2.2, -19), (sgn * 2.4 + s, -1.5)], 3.4, 2.8)
        pen.ell((20, 14, 20), sgn * 2.4 + s + 1.4, -1, 5.5, 2.6)
    pen.poly((110, 20, 34), [(-5, -35), (5.5, -35), (4.5, -18), (-4.5, -18)])   # vest
    pen.line((200, 170, 90), (0.3, -34), (0.3, -19), 0.5)
    pen.poly((24, 16, 28), [(-6, -36), (-8, -44), (-3, -38), (3, -38), (7, -45), (6, -36)])  # high collar
    hx, hy = 1.5, -41
    pen.ell((228, 216, 222), hx, hy, 10.5, 12)                         # pale face
    pen.poly((18, 12, 20), [(hx - 5.6, hy), (hx - 4, hy - 6.8), (hx + 3, hy - 7.2), (hx + 5.6, hy - 3),
                            (hx + 1, hy - 4.6), (hx - 2, hy - 2)])     # slick hair, widow's peak
    pen.poly((228, 216, 222), [(hx - 4.5, hy - 1), (hx - 9, hy - 4.5), (hx - 4.5, hy + 1.5)])   # pointed ear
    pen.circle((255, 40, 50), hx + 2.8, hy - 0.6, 1.0)
    pen.circle((255, 200, 200), hx + 2.6, hy - 0.9, 0.3)
    pen.line((120, 40, 60), (hx + 1.5, hy + 3.2), (hx + 4.8, hy + 3), 0.4)
    for fx in (hx + 2.2, hx + 3.8):                                     # fangs
        pen.poly((255, 255, 255), [(fx - 0.5, hy + 3.1), (fx + 0.5, hy + 3.1), (fx, hy + 4.6)], outline=None)
    hand = (10, -27 + sw * 0.2)
    pen.tube((110, 20, 34), bez((3, -33), (7, -31), hand, 6), 3, 2.4)
    for i in range(3):                                                 # claws
        pen.line((228, 216, 222), (hand[0], hand[1] + i * 0.7 - 0.7), (hand[0] + 3, hand[1] + i * 1.1 - 1.2), 0.45)
    return pen


def _mafor(frame, defeated):
    pen = Pen(120, 156, (60, 152), 1.0)
    pen.texture = "cloth"
    gold, white, robe = (236, 196, 90), (252, 248, 236), (240, 228, 190)
    ph = frame / 12 * math.tau
    cy = 14 if defeated else 0                                         # kneels when defeated
    head = (0, -112 + cy)
    if not defeated:                                                   # crown of sun rays, slowly turning
        for i in range(12):
            a = ph * 0.15 + i * math.tau / 12
            r0, r1 = 13, 26 + (5 if i % 2 else 0)
            p0 = (head[0] + math.cos(a) * r0, head[1] + math.sin(a) * r0)
            p1 = (head[0] + math.cos(a) * r1, head[1] + math.sin(a) * r1)
            pen.tube(gold if i % 2 else (255, 232, 150), [p0, p1], 3.4, 0.4, outline=None)
        pen.arc((255, 236, 170), head[0], head[1], 16, 16, 0, math.tau, 1.2)       # halo
    hem_y = 0 if not defeated else -2
    wave = math.sin(ph) * 2.5
    hem = bez((-40, hem_y + wave), (0, hem_y - 6 - wave), (40, hem_y + wave), 12)
    pen.poly(robe, [(-18, -96 + cy)] + hem + [(18, -96 + cy)])        # outer mantle
    pen.poly(white, [(-9, -94 + cy), (-20, hem_y - 2), (20, hem_y - 2), (9, -94 + cy)])   # inner robe
    for x in (-20, 20):
        pen.line(gold, (x * 0.45, -94 + cy), (x, hem_y - 2), 1.4)
    pen.line(gold, (-38, hem_y + wave - 1.5), (38, hem_y + wave - 1.5), 2)
    pen.line(gold, (-12, -66 + cy), (12, -66 + cy), 2.6)              # belt with a sun clasp
    pen.circle((255, 226, 120), 0, -66 + cy, 3.4, outline=OUTLINE)
    pen.poly(robe, [(-18, -96 + cy), (-26, -84 + cy), (26, -84 + cy), (18, -96 + cy)])   # shoulders
    # arm with the sun staff
    staff_top = (30, -132 + cy) if not defeated else (34, -96 + cy)
    pen.tube(robe, bez((17, -92 + cy), (26, -88 + cy), (28, -100 + cy), 8), 7, 5.5)
    pen.tube((150, 116, 60), [(28, -60 + cy), staff_top], 2.6, 2.2)
    orb = (staff_top[0], staff_top[1] - 4)
    pen.circle((255, 236, 160), *orb, 6 + math.sin(ph * 2) * 0.8, outline=(180, 130, 40))
    pen.circle(white, orb[0] - 1.5, orb[1] - 1.5, 2)
    pen.circle((236, 214, 196), 28, -100 + cy, 3, outline=OUTLINE)    # hand
    # other arm: open palm full of light
    pen.tube(robe, bez((-17, -92 + cy), (-28, -80 + cy), (-30, -70 + cy), 8), 7, 5.5)
    pen.circle((236, 214, 196), -30, -69 + cy, 3, outline=OUTLINE)
    if not defeated:
        pen.circle((255, 246, 200), -31, -74 + cy, 3.5 + math.sin(ph * 3), outline=None)
    # golden mask
    pen.ell(gold, head[0], head[1], 20, 24)
    pen.ell((255, 222, 130), head[0] - 2, head[1] - 4, 10, 8, outline=None)
    for ex in (-4.5, 4.5):
        pen.poly((40, 26, 20), [(ex - 3, head[1] - 1), (ex + 3, head[1] - 2), (ex + 2, head[1] + 1), (ex - 3, head[1] + 1)])
        pen.circle((255, 255, 240) if not defeated else (120, 100, 80), ex, head[1] - 0.4, 0.9)
    pen.line((150, 110, 40), (-3, head[1] + 7), (3, head[1] + 7), 0.8)
    return pen


_MONSTERS = {
    "skeleton": lambda f, mv: _skeleton(f, mv),
    "skull": lambda f, mv: _skull(f),
    "priest": lambda f, mv: _priest(f),
    "vampire": lambda f, mv: _vampire(f, mv),
}


def draw_monster(screen, kind, feet_cx, feet_y, facing, t, moving=False, flash=False, alpha=255, dead=False):
    frame = int(t * 8) % 8
    key = ("mon", kind, frame, moving)
    pen = _cached(key, lambda: _MONSTERS[kind](frame, moving))
    surf = pen.finish(facing, flash=True) if flash else _cached(key + (facing,), lambda: pen.finish(facing))
    if dead:                                           # fallen over
        surf = pygame.transform.rotate(surf, 90 if facing < 0 else -90)
    if alpha < 255:
        surf = surf.copy()
        surf.set_alpha(alpha)
    oy = surf.get_height() - (14 if dead else 2)
    screen.blit(surf, (feet_cx - surf.get_width() / 2, feet_y - oy))


def draw_mafor(screen, cx, feet_y, facing, t, flash=False, defeated=False):
    frame = int(t * 8) % 12
    key = ("mafor", frame, defeated)
    pen = _cached(key, lambda: _mafor(frame, defeated))
    surf = pen.finish(facing, flash=True) if flash else _cached(key + (facing,), lambda: pen.finish(facing))
    screen.blit(surf, (cx - surf.get_width() / 2, feet_y - surf.get_height() + 4))
