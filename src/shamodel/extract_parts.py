"""Cut Shadowra's parts sheet into separate transparent PNGs (a development tool, not used by the game).

    python extract_parts.py            (in this folder) cuts sheets/*.jpg into parts/<piece>.png
    python extract_parts.py --debug    also writes labelled overviews parts/debug_<sheet>.png (delete them
                                       afterwards, they are not pieces)

How: everything that is near-white or near-black and connected to the sheet border is background (the white
cards, the black gaps and the white sticker borders). What is left falls apart into separate parts; each one
is matched by position to a name in PARTS below. The ink outline lost with the background is drawn back in.
The eye irises and the horns also get their own masks (<part>_eye.png, <part>_horn.png), so the game can
recolour them (eye colour by morality, Fira's colours).
"""
import os
import sys
from collections import deque

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_DIR = os.path.join(HERE, "sheets")
OUT = os.path.join(HERE, "parts")

INK = (26, 16, 30)

# name: a point inside the part (sheet pixels). The component under that point becomes the part.
PARTS = {
    "head_side": (90, 120),         # side view, looking left (the rig flips it)
    "head_side2": (300, 120),       # side / three-quarter view, looking left
    "head_front": (510, 120),       # front views for the close-up portrait
    "head_front_smile": (715, 120),
    "head_front_open": (915, 120),
    "horn_left": (250, 290),
    "horn_right": (345, 290),
    "torso": (510, 380),
    "tail_curl": (660, 300),
    "tail_seg": (790, 320),
    "tail_big": (930, 300),
    "tail_spiny": (720, 445),
    "wing_back_left": (130, 600),
    "wing_back_right": (380, 600),
    "wing_side": (620, 620),
    "arm_1": (830, 600),
    "arm_2": (945, 600),
    "leg_1": (95, 880),
    "leg_2": (205, 880),
    "leg_3": (320, 880),
    "leg_4": (445, 880),
    "leg_5": (585, 880),
    "leg_6": (715, 880),
    "leg_7": (840, 880),
    "tail_tip": (960, 900),
}


def is_bg(r, g, b):
    hi, lo = max(r, g, b), min(r, g, b)
    # white cards, black gaps, and the grey anti-aliasing between them (the art itself is never grey)
    return lo > 200 or hi < 34 or (hi - lo < 14 and hi > 105)


# Pieces given as a rectangle (x0, y0, x1, y1) take every part lying fully inside it – for pieces whose
# outline splits them (the chest's back spikes come out as separate bits otherwise).
TORSO_PARTS = {                     # torso.jpg
    "chest_side": (432, 60, 600, 270),          # side view of chest and shoulder, spikes down the back
    "chest_side_small": (478, 282, 606, 450),
    "neck_a": (692, 62, 840, 215),              # neck segments (the first one is bent, with spikes)
    "neck_b": (722, 222, 836, 338),
    "neck_c": (684, 350, 832, 472),             # flared neck base
    "neck_d": (874, 94, 975, 222),
    "neck_e": (892, 224, 986, 330),
    "neck_f": (884, 332, 990, 428),
    "ridge": (1268, 92, 1345, 215),             # dorsal ridge: a row of back spikes
    "spike_1": (1293, 212, 1350, 266),
    "spike_2": (1295, 258, 1350, 314),
    "spike_3": (1298, 305, 1342, 374),
    "spike_4": (1292, 370, 1335, 430),
    "spike_5": (1288, 425, 1325, 492),
    "spine_strip": (1072, 95, 1146, 278),
}
WING_PARTS = {                      # wings.jpg – whole wings seen from the side
    "wing_spread": (444, 37, 692, 153),
    "wing_up": (700, 38, 868, 148),
    "wing_long": (1023, 45, 1208, 120),
    "wing_fold": (954, 565, 1044, 763),
    "wing_fold2": (1152, 560, 1237, 770),
    "wing_half": (1243, 565, 1355, 763),
}


def sheets():
    """(sheet file, {piece name: point inside it}) for every parts sheet."""
    return [("Gemini_Generated_Image_2wt8xo2wt8xo2wt8.jpg", PARTS), ("torso.jpg", TORSO_PARTS),
            ("wings.jpg", WING_PARTS)]


def main(debug=False):
    pygame.init()
    for name, parts in sheets():
        extract(os.path.join(SHEET_DIR, name), parts, debug and os.path.splitext(name)[0], name == "torso.jpg")


def extract(path, parts, debug_tag, hide_sockets=False):
    """hide_sockets: the torso sheet marks joints (shoulder sockets, cut faces of neck segments) in pink –
    those are painted in a darker body tone, so they never show between the pieces."""
    sheet = pygame.image.load(path)
    W, H = sheet.get_size()
    raw = pygame.image.tobytes(sheet, "RGB")
    px = [(raw[i], raw[i + 1], raw[i + 2]) for i in range(0, len(raw), 3)]
    cand = bytearray(1 if is_bg(*p) else 0 for p in px)

    # 1. background: flood from the border through near-white / near-black pixels
    bg = bytearray(W * H)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            q.append(y * W + x)
    for y in range(H):
        for x in (0, W - 1):
            q.append(y * W + x)
    while q:
        i = q.popleft()
        if bg[i] or not cand[i]:
            continue
        bg[i] = 1
        x, y = i % W, i // W
        if x > 0:
            q.append(i - 1)
        if x < W - 1:
            q.append(i + 1)
        if y > 0:
            q.append(i - W)
        if y < H - 1:
            q.append(i + W)

    # 2. connected parts
    label = [0] * (W * H)
    comps = {}
    n = 0
    for start in range(W * H):
        if bg[start] or label[start]:
            continue
        n += 1
        stack = [start]
        label[start] = n
        pix = []
        while stack:
            i = stack.pop()
            pix.append(i)
            x, y = i % W, i // W
            for j, ok in ((i - 1, x > 0), (i + 1, x < W - 1), (i - W, y > 0), (i + W, y < H - 1)):
                if ok and not bg[j] and not label[j]:
                    label[j] = n
                    stack.append(j)
        comps[n] = pix

    os.makedirs(OUT, exist_ok=True)
    if debug_tag:
        dbg = sheet.copy()
        font = pygame.font.Font(None, 18)
        for c, pix in comps.items():
            if len(pix) < 150:
                continue
            xs = [i % W for i in pix]
            ys = [i // W for i in pix]
            r = pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
            pygame.draw.rect(dbg, (0, 255, 0), r, 1)
            dbg.blit(font.render("%d" % c, True, (0, 255, 0)), r.topleft)
            print("  comp %d at %s size %d  point (%d, %d)" % (c, tuple(r), len(pix), pix[len(pix) // 2] % W,
                                                              pix[len(pix) // 2] // W))
        pygame.image.save(dbg, os.path.join(OUT, "debug_%s.png" % debug_tag))

    # 3. save each named part
    written = []
    boxes = {}
    for c, p in comps.items():
        xs = [i % W for i in p[::7]] + [p[0] % W, p[-1] % W]
        ys = [i // W for i in p[::7]] + [p[0] // W, p[-1] // W]
        boxes[c] = (min(xs), min(ys), max(xs), max(ys))
    for name, spec in parts.items():
        if len(spec) == 4:                      # rectangle: every part fully inside
            x0, y0, x1, y1 = spec
            cs = [c for c, (a, b, cc, dd) in boxes.items()
                  if len(comps[c]) > 25 and a >= x0 and b >= y0 and cc <= x1 and dd <= y1
                  and min(cc - a, dd - b) > 5]           # not the thin border lines of a card
            pix = [i for c in cs for i in comps[c]]
        else:
            sx, sy = spec
            c = label[sy * W + sx]
            pix = comps[c] if c else []
        if not pix:
            print("!! nothing for", name, spec)
            continue
        xs = [i % W for i in pix]
        ys = [i // W for i in pix]
        x0, y0, x1, y1 = min(xs) - 3, min(ys) - 3, max(xs) + 4, max(ys) + 4
        w, h = x1 - x0, y1 - y0
        img = pygame.Surface((w, h), pygame.SRCALPHA)
        img.fill((0, 0, 0, 0))
        mask = bytearray(w * h)
        for i in pix:
            x, y = i % W - x0, i // W - y0
            mask[y * w + x] = 1
        # outline ring: pixels next to the part that are not part of it
        ring = bytearray(w * h)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                k = y * w + x
                if not mask[k] and (mask[k - 1] or mask[k + 1] or mask[k - w] or mask[k + w]):
                    ring[k] = 1
        eye = pygame.Surface((w, h), pygame.SRCALPHA)
        eye.fill((0, 0, 0, 0))
        horn = pygame.Surface((w, h), pygame.SRCALPHA)
        horn.fill((0, 0, 0, 0))
        n_eye = n_horn = 0
        for y in range(h):
            for x in range(w):
                k = y * w + x
                if mask[k]:
                    r, g, b = px[(y + y0) * W + x + x0]
                    if hide_sockets and r > 100 and r > g + 40 and b > g + 18:
                        r, g, b = int(r * 0.5), int(g * 0.8), int(b * 0.62)
                    img.set_at((x, y), (r, g, b, 255))
                    if r > 120 and r > g * 2.2 and r > b * 2.0:                     # red iris
                        eye.set_at((x, y), (255, 255, 255, 255))
                        n_eye += 1
                    elif r > 120 and g > 95 and r - b > 25 and r >= g >= b - 10 and r - g < 60:   # cream horn
                        horn.set_at((x, y), (255, 255, 255, 255))
                        n_horn += 1
                elif ring[k]:
                    img.set_at((x, y), (*INK, 255))
        pygame.image.save(img, os.path.join(OUT, name + ".png"))
        if n_eye > 20:
            pygame.image.save(eye, os.path.join(OUT, name + "_eye.png"))
        if n_horn > 40:
            pygame.image.save(horn, os.path.join(OUT, name + "_horn.png"))
        written.append("%s %dx%d eye=%d horn=%d" % (name, w, h, n_eye, n_horn))
    print("\n".join(written))


if __name__ == "__main__":
    main(debug="--debug" in sys.argv)
