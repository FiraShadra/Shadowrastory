"""Extra morals defined in data/morals.json (no code needed to add one).

Each moral has a name, a description, the ages at which it can be gained, a max value, the game events
that raise it, effects unlocked at certain values, and optionally a line Shadowra says at the limit.

    level "basic"     – an ordinary moral, any max
    level "advanced"  – hard-limited to ADVANCED_CAP points in this (FSK 12) version, whatever the JSON says

Broken entries are skipped with a printed warning, so a typo in the JSON never crashes the game.
The definitions are mirrored into the SQLite table `moral_defs` (see save.sync_moral_defs); the values
Shadowra has reached are saved per game in `moral_values`.
"""
import json
import os
import re
from dataclasses import dataclass, field

from .settings import ROOT, GAME_DIR

# a data/morals.json next to the game (also next to the built .exe) wins over the bundled one,
# so new morals can be added without rebuilding
MORALS_FILE = next((p for p in (os.path.join(GAME_DIR, "data", "morals.json"), os.path.join(ROOT, "data", "morals.json"))
                    if os.path.exists(p)), os.path.join(ROOT, "data", "morals.json"))
ADVANCED_CAP = 3                     # FSK 12: advanced morals never go higher than this
AGES = ("hatchling", "juvenile", "adult")
LEVELS = ("basic", "advanced")
EVENTS = ("cozy_meal", "rest", "kindness", "affection", "hunt_ground", "hunt_air", "sleepless", "horror",
          "greed", "wanting", "overflow")
MODS = ("stam_cost", "max_stam", "stam_regen", "mana_cost", "veil_drain", "food_heal", "claw_dmg",
        "blood_gain", "max_mana", "sleep_mana", "flee")


def _lang_text(d, fallback=""):
    """Pick the text for the current language from {"de": ..., "en": ...} (German as fallback)."""
    from . import texts
    if isinstance(d, str):
        return d
    if not isinstance(d, dict):
        return fallback
    return d.get(texts.LANG) or d.get("de") or d.get("en") or fallback


@dataclass(frozen=True)
class MoralEffect:
    """Same interface as morality.Effect (key, good, mods, name, desc), but its texts come from the JSON."""
    key: str
    good: bool
    mods: dict
    names: dict = field(default_factory=dict, compare=False)
    descs: dict = field(default_factory=dict, compare=False)

    @property
    def name(self):
        return _lang_text(self.names, self.key)

    @property
    def desc(self):
        return _lang_text(self.descs)


@dataclass
class MoralDef:
    key: str
    names: dict
    descs: dict
    level: str
    ages: tuple
    max: int
    gain: dict
    effects: list            # [(at, MoralEffect)]
    limit_lines: dict = None

    @property
    def name(self):
        return _lang_text(self.names, self.key)

    @property
    def desc(self):
        return _lang_text(self.descs)

    @property
    def limit_line(self):
        return _lang_text(self.limit_lines) if self.limit_lines else None

    def allowed_at(self, stage):
        return AGES[stage] in self.ages

    def as_json(self):
        """The cleaned-up definition (for the database copy)."""
        return dict(key=self.key, name=self.names, description=self.descs, level=self.level, ages=list(self.ages),
                    max=self.max, gain=self.gain, limit_line=self.limit_lines,
                    effects=[dict(at=at, good=e.good, name=e.names, description=e.descs, mods=e.mods)
                             for at, e in self.effects])


def _parse(entry, i, seen):
    """Validate one JSON entry. Returns (MoralDef or None, [warnings])."""
    w = []
    key = entry.get("key") if isinstance(entry, dict) else None
    where = f"morals[{i}]" + (f" '{key}'" if key else "")
    if not isinstance(entry, dict):
        return None, [f"{where}: is not an object – skipped"]
    if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", key):
        return None, [f"{where}: 'key' must be lowercase letters/digits/_ – skipped"]
    if key in seen:
        return None, [f"{where}: the key is used twice – skipped"]
    level = entry.get("level", "basic")
    if level not in LEVELS:
        return None, [f"{where}: 'level' must be 'basic' or 'advanced' – skipped"]
    ages = entry.get("ages", list(AGES))
    if isinstance(ages, str):
        ages = list(AGES) if ages == "any" else [ages]
    bad_ages = [a for a in ages if a not in AGES]
    if bad_ages or not ages:
        return None, [f"{where}: unknown ages {bad_ages} (use {', '.join(AGES)}) – skipped"]
    try:
        mx = int(entry.get("max", 1))
    except (TypeError, ValueError):
        return None, [f"{where}: 'max' must be a whole number – skipped"]
    if mx < 1:
        return None, [f"{where}: 'max' must be 1 or more – skipped"]
    if level == "advanced" and mx > ADVANCED_CAP:
        w.append(f"{where}: advanced morals are limited to {ADVANCED_CAP} in this version – max {mx} -> {ADVANCED_CAP}")
        mx = ADVANCED_CAP
    gain = {}
    for ev, amount in (entry.get("gain") or {}).items():
        if ev not in EVENTS:
            w.append(f"{where}: unknown event '{ev}' ignored (events: {', '.join(EVENTS)})")
            continue
        try:
            gain[ev] = float(amount)
        except (TypeError, ValueError):
            w.append(f"{where}: gain for '{ev}' is not a number – ignored")
    if not gain:
        w.append(f"{where}: has no valid 'gain' events – it can never grow")
    effects = []
    for j, eff in enumerate(entry.get("effects") or []):
        if not isinstance(eff, dict):
            w.append(f"{where}: effects[{j}] is not an object – ignored")
            continue
        mods = {}
        for mk, mv in (eff.get("mods") or {}).items():
            if mk not in MODS:
                w.append(f"{where}: effects[{j}] unknown mod '{mk}' ignored (mods: {', '.join(MODS)})")
                continue
            try:
                mods[mk] = float(mv)
            except (TypeError, ValueError):
                w.append(f"{where}: effects[{j}] mod '{mk}' is not a number – ignored")
        try:
            at = float(eff.get("at", mx))
        except (TypeError, ValueError):
            at = float(mx)
        if at > mx:
            w.append(f"{where}: effects[{j}] needs {at:g} but the max is {mx} – it can never unlock")
        effects.append((at, MoralEffect(f"{key}:{j}", bool(eff.get("good", True)), mods,
                                        eff.get("name") or {}, eff.get("description") or {})))
    effects.sort(key=lambda e: e[0])
    return MoralDef(key, entry.get("name") or {"de": key}, entry.get("description") or {}, level, tuple(ages),
                    mx, gain, effects, entry.get("limit_line")), w


_DEFS = None
WARNINGS = []


def load(path=MORALS_FILE, force=False):
    """All valid moral definitions, keyed by key (read once, cached)."""
    global _DEFS, WARNINGS
    if _DEFS is not None and not force:
        return _DEFS
    defs, WARNINGS = {}, []
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        raw = {"morals": []}
    except (OSError, json.JSONDecodeError) as e:
        WARNINGS.append(f"{os.path.basename(path)} could not be read: {e}")
        raw = {"morals": []}
    entries = raw.get("morals", []) if isinstance(raw, dict) else raw
    for i, entry in enumerate(entries if isinstance(entries, list) else []):
        d, w = _parse(entry, i, defs)
        WARNINGS += w
        if d:
            defs[d.key] = d
    for msg in WARNINGS:
        print("[morals.json]", msg)
    _DEFS = defs
    return defs
