"""Kapitel 2 – the snowlands at play time: the Frostpass, arrival (with Fira, alone – or carrying grief),
cold and the warmth of hearths, the humans, the otters (Tauchen), breath under the ice, the north road.

The map lives in src/world/snowylands (+ icecave, snowyvillage) and src/world/underwater.
"""
import math
import random

import pygame

from .settings import TILE, SCREEN_W, SCREEN_H
from . import abilities, render, texts
from .humans import Human, attitude_for

COLD_DRAIN = 5.0             # stamina per second in the cold (halved by the Herdsegen)
COLD_REGEN = 0.0             # in the cold her stamina does not come back – only at a hearth
COLD_HP = 3.0                # life per second once her stamina is gone
HEARTH_R = 7 * TILE          # warmth radius of a hearth
BREATH = 9.0                 # seconds under deep water (x2.5 with Tiefenatem)
DROWN_HP = 15.0
SNOW_DECOR = frozenset(("pine", "snowrock", "icicle", "humanhouse", "fence", "lantern_snow", "reed_frost", "kelp"))


class Snowlands:
    def __init__(self, play):
        self.play = play
        objs = play.snow_objects
        self.passages = [o for o in objs if o["kind"] == "passage"]
        self.hearths = [o for o in objs if o["kind"] == "hearth"]
        self.triggers = [o for o in objs if o["kind"] in ("snow_intro", "snow_arrive", "otters", "chapter_end")]
        self.humans = []
        for o in objs:
            if o["kind"] == "human":
                h = Human(o["x"], o["y"], o["id"], o["name"], o["gender"], o["role"])
                self.humans.append(h)
                play.creatures.append(h)
        self.frost = 0.0             # 0..1, frost on the screen edges
        self.warm = False
        self.att_t = 0.0
        self.refresh_attitude()

    # ---- helpers --------------------------------------------------------------------
    def attitude(self):
        return attitude_for(self.play.morality)

    def refresh_attitude(self):
        a = self.attitude()
        for h in self.humans:
            if h.alive and not h.leaving:
                h.attitude = a

    def near_hearth(self, px, py):
        return any(math.hypot(px - (o["x"] * TILE + 16), py - (o["y"] + 1) * TILE) < HEARTH_R for o in self.hearths)

    def max_breath(self):
        return BREATH * (2.5 if "deep_breath" in self.play.player.abilities else 1.0)

    # ---- per frame --------------------------------------------------------------------
    def update(self, dt):
        play, p = self.play, self.play.player
        flags = play.flags
        play.morality.grief = "left_fira" in flags and "mafor_defeated" not in flags
        self.att_t -= dt
        if self.att_t <= 0:
            self.att_t = 1.0
            self.refresh_attitude()
        if play.input_locked():
            return
        self.check_triggers()
        # --- cold ---
        lvl = play.level
        cold = lvl.is_cold(p.cx, p.cy) and "frost_scales" not in p.abilities
        self.warm = self.near_hearth(p.cx, p.feet)
        if self.warm:
            cold = False
        blessing = 0.5 if "hearth_blessing" in p.abilities else 1.0
        p.cold_regen = COLD_REGEN if cold else 1.0
        if cold:
            p.stamina = max(0.0, p.stamina - COLD_DRAIN * blessing * dt)
            if p.stamina <= 0.5:
                p.hp -= COLD_HP * blessing * dt
                play.toast(texts.SNOW["cold_hurt"], key="cold_hurt")
                if p.hp <= 0:
                    p.hp, p.dead = 0, True
            if "cold_hint" not in flags:
                flags.add("cold_hint")
                play.hud.toast(texts.SNOW["cold_hint"], dur=5.0)
        self.frost += ((1.0 if cold else 0.0) - self.frost) * min(1.0, dt * 1.5)
        # --- breath under deep water ---
        mb = self.max_breath()
        if lvl.tile_at(p.cx, p.y + 4) == "w":
            p.breath = max(0.0, p.breath - dt)
            if p.breath < mb * 0.3:
                play.toast(texts.SNOW["breath_low"], key="breath_low")
            if p.breath <= 0:
                p.hp -= DROWN_HP * dt
                if p.hp <= 0:
                    p.hp, p.dead = 0, True
        else:
            p.breath = min(mb, p.breath + dt * 4)
        if p.in_deep and "dive" not in p.abilities:
            play.toast(texts.SNOW["deep_no_dive"], key="deep_no_dive")

    def check_triggers(self):
        play, p = self.play, self.play.player
        flags = play.flags
        for tr in self.triggers:
            tx = tr["x"] * TILE
            near = abs(p.cx - (tx + 16)) < 48 and abs(p.feet - (tr["y"] + 1) * TILE) < 60
            same_level = abs(p.feet - (tr["y"] + 1) * TILE) < 5 * TILE    # (the tunnel lies under the summit)
            k = tr["kind"]
            if not same_level:
                continue
            if k == "snow_intro" and p.cx > tx and "frostpass_seen" not in flags:
                flags.add("frostpass_seen")
                play.dialog.show(texts.SNOW["frostpass"])
            elif k == "snow_arrive" and p.cx > tx and "snow_arrived" not in flags:
                flags.add("snow_arrived")
                p.vx = 0
                play.record_event("north")
                if "mafor_defeated" not in flags:          # she left Fira in his cage
                    flags.add("left_fira")
                    play.dialog.show(texts.SNOW["arrive"] + texts.SNOW["grief"])
                else:
                    extra = {"fira_joined": "arrive_fira", "fira_dead": "arrive_mad",
                             "fira_caged": "arrive_caged"}
                    line = next((texts.SNOW[v] for f, v in extra.items() if f in flags), None)
                    play.dialog.show(texts.SNOW["arrive"] + ([line] if line else []))
            elif k == "otters" and near and "dive" not in p.abilities:
                p.vx = 0
                play.cutscene = dict(kind="otters", t=0.0)

                def done():
                    p.abilities.add("dive")
                    play.record_event("dive")
                    play.cutscene = None
                play.dialog.show(texts.SNOW["otters"], on_done=done)
            elif k == "chapter_end" and near and "north_road" not in flags:
                flags.add("north_road")
                lines = list(texts.SNOW["north"])
                if "fira_joined" in flags:
                    lines.insert(1, texts.SNOW["north_fira"])
                elif "fira_dead" in flags:
                    lines.insert(1, texts.SNOW["north_mad"])
                play.dialog.show(lines)

    # ---- E: passages, humans, Fira --------------------------------------------------
    def nearest_passage(self):
        p = self.play.player
        for o in self.passages:
            if abs(p.cx - (o["x"] * TILE + 16)) < 50 and abs(p.feet - (o["y"] + 1) * TILE) < 40:
                return o
        return None

    def use_passage(self, o):
        p = self.play.player
        tx, ty = o["to"]
        p.x = tx * TILE + TILE / 2 - p.w / 2
        p.y = (ty + 1) * TILE - p.h
        p.vx = p.vy = 0
        self.play.particles.burst(p.cx, p.feet, (200, 220, 255), 16, 100)

    def talk_human(self, h):
        play = self.play
        att = self.attitude()
        if att == "wary":
            play.dialog.show([(h.name, texts.HUMAN_TALK["wary"])])
            return
        lines = []
        if play.companion and "humans_saw_fira" not in play.flags:
            play.flags.add("humans_saw_fira")
            lines.append((h.name, texts.HUMAN_TALK["fira"]))
        talk = texts.HUMANS[h.name]["talk"]
        lines.append((h.name, talk[h.talk_i % len(talk)]))
        h.talk_i += 1
        p = play.player
        if h.role == "elder" and "hearth_blessing" not in p.abilities:     # Gunnar's gift
            lines += texts.HUMAN_TALK["elder_gift"]
            p.abilities.add("hearth_blessing")
            play.record_event("gift", "hearth_blessing")
            lines.append((texts.UI["new_item"] + abilities.name("hearth_blessing"), abilities.desc("hearth_blessing")))
        play.dialog.show(lines)

    def talk_fira(self):
        c = self.play.companion
        self.play.dialog.show([texts.FIRA_TALK[c.talk_i % len(texts.FIRA_TALK)]])
        c.talk_i += 1

    def altar_locked(self, altar):
        return altar.get("locked_humans") and self.attitude() != "kind"

    # ---- drawing ------------------------------------------------------------------------
    def draw_world(self, screen, cam):
        t = self.play.t
        for o in self.passages:                              # the icy cleft / the way back up
            x = o["x"] * TILE + 16 - cam[0]
            y = (o["y"] + 1) * TILE - cam[1]
            if not -100 < x < SCREEN_W + 100:
                continue
            pygame.draw.ellipse(screen, (150, 190, 230), (x - 26, y - 12, 52, 16))
            pygame.draw.ellipse(screen, (16, 24, 44), (x - 20, y - 9, 40, 11))
            for i in range(3):                               # cold wind drifting out
                wx = x - 14 + i * 14 + math.sin(t * 2 + i) * 4
                pygame.draw.line(screen, (210, 230, 255), (wx, y - 14), (wx + 6, y - 30 - (t * 20 + i * 9) % 18), 1)
        for o in self.hearths:                               # the village hearth fire
            x = o["x"] * TILE + 16 - cam[0]
            y = (o["y"] + 1) * TILE - cam[1]
            if not -200 < x < SCREEN_W + 200:
                continue
            render.draw_light_circle(screen, x, y - 20, 120, col=(255, 170, 80), alpha=70)
            pygame.draw.ellipse(screen, (90, 80, 76), (x - 26, y - 10, 52, 14))
            for i in range(5):                               # stones around the fire
                pygame.draw.circle(screen, (120, 110, 104), (int(x - 22 + i * 11), int(y - 4)), 5)
            for i in range(4):
                fh = 18 + 10 * math.sin(t * 7 + i * 1.7)
                fx = x - 9 + i * 6
                pygame.draw.polygon(screen, (255, 120, 40), [(fx - 5, y - 6), (fx, y - 6 - fh), (fx + 5, y - 6)])
                pygame.draw.polygon(screen, (255, 220, 120), [(fx - 2, y - 6), (fx, y - 6 - fh * 0.55), (fx + 2, y - 6)])
        for tr in self.triggers:                             # otters at the hole in the ice
            if tr["kind"] != "otters":
                continue
            x = tr["x"] * TILE + 16 - cam[0]
            y = (tr["y"] + 1) * TILE - cam[1]
            if not -100 < x < SCREEN_W + 100:
                continue
            for i in range(2):
                ph = (t * 0.6 + i * 0.5) % 1.0
                if ph < 0.6:                                 # popping up out of the water
                    ox = x - 30 + i * 60
                    oy = y + 10 - math.sin(ph / 0.6 * math.pi) * 22
                    pygame.draw.ellipse(screen, (110, 76, 52), (ox - 9, oy - 14, 18, 22))
                    pygame.draw.circle(screen, (130, 92, 64), (int(ox), int(oy - 14)), 7)
                    pygame.draw.circle(screen, (20, 14, 10), (int(ox + 3), int(oy - 16)), 1)
                    pygame.draw.circle(screen, (230, 220, 210), (int(ox + 5), int(oy - 12)), 2)

    def draw_decor(self, screen, d, x, y, back):
        kind = d["decor"]
        t = self.play.t
        if back and kind == "humanhouse":                    # a log house with a snowy roof and a chimney
            k = d.get("size", 1.0)
            w, h = 84 * k, 56 * k
            lit = self.attitude() != "hostile"
            pygame.draw.rect(screen, (104, 72, 48), (x - w / 2, y - h, w, h))
            for i in range(5):                               # logs
                ly = y - h + (i + 0.5) * h / 5
                pygame.draw.line(screen, (76, 52, 34), (x - w / 2, ly), (x + w / 2, ly), 2)
            roof = [(x - w / 2 - 14 * k, y - h + 4), (x, y - h - 38 * k), (x + w / 2 + 14 * k, y - h + 4)]
            pygame.draw.polygon(screen, (70, 50, 44), roof)
            pygame.draw.polygon(screen, (236, 242, 252), [(x - w / 2 - 14 * k, y - h + 4), (x, y - h - 38 * k),
                                                          (x + w / 2 + 14 * k, y - h + 4), (x, y - h - 26 * k)])
            pygame.draw.rect(screen, (90, 84, 80), (x + w / 4, y - h - 30 * k, 10 * k, 22 * k))
            for i in range(3):                               # chimney smoke
                sx = x + w / 4 + 5 * k + math.sin(t + i) * 6
                sy = y - h - 36 * k - ((t * 14 + i * 16) % 48)
                pygame.draw.circle(screen, (190, 196, 210), (int(sx), int(sy)), 4 + i)
            door = pygame.Rect(0, 0, 20 * k, 30 * k)
            door.midbottom = (x, y)
            pygame.draw.rect(screen, (50, 34, 22), door)
            win = (255, 200, 120) if lit else (60, 60, 80)
            for wx in (x - w / 3, x + w / 3):
                pygame.draw.rect(screen, win, (wx - 7 * k, y - h * 0.65, 14 * k, 12 * k))
                pygame.draw.rect(screen, (60, 40, 28), (wx - 7 * k, y - h * 0.65, 14 * k, 12 * k), 2)
        elif back and kind == "pine":                        # snowy fir tree
            pygame.draw.rect(screen, (70, 50, 36), (x - 5, y - 22, 10, 22))
            for i, (wid, top) in enumerate(((44, 34), (36, 58), (26, 80), (16, 98))):
                pts = [(x - wid, y - top + 30), (x, y - top - 16), (x + wid, y - top + 30)]
                pygame.draw.polygon(screen, (34, 70, 60), pts)
                pygame.draw.polygon(screen, (236, 242, 252), [(x - wid * 0.6, y - top + 8), (x, y - top - 16),
                                                              (x + wid * 0.6, y - top + 8), (x, y - top)])
        elif back and kind == "snowrock":
            pygame.draw.ellipse(screen, (90, 96, 116), (x - 22, y - 26, 44, 30))
            pygame.draw.ellipse(screen, (236, 242, 252), (x - 18, y - 28, 36, 12))
        elif back and kind == "icicle":                      # icicles hanging from the ceiling
            top = d["top"] * TILE - self.play.cam[1] if "top" in d else y - 120
            for i in range(4):
                ix = x - 18 + i * 12
                ln = 14 + (i * 7 + int(d["x"])) % 18
                pygame.draw.polygon(screen, (190, 226, 250), [(ix - 4, top), (ix, top + ln), (ix + 4, top)])
            pygame.draw.circle(screen, (200, 230, 255), (int(x), int(y - 3)), 3)
        elif not back and kind == "fence":
            for i in range(4):
                pygame.draw.rect(screen, (110, 80, 54), (x - 24 + i * 15, y - 26, 6, 26))
                pygame.draw.rect(screen, (240, 244, 252), (x - 25 + i * 15, y - 29, 8, 4))
            pygame.draw.line(screen, (96, 70, 48), (x - 26, y - 16), (x + 24, y - 16), 3)
        elif not back and kind == "lantern_snow":
            pygame.draw.line(screen, (80, 60, 44), (x, y), (x, y - 46), 3)
            render.draw_light_circle(screen, x, y - 48, 50, col=(255, 190, 110), alpha=70)
            pygame.draw.circle(screen, (255, 220, 150), (int(x), int(y - 48)), 6)
        elif not back and kind == "reed_frost":
            for i in range(5):
                pygame.draw.line(screen, (200, 214, 226), (x - 8 + i * 4, y), (x - 10 + i * 5, y - 20 - i % 3 * 6), 2)
        elif kind == "kelp" and back:
            for i in range(3):
                pts = [(x - 10 + i * 10 + math.sin(t * 1.3 + j * 0.7 + i) * 5, y - j * 12) for j in range(7)]
                pygame.draw.lines(screen, (40, 110, 90), False, pts, 4)

    def draw_overlay(self, screen):
        """Frost on the screen edges in the cold, and the breath bar under water."""
        if self.frost > 0.03:
            if not hasattr(self, "_frost_img"):
                s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                for i in range(30):
                    a = int(150 * (1 - i / 30) ** 2)
                    pygame.draw.rect(s, (210, 232, 255, a), (i * 4, i * 4, SCREEN_W - i * 8, SCREEN_H - i * 8), 4)
                self._frost_img = s
            self._frost_img.set_alpha(int(255 * self.frost))
            screen.blit(self._frost_img, (0, 0))
        p = self.play.player
        mb = self.max_breath()
        if p.breath < mb - 0.05:
            w = 160
            x, y = SCREEN_W // 2 - w // 2, SCREEN_H - 120
            k = max(0.0, p.breath / mb)
            pygame.draw.rect(screen, (10, 20, 40), (x - 2, y - 2, w + 4, 12), border_radius=6)
            col = (120, 200, 255) if k > 0.3 else (255, 110, 110)
            pygame.draw.rect(screen, col, (x, y, int(w * k), 8), border_radius=4)
            for i in range(int(k * 6) + 1):                  # little bubbles
                bx = x + w + 10 + (i % 3) * 7
                by = y + 4 - ((self.play.t * 30 + i * 9) % 30)
                pygame.draw.circle(screen, (200, 230, 255), (int(bx), int(by)), 2, 1)
