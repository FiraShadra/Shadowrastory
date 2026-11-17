"""Umarmen: Shadowra can hug the creatures that let her close – at every age.

Pressing E near a Moosläufer, Morwen or one of the elves opens a small menu with "Umarmen".
How the creature reacts depends on Shadowra's soul and on how often she has hugged *this* creature:

    her soul is very dark (trust "gone")  -> rejected   (they pull away / flee)
    her soul frightens them ("afraid")    -> afraid     (they tolerate it, trembling)
    elves she left alone in the fight     -> cold
    first hug                             -> confused   ("?")
    2nd and 3rd hug                       -> warming
    from the 4th hug on                   -> loves      (hearts, they heal her a little)

Hugs give "kindness" (feeds Vertrauen) and "affection" points (feed Zuneigung).
Hugging the same creature again within COOLDOWN seconds is nice, but gives no new points.
"""
import math

import pygame

from . import texts
from .assets import font

COOLDOWN = 25.0
LOVE_AT = 3                    # rewarded hugs before a creature loves her
POINTS = {                     # reaction -> (kindness, affection)
    "confused": (0.5, 0.5),
    "accepts": (0.75, 1.0),    # first hug, women: they accept it warmly
    "blush": (0.5, 0.75),      # first hug, men: they blush and stammer
    "warming": (1.0, 1.0),
    "loves": (1.0, 1.5),
    "afraid": (0.25, 0.0),
}
HEART = (236, 120, 170)


class Hugs:
    def __init__(self, play, counts=None):
        self.play = play
        self.count = dict(counts or {})     # creature id -> rewarded hugs (saved)
        self.last = {}                      # creature id -> time of the last rewarded hug

    # ---- who can be hugged -----------------------------------------------------
    def huggable(self, c):
        if not c.alive:
            return False
        if c.kind == "peaceful":
            return True
        if c.kind == "owl":
            return not c.leaving
        if c.kind in ("elf", "villager"):
            return not c.hostile and not c.leaving
        if c.kind == "human":                         # the humans in the snow (only while not hostile)
            return c.attitude != "hostile" and not c.leaving
        return False

    def nearest(self):
        p = self.play.player
        best = None
        for c in self.play.creatures:
            if not self.huggable(c):
                continue
            dx = abs(c.cx - p.cx)
            if dx < p.w / 2 + c.w / 2 + 30 and abs(c.cy - p.cy) < 70:
                if best is None or dx < abs(best.cx - p.cx):
                    best = c
        return best

    def loves(self, c):
        return self.count.get(c.id, 0) >= LOVE_AT

    @staticmethod
    def name(c):
        return getattr(c, "name", None) or texts.HUG_NAMES.get(c.kind, "")

    # ---- the interaction menu ----------------------------------------------------
    def open_menu(self, c):
        play = self.play
        M = texts.HUG_MENU
        if c.kind == "peaceful":
            actions = [(M["hug"], lambda: self.hug(c)), (M["leave_be"], None)]
        elif c.kind == "owl":
            actions = [(M["talk"], lambda: play.talk_owl(c)), (M["hug"], lambda: self.hug(c)), (M["leave"], None)]
        elif c.kind == "villager":
            actions = [(M["talk"], lambda: play.grove.talk_villager(c)), (M["hug"], lambda: self.hug(c)),
                       (M["leave"], None)]
        elif c.kind == "human":
            actions = [(M["talk"], lambda: play.snow.talk_human(c)), (M["hug"], lambda: self.hug(c)),
                       (M["leave"], None)]
        else:
            actions = [(M["talk"], lambda: play.grove.talk(c)), (M["hug"], lambda: self.hug(c))]
            if play.grove.can_nuzzle():
                actions.append((M["nuzzle"], lambda: play.grove.nuzzle(c)))
            actions.append((M["leave"], None))

        def pick(i):
            fn = actions[i][1]
            if fn:
                fn()
        play.dialog.show([(self.name(c), texts.HUG_PROMPT)], choice=([a[0] for a in actions], pick))

    # ---- hugging -------------------------------------------------------------------
    def reaction(self, c):
        play = self.play
        trust = play.morality.trust()
        if trust == "gone" or getattr(c, "hostile", False):
            return "rejected"
        if trust == "afraid":
            return "afraid"
        if c.kind in ("elf", "villager") and play.grove.outcome == "alone":
            return "cold"
        if play.t - self.last.get(c.id, -1e9) < COOLDOWN:
            return "again"
        n = self.count.get(c.id, 0)
        if n == 0:                       # the very first hug: women accept it, men blush
            gender = getattr(c, "gender", None)
            return {"f": "accepts", "m": "blush"}.get(gender, "confused")
        return "warming" if n < LOVE_AT else "loves"

    def hug(self, c):
        play = self.play
        p = play.player
        r = self.reaction(c)
        dur = 1.0 if r in ("rejected", "cold") else 2.0
        play.rest = dict(kind="hug", t=0.0, dur=dur, target=c, reaction=r)
        p.pose_override = "hug" if r not in ("rejected", "cold") else "nuzzle"
        p.vx = 0
        p.facing = 1 if c.cx > p.cx else -1
        c.facing = -p.facing
        c.vx = 0
        c.stun = max(c.stun, dur)                # the creature holds still during the hug
        c.react = (r, play.t + dur + 2.0)

    def update_rest(self, r, dt):
        play = self.play
        p = play.player
        c = r["target"]
        if r["reaction"] in ("warming", "loves", "again", "confused", "accepts", "blush") and math.sin(r["t"] * 9) > 0.92:
            x = (p.cx + c.cx) / 2
            play.particles.items.append([x + math.sin(r["t"] * 13) * 10, min(p.y, c.y) + 6,
                                         math.sin(r["t"] * 7) * 15, -70, 1.1, 1.1, HEART, 3])
        if r["t"] < r["dur"]:
            return
        play.rest = None
        p.pose_override = None
        self.finish(c, r["reaction"])

    def finish(self, c, reaction):
        play = self.play
        p = play.player
        kind_pts, aff_pts = POINTS.get(reaction, (0.0, 0.0))
        if kind_pts or aff_pts:
            play.morality.mark("kindness", kind_pts)
            play.morality.mark("affection", aff_pts)
            self.last[c.id] = play.t
            if reaction in ("confused", "accepts", "blush", "warming", "loves"):
                self.count[c.id] = self.count.get(c.id, 0) + 1
        if reaction == "blush":
            c.blush_until = play.t + 4.0               # red cheeks for a while
        if reaction == "loves":                     # a hug from someone who loves her heals
            p.hp = min(p.max_hp(), p.hp + p.max_hp() * 0.08)
            play.morality.add(madness=-0.5)
        if reaction == "rejected":
            if c.kind == "peaceful":
                c.scared = 5.0
            else:
                p.vx = -p.facing * 220             # pushed away
        # does this creature remember her from a younger age? (shared with talking: owl / elves)
        memory = {"owl": "owl", "elf": "elves"}.get(c.kind, f"hug_{c.id}")
        if c.kind == "villager":
            memory = f"vil_{c.name.lower()}"            # shared with talking to them
        grew = play.grew_since(memory) and reaction not in ("rejected", "afraid", "cold") \
            and c.kind != "human"                       # the humans only ever knew her grown up
        play.remember_age(memory)
        line = self.line(c, reaction)
        if c.kind == "peaceful":
            if grew:
                play.toast(texts.aged(texts.HUG_GREW["peaceful"], p.stage))
            play.toast(line)
        else:
            if c.kind in ("villager", "human"):
                grew_line = (c.name, texts.VILLAGE_TALK["grew"])
            else:
                grew_line = texts.aged(texts.HUG_GREW[c.name if c.kind == "elf" else c.kind], p.stage)
            play.dialog.show(([grew_line] if grew else []) + [(self.name(c), line)])

    def line(self, c, reaction):
        """The reaction text – depends on who it is, their gender (villagers) and Shadowra's age."""
        if c.kind in ("villager", "human"):
            people = texts.VILLAGERS if c.kind == "villager" else texts.HUMANS
            if reaction in ("accepts", "blush") and "first" in people[c.name]:
                return people[c.name]["first"]                 # each one's own first-hug line
            table = texts.VILLAGE_HUGS[c.gender]
        else:
            table = texts.HUGS[c.name if c.kind == "elf" else c.kind]
        return texts.aged(table.get(reaction) or table["again"], self.play.player.stage)

    # ---- reaction icon above the creature -------------------------------------------
    def draw_icon(self, screen, c, x, y):
        react = getattr(c, "react", None)
        if not react or self.play.t > react[1]:
            return
        kind = react[0]
        t = self.play.t
        bob = math.sin(t * 5) * 3
        y = y + bob
        if kind == "confused":
            s = font(22).render("?", True, (240, 230, 160))
            screen.blit(s, (x - s.get_width() / 2, y - 24))
        elif kind in ("warming", "again", "accepts"):
            _heart(screen, x, y - 12, 6)
        elif kind == "blush":                          # flustered: pink "///" lines
            for i in range(3):
                pygame.draw.line(screen, (240, 110, 150), (x - 9 + i * 6, y - 6), (x - 4 + i * 6, y - 16), 3)
        elif kind == "loves":
            for i, dx in enumerate((-12, 0, 12)):
                _heart(screen, x + dx, y - 12 - (6 if i == 1 else 0) + math.sin(t * 6 + i) * 2, 6 if i == 1 else 4)
        elif kind == "afraid":
            pygame.draw.circle(screen, (140, 190, 255), (int(x + 10), int(y - 6)), 4)
            pygame.draw.polygon(screen, (140, 190, 255), [(x + 6, y - 7), (x + 10, y - 16), (x + 14, y - 7)])
        elif kind == "rejected":
            for a in (0.6, -0.6):
                pygame.draw.line(screen, (230, 70, 70), (x - 7, y - 12 - a * 7), (x + 7, y - 12 + a * 7), 3)
        elif kind == "cold":
            s = font(20).render("...", True, (170, 170, 190))
            screen.blit(s, (x - s.get_width() / 2, y - 26))


def _heart(screen, x, y, r):
    x, y = int(x), int(y)
    pygame.draw.circle(screen, HEART, (x - r // 2, y), r // 2 + 1)
    pygame.draw.circle(screen, HEART, (x + r // 2, y), r // 2 + 1)
    pygame.draw.polygon(screen, HEART, [(x - r - 1, y + 1), (x + r + 1, y + 1), (x, y + r + 3)])
