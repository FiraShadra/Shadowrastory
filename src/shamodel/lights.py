"""Light sources on screen, so that scaly models can catch the light.

Every glow drawn with render.draw_light_circle (torches, candles, the hearth fire, priests' torches,
magic, ...) is registered here in screen coordinates. Models read the lights of the *previous* frame:
that list is complete no matter in which order things are drawn, and one frame of lag is invisible.

A light is (x, y, radius, colour, strength).
"""

_current = []
_last = []


def new_frame():
    """Called once per frame before anything is drawn."""
    global _current, _last
    _last, _current = _current, []


def add(x, y, r, col=(255, 230, 150), strength=1.0):
    if strength > 0.02 and len(_current) < 200:
        _current.append((float(x), float(y), float(r), tuple(col[:3]), float(strength)))


def last():
    return _last


_glow_cache = {}


def draw_glow(screen, x, y, r, col=(255, 230, 150), alpha=70):
    """A soft round glow that also counts as a light (what the game's render.draw_light_circle does)."""
    add(x, y, r, col, alpha / 70)
    key = (r, tuple(col), alpha)
    surf = _glow_cache.get(key)
    if surf is None:
        import pygame
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            pygame.draw.circle(surf, (*col, int(alpha * (7 - i) / 6)), (r, r), int(r * i / 6))
        if len(_glow_cache) > 100:
            _glow_cache.clear()
        _glow_cache[key] = surf
    screen.blit(surf, (x - r, y - r))
