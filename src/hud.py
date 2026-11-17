"""HUD (three bars, kept deliberately small), toasts and the dialog box."""
import pygame

from .settings import SCREEN_W, SCREEN_H, HP_COL, MANA_COL, STAM_COL, TEXT, TEXT_DIM
from .assets import font
from . import texts


def wrap(text, f, width):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.size(test)[0] > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def bar(screen, x, y, w, h, frac, col, cap_frac=1.0, flash=False):
    pygame.draw.rect(screen, (12, 6, 16), (x - 2, y - 2, w + 4, h + 4), border_radius=4)
    if cap_frac < 1.0:      # shrunk maximum (hunger / debuff) shown as a dark cap
        pygame.draw.rect(screen, (50, 30, 40), (x + int(w * cap_frac), y, w - int(w * cap_frac), h))
    fw = int(w * max(0.0, min(1.0, frac)) * cap_frac)
    c = tuple(min(255, v + 60) for v in col) if flash else col
    if fw > 0:
        pygame.draw.rect(screen, c, (x, y, fw, h), border_radius=3)
        pygame.draw.rect(screen, tuple(min(255, v + 50) for v in col), (x, y, fw, 3), border_radius=3)


class Hud:
    def __init__(self):
        self.toasts = []          # [text, time_left]
        self.toast_keys = {}
        self.zone_banner = None   # [text, time]

    def toast(self, text, dur=2.6, key=None):
        if key:
            if self.toast_keys.get(key, 0) > 0:
                return
            self.toast_keys[key] = dur + 0.4      # don't stack the same message
        self.toasts.append([text, dur])
        self.toasts = self.toasts[-4:]

    def banner(self, text):
        self.zone_banner = [text, 3.0]

    def update(self, dt):
        for t in self.toasts:
            t[1] -= dt
        self.toasts = [t for t in self.toasts if t[1] > 0]
        for k in list(self.toast_keys):
            self.toast_keys[k] -= dt
        if self.zone_banner:
            self.zone_banner[1] -= dt
            if self.zone_banner[1] <= 0:
                self.zone_banner = None

    def draw(self, screen, player, morality, t):
        f = font(16)
        x, y = 24, 22
        mods = morality.mods()
        bar(screen, x, y, 220, 14, player.hp / player.max_hp(), HP_COL, flash=player.hurt_flash > 0)
        bar(screen, x, y + 22, 180, 10, player.mana / player.max_mana(), MANA_COL)
        cap = player.max_stam(mods) / player.s["max_stam"]
        st_frac = player.stamina / max(1.0, player.max_stam(mods))
        exhausted = player.exhausted > 0 and int(t * 6) % 2 == 0
        bar(screen, x, y + 38, 180, 10, st_frac, (150, 90, 60) if exhausted else STAM_COL, cap_frac=cap)
        screen.blit(f.render(texts.STAGE_NAMES[player.stage], True, TEXT_DIM), (x, y + 54))
        sym = [("Hunger", False)] if player.hungry() else []
        sym += [(e.name, e.good) for e in morality.effects()]
        sx = x
        for name, good in sym:          # dark gifts in violet, burdens in red
            s = font(14).render(name, True, (170, 140, 230) if good else (200, 110, 120))
            screen.blit(s, (sx, y + 74))
            sx += s.get_width() + 14
        # toasts
        ty = SCREEN_H - 190
        for text, left in reversed(self.toasts):
            s = f.render(text, True, TEXT)
            s.set_alpha(int(255 * min(1.0, left * 2)))
            screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, ty))
            ty -= 24
        if self.zone_banner:
            text, left = self.zone_banner
            s = font(40, "title").render(text, True, (230, 210, 240))
            s.set_alpha(int(255 * min(1.0, left, 3.0 - left + 0.01)))
            screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, 90))


class Dialog:
    """Queue of (speaker, text) lines; optional choice at the end."""

    def __init__(self):
        self.lines = []
        self.choice = None        # (options, callback)
        self.sel = 0
        self.on_done = None
        self.reveal = 0.0

    @property
    def active(self):
        return bool(self.lines) or self.choice is not None

    def show(self, lines, on_done=None, choice=None):
        self.lines = list(lines)
        self.on_done = on_done
        self.choice = choice
        self.sel = 0
        self.reveal = 0.0

    def update(self, dt, ctl):
        if not self.active:
            return
        self.reveal += dt * 70
        if self.lines:
            if ctl.hit("confirm") or ctl.hit("interact"):
                full = len(self.lines[0][1])
                if self.reveal < full:
                    self.reveal = full
                else:
                    self.lines.pop(0)
                    self.reveal = 0.0
                    if not self.lines and self.choice is None:
                        cb, self.on_done = self.on_done, None
                        if cb:
                            cb()
            return
        opts, cb = self.choice
        if ctl.hit("up") or ctl.hit("left"):
            self.sel = (self.sel - 1) % len(opts)
        if ctl.hit("down") or ctl.hit("right"):
            self.sel = (self.sel + 1) % len(opts)
        if ctl.hit("confirm"):
            self.choice = None
            cb(self.sel)

    def draw(self, screen):
        if not self.active:
            return
        box = pygame.Rect(140, SCREEN_H - 170, SCREEN_W - 280, 140)
        s = pygame.Surface(box.size, pygame.SRCALPHA)
        s.fill((10, 5, 16, 225))
        screen.blit(s, box.topleft)
        pygame.draw.rect(screen, (110, 70, 140), box, 2, border_radius=6)
        f = font(20)
        if self.lines:
            who, text = self.lines[0]
            y = box.y + 16
            if who:
                screen.blit(font(18).render(who, True, (230, 150, 170)), (box.x + 22, y))
                y += 26
            shown = text[: int(self.reveal)]
            for line in wrap(shown, f, box.w - 44):
                screen.blit(f.render(line, True, TEXT), (box.x + 22, y))
                y += 26
            if self.reveal >= len(text):
                screen.blit(font(14).render("[E / Enter]", True, TEXT_DIM), (box.right - 110, box.bottom - 24))
        else:
            opts, _ = self.choice
            y = box.y + 22
            for i, o in enumerate(opts):
                col = (255, 220, 240) if i == self.sel else TEXT_DIM
                prefix = "›  " if i == self.sel else "   "
                screen.blit(f.render(prefix + o, True, col), (box.x + 30, y))
                y += 30
