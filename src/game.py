"""Main loop and scene switching."""
import random
import sys

import pygame

from .settings import SCREEN_W, SCREEN_H, FPS, TITLE
from .controls.cntl import Controls
from .assets import Sprites
from .render import TileArt, Backdrop
from .play import Play
from .scenes import Title, Pause, Ending
from . import morals, save, texts


class Game:
    def __init__(self, dev=False):
        texts.set_language(save.get_setting("language", "de"))
        save.sync_moral_defs(morals.load())          # data/morals.json -> table moral_defs
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.sprites = Sprites()
        try:
            pygame.display.set_icon(pygame.transform.smoothscale(self.sprites.logo, (64, 64)))
        except pygame.error:
            pass
        self.tile_art = TileArt(self.sprites)
        self.backdrop = Backdrop(self.sprites)
        self.ctl = Controls()
        self.dev = dev
        self.dev_pressed = set()
        self.shake = 0.0
        self.shake_off = (0, 0)
        self.running = True
        self.scene = Title(self)

    # ---- scene changes ------------------------------------------------------
    def to_menu(self):
        self.ctl.clear()
        self.scene = Title(self)

    def new_game(self):
        save.clear_soul_lost()
        save.clear_journey()            # a new journey for the credits replay
        self.ctl.clear()
        self.scene = Play(self, None)

    def continue_game(self):
        data = save.load()
        self.ctl.clear()
        if data is None:
            self.new_game()
        else:
            self.scene = Play(self, data)

    def show_ending(self, key, morality):
        self.ctl.clear()
        self.scene = Ending(self, key, morality)

    # ---- loop -------------------------------------------------------------
    def step(self, dt, events):
        self.ctl.begin_frame()
        self.dev_pressed.clear()
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False
            self.ctl.handle(e)
            if e.type == pygame.KEYDOWN:
                self.dev_pressed.add(e.key)
        if isinstance(self.scene, Play) and self.ctl.hit("pause") and not self.scene.dialog.active:
            self.scene = Pause(self, self.scene)
            self.ctl.pressed.discard("pause")
        self.scene.update(dt, self.ctl)
        self.shake = max(0.0, self.shake - dt)
        self.shake_off = ((random.uniform(-6, 6), random.uniform(-6, 6)) if self.shake > 0 else (0, 0))
        self.scene.draw(self.screen)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30)
            self.step(dt, pygame.event.get())
            pygame.display.flip()
        pygame.quit()


def main():
    Game(dev="--dev" in sys.argv).run()
