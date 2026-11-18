"""The playing state: world simulation, interactions, rests, cutscenes, boss and saving."""
import math
import random

import pygame

from .settings import (TILE, SCREEN_W, SCREEN_H, SUN_DMG, LAVA_LIGHT_DMG, TORCH_DMG, VEIL_DRAIN_SUN,
                       VEIL_DRAIN_LAVA, VEIL_DRAIN_TORCH, VEIL_EMPTY_DMG, GROWTH_NEED, STAGES,
                       TEXT, TEXT_DIM, LIGHT_COL, LAVA_COL, SPIKE_DMG, FIRE_DPS, DAY_DMG, VEIL_DRAIN_DAY,
                       SHRINE_EXPOSURE_RATE, SHRINE_DMG)
from .world import Level, X, GROVE, LAVA, MEADOW, PLATEAU, VALE, VALE_W, SHADOW_STONES
from .player import Player
from .morality import Morality
from .creatures import KINDS, Particles, Projectile, Mafor, Fish, FiraCompanion
from .snow import Snowlands, SNOW_DECOR
from .grove import GroveQuest, Elf
from .hugs import Hugs
from .hud import Hud, Dialog
from .assets import font
from . import abilities, cheats, render, save, texts

DEV_TELEPORTS = [(16, 39), (66, 37), (MEADOW[0] + 1, 37), (MEADOW[0] + 40, 37), (VALE[0] + 1, 37),
                 (VALE[0] + 66, 37), (X(117), 37), (X(148), 45), (X(155), 17), (X(170), 17), (X(224), 17),
                 (PLATEAU[0] + 38, 17), (X(264), 14), (X(305), 11)]
WORLD_VERSION = 3          # 2 = + Sonnenwiesen / Gleißende Hochebene, 3 = + Tal der Schattensteine


def migrate_world_v1(data):
    """Saves from older map versions: move positions into the current, larger world."""
    version = data.get("world_version", 1)
    if version == 1:
        shift = X                                   # original coordinates -> today's world
    else:                                           # v2: everything east of the meadow moved by the valley
        def shift(x):
            return x + VALE_W if x >= VALE[0] else x
    p = data["player"]
    old_tx = int((p["x"] + 1) // TILE)
    p["x"] += (shift(old_tx) - old_tx) * TILE
    w = data.setdefault("world", {})
    w["broken"] = [[shift(x), y] for x, y in w.get("broken", [])]
    w["burned"] = [[shift(x), y] for x, y in w.get("burned", [])]
    data["world_version"] = WORLD_VERSION
    return data


def overlap(a, b):
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]


class Play:
    def __init__(self, game, data=None):
        self.game = game
        self.sprites = game.sprites
        self.hud = Hud()
        self.dialog = Dialog()
        self.particles = Particles()
        if data and data.get("world_version", 1) < WORLD_VERSION:
            data = migrate_world_v1(data)
        world = (data or {}).get("world", {})
        self.broken = [tuple(p) for p in world.get("broken", [])]
        self.burned = [tuple(p) for p in world.get("burned", [])]
        self.level = Level(self.broken, self.burned)
        self.picked = set(world.get("picked", []))
        self.flags = set(world.get("flags", []))
        self.morality = Morality((data or {}).get("morality"))
        self.morality.stage = ((data or {}).get("player") or {}).get("stage", 0)
        self.checkpoint = (data or {}).get("checkpoint", "N")
        self.t = world.get("t", 0.0)
        self.session_flags = set()
        self.journey = []               # recorded path since the last save (credits replay)
        self.rec_acc = 0.0
        self.rec_last = None

        self.altars, self.items, self.triggers, self.decor, self.shrines = [], [], [], [], []
        self.snow_objects = []
        self.creatures, self.projectiles = [], []
        self.boss = self.fira = None
        self.fish_respawn = []
        start = (16, 39)
        default_stock = {}
        for o in self.level.objects:
            k = o["kind"]
            if k == "altar":
                default_stock[o["id"]] = dict(o["stock"])
                self.altars.append(o)
            elif k == "start":
                start = (o["x"], o["y"])
            elif k in ("crystal", "relic"):
                if o["id"] not in self.picked:
                    self.items.append(o)
            elif k in ("birds", "storm", "noreturn", "gate_hint", "sun_intro", "vale_gate"):
                self.triggers.append(o)
            elif k in ("sun_shrine", "burrow", "shadow_stone"):
                self.shrines.append(o)          # simple "press E here" spots
            elif k == "boss":
                if "mafor_defeated" in self.flags:           # the story goes on after Mafor
                    continue
                self.boss = Mafor(o["x"], o["y"], o["id"], o["arena_left"])
                floor = (o["y"] + 6) * TILE
                self.boss.floor_y = floor - self.boss.h
                self.boss.base_y = floor - self.boss.h - 110
                self.boss.y = self.boss.base_y
            elif k == "decor":
                self.decor.append(o)
            elif k == "elf":
                self.creatures.append(Elf(o["x"], o["y"], o["id"], o["name"]))
            elif k in ("passage", "hearth", "human", "otters", "snow_intro", "snow_arrive", "chapter_end"):
                self.snow_objects.append(o)                  # Frostpass and the snowlands (snow.py)
            elif k in KINDS:
                if k == "owl" and self.morality.trust() == "gone":
                    continue
                if k == "fira" and self.flags & {"fira_joined", "fira_dead"}:
                    continue                                 # he walks with her now – or he is gone
                c = KINDS[k](o["x"], o["y"], o["id"])
                if k == "fira":
                    self.fira = c
                if k == "owl":
                    c.talked = "owl_talked" in self.flags
                    c.gift_given = "owl_gift" in self.flags
                self.creatures.append(c)
        self.stock = dict(default_stock)
        self.stock.update(world.get("stock") or {})      # old saves don't know newer altars yet
        self.grove = GroveQuest(self)
        if "vale_gate_open" in self.flags:
            self.level.open_vale_gate()
        self.hugs = Hugs(self, world.get("hugs"))
        self.violence_t = -99.0          # last time she hurt anything – peaceful creatures stay wary

        if data and "player" in data:
            self.player = Player.from_dict(data["player"])
        else:
            p = Player(0, 0, 0)
            p.x = start[0] * TILE + TILE / 2 - p.w / 2
            p.y = (start[1] + 1) * TILE - p.h
            self.player = p
        self.companion = None
        if "fira_joined" in self.flags:                  # light / redemption: Fira walks with her
            self.companion = FiraCompanion(0, 0)
            self.companion.x = self.player.cx - 80 - self.companion.w / 2
            self.companion.y = self.player.feet - self.companion.h
            self.creatures.append(self.companion)
        self.snow = Snowlands(self)                      # cold, the Frostpass, humans, otters, diving
        self.ward = None                                 # the rest spot whose ward protects her right now
        self.cheats = cheats.load()                      # active cheats (src/controls/xheats.json)
        self.cam = [self.player.cx - SCREEN_W / 2, self.player.cy - SCREEN_H / 2]
        self.clamp_cam()
        self.rest = None
        self.fourth_wall = None            # CloseUp while she talks to the player directly
        self.cutscene = None
        self.death_t = None
        self.fade_in = 1.0
        self.zone = ""
        self.boss_done = False
        self.end_t = None
        self.end_key = None
        self.prompt = None
        self.tile_art = game.tile_art
        self.backdrop = game.backdrop
        self.cave_mix = 1.0 if self.level.is_cave(self.player.cx, self.player.cy) else 0.0
        self.lava_mix = 0.0
        self.grove_mix = 0.0
        self.day_mix = 1.0 if self.level.day_zone(self.player.cx) else 0.0
        self.snow_mix = 1.0 if self.level.in_snow(self.player.cx) else 0.0
        self.under_mix = 0.0
        self.ice_mix = 0.0
        self.halluc = []

        if not data:
            self.flags.add("intro")
            self.dialog.show(texts.INTRO)
            self.save_game("N")

    # ------------------------------------------------------------------
    # helpers used by the player
    # ------------------------------------------------------------------
    # ---- journey recording (credits replay) ------------------------------------
    REC_HZ = 8.0
    SKIP_POSES = ("eat", "curl_eat", "sleep", "dead", "endure")

    def record(self, dt):
        """Sample Shadowra's movement ~8x per second. Standing still and resting are left out."""
        p = self.player
        if p.dead or self.death_t is not None:
            return
        self.rec_acc += dt
        if self.rec_acc < 1.0 / self.REC_HZ:
            return
        self.rec_acc = 0.0
        pose = p.pose()
        if pose in self.SKIP_POSES:
            return
        sample = (round(p.cx, 1), round(p.feet, 1), p.stage, pose, p.facing, round(p.flap_anim, 2), None)
        last = self.rec_last
        if last and abs(last[0] - sample[0]) < 2 and abs(last[1] - sample[1]) < 2 and last[3] == pose:
            return                                       # nothing happens: skip the boring frames
        self.rec_last = sample
        self.journey.append(sample)

    def record_event(self, key, ref=None):
        """A milestone shown as a caption in the replay. Stored language-neutral ("@relic:veil"),
        so the credits show it in whatever language is chosen then (texts.replay_caption)."""
        p = self.player
        text = f"@{key}" + (f":{ref}" if ref is not None else "")
        self.journey.append((round(p.cx, 1), round(p.feet, 1), p.stage, p.pose(), p.facing, 0.0, text))

    def toast(self, text, key=None):
        self.hud.toast(text, key=key)

    def input_locked(self):
        return (self.dialog.active or self.rest is not None or self.death_t is not None
                or self.end_t is not None or self.fourth_wall is not None)

    def spawn_spike(self, p):
        y = p.y + p.h * 0.35
        x = p.x + p.w if p.facing > 0 else p.x
        mult = p.spell_mult()                        # adult + Manaschulung: harder-hitting spikes
        self.projectiles.append(Projectile(x, y, p.facing * 620, 0, SPIKE_DMG * mult, "player", "spike",
                                           r=5 if mult <= 1 else 7, life=1.2))

    def spawn_enemy_orb(self, x, y, ang, speed, dmg):
        self.projectiles.append(Projectile(x, y, math.cos(ang) * speed, math.sin(ang) * speed,
                                           dmg, "enemy", "orb", r=8, life=4.0))

    def spawn_arrow(self, elf, tx, ty, owner):
        """Sera's arrows: owner "elf" hits monsters, owner "enemy" hits Shadowra."""
        x, y = elf.cx + elf.facing * 12, elf.y + 16
        ang = math.atan2(ty - y, tx - x)
        self.projectiles.append(Projectile(x, y, math.cos(ang) * 560, math.sin(ang) * 560,
                                           12, owner, "arrow", r=5, life=1.5))

    def spawn_spear(self, hunter, tx, ty):
        """A hostile hunter in the snow throws a spear at Shadowra."""
        from .humans import THROW_DMG
        x, y = hunter.cx + hunter.facing * 14, hunter.y + 20
        ang = math.atan2(ty - y, tx - x) - 0.12            # a slight arc
        self.projectiles.append(Projectile(x, y, math.cos(ang) * 470, math.sin(ang) * 470,
                                           THROW_DMG, "enemy", "spear", r=6, life=1.6))

    def threatening(self):
        """Is Shadowra acting dangerous right now? Calm walking lets shy creatures stay."""
        p = self.player
        return (p.attack is not None or p.fire_on or p.dash_t > 0 or p.diving
                or abs(p.vx) > p.s["walk"] * 1.25 or self.t - self.violence_t < 4.0)

    @staticmethod
    def friendly(c):
        return getattr(c, "friendly", False)

    def target_of(self, c):
        """Who a monster hunts: grove monsters may go for the elves instead of Shadowra."""
        if getattr(c, "grove", False) and self.grove:
            return self.grove.target_of(c)
        return self.player

    def summon_priests(self, boss):
        from .creatures import Priest
        for dx in (-6, 6):
            tx = int(boss.cx // TILE) + dx
            pr = Priest(tx, 11, f"summon{dx}")
            self.creatures.append(pr)
            self.particles.burst(pr.cx, pr.cy, LIGHT_COL, 30, 200)

    def dive_impact(self, p):
        self.particles.burst(p.cx, p.feet, (60, 20, 90), 40, 300)
        self.game.shake = 0.3
        for c in self.creatures + ([self.boss] if self.boss else []):
            if c.alive and not self.friendly(c) and math.hypot(c.cx - p.cx, c.cy - p.feet) < 110:
                self.damage_creature(c, 25, p.cx, knock=200)
                c.stun = 1.2

    # ------------------------------------------------------------------
    # saving
    # ------------------------------------------------------------------
    def save_game(self, altar_id):
        self.checkpoint = altar_id
        p = self.player
        a = next((a for a in self.altars if a["id"] == altar_id), None)
        pd = p.to_dict()
        if a:
            pd["x"] = a["x"] * TILE + TILE / 2 - p.w / 2 + 40
            pd["y"] = (a["y"] + 1) * TILE - p.h
        data = dict(player=pd, morality=self.morality.to_dict(), checkpoint=altar_id, world_version=WORLD_VERSION,
                    world=dict(broken=self.broken, burned=self.burned, picked=sorted(self.picked),
                               stock=self.stock, flags=sorted(self.flags), t=self.t,
                               hugs=self.hugs.count))
        save.write(data)
        save.append_journey(self.journey)       # this stretch led to a save: keep it for the credits
        self.journey = []

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------
    def update(self, dt, ctl):
        self.t += dt
        self.fade_in = max(0.0, self.fade_in - dt)
        self.hud.update(dt)
        self.particles.update(dt)
        p = self.player
        self.morality.stage = p.stage                    # extra morals can depend on her age

        if self.game.dev:
            self.dev_keys()

        if self.death_t is not None:
            self.death_t += dt
            if self.death_t > 2.4:
                self.game.continue_game()
            return
        if self.end_t is not None:
            self.end_t += dt
            if self.end_t > 2.0:
                self.game.show_ending(self.end_key, self.morality)
            return
        if self.fourth_wall:                             # the world holds still while she talks to the player
            self.update_fourth_wall(dt, ctl)
            return

        if self.dialog.active:
            self.dialog.update(dt, ctl)
        elif self.rest:
            self.update_rest(dt)
        else:
            if ctl.hit("interact"):
                self.interact()

        p.update(dt, ctl, self)
        self.record(dt)
        self.snow.update(dt)                             # cold, breath, grief, the snowlands' events
        if not self.dialog.active:
            self.update_world(dt)
        cheats.apply(self, self.cheats)                  # src/controls/xheats.json

        if p.dead and self.death_t is None:
            self.death_t = 0.0
            p.pose_override = "dead"
            self.particles.burst(p.cx, p.cy, (40, 10, 50), 40, 200)

        # learning blood in an emergency
        if (p.stage >= 1 and "blood" not in p.abilities and not p.dead
                and p.hp < p.max_hp() * 0.35 and not self.dialog.active):
            p.abilities.add("blood")
            self.record_event("blood")
            self.dialog.show(texts.BLOOD_LEARNED)

        zone = self.level.zone_name(p.cx, p.cy)
        if zone != self.zone:
            self.zone = zone
            self.hud.banner(zone)
        self.update_camera(dt)

    def update_world(self, dt):
        p = self.player
        lvl = self.level
        # creatures
        battle = self.grove.state == "fight"
        in_grove = lvl.in_grove(p.cx, p.cy)
        near = [c for c in self.creatures if abs(c.cx - p.cx) < 1500
                or (c.kind in ("elf", "villager") and in_grove)
                or (battle and getattr(c, "grove", False))]
        for c in near:
            c.update(dt, self)
            if isinstance(c, Fish) and not c.alive:
                self.creatures.remove(c)
                self.fish_respawn.append([45.0, c])
        if self.boss and abs(self.boss.cx - p.cx) < 1500:
            self.boss.update(dt, self)
        self.grove.update(dt)
        self.update_ward()                               # rest spots: nothing hostile comes close to her
        self.creatures = [c for c in self.creatures if c.alive or c.corpse_t > 0]
        for r in self.fish_respawn:
            r[0] -= dt
            if r[0] <= 0 and abs(r[1].home[0] - p.cx) > SCREEN_W * 0.6:
                fx = int(r[1].home[0] // TILE)
                fy = int(r[1].home[1] // TILE)
                self.creatures.append(Fish(fx, fy, r[1].id))
        self.fish_respawn = [r for r in self.fish_respawn if r[0] > 0]

        # owl reacts to what she has become
        for c in self.creatures:
            if c.kind == "owl" and c.alive and not c.leaving and self.morality.trust() == "gone":
                if abs(c.cx - p.cx) < 400:
                    c.leaving = True

        # projectiles
        for pr in self.projectiles:
            pr.update(dt, lvl)
            if not pr.alive:
                continue
            pr_box = (pr.x - pr.r, pr.y - pr.r, pr.r * 2, pr.r * 2)
            if pr.owner == "player":
                for c in self.creatures + ([self.boss] if self.boss and self.boss.active else []):
                    if (c.alive and c.kind not in ("fira", "owl") and not self.friendly(c)
                            and overlap(pr_box, c.rect())):
                        self.damage_creature(c, pr.dmg, pr.x, knock=80)
                        pr.alive = False
                        self.particles.burst(pr.x, pr.y, (120, 80, 200), 8, 120)
                        break
            elif pr.owner == "elf":
                for c in self.creatures:
                    if c.alive and c.hostile and c.kind != "elf" and overlap(pr_box, c.rect()):
                        c.hurt(pr.dmg, pr.x, knock=60)       # the elves' kills are not hers
                        pr.alive = False
                        self.particles.burst(pr.x, pr.y, (200, 230, 200), 6, 100)
                        break
            else:
                if overlap((pr.x - pr.r, pr.y - pr.r, pr.r * 2, pr.r * 2), p.rect()):
                    if p.hurt(pr.dmg, pr.x):
                        self.particles.burst(pr.x, pr.y, LIGHT_COL, 10, 150)
                    pr.alive = False
        self.projectiles = [pr for pr in self.projectiles if pr.alive]

        if p.dead or self.death_t is not None or self.end_t is not None:
            return
        self.player_combat(dt)
        self.player_light(dt)
        self.check_pickups()
        self.check_triggers()
        self.update_boss_flow()
        self.update_hallucinations(dt)

    # ------------------------------------------------------------------
    def damage_creature(self, c, dmg, from_x, knock=150):
        was_alive = c.alive
        self.violence_t = self.t
        if not c.hurt(dmg, from_x, knock=knock, play=self):
            return
        self.particles.burst(c.cx, c.cy, (170, 30, 50) if c.blood else (200, 200, 190), 6, 120)
        if getattr(c, "grove", False):
            c.aggro = True                       # she attacked it – now it hunts her too
        if was_alive and not c.alive:
            if getattr(c, "grove", False):
                self.grove.player_kills += 1
            if c.kind == "elf":
                self.grove.elf_killed(c)
            elif c.kind == "peaceful":
                self.morality.add(wild=5, deed=self.hunt_deed())
            elif c.kind == "owl":
                self.morality.add(madness=8, abhorrent=1, deed="horror")
                self.flags.add("owl_dead")
            elif c.kind == "human":                      # a hunter who attacked her – it still weighs on her
                self.morality.add(wild=4, madness=2, deed="horror")

    def player_combat(self, dt):
        p = self.player
        lvl = self.level
        box = p.attack_box()
        if box:
            a = p.attack
            targets = self.creatures + ([self.boss] if self.boss and self.boss.active else [])
            for c in targets:
                if c.id in a["hit"] or not c.alive or c.kind == "fira" or self.friendly(c):
                    continue
                if overlap(box, c.rect()):
                    a["hit"].add(c.id)
                    if c.kind == "fish":
                        self.catch_fish(c)
                        continue
                    knock = 420 if a["kind"] == "tail" else 160
                    self.damage_creature(c, a["dmg"], p.cx, knock=knock)
                    if a["kind"] == "claw" and "obsidian" in p.abilities and c.alive and c.blood:
                        c.hp -= 2      # obsidian claws make them bleed
            if a["kind"] == "tail":
                for pr in self.projectiles:
                    if pr.owner == "enemy" and overlap(box, (pr.x - pr.r, pr.y - pr.r, pr.r * 2, pr.r * 2)):
                        pr.owner, pr.vx, pr.vy = "player", -pr.vx * 1.2, -pr.vy * 1.2
            if a["kind"] == "claw":
                hit_wall = None
                for ty in range(int(box[1] // TILE), int((box[1] + box[3]) // TILE) + 1):
                    for tx in range(int(box[0] // TILE), int((box[0] + box[2]) // TILE) + 1):
                        if lvl.tile(tx, ty) == "C":
                            hit_wall = (tx, ty)
                if hit_wall:
                    if "obsidian" in p.abilities:
                        removed = lvl.break_wall(*hit_wall)
                        self.broken += removed
                        for (x, y) in removed:
                            self.particles.burst(x * TILE + 16, y * TILE + 16, (90, 70, 80), 6, 200)
                        self.game.shake = 0.25
                    else:
                        self.toast(texts.TOASTS["too_hard"], key="too_hard")
        fb = p.fire_box()
        if fb:
            for i in range(3):
                fx = fb[0] + random.random() * fb[2]
                fy = fb[1] + random.random() * fb[3]
                self.particles.items.append([fx, fy, p.facing * 80, -30, 0.35, 0.35,
                                             random.choice(((90, 30, 140), (150, 60, 200), (40, 10, 60))), 5])
            for c in self.creatures + ([self.boss] if self.boss and self.boss.active else []):
                if c.alive and c.kind not in ("fira",) and not self.friendly(c) and overlap(fb, c.rect()):
                    if c.kind == "fish":
                        continue
                    self.damage_creature(c, FIRE_DPS * p.spell_mult() * dt, p.cx, knock=0)
            for ty in range(int(fb[1] // TILE), int((fb[1] + fb[3]) // TILE) + 1):
                for tx in range(int(fb[0] // TILE), int((fb[0] + fb[2]) // TILE) + 1):
                    if lvl.tile(tx, ty) == "V":
                        removed = lvl.burn_vines(tx, ty)
                        self.burned += removed
                        for (x, y) in removed:
                            self.particles.burst(x * TILE + 16, y * TILE + 16, (255, 140, 60), 8, 160)
                    elif lvl.tile(tx, ty) == "I":                    # the Eishöhle: fire melts the ice wall
                        removed = lvl.melt_ice(tx, ty)
                        self.burned += removed
                        for (x, y) in removed:
                            self.particles.burst(x * TILE + 16, y * TILE + 16, (190, 226, 255), 8, 140)
        elif p.attack is None and not p.fire_on:
            # hint when walking into vines / ice
            if lvl.rect_has(p.x - 4, p.y, p.w + 8, p.h, "V"):
                self.toast(texts.TOASTS["vines"], key="vines")
            elif lvl.rect_has(p.x - 4, p.y, p.w + 8, p.h, "I"):
                self.toast(texts.SNOW["melt_hint"], key="melt_hint")

        # contact damage
        for c in self.creatures + ([self.boss] if self.boss and self.boss.active and not self.boss.defeated else []):
            if c.alive and c.hostile and c.contact and c.stun <= 0 and overlap(c.rect(), p.rect()):
                p.hurt(c.contact, c.cx)

    def catch_fish(self, fish):
        p = self.player
        if p.stage == 0:
            self.toast(texts.TOASTS["fish_young"], key="fish_young")
            fish.facing *= -1
            return
        fish.alive = False
        self.eat("fish", amount=1.0)
        self.toast(texts.TOASTS["fish_eat"])
        self.particles.burst(fish.cx, fish.cy, (180, 200, 230), 10, 100)

    def eat(self, food, amount=1.0, at_altar=False):
        """Food heals and refills stamina; it also counts towards growth for the right age."""
        p = self.player
        mods = self.morality.mods()
        mult = mods["food_heal"]
        heal = {"milk": 0.45, "fish": 0.3, "meat": 0.45}[food] * p.max_hp() * mult * amount
        stam = p.max_stam(mods) * (0.6 if not at_altar else 1.0)
        p.hunger_time = 0
        need = GROWTH_NEED.get(p.stage)
        if need and need[0] == food:
            p.food[food] += 1
            if p.food[food] == need[1]:
                self.toast(texts.TOASTS["growth_ready"])
        if at_altar:
            return heal, stam
        p.hp = min(p.max_hp(), p.hp + heal)
        p.stamina = min(p.max_stam(mods), p.stamina + stam)
        return heal, stam

    def gain_sun_exposure(self, seconds):
        """Lichtgewöhnung grows with every second in sunlight; toast at 25/50/75 %."""
        p = self.player
        before = int(p.adaptation() * 4)
        p.sun_exposure += seconds
        after = int(p.adaptation() * 4)
        if after > before:
            self.toast(texts.TOASTS["sun_adapt"].format(pct=after * 25))

    def player_light(self, dt):
        p = self.player
        lvl = self.level
        kind = None
        if lvl.sun_at(p.cx, p.cy, self.t):
            kind = "sun"
        elif lvl.sunlit(p.cx, p.cy, self.t):
            kind = "day"
        elif lvl.lava_light_at(p.cx, p.cy):
            kind = "lava"
        else:
            for c in self.creatures + ([self.boss] if self.boss else []):
                L = c.light() if hasattr(c, "light") else None
                if L and math.hypot(p.cx - L[0], p.cy - L[1]) < L[2]:
                    kind = "torch"
                    break
            if self.boss and self.boss.strike_rect() and overlap(self.boss.strike_rect(), p.rect()):
                kind = "strike"
        if not kind:
            return
        sunlight = kind in ("sun", "day", "strike")        # real sunlight trains Lichtgewöhnung
        if sunlight:
            self.gain_sun_exposure(dt)
        if "veil" in p.abilities:
            rate = {"sun": VEIL_DRAIN_SUN, "day": VEIL_DRAIN_DAY, "lava": VEIL_DRAIN_LAVA,
                    "torch": VEIL_DRAIN_TORCH, "strike": 30}[kind]
            rate *= self.morality.mods()["veil_drain"]
            if kind == "lava" and "fire" in p.abilities:
                rate *= 0.75
            if sunlight:
                rate *= p.sun_veil_mult()
            if p.mana > 0:
                p.spend_mana(rate * dt)            # holding the veil up trains her magic too
                if random.random() < 0.3:
                    self.particles.burst(p.cx, p.y, (60, 30, 90), 1, 40, up=40)
                return
            dmg = VEIL_EMPTY_DMG if kind != "strike" else 40
        else:
            dmg = {"sun": SUN_DMG, "day": DAY_DMG, "lava": LAVA_LIGHT_DMG, "torch": TORCH_DMG, "strike": 50}[kind]
        if sunlight:
            dmg *= p.sun_dmg_mult()
        p.burn(dmg * dt)
        self.toast(texts.TOASTS["light_burn"], key="burn")
        if random.random() < 0.5:
            self.particles.burst(p.cx + random.uniform(-p.w / 2, p.w / 2), p.y + 4, (120, 110, 110), 1, 40, up=60)

    def check_pickups(self):
        p = self.player
        for it in list(self.items):
            r = (it["x"] * TILE, it["y"] * TILE, TILE, TILE)
            if not overlap(r, p.rect()):
                continue
            self.items.remove(it)
            self.picked.add(it["id"])
            if it["kind"] == "crystal":
                p.mana = min(p.max_mana(), p.mana + 25)
                self.toast(texts.TOASTS["crystal"])
                self.particles.burst(r[0] + 16, r[1] + 16, (150, 90, 230), 16, 140)
            else:
                rel = it["relic"]
                p.abilities.add(rel)
                self.record_event("relic", rel)
                name, desc = abilities.name(rel), abilities.desc(rel)     # src/world/<place>/abilities.json
                self.dialog.show([(texts.UI["new_item"] + name, desc)])
                self.particles.burst(r[0] + 16, r[1] + 16, (200, 120, 255), 40, 220)

    def check_triggers(self):
        p = self.player
        for tr in self.triggers:
            tx, ty = tr["x"] * TILE, tr["y"] * TILE
            near = abs(p.cx - (tx + 16)) < 48 and abs(p.feet - (ty + TILE)) < 40
            if tr["kind"] == "birds" and near and "birds" not in self.flags:
                self.flags.add("birds")
                self.cutscene = dict(kind="birds", t=0.0)
                p.vx = 0

                def done():
                    p.abilities.add("glide")
                    self.record_event("glide")
                    self.cutscene = None
                self.dialog.show(texts.BIRDS, on_done=done)
            elif tr["kind"] == "storm" and near and ("storm" not in self.flags or
                                                    (p.stage == 2 and "flight_seen" not in p.abilities)):
                first = "storm" not in self.flags
                self.flags.add("storm")
                self.cutscene = dict(kind="storm", t=0.0)
                p.vx = 0
                p.abilities.add("flight_seen")
                self.record_event("storm")
                lines = list(texts.STORM_DRAGON) if first else []
                lines.append(texts.STORM_DRAGON_ADULT if p.stage == 2 else texts.STORM_DRAGON_YOUNG)

                def done():
                    self.cutscene = None
                self.dialog.show(lines, on_done=done)
            elif tr["kind"] == "gate_hint" and p.stage < tr["need_stage"] and abs(p.cx - (tx + 16)) < 72 \
                    and abs(p.feet - (ty + TILE)) < 40:
                need = GROWTH_NEED.get(p.stage)
                have = p.food[need[0]] if need else 0
                text = texts.GATE_HINT.format(food=texts.FOOD_NAMES[need[0]], have=min(have, need[1]), need=need[1])
                self.toast(text, key="gate_hint")
            elif tr["kind"] == "vale_gate" and "vale_gate_open" not in self.flags and abs(p.cx - tx) < 3 * TILE:
                self.toast(texts.GATE_CLOSED.format(n=self.stones_awake()), key="vale_gate")
            elif tr["kind"] == "sun_intro" and p.cx > tx and f"sun_intro_{tr['text']}" not in self.flags:
                self.flags.add(f"sun_intro_{tr['text']}")
                p.vx = 0
                self.dialog.show(texts.SUN_INTRO[tr["text"]])
            elif (tr["kind"] == "noreturn" and tx < p.cx < tx + 14 * TILE and abs(p.feet - (ty + TILE)) < 3 * TILE
                  and "noreturn" not in self.session_flags and "mafor_defeated" not in self.flags):
                self.session_flags.add("noreturn")
                if self.morality.doomed():
                    self.dialog.show(texts.NO_RETURN_GREED)
                elif self.morality.close_to_doom():
                    self.dialog.show(texts.NO_RETURN_CLOSE)
                else:
                    self.dialog.show([texts.LAST_REST])

    def update_boss_flow(self):
        b, p = self.boss, self.player
        if not b:
            return
        left = b.arena_left
        on_summit = p.feet < b.floor_y + b.h + 3 * TILE      # (not in the Frostpass tunnel below the arena)
        if not b.active and not self.boss_done and p.x > left + 2 * TILE and on_summit:
            b.active = True
            self.dialog.show(texts.BOSS_INTRO)
        if b.active and not self.boss_done and on_summit:
            if p.x < left:
                p.x = left
                p.vx = 0
            if b.defeated and not self.dialog.active:
                self.boss_done = True
                self.projectiles = [pr for pr in self.projectiles if pr.owner == "player"]
                for c in self.creatures:
                    if c.kind == "priest" and c.id.startswith("summon"):
                        c.alive, c.corpse_t = False, 2.0

                def choose(i):
                    if i == 0:
                        self.morality.boss_choice = "spared"
                        self.morality.add(wild=-5, lust=-3)
                        self.morality.mark("kindness", 3)
                        self.dialog.show([texts.BOSS_SPARED], on_done=self.free_fira)
                    else:
                        self.morality.boss_choice = "devoured"
                        self.morality.add(lust=25, deed="overflow")
                        p.hp, p.mana = p.max_hp(), p.max_mana()
                        self.particles.burst(b.cx, b.cy, LIGHT_COL, 80, 300)
                        self.dialog.show([texts.BOSS_DEVOURED], on_done=self.free_fira)
                    b.active = False
                    b.alive = False
                    b.gone = True
                self.dialog.show(texts.BOSS_DEFEATED, choice=(texts.BOSS_CHOICE, choose))

    # what becomes of Fira in each ending – every ending but greed lets the story go on (snowlands)
    FIRA_FATE = {"light": "fira_joined", "redemption": "fira_joined", "madness": "fira_dead",
                 "obsession": "fira_caged"}

    def free_fira(self):
        if self.fira:
            self.fira.caged = False
            self.particles.burst(self.fira.cx, self.fira.cy, (255, 160, 80), 50, 200)
        self.record_event("mafor")
        save.append_journey(self.journey)       # the final fight belongs to the replay too
        self.journey = []
        save.mark_story_finished()              # the credits close-up knows her story reached its end
        self.end_key = self.morality.ending()
        self.end_t = -1.5
        if self.end_key in self.FIRA_FATE:      # chapter 1 ends – the game is saved so the story can go on
            self.flags.add("mafor_defeated")
            self.flags.add(self.FIRA_FATE[self.end_key])
            self.save_game("A4")

    def update_hallucinations(self, dt):
        if "hallucinations" not in self.morality.debuffs():
            self.halluc = []
            return
        if random.random() < dt * 0.6:
            self.halluc.append([random.uniform(100, SCREEN_W - 100), random.uniform(200, SCREEN_H - 150),
                                random.uniform(0.6, 1.6), random.choice(("eyes", "skeleton", "shadow"))])
        for h in self.halluc:
            h[2] -= dt
        self.halluc = [h for h in self.halluc if h[2] > 0]

    # ------------------------------------------------------------------
    # interaction
    # ------------------------------------------------------------------
    # ---- rest spots are safe -------------------------------------------------------------
    WARD_R = 5 * TILE            # how far the ward of a rest spot reaches (left and right of the altar)

    def altar_usable(self, a):
        """Locked rest spots (the elf camp before they trust her, the humans' hearth) don't protect her."""
        if a.get("locked") and not self.grove.camp_open():
            return False
        return not self.snow.altar_locked(a)

    def active_ward(self):
        """The rest spot Shadowra is standing at (its ward protects her), or None."""
        p = self.player
        for a in self.altars:
            ax, ay = a["x"] * TILE + TILE / 2, (a["y"] + 1) * TILE
            if abs(p.cx - ax) < self.WARD_R and abs(p.feet - ay) < 3 * TILE and self.altar_usable(a):
                return a
        return None

    def update_ward(self):
        """While she is at a rest spot, nothing hostile can come close: creatures are pushed back to the edge
        of the ward and enemy projectiles fizzle out at it – so she can eat, drink and sleep in peace."""
        self.ward = a = self.active_ward()
        if not a:
            return
        ax, ay = a["x"] * TILE + TILE / 2, (a["y"] + 1) * TILE
        R = self.WARD_R
        pushed = False
        for c in self.creatures:
            if not (c.alive and c.hostile):
                continue
            if abs(c.cx - ax) < R and -7 * TILE < c.cy - ay < 2 * TILE:
                side = 1 if c.cx >= ax else -1
                nx = ax + R if side > 0 else ax - R - c.w
                if not self.level.rect_solid(nx, c.y, c.w, c.h - 2):
                    c.x = nx                             # pushed out to the edge of the ward, facing away
                    c.vx = side * 60
                else:                                    # no room outside (a wall): it simply can't move or strike
                    c.vx = 0
                c.stun = max(c.stun, 0.3)
                c.facing = side
                pushed = True
                self.particles.burst(ax + side * R, c.cy, (170, 120, 255), 4, 60)
        for pr in self.projectiles:
            if pr.owner == "enemy" and abs(pr.x - ax) < R and -7 * TILE < pr.y - ay < 2 * TILE:
                pr.alive = False
                self.particles.burst(pr.x, pr.y, (170, 120, 255), 8, 90)
                pushed = True
        if pushed:
            self.toast(texts.TOASTS["ward"], key="ward")

    def nearest_altar(self):
        p = self.player
        for a in self.altars:
            ax = a["x"] * TILE + TILE / 2
            ay = (a["y"] + 1) * TILE
            if abs(p.cx - ax) < 60 and abs(p.feet - ay) < 40:
                return a
        return None

    # ---- Tal der Schattensteine ------------------------------------------------
    def stones_awake(self):
        return sum(1 for s in SHADOW_STONES if f"{s}_awake" in self.flags)

    def wake_stone(self, stone):
        name = texts.STONE_NAMES[stone["id"]]
        if f"{stone['id']}_awake" in self.flags:
            self.toast(texts.STONE_AWAKE.format(name=name), key="stone_awake")
            return
        self.flags.add(f"{stone['id']}_awake")
        self.record_event("stone", stone["id"])
        x, y = stone["x"] * TILE + TILE / 2, stone["y"] * TILE
        self.particles.burst(x, y, (170, 110, 255), 40, 200)
        self.toast(texts.STONE_WAKE.format(name=name, n=self.stones_awake()))
        if self.stones_awake() == len(SHADOW_STONES):
            self.flags.add("vale_gate_open")
            self.record_event("gate")
            self.level.open_vale_gate()
            self.game.shake = 0.6
            self.dialog.show(texts.GATE_OPEN)

    def nearest_shrine(self):
        p = self.player
        for s in self.shrines:
            if abs(p.cx - (s["x"] * TILE + TILE / 2)) < 60 and abs(p.feet - (s["y"] + 1) * TILE) < 40:
                return s
        return None

    def open_shrine_menu(self, shrine):
        def pick(i):
            if i == 0:
                self.start_endure()
        self.dialog.show([(texts.SHRINE_NAME, texts.SHRINE_PROMPT)], choice=(texts.SHRINE_MENU, pick))

    def start_endure(self):
        """Sonnenschrein: she lowers the veil and endures the light on purpose – it burns, she adapts."""
        p = self.player
        self.rest = dict(kind="endure", t=0.0, dur=5.0)
        p.pose_override = "exhausted"
        p.vx = 0
        self.toast(texts.SHRINE_ENDURE)

    def update_endure(self, r, dt):
        p = self.player
        p.burn(SHRINE_DMG * p.sun_dmg_mult() * dt)
        self.gain_sun_exposure(dt * SHRINE_EXPOSURE_RATE)
        if random.random() < 0.6:
            self.particles.burst(p.cx + random.uniform(-p.w / 2, p.w / 2), p.y, (255, 220, 140), 1, 50, up=70)
        if p.hp < p.max_hp() * 0.15 and r["t"] < r["dur"]:
            r["t"] = r["dur"]                       # she staggers out before it kills her
            self.toast(texts.SHRINE_STOP)
        if r["t"] >= r["dur"]:
            self.rest = None
            p.pose_override = None

    def interact_target(self):
        """What E would use right now: a shrine, or the closer of a huggable creature and an altar."""
        shrine = self.nearest_shrine()
        if shrine:
            return shrine
        passage = self.snow.nearest_passage()            # the Frostpass
        if passage:
            return passage
        p = self.player
        creature = self.hugs.nearest()
        if creature is None and self.companion and abs(self.companion.cx - p.cx) < p.w / 2 + 70 \
                and abs(self.companion.cy - p.cy) < 80:
            creature = self.companion                    # talk to Fira
        a = self.nearest_altar()
        if a and (creature is None or abs(p.cx - (a["x"] * TILE + TILE / 2)) < abs(p.cx - creature.cx)):
            return a
        return creature

    def interact(self):
        p = self.player
        target = self.interact_target()
        if isinstance(target, dict) and target["kind"] == "sun_shrine":
            self.open_shrine_menu(target)
            return
        if isinstance(target, dict) and target["kind"] == "shadow_stone":
            self.wake_stone(target)
            return
        if isinstance(target, dict) and target["kind"] == "burrow":
            tx, ty = target["to"]
            p.x = tx * TILE + TILE / 2 - p.w / 2
            p.y = (ty + 1) * TILE - p.h
            p.vx = p.vy = 0
            self.particles.burst(p.cx, p.feet, (110, 80, 50), 14, 90)
            return
        if isinstance(target, dict) and target["kind"] == "passage":
            self.snow.use_passage(target)
            return
        if isinstance(target, dict):                     # an altar
            if target.get("locked") and not self.grove.camp_open():
                self.toast(texts.GROVE["camp_locked"], key="camp_locked")
                return
            if self.snow.altar_locked(target):           # the humans' hearth
                self.toast(texts.HUMAN_TALK["locked"], key="human_locked")
                return
            self.open_rest_menu(target)
            return
        if target is not None and target is self.companion:
            self.snow.talk_fira()
            return
        if target is not None:                           # Moosläufer, Morwen, Sera, Erila, humans
            self.hugs.open_menu(target)
            return
        # eat a fallen warm-blooded creature (adult only)
        for c in self.creatures:
            if c.edible and not c.alive and c.corpse_t > 0 and abs(c.cx - p.cx) < p.w and abs(c.cy - p.cy) < 60:
                if p.stage < 2:
                    self.toast(texts.CANT_EAT["meat"])
                    return
                c.corpse_t = 0
                self.eat("meat")
                self.morality.add(wild=2, deed="hunt_ground")
                p.pose_override = None
                self.toast(texts.TOASTS["meat_eat"])
                self.particles.burst(c.cx, c.cy, (150, 20, 40), 16, 100)
                return

    def remember_age(self, who):
        """Characters remember how big Shadowra was when they saw her (saved as flags)."""
        self.flags.add(f"{who}_saw_{texts.AGE[self.player.stage]}")

    def grew_since(self, who):
        """True if this character only knows her from a younger age and sees her grown for the first time."""
        stage = self.player.stage
        now = f"{who}_saw_{texts.AGE[stage]}"
        younger = any(f"{who}_saw_{texts.AGE[s]}" in self.flags for s in range(stage))
        return younger and now not in self.flags

    def talk_owl(self, owl):
        p = self.player
        trust = self.morality.trust()
        if trust == "afraid":
            line = texts.OWL.get(self.morality.owl_reaction(), texts.OWL["afraid"])
            self.dialog.show([texts.aged(line, p.stage)])
            return
        if trust == "gone":
            self.dialog.show([texts.OWL["gone"]])
            return
        lines = []
        if not owl.talked:
            lines += texts.aged(texts.OWL["first"], p.stage)
            owl.talked = True
            self.flags.add("owl_talked")
            self.morality.mark("kindness")
        elif self.grew_since("owl"):
            lines += texts.OWL["grew"]                      # "Oh, hallo, du Große! Du bist zu mir zurückgekommen."
        else:
            lines.append(texts.aged(texts.OWL["greet"], p.stage))
        self.remember_age("owl")
        if not owl.gift_given and p.stage >= 1:
            lines.append(texts.aged(texts.OWL["gift"], p.stage))
            owl.gift_given = True
            self.flags.add("owl_gift")

            def gift():
                self.eat("fish")
                self.toast(texts.TOASTS["fish_eat"])
            done = gift
        else:
            done = None
        if "veil" not in p.abilities:
            lines.append(texts.OWL["hint_veil"])
        elif p.stage < 2:
            lines.append(texts.OWL["hint_fish"])
        elif "fire" not in p.abilities:
            lines.append(texts.OWL["hint_fire"])
        else:
            lines.append(texts.OWL["hint_general"])
        self.dialog.show(lines, on_done=done)

    def hunt_deed(self):
        """Hunting from the air feeds the Flügelschlag subpath, on the ground the Raubtier subpath."""
        p = self.player
        return "hunt_air" if (not p.on_ground and not p.in_water) or p.diving else "hunt_ground"

    def try_blood(self):
        p = self.player
        if "blood" not in p.abilities:
            return
        best = None
        for c in self.creatures + ([self.boss] if self.boss and self.boss.active else []):
            if not c.blood or c.kind == "fira" or (c.alive and self.friendly(c)):
                continue
            ok = (not c.alive and c.corpse_t > 0) or c.weakened() or (c.kind == "fish" and c.alive)
            if c.kind == "boss":
                ok = False
            d = math.hypot(c.cx - p.cx, c.cy - p.cy)
            if ok and d < p.w / 2 + p.s["reach"] + 24 and (best is None or d < best[0]):
                best = (d, c)
        if not best:
            self.toast(texts.TOASTS["no_blood"], key="no_blood")
            return
        c = best[1]
        m = self.morality
        overflowing = p.mana > p.max_mana() * 0.95     # already full: the power has nowhere to go
        greedy = p.mana > p.max_mana() * 0.7
        mana_gain = (10 if c.kind == "fish" else 35) * m.mods()["blood_gain"]
        p.mana = min(p.max_mana(), p.mana + mana_gain)
        p.hp = min(p.max_hp(), p.hp + (5 if c.kind == "fish" else 15))
        m.blood_count += 1
        hunt = self.hunt_deed()
        if c.kind == "fish":
            m.add(wild=2, deed=hunt)
            msg = texts.BLOOD_MSG["fish"]
        elif c.blood in ("elf", "human"):                 # the blood of a thinking being
            m.add(lust=8, deed="wanting")
            m.add(madness=8, abhorrent=1, deed="horror")
            msg = texts.BLOOD_MSG[c.blood]
        elif c.blood == "priest":
            m.add(lust=8, deed="wanting")
            m.add(madness=3, deed="horror")
            msg = texts.BLOOD_MSG["priest"]
        else:
            m.add(wild=12, abhorrent=1, deed=hunt)
            if c.kind == "owl":
                m.add(madness=10, deed="horror")
            msg = texts.BLOOD_MSG["peaceful"]
        if greedy:
            m.add(lust=5, deed="overflow" if overflowing else "greed")
            msg = texts.BLOOD_MSG["greedy"]
        if c.alive and c.kind == "peaceful":
            m.add(wild=5, deed=hunt)
        c.alive = False
        c.corpse_t = 0
        self.toast(msg)
        self.particles.burst(c.cx, c.cy, (150, 10, 30), 30, 160)

    # ------------------------------------------------------------------
    # rests at nest / altars: eating, drinking, sleeping
    # ------------------------------------------------------------------
    def edible_here(self, altar):
        st = self.stock.get(altar["id"], {})
        order = {0: ["milk"], 1: ["fish"], 2: ["meat", "fish"]}[self.player.stage]
        for f in order:
            if st.get(f, 0) > 0:
                return f
        return None

    def open_rest_menu(self, altar):
        st = self.stock.get(altar["id"], {})
        ui = texts.UI
        food_txt = ", ".join(f"{texts.FOOD_NAMES[k]} ×{v}" for k, v in st.items() if v > 0) or ui["rest_empty"]
        opts = [ui["rest_food"].format(food=food_txt), ui["rest_sleep"], ui["rest_leave"]]

        def pick(i):
            if i == 0:
                self.start_eat(altar)
            elif i == 1:
                self.start_sleep(altar)
        self.dialog.show([], choice=(opts, pick))
        self.dialog.lines = [(texts.ALTAR_NAMES.get(altar["id"], ui["altar"]), ui["rest_prompt"])]

    def refuse_to_player(self, line):
        """A moral is at its limit (e.g. SAffection, FSK 12): she walks up to the camera and tells the player no."""
        from .closeup import CloseUp
        p = self.player
        p.vx = 0
        self.fourth_wall = CloseUp(p.stage, self.morality.eye_color(),
                                   start=(p.cx - self.cam[0], p.feet - self.cam[1]),
                                   text=line, wink=False, blush=False, fierce=True, hint="[E / Enter]")

    def update_fourth_wall(self, dt, ctl):
        fw = self.fourth_wall
        fw.update(dt)
        if fw.hold > fw.TALK_AT and (ctl.hit("confirm") or ctl.hit("interact") or ctl.hit("pause")):
            if not fw.text_done():
                fw.skip_typing()
            else:
                self.fourth_wall = None                  # she turns back into the game

    @staticmethod
    def food_spot(altar, food):
        """World x where this food lies at the altar (as drawn in draw_objects): fish left of the stone,
        meat right of it, milk in the pool (the nest's pool is in the middle, the moon spring's to the right)."""
        ax = altar["x"] * TILE + TILE / 2
        if food == "milk":
            return ax + (40 if altar["id"] == "M" else 0)
        return ax - 36 if food == "fish" else ax + 36

    def cozy_spot(self, altar, food):
        """She stands right on her food – so she can lie down curled around it, the meal at her side."""
        p = self.player
        return abs(p.cx - self.food_spot(altar, food)) <= max(16, p.w * 0.45)

    def start_eat(self, altar):
        p = self.player
        food = self.edible_here(altar)
        mods = self.morality.mods()
        cozy = False
        if food:
            cozy = self.cozy_spot(altar, food)
            refusal = self.morality.moral_refusal("cozy_meal") if cozy else None
            if refusal:                                  # e.g. SAffection at its FSK 12 limit
                self.refuse_to_player(refusal)
                return
            self.stock[altar["id"]][food] -= 1
            heal, stam = self.eat(food, at_altar=True)
            msg = texts.UI["eat_msg"].format(food=texts.FOOD_NAMES[food])
            if cozy:                                     # head towards the altar stone, the food at her flank
                p.facing = 1 if altar["x"] * TILE + TILE / 2 >= p.cx else -1
                k = (0.62, 1.0, 1.42)[p.stage]           # model scale (see models.draw_dragon)
                nx = self.food_spot(altar, food) + p.facing * 28 * k - p.w / 2   # food just behind her hip
                lv = self.level
                if not any(lv.solid(int(x // TILE), int((p.feet - 4) // TILE)) for x in (nx + 1, nx + p.w - 1)):
                    p.x = nx
        else:
            st = self.stock.get(altar["id"], {})
            other = next((k for k, v in st.items() if v > 0), None)
            msg = (texts.CANT_EAT[other] if other else texts.TOASTS["no_food"]) + texts.UI["drink_only"]
            heal, stam = p.max_hp() * 0.05, p.max_stam(mods)
        self.rest = dict(kind="eat", t=0.0, dur=3.2 if cozy else 2.6, altar=altar, heal=heal, stam=stam, msg=msg,
                         cozy=cozy, food=food)
        p.pose_override = "curl_eat" if cozy else "eat"
        p.vx = 0

    def start_sleep(self, altar):
        p = self.player
        mods = self.morality.mods()
        gain = (p.max_mana() - p.mana) * mods["sleep_mana"]      # "Trügerischer Schlaf" restores less
        if "moon_dew" in p.abilities:                            # Erila's Mondtau
            gain = min(p.max_mana() - p.mana, gain * 1.2 + p.max_mana() * 0.05)
        self.rest = dict(kind="sleep", t=0.0, dur=3.2, altar=altar, mana0=p.mana,
                         mana=gain, stam=p.max_stam(mods))
        p.pose_override = "sleep"
        p.vx = 0

    def update_rest(self, dt):
        r = self.rest
        p = self.player
        r["t"] += dt
        frac_dt = dt / r["dur"]
        if r["kind"] == "hug":
            self.hugs.update_rest(r, dt)
            return
        if r["kind"] == "endure":
            self.update_endure(r, dt)
            return
        if r["kind"] == "nuzzle":                   # cuddling up to an elf (Zuneigung)
            p.hp = min(p.max_hp(), p.hp + r["heal"] * frac_dt)
            if random.random() < dt * 6:
                e = r["elf"]
                self.particles.items.append([(p.cx + e.cx) / 2 + random.uniform(-10, 10), p.y,
                                             random.uniform(-15, 15), -60, 1.0, 1.0, (210, 150, 230), 3])
            if r["t"] >= r["dur"]:
                self.rest = None
                p.pose_override = None
            return
        if r["kind"] == "eat":
            if r.get("cozy") and random.random() < dt * 4:          # soft, warm motes while she curls up
                self.particles.items.append([p.cx + random.uniform(-p.w / 2, p.w / 2), p.feet - p.h * 0.6,
                                             random.uniform(-10, 10), -40, 1.2, 1.2, (230, 160, 220), 3])
            pulse = 1.0 + math.sin(r["t"] * 9)          # bars rise in rhythm with her chewing
            p.hp = min(p.max_hp(), p.hp + r["heal"] * frac_dt * pulse)
            p.stamina = min(p.max_stam(self.morality.mods()), p.stamina + r["stam"] * frac_dt * pulse)
        else:
            p.mana = min(p.max_mana(), p.mana + r["mana"] * frac_dt)
            p.stamina = min(p.max_stam(self.morality.mods()), p.stamina + r["stam"] * frac_dt)
        if r["t"] < r["dur"]:
            return
        self.rest = None
        p.pose_override = None
        altar = r["altar"]
        self.morality.mark("rest")
        if altar["id"] == "A4" and p.stage == 2 and "ash_wings" not in p.abilities:
            p.abilities.add("ash_wings")                 # she crossed the Lava Sea: Aschenschwingen
            self.record_event("gift", "ash_wings")
            self.dialog.show([texts.SNOW["ash_wings"],
                              (texts.UI["new_item"] + abilities.name("ash_wings"), abilities.desc("ash_wings"))])
        if r["kind"] == "eat":
            if r.get("cozy"):
                # the food at her side, curled around it: she is kind to herself (Zuneigung + SAffection)
                self.morality.mark("affection", 1.0)
                grew = self.morality.moral_event("cozy_meal")   # extra morals (data/morals.json), capped
                self.toast(r["msg"])
                self.toast(texts.TOASTS["cozy_meal"] + "".join(f"  +{n}" for n in grew))
            else:
                self.toast(r["msg"])
                if r.get("food") and "cozy_hint" not in self.flags:
                    self.flags.add("cozy_hint")         # tell the player once that a cozier way exists
                    self.hud.toast(texts.TOASTS["cozy_hint"], dur=5.0)
            self.open_rest_menu(altar)
            return
        # woke up
        p.mana = min(p.max_mana(), r["mana0"] + r["mana"])
        p.awake_time = 0.0
        p.exhausted = 0.0
        self.morality.add(madness=-4)
        lines = []
        need = GROWTH_NEED.get(p.stage)
        if need and p.food[need[0]] >= need[1]:
            p.grow()
            self.record_event("grew", p.stage)
            lines += texts.STAGE_UP[p.stage]
            if p.stage == 2 and "flight_seen" not in p.abilities:
                lines.append(texts.FLY_NOT_SEEN)
        self.save_game(altar["id"])
        self.toast(texts.TOASTS["saved"])
        if lines:
            self.particles.burst(p.cx, p.cy, (120, 70, 180), 60, 200)
            self.dialog.show(lines)

    # ------------------------------------------------------------------
    def dev_keys(self):
        keys = self.game.dev_pressed
        p = self.player
        if pygame.K_F1 in keys and p.stage < 2:
            p.grow()
        if pygame.K_F2 in keys:
            p.abilities |= {"glide", "flight_seen", "veil", "obsidian", "fire", "blood"}
            self.toast("DEV: alle Fähigkeiten")
        if pygame.K_F3 in keys:
            p.hp, p.mana, p.stamina = p.max_hp(), p.max_mana(), p.s["max_stam"]
        if pygame.K_F4 in keys:
            self.morality.add(wild=20)
            self.toast(f"DEV: Korruption {self.morality.corruption:.0f} -> Ende: {self.morality.ending()}")
        if pygame.K_F5 in keys:
            i = getattr(self, "_tp", 0) % len(DEV_TELEPORTS)
            self._tp = i + 1
            tx, ty = DEV_TELEPORTS[i]
            p.x = tx * TILE + TILE / 2 - p.w / 2
            p.y = (ty + 1) * TILE - p.h - 2
            p.vx = p.vy = 0

    # ------------------------------------------------------------------
    # camera & drawing
    # ------------------------------------------------------------------
    def clamp_cam(self):
        self.cam[0] = max(0, min(self.level.pw - SCREEN_W, self.cam[0]))
        self.cam[1] = max(0, min(self.level.ph - SCREEN_H, self.cam[1]))

    def update_camera(self, dt):
        p = self.player
        tx = p.cx - SCREEN_W / 2 + p.facing * 80
        ty = p.cy - SCREEN_H / 2 - 40
        if self.level.in_grove(p.cx, p.cy):
            # keep the view inside the grove: no peeking at the lava sea or the ruins through thin walls
            tx = max(GROVE[0] * TILE, min((GROVE[1] + 2) * TILE - SCREEN_W, tx))
            ty = max(22 * TILE, ty)
        elif X(151) * TILE <= p.cx <= (X(225) + 1) * TILE:
            # on the cliff / in the ruins: don't look down through the floor into the grove below
            ty = min(24 * TILE - SCREEN_H, ty)
        k = min(1.0, dt * 5)
        self.cam[0] += (tx - self.cam[0]) * k
        self.cam[1] += (ty - self.cam[1]) * k
        self.clamp_cam()
        target_cave = 1.0 if self.level.is_cave(p.cx, p.cy) else 0.0
        self.cave_mix += (target_cave - self.cave_mix) * min(1.0, dt * 2)
        target_grove = 1.0 if self.level.in_grove(p.cx, p.cy) else 0.0
        self.grove_mix += (target_grove - self.grove_mix) * min(1.0, dt * 2)
        target_lava = 1.0 if LAVA[0] * TILE <= p.cx <= LAVA[1] * TILE else 0.0
        target_day = 1.0 if self.level.day_zone(p.cx) else 0.0
        self.day_mix += (target_day - self.day_mix) * min(1.0, dt * 2)
        self.lava_mix += (target_lava - self.lava_mix) * min(1.0, dt * 2)
        zone = self.level.zone_key(p.cx, p.cy)
        target_snow = 1.0 if self.level.in_snow(p.cx) else 0.0
        self.snow_mix += (target_snow - self.snow_mix) * min(1.0, dt * 2)
        target_under = 1.0 if zone == "underwater" else 0.0
        self.under_mix += (target_under - self.under_mix) * min(1.0, dt * 2.5)
        target_ice = 1.0 if zone in ("icecave", "frostpass") else 0.0
        self.ice_mix += (target_ice - self.ice_mix) * min(1.0, dt * 2)

    def draw(self, screen):
        cam = (int(self.cam[0] + self.game.shake_off[0]), int(self.cam[1] + self.game.shake_off[1]))
        self.backdrop.draw(screen, cam, self.cave_mix, self.lava_mix, self.t, self.grove_mix, self.day_mix,
                           self.snow_mix)
        if self.grove_mix > 0.01:
            self.backdrop.draw_grove(screen, cam, self.grove_mix, self.t)
        if self.ice_mix > 0.01:                          # Eishöhle / Frostpass: a cold blue cave
            if not hasattr(self, "_ice_tint"):
                self._ice_tint = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                self._ice_tint.fill((60, 120, 190, 70))
            self._ice_tint.set_alpha(int(255 * self.ice_mix))
            screen.blit(self._ice_tint, (0, 0))
        render.draw_beams(screen, self.level, cam, self.t)
        if self.lava_mix > 0.01:
            render.draw_lava_glow(screen, self.level, cam, self.t)
        if self.day_mix > 0.01:
            render.draw_daylight(screen, self.level, cam, self.t, self.sprites)
        self.draw_decor(screen, cam, back=True)
        self.tile_art.draw(screen, self.level, cam, self.t)
        self.draw_decor(screen, cam, back=False)
        self.draw_objects(screen, cam)
        self.snow.draw_world(screen, cam)                # Frostpass cleft, hearth fire, otters
        for c in self.creatures:
            if -200 < c.cx - cam[0] < SCREEN_W + 200:
                self.draw_creature(screen, c, cam)
        if self.boss and not getattr(self.boss, "gone", False) and abs(self.boss.cx - self.player.cx) < 1600:
            self.draw_boss(screen, cam)
        self.draw_player(screen, cam)
        for pr in self.projectiles:
            x, y = int(pr.x - cam[0]), int(pr.y - cam[1])
            if pr.kind == "arrow":
                img = pygame.transform.rotate(self.sprites.arrow, -math.degrees(math.atan2(pr.vy, pr.vx)))
                screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
            elif pr.kind == "spear":
                ang = math.atan2(pr.vy, pr.vx)
                dx, dy = math.cos(ang) * 22, math.sin(ang) * 22
                pygame.draw.line(screen, (120, 86, 56), (x - dx, y - dy), (x + dx, y + dy), 3)
                pygame.draw.polygon(screen, (200, 206, 214), [(x + dx * 1.35, y + dy * 1.35),
                                                              (x + dx - dy * 0.2, y + dy + dx * 0.2),
                                                              (x + dx + dy * 0.2, y + dy - dx * 0.2)])
            elif pr.owner == "player":
                pygame.draw.circle(screen, (60, 20, 90), (x, y), pr.r + 3)
                pygame.draw.circle(screen, (170, 120, 255), (x, y), pr.r)
            else:
                render.draw_light_circle(screen, x, y, 22, alpha=90)
                pygame.draw.circle(screen, (255, 245, 200), (x, y), pr.r)
        for pt in self.particles.items:
            a = pt[4] / pt[5]
            pygame.draw.circle(screen, pt[6], (int(pt[0] - cam[0]), int(pt[1] - cam[1])), max(1, int(pt[7] * a)))
        if self.snow_mix > 0.05 and self.cave_mix < 0.9:  # snow falling outside
            self.backdrop.draw_snowfall(screen, cam, self.t, self.snow_mix * (1 - self.cave_mix))
        if self.under_mix > 0.02:                        # deep under the ice: dark blue water all around
            if not hasattr(self, "_under_tint"):
                self._under_tint = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                self._under_tint.fill((10, 40, 90, 110))
            self._under_tint.set_alpha(int(255 * self.under_mix))
            screen.blit(self._under_tint, (0, 0))
        self.draw_cutscene(screen)
        self.draw_overlays(screen)
        self.snow.draw_overlay(screen)                   # frost on the edges, breath bar
        self.hud.draw(screen, self.player, self.morality, self.t)
        if self.cheats:                                  # so it's always clear a run uses cheats
            names = " · ".join(texts.CHEAT_NAMES.get(k, k) for k in cheats.KNOWN if k in self.cheats)
            s = font(15).render(texts.UI["cheats"].format(names=names), True, (255, 200, 120))
            screen.blit(s, (SCREEN_W - s.get_width() - 16, 14))
        self.draw_prompt(screen, cam)
        if self.boss and self.boss.active and not self.boss.defeated:
            w = 600
            x = SCREEN_W // 2 - w // 2
            screen.blit(font(22, "title").render(texts.UI["boss_name"], True, (255, 230, 170)), (x, SCREEN_H - 70))
            pygame.draw.rect(screen, (20, 10, 10), (x - 2, SCREEN_H - 40, w + 4, 14))
            pygame.draw.rect(screen, (240, 200, 90), (x, SCREEN_H - 38, int(w * self.boss.hp / self.boss.max_hp), 10))
        self.dialog.draw(screen)
        if self.rest and self.rest["kind"] == "sleep":
            r = self.rest
            a = math.sin(min(1.0, r["t"] / r["dur"]) * math.pi)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((5, 2, 10, int(220 * a)))
            screen.blit(ov, (0, 0))
            z = font(30, "title").render("z z z", True, (150, 120, 200))
            z.set_alpha(int(255 * a))
            screen.blit(z, (SCREEN_W // 2 - z.get_width() // 2, SCREEN_H // 2 - 80))
        if self.death_t is not None:
            a = min(1.0, self.death_t / 1.2)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, int(255 * a)))
            screen.blit(ov, (0, 0))
            s = font(42, "title").render(texts.DEATH, True, (200, 60, 80))
            s.set_alpha(int(255 * a))
            screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, SCREEN_H // 2 - 30))
        if self.end_t is not None and self.end_t > 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, int(255 * min(1.0, self.end_t / 2.0))))
            screen.blit(ov, (0, 0))
        if self.fourth_wall:
            self.fourth_wall.draw(screen, self.t)
        if self.fade_in > 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, int(255 * self.fade_in)))
            screen.blit(ov, (0, 0))

    def draw_player(self, screen, cam):
        p = self.player
        if self.fourth_wall:                             # she has walked out of the world, up to the camera
            return
        if p.invuln > 0 and int(p.invuln * 20) % 2 == 0 and p.hurt_flash <= 0 and not p.dead:
            return
        tint = None
        if p.hurt_flash > 0:
            tint = (120, 40, 40)
        elif p.burning > 0:
            tint = (90, 50, 10)
        elif p.dash_t > 0:
            tint = None
        pose = p.pose()
        if pose == "dash":
            for i in range(4):
                s = pygame.Surface((p.w, p.h), pygame.SRCALPHA)
                s.fill((40, 15, 60, 90 - i * 20))
                screen.blit(s, (p.x - cam[0] - p.facing * i * 14, p.y - cam[1]))
            return
        if p.on_ground:                                    # soft contact shadow under her feet
            render.ground_shadow(screen, p.cx - cam[0], p.feet - cam[1], p.w * 1.7)
        # faint aura so a dark dragon stays readable in dark caves
        render.draw_light_circle(screen, p.cx - cam[0], p.cy - cam[1] - p.h * 0.2,
                                 int(max(p.w, p.h) * 1.3), col=(150, 110, 190), alpha=45, shine=False)
        render.draw_dragon(screen, p.cx - cam[0], p.feet - cam[1], p.stage, p.facing, pose, p.anim_t,
                           eye=self.morality.eye_color(), obsidian="obsidian" in p.abilities,
                           tint=tint, flap=p.flap_anim, extra_lights=self.world_lights(p.cx, p.cy, cam))
        lit = (self.level.sun_at(p.cx, p.cy, self.t) or self.level.lava_light_at(p.cx, p.cy)
               or self.level.sunlit(p.cx, p.cy, self.t))
        if "veil" in p.abilities and lit and p.mana > 0:
            s = pygame.Surface((p.w + 30, p.h + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (30, 10, 50, 110), s.get_rect())
            screen.blit(s, (p.x - 15 - cam[0], p.y - 15 - cam[1]))
        if p.exhausted > 0 and int(p.anim_t * 3) % 2 == 0:
            hx = p.cx + p.facing * p.w * 0.6 - cam[0]
            pygame.draw.circle(screen, (200, 200, 210), (int(hx), int(p.y + p.h * 0.4 - cam[1])), 3)

    def world_lights(self, wx, wy, cam):
        """Light that isn't drawn as a glow but should still make dragon scales shine (screen space):
        a sunbeam or open daylight from above, the glow of lava from below."""
        x, y = wx - cam[0], wy - cam[1]
        out = []
        if self.level.sun_at(wx, wy, self.t):
            out.append((x + 30, y - 150, 160, LIGHT_COL, 1.0))
        elif self.day_mix > 0.01 and self.level.sunlit(wx, wy, self.t):
            out.append((x - 90, y - 170, 180, (255, 236, 170), 0.8 * self.day_mix))
        if self.lava_mix > 0.01 and self.level.lava_light_at(wx, wy):
            out.append((x + 20, y + 110, 130, LAVA_COL, 0.9 * self.lava_mix))
        return out

    def draw_creature(self, screen, c, cam):
        if c.alive and c.gravity and c.on_ground and c.kind != "fira":     # soft contact shadow
            render.ground_shadow(screen, c.cx - cam[0], c.y + c.h - cam[1], c.w * 1.6)
        self._draw_creature_body(screen, c, cam)
        self.hugs.draw_icon(screen, c, c.cx - cam[0], c.y - cam[1] - 8)

    def _draw_creature_body(self, screen, c, cam):
        x, y = c.x - cam[0], c.y - cam[1]
        sp = self.sprites
        fr = int(c.anim_t * 6) % 4
        alpha = 255 if c.alive else int(255 * max(0.0, min(1.0, c.corpse_t / 2)))
        if c.kind == "elf":
            pose = "dead" if not c.alive else ("shoot" if c.cast > 0 and c.role == "archer" else
                                              "cast" if c.cast > 0 else "walk" if abs(c.vx) > 5 else "idle")
            render.draw_elf(screen, c.cx - cam[0], c.y + c.h - cam[1], c.facing, c.name, pose, c.anim_t,
                            flash=c.flash > 0)
            if c.alive and c.hp < c.max_hp:             # small health bar over hurt elves
                bx, by = c.cx - cam[0] - 18, c.y - cam[1] - 14
                pygame.draw.rect(screen, (20, 10, 20), (bx - 1, by - 1, 38, 6))
                pygame.draw.rect(screen, (120, 210, 150), (bx, by, int(36 * c.hp / c.max_hp), 4))
        elif c.kind == "villager":
            pose = "walk" if abs(c.vx) > 5 else "idle"
            blush = getattr(c, "blush_until", 0) > self.t
            if c.leaving:                                  # slipping back into the house
                alpha = int(255 * max(0.0, 1 - c.leave_t / 1.2))
            if alpha > 10:
                render.draw_elf(screen, c.cx - cam[0], c.y + c.h - cam[1], c.facing, c.name, pose, c.anim_t,
                                flash=c.flash > 0, style=c.style, blush=blush)
        elif c.kind == "human":                            # the humans in the snow
            pose = "dead" if not c.alive else ("shoot" if c.cast > 0 else "walk" if abs(c.vx) > 5 else "idle")
            blush = getattr(c, "blush_until", 0) > self.t
            if c.leaving:
                alpha = int(255 * max(0.0, 1 - c.leave_t / 1.2))
            if alpha > 10:
                render.draw_elf(screen, c.cx - cam[0], c.y + c.h - cam[1], c.facing, c.name, pose, c.anim_t,
                                flash=c.flash > 0, style=c.style, blush=blush)
            if c.alive and c.hostile and c.hp < c.max_hp:
                bx, by = c.cx - cam[0] - 18, c.y - cam[1] - 14
                pygame.draw.rect(screen, (20, 10, 20), (bx - 1, by - 1, 38, 6))
                pygame.draw.rect(screen, (220, 90, 90), (bx, by, int(36 * c.hp / c.max_hp), 4))
        elif c.kind == "fira_companion":                   # Fira at her side
            if c.pose in ("idle", "walk"):
                render.ground_shadow(screen, c.cx - cam[0], c.y + c.h - cam[1], 90)
            render.draw_dragon(screen, c.cx - cam[0], c.y + c.h - cam[1], 2, c.facing, c.pose, c.anim_t,
                               eye=(255, 190, 60), body=(150, 66, 40), horn=(70, 40, 30), scale_mult=0.9,
                               flap=(c.anim_t * 2.4 % 1) * 0.35, extra_lights=self.world_lights(c.cx, c.cy, cam))
        elif c.kind in ("priest", "skeleton", "skull", "vampire"):
            if c.kind == "priest" and c.alive:              # torch light behind the priest
                L = c.light()
                render.draw_light_circle(screen, L[0] - cam[0], L[1] - cam[1], int(L[2]), alpha=60)
            render.draw_monster(screen, c.kind, c.cx - cam[0], c.y + c.h - cam[1], c.facing, c.anim_t,
                                moving=abs(c.vx) > 5, flash=c.flash > 0, alpha=alpha, dead=not c.alive)
        elif c.kind == "peaceful":
            render.draw_moss_runner(screen, c.cx - cam[0], c.y + c.h - cam[1], c.facing, c.anim_t,
                                    abs(c.vx) > 5, c.fleeing, c.flash > 0, alpha, not c.alive)
        elif c.kind == "fish":
            render.draw_fish(screen, c.cx - cam[0], c.cy - cam[1], c.facing)
        elif c.kind == "owl":
            render.draw_owl(screen, c.cx - cam[0], c.y + c.h - cam[1], c.anim_t, c.flash > 0, alpha)
        elif c.kind == "fira":
            fx, fy = c.cx - cam[0], c.y + c.h - cam[1]
            render.draw_dragon(screen, fx, fy, 2, -1, "exhausted" if c.caged else "idle", c.anim_t,
                               eye=(255, 190, 60), body=(150, 66, 40), horn=(70, 40, 30), scale_mult=0.9)
            if c.caged:
                for i in range(7):
                    bx = fx - 50 + i * 16
                    pygame.draw.line(screen, (240, 220, 150), (bx, fy - 90), (bx, fy), 3)
                pygame.draw.line(screen, (240, 220, 150), (fx - 54, fy - 90), (fx + 50, fy - 90), 5)
                render.draw_light_circle(screen, fx, fy - 45, 70, alpha=40)

    def draw_boss(self, screen, cam):
        b = self.boss
        x, y = b.cx - cam[0], b.y + b.h - cam[1]
        if not b.defeated:
            render.draw_light_circle(screen, x, b.cy - cam[1], int(b.aura_r * 1.3), alpha=80)
        render.draw_mafor(screen, x, y, b.facing, b.anim_t, flash=b.flash > 0, defeated=b.defeated)
        sr = b.strike_rect()
        if b.strike:
            sx = b.strike["x"] - cam[0]
            if sr:
                s = pygame.Surface((80, SCREEN_H), pygame.SRCALPHA)
                s.fill((255, 240, 180, 170))
                screen.blit(s, (sx - 40, 0))
            else:
                pygame.draw.line(screen, (255, 220, 120), (sx, 0), (sx, SCREEN_H), 2)
                pygame.draw.rect(screen, (255, 220, 120), (sx - 40, 0, 80, SCREEN_H), 1)

    def draw_decor(self, screen, cam, back):
        """Elfenhain props: trees/tents behind the rock edges, mushrooms/lanterns/grass in front."""
        sp = self.sprites
        for d in self.decor:
            x = d["x"] * TILE + TILE / 2 - cam[0]
            y = (d["y"] + 1) * TILE - cam[1]
            if not -200 < x < SCREEN_W + 200:
                continue
            kind = d["decor"]
            if kind in SNOW_DECOR:                            # the snowlands' props (snow.py)
                self.snow.draw_decor(screen, d, x, y, back)
                continue
            if back and kind == "elfhouse":                   # Elfendorf: round wooden house with a leaf roof
                k = d.get("size", 1.0)
                w, h = 70 * k, 52 * k
                lit = self.grove.village_out
                pygame.draw.rect(screen, (96, 66, 44), (x - w / 2, y - h, w, h), border_radius=int(12 * k))
                pygame.draw.rect(screen, (60, 40, 28), (x - w / 2, y - h, w, h), 2, border_radius=int(12 * k))
                for i in range(3):                             # planks
                    py = y - h + (i + 1) * h / 4
                    pygame.draw.line(screen, (78, 52, 34), (x - w / 2 + 4, py), (x + w / 2 - 4, py), 1)
                roof = [(x - w / 2 - 12 * k, y - h + 6 * k), (x, y - h - 34 * k), (x + w / 2 + 12 * k, y - h + 6 * k)]
                pygame.draw.polygon(screen, (52, 110, 66), roof)
                pygame.draw.polygon(screen, (34, 76, 44), roof, 3)
                for i in range(5):                             # leaf shingles
                    lx = x - w / 2 + i * w / 4
                    pygame.draw.ellipse(screen, (70, 140, 80), (lx - 9 * k, y - h - 2 * k, 18 * k, 10 * k))
                door = pygame.Rect(0, 0, 18 * k, 28 * k)
                door.midbottom = (x, y)
                pygame.draw.rect(screen, (40, 26, 18), door, border_top_left_radius=int(9 * k),
                                 border_top_right_radius=int(9 * k))
                win = (255, 214, 140) if lit else (120, 150, 200)    # warm light once they are home again
                for wx in (x - w / 3, x + w / 3):
                    pygame.draw.circle(screen, win, (int(wx), int(y - h * 0.62)), int(6 * k))
                    pygame.draw.circle(screen, (60, 40, 28), (int(wx), int(y - h * 0.62)), int(6 * k), 2)
                continue
            if back and kind in ("trunk", "pillar"):          # daylight props: tree trunks, temple pillars
                top = d["top"] * TILE - cam[1]
                if kind == "trunk":
                    pygame.draw.rect(screen, (92, 62, 40), (x - 9, top, 18, y - top))
                    pygame.draw.rect(screen, (66, 44, 30), (x - 9, top, 5, y - top))
                    pygame.draw.polygon(screen, (92, 62, 40), [(x - 9, y), (x - 18, y), (x - 9, y - 12)])
                    pygame.draw.polygon(screen, (92, 62, 40), [(x + 9, y), (x + 18, y), (x + 9, y - 12)])
                else:
                    pygame.draw.rect(screen, (196, 178, 140), (x - 11, top, 22, y - top))
                    pygame.draw.rect(screen, (150, 132, 100), (x + 5, top, 6, y - top))
                    pygame.draw.rect(screen, (214, 198, 160), (x - 15, top, 30, 6))
                    pygame.draw.rect(screen, (214, 198, 160), (x - 15, y - 6, 30, 6))
                continue
            if not back and kind in ("flower", "grass_day", "bush_day", "stone_day"):
                img = sp.decor_day[kind]
                screen.blit(img, (x - img.get_width() / 2, y - img.get_height()))
                continue
            if back and kind in ("tree", "tent", "stone"):
                if kind == "tent":
                    pygame.draw.polygon(screen, (60, 80, 110), [(x - 34, y), (x, y - 50), (x + 34, y)])
                    pygame.draw.polygon(screen, (30, 40, 60), [(x - 8, y), (x, y - 30), (x + 8, y)])
                    pygame.draw.polygon(screen, (150, 180, 210), [(x - 34, y), (x, y - 50), (x + 34, y)], 2)
                else:
                    img = sp.decor[kind]
                    screen.blit(img, (x - img.get_width() / 2, y - img.get_height()))
            elif not back and kind in ("bush", "grass", "mushroom", "lantern"):
                if kind == "mushroom":                     # glowing – soft moonlight, harmless
                    glow = 0.5 + 0.5 * math.sin(self.t * 1.5 + d["x"])
                    render.draw_light_circle(screen, x, y - 12, 28, col=(100, 220, 210), alpha=int(40 + 30 * glow))
                    for dx, h, r in ((-8, 10, 7), (4, 16, 9), (12, 8, 5)):
                        pygame.draw.line(screen, (180, 200, 190), (x + dx, y), (x + dx, y - h), 2)
                        pygame.draw.ellipse(screen, (70, 190, 190), (x + dx - r, y - h - r * 0.6, r * 2, r * 1.2))
                elif kind == "lantern":
                    pygame.draw.line(screen, (90, 70, 50), (x, y), (x, y - 44), 3)
                    render.draw_light_circle(screen, x, y - 46, 46, col=(150, 190, 255), alpha=70)
                    pygame.draw.circle(screen, (200, 225, 255), (int(x), int(y - 46)), 6)
                else:
                    img = sp.decor[kind]
                    screen.blit(img, (x - img.get_width() / 2, y - img.get_height()))

    def draw_objects(self, screen, cam):
        t = self.t
        for s in self.shrines:                              # Sonnenschrein: a golden, blazing altar
            x = s["x"] * TILE + TILE / 2 - cam[0]
            y = (s["y"] + 1) * TILE - cam[1]
            if s["kind"] == "burrow" and -200 < x < SCREEN_W + 200:        # Erdbau: a dark burrow mouth
                pygame.draw.ellipse(screen, (110, 76, 50), (x - 30, y - 30, 60, 34))
                pygame.draw.ellipse(screen, (14, 8, 6), (x - 20, y - 22, 40, 24))
                continue
            if s["kind"] == "shadow_stone":
                if -200 < x < SCREEN_W + 200:                 # dark obelisk, violet runes once awake
                    awake = f"{s['id']}_awake" in self.flags
                    if awake:
                        render.draw_light_circle(screen, x, y - 36, 54, col=(160, 100, 255), alpha=80)
                    body = [(x - 14, y), (x - 10, y - 58), (x, y - 68), (x + 10, y - 58), (x + 14, y)]
                    pygame.draw.polygon(screen, (34, 26, 44), body)
                    pygame.draw.polygon(screen, (90, 70, 110), body, 2)
                    rune = (200, 150, 255) if awake else (70, 56, 86)
                    for i in range(3):
                        ry = y - 16 - i * 14 + (math.sin(t * 3 + i) * 1.5 if awake else 0)
                        pygame.draw.circle(screen, rune, (int(x), int(ry)), 4, 0 if awake else 1)
                continue
            if -200 < x < SCREEN_W + 200:
                render.draw_light_circle(screen, x, y - 40, 70, col=(255, 220, 120), alpha=70)
                pygame.draw.polygon(screen, (220, 190, 110), [(x - 22, y), (x + 22, y), (x + 14, y - 30), (x - 14, y - 30)])
                pygame.draw.polygon(screen, (150, 120, 60), [(x - 22, y), (x + 22, y), (x + 14, y - 30), (x - 14, y - 30)], 2)
                pygame.draw.circle(screen, (255, 236, 160), (int(x), int(y - 42)), 11)
                for i in range(8):
                    a = t * 0.8 + i * math.pi / 4
                    pygame.draw.line(screen, (255, 220, 120), (x + math.cos(a) * 15, y - 42 + math.sin(a) * 15),
                                     (x + math.cos(a) * 24, y - 42 + math.sin(a) * 24), 2)
        if self.ward:                                       # the ward of the rest spot she stands at
            a = self.ward
            x = a["x"] * TILE + TILE / 2 - cam[0]
            y = (a["y"] + 1) * TILE - cam[1]
            R = self.WARD_R
            if not hasattr(self, "_ward_img"):
                img = pygame.Surface((R * 2, 40), pygame.SRCALPHA)
                for i in range(8):
                    k = i / 8
                    pygame.draw.ellipse(img, (150, 100, 230, int(30 + 50 * k)),
                                        (R * k * 0.5, 20 * k * 0.5, R * 2 * (1 - k * 0.5), 40 * (1 - k * 0.5)))
                pygame.draw.ellipse(img, (200, 160, 255, 200), (0, 0, R * 2, 40), 3)     # the ward's rim
                self._ward_img = img
            pulse = 0.75 + 0.25 * math.sin(t * 2)
            self._ward_img.set_alpha(int(255 * pulse))
            screen.blit(self._ward_img, (x - R, y - 20))
            for side in (-1, 1):                            # shimmering walls at the ward's edges
                ex = x + side * R
                for i in range(7):
                    ey = y - 6 - ((t * 40 + i * 19) % 130)
                    pygame.draw.circle(screen, (200, 165, 255), (int(ex + math.sin(t * 3 + i) * 3), int(ey)), 3)
        for a in self.altars:
            x = a["x"] * TILE + TILE / 2 - cam[0]
            y = (a["y"] + 1) * TILE - cam[1]
            if not -200 < x < SCREEN_W + 200:
                continue
            st = self.stock.get(a["id"], {})
            if a["id"] in ("N", "M"):
                if a["id"] == "N":
                    self.draw_nest_mood(screen, x, y)
                    for i in range(7):
                        pygame.draw.arc(screen, (90, 60, 40), (x - 40 + i * 2, y - 22 + (i % 2) * 3, 80 - i * 4, 30), 3.3, 6.1, 3)
                pool = (230, 225, 240) if st.get("milk", 0) > 0 else (70, 70, 90)
                pygame.draw.ellipse(screen, pool, (x - 22 + (40 if a["id"] == "M" else 0), y - 8, 44, 10))
                if a["id"] == "M":
                    render.draw_light_circle(screen, x + 40, y - 4, 50, col=(200, 200, 255), alpha=40)
            else:
                pulse = int(40 + 30 * math.sin(t * 2))
                pygame.draw.rect(screen, (34, 22, 44), (x - 14, y - 52, 28, 52))
                pygame.draw.rect(screen, (70, 50, 90), (x - 14, y - 52, 28, 52), 2)
                pygame.draw.circle(screen, (120 + pulse, 60, 200), (int(x), int(y - 36)), 6)
                render.draw_light_circle(screen, x, y - 36, 40, col=(140, 80, 220), alpha=50)
                if st.get("meat", 0) > 0:
                    for i in range(3):
                        pygame.draw.arc(screen, (200, 190, 170), (x + 18 + i * 8, y - 22, 14, 24), 0, 3.1, 2)
                    pygame.draw.ellipse(screen, (110, 30, 40), (x + 18, y - 12, 36, 12))
                if st.get("fish", 0) > 0:
                    for i in range(st["fish"]):
                        pygame.draw.ellipse(screen, (150, 170, 200), (x - 50 + i * 10, y - 8 - i * 3, 18, 7))
                pygame.draw.ellipse(screen, (40, 60, 110), (x - 30, y - 6, 26, 8))
        for it in self.items:
            x = it["x"] * TILE + 16 - cam[0]
            y = it["y"] * TILE + 16 - cam[1] + math.sin(t * 3 + it["x"]) * 4
            if it["kind"] == "crystal":
                pts = [(x, y - 12), (x + 7, y), (x, y + 12), (x - 7, y)]
                render.draw_light_circle(screen, x, y, 30, col=(150, 90, 230), alpha=60)
                pygame.draw.polygon(screen, (120, 70, 210), pts)
                pygame.draw.polygon(screen, (210, 170, 255), pts, 2)
            else:
                col = abilities.color(it["relic"])
                render.draw_light_circle(screen, x, y, 46, col=col, alpha=90)
                pygame.draw.circle(screen, (15, 8, 20), (int(x), int(y)), 11)
                pygame.draw.circle(screen, col, (int(x), int(y)), 11, 3)
        for tr in self.triggers:
            if tr["kind"] == "birds" and "birds" not in self.flags:
                x = tr["x"] * TILE + 16 - cam[0]
                y = tr["y"] * TILE + 16 - cam[1]
                for i in range(3):
                    a = t * 2 + i * 2
                    pygame.draw.circle(screen, (200, 190, 220), (int(x + math.cos(a) * 14), int(y - 10 + math.sin(a) * 6)), 2)

    def draw_nest_mood(self, screen, x, y):
        mood = self.morality.nest_mood()
        rng = random.Random(5)
        if mood == "bloom":
            for i in range(6):
                fx = x - 60 + rng.randint(0, 120)
                pygame.draw.line(screen, (60, 90, 70), (fx, y), (fx, y - 10), 2)
                c = (180, 140, 255) if i % 2 else (140, 200, 255)
                render.draw_light_circle(screen, fx, y - 12, 10, col=c, alpha=80)
                pygame.draw.circle(screen, c, (int(fx), int(y - 12)), 3)
        elif mood == "scratches":
            for i in range(8):
                sx = x - 70 + i * 18
                pygame.draw.line(screen, (150, 40, 60), (sx, y - 90), (sx + rng.randint(-20, 20), y - 30), 2)
        elif mood == "hoard":
            for i in range(5):
                sx = x - 60 + i * 26
                pygame.draw.circle(screen, (210, 200, 180), (int(sx), int(y - 7)), 7)
                pygame.draw.circle(screen, (30, 20, 20), (int(sx - 2), int(y - 8)), 2)
                pygame.draw.circle(screen, (30, 20, 20), (int(sx + 3), int(y - 8)), 2)
                pygame.draw.circle(screen, (240, 200, 80), (int(sx + 12), int(y - 3)), 3)
        else:
            for i in range(5):
                sx = x - 60 + i * 28
                pygame.draw.line(screen, (210, 200, 180), (sx, y - 3), (sx + 18, y - 6), 3)

    def draw_cutscene(self, screen):
        if not self.cutscene:
            return
        cs = self.cutscene
        cs["t"] += 1 / 60
        t = cs["t"]
        if cs["kind"] == "birds":
            for i in range(7):
                bx = (t * 140 + i * 90) % (SCREEN_W + 200) - 100
                by = 80 + i * 18 + math.sin(t * 2 + i) * 12
                wing = math.sin(t * 6 + i) * 6
                pygame.draw.lines(screen, (25, 15, 35), False,
                                  [(bx - 14, by - wing), (bx, by), (bx + 14, by - wing)], 3)
        elif cs["kind"] == "storm":
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((20, 20, 40, 60))
            screen.blit(ov, (0, 0))
            dx = (t * 160) % (SCREEN_W + 800) - 400
            render.draw_dragon(screen, dx, 260, 2, 1, "flap" if int(t * 2) % 2 else "glide", t,
                               body=(20, 14, 26), horn=(40, 30, 40), eye=(20, 14, 26),
                               scale_mult=2.6, flap=(t % 0.5) * 0.7)

    def draw_overlays(self, screen):
        m = self.morality
        if "hallucinations" in m.debuffs():
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((60, 0, 30, int(25 + 15 * math.sin(self.t * 1.7))))
            screen.blit(ov, (0, 0))
            for hx, hy, life, kind in self.halluc:
                a = int(120 * min(1.0, life))
                if kind == "eyes":
                    for dx in (-8, 8):
                        s = pygame.Surface((10, 10), pygame.SRCALPHA)
                        pygame.draw.circle(s, (255, 40, 40, a), (5, 5), 4)
                        screen.blit(s, (hx + dx, hy))
                elif kind == "skeleton":
                    img = self.sprites.skeleton[0].copy()
                    img.set_alpha(a // 2)
                    screen.blit(img, (hx, hy))
                else:
                    s = pygame.Surface((60, 90), pygame.SRCALPHA)
                    pygame.draw.ellipse(s, (0, 0, 0, a), s.get_rect())
                    screen.blit(s, (hx, hy))

    def draw_prompt(self, screen, cam):
        if self.input_locked():
            return
        p = self.player
        text = None
        target = self.interact_target()
        if isinstance(target, dict) and target["kind"] == "sun_shrine":
            text = f"[E] {texts.SHRINE_NAME}"
        elif isinstance(target, dict) and target["kind"] == "shadow_stone":
            text = texts.STONE_PROMPT if f"{target['id']}_awake" not in self.flags else f"[E] {texts.STONE_NAMES[target['id']]}"
        elif isinstance(target, dict) and target["kind"] == "burrow":
            text = "[E] " + (texts.BURROW_IN if target["id"] == "burrow_top" else texts.BURROW_OUT)
        elif isinstance(target, dict) and target["kind"] == "passage":
            text = "[E] " + texts.PASSAGE_LABELS.get(target.get("label"), "")
        elif isinstance(target, dict):
            text = texts.UI["prompt_rest"]
        elif target is not None:
            text = f"[E] {self.hugs.name(target)}"
        else:
            for c in self.creatures:
                if (c.edible and not c.alive and c.corpse_t > 0 and p.stage == 2
                      and abs(c.cx - p.cx) < p.w and abs(c.cy - p.cy) < 60):
                    text = texts.UI["prompt_eat"]
                if (c.blood and "blood" in p.abilities and c.kind not in ("boss",)
                        and not (c.alive and self.friendly(c))
                        and ((not c.alive and c.corpse_t > 0) or c.weakened())
                        and math.hypot(c.cx - p.cx, c.cy - p.cy) < p.w / 2 + p.s["reach"] + 24):
                    text = (text + "   " if text else "") + "[U] Blut-Sog"
                if text:
                    break
        if text:
            s = font(16).render(text, True, TEXT)
            screen.blit(s, (p.cx - cam[0] - s.get_width() / 2, p.y - cam[1] - 34))
