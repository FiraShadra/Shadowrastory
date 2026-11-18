"""Shadowra as a cutout rig: drawn pieces from her parts sheet (parts/, cut out by
extract_parts.py) that turn at their joints for every pose.

Coordinates are model units like the drawn model in render.py: feet at y = 0, facing right, 1 unit = k pixels.
The sheet draws her looking left, so every piece is mirrored. Joint and pivot points are given in the sheet
piece's own pixels (before mirroring) and are carried through mirroring, scaling and turning, so the pieces
stay attached in every pose. Standing poses are moved so that the lowest foot touches the ground.

Colours: the original art is used as it is for Shadowra's standard colours; other colours (Fira, the editor)
are made by scaling the colour channels, with horns and eyes masked separately (<piece>_horn / _eye.png).
"""
import math
import os

import pygame

PART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts")
ART_BODY = (78, 54, 80)              # average body colour of the art (what "standard colour" means)
ART_WING = (70, 48, 72)
ART_HORN = (214, 190, 140)
SSC = 2                              # pieces are composed at 2x and smoothly scaled down

# ---------------------------------------------------------------------------------------------------------
# Pieces: image, pivot (where it hangs on its parent) and named points, all in sheet pixels (looking left).
# 'scale' turns sheet pixels into model units.
# ---------------------------------------------------------------------------------------------------------
PIECES = {
    "torso": dict(pivot=(75, 130), scale=0.17,
                  points=dict(neck=(76, 14), front_hip=(52, 66), hind_hip=(78, 212), tail=(98, 240),
                              wing=(116, 62), chest=(40, 90), back=(128, 120), hips=(92, 205))),
    "head_side": dict(pivot=(126, 188), scale=0.17,
                      points=dict(head=(80, 110), snout=(20, 140), crown=(110, 60))),
    "head_side2": dict(pivot=(120, 175), scale=0.17,
                       points=dict(head=(80, 100), snout=(15, 130), crown=(110, 55))),
    "leg_1": dict(pivot=(70, 22), scale=0.115, points=dict(foot=(45, 248))),
    "leg_2": dict(pivot=(62, 22), scale=0.115, points=dict(foot=(40, 250))),
    "arm_1": dict(pivot=(34, 16), scale=0.142, points=dict(foot=(30, 225))),
    "arm_2": dict(pivot=(26, 16), scale=0.142, points=dict(foot=(30, 228))),
    "leg_5": dict(pivot=(60, 28), scale=0.125, points=dict(foot=(40, 210))),
    "leg_6": dict(pivot=(45, 28), scale=0.125, points=dict(foot=(40, 218))),
    "leg_7": dict(pivot=(55, 28), scale=0.125, points=dict(foot=(40, 222))),
    "leg_3": dict(pivot=(55, 22), scale=0.12, points=dict(foot=(45, 238))),
    "tail_spiny": dict(pivot=(10, 50), scale=0.2, points=dict(tail_mid=(95, 88), tail_tip=(120, 36))),
    "tail_seg": dict(pivot=(10, 40), scale=0.2, points=dict(tail_mid=(70, 60), tail_tip=(135, 100))),
    "tail_big": dict(pivot=(12, 52), scale=0.2, points=dict(tail_mid=(130, 70), tail_tip=(100, 155))),
    "tail_curl": dict(pivot=(60, 10), scale=0.2, points=dict(tail_mid=(40, 70), tail_tip=(30, 140))),
    "wing_side": dict(pivot=(24, 150), scale=0.19, points=dict(wing_tip=(64, 12))),
    # from torso.jpg
    "chest_side": dict(pivot=(80, 110), scale=0.15, points=dict(socket=(75, 128))),
    "neck_a": dict(pivot=(110, 122), scale=0.15, points=dict(top=(48, 42), mid=(80, 80))),
    # from wings.jpg: a drawn wing for each state ("flip": False = already faces the right way)
    "wing_spread": dict(pivot=(8, 75), scale=0.21, points=dict(wing_tip=(240, 90))),
    "wing_up": dict(pivot=(150, 66), scale=0.22, flip=False, points=dict(wing_tip=(5, 100))),
    "wing_half": dict(pivot=(6, 80), scale=0.2, points=dict(wing_tip=(60, 190))),
    "wing_fold": dict(pivot=(45, 22), scale=0.19, points=dict(wing_tip=(35, 190))),
}
# which drawn wing (and how it is turned / sized) for each wing state of the "states" wing set
WING_STATES = {
    "rest": ("wing_half", -8, 0.95, 1.0),
    "spread": ("wing_spread", -6, 1.0, 1.0),
    "up": ("wing_up", -18, 1.35, 1.0),
    "down": ("wing_spread", 40, 0.95, 0.8),
    "droop": ("wing_half", 38, 0.65, 0.9),
    "embrace": ("wing_half", -50, 0.7, 1.0),
    "tucked": ("wing_half", 62, 0.62, 0.85),
}
CHOICES = {                          # what the editor offers for each slot
    "head": ("head_side", "head_side2"),
    "front_leg": ("leg_1", "leg_2", "arm_1", "arm_2", "leg_3"),
    "hind_leg": ("leg_6", "leg_5", "leg_7"),
    "tail": ("tail_spiny", "tail_seg", "tail_big"),
    "wing": ("states", "wing_side"),
    "neck": ("neck_a", "none"),
    "chest": ("none", "chest_side"),
}
DEFAULT_CHOICE = {"head": "head_side", "front_leg": "leg_1", "hind_leg": "leg_6", "tail": "tail_spiny",
                  "wing": "states", "neck": "neck_a", "chest": "none"}
SLOTS = ("head", "neck", "torso", "chest", "front_leg", "hind_leg", "tail", "wing")

_img = {}
_cache = {}


def available():
    return os.path.exists(os.path.join(PART_DIR, "torso.png"))


def _load(name, kind=""):
    key = name + kind
    if key not in _img:
        path = os.path.join(PART_DIR, name + kind + ".png")
        img = pygame.image.load(path) if os.path.exists(path) else None
        if img is not None and pygame.display.get_init() and pygame.display.get_surface() is not None:
            img = img.convert_alpha()
        _img[key] = img
    return _img[key]


def _cached(key, build):
    if key not in _cache:
        if len(_cache) > 400:
            _cache.clear()
        _cache[key] = build()
    return _cache[key]


def _ratio(col, ref):
    return tuple(c / max(1, r) for c, r in zip(col, ref))


def _scale_rgb(img, ratio):
    """img * ratio per colour channel (ratio may be > 1), alpha untouched."""
    out = img.copy()
    n = 0
    while max(ratio) / (2 ** n) > 1.0:
        n += 1
    out.fill(tuple(max(0, min(255, int(r / 2 ** n * 255))) for r in ratio), special_flags=pygame.BLEND_RGB_MULT)
    for _ in range(n):                                   # double back up
        out.blit(out.copy(), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return out


def colored(name, body, wing, horn, eye, closed_eye=False):
    """A piece in the given colours. Standard colours + red eyes = the art untouched."""
    def build():
        img = _load(name)
        if img is None:
            return None
        base = ART_WING if name.startswith("wing") else ART_BODY
        target = wing if name.startswith("wing") else body
        hmask, emask = _load(name, "_horn"), _load(name, "_eye")
        out = img if target == base else _scale_rgb(img, _ratio(target, base))
        if out is img and (hmask is not None or emask is not None or closed_eye):
            out = img.copy()
        if hmask is not None and tuple(horn) != ART_HORN:
            h = _scale_rgb(img, _ratio(horn, ART_HORN))
            h.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            out.blit(hmask, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            out.blit(h, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        if emask is not None:
            if closed_eye:
                _close_eye(out, emask, body)
            elif tuple(eye[:3]) != (220, 30, 40):            # the art's iris shading in the new colour
                r = _scale_rgb(pygame.transform.grayscale(img), tuple(c * 3.0 / 255 for c in eye[:3]))
                r.blit(emask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                out.blit(emask, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
                out.blit(r, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return out
    return _cached(("col", name, tuple(body), tuple(wing), tuple(horn), tuple(eye[:3]), closed_eye), build)


def _close_eye(out, emask, body):
    """Paint a closed eyelid over the eye (sleeping, nuzzling)."""
    m = pygame.mask.from_surface(emask, 10)
    for r in m.get_bounding_rects():
        if r.w * r.h < 12:
            continue
        lid = r.inflate(r.w * 0.7, r.h * 0.7)
        skin = tuple(max(0, int(c * 0.85)) for c in body)
        pygame.draw.ellipse(out, skin, lid)
        pygame.draw.arc(out, (24, 14, 28), lid.inflate(-lid.w * 0.15, -lid.h * 0.3).move(0, lid.h * 0.12),
                        math.pi * 1.1, math.pi * 1.9, max(2, lid.h // 8))


class Placed:
    """A piece put into the model: mirrored, scaled (sx along width, sy along height), turned by angle
    (degrees, counter-clockwise like pygame) with its pivot on 'at' (model units)."""

    def __init__(self, name, at, angle, sx=1.0, sy=1.0, dark=0.0, layer=0):
        p = PIECES[name]
        img = _load(name)
        self.name, self.at, self.angle, self.dark, self.layer = name, at, angle, dark, layer
        self.w, self.h = img.get_size()
        self.sx, self.sy = p["scale"] * sx, p["scale"] * sy
        self.flip = p.get("flip", True)
        self.pivot = self._local(p["pivot"])

    def _local(self, pt):                      # sheet pixel -> (mirrored,) scaled offset in model units
        return ((self.w - pt[0] if self.flip else pt[0]) * self.sx, pt[1] * self.sy)

    def point(self, pt):
        """Where a sheet pixel of this piece ends up (model units)."""
        if isinstance(pt, str):
            pt = PIECES[self.name]["points"][pt]
        x, y = self._local(pt)
        vx, vy = x - self.pivot[0], y - self.pivot[1]
        a = math.radians(self.angle)
        return (self.at[0] + vx * math.cos(a) + vy * math.sin(a),
                self.at[1] - vx * math.sin(a) + vy * math.cos(a))

    def moved(self, dy):
        self.at = (self.at[0], self.at[1] + dy)


def _pose(pose, t, flap):
    """Joint angles (degrees, CCW) and offsets for a pose."""
    P = dict(torso=-62, by=-24.0, head=0.0, head_dx=0.0, head_dy=0.0, fl=4.0, hl=-4.0, ffl=-6.0, fhl=6.0,
             tail=0.0, wing=28.0, wing_s=0.7, wing_state="rest", wing_sy=1.0, ground=True, tail_piece=None, eyes_closed=False)
    walk = {"walk": (9, 16), "run": (14, 26)}.get(pose)
    if walk:
        sp, amp = walk
        s = math.sin(t * sp)
        P.update(fl=amp * s, ffl=-amp * s, hl=-amp * s * 0.9, fhl=amp * s * 0.9, by=-24 + abs(s) * 1.2,
                 tail=math.sin(t * sp * 0.5) * 4, head=math.sin(t * sp) * 2)
    elif pose == "idle":
        P.update(by=-24 + math.sin(t * 2) * 0.5, tail=math.sin(t * 2.2) * 4, head=math.sin(t * 1.3) * 1.5)
    if pose in ("jump", "glide", "flap", "dive", "swim"):
        P.update(ground=False, fl=-25, ffl=-35, hl=-35, fhl=-45, torso=-70, wing=62, wing_s=1.0,
                 tail=-4 + math.sin(t * 3) * 3, wing_state="spread")
        if pose == "dive":
            P.update(torso=-112, head=-28, wing=40, wing_s=0.9, fl=10, ffl=0)
        if pose == "flap":
            up = flap >= 0.18
            P.update(wing=14 if up else 84, wing_sy=1.0 if up else 0.7, wing_state="up" if up else "down")
        if pose == "jump":
            P.update(wing=45, wing_s=0.85)
    if pose == "exhausted":
        P.update(head=-25, head_dx=2, head_dy=6, wing=88, wing_s=0.62, by=-21 + math.sin(t * 5) * 1.0, tail=-6,
                 wing_state="droop")
    if pose in ("eat", "nuzzle", "hug"):
        P.update(head=-38, head_dx=3, head_dy=8 + (math.sin(t * 8) * 1.5 if pose == "eat" else 0))
        if pose == "nuzzle" or pose == "hug":
            P.update(head=-20 + math.sin(t * 4) * 6, head_dx=5, eyes_closed=True)
        if pose == "hug":
            P.update(wing=-20, wing_s=0.85, wing_state="embrace")
    if pose == "fire":
        P.update(head=-8, head_dx=2)
    if pose == "claw":
        P.update(fl=70, ffl=10)
    if pose == "tail":
        P.update(tail=-28 * math.sin(min(1.0, (t % 0.35) / 0.35) * math.pi))
    if pose in ("sleep", "dead", "curl_eat"):
        P.update(torso=-86, by=-13, fl=82, ffl=78, hl=80, fhl=76, head=-14, head_dx=4, head_dy=9, wing=96,
                 wing_s=0.55, eyes_closed=pose != "curl_eat", tail=6, wing_state="tucked")
        if pose == "curl_eat":
            P.update(tail_piece="tail_big", head=-24 + math.sin(t * 8) * 3, tail=-6)
        if pose == "dead":
            P.update(head=-4, head_dy=11, wing=130, wing_s=0.7)
    return P


def build(stage, pose, t, flap, design, body, wing, horn, eye, k):
    """Place every piece for this frame. Returns (pieces in draw order, anchors, ground offset)."""
    S = design["sizes"]
    rig = design.get("rig") or {}
    ch = dict(DEFAULT_CHOICE, **(design.get("cutout") or {}))
    P = _pose(pose, t, flap)
    hk = (1.35, 1.0, 0.95)[stage] * S["head"]
    bl, bh = S["body_length"], S["body_height"]

    def adj(slot):
        r = rig.get(slot) or {}
        return r.get("dx", 0.0), r.get("dy", 0.0), r.get("rot", 0.0), r.get("scale", 1.0)

    tdx, tdy, trot, tsc = adj("torso")
    torso = Placed("torso", (6 + tdx, P["by"] + tdy), P["torso"] + trot, sx=bh * tsc, sy=bl * tsc)  # over the hitbox
    anchors = {}
    for name in ("chest", "back", "hips"):
        anchors[name] = torso.point(name)

    # wings (far one first, darker)
    wdx, wdy, wrot, wsc = adj("wing")
    ws = S["wing"] * P["wing_s"] * wsc
    far_wing = near_wing = None
    if design["parts"].get("wings", True):
        root = torso.point("wing")
        if ch["wing"] == "states":                   # a drawn wing for each state (wings.jpg)
            name, ang, sc, sy = WING_STATES[P["wing_state"]]
            ws = S["wing"] * sc * wsc
            far_wing = Placed(name, (root[0] + 4 + wdx, root[1] - 2 + wdy), ang + wrot + 6, ws, ws * sy, dark=0.4)
            near_wing = Placed(name, (root[0] + wdx, root[1] + wdy), ang + wrot, ws, ws * sy)
        else:                                        # one wing turned into every state
            far_wing = Placed(ch["wing"], (root[0] + 4 + wdx, root[1] - 2 + wdy), P["wing"] + wrot + 8,
                              ws, ws * P["wing_sy"], dark=0.4)
            near_wing = Placed(ch["wing"], (root[0] + wdx, root[1] + wdy), P["wing"] + wrot, ws,
                               ws * P["wing_sy"])

    # legs
    lk = S["leg_length"]
    lt = S["leg_thickness"]
    fdx, fdy, frot, fsc = adj("front_leg")
    hdx, hdy, hrot, hsc = adj("hind_leg")
    fh, hh = torso.point("front_hip"), torso.point("hind_hip")
    legs_far = [Placed(ch["front_leg"], (fh[0] + 2 + fdx, fh[1] - 1 + fdy), P["ffl"] + frot, lt * fsc, lk * fsc, 0.35),
                Placed(ch["hind_leg"], (hh[0] + 2 + hdx, hh[1] - 1 + hdy), P["fhl"] + hrot, lt * hsc, lk * hsc, 0.35)]
    legs_near = [Placed(ch["hind_leg"], (hh[0] + hdx, hh[1] + hdy), P["hl"] + hrot, lt * hsc, lk * hsc),
                 Placed(ch["front_leg"], (fh[0] + fdx, fh[1] + fdy), P["fl"] + frot, lt * fsc, lk * fsc)]

    # tail
    xdx, xdy, xrot, xsc = adj("tail")
    tail_name = P["tail_piece"] or ch["tail"]
    tr = torso.point("tail")
    tail = Placed(tail_name, (tr[0] + xdx, tr[1] + xdy), P["tail"] + xrot, S["tail_thickness"] * xsc,
                  S["tail_length"] * xsc) if tail_name in PIECES else None

    # side-view chest over the front of the body (its shoulder socket sits under the front leg)
    cdx, cdy, crot, csc = adj("chest")
    chest = None
    if ch.get("chest", "none") in PIECES:
        cp = torso.point("chest")
        chest = Placed(ch["chest"], (cp[0] + 4 + cdx, cp[1] - 3 + cdy), P["torso"] + 62 + crot, bh * csc, bh * csc)
        fh = chest.point("socket")                  # front legs hang from the shoulder socket
        for lg, dx_, dy_ in ((legs_far[0], 2, -1), (legs_near[1], 0, 0)):
            lg.at = (fh[0] + dx_ + fdx, fh[1] + dy_ + fdy)

    # neck: a drawn segment between body and head, bending with the head
    edx, edy, erot, esc = adj("head")
    ndx, ndy, nrot, nsc = adj("neck")
    nk = torso.point("neck")
    nl = S.get("neck_length", 1.0)
    neck = None
    if ch.get("neck", "none") in PIECES:
        neck = Placed(ch["neck"], (nk[0] + ndx, nk[1] + 2 + ndy), P["torso"] + 62 + P["head"] * 0.5 + nrot,
                      S.get("neck_thickness", 1.0) * nsc, nl * nsc)
        top = neck.point("top")
        head_at = (top[0] + P["head_dx"] * 0.6 + edx, top[1] + 6 + P["head_dy"] * 0.6 + edy)
    else:
        a = math.radians(P["torso"])
        up = (math.sin(-a) * -1, -math.cos(a))        # direction the neck stump points
        head_at = (nk[0] + P["head_dx"] + edx + up[0] * (nl - 1) * 10, nk[1] + P["head_dy"] + edy + up[1] * (nl - 1) * 10)
    head = Placed(ch["head"], head_at, P["head"] + erot, hk * esc, hk * esc)
    anchors["neck"] = neck.point("mid") if neck else ((nk[0] + head.at[0]) / 2, (nk[1] + head.at[1]) / 2)
    for name in ("head",):
        anchors[name] = head.point("head")
    if tail:
        anchors["tail_mid"] = tail.point("tail_mid")
        anchors["tail_tip"] = tail.point("tail_tip")

    order = [far_wing] + legs_far + [tail, "custom:behind", torso, chest, legs_near[0], neck, legs_near[1], head,
                                      "custom:front", near_wing, "custom:top"]
    order = [o for o in order if o is not None]
    ground = 0.0
    if P["ground"]:                                     # lowest foot on the ground
        feet = [lg.point("foot") for lg in legs_near + legs_far]
        lowest = max(f[1] for f in feet)
        if pose in ("sleep", "dead", "curl_eat"):                  # lying: belly and chin on the ground
            lowest = max(torso.point("hips")[1] + 3, head.point("snout")[1] + 3)
        ground = -lowest
    for o in order:
        if isinstance(o, Placed):
            o.moved(ground)
    anchors = {n: (x, y + ground) for n, (x, y) in anchors.items()}
    return order, anchors, P


def render_piece(canvas, pc, K, ox, oy, cols):
    body, wing, horn, eye, closed = cols
    img = colored(pc.name, body, wing, horn, eye, closed and pc.name.startswith("head"))
    if img is None:
        return
    w = max(1, int(pc.w * pc.sx * K))
    h = max(1, int(pc.h * pc.sy * K))

    def make():
        im = pygame.transform.flip(img, True, False) if pc.flip else img
        im = pygame.transform.smoothscale(im, (w, h))
        if pc.dark:
            v = int(255 * (1 - pc.dark))
            im.fill((v, v, int(v * 1.05) if v < 243 else v), special_flags=pygame.BLEND_RGB_MULT)
        return im
    im = _cached(("sc", id(img), w, h, pc.dark, pc.flip), make)
    rot = pygame.transform.rotate(im, pc.angle) if abs(pc.angle) > 0.01 else im
    # where the image centre goes so that the pivot sits on pc.at
    px, py = pc.pivot[0] * K, pc.pivot[1] * K
    vx, vy = px - w / 2, py - h / 2
    a = math.radians(pc.angle)
    rvx, rvy = vx * math.cos(a) + vy * math.sin(a), -vx * math.sin(a) + vy * math.cos(a)
    cx = ox + pc.at[0] * K - rvx
    cy = oy + pc.at[1] * K - rvy
    canvas.blit(rot, (cx - rot.get_width() / 2, cy - rot.get_height() / 2))
