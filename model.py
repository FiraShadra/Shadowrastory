#this here is for the dragon design editor, which is a separate program from the game itself. It is not used by the game, but it is used to create and edit dragon designs. The game loads the design from a JSON file, and this code provides functions to load, save, and normalize the design data.

"""Shadowra Modeler – shape, colour and build Shadowra's design, then save / export it.

Run:  python model.py                    (or: python main.py --editor)
      python model.py some.json          (open another design file)

This file is the whole editor; the design format (load / save / normalize) is in src/dragon_design.py.

Left: tabs Shape · Colours · Parts · Extras. Right: live preview (all stages and poses, side view or close-up
portrait, a test light that follows the mouse so you can watch her scales shine).

Save    writes data/shadowra_design.json – the game draws Shadowra with it from the next start.
Export  saves too and writes exports/<name>_<date>/: design.json, a PNG of every pose for every stage,
        a sprite sheet and the close-up portraits.

Keys: Ctrl+Z undo · Ctrl+Y redo · Ctrl+S save · Ctrl+E export · Space animate · F flip · Delete removes the
selected extra part · arrow keys nudge it (Shift = faster) · mouse wheel over the preview zooms.
"""
import copy
import json
import math
import os
import sys
import time

import pygame

from src import dragon_design as dd
from src import lights, models, render
from src.settings import ROOT, GAME_DIR

W, H = 1280, 720
PANEL_W = 390
TOP_H = 44
BAR_H = 44

BG = (24, 18, 30)
PANEL = (36, 28, 44)
PANEL_2 = (48, 38, 58)
LINE = (70, 58, 84)
TEXT = (232, 224, 240)
DIM = (150, 138, 166)
ACCENT = (178, 120, 230)
ACCENT_2 = (120, 80, 170)
WARN = (240, 170, 90)

STAGES = (("Hatchling", 0), ("Young", 1), ("Adult", 2))
POSES = ("idle", "walk", "run", "jump", "glide", "flap", "dive", "fire", "claw", "tail", "eat", "nuzzle", "hug",
         "exhausted", "sleep", "curl_eat", "dead")
EXPORT_POSES = ("idle", "walk", "run", "jump", "glide", "flap", "dive", "fire", "claw", "tail", "eat", "sleep",
                "exhausted", "curl_eat")

SHAPE_SLIDERS = (                              # (label, key, min, max) – grouped with headers
    ("Whole body", None, 0, 0),
    ("Overall size", "overall", 0.5, 1.6),
    ("Body length", "body_length", 0.7, 1.45),
    ("Body height", "body_height", 0.7, 1.45),
    ("Chest", "chest", 0.7, 1.5),
    ("Head", None, 0, 0),
    ("Head size", "head", 0.6, 1.6),
    ("Snout length", "snout", 0.6, 1.5),
    ("Eye size", "eye", 0.6, 1.8),
    ("Neck length", "neck_length", 0.6, 1.6),
    ("Neck thickness", "neck_thickness", 0.6, 1.6),
    ("Horns", None, 0, 0),
    ("Horn length", "horn_length", 0.2, 2.4),
    ("Horn thickness", "horn_thickness", 0.4, 2.0),
    ("Horn angle", "horn_angle", -70, 70),
    ("Horn curve", "horn_curve", -1.0, 2.5),
    ("Limbs & tail", None, 0, 0),
    ("Leg length", "leg_length", 0.7, 1.5),
    ("Leg thickness", "leg_thickness", 0.6, 1.6),
    ("Tail length", "tail_length", 0.5, 1.8),
    ("Tail thickness", "tail_thickness", 0.6, 1.6),
    ("Wing size", "wing", 0.5, 1.6),
    ("Details", None, 0, 0),
    ("Spike size", "spikes", 0.0, 2.5),
    ("Ear frill length", "frills", 0.3, 2.0),
    ("Scale size", "scales", 0.5, 2.5),
    ("Scale shine", "shine", 0.0, 2.5),
)

PART_LABELS = (
    ("horns", "Horns"), ("far_horn", "Far horn (behind the head)"), ("horn_rings", "Horn growth rings"),
    ("ear_frills", "Ear frills"), ("crest_spike", "Forehead crest spike"), ("brow", "Brow ridge"),
    ("fangs", "Fangs"), ("smile", "Smile line"), ("neck_spines", "Neck spines"),
    ("back_spikes", "Back spikes"), ("tail_spines", "Tail spines"), ("tail_spade", "Tail spade"),
    ("throat_plates", "Throat plates"), ("belly_plates", "Belly plates"), ("toes", "Toes & claws"),
    ("muscles", "Muscle lines"), ("wings", "Wings"), ("scales", "Scale texture"), ("sheen", "Scales shine in light"),
)
COUNT_LABELS = (("back_spikes", "Back spikes", 0, 14), ("neck_spines", "Neck spines", 0, 8),
                ("tail_spines", "Tail spines", 0, 12), ("ear_frills", "Ear frills", 0, 6), ("toes", "Toes", 1, 5))

COLOR_LABELS = (("body", "Body"), ("belly", "Belly & plates"), ("spikes", "Spikes & frills"), ("wing", "Wings"),
                ("horn", "Horns"), ("claw", "Claws"), ("outline", "Outline"))
PALETTE = ((86, 56, 88), (64, 40, 82), (40, 30, 48), (24, 18, 30), (120, 70, 130), (150, 66, 40),
           (60, 80, 120), (40, 90, 80), (140, 40, 60), (200, 190, 210), (228, 208, 170), (226, 214, 190),
           (240, 200, 90), (150, 90, 255), (90, 200, 220), (220, 60, 60))
EYE_COLORS = ((220, 30, 40), (255, 190, 60), (150, 90, 255), (60, 200, 140), (90, 150, 255))
LIGHTS = (("Torch", (255, 230, 150)), ("Lava", (255, 110, 40)), ("Magic", (150, 110, 255)), ("Moon", (170, 200, 255)))
BACKDROPS = ("Cave", "Dusk", "Day", "Grey")


def _fit(v, lo, hi):
    return max(lo, min(hi, v))


class UI:
    """A tiny immediate-mode GUI: widgets are drawn and checked for clicks in the same call."""

    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.small = pygame.font.Font(None, 18)
        self.big = pygame.font.Font(None, 30)
        self.mouse = (0, 0)
        self.pressed = None          # where the mouse went down this frame
        self.held = False
        self.released = False
        self.active = None           # id of the slider being dragged
        self.clip = None             # widgets only react inside this rect (scrolling panel)
        self.on_change = None        # called once before a widget changes the design (undo checkpoint)

    def begin(self, events):
        self.pressed, self.released = None, False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.pressed, self.held = e.pos, True
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.held, self.released = False, True
        self.mouse = pygame.mouse.get_pos()
        if not self.held:
            self.active = None

    def _inside(self, rect, pos):
        return pos is not None and rect.collidepoint(pos) and (self.clip is None or self.clip.collidepoint(pos))

    def hit(self, rect):
        return self._inside(rect, self.pressed)

    def text(self, surf, txt, pos, col=TEXT, font=None, center=False):
        img = (font or self.font).render(str(txt), True, col)
        r = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        surf.blit(img, r)
        return r

    def button(self, surf, rect, label, on=False, enabled=True, col=None):
        rect = pygame.Rect(rect)
        hover = self._inside(rect, self.mouse) and enabled
        base = col or (ACCENT_2 if on else PANEL_2)
        pygame.draw.rect(surf, tuple(min(255, c + 22) for c in base) if hover else base, rect, border_radius=5)
        pygame.draw.rect(surf, ACCENT if on else LINE, rect, 1, border_radius=5)
        self.text(surf, label, rect.center, TEXT if enabled else DIM, self.small if rect.h < 24 else self.font, True)
        return enabled and self.hit(rect)

    def checkbox(self, surf, rect, label, value):
        rect = pygame.Rect(rect)
        box = pygame.Rect(rect.x, rect.y + (rect.h - 18) // 2, 18, 18)
        pygame.draw.rect(surf, PANEL_2, box, border_radius=3)
        pygame.draw.rect(surf, ACCENT if value else LINE, box, 1, border_radius=3)
        if value:
            pygame.draw.lines(surf, ACCENT, False, [(box.x + 4, box.y + 9), (box.x + 8, box.y + 13),
                                                   (box.x + 14, box.y + 4)], 3)
        self.text(surf, label, (box.right + 8, rect.y + (rect.h - 15) // 2), TEXT if value else DIM)
        if self.hit(rect):
            self.changing()
            return not value
        return value

    def changing(self):
        if self.on_change:
            self.on_change()

    def slider(self, surf, wid, rect, label, value, lo, hi, step=None, fmt="{:.2f}"):
        rect = pygame.Rect(rect)
        self.text(surf, label, (rect.x, rect.y), DIM, self.small)
        self.text(surf, fmt.format(value), (rect.right - 44, rect.y), TEXT, self.small)
        track = pygame.Rect(rect.x, rect.y + 17, rect.w, 8)
        grab = pygame.Rect(track.x - 4, track.y - 6, track.w + 8, track.h + 12)
        if self.hit(grab):
            self.active = wid
            self.changing()
        if self.active == wid and self.held:
            u = _fit((self.mouse[0] - track.x) / max(1, track.w), 0, 1)
            value = lo + (hi - lo) * u
            if step:
                value = round(value / step) * step
        pygame.draw.rect(surf, PANEL_2, track, border_radius=4)
        u = _fit((value - lo) / ((hi - lo) or 1), 0, 1)
        if lo < 0 < hi:                                     # bipolar: fill from zero
            z = track.x + track.w * (-lo / (hi - lo))
            x = track.x + track.w * u
            pygame.draw.rect(surf, ACCENT_2, (min(z, x), track.y, abs(x - z), track.h), border_radius=4)
        else:
            pygame.draw.rect(surf, ACCENT_2, (track.x, track.y, track.w * u, track.h), border_radius=4)
        pygame.draw.circle(surf, ACCENT if self.active == wid else TEXT, (int(track.x + track.w * u), track.centery), 7)
        return value

    def stepper(self, surf, rect, label, value, lo, hi):
        rect = pygame.Rect(rect)
        self.text(surf, label, (rect.x, rect.y + 5), TEXT)
        minus = pygame.Rect(rect.right - 92, rect.y, 28, 24)
        plus = pygame.Rect(rect.right - 28, rect.y, 28, 24)
        self.text(surf, value, (rect.right - 46, rect.y + 12), TEXT, center=True)
        if self.button(surf, minus, "-") and value > lo:
            self.changing()
            return value - 1
        if self.button(surf, plus, "+") and value < hi:
            self.changing()
            return value + 1
        return value


class Editor:
    def __init__(self, path=None):
        pygame.init()
        pygame.display.set_caption("Shadowra Modeler")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.ui = UI()
        self.ui.on_change = self.checkpoint
        self.path = path or dd.DESIGN_FILE
        self.design = dd.load(path) if path else dd.load()
        self.saved = json.dumps(self.design, sort_keys=True)
        self.undo, self.redo = [], []
        self.tab = "Shape"
        self.scroll = {"Shape": 0, "Colours": 0, "Parts": 0, "Extras": 0}
        self.content_h = 0
        self.color_key = "body"
        self.selected = None                  # index of the selected extra part
        self.stage, self.pose, self.facing = 2, "idle", 1
        self.animate, self.t = False, 0.3
        self.view = "side"
        self.zoom = 2.0
        self.light_on, self.light_kind, self.light_pos = True, 0, None
        self.backdrop = 0
        self.eye = 0
        self.drag = None                      # dragging an extra part in the preview
        self.msg, self.msg_t = "", 0.0
        self.quit_armed = False
        self.portrait_cache = {}
        self.running = True

    # ---- design bookkeeping ------------------------------------------------
    def checkpoint(self):
        snap = copy.deepcopy(self.design)
        if not self.undo or self.undo[-1] != snap:
            self.undo.append(snap)
            del self.undo[:-200]
            self.redo.clear()

    def do_undo(self):
        if self.undo:
            self.redo.append(copy.deepcopy(self.design))
            self.design = self.undo.pop()
            self._fix_selection()
            self.say("Undo")

    def do_redo(self):
        if self.redo:
            self.undo.append(copy.deepcopy(self.design))
            self.design = self.redo.pop()
            self._fix_selection()
            self.say("Redo")

    def _fix_selection(self):
        if self.selected is not None and self.selected >= len(self.design["custom"]):
            self.selected = None

    @property
    def dirty(self):
        return json.dumps(self.design, sort_keys=True) != self.saved

    def say(self, msg):
        self.msg, self.msg_t = msg, 4.0

    def save(self):
        path = dd.save(self.design, self.path)
        self.saved = json.dumps(self.design, sort_keys=True)
        dd.set_current(self.design)
        self.say("Saved to " + os.path.relpath(path, ROOT))
        return path

    def export(self):
        self.save()
        name = "".join(c for c in self.design.get("name", "Shadowra") if c.isalnum() or c in "-_") or "Shadowra"
        base = os.path.join(GAME_DIR if os.access(GAME_DIR, os.W_OK) else ROOT, "exports")
        out = os.path.join(base, "%s_%s" % (name, time.strftime("%Y%m%d_%H%M%S")))
        os.makedirs(out, exist_ok=True)
        dd.save(self.design, os.path.join(out, "design.json"))
        lights.new_frame()
        lights.new_frame()                   # exports are drawn without test lights
        eye = EYE_COLORS[self.eye]
        cells = []
        for label, st in STAGES:
            for pose in EXPORT_POSES:
                img = self._render_alone(st, pose, eye)
                pygame.image.save(img, os.path.join(out, "%s_%s.png" % (label.lower(), pose)))
                cells.append(img)
            p = models.build_portrait(600, st, eye, design=self.design)
            pygame.image.save(p, os.path.join(out, "portrait_%s.png" % label.lower()))
        cw = max(c.get_width() for c in cells) + 8
        ch = max(c.get_height() for c in cells) + 8
        cols = len(EXPORT_POSES)
        sheet = pygame.Surface((cw * cols, ch * len(STAGES)), pygame.SRCALPHA)
        for i, c in enumerate(cells):
            x, y = (i % cols) * cw, (i // cols) * ch
            sheet.blit(c, (x + (cw - c.get_width()) // 2, y + ch - 4 - c.get_height()))
        pygame.image.save(sheet, os.path.join(out, "sprite_sheet.png"))
        with open(os.path.join(out, "README.txt"), "w", encoding="utf-8") as f:
            f.write("Shadowra model export\n\n"
                    "design.json        the design (copy it to data/shadowra_design.json to use it in the game;\n"
                    "                   Save in the modeler already did that)\n"
                    "<stage>_<pose>.png every pose, facing right, transparent background\n"
                    "sprite_sheet.png   all of them: one row per stage (%s), columns: %s\n"
                    "portrait_*.png     the close-up portraits\n"
                    % (", ".join(s for s, _ in STAGES), ", ".join(EXPORT_POSES)))
        self.say("Exported to " + os.path.relpath(out, ROOT))
        return out

    def _render_alone(self, stage, pose, eye):
        s = pygame.Surface((900, 720), pygame.SRCALPHA)
        models.draw_dragon(s, 450, 700, stage, 1, pose, 0.3, eye=eye, design=self.design)
        r = s.get_bounding_rect(min_alpha=1)
        return s.subsurface(r).copy() if r.w and r.h else s

    # ---- main loop -----------------------------------------------------------
    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            events = pygame.event.get()
            self.ui.begin(events)
            for e in events:
                self.handle(e)
            if self.animate:
                self.t += dt
            self.msg_t = max(0.0, self.msg_t - dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle(self, e):
        if e.type == pygame.QUIT:
            self.request_quit()
        elif e.type == pygame.KEYDOWN:
            ctrl = e.mod & pygame.KMOD_CTRL
            shift = e.mod & pygame.KMOD_SHIFT
            if ctrl and e.key == pygame.K_z:
                self.do_redo() if shift else self.do_undo()
            elif ctrl and e.key == pygame.K_y:
                self.do_redo()
            elif ctrl and e.key == pygame.K_s:
                self.save()
            elif ctrl and e.key == pygame.K_e:
                self.export()
            elif e.key == pygame.K_ESCAPE:
                self.request_quit()
            elif e.key == pygame.K_SPACE:
                self.animate = not self.animate
            elif e.key == pygame.K_f:
                self.facing = -self.facing
            elif e.key in (pygame.K_DELETE, pygame.K_BACKSPACE) and self.selected is not None:
                self.delete_selected()
            elif self.selected is not None and e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                p = self.design["custom"][self.selected]
                step = 2.0 if shift else 0.5
                self.checkpoint()
                if e.key == pygame.K_LEFT:
                    p["x"] -= step * self.facing
                elif e.key == pygame.K_RIGHT:
                    p["x"] += step * self.facing
                elif e.key == pygame.K_UP:
                    p["y"] -= step
                else:
                    p["y"] += step
        elif e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx < PANEL_W:
                self.scroll[self.tab] = _fit(self.scroll[self.tab] - e.y * 40, 0,
                                             max(0, self.content_h - (H - TOP_H - 40)))
            else:
                self.zoom = _fit(self.zoom + e.y * 0.25, 0.75, 3.0)

    def request_quit(self):
        if self.dirty and not self.quit_armed:
            self.quit_armed = True
            self.say("Unsaved changes! Ctrl+S saves – press Esc / close again to quit without saving")
        else:
            self.running = False

    def delete_selected(self):
        self.checkpoint()
        del self.design["custom"][self.selected]
        self.selected = None
        self.say("Part removed")

    # ---- drawing ---------------------------------------------------------------
    def draw(self):
        scr = self.screen
        scr.fill(BG)
        lights.new_frame()
        self.draw_preview(scr)
        self.draw_panel(scr)
        self.draw_top(scr)

    def draw_top(self, scr):
        ui = self.ui
        pygame.draw.rect(scr, PANEL, (0, 0, W, TOP_H))
        pygame.draw.line(scr, LINE, (0, TOP_H - 1), (W, TOP_H - 1))
        ui.text(scr, "Shadowra Modeler", (14, 12), TEXT, ui.big)
        x = 230
        for label, fn, w in (("Save", self.save, 70), ("Export", self.export, 80), ("Undo", self.do_undo, 64),
                             ("Redo", self.do_redo, 64), ("Revert", self.revert, 74),
                             ("Standard look", self.reset_all, 120)):
            if ui.button(scr, (x, 8, w, 28), label, col=(90, 60, 130) if label == "Export" else None):
                fn()
            x += w + 8
        state = ("* unsaved changes" if self.dirty else "saved")
        ui.text(scr, state, (x + 10, 15), WARN if self.dirty else DIM, ui.small)
        if self.msg_t > 0:
            ui.text(scr, self.msg, (W - 12 - ui.small.size(self.msg)[0], 15), WARN if "Unsaved" in self.msg else ACCENT,
                    ui.small)

    def revert(self):
        self.checkpoint()
        self.design = dd.load(self.path) if os.path.exists(self.path) else dd.normalize({})
        self._fix_selection()
        self.say("Back to the last saved design")

    def reset_all(self):
        self.checkpoint()
        name = self.design.get("name", "Shadowra")
        self.design = dd.normalize({"name": name})
        self.selected = None
        self.say("Standard look (Ctrl+Z to undo)")

    # ---- left panel --------------------------------------------------------------
    def draw_panel(self, scr):
        ui = self.ui
        pygame.draw.rect(scr, PANEL, (0, TOP_H, PANEL_W, H - TOP_H))
        pygame.draw.line(scr, LINE, (PANEL_W, TOP_H), (PANEL_W, H))
        tabs = ("Shape", "Colours", "Parts", "Extras")
        tw = (PANEL_W - 20) // len(tabs)
        for i, name in enumerate(tabs):
            if ui.button(scr, (10 + i * tw, TOP_H + 8, tw - 6, 28), name, on=self.tab == name):
                self.tab = name
        area = pygame.Rect(0, TOP_H + 44, PANEL_W - 1, H - TOP_H - 44)
        scr.set_clip(area)
        ui.clip = area
        y0 = area.y + 6 - self.scroll[self.tab]
        y = getattr(self, "panel_" + self.tab.lower())(scr, y0)
        self.content_h = y - y0 + 20
        self.scroll[self.tab] = _fit(self.scroll[self.tab], 0, max(0, self.content_h - area.h))
        ui.clip = None
        scr.set_clip(None)
        if self.content_h > area.h:                       # scrollbar
            frac = area.h / self.content_h
            pos = self.scroll[self.tab] / max(1, self.content_h - area.h)
            bar_h = max(30, area.h * frac)
            pygame.draw.rect(scr, LINE, (PANEL_W - 7, area.y + (area.h - bar_h) * pos, 4, bar_h), border_radius=2)

    def panel_shape(self, scr, y):
        ui, S = self.ui, self.design["sizes"]
        for label, key, lo, hi in SHAPE_SLIDERS:
            if key is None:
                ui.text(scr, label.upper(), (16, y + 6), ACCENT, ui.small)
                y += 26
                continue
            fmt = "{:+.0f}°" if key == "horn_angle" else "{:.2f}"
            S[key] = ui.slider(scr, "s_" + key, (16, y, PANEL_W - 40, 30), label, S[key], lo, hi,
                               step=1 if key == "horn_angle" else 0.01, fmt=fmt)
            y += 36
        y += 6
        if ui.button(scr, (16, y, 160, 28), "Reset shape"):
            self.checkpoint()
            self.design["sizes"] = copy.deepcopy(dd.DEFAULT["sizes"])
        return y + 34

    def panel_colours(self, scr, y):
        ui, C = self.ui, self.design["colors"]
        cols = dd.colors(self.design)
        for key, label in COLOR_LABELS:
            r = pygame.Rect(16, y, PANEL_W - 40, 30)
            sel = self.color_key == key
            pygame.draw.rect(scr, PANEL_2 if sel else PANEL, r, border_radius=5)
            if sel:
                pygame.draw.rect(scr, ACCENT, r, 1, border_radius=5)
            pygame.draw.rect(scr, cols[key], (r.x + 6, r.y + 5, 34, 20), border_radius=4)
            pygame.draw.rect(scr, LINE, (r.x + 6, r.y + 5, 34, 20), 1, border_radius=4)
            ui.text(scr, label, (r.x + 50, r.y + 8), TEXT)
            if C.get(key) is None:
                ui.text(scr, "auto", (r.right - 44, r.y + 9), DIM, ui.small)
            if ui.hit(r):
                self.color_key = key
            y += 34
        key = self.color_key
        y += 8
        ui.text(scr, "EDIT: " + dict(COLOR_LABELS)[key].upper(), (16, y), ACCENT, ui.small)
        y += 22
        if key in ("belly", "spikes"):
            auto = C.get(key) is None
            new = ui.checkbox(scr, (16, y, 300, 24), "Automatic (follows the body colour)", auto)
            if new != auto:
                C[key] = None if new else list(cols[key])
            y += 30
        if C.get(key) is not None:
            c = list(C[key])
            for i, ch in enumerate("RGB"):
                c[i] = int(ui.slider(scr, "c_%s_%d" % (key, i), (16, y, PANEL_W - 40, 30), ch, c[i], 0, 255,
                                     step=1, fmt="{:.0f}"))
                y += 36
            hsv = pygame.Color(*c).hsva
            light = ui.slider(scr, "c_%s_v" % key, (16, y, PANEL_W - 40, 30), "Brightness", hsv[2], 0, 100,
                              step=1, fmt="{:.0f}")
            if abs(light - hsv[2]) > 0.5:
                col = pygame.Color(0)
                col.hsva = (hsv[0], hsv[1], light, 100)
                c = [col.r, col.g, col.b]
            y += 40
            C[key] = c
            ui.text(scr, "Palette", (16, y), DIM, ui.small)
            y += 18
            for i, pc in enumerate(PALETTE):
                r = pygame.Rect(16 + (i % 8) * 42, y + (i // 8) * 34, 36, 28)
                pygame.draw.rect(scr, pc, r, border_radius=4)
                pygame.draw.rect(scr, LINE, r, 1, border_radius=4)
                if ui.hit(r):
                    self.checkpoint()
                    C[key] = list(pc)
            y += 34 * ((len(PALETTE) + 7) // 8) + 8
        y += 6
        ui.text(scr, "Preview eye colour (in the game it follows her morality):", (16, y), DIM, ui.small)
        y += 20
        for i, ec in enumerate(EYE_COLORS):
            r = pygame.Rect(16 + i * 42, y, 36, 26)
            pygame.draw.rect(scr, ec, r, border_radius=13)
            pygame.draw.rect(scr, TEXT if i == self.eye else LINE, r, 2 if i == self.eye else 1, border_radius=13)
            if ui.hit(r):
                self.eye = i
        y += 40
        if ui.button(scr, (16, y, 160, 28), "Reset colours"):
            self.checkpoint()
            self.design["colors"] = copy.deepcopy(dd.DEFAULT["colors"])
        return y + 34

    def panel_parts(self, scr, y):
        ui, P, N = self.ui, self.design["parts"], self.design["counts"]
        ui.text(scr, "BODY PARTS – untick to remove", (16, y + 4), ACCENT, ui.small)
        y += 26
        for key, label in PART_LABELS:
            P[key] = ui.checkbox(scr, (16, y, PANEL_W - 40, 26), label, P[key])
            y += 28
        y += 10
        ui.text(scr, "HOW MANY", (16, y), ACCENT, ui.small)
        y += 24
        for key, label, lo, hi in COUNT_LABELS:
            N[key] = ui.stepper(scr, (16, y, PANEL_W - 40, 26), label, N[key], lo, hi)
            y += 32
        y += 10
        ui.text(scr, "New parts of your own: tab Extras.", (16, y), DIM, ui.small)
        return y + 24

    def panel_extras(self, scr, y):
        ui, parts = self.ui, self.design["custom"]
        ui.text(scr, "ADD A PART", (16, y + 4), ACCENT, ui.small)
        y += 26
        bw = (PANEL_W - 40) // 3
        for i, kind in enumerate(dd.PART_TYPES):
            if ui.button(scr, (16 + (i % 3) * (bw + 4), y + (i // 3) * 32, bw, 28), "+ " + kind.capitalize()):
                self.checkpoint()
                parts.append(dd.new_part(kind))
                self.selected = len(parts) - 1
                self.say("Added a %s – drag it in the preview" % kind)
        y += 70
        ui.text(scr, "YOUR PARTS (%d)" % len(parts), (16, y), ACCENT, ui.small)
        y += 22
        if not parts:
            ui.text(scr, "None yet. Add one above, then drag it on her.", (16, y), DIM, ui.small)
            y += 24
        for i, p in enumerate(parts):
            r = pygame.Rect(16, y, PANEL_W - 40, 26)
            sel = i == self.selected
            pygame.draw.rect(scr, PANEL_2 if sel else PANEL, r, border_radius=4)
            if sel:
                pygame.draw.rect(scr, ACCENT, r, 1, border_radius=4)
            col = dd.part_color(p, dd.colors(self.design))
            pygame.draw.circle(scr, col, (r.x + 14, r.centery), 7)
            ui.text(scr, "%d. %s  on %s  (%s)" % (i + 1, p["type"], p["anchor"].replace("_", " "), p["layer"]),
                    (r.x + 28, r.y + 6), TEXT if sel else DIM, ui.small)
            if ui.hit(r):
                self.selected = None if sel else i
            y += 30
        if self.selected is None:
            return y + 10
        p = parts[self.selected]
        y += 10
        ui.text(scr, "EDIT PART %d – %s" % (self.selected + 1, p["type"].upper()), (16, y), ACCENT, ui.small)
        y += 24
        for label, key, options in (("Attached to", "anchor", dd.ANCHORS), ("Layer", "layer", dd.LAYERS)):
            ui.text(scr, label, (16, y + 5), DIM, ui.small)
            i = options.index(p[key]) if p[key] in options else 0
            if ui.button(scr, (150, y, 26, 24), "<"):
                self.checkpoint()
                p[key] = options[(i - 1) % len(options)]
            ui.text(scr, p[key].replace("_", " "), (245, y + 12), TEXT, center=True)
            if ui.button(scr, (PANEL_W - 50, y, 26, 24), ">"):
                self.checkpoint()
                p[key] = options[(i + 1) % len(options)]
            y += 30
        for label, key, lo, hi in (("Position X", "x", -40, 40), ("Position Y", "y", -40, 40),
                                   ("Size / width", "size", 0.2, 16), ("Length", "length", 0.5, 45),
                                   ("Angle", "angle", -180, 180), ("Bend", "bend", -1.5, 1.5)):
            fmt = "{:+.0f}°" if key == "angle" else "{:.1f}"
            p[key] = ui.slider(scr, "p%d_%s" % (self.selected, key), (16, y, PANEL_W - 40, 30), label, p[key], lo, hi,
                               step=1 if key == "angle" else 0.1, fmt=fmt)
            y += 36
        ui.text(scr, "Colour", (16, y + 5), DIM, ui.small)
        names = dd.COLOR_NAMES + ("own",)
        cur = p["color"] if isinstance(p["color"], str) else "own"
        i = names.index(cur) if cur in names else 0
        if ui.button(scr, (150, y, 26, 24), "<"):
            self.checkpoint()
            p["color"] = self._color_choice(names[(i - 1) % len(names)], p)
        ui.text(scr, cur, (245, y + 12), TEXT, center=True)
        if ui.button(scr, (PANEL_W - 50, y, 26, 24), ">"):
            self.checkpoint()
            p["color"] = self._color_choice(names[(i + 1) % len(names)], p)
        y += 30
        if not isinstance(p["color"], str):
            c = list(p["color"])
            for j, ch in enumerate("RGB"):
                c[j] = int(ui.slider(scr, "pc%d_%d" % (self.selected, j), (16, y, PANEL_W - 40, 30), ch, c[j], 0, 255,
                                     step=1, fmt="{:.0f}"))
                y += 36
            p["color"] = c
        p["far_copy"] = ui.checkbox(scr, (16, y, PANEL_W - 40, 26), "Also on her far side (darker copy)",
                                    p.get("far_copy", False))
        y += 34
        if ui.button(scr, (16, y, 110, 28), "Duplicate"):
            self.checkpoint()
            q = copy.deepcopy(p)
            q["x"] += 3
            parts.append(q)
            self.selected = len(parts) - 1
        if ui.button(scr, (134, y, 110, 28), "Delete", col=(110, 40, 60)):
            self.delete_selected()
        return y + 40

    def _color_choice(self, name, p):
        if name == "own":
            return list(dd.part_color(p, dd.colors(self.design)))
        return name

    # ---- preview -------------------------------------------------------------------
    def preview_rect(self):
        return pygame.Rect(PANEL_W + 1, TOP_H, W - PANEL_W - 1, H - TOP_H - BAR_H)

    def draw_backdrop(self, scr, r):
        kind = BACKDROPS[self.backdrop]
        if kind == "Grey":
            scr.fill((92, 92, 98), r)
            return
        top, bottom = {"Cave": ((14, 10, 20), (40, 30, 48)), "Dusk": ((40, 34, 80), (150, 90, 110)),
                       "Day": ((110, 170, 220), (200, 225, 240))}[kind]
        for i in range(r.h):
            u = i / r.h
            pygame.draw.line(scr, [int(a + (b - a) * u) for a, b in zip(top, bottom)], (r.x, r.y + i), (r.right, r.y + i))
        ground = {"Cave": (30, 24, 36), "Dusk": (40, 34, 50), "Day": (70, 120, 60)}[kind]
        pygame.draw.rect(scr, ground, (r.x, r.bottom - 60, r.w, 60))

    def draw_preview(self, scr):
        ui = self.ui
        r = self.preview_rect()
        scr.set_clip(r)
        self.draw_backdrop(scr, r)
        eye = EYE_COLORS[self.eye]
        mouse_in = r.collidepoint(ui.mouse)
        # test light follows the mouse (or stays where it was last)
        if self.light_on:
            if mouse_in and not self.drag and not (ui.active and ui.held):
                self.light_pos = ui.mouse
            if self.light_pos is None:
                self.light_pos = (r.centerx + 160, r.y + 120)
            col = LIGHTS[self.light_kind][1]
            render.draw_light_circle(scr, *self.light_pos, 110, col=col, alpha=70)
            pygame.draw.circle(scr, col, self.light_pos, 6)
        info = {}
        if self.view == "side":
            fx, fy = r.centerx, r.bottom - 60
            lights.new_frame()                  # this frame's test light counts for this frame's model
            if self.light_on:
                lights.add(*self.light_pos, 110, LIGHTS[self.light_kind][1], 1.0)
            lights.new_frame()
            models.ground_shadow(scr, fx, fy, 120 * self.zoom * (0.62, 1.0, 1.42)[self.stage])
            models.draw_dragon(scr, fx, fy, self.stage, self.facing, self.pose, self.t, eye=eye,
                               scale_mult=self.zoom, design=self.design, info=info)
            # real in-game size, top right
            inset = pygame.Rect(r.right - 230, r.y + 10, 220, 130)
            pygame.draw.rect(scr, (0, 0, 0), inset)
            pygame.draw.rect(scr, LINE, inset, 1)
            models.draw_dragon(scr, inset.centerx, inset.bottom - 12, self.stage, self.facing, self.pose, self.t,
                               eye=eye, design=self.design)
            ui.text(scr, "in-game size", (inset.x + 6, inset.y + 4), DIM, ui.small)
            ui.text(scr, "zoom %.2fx (mouse wheel)" % self.zoom, (r.x + 12, r.y + 10), DIM, ui.small)
            if self.light_on:
                ui.text(scr, "the light follows your mouse", (r.x + 12, r.y + 28), DIM, ui.small)
            if self.tab == "Extras":
                self.draw_part_handles(scr, r, info)
        else:
            key = (json.dumps(self.design, sort_keys=True), self.stage, self.eye)
            img = self.portrait_cache.get(key)
            if img is None:
                if len(self.portrait_cache) > 6:
                    self.portrait_cache.clear()
                img = models.build_portrait(int(r.h * 0.95), self.stage, eye, design=self.design)
                self.portrait_cache[key] = img
            scr.blit(img, (r.centerx - img.get_width() // 2, r.bottom - img.get_height()))
            ui.text(scr, "Close-up (front view): extra parts are side-view only", (r.x + 12, r.y + 10), DIM, ui.small)
        scr.set_clip(None)
        self.draw_bar(scr)

    def draw_part_handles(self, scr, r, info):
        ui = self.ui
        if not info:
            return
        to_screen, k, fac = info["to_screen"], info["px_per_unit"], info["facing"]
        for name, (ax, ay, unit) in info["anchors"].items():           # where parts can attach
            pygame.draw.circle(scr, (90, 200, 220), [int(v) for v in to_screen(ax, ay)], 4, 1)
        handles = []
        for i, p in enumerate(self.design["custom"]):
            if p["anchor"] not in info["anchors"]:
                continue
            ax, ay, unit = info["anchors"][p["anchor"]]
            pos = to_screen(ax + p["x"] * unit, ay + p["y"] * unit)
            handles.append((i, pos, unit))
            sel = i == self.selected
            pygame.draw.circle(scr, ACCENT if sel else TEXT, [int(v) for v in pos], 8 if sel else 6, 2)
            if sel:
                ui.text(scr, "drag me", (pos[0] + 10, pos[1] - 18), ACCENT, ui.small)
        if ui.pressed and r.collidepoint(ui.pressed):                     # pick up a part
            best = min(handles, key=lambda h: math.dist(h[1], ui.pressed), default=None)
            if best and math.dist(best[1], ui.pressed) < 14:
                self.selected = best[0]
                self.checkpoint()
                self.drag = (best[0], ui.pressed, self.design["custom"][best[0]]["x"],
                             self.design["custom"][best[0]]["y"], best[2])
        if self.drag and ui.held:
            i, start, x0, y0, unit = self.drag
            if i < len(self.design["custom"]):
                p = self.design["custom"][i]
                p["x"] = round(x0 + (ui.mouse[0] - start[0]) / (k * unit) * fac, 1)
                p["y"] = round(y0 + (ui.mouse[1] - start[1]) / (k * unit), 1)
        elif self.drag:
            self.drag = None

    def draw_bar(self, scr):
        ui = self.ui
        bar = pygame.Rect(PANEL_W + 1, H - BAR_H, W - PANEL_W - 1, BAR_H)
        pygame.draw.rect(scr, PANEL, bar)
        pygame.draw.line(scr, LINE, bar.topleft, bar.topright)
        x, y = bar.x + 8, bar.y + 9

        def btn(w, label, on=False):
            nonlocal x
            hit = ui.button(scr, (x, y, w, 26), label, on=on)
            x += w + 4
            return hit

        for label, st in STAGES:
            if btn(80, label, self.stage == st):
                self.stage = st
        x += 6
        if btn(22, "<"):
            self.pose = POSES[(POSES.index(self.pose) - 1) % len(POSES)]
        ui.text(scr, self.pose, (x + 40, y + 13), TEXT, center=True)
        x += 84
        if btn(22, ">"):
            self.pose = POSES[(POSES.index(self.pose) + 1) % len(POSES)]
        x += 6
        if btn(46, "Flip", self.facing < 0):
            self.facing = -self.facing
        if btn(70, "Animate", self.animate):
            self.animate = not self.animate
        if btn(52, "Light", self.light_on):
            self.light_on = not self.light_on
        if btn(58, LIGHTS[self.light_kind][0]):
            self.light_kind = (self.light_kind + 1) % len(LIGHTS)
        if btn(52, BACKDROPS[self.backdrop]):
            self.backdrop = (self.backdrop + 1) % len(BACKDROPS)
        if btn(bar.right - x - 8, "Close-up" if self.view == "side" else "Side view", self.view == "portrait"):
            self.view = "portrait" if self.view == "side" else "side"

def main(path=None):
    if path is None:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        path = args[0] if args else None
    Editor(path).run()


if __name__ == "__main__":
    main()
