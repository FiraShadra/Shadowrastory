"""Elfenhain: the elves Sera & Erila, the monster waves that hunt them, and Shadowra's choice.

Choices when she meets them (depends on how the elves see her – Morality.trust()):
    trust   -> "Helfen" / "Nicht helfen" (+ "Bei ihnen bleiben und sich anschmiegen" with the Zuneigung subpath)
    afraid  -> "Helfen" / "Nicht helfen" – but even if she helps, their camp stays closed
    gone    -> Sera attacks her, Erila flees
Outcomes: friends (camp opens, healing, kindness) · wary · alone · dead (horror if she watched) · hostile
"""
import math
import random

from .settings import TILE
from .world import X
from .creatures import Creature, Skeleton, Skull, Projectile
from .morality import AffectionSubpath
from . import texts


# Tuned by simulation: without Shadowra the elves survive the 3 waves about half the time,
# with her help (fighting or nuzzle-shielding) they survive every time.
ARCHER_COOL = 1.0      # seconds between Sera's arrows
HEAL = 16              # Erila's heal per cast (every 3.5 s)


def overlap(a, b):
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]


class Elf(Creature):
    kind = "elf"
    blood = "elf"
    w, h = 24, 46
    max_hp = 75
    gravity = True

    def __init__(self, x, y, oid, name):
        super().__init__(x, y, oid)
        self.name = name
        self.role = "archer" if name == "Sera" else "healer"
        self.gender = "f"
        self.hostile = False
        self.cool = random.uniform(0.3, 1.0)
        self.invuln = 0.0
        self.cast = 0.0            # bow draw / staff glow animation timer
        self.leaving = False
        self.leave_t = 0.0
        self.facing = -1

    @property
    def friendly(self):
        return not self.hostile

    def hurt(self, dmg, from_x, knock=150, play=None):
        """Damage from Shadowra – only possible once the elves have turned on her."""
        if not self.hostile:
            return False
        return super().hurt(dmg, from_x, knock=knock)

    def monster_hit(self, dmg, from_x):
        if self.invuln > 0 or not self.alive:
            return
        self.hp -= dmg
        self.flash = 0.15
        self.invuln = 0.7
        self.vx = (1 if self.cx >= from_x else -1) * 120
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.corpse_t = 1e9    # the elves stay where they fell

    def heal(self, amount):
        if self.alive:
            self.hp = min(self.max_hp, self.hp + amount)

    def think(self, dt, play):
        self.invuln = max(0.0, self.invuln - dt)
        self.cast = max(0.0, self.cast - dt)
        self.cool -= dt
        p = play.player
        q = play.grove
        if self.leaving:                         # Erila runs and hides
            self.leave_t += dt
            self.facing = 1
            self.vx = 200
            if self.leave_t > 2.5:
                self.alive = False
                self.corpse_t = 0
            return
        if self.hostile:
            self.facing = 1 if p.cx > self.cx else -1
            self.vx = 0
            if self.role == "archer" and self.cool <= 0 and abs(p.cx - self.cx) < 520:
                self.cool = 1.3
                self.cast = 0.3
                play.spawn_arrow(self, p.cx, p.cy, "enemy")
            return
        fighting = q is not None and q.state == "fight"
        if not fighting:
            self.vx = 0
            if abs(p.cx - self.cx) < 300:
                self.facing = 1 if p.cx > self.cx else -1
            return
        foes = [m for m in q.monsters if m.alive]
        near = min(foes, key=lambda m: abs(m.cx - self.cx), default=None)
        if self.role == "archer":
            if near and math.hypot(near.cx - self.cx, near.cy - self.cy) < 500:
                self.facing = 1 if near.cx > self.cx else -1
                if self.cool <= 0:
                    self.cool = ARCHER_COOL
                    self.cast = 0.3
                    play.spawn_arrow(self, near.cx, near.cy, "elf")
        else:
            if self.cool <= 0:
                self.cool = 3.5
                targets = [e for e in q.elves if e.alive and e.hp < e.max_hp]
                if targets:
                    t = min(targets, key=lambda e: e.hp / e.max_hp)
                    t.heal(HEAL)
                    self.cast = 0.6
                    play.particles.burst(t.cx, t.cy, (190, 230, 255), 14, 90)
                if q.friendly_to_player() and p.hp < p.max_hp() and abs(p.cx - self.cx) < 260:
                    p.hp = min(p.max_hp(), p.hp + 12)
                    self.cast = 0.6
                    play.particles.burst(p.cx, p.cy, (190, 230, 255), 14, 90)
            if near:
                self.facing = 1 if near.cx > self.cx else -1
        # step back from monsters, but never leave the camp
        if near and abs(near.cx - self.cx) < 70 and abs(near.cy - self.cy) < 60:
            self.vx = (1 if self.cx > near.cx else -1) * 90
        else:
            self.vx = max(-60, min(60, (self.home[0] - self.x) * 2))
        if abs(self.x - self.home[0]) > 3 * TILE:
            self.vx = (1 if self.home[0] > self.x else -1) * 90
        if self.ledge_ahead(play.level) and self.on_ground:
            self.vx = 0


class Villager(Creature):
    """An elf of the Elfendorf. Hides in the houses during the attack, strolls around afterwards."""
    kind = "villager"
    blood = "elf"
    w, h = 24, 46
    max_hp = 60
    friendly = True
    hostile = False

    def __init__(self, x, y, oid, name):
        super().__init__(x, y, oid)
        self.name = name
        data = texts.VILLAGERS[name]
        self.gender = data["gender"]
        self.style = data["style"]
        self.timer = random.uniform(0.5, 3.0)
        self.leaving = False
        self.leave_t = 0.0
        self.talk_i = 0

    def hurt(self, *a, **k):
        return False                    # Shadowra's claws never touch the villagers

    def think(self, dt, play):
        p = play.player
        if self.leaving:                # her soul turned dark: they hide in their houses
            self.leave_t += dt
            self.vx = 0
            if self.leave_t > 1.2:
                self.alive, self.corpse_t = False, 0
            return
        if math.hypot(p.cx - self.cx, p.cy - self.cy) < 200:
            self.vx = 0
            self.facing = 1 if p.cx > self.cx else -1          # curious: they watch the dragon
            return
        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(1.5, 4.0)
            self.facing = random.choice((-1, 1))
            self.vx = self.facing * random.choice((0, 35, 35))
        if abs(self.cx - self.home[0]) > 2 * TILE:
            self.facing = 1 if self.home[0] > self.cx else -1
            self.vx = self.facing * 35
        if self.on_ground and (self.ledge_ahead(play.level) or self.wall_ahead(play.level)):
            self.vx = 0


class Vampire(Creature):
    """Blutsauger – leaping undead from the deep. No blood of their own to drink."""
    kind = "vampire"
    hostile = True
    w, h = 30, 44
    max_hp = 50
    contact = 14

    def __init__(self, x, y, oid):
        super().__init__(x, y, oid)
        self.leap = random.uniform(1.0, 2.0)

    def think(self, dt, play):
        t = play.target_of(self)
        dx = t.cx - self.cx
        self.facing = 1 if dx > 0 else -1
        self.leap -= dt
        if self.on_ground:
            self.vx = self.facing * 85
            if self.wall_ahead(play.level):
                self.vy = -800
            elif abs(dx) < 190 and self.leap <= 0:
                self.leap = 2.0
                self.vx = self.facing * 330
                self.vy = -520


class GroveQuest:
    WAVES = [
        [("skeleton", 0), ("skeleton", 2), ("skeleton", 4)],
        [("skeleton", 0), ("skeleton", 3), ("skull", 1), ("skull", 5)],
        [("vampire", 0), ("vampire", 3), ("skeleton", 5), ("skull", 2), ("skull", 6)],
    ]
    SPAWN_X = X(179)       # they drop from the darkness in the middle of the hall
    SPAWN_Y = 30
    MEET_X = X(161)
    WAVE_TIMEOUT = 45.0    # stragglers that got stuck somewhere crumble back into shadow

    def __init__(self, play):
        self.play = play
        self.elves = [c for c in play.creatures if c.kind == "elf"]
        self.monsters = []
        self.mode = None
        self.met_as = None
        self.wave = 0
        self.wave_t = 0.0
        self.timer = 0.0
        self.player_kills = 0
        self.nuzzle_cool = 0.0
        flags = play.flags
        self.outcome = next((f[6:] for f in flags if f.startswith("grove_") and f != "grove_done"), None)
        self.state = "done" if "grove_done" in flags else "idle"
        # restore what happened before the last save
        gone = set()
        if self.outcome == "dead":
            gone = {"sera", "erila"}
        if "sera_dead" in flags:
            gone.add("sera")
        if "erila_gone" in flags or "erila_dead" in flags:
            gone.add("erila")
        if gone:
            play.creatures = [c for c in play.creatures if c.id not in gone]
            self.elves = [e for e in self.elves if e.id not in gone]
        if self.outcome == "hostile":
            for e in self.elves:
                e.hostile = e.role == "archer"
                e.leaving = e.role == "healer"
        # the Elfendorf's villagers stay inside their houses until the attack is over
        self.villagers = [Villager(o["x"], o["y"], o["id"], o["name"])
                          for o in play.level.objects if o["kind"] == "villager"]
        self.village_out = False

    # ---- the village ----------------------------------------------------------
    def village_open(self):
        return (self.state == "done" and self.outcome in ("friends", "wary", "alone")
                and self.play.morality.trust() != "gone")

    def update_village(self):
        play = self.play
        if not self.village_out and self.village_open():
            self.village_out = True
            play.creatures += [v for v in self.villagers if v.alive]
        elif self.village_out and play.morality.trust() == "gone":
            for v in self.villagers:                    # they hide from what she has become
                v.leaving = True

    def talk_villager(self, v):
        play = self.play
        stage = play.player.stage
        memory = f"vil_{v.name.lower()}"
        lines = []
        if self.outcome == "alone":
            lines.append((v.name, texts.VILLAGE_TALK["cold"]))
        elif self.outcome == "wary":
            lines.append((v.name, texts.VILLAGE_TALK["wary"]))
        else:
            if play.grew_since(memory):
                lines.append((v.name, texts.VILLAGE_TALK["grew"]))
            talk = texts.VILLAGERS[v.name]["talk"]
            lines.append((v.name, talk[v.talk_i % len(talk)]))
            v.talk_i += 1
        play.remember_age(memory)
        play.dialog.show(lines)

    # ---- helpers ------------------------------------------------------------
    def in_grove(self):
        p = self.play.player
        return self.play.level.in_grove(p.cx, p.cy)

    def affection_active(self):
        return any(isinstance(s, AffectionSubpath) for s in self.play.morality.subpaths())

    def friendly_to_player(self):
        return self.mode in ("help", "nuzzle") or self.outcome in ("friends",)

    def camp_open(self):
        return self.outcome == "friends" and self.play.morality.trust() != "gone"

    def target_of(self, monster):
        """Monsters hunt the nearest elf – and Shadowra only if she fights them or comes too close."""
        p = self.play.player
        cands = [e for e in self.elves if e.alive]
        hunts_her = self.mode in ("help", "nuzzle") or getattr(monster, "aggro", False)
        if hunts_her or math.hypot(p.cx - monster.cx, p.cy - monster.cy) < 180 or not cands:
            cands.append(p)
        return min(cands, key=lambda c: abs(c.cx - monster.cx) + abs(c.cy - monster.cy))

    # ---- flow ---------------------------------------------------------------
    def update(self, dt):
        self.nuzzle_cool = max(0.0, self.nuzzle_cool - dt)
        play = self.play
        p = play.player
        self.update_village()
        if self.state == "idle":
            if self.in_grove() and p.cx > self.MEET_X * TILE and not play.dialog.active:
                self.meet()
            return
        if self.state != "fight":
            return
        self.monsters = [m for m in self.monsters if m.alive]
        self.wave_t += dt
        if self.monsters and self.wave_t > self.WAVE_TIMEOUT:
            for m in self.monsters:
                m.alive, m.corpse_t = False, 0
                play.particles.burst(m.cx, m.cy, (30, 10, 40), 16, 120)
            self.monsters = []
        alive = [e for e in self.elves if e.alive]
        if not alive:
            self.finish_dead()
            return
        if self.mode == "decline" and not self.in_grove():
            for m in self.monsters:          # she left: the elves fight it out on their own
                m.alive, m.corpse_t = False, 0
            self.monsters = []
            if random.random() < 0.5:        # same odds as when she stays and watches
                self.finish_won()
            else:
                for e in self.elves:
                    e.alive, e.hp, e.corpse_t = False, 0, 1e9
                self.finish_dead(absent=True)
            return
        # monsters claw at the elves; Shadowra's shadow protects them in "nuzzle" mode
        for m in self.monsters:
            if not m.contact or m.stun > 0:
                continue
            for e in alive:
                if overlap(m.rect(), e.rect()):
                    dmg = m.contact
                    if self.mode == "nuzzle" and math.hypot(p.cx - e.cx, p.cy - e.cy) < 150:
                        dmg *= 0.4
                    e.monster_hit(dmg, m.cx)
        if not self.monsters:
            self.timer += dt
            if self.timer > 2.5:
                self.timer = 0.0
                if self.wave + 1 < len(self.WAVES):
                    self.wave += 1
                    self.spawn_wave()
                else:
                    self.finish_won()

    def meet(self):
        play = self.play
        self.state = "meeting"
        trust = play.morality.trust()
        self.met_as = trust
        play.remember_age("elves")
        if trust == "gone":
            play.dialog.show(texts.GROVE["meet_hostile"], on_done=self.turn_hostile)
            return
        opts = list(texts.GROVE["choice"])
        if trust == "trust" and self.affection_active():
            opts.append(texts.GROVE["choice_nuzzle"])
        lines = texts.aged(texts.GROVE["meet_trust"] if trust == "trust" else texts.GROVE["meet_afraid"],
                           play.player.stage)
        play.remember_age("elves")
        play.dialog.show(texts.aged(lines, play.player.stage), choice=(opts, self.choose))

    def choose(self, i):
        self.mode = ("help", "decline", "nuzzle")[i]
        self.play.dialog.show(texts.GROVE[self.mode], on_done=self.start_fight)

    def start_fight(self):
        self.state = "fight"
        self.wave = 0
        self.spawn_wave()

    def spawn_wave(self):
        play = self.play
        self.wave_t = 0.0
        for i, (kind, off) in enumerate(self.WAVES[self.wave]):
            tx = self.SPAWN_X + off * 2
            if kind == "skull":
                m = Skull(tx, self.SPAWN_Y, f"grove_w{self.wave}_{i}")
            elif kind == "vampire":
                m = Vampire(tx, self.SPAWN_Y, f"grove_w{self.wave}_{i}")
            else:
                m = Skeleton(tx, self.SPAWN_Y, f"grove_w{self.wave}_{i}")
            m.grove = True
            m.aggro = False
            play.creatures.append(m)
            self.monsters.append(m)
            play.particles.burst(m.cx, m.cy, (30, 10, 40), 16, 120)
        play.toast(texts.GROVE["wave"].format(n=self.wave + 1, total=len(self.WAVES)))

    def finish_won(self):
        play = self.play
        p = play.player
        self.state = "done"
        helped = self.mode in ("help", "nuzzle") or self.player_kills >= 3
        if helped and self.met_as == "trust":
            self.outcome = "friends"
            play.record_event("elves")
            p.hp, p.mana = p.max_hp(), p.max_mana()        # Erila's healing and Mondtau
            play.morality.mark("kindness", 3)
            lines = list(texts.GROVE["won_friends"])
            if self.mode == "nuzzle":
                lines += texts.GROVE["won_nuzzle_extra"]
            if "moon_dew" not in p.abilities:               # the elves' gift (elfvillage/abilities.json)
                from . import abilities
                p.abilities.add("moon_dew")
                play.record_event("gift", "moon_dew")
                lines += [texts.SNOW["moon_dew"],
                          (texts.UI["new_item"] + abilities.name("moon_dew"), abilities.desc("moon_dew"))]
        elif helped:
            self.outcome = "wary"
            p.hp = min(p.max_hp(), p.hp + p.max_hp() * 0.5)
            play.morality.mark("kindness", 2)
            lines = texts.GROVE["won_afraid"]
        else:
            self.outcome = "alone"
            lines = texts.GROVE["won_alone"]
        play.flags |= {"grove_done", f"grove_{self.outcome}"}
        play.dialog.show(lines)

    def finish_dead(self, absent=False):
        play = self.play
        self.state = "done"
        self.outcome = "dead"
        for m in self.monsters:
            m.aggro = True
        if absent:                                            # she wasn't there to see it
            play.flags |= {"grove_done", "grove_dead"}
            return
        if self.mode == "decline" and self.in_grove():
            play.morality.add(madness=6, deed="horror")       # she watched them die
            play.dialog.show(texts.GROVE["dead_watched"])
        else:
            play.morality.add(madness=3, deed="horror")
            play.dialog.show(texts.GROVE["dead_helped"])
        play.flags |= {"grove_done", "grove_dead"}

    def turn_hostile(self):
        self.state = "done"
        self.outcome = "hostile"
        for e in self.elves:
            if e.role == "archer":
                e.hostile = True
            else:
                e.leaving = True
        self.play.flags |= {"grove_done", "grove_hostile", "erila_gone"}

    # ---- interaction ----------------------------------------------------------
    def talk(self, elf):
        play = self.play
        if not elf.alive or elf.hostile or elf.leaving:
            return
        if self.state == "fight":
            return
        stage = play.player.stage
        if self.outcome == "friends":
            key = "talk_turned" if play.morality.trust() == "gone" else "talk_friends"
        else:
            key = "talk_alone"
        lines = list(texts.aged(texts.GROVE[key], stage))
        if key == "talk_friends" and play.grew_since("elves"):
            lines = list(texts.GROVE["grew"]) + lines      # "Bei den Sternen – du bist gewachsen!"
        play.remember_age("elves")
        play.dialog.show(lines)

    def can_nuzzle(self):
        """'Anschmiegen' is offered in the elf menu while Zuneigung is active and they trust her."""
        return (self.affection_active() and self.mode != "decline" and self.outcome in (None, "friends")
                and self.play.morality.trust() == "trust")

    def nuzzle(self, elf):
        play = self.play
        p = play.player
        if play.rest:
            return
        play.rest = dict(kind="nuzzle", t=0.0, dur=1.6, heal=p.max_hp() * 0.1, elf=elf)
        p.pose_override = "nuzzle"
        p.vx = 0
        p.facing = 1 if elf.cx > p.cx else -1
        play.toast(texts.GROVE["nuzzle_again"].format(name=elf.name), key="nuzzle")
        if self.nuzzle_cool <= 0:
            self.nuzzle_cool = 30.0
            play.morality.mark("kindness", 0.5)

    def elf_killed(self, elf):
        """Shadowra killed an elf that had turned on her."""
        self.play.morality.add(madness=5, deed="horror")
        self.play.flags.add(f"{elf.id}_dead")
