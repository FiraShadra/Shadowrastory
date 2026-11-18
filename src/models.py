"""High-resolution creature models (the elves, Moosläufer, fish, owl, the enemies).

Shadowra herself (and Fira, who reuses her model) lives in src/shamodel/ – her modelling kit with the editor,
the rig, her drawn pieces and her design file. The shared drawing helpers (Pen, shade, bez, ...) come from
there too and are re-exported here for existing callers (render.py, closeup.py).

Every model is drawn at SS× resolution on its own surface and then smoothly scaled down (supersampling).
Coordinates are in *model units* relative to the feet (0, 0), facing right.
"""
import math
import os

import pygame

from .settings import GAME_DIR
from .shamodel import design as _design
from .shamodel.render import (OUTLINE, Pen, bez, glow, shade,  # noqa: F401  (shared helpers, re-exported)
                              PORTRAIT_H, build_portrait, draw_dragon, ground_shadow)

# a design file next to the built game overrides the one in src/shamodel (like data/morals.json)
_design.OVERRIDE_PATHS.append(os.path.join(GAME_DIR, "data", "shadowra_design.json"))


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
