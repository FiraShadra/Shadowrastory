"""The humans of the village in the snow (src/world/snowylands/snowyvillage, see humans.md there).

They meet Shadowra kindly – or try to kill her. It depends on what she has become:

    her soul is still trusted   -> "kind"     talk, hugs (women accept the first hug, men blush),
                                              the elder Gunnar gives her the Herdsegen
    her soul frightens them     -> "wary"     they keep their distance and ask her to stay away
    her soul is lost / beastly  -> "hostile"  the hunters attack with spears (thrust + throw),
                                              everyone else flees into the houses

Lines live in texts.HUMANS / texts.HUMAN_TALK, looks in STYLES below.
"""
import math
import random

from .creatures import Creature

# looks: the elf model with round human ears ("human"), warm fur clothes ("fur"), spears for hunters
STYLES = {
    "Mira": dict(gender="f", hair=(150, 90, 50), cloth=(150, 60, 50), trim=(240, 236, 228), skin=(238, 214, 196),
                 boots=(80, 56, 40), eyes=(70, 100, 140), hair_style="braid", outfit="fur", human=True),
    "Bjarn": dict(gender="m", hair=(196, 150, 80), cloth=(110, 84, 60), trim=(236, 230, 220), skin=(232, 200, 176),
                  boots=(70, 50, 36), eyes=(60, 90, 130), hair_style="short", outfit="fur", weapon="spear", human=True),
    "Hanne": dict(gender="f", hair=(232, 210, 150), cloth=(70, 100, 150), trim=(244, 240, 232), skin=(242, 222, 208),
                  boots=(60, 60, 90), eyes=(80, 120, 170), hair_style="long", outfit="fur", human=True),
    "Gunnar": dict(gender="m", hair=(220, 220, 214), cloth=(96, 70, 60), trim=(240, 236, 228), skin=(226, 200, 182),
                   boots=(60, 44, 34), eyes=(100, 110, 120), hair_style="elder", outfit="fur", weapon="staff", human=True),
    "Tomas": dict(gender="m", hair=(70, 50, 40), cloth=(70, 96, 70), trim=(236, 232, 224), skin=(214, 180, 150),
                  boots=(56, 44, 32), eyes=(70, 80, 60), hair_style="short", outfit="fur", weapon="spear", human=True),
    "Ylva": dict(gender="f", hair=(120, 60, 40), cloth=(120, 70, 120), trim=(242, 236, 230), skin=(240, 218, 200),
                 boots=(70, 50, 60), eyes=(110, 80, 60), hair_style="bun", outfit="fur", human=True),
}

SPEAR_DMG = 14
THROW_DMG = 11


def attitude_for(morality):
    return {"trust": "kind", "afraid": "wary"}.get(morality.trust(), "hostile")


class Human(Creature):
    kind = "human"
    w, h = 30, 72
    max_hp = 70
    gravity = True

    def __init__(self, x, y, oid, name, gender, role):
        super().__init__(x, y, oid)
        self.name, self.gender, self.role = name, gender, role
        self.style = STYLES.get(name, STYLES["Mira"])
        self.attitude = "kind"
        self.timer = random.uniform(0.5, 3.0)
        self.cool = 0.0                 # spear cooldown
        self.cast = 0.0                 # spear thrust / throw animation
        self.leaving = False
        self.leave_t = 0.0
        self.talk_i = 0
        self.shout_t = 0.0

    # ---- who she can touch -------------------------------------------------------
    @property
    def hostile(self):
        return self.attitude == "hostile" and self.role == "hunter"

    @property
    def friendly(self):
        return not self.hostile          # only the hunters who attack her can be hurt

    @property
    def blood(self):
        return "human" if self.hostile else None

    @property
    def contact(self):
        return 0

    def hurt(self, dmg, from_x, knock=150, play=None):
        if not self.hostile:
            return False
        return super().hurt(dmg, from_x, knock, play)

    # ---- behaviour ----------------------------------------------------------------
    def think(self, dt, play):
        p = play.player
        self.cool = max(0.0, self.cool - dt)
        self.cast = max(0.0, self.cast - dt)
        self.shout_t = max(0.0, self.shout_t - dt)
        dx = p.cx - self.cx
        dist = abs(dx)
        if self.leaving:                                    # slipping into a house
            self.leave_t += dt
            self.vx = 0
            if self.leave_t > 1.2:
                self.alive, self.corpse_t = False, 0.0
            return
        if self.attitude == "hostile":
            if self.role != "hunter":                       # run home and hide
                self.facing = -1 if dx > 0 else 1
                self.vx = self.facing * 150
                if dist > 260:
                    self.leaving = True
                return
            if dist < 600 and self.shout_t <= 0:
                from . import texts
                play.toast(f"{self.name}: {random.choice(texts.HUMAN_TALK['hostile'])}", key=f"shout_{self.id}")
                self.shout_t = 9.0
            self.facing = 1 if dx > 0 else -1
            if dist < 70 and abs(p.cy - self.cy) < 60:      # spear thrust
                self.vx = 0
                if self.cool <= 0:
                    self.cool, self.cast = 1.4, 0.35
                    p.hurt(SPEAR_DMG, self.cx)
            elif dist < 420 and self.cool <= 0 and abs(p.cy - self.cy) < 220:   # throw a spear
                self.vx = 0
                self.cool, self.cast = 2.6, 0.4
                play.spawn_spear(self, p.cx, p.cy)
            elif dist < 700:
                self.vx = self.facing * 110
            else:
                self.vx = 0
            if self.wall_ahead(play.level) or self.ledge_ahead(play.level):
                self.vx = 0
            return
        if self.attitude == "wary" and dist < 160:          # keep their distance
            self.facing = -1 if dx > 0 else 1
            self.vx = self.facing * 90
            if self.wall_ahead(play.level) or self.ledge_ahead(play.level):
                self.vx = 0
            return
        # kind (or wary and far enough): stroll around home, turn to look at her
        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(1.5, 4.0)
            home_dx = self.home[0] - self.x
            self.vx = random.choice((-40, 0, 40)) if abs(home_dx) < 60 else math.copysign(40, home_dx)
        if self.vx:
            self.facing = 1 if self.vx > 0 else -1
            if self.wall_ahead(play.level) or self.ledge_ahead(play.level):
                self.vx = 0
        elif dist < 220:
            self.facing = 1 if dx > 0 else -1
