"""Cheats from src/controls/xheats.json:  "name": true = on, false = off.

    "infinite mana"     her mana is always full
    "infinite stamina"  her stamina is always full (she never gets exhausted)
    "infinite health"   her life is always full – nothing can kill her (not even lava, spikes, cold or drowning)

The file is read whenever a game is started or continued, so it can be changed between sessions.
A built game (.exe / AppImage) uses a xheats.json placed next to it if there is one, otherwise the bundled one.
Unknown names or values are ignored (with a note in the terminal) – a typo never crashes the game.
"""
import json
import os

from .settings import ROOT, GAME_DIR

KNOWN = ("infinite mana", "infinite stamina", "infinite health")


def cheats_file():
    for p in (os.path.join(GAME_DIR, "xheats.json"), os.path.join(GAME_DIR, "src", "controls", "xheats.json"),
              os.path.join(ROOT, "src", "controls", "xheats.json")):
        if os.path.exists(p):
            return p
    return None


def load():
    """The set of active cheats."""
    path = cheats_file()
    if not path:
        return set()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print("[xheats.json] could not be read:", e)
        return set()
    active = set()
    for name, value in (data.items() if isinstance(data, dict) else []):
        key = str(name).strip().lower()
        if key not in KNOWN:
            print(f"[xheats.json] unknown cheat '{name}' ignored (known: {', '.join(KNOWN)})")
            continue
        if isinstance(value, str):
            value = value.strip().lower() == "true"
        if value is True:
            active.add(key)
    return active


def apply(play, active):
    """Called every frame after everything else has happened to her."""
    if not active:
        return
    p = play.player
    mods = play.morality.mods()
    if "infinite mana" in active:
        p.mana = p.max_mana()
    if "infinite stamina" in active:
        p.stamina = p.max_stam(mods)
        p.exhausted = 0.0
    if "infinite health" in active:
        p.hp = p.max_hp()
        if p.dead and play.death_t is None:              # lava, spikes, cold, drowning: she just stays alive
            p.dead = False
            p.pose_override = None if p.pose_override == "dead" else p.pose_override
