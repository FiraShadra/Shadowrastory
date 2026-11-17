"""Shadowra walks up to the camera and talks to the player directly (fourth-wall moments).

Used by the credits (she blinks and winks at the player, and asks why they stop if the story is
unfinished) and in the game (she refuses when SAffection would go past the FSK 12 limit).
The large, smooth portrait comes from models.build_portrait; its frames are cached per eyelid/mouth state.
"""
import math

import pygame

from .settings import SCREEN_W, SCREEN_H
from .assets import font
from .hud import wrap
from . import models, render


class CloseUp:
    APPROACH = 2.6                    # seconds the walk-up takes
    PORTRAIT_PX = 600
    LIDS = (0.0, 0.34, 0.67, 1.0)
    TALK_AT = 1.6                     # seconds after arriving when she starts to speak
    CHARS_PER_S = 32
    PREWARM = ((0, 0, 0), (0.34, 0.34, 0), (0.67, 0.67, 0), (1, 1, 0), (0, 0.34, 0), (0, 0.67, 0), (0, 1, 0),
               (0, 0, 0.6))

    def __init__(self, stage, eye, start=(SCREEN_W / 2, SCREEN_H - 110), text=None, wink=True,
                 blush=True, fierce=False, hint=None):
        self.stage, self.eye = stage, eye
        self.hint = hint                   # shown under the bubble once she has finished talking
        self.start = start                 # where she stands on screen before walking up (her feet)
        self.text = text                   # what she says to the player (None = she only blinks)
        self.wink, self.blush, self.fierce = wink, blush, fierce
        self.c = 0.0                       # seconds since she started walking up
        self.portraits = {}
        self._vignette = None

    # ---- timing ------------------------------------------------------------------
    @property
    def hold(self):
        """Seconds since she arrived in front of the camera."""
        return max(0.0, self.c - self.APPROACH)

    def typed(self):
        return int(max(0.0, self.hold - self.TALK_AT) * self.CHARS_PER_S)

    def text_done(self):
        return self.text is None or self.typed() >= len(self.text)

    def skip_typing(self):
        """Show the whole sentence at once (first key press while she talks)."""
        if self.text and not self.text_done():
            self.c = self.APPROACH + self.TALK_AT + len(self.text) / self.CHARS_PER_S

    def update(self, dt):
        self.c += dt
        for key in self.PREWARM:                   # build one frame per update – no hitches later
            if key not in self.portraits:
                self.portrait(key)
                break

    # ---- portrait frames ------------------------------------------------------------
    def portrait(self, key):
        if key not in self.portraits:
            self.portraits[key] = models.build_portrait(self.PORTRAIT_PX, self.stage, self.eye, *key,
                                                        blush=self.blush, fierce=self.fierce)
        return self.portraits[key]

    def state(self):
        """Eyelids (left, right) and mouth for the current moment."""
        h = self.hold

        def tri(x, a, b):                          # 0 → 1 → 0 over [a, b]
            if not a <= x <= b:
                return 0.0
            return 1.0 - abs((x - a) / (b - a) * 2 - 1)
        both = tri(h, 0.9, 1.25)                   # a slow first blink …
        wink = 0.0
        if self.wink:                              # … then a wink at the player
            wink = min(1.0, max(0.0, (h - 2.4) / 0.15)) * (1.0 if h < 3.2 else max(0.0, 1 - (h - 3.2) / 0.15))
        if h > 5.0:
            both = max(both, tri((h - 5.0) % 3.6, 0.0, 0.3))
        q = lambda v: min(self.LIDS, key=lambda L: abs(L - v))
        mouth = 0.0
        if self.text and not self.text_done() and h > self.TALK_AT and int(h * 9) % 2:
            mouth = 0.6
        lid_l, lid_r = q(both), q(max(both, wink))
        if mouth and (lid_l or lid_r):
            mouth = 0.0
        return (lid_l, lid_r, mouth)

    # ---- drawing ------------------------------------------------------------------
    def _vignette_surface(self):
        if self._vignette is None:
            v = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            v.fill((6, 2, 12, 200))
            for i in range(1, 25):                 # dark edges, clear centre (inner overwrites outer)
                r = 1.25 - i / 24 * 0.85
                pygame.draw.ellipse(v, (6, 2, 12, int(200 * (1 - i / 24) ** 1.6)),
                                    pygame.Rect(0, 0, SCREEN_W * r, SCREEN_H * r * 1.2).move(
                                        SCREEN_W * (1 - r) / 2, SCREEN_H * (1 - r * 1.2) / 2 + 40))
            self._vignette = v
        return self._vignette

    def draw(self, screen, t):
        """She walks up to the camera, grows huge and smooth in front of the player and blinks at them."""
        u = min(1.0, self.c / self.APPROACH)
        e = u * u * (3 - 2 * u)                    # smoothstep
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((8, 3, 14, int(150 * e)))
        screen.blit(dim, (0, 0))
        vig = self._vignette_surface()
        vig.set_alpha(int(255 * e))
        screen.blit(vig, (0, 0))
        img = self.portrait(self.state() if u >= 1.0 else (0, 0, 0))
        # walking closer: small where she stands → large in front of the camera, with a soft step bob
        sx, sy = self.start
        scale = 0.16 + 0.84 * e
        step = abs(math.sin(self.c * 5.0)) * 10 * (1 - e) * scale if u < 1.0 else 0.0
        breathe = math.sin(t * 1.6) * 4 * e
        bx = sx + (SCREEN_W / 2 - sx) * e
        by = (sy + 6) + (SCREEN_H + 30 - (sy + 6)) * e - step + breathe
        if scale < 0.999:
            img = pygame.transform.smoothscale(img, (max(1, int(img.get_width() * scale)),
                                                     max(1, int(img.get_height() * scale))))
        if e < 0.9:
            render.ground_shadow(screen, bx, by - 4, img.get_width() * 0.7)
        screen.blit(img, (bx - img.get_width() / 2, by - img.get_height()))
        if self.text and self.hold > self.TALK_AT:
            self.draw_bubble(screen)

    def draw_bubble(self, screen):
        f = font(24)
        lines = wrap(self.text, f, 360)
        bw = 400
        bh = 28 + len(lines) * 32 + (18 if self.hint else 0)
        bx0, by0 = SCREEN_W - bw - 50, 90
        bubble = pygame.Surface((bw, bh + 30), pygame.SRCALPHA)
        pygame.draw.rect(bubble, (246, 236, 250, 238), (0, 0, bw, bh), border_radius=22)
        pygame.draw.rect(bubble, (120, 80, 150, 255), (0, 0, bw, bh), 3, border_radius=22)
        pygame.draw.polygon(bubble, (246, 236, 250, 238), [(40, bh - 3), (80, bh - 3), (20, bh + 28)])
        pygame.draw.lines(bubble, (120, 80, 150, 255), False, [(40, bh - 2), (20, bh + 28), (80, bh - 2)], 3)
        screen.blit(bubble, (bx0, by0))
        left = self.typed()
        y = by0 + 14
        for line in lines:                         # typewriter, keeps the final wrapping
            part = line[:max(0, left)]
            left -= len(line) + 1
            if part:
                screen.blit(f.render(part, True, (50, 26, 66)), (bx0 + 20, y))
            y += 32
        if self.hint and self.text_done():
            s = font(14).render(self.hint, True, (120, 90, 140))
            screen.blit(s, (bx0 + bw - s.get_width() - 18, by0 + bh - 22))
