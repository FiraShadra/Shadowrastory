"""Loads art and fonts from /assets, with safe fallbacks so a missing file never crashes the game."""
import os
import pygame

from .settings import ASSETS

_cache = {}


def _path(*parts):
    return os.path.join(ASSETS, *parts)


def image(*parts, scale=None, alpha=True):
    key = (parts, scale)
    if key in _cache:
        return _cache[key]
    try:
        surf = pygame.image.load(_path(*parts))
        surf = surf.convert_alpha() if alpha else surf.convert()
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 160))
    if scale:
        if isinstance(scale, (int, float)):
            scale = (int(surf.get_width() * scale), int(surf.get_height() * scale))
        surf = pygame.transform.scale(surf, scale)
    _cache[key] = surf
    return surf


def smooth_up(surf, scale):
    """Upscale tiny pixel art without blocky edges: repeated scale2x (an edge-smoothing pixel-art
    filter) to at least the target size, then a smooth resample to the exact size."""
    target = (max(1, int(surf.get_width() * scale)), max(1, int(surf.get_height() * scale)))
    s = surf
    while s.get_width() < target[0] or s.get_height() < target[1]:
        s = pygame.transform.scale2x(s)
    s = pygame.transform.scale2x(s)          # one extra step so the final resample only shrinks
    return pygame.transform.smoothscale(s, target)


def frames(folder, prefix, count=4, scale=2.5):
    """Creature animation frames, smoothly upscaled."""
    out = []
    for i in range(1, count + 1):
        key = (folder, prefix, i, "smooth", scale)
        if key not in _cache:
            _cache[key] = smooth_up(image(*folder, f"{prefix}_{i}.png"), scale)
        out.append(_cache[key])
    return out


_fonts = {}


def font(size, kind="text"):
    key = (size, kind)
    if key in _fonts:
        return _fonts[key]
    f = None
    if kind == "title":
        # Kalnia Glaze (SIL Open Font License – free for commercial use)
        try:
            f = pygame.font.Font(_path("font", "Kalnia_Glaze", "static", "KalniaGlaze-SemiBold.ttf"), size)
        except (pygame.error, FileNotFoundError, OSError):
            f = None
    if f is None:
        f = pygame.font.SysFont("georgia,palatino linotype,serif", size)
    _fonts[key] = f
    return f


class Sprites:
    """Every sprite sheet the game uses, loaded once after the display exists."""

    def __init__(self):
        ca = ("images", "gameassets", "Character-animation")
        items = ("images", "gameassets", "items-and-trap-animation")
        self.priest = frames(ca + ("priests_idle", "priest1", "v1"), "priest1_v1", scale=3)
        self.priest_boss = frames(ca + ("priests_idle", "priest3", "v1"), "priest3_v1", scale=9)
        self.skeleton = frames(ca + ("monsters_idle", "skeleton1", "v1"), "skeleton_v1", scale=3)
        self.skull = frames(ca + ("monsters_idle", "skull", "v1"), "skull_v1", scale=2.5)
        self.torch = frames(items + ("torch",), "torch", scale=2)
        self.spikes = [image("images", "starry_night_by_quintino_pixels", "Spikes",
                             f"spike_ground{i}.png", scale=2) for i in (1, 2, 3)]
        self.water = [image("images", "starry_night_by_quintino_pixels", "Water",
                            f"water{i}.png", scale=2) for i in (1, 2, 3, 4)]
        self.sky = image("images", "starry_night_by_quintino_pixels", "background_sky.png", alpha=False)
        self.clouds = image("images", "starry_night_by_quintino_pixels", "clouds.png")
        self.mountains1 = image("images", "Wasteland_Mountains_1.png")
        self.mountains2 = image("images", "Wasteland_Mountains_2.png")
        self.logo = image("images", "logo", "Logo.png")
        self.vampire = frames(ca + ("monsters_idle", "vampire", "v1"), "vampire_v1", scale=3)
        arrow = image(*items, "arrow", "Just_arrow.png", scale=2)
        self.arrow = arrow
        # Elfenhain props from the Grassland pack, tinted into the grove's night colours
        gl = ("images", "Multi_Platformer_Tileset_Free", "Multi_Platformer_Tileset_Free", "GrassLand", "Props")
        bg = gl[:-1] + ("Background",)
        self.day_layers = [image(*bg, f"GrassLand_Background_{i}.png", alpha=True) for i in (1, 2, 3, 4, 5)]
        self.day_clouds = [image(*bg, f"GrassLand_Cloud_{i}.png", scale=5) for i in (3, 2, 1)]
        self.decor_day = {k: image(*gl, n, scale=2) for k, n in (
            ("flower", "GrassLand_Flower_1.png"), ("grass_day", "GrassLand_TallGrass_2.png"),
            ("bush_day", "GrassLand_Bush.png"), ("stone_day", "GrassLand_Stone_2.png"))}
        self.decor = {}
        for key, name in (("tree", "GrassLand_Tree.png"), ("bush", "GrassLand_Bush.png"),
                          ("stone", "GrassLand_Stone_3.png"), ("grass", "GrassLand_TallGrass_1.png")):
            img = image(*gl, name, scale=2).copy()
            img.fill((50, 85, 110), special_flags=pygame.BLEND_RGB_MULT)
            self.decor[key] = img
