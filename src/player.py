"""Shadowra: three resources (Leben, Mana, Ausdauer), growth stages, glide -> updraft -> flight."""
import math

from .settings import (TILE, GRAVITY, MAX_FALL, STAGES, SPRINT_MULT, SPRINT_DRAIN,
                       GROUND_STAM_REGEN, WATER_STAM_REGEN, EXHAUST_TIME, FLAP_COST, FLAP_VY,
                       ADULT_GLIDE_DRAIN, WALLJUMP_COST, DASH_COST, TAIL_COST, DIVE_COST,
                       SPIKE_MANA, FIRE_MANA, HUNGER_TIME, SLEEPLESS_TIME, LAVA_HEAT_STAM,
                       MANA_MASTERY_SCALE, ADULT_MANA_BONUS, ADULT_SPELL_MULT, MASTERY_SPELL_BONUS,
                       SUN_ADAPT_SCALE, SUN_ADAPT_DMG, SUN_ADAPT_VEIL)
from . import texts


def approach(v, target, step):
    if v < target:
        return min(target, v + step)
    return max(target, v - step)


class Player:
    def __init__(self, x, y, stage=0):
        self.stage = stage
        s = STAGES[stage]
        self.w, self.h = s["w"], s["h"]
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.facing = 1
        self.hp = s["max_hp"] * 0.6          # she wakes up hungry
        self.mana = s["max_mana"] * 0.5
        self.stamina = s["max_stam"]
        self.abilities = set()
        self.mana_cap = 1.0            # set every frame from the moral path effects
        self.mana_spent = 0.0          # Manaschulung: all mana she has ever used (any age)
        self.sun_exposure = 0.0        # Lichtgewöhnung: seconds she has endured sunlight
        self.food = {"milk": 0, "fish": 0, "meat": 0}
        self.on_ground = False
        self.in_water = False
        self.in_deep = False           # deep ice water ('w') – Tauchen, breath
        self.breath = 9.0              # seconds of air left under deep water (refilled by snow.Snowlands)
        self.cold_regen = 1.0          # stamina regeneration multiplier (the cold lowers it)
        self.gliding = False
        self.flying = False
        self.exhausted = 0.0
        self.coyote = 0.0
        self.jump_cut = False
        self.last_wall = 0
        self.wall = 0
        self.attack = None
        self.combo = 0
        self.combo_window = 0.0
        self.invuln = 0.0
        self.dash_t = 0.0
        self.diving = False
        self.fire_on = False
        self.awake_time = 0.0
        self.hunger_time = 0.0
        self.anim_t = 0.0
        self.flap_anim = 0.0
        self.burning = 0.0
        self.hurt_flash = 0.0
        self.dead = False
        self.pose_override = None      # "eat" / "sleep" during rests and cutscenes
        self.slow_walk = False         # used by the greed ending

    # ---- derived stats ----------------------------------------------------
    @property
    def s(self):
        return STAGES[self.stage]

    def max_hp(self):
        return self.s["max_hp"]

    def max_mana(self):
        # adult: the training from all the mana she has used becomes a bigger pool;
        # "Überfluss" (moral subpath) scales the whole thing
        return (self.s["max_mana"] + self.mana_bonus()) * self.mana_cap

    # ---- Manaschulung -------------------------------------------------------
    def mastery(self):
        """0..1 – how practised she is with her magic, from all the mana she has ever spent."""
        return 1.0 - math.exp(-self.mana_spent / MANA_MASTERY_SCALE)

    def mana_bonus(self):
        return ADULT_MANA_BONUS * self.mastery() if self.stage == 2 else 0.0

    def spell_mult(self):
        """Damage multiplier for her magic: only the grown body can unleash it fully."""
        if self.stage < 2:
            return 1.0
        return ADULT_SPELL_MULT * (1.0 + MASTERY_SPELL_BONUS * self.mastery())

    # ---- Lichtgewöhnung -------------------------------------------------------
    def adaptation(self):
        """0..1 – how used her body is to sunlight (it only grows by enduring it)."""
        return 1.0 - math.exp(-self.sun_exposure / SUN_ADAPT_SCALE)

    def sun_dmg_mult(self):
        return 1.0 - SUN_ADAPT_DMG * self.adaptation()

    def sun_veil_mult(self):
        return 1.0 - SUN_ADAPT_VEIL * self.adaptation()

    def spend_mana(self, amount):
        amount = max(0.0, min(amount, self.mana))
        self.mana -= amount
        self.mana_spent += amount
        return amount

    def max_stam(self, mods=None):
        """mods = Morality.mods() (moral path effects); None means unaffected."""
        m = self.s["max_stam"]
        if mods:
            m *= mods["max_stam"]
        if self.hungry():
            m *= 0.8
        return m

    def hungry(self):
        return self.hunger_time > HUNGER_TIME

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    @property
    def feet(self):
        return self.y + self.h

    def rect(self):
        return (self.x, self.y, self.w, self.h)

    def in_chimney(self, level, max_gap=4):
        """Wall jumps only work between two close rock walls (zigzag climbing).
        Kicking off a single cliff face would let her skip growth gates."""
        if not self.wall:
            return False
        step = -self.wall
        edge = self.x - 1 if step < 0 else self.x + self.w
        for i in range(max_gap + 1):
            if level.rect_solid(edge + step * i * TILE, self.y + 2, 1, self.h - 4):
                return True
        return False

    def can_fly(self):
        return self.stage == 2 and "flight_seen" in self.abilities

    # ---- serialisation ----------------------------------------------------
    def to_dict(self):
        return dict(stage=self.stage, x=self.x, y=self.y, hp=self.hp, mana=self.mana,
                    stamina=self.stamina, abilities=sorted(self.abilities), food=self.food,
                    awake_time=self.awake_time, hunger_time=self.hunger_time, facing=self.facing,
                    mana_spent=self.mana_spent, sun_exposure=self.sun_exposure)

    @classmethod
    def from_dict(cls, d):
        p = cls(d["x"], d["y"], d["stage"])
        p.mana_spent = d.get("mana_spent", 0.0)
        p.sun_exposure = d.get("sun_exposure", 0.0)
        p.hp, p.mana, p.stamina = d["hp"], d["mana"], d["stamina"]
        p.abilities = set(d["abilities"])
        p.food = dict(d["food"])
        p.awake_time = d.get("awake_time", 0.0)
        p.hunger_time = d.get("hunger_time", 0.0)
        p.facing = d.get("facing", 1)
        return p

    # ---- growth -----------------------------------------------------------
    def grow(self):
        feet, cx = self.feet, self.cx
        ratios = (self.hp / self.max_hp(), self.mana / self.max_mana())
        self.stage = min(2, self.stage + 1)
        self.w, self.h = self.s["w"], self.s["h"]
        self.x, self.y = cx - self.w / 2, feet - self.h
        self.hp = self.max_hp() * ratios[0]
        self.mana = self.max_mana() * ratios[1]
        self.stamina = self.s["max_stam"]

    # ---- damage -----------------------------------------------------------
    def hurt(self, amount, from_x=None, knock=True):
        if self.invuln > 0 or self.dash_t > 0 or self.dead:
            return False
        self.hp -= amount
        self.hurt_flash = 0.25
        self.invuln = 0.8
        if knock and from_x is not None:
            d = 1 if self.cx >= from_x else -1
            self.vx = d * 260
            self.vy = -260
            self.on_ground = False
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return True

    def burn(self, amount):
        """Damage over time from light – no knockback, no invulnerability frames."""
        if self.dead:
            return
        self.hp -= amount
        self.burning = 0.2
        if self.hp <= 0:
            self.hp = 0
            self.dead = True

    # ---- per-frame --------------------------------------------------------
    def update(self, dt, ctl, play):
        level = play.level
        mods = play.morality.mods()
        cost_mult = mods["stam_cost"]
        mana_mult = mods["mana_cost"]
        self.mana_cap = mods["max_mana"]
        self.mana = min(self.mana, self.max_mana())
        step = int(self.mastery() * 4)                 # tell the player at 25 / 50 / 75 % training
        if getattr(self, "_mastery_step", None) is None:
            self._mastery_step = step
        elif step > self._mastery_step:
            self._mastery_step = step
            key = "mastery_adult" if self.stage == 2 else "mastery_young"
            play.toast(texts.TOASTS[key].format(pct=step * 25))
        s = self.s
        self.anim_t += dt
        self.invuln = max(0.0, self.invuln - dt)
        self.hurt_flash = max(0.0, self.hurt_flash - dt)
        self.burning = max(0.0, self.burning - dt)
        self.combo_window = max(0.0, self.combo_window - dt)
        self.flap_anim = max(0.0, self.flap_anim - dt)
        self.coyote = max(0.0, self.coyote - dt)
        was_hungry = self.hungry()
        self.awake_time += dt
        self.hunger_time += dt
        if self.hungry() and not was_hungry:
            play.toast(texts.TOASTS["hungry"])
        if self.awake_time > SLEEPLESS_TIME:
            play.morality.add(madness=dt / 60.0, deed="sleepless")
            if int(self.awake_time) % 90 == 0 and int(self.awake_time - dt) % 90 != 0:
                play.toast(texts.TOASTS["sleepless"])
        if self.exhausted > 0:
            self.exhausted -= dt
            if self.exhausted <= 0 and self.stamina < self.max_stam(mods) * 0.25:
                self.exhausted = 0.05          # stay exhausted until she has caught her breath
        locked = play.input_locked()
        ax = 0 if locked else ctl.axis()
        if self.slow_walk:
            ax = max(0, ax)

        # ---------------- dash (Schattensprung) ----------------
        if self.dash_t > 0:
            self.dash_t -= dt
            self.vy = 0
            self._move(dt, level, play)
            return
        if not locked and ctl.hit("dash") and self.stage >= 1 and self.exhausted <= 0:
            cost = DASH_COST * cost_mult
            if self.stamina >= cost:
                self.stamina -= cost
                self.dash_t = 0.18
                self.vx = self.facing * 720
                self.invuln = max(self.invuln, 0.25)
                self.attack = None
                play.particles.burst(self.cx, self.cy, (40, 20, 60), 18, 160)
                return

        # ---------------- horizontal ----------------
        sprinting = (not locked and ctl.down("sprint") and ax != 0 and self.stamina > 0
                     and self.exhausted <= 0 and not self.in_water and not self.slow_walk)
        speed = s["walk"]
        if sprinting:
            speed *= SPRINT_MULT
            self.stamina -= SPRINT_DRAIN * cost_mult * dt
        if not self.on_ground and self.gliding and self.vy > 0:
            speed = max(speed, s["walk"] * 1.4)
        elif self.flying:
            speed = max(speed, s["walk"] * 1.5)
        if self.exhausted > 0:
            speed *= 0.55
        if self.in_water:
            speed *= 0.6
        if self.slow_walk:
            speed = 45
        if self.attack and self.on_ground and self.attack["kind"] in ("claw", "tail"):
            speed *= 0.45
        if self.fire_on:
            speed *= 0.4
        accel = 2600 if self.on_ground else 1500
        self.vx = approach(self.vx, ax * speed, accel * dt)
        if ax and not (self.attack and self.attack["t"] < self.attack["dur"]):
            self.facing = ax

        # ---------------- jump / wall jump / flap ----------------
        if not locked and ctl.hit("jump") and not self.slow_walk:
            if self.in_water:
                self.vy = -0.85 * s["jump"]
            elif self.on_ground or self.coyote > 0:
                self.vy = -s["jump"]
                self.on_ground = False
                self.coyote = 0
                self.jump_cut = True
            elif (self.wall and self.wall != self.last_wall and self.exhausted <= 0
                  and self.stamina >= WALLJUMP_COST * cost_mult and self.in_chimney(level)):
                self.stamina -= WALLJUMP_COST * cost_mult
                self.vy = -s["jump"] * 0.9
                self.vx = -self.wall * 320
                self.facing = -self.wall
                self.last_wall = self.wall
                self.jump_cut = True
            elif self.can_fly() and self.exhausted <= 0 and self.stamina > 0:
                self.stamina -= FLAP_COST * cost_mult
                self.vy = FLAP_VY
                self.flying = True
                self.flap_anim = 0.35
                self.jump_cut = False
        if ctl.up("jump") and self.vy < 0 and self.jump_cut:
            self.vy *= 0.45
            self.jump_cut = False

        self.gliding = (not locked and ctl.down("jump") and not self.on_ground and not self.in_water
                        and "glide" in self.abilities and self.exhausted <= 0 and not self.diving
                        and (self.stage < 2 or self.stamina > 0))

        # ---------------- gravity, glide, updraft ----------------
        in_updraft = self.gliding and level.tile_at(self.cx, self.cy) == "U"
        if in_updraft:
            # the warm wind carries her instead of gravity (a hatchling is too light to steer it upward)
            self.vy = approach(self.vy, s["updraft"], 1800 * dt)
            if self.stage == 0 and int(self.anim_t * 3) % 4 == 0:
                play.particles.burst(self.cx, self.cy, (200, 200, 230), 1, 60)
        elif self.in_deep:                                   # deep ice water ('w')
            if "dive" in self.abilities and not locked and ctl.down("down"):
                self.vy = approach(self.vy, 220, 900 * dt)  # Tauchen: she swims down
            elif "dive" not in self.abilities and level.tile_at(self.cx, self.y + 2) == "w":
                self.vy = approach(self.vy, -260, 1400 * dt)   # without Tauchen her body floats back up
            else:
                self.vy += GRAVITY * 0.12 * dt
                self.vy = max(-260, min(self.vy, 90))
        elif self.in_water:
            self.vy += GRAVITY * 0.35 * dt
            self.vy = min(self.vy, 160)
        else:
            self.vy += GRAVITY * dt
            self.vy = min(self.vy, 1300 if self.diving else MAX_FALL)
        if self.gliding and not in_updraft and self.vy > s["glide_fall"]:
            self.vy = max(s["glide_fall"], self.vy - 3200 * dt)
        if self.gliding and self.stage == 2:
            self.stamina -= ADULT_GLIDE_DRAIN * cost_mult * dt
        if not self.on_ground and level.lava_light_at(self.cx, self.cy):
            self.stamina -= LAVA_HEAT_STAM * dt * (0.5 if "ash_wings" in self.abilities else 1.0)

        # ---------------- stamina ----------------
        cold = self.cold_regen                                 # < 1 in the cold of the snowlands
        if self.on_ground and not sprinting:
            self.stamina += GROUND_STAM_REGEN * mods["stam_regen"] * cold * dt * (0.5 if self.exhausted > 0 else 1.0)
        elif self.in_water:
            self.stamina += WATER_STAM_REGEN * mods["stam_regen"] * cold * dt
        if self.stamina <= 0 and self.exhausted <= 0:
            self.stamina = 0
            self.exhausted = EXHAUST_TIME
            self.flying = False
            play.toast(texts.TOASTS["exhausted"])
        self.stamina = max(0.0, min(self.max_stam(mods), self.stamina))

        # ---------------- attacks ----------------
        if not locked and not self.slow_walk:
            self._attacks(dt, ctl, play, cost_mult, mana_mult, mods["claw_dmg"])
        else:
            self.fire_on = False
        if self.attack:
            self.attack["t"] += dt
            if self.attack["t"] >= self.attack["dur"]:
                self.attack = None

        self._move(dt, level, play)

    def _attacks(self, dt, ctl, play, cost_mult, mana_mult, claw_mult=1.0):
        s = self.s
        claw_dmg = s["claw"] * (1.6 if "obsidian" in self.abilities else 1.0) * claw_mult
        weak = 0.6 if self.exhausted > 0 else 1.0
        if ctl.hit("claw"):
            if (not self.on_ground and ctl.down("down") and self.stage == 2
                    and self.stamina >= DIVE_COST * cost_mult and not self.diving):
                self.stamina -= DIVE_COST * cost_mult
                self.diving = True
                self.vy = 950
                self.vx *= 0.3
                self.attack = dict(kind="dive", t=0, dur=99, dmg=claw_dmg * 1.5, hit=set())
            elif self.attack is None or (self.attack["kind"] == "claw" and self.attack["t"] > 0.14):
                self.combo = self.combo + 1 if self.combo_window > 0 else 1
                if self.combo > 3:
                    self.combo = 1
                mult = 1.5 if self.combo == 3 else 1.0
                dur = 0.26 if self.exhausted <= 0 else 0.4
                self.attack = dict(kind="claw", t=0, dur=dur, dmg=claw_dmg * mult * weak,
                                   hit=set(), combo=self.combo)
                self.combo_window = 0.5
        if ctl.hit("tail") and self.attack is None and self.exhausted <= 0:
            if self.stamina >= TAIL_COST * cost_mult:
                self.stamina -= TAIL_COST * cost_mult
                self.attack = dict(kind="tail", t=0, dur=0.35, dmg=claw_dmg * 0.8, hit=set())
        if ctl.hit("spike"):
            cost = SPIKE_MANA * mana_mult
            if self.mana >= cost:
                self.spend_mana(cost)
                play.spawn_spike(self)
            else:
                play.toast(texts.TOASTS["no_mana"], key="no_mana")
        self.fire_on = False
        if ctl.down("fire") and "fire" in self.abilities:
            cost = FIRE_MANA * mana_mult * dt
            if self.mana >= cost:
                self.spend_mana(cost)
                self.fire_on = True
            elif ctl.hit("fire"):
                play.toast(texts.TOASTS["no_mana"], key="no_mana")
        if ctl.hit("blood"):
            play.try_blood()

    # ---- hitboxes ---------------------------------------------------------
    def attack_box(self):
        a = self.attack
        if not a:
            return None
        r = self.s["reach"]
        if a["kind"] == "claw":
            if a["t"] > a["dur"] * 0.75:
                return None
            if self.facing > 0:
                return (self.x + self.w * 0.6, self.y - 6, r + self.w * 0.4, self.h + 10)
            return (self.x - r, self.y - 6, r + self.w * 0.4, self.h + 10)
        if a["kind"] == "tail":
            return (self.x - r * 1.3, self.y + self.h * 0.3, self.w + r * 2.6, self.h * 0.7)
        if a["kind"] == "dive":
            return (self.x - 4, self.y + self.h * 0.5, self.w + 8, self.h * 0.6)
        return None

    def fire_box(self):
        if not self.fire_on:
            return None
        length = (90, 120, 150)[self.stage]
        hy = self.y + self.h * 0.1
        if self.facing > 0:
            return (self.x + self.w, hy - 10, length, self.h * 0.6 + 20)
        return (self.x - length, hy - 10, length, self.h * 0.6 + 20)

    # ---- physics ----------------------------------------------------------
    def _move(self, dt, level, play):
        was_ground = self.on_ground
        self.x, hit_x = level.move_x(self.x, self.y, self.w, self.h, self.vx * dt)
        if hit_x:
            self.vx = 0
        self.y, hit_y = level.move_y(self.x, self.y, self.w, self.h, self.vy * dt)
        if hit_y:
            if self.vy > 0:
                if self.diving:
                    play.dive_impact(self)
                self.diving = False
                if self.attack and self.attack["kind"] == "dive":
                    self.attack = None
            self.vy = 0
        self.on_ground = self.vy >= 0 and level.rect_solid(self.x + 1, self.y + self.h, self.w - 2, 1)
        if self.on_ground:
            self.coyote = 0.1
            self.last_wall = 0
            self.flying = False
            if not was_ground and self.vy == 0:
                pass
        if not self.on_ground:
            if level.rect_solid(self.x - 1, self.y + 2, 1, self.h - 4):
                self.wall = -1
            elif level.rect_solid(self.x + self.w, self.y + 2, 1, self.h - 4):
                self.wall = 1
            else:
                self.wall = 0
        else:
            self.wall = 0
        here = level.tile_at(self.cx, self.cy)
        self.in_water = here in "~w"
        self.in_deep = here == "w"
        if self.in_water:
            self.flying = False
            self.diving = False

        # hazards
        if level.rect_has(self.x + 4, self.y + 4, self.w - 8, self.h - 4, "xL"):
            self.hp = 0
            self.dead = True
        elif level.rect_has(self.x + 2, self.y + 2, self.w - 4, self.h - 2, "^"):
            self.hurt(20, self.cx + 1)

    def pose(self):
        if self.pose_override:
            return self.pose_override
        if self.dash_t > 0:
            return "dash"
        if self.diving:
            return "dive"
        if self.fire_on:
            return "fire"
        if self.attack:
            return self.attack["kind"]
        if self.in_water:
            return "swim"
        if not self.on_ground:
            if self.flap_anim > 0:
                return "flap"
            if self.gliding and self.vy >= 0:
                return "glide"
            if self.flying:
                return "glide"
            return "jump"
        if self.exhausted > 0:
            return "exhausted"
        if abs(self.vx) > 10:
            return "run" if abs(self.vx) > self.s["walk"] * 1.2 else "walk"
        return "idle"
