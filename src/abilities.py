"""What Shadowra can learn, place by place: every src/world/<place>/abilities.json.

Each file lists the abilities of one place:
    key           id used by the game code (glide, veil, dive, ...) – don't change it after release
    name          {"de": ..., "en": ...}
    description   what it does, per language
    learn         how she gets it: "watch" (seeing someone do it), "relic" (an item), "gift", "instinct", "trait"
    learned_from  where / how, per language
    ages          at which ages she can learn it ("hatchling", "juvenile", "adult")
    color         (relics only) colour of the glowing item in the world

Names and descriptions can be edited freely in the JSON files. A broken file never crashes the game:
the problem is printed and the entry skipped.
"""
import json
import os

from .settings import ROOT

WORLD_DIR = os.path.join(ROOT, "src", "world")
# the order places are listed in (journey order)
PLACES = ("scave", "sunnyforest", "lowrow", "elfvillage", "lavacave", "snowylands",
          os.path.join("snowylands", "icecave"), os.path.join("snowylands", "snowyvillage"), "underwater")
AGES = ("hatchling", "juvenile", "adult")
LEARN = ("watch", "relic", "gift", "instinct", "trait")

_REG = None
WARNINGS = []


def _lang(d, fallback=""):
    from . import texts
    if isinstance(d, str):
        return d
    if not isinstance(d, dict):
        return fallback
    return d.get(texts.LANG) or d.get("de") or d.get("en") or fallback


def load(force=False):
    """key -> ability dict (with 'place'), in journey order."""
    global _REG, WARNINGS
    if _REG is not None and not force:
        return _REG
    reg, WARNINGS = {}, []
    for place in PLACES:
        path = os.path.join(WORLD_DIR, place, "abilities.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            continue
        except (OSError, json.JSONDecodeError) as e:
            WARNINGS.append(f"{place}/abilities.json could not be read: {e}")
            continue
        for i, a in enumerate(data.get("abilities", []) if isinstance(data, dict) else []):
            key = a.get("key") if isinstance(a, dict) else None
            if not isinstance(key, str) or not key:
                WARNINGS.append(f"{place}/abilities.json [{i}]: missing 'key' – skipped")
                continue
            if key in reg:
                WARNINGS.append(f"{place}/abilities.json: '{key}' is already defined in {reg[key]['place']} – skipped")
                continue
            ages = [x for x in a.get("ages", AGES) if x in AGES] or list(AGES)
            learn = a.get("learn", "relic")
            if learn not in LEARN:
                WARNINGS.append(f"{place}/abilities.json '{key}': unknown learn type '{learn}' (use {', '.join(LEARN)})")
            col = a.get("color")
            reg[key] = dict(key=key, place=place.replace(os.sep, "/"), names=a.get("name") or {"de": key},
                            descs=a.get("description") or {}, learn=learn, froms=a.get("learned_from") or {},
                            ages=tuple(ages), color=tuple(col) if isinstance(col, list) and len(col) == 3 else None)
    for msg in WARNINGS:
        print("[abilities]", msg)
    _REG = reg
    return reg


def get(key):
    return load().get(key)


def name(key):
    a = get(key)
    return _lang(a["names"], key) if a else key


def desc(key):
    a = get(key)
    return _lang(a["descs"]) if a else ""


def learned_from(key):
    a = get(key)
    return _lang(a["froms"]) if a else ""


def color(key, default=(140, 80, 220)):
    a = get(key)
    return (a["color"] if a and a["color"] else default)


def shown(abilities):
    """Learned abilities in journey order – e.g. for the credits."""
    return [k for k in load() if k in abilities]
