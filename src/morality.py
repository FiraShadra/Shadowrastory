"""Shadowra's hidden soul state.

The raw deeds are counted in `Morality` (wild / madness / lust / abhorrent) and, per kind of deed, in
`Morality.deeds`. How those deeds *shape her* is decided by the moral paths and their subpaths:

    MoralPath            base class: tiers, subpaths, NPC reaction, nest, ending
    ├─ GentlePath        Sanftmut   – she stays herself
    │  ├─ CalmBreathSubpath    Ruhige Atmung – she can breathe calmly, and her stamina costs are lower
    │  └─ TrustedSubpath       Vertrauen     – she is trusted by the world, and food heals her better
    ├─ WildPath          Wildheit   – the predator: blood of innocents, hunting warm-blooded creatures
    │  ├─ StrengthSubpath      Raubtier      – claws, but prey flees and food is unsatisfying – she just wants to hunt
    │  └─ FlightSubpath        Flügelschlag  – she flies well, but her stamina is low and prey flees
    ├─ MadnessPath       Wahnsinn   – sleeplessness and horror she cannot process
    │  ├─ SleeplessSubpath     Schlaflos     – she cannot sleep, and the world starts to lie to her
    │  ├─ HorrorSubpath        Grauen        – she sees things that aren't there, and her focus is torn
    │  └─ TwistedSubpath       Zerrissen     – she is haunted by the horrors she has seen, and her mind is fraying
    └─ LustPath          Gier       – power hunger: drinking when not needed, devouring
       ├─ GreedySubpath        Gierig        – she takes more than she needs; nothing satisfies her any more
       ├─ WantingSubpath       Besessen      – she craves the power of others; her body and heart pay for it
       ├─ OverflowingSubpath   Überfluss     – more power than her body can hold; it leaks out of her
       └─ AffectionSubpath     Zuneigung     – her hunger turns into longing for Fira (requires lust AND the gentle path)
                                               – also grows from hugging creatures (affection points)

Tier (Stufe) = how deep she has gone down a path (from the path's value).
Subpath      = which way she went down it, chosen by the kind of deeds that fed the path.
The active subpath's effects for the current tier are applied as stat multipliers. Effects of all paths
stack (she can be wild AND mad); the strongest path decides her ending.

To add a subpath: subclass SubPath (key, SOURCE or score(), EFFECTS_BY_TIER), add it to the path's SUBPATHS
and its name/description to texts.SUBPATHS.
"""
from dataclasses import dataclass, field

from . import morals, texts


@dataclass(frozen=True)
class Effect:
    key: str
    good: bool = False
    mods: dict = field(default_factory=dict)   # multipliers, e.g. {"stam_cost": 1.4}

    @property
    def name(self):
        return texts.EFFECTS[self.key][0]

    @property
    def desc(self):
        return texts.EFFECTS[self.key][1]


# Modifier keys and what they scale:
#   stam_cost  sprint / flap / dash / tail / wall jump / glide   max_stam   maximum stamina
#   stam_regen stamina regeneration                                mana_cost  spikes, fire
#   veil_drain mana burned by the veil in light                    food_heal  healing from food
#   claw_dmg   melee damage                                        blood_gain mana from blood
#   max_mana   maximum mana                                        sleep_mana mana restored by sleep
#   flee       (additive, px) how early peaceful creatures flee
NEUTRAL_MODS = dict(stam_cost=1.0, max_stam=1.0, stam_regen=1.0, mana_cost=1.0, veil_drain=1.0,
                    food_heal=1.0, claw_dmg=1.0, blood_gain=1.0, max_mana=1.0, sleep_mana=1.0, flee=0.0)

# Kinds of deeds (keys of Morality.deeds):
#   hunt_ground / hunt_air  killing or drinking from creatures on the ground / in the air   -> Wildheit
#   sleepless               madness from staying awake                                     -> Wahnsinn
#   horror                  abhorrent deeds, the owl, the blood of thinking beings          -> Wahnsinn
#   greed                   drinking blood with plenty of mana left                         -> Gier
#   wanting                 drinking priests' blood                                         -> Gier
#   overflow                drinking with full mana, devouring Mafor's light                -> Gier
#   rest / kindness         sleeping and eating at altars / talking to Morwen, sparing Mafor, hugs -> Sanftmut
#   affection               hugging creatures that let her close, cozy meals                  -> Zuneigung
DEEDS = ("hunt_ground", "hunt_air", "sleepless", "horror", "greed", "wanting", "overflow", "rest", "kindness",
         "affection")
# Extra morals (e.g. SAffection) are defined in data/morals.json – see src/morals.py. Every deed above is also
# an *event* those morals can listen to ("gain"), plus "cozy_meal". Advanced ones are capped at 3 (FSK 12).


# ---------------------------------------------------------------------------
# Subpaths
# ---------------------------------------------------------------------------
class SubPath:
    key = "base"
    SOURCE = None            # deed key that feeds this subpath (or override score())
    EFFECTS_BY_TIER = ()     # effect keys unlocked at tier 1, 2, 3 ...
    THRESHOLDS = None        # own tier thresholds; None = use the parent path's

    def __init__(self, path):
        self.path = path
        self.m = path.m

    def score(self):
        return self.m.deeds.get(self.SOURCE, 0.0) if self.SOURCE else 0.0

    def eligible(self):
        return True

    def tier(self):
        if self.THRESHOLDS is None:
            return self.path.tier()
        v = self.path.value()
        return sum(1 for t in self.THRESHOLDS if v >= t)

    def effects(self):
        out = []
        for keys in self.EFFECTS_BY_TIER[: self.tier()]:
            out += [EFFECTS[k] for k in keys]
        return out

    @property
    def name(self):
        return texts.SUBPATHS[self.key][0]

    @property
    def desc(self):
        return texts.SUBPATHS[self.key][1]


# --- Sanftmut ---
class CalmBreathSubpath(SubPath):
    key = "calm_breath"
    SOURCE = "rest"
    EFFECTS_BY_TIER = (["calm_breath"], ["deep_rest"])


class TrustedSubpath(SubPath):
    key = "trusted"
    SOURCE = "kindness"
    EFFECTS_BY_TIER = (["trusted"], ["gentle_presence"])

    def score(self):
        return super().score() * 3       # kind deeds are rarer than rests, so they weigh more


# --- Wildheit ---
class StrengthSubpath(SubPath):
    key = "strength"
    SOURCE = "hunt_ground"
    EFFECTS_BY_TIER = (["skittish_prey"], ["predator", "wild_hunger"], ["hunting_frenzy"])


class FlightSubpath(SubPath):
    key = "flight"
    SOURCE = "hunt_air"
    EFFECTS_BY_TIER = (["skittish_prey"], ["hunter_wings", "lean_body"], ["sky_hunger"])


# --- Wahnsinn ---
class SleeplessSubpath(SubPath):
    key = "sleepless"
    SOURCE = "sleepless"
    EFFECTS_BY_TIER = (["restless_sleep"], ["hallucinations"], ["false_rest"])


class HorrorSubpath(SubPath):
    key = "horror"
    SOURCE = "horror"
    EFFECTS_BY_TIER = (["hallucinations"], ["torn_focus"], ["dread"])


class TwistedSubpath(SubPath):
    """Zerrissen: torn between sleeplessness AND horror – only wins when both are strong."""
    key = "twisted"
    EFFECTS_BY_TIER = (["restless_sleep", "hallucinations"], ["torn_focus"], ["fraying_mind"])

    def score(self):
        d = self.m.deeds
        return 2 * min(d.get("sleepless", 0.0), d.get("horror", 0.0))


# --- Gier ---
class GreedySubpath(SubPath):
    key = "greedy"
    SOURCE = "greed"
    EFFECTS_BY_TIER = (["dark_affinity"], ["greedy_soul"], ["insatiable"])


class WantingSubpath(SubPath):
    key = "wanting"
    SOURCE = "wanting"
    EFFECTS_BY_TIER = (["dark_affinity"], ["blood_thirst", "restless_heart"], ["possessed"])


class OverflowingSubpath(SubPath):
    key = "overflowing"
    SOURCE = "overflow"
    EFFECTS_BY_TIER = (["overflow"], ["leaking_power"], ["bursting_heart"])


class AffectionSubpath(SubPath):
    """Zuneigung: only possible while the gentle path still defines her (corruption < 20).
    Her hunger turns into longing – towards Fira and everyone who lets her close.
    Grows from a little lust (10/15) OR from affection points earned by hugging (3/8)."""
    key = "affection"
    EFFECTS_BY_TIER = (["longing"], ["devotion"])
    THRESHOLDS = (10, 15)            # lust can't grow past ~19 while she is still gentle
    HUG_THRESHOLDS = (3, 8)          # affection points from hugs

    def eligible(self):
        return self.m.corruption < Morality.GENTLE_LIMIT

    def tier(self):
        lust = self.m.lust
        hugs = self.m.deeds.get("affection", 0.0)
        return max(sum(1 for t in self.THRESHOLDS if lust >= t),
                   sum(1 for t in self.HUG_THRESHOLDS if hugs >= t))

    def score(self):
        return float("inf")      # if possible, it always wins


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
class MoralPath:
    key = "base"
    THRESHOLDS = ()      # value needed for tier 1, 2, 3 ...
    SUBPATHS = ()
    ending_by_tier = {}  # tier -> ending key (missing tiers fall back to "redemption")
    nest = "bones"
    owl = "afraid"

    def __init__(self, m):
        self.m = m

    def value(self):
        raise NotImplementedError

    def tier(self):
        """0 = path not taken, 1..n = how deep she has gone."""
        v = self.value()
        return sum(1 for t in self.THRESHOLDS if v >= t)

    def subpath(self):
        """The branch her deeds have pushed her down (None while the path is not taken)."""
        options = [S(self) for S in self.SUBPATHS]
        options = [s for s in options if s.eligible() and s.tier() > 0]
        if not options:
            return None
        return max(options, key=lambda s: s.score())    # ties -> first listed (the default branch)

    def tier_title(self):
        t = self.tier()
        return texts.PATHS[self.key][t] if t else ""

    def title(self):
        sp = self.subpath()
        if not sp:
            return self.tier_title()
        return f"{self.tier_title()} · {sp.name}" if self.tier_title() else sp.name

    def effects(self):
        sp = self.subpath()
        return sp.effects() if sp else []

    def ending(self):
        return self.ending_by_tier.get(self.tier(), "redemption")


class GentlePath(MoralPath):
    """Sanftmut: the less corrupted she is, the more the world helps her."""
    key = "gentle"
    THRESHOLDS = (80, 90)
    SUBPATHS = (CalmBreathSubpath, TrustedSubpath)
    ending_by_tier = {0: "light", 1: "light", 2: "light"}   # dominant only while corruption < 20
    nest = "bloom"
    owl = "trust"

    def value(self):
        return max(0.0, 100.0 - self.m.corruption * 5)     # corruption 0 -> 100, 2 -> 90, 4 -> 80


class WildPath(MoralPath):
    key = "wild"
    THRESHOLDS = (15, 35, 60)
    SUBPATHS = (StrengthSubpath, FlightSubpath)
    ending_by_tier = {1: "redemption", 2: "redemption", 3: "redemption"}
    nest = "bones"
    owl = "afraid_wild"

    def value(self):
        return self.m.wild


class MadnessPath(MoralPath):
    key = "madness"
    THRESHOLDS = (10, 25, 45)
    SUBPATHS = (SleeplessSubpath, HorrorSubpath, TwistedSubpath)
    ending_by_tier = {1: "redemption", 2: "madness", 3: "madness"}
    nest = "scratches"
    owl = "afraid_mad"

    def value(self):
        return self.m.madness


class LustPath(MoralPath):
    key = "lust"
    THRESHOLDS = (10, 25, 45)
    SUBPATHS = (GreedySubpath, WantingSubpath, OverflowingSubpath, AffectionSubpath)
    ending_by_tier = {1: "redemption", 2: "obsession", 3: "obsession"}
    nest = "hoard"
    owl = "afraid_lust"

    def value(self):
        return self.m.lust


EFFECTS = {e.key: e for e in (
    # Sanftmut
    Effect("calm_breath", good=True, mods=dict(stam_cost=0.9)),
    Effect("deep_rest", good=True, mods=dict(stam_regen=1.15)),
    Effect("trusted", good=True, mods=dict(food_heal=1.15)),
    Effect("gentle_presence", good=True, mods=dict(flee=-60)),
    # Wildheit – Raubtier
    Effect("skittish_prey", mods=dict(flee=90)),
    Effect("predator", good=True, mods=dict(claw_dmg=1.2)),
    Effect("wild_hunger", mods=dict(food_heal=0.5)),
    Effect("hunting_frenzy", mods=dict(claw_dmg=1.15, stam_regen=0.8)),
    # Wildheit – Flügelschlag
    Effect("hunter_wings", good=True, mods=dict(stam_cost=0.8)),
    Effect("lean_body", mods=dict(max_stam=0.8)),
    Effect("sky_hunger", mods=dict(food_heal=0.6, flee=60)),
    # Wahnsinn
    Effect("restless_sleep", mods=dict(stam_regen=0.85)),
    Effect("hallucinations"),
    Effect("false_rest", mods=dict(sleep_mana=0.6)),
    Effect("torn_focus", mods=dict(mana_cost=1.4, veil_drain=1.5)),
    Effect("dread", mods=dict(stam_cost=1.2)),
    Effect("fraying_mind", mods=dict(mana_cost=1.2, food_heal=0.8, sleep_mana=0.8)),
    # Gier
    Effect("dark_affinity", good=True, mods=dict(mana_cost=0.8)),
    Effect("greedy_soul", mods=dict(food_heal=0.6, max_stam=0.9)),
    Effect("insatiable", mods=dict(food_heal=0.7, blood_gain=1.2)),
    Effect("blood_thirst", good=True, mods=dict(blood_gain=1.4)),
    Effect("restless_heart", mods=dict(stam_regen=0.7)),
    Effect("possessed", mods=dict(claw_dmg=1.15, max_stam=0.85)),
    Effect("overflow", good=True, mods=dict(max_mana=1.25)),
    Effect("leaking_power", mods=dict(veil_drain=1.3)),
    Effect("bursting_heart", mods=dict(stam_regen=0.75, max_stam=0.9)),
    Effect("longing", good=True, mods=dict(mana_cost=0.9)),
    Effect("devotion", good=True, mods=dict(food_heal=1.1)),
    # she went on to the snowlands and left Fira in his cage – the grief weighs on almost everything
    Effect("grief", mods=dict(stam_cost=1.3, max_stam=0.8, stam_regen=0.75, food_heal=0.7, claw_dmg=0.8,
                              mana_cost=1.25, max_mana=0.85, sleep_mana=0.8)),
    # SAffection (self-affection) – she takes care of herself
)}

PATHS = (GentlePath, WildPath, MadnessPath, LustPath)


class Morality:
    GREED_ABHORRENT = 3      # deeds she completely abhors before the save is lost
    GREED_CORRUPTION = 120   # ...or simply too many immoral deeds
    GENTLE_LIMIT = 20        # below this corruption the gentle path still defines her

    def __init__(self, data=None):
        self.wild = 0.0
        self.madness = 0.0
        self.lust = 0.0
        self.abhorrent = 0
        self.blood_count = 0
        self.boss_choice = None
        self.deeds = {k: 0.0 for k in DEEDS}
        self.values = {}                 # extra morals from data/morals.json: key -> value
        self.stage = 0                   # her age – some extra morals only grow at certain ages (set by Play)
        self.grief = False               # she left Fira behind (set by Play from the story flags)
        if data:
            for k, v in data.items():
                if k == "deeds":
                    self.deeds.update(v)
                elif k == "values":
                    self.values.update(v or {})
                else:
                    setattr(self, k, v)
        old = self.deeds.pop("self_affection", 0.0)          # SAffection used to be a deed (2026-11-17)
        if old and "saffection" not in self.values:
            self.values["saffection"] = old
        defs = morals.load()
        for key, v in list(self.values.items()):             # never above the max (FSK 12 cap included)
            if key in defs:
                self.values[key] = max(0.0, min(float(defs[key].max), float(v)))

    def to_dict(self):
        return dict(wild=self.wild, madness=self.madness, lust=self.lust,
                    abhorrent=self.abhorrent, blood_count=self.blood_count,
                    boss_choice=self.boss_choice, deeds=dict(self.deeds), values=dict(self.values))
        # (grief is not stored: Play derives it from the story flags every frame)

    @property
    def corruption(self):
        return self.wild + self.madness + self.lust

    def add(self, wild=0.0, madness=0.0, lust=0.0, abhorrent=0, deed=None):
        """Record a deed. `deed` names its kind, which decides the subpath it pushes her towards."""
        self.wild = max(0.0, self.wild + wild)
        self.madness = max(0.0, self.madness + madness)
        self.lust = max(0.0, self.lust + lust)
        self.abhorrent += abhorrent
        gain = max(0.0, wild) + max(0.0, madness) + max(0.0, lust)
        if deed and gain:
            self.deeds[deed] = self.deeds.get(deed, 0.0) + gain
            self.moral_event(deed)

    def mark(self, deed, amount=1.0):
        """A deed that shapes her without corrupting her (resting, kindness)."""
        self.deeds[deed] = self.deeds.get(deed, 0.0) + amount
        self.moral_event(deed, amount)

    # ---- extra morals (data/morals.json) ------------------------------------------
    def moral_event(self, event, times=1.0):
        """Something happened in the game: raise every extra moral that listens to this event (at her age,
        never past its max). Returns the names of the morals that grew."""
        grew = []
        for d in morals.load().values():
            g = d.gain.get(event)
            if not g or not d.allowed_at(self.stage):
                continue
            v = self.values.get(d.key, 0.0)
            new = min(float(d.max), v + g * times)
            if new > v:
                self.values[d.key] = new
                grew.append(d.name)
        return grew

    def moral_refusal(self, event):
        """The line she says if this event would push a moral past its max (None = no refusal)."""
        for d in morals.load().values():
            if (d.gain.get(event) and d.limit_line and d.allowed_at(self.stage)
                    and self.values.get(d.key, 0.0) >= d.max):
                return d.limit_line
        return None

    def moral_value(self, key):
        return self.values.get(key, 0.0)

    def affection(self):
        return self.deeds.get("affection", 0.0)

    def moral_summary(self):
        """'SAffection 2/3 · ...' for every extra moral she has gained."""
        defs = morals.load()
        return "   ·   ".join(f"{d.name} {self.values[k]:g}/{d.max}" for k, d in defs.items()
                              if self.values.get(k, 0.0) > 0)

    def moral_effects(self):
        out = []
        for d in morals.load().values():
            v = self.values.get(d.key, 0.0)
            out += [e for at, e in d.effects if v >= at]
        return out

    # ---- paths ------------------------------------------------------------
    def paths(self):
        return [P(self) for P in PATHS]

    def dark_paths(self):
        return [p for p in self.paths() if not isinstance(p, GentlePath)]

    def dominant(self):
        """The path that defines her: gentle while barely corrupted, otherwise her strongest dark path."""
        if self.corruption < self.GENTLE_LIMIT:
            return GentlePath(self)
        return max(self.dark_paths(), key=lambda p: (p.tier(), p.value()))

    def subpaths(self):
        """Every active subpath, e.g. [Raubtier, Schlaflos]."""
        return [sp for sp in (p.subpath() for p in self.paths()) if sp]

    def effects(self):
        out = []
        for p in self.paths():
            out += p.effects()
        out += self.moral_effects()              # extra morals from data/morals.json
        if self.grief:
            out.append(EFFECTS["grief"])
        seen, unique = set(), []
        for e in out:                     # the same effect from two subpaths counts once
            if e.key not in seen:
                seen.add(e.key)
                unique.append(e)
        return unique

    def mods(self):
        m = dict(NEUTRAL_MODS)
        for e in self.effects():
            for k, v in e.mods.items():
                m[k] = m[k] + v if k == "flee" else m[k] * v
        return m

    def debuffs(self):
        """Keys of every active effect (good and bad)."""
        return {e.key for e in self.effects()}

    # ---- consequences -----------------------------------------------------
    def trust(self):
        """How friendly creatures react to her."""
        c = self.corruption
        if c >= 60 or self.abhorrent >= 2:
            return "gone"
        if c >= 30:
            return "afraid"
        return "trust"

    def owl_reaction(self):
        """Which line the owl uses when she is afraid – depends on what Shadowra is becoming."""
        return self.dominant().owl if self.trust() == "afraid" else self.trust()

    def flee_radius(self):
        return max(60, 110 + min(260, self.wild * 3) + self.mods()["flee"])

    def doomed(self):
        return self.abhorrent >= self.GREED_ABHORRENT or self.corruption >= self.GREED_CORRUPTION

    def close_to_doom(self):
        return not self.doomed() and (self.abhorrent == self.GREED_ABHORRENT - 1 or self.corruption >= 90)

    def ending(self):
        if self.doomed():
            return "greed"
        return self.dominant().ending()

    def title(self):
        """Her current nature, e.g. 'Bestie · Flügelschlag' – shown only in the pause menu."""
        if self.doomed():
            return texts.DOOMED_TITLE
        d = self.dominant()
        title = d.title() or texts.PATHS["gentle"][0]
        if isinstance(d, GentlePath):
            love = LustPath(self).subpath()
            if love and isinstance(love, AffectionSubpath):
                title += f" · {love.name}"          # she is still gentle – and in love
        return title

    def nest_mood(self):
        """What her nest looks like when she returns: a mirror of her soul."""
        return self.dominant().nest

    def eye_color(self):
        c = min(1.0, self.corruption / 100.0)
        return (int(200 + 55 * c), int(40 - 30 * c), int(50 - 40 * c))
