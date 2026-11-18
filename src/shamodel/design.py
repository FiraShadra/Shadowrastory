"""Shadowra's design: sizes, colours, which body parts she has and extra parts added in the editor.

The design lives in shadowra_design.json in this folder (edit it with `python editor.py`). The game also looks
for data/shadowra_design.json next to the built game first (it adds that to OVERRIDE_PATHS), like morals.json.
Anything missing from the file falls back to DEFAULT, so old or hand-written files keep working.
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN_FILE = os.path.join(HERE, "shadowra_design.json")
# other places a design may come from first (the game adds data/shadowra_design.json next to the built game)
OVERRIDE_PATHS = []

DEFAULT = {
    "version": 1,
    "name": "Shadowra",
    # "cutout": built from the drawn pieces of her parts sheet (rig.py); "drawn": drawn in code (render.py)
    "model": "cutout",
    # which sheet piece fills each slot of the cutout rig (see cutout.CHOICES)
    "cutout": {"head": "head_side", "front_leg": "leg_1", "hind_leg": "leg_6", "tail": "tail_spiny",
               "wing": "states", "neck": "neck_a", "chest": "none"},
    # fine-tuning per cutout piece: move (dx, dy in model units), turn (rot, degrees), size (scale)
    "rig": {},
    # every size is a multiplier: 1.0 = her standard look
    "sizes": {
        "overall": 1.0, "head": 1.0, "snout": 1.0, "eye": 1.0,
        "horn_length": 1.0, "horn_thickness": 1.0, "horn_angle": 0.0, "horn_curve": 1.0,
        "neck_length": 1.0, "neck_thickness": 1.0,
        "body_length": 1.0, "body_height": 1.0, "chest": 1.0,
        "leg_length": 1.0, "leg_thickness": 1.0,
        "tail_length": 1.0, "tail_thickness": 1.0,
        "wing": 1.0, "spikes": 1.0, "frills": 1.0, "scales": 1.0, "shine": 1.0,
    },
    # None = derived from the body colour (belly lighter, spikes darker, wing a bit darker)
    "colors": {
        "body": [86, 56, 88], "belly": None, "spikes": None, "wing": [66, 42, 70],
        "horn": [228, 208, 170], "claw": [226, 214, 190], "outline": [22, 12, 26],
    },
    "parts": {
        "horns": True, "far_horn": True, "horn_rings": True, "ear_frills": True, "crest_spike": True,
        "back_spikes": True, "neck_spines": True, "tail_spines": True, "throat_plates": True,
        "belly_plates": True, "toes": True, "fangs": True, "smile": True, "brow": True, "wings": True,
        "muscles": True, "tail_spade": False, "scales": True, "sheen": True,
    },
    "counts": {"back_spikes": 7, "neck_spines": 4, "tail_spines": 5, "ear_frills": 3, "toes": 3},
    # extra parts: {"type", "anchor", "x", "y", "size", "length", "angle", "bend", "color", "layer", "far_copy"}
    "custom": [],
}

PART_TYPES = ("spike", "horn", "fin", "oval", "whisker", "gem")
ANCHORS = ("head", "neck", "back", "chest", "hips", "tail_mid", "tail_tip")
LAYERS = ("behind", "front", "top")             # behind the body / over body and head / over everything
COLOR_NAMES = ("spikes", "horn", "body", "belly", "wing", "claw", "outline")

NEW_PART = {
    "spike":   {"anchor": "back", "x": 0.0, "y": -10.0, "size": 3.0, "length": 6.0, "angle": 0.0, "bend": 0.0,
                "color": "spikes"},
    "horn":    {"anchor": "head", "x": 2.0, "y": -6.0, "size": 2.5, "length": 9.0, "angle": -20.0, "bend": 0.5,
                "color": "horn"},
    "fin":     {"anchor": "back", "x": -4.0, "y": -9.0, "size": 6.0, "length": 18.0, "angle": 0.0, "bend": 0.0,
                "color": "wing"},
    "oval":    {"anchor": "chest", "x": 0.0, "y": 0.0, "size": 4.0, "length": 6.0, "angle": 0.0, "bend": 0.0,
                "color": "belly"},
    "whisker": {"anchor": "head", "x": 12.0, "y": 1.0, "size": 0.5, "length": 10.0, "angle": 110.0, "bend": 0.6,
                "color": "horn"},
    "gem":     {"anchor": "head", "x": 1.0, "y": -5.0, "size": 1.6, "length": 1.6, "angle": 0.0, "bend": 0.0,
                "color": [150, 90, 255]},
}


def new_part(kind):
    p = {"type": kind, "layer": "front", "far_copy": False}
    p.update(copy.deepcopy(NEW_PART[kind]))
    if kind == "fin":
        p["layer"] = "behind"
    return p


def normalize(d):
    """A complete design: DEFAULT with everything from d on top (unknown keys are kept)."""
    out = copy.deepcopy(DEFAULT)
    if not isinstance(d, dict):
        return out
    for key, val in d.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key].update(val)
        else:
            out[key] = copy.deepcopy(val)
    out["custom"] = [dict(new_part(p.get("type", "spike")), **p) for p in out.get("custom") or []
                     if isinstance(p, dict) and p.get("type") in PART_TYPES]
    return out


def load(path=None):
    for p in ([path] if path else OVERRIDE_PATHS + [DESIGN_FILE]):
        if p and os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    return normalize(json.load(f))
            except (OSError, ValueError):
                pass
    return normalize({})


def save(design, path=None):
    path = path or DESIGN_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(design, f, indent=2)
    return path


_current = None


def current():
    """The design the game draws Shadowra with (loaded once)."""
    global _current
    if _current is None:
        _current = load()
    return _current


def set_current(design):
    """Used by the editor: draw Shadowra with this design from now on."""
    global _current
    _current = normalize(design)


def shade(col, d):
    return tuple(max(0, min(255, int(c + d))) for c in col[:3])


def colors(design, body=None, horn=None):
    """Resolved colours. body / horn: overrides (Fira and other dragons that reuse the model)."""
    c = design["colors"]
    b = tuple(body[:3]) if body is not None else tuple(c["body"])
    return {
        "body": b,
        "belly": tuple(c["belly"]) if c.get("belly") and body is None else shade(b, 26),
        "spikes": tuple(c["spikes"]) if c.get("spikes") and body is None else shade(b, -38),
        "wing": tuple(c["wing"]) if c.get("wing") and body is None else shade(b, -14),
        "horn": tuple(horn[:3]) if horn is not None else tuple(c["horn"]),
        "claw": tuple(c["claw"]),
        "outline": tuple(c["outline"]),
    }


def part_color(part, cols):
    c = part.get("color", "spikes")
    if isinstance(c, str):
        return cols.get(c, cols["spikes"])
    return tuple(c[:3])
