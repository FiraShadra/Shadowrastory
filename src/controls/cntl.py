"""Keyboard bindings and per-frame input state."""
import pygame

BINDINGS = {
    "left": (pygame.K_a, pygame.K_LEFT),
    "right": (pygame.K_d, pygame.K_RIGHT),
    "up": (pygame.K_w, pygame.K_UP),
    "down": (pygame.K_s, pygame.K_DOWN),
    "jump": (pygame.K_SPACE,),
    "sprint": (pygame.K_LSHIFT, pygame.K_RSHIFT),
    "claw": (pygame.K_j,),
    "tail": (pygame.K_k,),
    "spike": (pygame.K_l,),
    "fire": (pygame.K_i,),
    "blood": (pygame.K_u,),
    "dash": (pygame.K_q,),
    "interact": (pygame.K_e,),
    "confirm": (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE),
    "pause": (pygame.K_ESCAPE,),
}

# (the key descriptions shown in the controls screen are in texts.HELP, so they can be translated)


class Controls:
    def __init__(self):
        self.held = set()
        self.pressed = set()
        self.released = set()

    def begin_frame(self):
        self.pressed.clear()
        self.released.clear()

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            for action, keys in BINDINGS.items():
                if event.key in keys:
                    self.held.add(action)
                    self.pressed.add(action)
        elif event.type == pygame.KEYUP:
            for action, keys in BINDINGS.items():
                if event.key in keys:
                    self.held.discard(action)
                    self.released.add(action)

    def down(self, action):
        return action in self.held

    def hit(self, action):
        return action in self.pressed

    def up(self, action):
        return action in self.released

    def axis(self):
        return (1 if self.down("right") else 0) - (1 if self.down("left") else 0)

    def clear(self):
        self.held.clear()
        self.pressed.clear()
        self.released.clear()
