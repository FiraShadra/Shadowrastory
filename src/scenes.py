"""Title menu, start warning, pause screen and the endings."""
import math
import random

import pygame

from .settings import SCREEN_W, SCREEN_H, TEXT, TEXT_DIM
from .assets import font
from .hud import Dialog, wrap
from . import render, save, texts


def ui(key, **kw):
    s = texts.UI[key]
    return s.format(**kw) if kw else s


def center(screen, surf, y):
    screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))


class Title:
    def __init__(self, game):
        self.game = game
        self.t = 0.0
        self.sel = 0
        self.confirm = None
        self.show_help = False
        self.lost = save.soul_lost()
        logo = game.sprites.logo
        self.logo = pygame.transform.smoothscale(logo, (380, 380))
        if self.lost:
            self.logo = self.logo.copy()
            self.logo.fill((150, 40, 40), special_flags=pygame.BLEND_RGB_MULT)
        self.refresh()

    def refresh(self):
        self.has_save = save.has_save()
        self.options = ["new_game"]                 # keys into texts.UI – the labels follow the language
        if self.has_save:
            self.options.append("continue")
        self.options += ["controls", "settings", "credits", "quit"]

    def update(self, dt, ctl):
        self.t += dt
        if self.show_help:
            if ctl.hit("confirm") or ctl.hit("pause"):
                self.show_help = False
            return
        if self.confirm is not None:
            if ctl.hit("left") or ctl.hit("right") or ctl.hit("up") or ctl.hit("down"):
                self.confirm = 1 - self.confirm
            if ctl.hit("pause"):
                self.confirm = None
            elif ctl.hit("confirm"):
                if self.confirm == 0:
                    self.game.scene = Warning(self.game)
                self.confirm = None
            return
        if ctl.hit("up"):
            self.sel = (self.sel - 1) % len(self.options)
        if ctl.hit("down"):
            self.sel = (self.sel + 1) % len(self.options)
        if ctl.hit("confirm"):
            o = self.options[self.sel]
            if o == "new_game":
                if self.has_save:
                    self.confirm = 1
                else:
                    self.game.scene = Warning(self.game)
            elif o == "continue":
                self.game.continue_game()
            elif o == "controls":
                self.show_help = True
            elif o == "settings":
                self.game.scene = Settings(self.game, back=self)
            elif o == "credits":
                self.game.scene = Credits(self.game)
            else:
                self.game.running = False

    def draw(self, screen):
        top = (40, 6, 10) if self.lost else (16, 8, 24)
        for y in range(0, SCREEN_H, 8):
            k = y / SCREEN_H
            col = tuple(int(c * (1 - k) + 4 * k) for c in top)
            pygame.draw.rect(screen, col, (0, y, SCREEN_W, 8))
        rng = random.Random(1)
        for i in range(90):
            x, y = rng.randrange(SCREEN_W), rng.randrange(SCREEN_H)
            a = 0.5 + 0.5 * math.sin(self.t * 2 + i)
            c = (int(120 + 100 * a), 60, 60) if self.lost else (int(120 + 100 * a), int(110 + 80 * a), int(160 + 90 * a))
            screen.set_at((x, y), c)
        screen.blit(self.logo, (110, SCREEN_H // 2 - 190 + math.sin(self.t) * 6))
        size = 76
        while size > 40 and font(size, "title").size("Shadowra's Story")[0] > SCREEN_W - 590:
            size -= 4                                    # fit the title font beside the logo
        title = font(size, "title").render("Shadowra's Story", True, (200, 60, 70) if self.lost else (220, 190, 235))
        screen.blit(title, (560, 190 - title.get_height()))
        sub = font(20).render(texts.SUBTITLE, True, TEXT_DIM)
        screen.blit(sub, (566, 200))
        y = 280
        for i, o in enumerate(self.options):
            col = (255, 220, 240) if i == self.sel else TEXT_DIM
            s = font(30).render(("›  " if i == self.sel else "   ") + ui(o), True, col)
            screen.blit(s, (580, y))
            y += 46
        if self.lost:
            s = font(26, "title").render(texts.GREED_SLOT, True, (200, 50, 60))
            s.set_alpha(int(160 + 90 * math.sin(self.t * 1.5)))
            screen.blit(s, (580, y + 30))
        if self.confirm is not None:
            box = pygame.Rect(SCREEN_W // 2 - 260, SCREEN_H // 2 - 80, 520, 160)
            pygame.draw.rect(screen, (12, 6, 18), box)
            pygame.draw.rect(screen, (140, 80, 160), box, 2)
            center(screen, font(22).render(ui("overwrite"), True, TEXT), box.y + 30)
            for i, o in enumerate((ui("yes"), ui("no"))):
                col = (255, 220, 240) if i == self.confirm else TEXT_DIM
                s = font(26).render(o, True, col)
                screen.blit(s, (box.x + 150 + i * 180, box.y + 90))
        if self.show_help:
            draw_help(screen)


def draw_help(screen):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((5, 2, 10, 235))
    screen.blit(ov, (0, 0))
    center(screen, font(44, "title").render(ui("controls"), True, (220, 190, 235)), 70)
    y = 160
    for key, desc in texts.HELP:
        screen.blit(font(22).render(key, True, (230, 150, 170)), (300, y))
        screen.blit(font(22).render(desc, True, TEXT), (480, y))
        y += 36
    y += 16
    for l in texts.HELP_NOTES:
        center(screen, font(18).render(l, True, TEXT_DIM), y)
        y += 26


class Warning:
    def __init__(self, game):
        self.game = game
        self.t = 0.0

    def update(self, dt, ctl):
        self.t += dt
        if self.t > 1.0 and ctl.hit("confirm"):
            self.game.new_game()
        if ctl.hit("pause"):
            self.game.to_menu()

    def draw(self, screen):
        screen.fill((6, 2, 8))
        y = 150
        for i, line in enumerate(texts.START_WARNING):
            a = max(0.0, min(1.0, self.t * 1.5 - i * 0.12))
            red = texts.WARN_KEYWORD in line
            col = (230, 70, 80) if red else (TEXT_DIM if line.startswith("[") else TEXT)
            s = font(26 if red else 22).render(line, True, col)
            s.set_alpha(int(255 * a))
            center(screen, s, y)
            y += 36


class Pause:
    def __init__(self, game, play):
        self.game = game
        self.play = play
        self.sel = 0
        self.opts = ["resume", "controls", "settings", "main_menu"]
        self.help = False

    def update(self, dt, ctl):
        if self.help:
            if ctl.hit("confirm") or ctl.hit("pause"):
                self.help = False
            return
        if ctl.hit("pause"):
            self.game.scene = self.play
            return
        if ctl.hit("up"):
            self.sel = (self.sel - 1) % len(self.opts)
        if ctl.hit("down"):
            self.sel = (self.sel + 1) % len(self.opts)
        if ctl.hit("confirm"):
            o = self.opts[self.sel]
            if o == "resume":
                self.game.scene = self.play
            elif o == "controls":
                self.help = True
            elif o == "settings":
                self.game.scene = Settings(self.game, back=self)
            else:
                self.game.to_menu()

    def draw(self, screen):
        self.play.draw(screen)
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((5, 2, 10, 190))
        screen.blit(ov, (0, 0))
        center(screen, font(50, "title").render(ui("pause"), True, (220, 190, 235)), 170)
        center(screen, font(16).render(ui("pause_note"), True, TEXT_DIM), 236)
        m = self.play.morality
        p = self.play.player
        mastery = ui("mastery", pct=f"{p.mastery() * 100:.0f}")
        if p.stage == 2:
            mastery += ui("mastery_adult", bonus=f"{p.mana_bonus():.0f}", mult=f"{p.spell_mult():.2f}")
        else:
            mastery += ui("mastery_young")
        mastery += ui("adaptation", pct=f"{p.adaptation() * 100:.0f}")
        center(screen, font(16).render(mastery, True, (150, 140, 230)), 456)
        center(screen, font(20).render(ui("nature", title=m.title()), True, (200, 160, 220)), 480)
        y = 505
        subs = m.subpaths()
        if subs:
            center(screen, font(15).render(ui("ways") + "  ·  ".join(s.name for s in subs), True, TEXT_DIM), y)
            y += 20
        extra = m.moral_summary()                    # extra morals from data/morals.json, e.g. SAffection 2/3
        if m.affection() or extra:
            s = "   ·   ".join(x for x in (ui("affection_stats", a=f"{m.affection():.0f}") if m.affection() else "",
                                           extra) if x)
            center(screen, font(15).render(s, True, (225, 160, 210)), y)
            y += 20
        y += 1
        for e in m.effects():
            col = (170, 140, 230) if e.good else (200, 110, 120)
            center(screen, font(15).render(f"{e.name} – {e.desc}", True, col), y)
            y += 19
        for i, o in enumerate(self.opts):
            col = (255, 220, 240) if i == self.sel else TEXT_DIM
            center(screen, font(28).render(ui(o), True, col), 270 + i * 44)
        if self.help:
            draw_help(screen)


class Settings:
    """Settings screen (from the title menu or the pause menu): currently the language."""

    def __init__(self, game, back):
        self.game = game
        self.back = back                   # the scene to return to (Title or Pause)
        self.t = 0.0
        self.langs = list(texts.LANGUAGES)

    def update(self, dt, ctl):
        self.t += dt
        if ctl.hit("left") or ctl.hit("right"):
            i = self.langs.index(texts.LANG)
            i = (i + (1 if ctl.hit("right") else -1)) % len(self.langs)
            texts.set_language(self.langs[i])
            save.set_setting("language", texts.LANG)
        elif ctl.hit("pause") or ctl.hit("confirm") or ctl.hit("interact"):
            self.game.scene = self.back

    def draw(self, screen):
        if isinstance(self.back, Pause):
            self.back.play.draw(screen)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((5, 2, 10, 215))
            screen.blit(ov, (0, 0))
        else:
            screen.fill((12, 6, 20))
        center(screen, font(50, "title").render(ui("settings"), True, (220, 190, 235)), 170)
        y = 320
        label = font(26).render(ui("language"), True, TEXT)
        screen.blit(label, (SCREEN_W // 2 - 300, y))
        x = SCREEN_W // 2 - 20
        for code, name in texts.LANGUAGES.items():
            on = code == texts.LANG
            s = font(28).render(name, True, (255, 220, 240) if on else TEXT_DIM)
            if on:
                box = s.get_rect(topleft=(x, y - 2)).inflate(24, 12)
                pygame.draw.rect(screen, (60, 30, 80), box, border_radius=10)
                pygame.draw.rect(screen, (170, 110, 200), box, 2, border_radius=10)
            screen.blit(s, (x, y - 2))
            x += s.get_width() + 60
        center(screen, font(16).render(ui("settings_hint"), True, TEXT_DIM), 460)


class Credits:
    """Main-menu credits: Shadowra walks and flies through the night while the credits scroll –
    then her journey so far (from the save) and a tableau of how her story could end."""
    SPEED = 46.0                       # scroll speed (px / s)

    def __init__(self, game):
        from .player import Player
        from .morality import Morality
        from .world import SHADOW_STONES
        self.game = game
        self.t = 0.0
        self.scroll = 0.0
        self.data = save.load()
        self.lost = save.soul_lost()
        d = self.data or {}
        self.player = Player.from_dict(d["player"]) if d.get("player") else None
        self.morality = Morality(d.get("morality"))
        flags = set(d.get("world", {}).get("flags", []))
        hugs = d.get("world", {}).get("hugs", {})
        self.stage = self.player.stage if self.player else 0
        self.fate = "lost" if self.lost else ("start" if not self.player else self.morality.ending())
        grove = next((f[6:] for f in flags if f.startswith("grove_") and f != "grove_done"), None)
        # "another one": friends who love her join the endings that are not lonely
        together = self.fate in ("light", "redemption")
        self.with_elves = grove == "friends" and together
        self.with_owl = hugs.get("owl", 0) >= 3 and together
        # the scrolling lines: credits, then her journey from the save
        lines = list(texts.CREDITS_HEAD)
        lines.append(("head", texts.CREDITS_JOURNEY))
        if not self.player:
            lines.append(("text", texts.CREDITS_NO_SAVE))
        else:
            p = self.player
            lines.append(("text", texts.STAGE_NAMES[p.stage]))
            from . import abilities
            ab = [abilities.name(a) for a in abilities.shown(p.abilities)]
            if ab:
                lines.append(("text", ui("abilities") + ", ".join(ab)))
            lines.append(("text", ui("journey_stats", m=f"{p.mastery() * 100:.0f}", a=f"{p.adaptation() * 100:.0f}")))
            lines.append(("text", ui("her_nature", title=self.morality.title())))
            subs = self.morality.subpaths()
            if subs:
                lines.append(("text", ui("her_ways") + ", ".join(s.name for s in subs)))
            stones = sum(1 for s in SHADOW_STONES if f"{s}_awake" in flags)
            lines.append(("text", ui("stones", n=stones)))
            if grove:
                lines.append(("text", ui("grove", fate=texts.GROVE_FATES.get(grove, grove))))
            loved = sum(1 for n in hugs.values() if n >= 3)
            total = sum(hugs.values())
            if total:
                lines.append(("text", ui("hugs", total=total, loved=loved)))
            m = self.morality
            if m.affection():
                lines.append(("text", ui("affection_stats", a=f"{m.affection():.0f}")))
            if m.moral_summary():
                lines.append(("text", m.moral_summary()))
        lines += [("gap", ""), ("head", texts.CREDITS_FATE_INTRO), ("gap", ""), ("gap", ""), ("gap", "")]
        self.lines = lines
        self.text_h = sum(70 if k == "title" else 44 if k == "head" else 22 if k == "gap" else 34 for k, _ in lines)
        self.duration = (self.text_h + SCREEN_H) / self.SPEED
        self.tableau_t = None
        # ---- the replay of her real journey (recorded while playing, deaths left out) ----
        self.samples = save.load_journey() if self.data else []
        self.replay = len(self.samples) >= 30
        if self.replay:
            from .play import Play
            import copy
            self.world = Play(game, copy.deepcopy(self.data))
            self.world.creatures, self.world.boss, self.world.projectiles = [], None, []
            self.world.dialog.lines, self.world.dialog.choice = [], None
            real_seconds = len(self.samples) / Play.REC_HZ
            self.speed = max(1.5, real_seconds / 150.0)        # the whole journey in ~2.5 minutes at most
            self.ri = 0.0
            self.cam = [self.samples[0][0] - SCREEN_W / 2, self.samples[0][1] - SCREEN_H / 2]
            self.mix = dict(cave=1.0, lava=0.0, grove=0.0, day=0.0)
            self.caption = None
            self.next_event = 0
            replay_secs = len(self.samples) / (Play.REC_HZ * self.speed)
            self.band_speed = (self.text_h + 330) / max(10.0, replay_secs)
        # ---- the close-up at the very end: she comes to the camera and blinks at the player ----
        self.close = self.fate not in ("greed", "lost")          # (not when her soul is gone)
        finished = save.story_finished() or any(s[6] in ("@mafor", "Mafor besiegt") for s in self.samples)
        self.talk = self.close and not finished                  # story not finished yet → she asks why
        fierce = self.fate in ("madness", "obsession")
        her_x = SCREEN_W // 2 - (70 if self.fate in ("light", "redemption") else 0)
        from .closeup import CloseUp
        self.closeup = CloseUp(self.stage, self.morality.eye_color() if self.player else (220, 30, 40),
                               start=(her_x, SCREEN_H - 110),
                               text=texts.CREDITS_CLOSEUP_UNFINISHED if self.talk else None,
                               wink=not fierce, blush=not fierce, fierce=fierce)
        self.end_at = (self.CLOSE_AT + CloseUp.APPROACH + (10.0 if self.talk else 6.0)) if self.close else 14.0

    CLOSE_AT = 6.0                    # tableau seconds before she walks up to the camera

    # ---- flow -----------------------------------------------------------------
    def update(self, dt, ctl):
        speed = 4.0 if ctl.down("jump") else 1.0
        self.t += dt * speed
        if self.tableau_t is not None:
            self.tableau_t += dt
            if self.close:                        # prepares its frames early, then walks up at CLOSE_AT
                self.closeup.c = self.tableau_t - self.CLOSE_AT
                self.closeup.update(0.0)
        elif self.replay:
            from .play import Play
            self.ri += dt * Play.REC_HZ * self.speed * speed
            self.scroll += self.band_speed * dt * speed
            if self.ri >= len(self.samples) - 1:
                self.tableau_t = 0.0
        else:
            self.scroll += self.SPEED * dt * speed
            if self.scroll > self.text_h + SCREEN_H * 0.35:
                self.tableau_t = 0.0
        if ctl.hit("pause") or ctl.hit("confirm") and (self.tableau_t or 0) > 1.0 or \
                ctl.hit("interact") or (self.tableau_t or 0) > self.end_at:
            self.game.to_menu()

    # ---- drawing ----------------------------------------------------------------
    def _ground(self, screen, cam_x, y):
        tile = self.game.tile_art.rock[1][0] if self.fate not in ("light", "redemption") else \
            self.game.tile_art.grass[1][0]
        body = self.game.tile_art.rock[0][0] if tile is self.game.tile_art.rock[1][0] else self.game.tile_art.grass[0][0]
        off = int(cam_x) % 32
        for x in range(-off, SCREEN_W + 32, 32):
            screen.blit(tile, (x, y))
            for yy in range(y + 32, SCREEN_H, 32):
                screen.blit(body, (x, yy))

    def _shadowra_parade(self, screen, ground):
        """She walks through every growth stage she has reached – the adult takes off and flies."""
        stages = list(range(self.stage + 1))
        cycle = 12.0
        seg = int(self.t // cycle) % len(stages)
        st = stages[seg]
        u = (self.t % cycle) / cycle
        x = -120 + u * (SCREEN_W + 240)
        eye = self.morality.eye_color()
        obsidian = bool(self.player and "obsidian" in self.player.abilities)
        if st == 2 and u > 0.45:                                  # take off and fly
            h = min(1.0, (u - 0.45) / 0.15)
            y = ground - h * (150 + math.sin(self.t * 1.6) * 25)
            pose = "flap" if int(self.t * 2.2) % 2 == 0 else "glide"
            flap = (self.t * 2.2 % 1) * 0.35
            draw = lambda: render.draw_dragon(screen, x, y, 2, 1, pose, self.t, eye=eye, obsidian=obsidian, flap=flap)
        elif st == 1 and 0.55 < u < 0.7:                          # the young dragon jumps and glides a little
            k = (u - 0.55) / 0.15
            y = ground - math.sin(k * math.pi) * 70
            draw = lambda: render.draw_dragon(screen, x, y, 1, 1, "glide", self.t, eye=eye, obsidian=obsidian)
        else:
            y = ground
            draw = lambda: render.draw_dragon(screen, x, y, st, 1, "walk", self.t, eye=eye, obsidian=obsidian)
        if y >= ground - 1:
            render.ground_shadow(screen, x, ground, (28, 44, 62)[st] * 1.7)
        draw()

    def _tableau(self, screen, ground):
        """How her story could end: with Fira, alone – or with others who love her."""
        a = min(1.0, self.tableau_t / 1.5)
        cx = SCREEN_W // 2
        st = self.stage
        eye = self.morality.eye_color()
        fate = self.fate
        her = not (self.close and self.tableau_t >= self.CLOSE_AT)   # she has walked up to the camera
        if fate == "start":                                       # no save yet: the hatchling, all alone
            if her:
                render.ground_shadow(screen, cx, ground, 50)
                render.draw_dragon(screen, cx, ground, 0, 1, "idle", self.t)
        elif fate in ("greed", "lost"):
            render.draw_dragon(screen, cx, ground, st, 1, "dead", self.t, eye=(120, 30, 30))
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((60, 0, 10, 70))
            screen.blit(ov, (0, 0))
        elif fate in ("light", "redemption"):
            if her:
                render.ground_shadow(screen, cx - 70, ground, 100)
                render.draw_dragon(screen, cx - 70, ground, st, 1, "idle", self.t, eye=eye)
            fx = cx + (90 if fate == "light" else 230)            # redemption: Fira keeps a little distance
            render.ground_shadow(screen, fx, ground, 100)
            render.draw_dragon(screen, fx, ground, 2, -1, "idle", self.t + 1, eye=(255, 190, 60),
                               body=(150, 66, 40), horn=(70, 40, 30), scale_mult=0.9)
        else:
            if her:
                render.ground_shadow(screen, cx, ground, 100)
                render.draw_dragon(screen, cx, ground, st, 1, "exhausted" if fate == "madness" else "idle", self.t,
                                   eye=eye)
            if fate == "madness":                                  # whispering eyes in the dark
                for i in range(5):
                    ex = cx - 260 + i * 130 + math.sin(self.t + i) * 10
                    ey = ground - 160 - (i % 2) * 60
                    for dx in (-7, 7):
                        pygame.draw.circle(screen, (220, 40, 50), (int(ex + dx), int(ey)), 3)
            else:                                                  # obsession: a hoard of skulls and gold
                for i in range(9):
                    sx = cx - 110 + i * 27
                    pygame.draw.circle(screen, (214, 204, 186), (sx, ground - 7), 8)
                    pygame.draw.circle(screen, (30, 20, 20), (sx - 3, ground - 9), 2)
                    pygame.draw.circle(screen, (30, 20, 20), (sx + 3, ground - 9), 2)
                    pygame.draw.circle(screen, (240, 200, 80), (sx + 13, ground - 3), 4)
        if self.with_elves:                                        # "another one": the elves who love her
            for i, name in enumerate(("Sera", "Erila")):
                ex = 150 + i * 60
                render.ground_shadow(screen, ex, ground, 40)
                render.draw_elf(screen, ex, ground, 1, name, "idle", self.t + i)
        if self.with_owl:
            render.draw_owl(screen, SCREEN_W - 170, ground, self.t, False, 255)
        caption = texts.CREDITS_FATES[fate]
        extra = []
        if self.with_elves:
            extra.append(texts.CREDITS_ELVES)
        if self.with_owl:
            extra.append(texts.CREDITS_OWL)
        y = 120
        for i, line in enumerate([texts.CREDITS_FATE_INTRO, caption] + extra + ["", texts.CREDITS_END]):
            f = font(30) if i == 1 else font(20)        # (the title font has no dashes/umlaut-safe glyphs)
            s = f.render(line, True, (230, 210, 240) if i != 1 else ((220, 70, 80) if fate in ("greed", "lost") else (240, 214, 250)))
            s.set_alpha(int(255 * a))
            center(screen, s, y)
            y += 56 if i == 1 else 32


    # ---- replay of her journey ----------------------------------------------------
    def _replay_draw(self, screen):
        w = self.world
        lv = w.level
        n = len(self.samples)
        i = min(int(self.ri), n - 1)
        a, b = self.samples[i], self.samples[min(i + 1, n - 1)]
        f = self.ri - i
        if abs(a[0] - b[0]) < 160 and abs(a[1] - b[1]) < 160:     # smooth in-between frames
            x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        else:                                                     # burrow / big jump between saves
            x, y = a[0], a[1]
        stage, pose, facing, flap = a[2], a[3], a[4], a[5]
        while self.next_event <= i:                               # captions for milestones
            ev = self.samples[self.next_event][6]
            if ev:
                self.caption = [texts.replay_caption(ev), self.t]
            self.next_event += 1
        # camera and the light of each region, like in the game
        k = 0.12
        self.cam[0] += (x - SCREEN_W / 2 + facing * 80 - self.cam[0]) * k
        self.cam[1] += (y - SCREEN_H / 2 - 40 - self.cam[1]) * k
        self.cam[0] = max(0, min(lv.pw - SCREEN_W, self.cam[0]))
        self.cam[1] = max(0, min(lv.ph - SCREEN_H, self.cam[1]))
        cam = (int(self.cam[0]), int(self.cam[1]))
        targets = dict(cave=1.0 if lv.is_cave(x, y - 20) else 0.0,
                       lava=1.0 if lv.zone_key(x) == "lava" else 0.0,
                       grove=1.0 if lv.in_grove(x, y - 20) else 0.0,
                       day=1.0 if lv.day_zone(x) else 0.0)
        for key, v in targets.items():
            self.mix[key] += (v - self.mix[key]) * 0.08
        w.t = self.t
        w.backdrop.draw(screen, cam, self.mix["cave"], self.mix["lava"], self.t, self.mix["grove"], self.mix["day"])
        if self.mix["day"] > 0.01:
            render.draw_daylight(screen, lv, cam, self.t, w.sprites)
        render.draw_beams(screen, lv, cam, self.t)
        if self.mix["lava"] > 0.01:
            render.draw_lava_glow(screen, lv, cam, self.t)
        w.draw_decor(screen, cam, back=True)
        w.tile_art.draw(screen, lv, cam, self.t)
        w.draw_decor(screen, cam, back=False)
        w.draw_objects(screen, cam)
        if pose in ("idle", "walk", "run", "claw", "tail", "fire", "exhausted", "hug", "nuzzle"):
            render.ground_shadow(screen, x - cam[0], y - cam[1], (28, 44, 62)[stage] * 1.7)
        render.draw_dragon(screen, x - cam[0], y - cam[1], stage, facing, pose, self.t,
                           eye=self.morality.eye_color(),
                           obsidian=bool(self.player and "obsidian" in self.player.abilities), flap=flap)
        # region name + milestone caption at the bottom
        zone = font(18).render(lv.zone_name(x, y - 20), True, TEXT_DIM)
        screen.blit(zone, (24, SCREEN_H - 40))
        if self.caption and self.t - self.caption[1] < 3.5 / max(1.0, self.speed / 3):
            s = font(28, "title").render(self.caption[0].replace("–", "-"), True, (240, 214, 250))
            box = pygame.Surface((s.get_width() + 40, s.get_height() + 16), pygame.SRCALPHA)
            box.fill((10, 5, 16, 170))
            screen.blit(box, (SCREEN_W // 2 - box.get_width() // 2, SCREEN_H - 120))
            center(screen, s, SCREEN_H - 112)
        # the credits scroll in a dark band at the top
        if not hasattr(self, "_band"):
            self._band = pygame.Surface((SCREEN_W, 300), pygame.SRCALPHA)
            for yy in range(300):
                self._band.fill((8, 4, 14, int(170 * (1 - yy / 300) ** 1.4)), (0, yy, SCREEN_W, 1))
        screen.blit(self._band, (0, 0))
        y = 300 - self.scroll
        for kind, text in self.lines:
            h = 70 if kind == "title" else 44 if kind == "head" else 22 if kind == "gap" else 34
            if -70 < y < 300 and text:
                if kind == "title":
                    s = font(54, "title").render(text, True, (220, 190, 235))
                elif kind == "head":
                    s = font(24, "title").render(text, True, (200, 150, 220))
                elif kind == "sub":
                    s = font(18).render(text, True, TEXT_DIM)
                else:
                    s = font(20).render(text, True, TEXT)
                s.set_alpha(int(255 * max(0.0, min(1.0, (300 - y) / 60, (y + 40) / 60))))
                center(screen, s, y)
            y += h

    def draw(self, screen):
        if self.replay and self.tableau_t is None:
            self._replay_draw(screen)
            hint = font(14).render(texts.CREDITS_SKIP, True, TEXT_DIM)
            screen.blit(hint, (SCREEN_W - hint.get_width() - 16, SCREEN_H - 26))
            return
        cam = (self.t * 40, 700)
        self.game.backdrop.draw(screen, cam, 0.0, 0.0, self.t)
        ground = SCREEN_H - 110
        if self.tableau_t is None:
            y = ground - self.scroll + SCREEN_H - ground       # text rises from behind the horizon
            for kind, text in self.lines:
                h = 70 if kind == "title" else 44 if kind == "head" else 22 if kind == "gap" else 34
                if -80 < y < SCREEN_H and text:
                    if kind == "title":
                        s = font(60, "title").render(text, True, (220, 190, 235))
                    elif kind == "head":
                        s = font(26, "title").render(text, True, (200, 150, 220))
                    elif kind == "sub":
                        s = font(20).render(text, True, TEXT_DIM)
                    else:
                        s = font(22).render(text, True, TEXT)
                    center(screen, s, y)
                y += h
            self._ground(screen, cam[0] * 2, ground)
            self._shadowra_parade(screen, ground)
        else:
            self._ground(screen, cam[0] * 2, ground)
            self._tableau(screen, ground)
            if self.close and self.tableau_t >= self.CLOSE_AT:
                self.closeup.draw(screen, self.t)
        hint = font(14).render(texts.CREDITS_SKIP, True, TEXT_DIM)
        screen.blit(hint, (SCREEN_W - hint.get_width() - 16, SCREEN_H - 26))


class Ending:
    def __init__(self, game, key, morality):
        self.game = game
        self.key = key
        self.data = texts.ENDINGS[key]
        self.t = 0.0
        self.phase = "dialog"
        self.dialog = Dialog()
        self.dialog.show(self.data["lines"], on_done=self.after_dialog)
        self.morality = morality
        # greed collapse sequence
        self.sx = 300.0
        self.bars = 1.0
        self.collapse_t = 0.0
        if key == "greed":
            save.wipe_for_greed()      # it is final the moment the ending begins

    def after_dialog(self):
        if self.key == "greed":
            self.phase = "collapse"
        else:
            self.phase = "card"
        self.t = 0.0

    def update(self, dt, ctl):
        self.t += dt
        if self.phase == "dialog":
            self.dialog.update(dt, ctl)
        elif self.phase == "collapse":
            # Shadowra still answers to the player – barely. She can only drag herself forward.
            self.bars = max(0.0, self.bars - dt / 7.0)
            if ctl.down("right") and self.bars > 0.15:
                self.sx += 40 * dt
            if self.bars <= 0.15:
                self.collapse_t += dt
            if self.collapse_t > 3.0:
                self.phase = "dead"
                self.t = 0.0
        elif self.phase in ("card", "dead"):
            from .play import Play
            goes_on = self.phase == "card" and self.key in Play.FIRA_FATE
            if self.t > 2.0 and ctl.hit("confirm"):
                if goes_on:                                  # chapter 2: the snowlands
                    self.game.continue_game()
                else:
                    self.game.to_menu()
            elif self.t > 2.0 and goes_on and ctl.hit("pause"):
                self.game.to_menu()

    def draw(self, screen):
        greed = self.key == "greed"
        sky = (10, 4, 8) if greed else (14, 10, 30)
        screen.fill(sky)
        if self.phase in ("dialog", "collapse"):
            rng = random.Random(2)
            for _ in range(80):
                screen.set_at((rng.randrange(SCREEN_W), rng.randrange(SCREEN_H // 2)), (180, 170, 200))
            pygame.draw.rect(screen, (30, 18, 36), (0, 520, SCREEN_W, SCREEN_H - 520))
            if self.phase == "dialog":
                render.draw_dragon(screen, 520, 520, 2, 1, "idle", self.t, eye=self.morality.eye_color(),
                                   obsidian=True)
                fira_x = 820 + (min(1.0, self.t / 6) * 120 if greed else 0)
                render.draw_dragon(screen, fira_x, 520, 2, -1, "idle", self.t + 1, eye=(255, 190, 60),
                                   body=(150, 66, 40), horn=(70, 40, 30), scale_mult=0.9)
                self.dialog.draw(screen)
            else:
                pose = "exhausted" if self.collapse_t <= 0 else ("sleep" if self.collapse_t < 1.5 else "dead")
                render.draw_dragon(screen, self.sx, 520, 2, 1, pose, self.t, eye=(120, 30, 30), obsidian=True)
                from .hud import bar
                from .settings import HP_COL, MANA_COL, STAM_COL
                bar(screen, 24, 22, 220, 14, self.bars, HP_COL)
                bar(screen, 24, 44, 180, 10, self.bars * 0.5, MANA_COL)
                bar(screen, 24, 60, 180, 10, self.bars * 0.3, STAM_COL)
                if self.t < 5:
                    s = font(16).render("→  ...", True, TEXT_DIM)
                    screen.blit(s, (self.sx + 60, 470))
                ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                ov.fill((0, 0, 0, int(min(255, self.collapse_t * 85))))
                screen.blit(ov, (0, 0))
        elif self.phase == "card":
            a = min(1.0, self.t / 1.5)
            s = font(64, "title").render(self.data["title"], True, (220, 190, 235))
            s.set_alpha(int(255 * a))
            center(screen, s, 260)
            f = font(22).render(self.data["footer"], True, TEXT)
            f.set_alpha(int(255 * a))
            center(screen, f, 360)
            if self.t > 2:
                from .play import Play
                if self.key in Play.FIRA_FATE:
                    s = font(22).render(ui("story_goes_on"), True, (220, 200, 240))
                    s.set_alpha(int(255 * min(1.0, (self.t - 2) / 1.0)))
                    center(screen, s, 440)
                    center(screen, font(16).render(ui("continue_or_menu"), True, TEXT_DIM), 620)
                else:
                    center(screen, font(16).render(ui("enter_menu"), True, TEXT_DIM), 620)
        elif self.phase == "dead":
            screen.fill((0, 0, 0))
            a = min(1.0, self.t / 2.0)
            s = font(48, "title").render(texts.GREED_DEATH, True, (200, 40, 50))
            s.set_alpha(int(255 * a))
            center(screen, s, 300)
            if self.t > 2:
                t2 = font(18).render(ui("save_deleted"), True, TEXT_DIM)
                center(screen, t2, 380)
                center(screen, font(16).render("[Enter]", True, TEXT_DIM), 620)
