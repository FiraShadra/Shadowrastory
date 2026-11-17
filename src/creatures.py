"""Everything that lives in Shadowra's world besides her."""
import math
import random

from .settings import TILE, GRAVITY


class Particles:
    def __init__(self):
        self.items = []

    def burst(self, x, y, color, n=10, speed=120, life=0.6, size=3, up=0.0):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(0.3, 1.0) * speed
            self.items.append([x, y, math.cos(a) * v, math.sin(a) * v - up, life, life, color, size])

    def update(self, dt):
        for p in self.items:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 200 * dt
            p[4] -= dt
        self.items = [p for p in self.items if p[4] > 0]


class Projectile:
    def __init__(self, x, y, vx, vy, dmg, owner, kind, r=6, life=2.0):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.dmg, self.owner, self.kind, self.r, self.life = dmg, owner, kind, r, life
        self.alive = True

    def update(self, dt, level):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0 or level.solid(int(self.x // TILE), int(self.y // TILE)):
            self.alive = False


class Creature:
    kind = "creature"
    hostile = False
    blood = None           # None = cannot drink, otherwise moral category
    w, h = 30, 30
    max_hp = 20
    contact = 0
    gravity = True
    edible = False         # adult can eat the corpse

    def __init__(self, x, y, oid):
        self.id = oid
        self.x = x * TILE + TILE / 2 - self.w / 2
        self.y = (y + 1) * TILE - self.h
        self.home = (self.x, self.y)
        self.vx = self.vy = 0.0
        self.hp = self.max_hp
        self.alive = True
        self.corpse_t = 0.0
        self.stun = 0.0
        self.flash = 0.0
        self.facing = -1
        self.anim_t = random.random() * 3
        self.on_ground = False
        self.fleeing = False

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def rect(self):
        return (self.x, self.y, self.w, self.h)

    def hurt(self, dmg, from_x, knock=150, play=None):
        if not self.alive:
            return False
        self.hp -= dmg
        self.flash = 0.15
        d = 1 if self.cx >= from_x else -1
        self.vx = d * knock
        if self.gravity and knock > 0:
            self.vy = -knock * 0.6
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.corpse_t = 6.0
        return True

    def weakened(self):
        return self.alive and self.hp <= self.max_hp * 0.35

    def physics(self, dt, level):
        if self.gravity:
            self.vy = min(self.vy + GRAVITY * dt, 900)
        nx, hx = level.move_x(self.x, self.y, self.w, self.h, self.vx * dt)
        self.x = nx
        if hx:
            self.vx = 0
            self.facing *= -1
        ny, hy = level.move_y(self.x, self.y, self.w, self.h, self.vy * dt)
        self.y = ny
        if hy:
            self.vy = 0
        self.on_ground = level.rect_solid(self.x + 1, self.y + self.h, self.w - 2, 1)
        if level.rect_has(self.x, self.y, self.w, self.h, "xL"):
            self.alive = False
            self.corpse_t = 0

    def wall_ahead(self, level):
        fx = self.x + self.w + 3 if self.facing > 0 else self.x - 3
        return level.solid(int(fx // TILE), int((self.y + self.h - 6) // TILE))

    def ledge_ahead(self, level):
        fx = self.x + self.w + 2 if self.facing > 0 else self.x - 2
        return not level.solid(int(fx // TILE), int((self.y + self.h + 4) // TILE))

    def update(self, dt, play):
        self.anim_t += dt
        self.flash = max(0.0, self.flash - dt)
        if not self.alive:
            self.corpse_t -= dt
            self.vx *= 0.9
            if self.gravity:
                self.physics(dt, play.level)
            return
        if self.stun > 0:
            self.stun -= dt
            self.vx *= 0.9
            self.physics(dt, play.level)
            return
        self.think(dt, play)
        self.physics(dt, play.level)

    def think(self, dt, play):
        pass


class Peaceful(Creature):
    """Moosläufer – a gentle, warm-blooded grazer. Shadowra does not like hunting them."""
    kind = "peaceful"
    blood = "peaceful"
    edible = True
    w, h = 34, 26
    max_hp = 25

    def __init__(self, x, y, oid):
        super().__init__(x, y, oid)
        self.timer = random.uniform(1, 3)
        self.scared = 0.0

    def think(self, dt, play):
        p = play.player
        dist = math.hypot(p.cx - self.cx, p.cy - self.cy)
        self.scared = max(0.0, self.scared - dt)
        m = play.morality
        loved = play.hugs.loves(self)
        # They only flee from a *threatening* dragon: sprinting, attacking, a dark soul – or after a
        # rejected hug. A calm Shadowra may walk right up to them.
        threat = (play.threatening() or self.scared > 0 or m.trust() == "gone"
                  or (m.corruption >= 15 and not loved))
        self.fleeing = dist < m.flee_radius() and threat
        if not self.fleeing and dist < 260 and abs(p.cy - self.cy) < 80 and not threat:
            self.facing = 1 if p.cx > self.cx else -1          # curious: watch her
            if loved and dist > 70:
                self.vx = self.facing * 70                     # they come to her once they love her
            elif dist < 150:
                self.vx = 0
            if self.on_ground and self.ledge_ahead(play.level):
                self.vx = 0
            return
        if self.fleeing:
            self.facing = 1 if self.cx > p.cx else -1
            self.vx = self.facing * 250
            if self.on_ground and self.ledge_ahead(play.level):
                self.vy = -500
        else:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = random.uniform(1.5, 4)
                self.facing = random.choice((-1, 1)) if random.random() < 0.7 else self.facing
                self.vx = self.facing * random.choice((0, 0, 60))
            if abs(self.cx - self.home[0]) > 4 * TILE:
                self.facing = 1 if self.home[0] > self.cx else -1
                self.vx = self.facing * 60
            if self.on_ground and self.ledge_ahead(play.level):
                self.facing *= -1
                self.vx = self.facing * abs(self.vx)


class Fish(Creature):
    kind = "fish"
    blood = "fish"
    w, h = 22, 12
    max_hp = 1
    gravity = False

    def __init__(self, x, y, oid):
        super().__init__(x, y, oid)
        self.y = y * TILE + 10
        self.home = (self.x, self.y)
        self.facing = random.choice((-1, 1))
        self.respawn = 0.0

    def think(self, dt, play):
        lvl = play.level
        p = play.player
        speed = 60
        if math.hypot(p.cx - self.cx, p.cy - self.cy) < 70:
            speed = 105            # a little slower than a swimming juvenile: catchable, not free
            self.facing = 1 if self.cx > p.cx else -1
        nx = self.cx + self.facing * (self.w / 2 + 4)
        if lvl.tile_at(nx, self.cy) not in "~w":
            self.facing *= -1
        self.vx = self.facing * speed
        self.vy = math.sin(self.anim_t * 2) * 20
        if lvl.tile_at(self.cx, self.y + self.vy * dt - 2) not in "~w" or lvl.tile_at(self.cx, self.y + self.h + 4) not in "~w":
            self.vy = 0

    def physics(self, dt, level):
        nx = self.x + self.vx * dt
        if level.tile_at(nx + self.w / 2, self.cy) in "~w":
            self.x = nx
        ny = self.y + self.vy * dt
        if level.tile_at(self.cx, ny) in "~w" and level.tile_at(self.cx, ny + self.h) in "~w":
            self.y = ny


class Priest(Creature):
    """Lichtpriester – Mafor's servants. Their torches burn Shadowra."""
    kind = "priest"
    hostile = True
    blood = "priest"
    w, h = 30, 44
    max_hp = 40
    torch_r = 85

    def __init__(self, x, y, oid):
        super().__init__(x, y, oid)
        self.cool = random.uniform(1.0, 2.0)

    def think(self, dt, play):
        p = play.player
        dx = p.cx - self.cx
        dist = math.hypot(dx, p.cy - self.cy)
        if dist < 400:
            self.facing = 1 if dx > 0 else -1
            self.vx = 0
            self.cool -= dt
            if self.cool <= 0:
                self.cool = 2.2
                ang = math.atan2(p.cy - self.cy, dx)
                play.spawn_enemy_orb(self.cx, self.y + 12, ang, 300, 12)
        else:
            if abs(self.cx - self.home[0]) > 3 * TILE or self.ledge_ahead(play.level):
                self.facing = 1 if self.home[0] > self.cx else -1
            self.vx = self.facing * 50

    def light(self):
        if self.alive:
            return (self.cx + self.facing * 14, self.y + 10, self.torch_r)
        return None


class Skeleton(Creature):
    kind = "skeleton"
    hostile = True
    w, h = 30, 44
    max_hp = 35
    contact = 12

    def think(self, dt, play):
        p = play.target_of(self)
        dx = p.cx - self.cx
        raider = getattr(self, "grove", False)      # grove monsters march on the elves' camp
        if raider or (abs(dx) < 330 and abs(p.cy - self.cy) < 140):
            self.facing = 1 if dx > 0 else -1
            self.vx = self.facing * 95 if abs(dx) > 8 else 0
            if not raider and self.ledge_ahead(play.level):
                self.vx = 0
            if raider and self.on_ground and self.wall_ahead(play.level):
                self.vy = -800                         # climb out of the pond / up the 4-tile camp ledge
        else:
            self.vx = 0


class Skull(Creature):
    kind = "skull"
    hostile = True
    w, h = 30, 30
    max_hp = 20
    contact = 10
    gravity = False

    def think(self, dt, play):
        p = play.target_of(self)
        dx, dy = p.cx - self.cx, p.cy - self.cy
        d = math.hypot(dx, dy)
        if d < 460 or getattr(self, "grove", False):
            self.facing = 1 if dx > 0 else -1
            self.vx = dx / max(d, 1) * 115
            self.vy = dy / max(d, 1) * 115 + math.sin(self.anim_t * 4) * 60
        else:
            self.vx = math.sin(self.anim_t) * 40
            self.vy = math.cos(self.anim_t * 1.3) * 30

    def physics(self, dt, level):
        nx, _ = level.move_x(self.x, self.y, self.w, self.h, self.vx * dt)
        ny, _ = level.move_y(nx, self.y, self.w, self.h, self.vy * dt)
        self.x, self.y = nx, ny
        if not self.alive:
            self.vy += 600 * dt


class Owl(Creature):
    kind = "owl"
    blood = "peaceful"
    w, h = 28, 34
    max_hp = 20
    gravity = False

    def __init__(self, x, y, oid):
        super().__init__(x, y, oid)
        self.talked = False
        self.gift_given = False
        self.leaving = False

    def think(self, dt, play):
        if self.leaving:
            self.vy = -160
            self.vx = 120
            if self.y < -200:
                self.alive = False
                self.corpse_t = 0
            return
        self.vx = self.vy = 0
        self.facing = 1 if play.player.cx > self.cx else -1

    def physics(self, dt, level):
        self.x += self.vx * dt
        self.y += self.vy * dt


class Fira(Creature):
    """Firas Käfig auf dem Gipfel."""
    kind = "fira"
    w, h = 60, 46
    max_hp = 9999
    gravity = True

    def __init__(self, x, y, oid):
        super().__init__(x, y, oid)
        self.caged = True
        self.facing = -1

    def hurt(self, *a, **k):
        return False


class FiraCompanion(Creature):
    """Fira after he is free (light / redemption): he stays close to Shadowra – walks beside her, flies
    when she flies, and catches up if she gets too far ahead. He can't be hurt."""
    kind = "fira_companion"
    name = "Fira"
    friendly = True                  # her attacks pass through him
    w, h = 56, 42
    max_hp = 9999
    gravity = False
    FOLLOW = 90                      # px behind her

    def __init__(self, x, y, oid="fira_companion"):
        super().__init__(x, y, oid)
        self.facing = 1
        self.pose = "idle"
        self.talk_i = 0

    def hurt(self, *a, **k):
        return False

    def update(self, dt, play):
        p = play.player
        self.anim_t += dt
        tx = p.cx - p.facing * self.FOLLOW
        ty = p.feet - self.h                      # his feet level with hers
        dx, dy = tx - self.cx, ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 900:                            # fell far behind (teleport, burrow, passage): catch up
            self.x, self.y = tx - self.w / 2, ty
            return
        speed = min(520.0, 2.6 * dist)
        if dist > 4:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = self.vy = 0.0
        self.x += self.vx * dt
        self.y += self.vy * dt
        if abs(self.vx) > 20:
            self.facing = 1 if self.vx > 0 else -1
        elif abs(p.cx - self.cx) > 10:
            self.facing = 1 if p.cx > self.cx else -1
        grounded = play.level.rect_solid(self.x + 2, self.y + self.h + 2, self.w - 4, 4)
        if not grounded and abs(dy) > 6:
            self.pose = "flap" if int(self.anim_t * 2.4) % 2 == 0 else "glide"
        elif abs(self.vx) > 30:
            self.pose = "walk"
        else:
            self.pose = "idle"


class Mafor(Creature):
    kind = "boss"
    hostile = True
    blood = "priest"
    w, h = 90, 130
    max_hp = 700
    contact = 15
    gravity = False
    aura_r = 130

    def __init__(self, x, y, oid, arena_left):
        super().__init__(x, y, oid)
        self.arena_left = arena_left * TILE
        self.active = False
        self.defeated = False
        self.orb_cool = 2.0
        self.strike_cool = 4.0
        self.strike = None         # dict(x, t) telegraph then beam
        self.summoned = False
        self.floor_y = self.y            # set properly by the play state once the level is known
        self.base_y = self.y - 40
        self.y = self.base_y
        self.target_x = self.x

    def hurt(self, dmg, from_x, knock=0, play=None):
        if not self.active or self.defeated:
            return False
        self.hp -= dmg
        self.flash = 0.12
        if self.hp <= 0:
            self.hp = 1
            self.defeated = True
            self.strike = None
        return True

    def update(self, dt, play):
        self.anim_t += dt
        self.flash = max(0.0, self.flash - dt)
        if not self.active:
            return
        if self.defeated:
            self.y = min(self.y + 120 * dt, self.floor_y)
            return
        p = play.player
        rage = self.hp < self.max_hp * 0.5
        if rage and not self.summoned:
            self.summoned = True
            play.summon_priests(self)
        # drift around the arena, staying above the player
        if abs(self.target_x - self.cx) < 20 or random.random() < 0.004:
            lo = self.arena_left + 80
            hi = self.arena_left + 32 * TILE - 80
            self.target_x = min(hi, max(lo, p.cx + random.uniform(-260, 260)))
        self.vx = max(-160, min(160, (self.target_x - self.cx) * 1.5))
        self.x += self.vx * dt
        self.y = self.base_y + math.sin(self.anim_t * 1.4) * 30
        self.facing = 1 if p.cx > self.cx else -1
        # orb volleys
        self.orb_cool -= dt
        if self.orb_cool <= 0:
            self.orb_cool = 1.6 if rage else 2.4
            base = math.atan2(p.cy - self.cy, p.cx - self.cx)
            n = 7 if rage else 5
            for i in range(n):
                a = base + (i - (n - 1) / 2) * 0.22
                play.spawn_enemy_orb(self.cx, self.cy, a, 260 if not rage else 320, 14)
        # sun strike: telegraph, then a beam of light
        if self.strike is None:
            self.strike_cool -= dt
            if self.strike_cool <= 0:
                self.strike = dict(x=p.cx, t=0.0)
                self.strike_cool = 3.5 if rage else 5.0
        else:
            self.strike["t"] += dt
            if self.strike["t"] > 2.0:
                self.strike = None

    def strike_rect(self):
        if self.strike and 1.0 <= self.strike["t"] <= 2.0:
            return (self.strike["x"] - 40, 0, 80, 12 * TILE)
        return None

    def light(self):
        if self.active and not self.defeated:
            return (self.cx, self.cy, self.aura_r)
        return None


KINDS = {
    "peaceful": Peaceful,
    "fish": Fish,
    "priest": Priest,
    "skeleton": Skeleton,
    "skull": Skull,
    "owl": Owl,
    "fira": Fira,
}
