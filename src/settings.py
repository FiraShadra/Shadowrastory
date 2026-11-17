"""Global constants for Shadowra's Story."""
import os
import sys

FROZEN = getattr(sys, "frozen", False)          # running as a built game (.exe / AppImage, PyInstaller)
if FROZEN:
    ROOT = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))     # bundled game files (read-only)
    # the folder the .exe – or the .AppImage file (the AppImage runtime sets $APPIMAGE) – lies in
    GAME_DIR = os.path.dirname(os.environ.get("APPIMAGE") or sys.executable)
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GAME_DIR = ROOT
ASSETS = os.path.join(ROOT, "assets")
# saves live next to the game; if that folder can't be written to (e.g. a system-wide install on Linux),
# they go to the user's data folder instead
SAVE_DIR = os.path.join(GAME_DIR, "saves")
if FROZEN and not os.access(GAME_DIR, os.W_OK):
    base = (os.environ.get("APPDATA") if os.name == "nt" else
            os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share"))
    SAVE_DIR = os.path.join(base or os.path.expanduser("~"), "shadowras-story", "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "spielstand.json")              # old format, imported once
CORRUPT_FLAG = os.path.join(SAVE_DIR, "korrumpierte_seele.flag")   # old format, imported once
# Saves now live in the SQLite database saves/shadowra.db (see src/save.py)

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TILE = 32
TITLE = "Shadowra's Story"

GRAVITY = 2000.0
MAX_FALL = 900.0

# --- Colours ---------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (240, 236, 245)
TEXT = (226, 214, 236)
TEXT_DIM = (150, 135, 165)
SHADOW_PURPLE = (58, 36, 74)
DEEP = (14, 9, 20)
CAVE_BG = (24, 15, 32)
ROCK = (46, 26, 58)
ROCK_DARK = (30, 17, 40)
ROCK_EDGE = (226, 120, 92)
ROCK_EDGE2 = (250, 180, 110)
HP_COL = (196, 40, 58)
MANA_COL = (120, 82, 230)
STAM_COL = (226, 178, 70)
LIGHT_COL = (255, 230, 150)
LAVA_COL = (255, 110, 40)
WATER_COL = (40, 70, 120)

# --- Shadowra's growth stages ----------------------------------------------
# Every number here was tuned against the level layout in world.py:
#   hatchling jump ~2.4 tiles, juvenile ~4.5, adult ~5.
STAGES = [
    dict(key="hatchling", name="Schlüpfling", w=28, h=22, walk=170, jump=560,
         max_hp=60, max_mana=40, max_stam=60, glide_fall=150, updraft=15,
         claw=6, reach=26, food="milk"),
    dict(key="juvenile", name="Jungdrachin", w=44, h=34, walk=205, jump=760,
         max_hp=100, max_mana=70, max_stam=90, glide_fall=105, updraft=-300,
         claw=10, reach=36, food="fish"),
    dict(key="adult", name="Finsternis-Drachin", w=62, h=46, walk=230, jump=800,
         max_hp=150, max_mana=100, max_stam=120, glide_fall=80, updraft=-340,
         claw=16, reach=48, food="meat"),
]
# Food needed (eaten while in a stage) before she grows during her next sleep.
GROWTH_NEED = {0: ("milk", 3), 1: ("fish", 5)}

# Resource tuning
SPRINT_MULT = 1.75
SPRINT_DRAIN = 22.0          # stamina / s
GROUND_STAM_REGEN = 34.0     # the "ground bonus"
WATER_STAM_REGEN = 10.0
EXHAUST_TIME = 2.0
FLAP_COST = 12.0
FLAP_VY = -520.0
ADULT_GLIDE_DRAIN = 2.0
WALLJUMP_COST = 8.0
DASH_COST = 20.0
TAIL_COST = 8.0
DIVE_COST = 15.0
SPIKE_MANA = 6.0
FIRE_MANA = 14.0             # per second
HUNGER_TIME = 8 * 60         # seconds without a meal before max stamina shrinks
SLEEPLESS_TIME = 10 * 60     # seconds awake before madness creeps in

# Manaschulung: every point of mana she ever spends (spikes, fire, the veil – at any age) trains her.
# The training pays off once she is an adult: a bigger mana pool and stronger spells.
#   mastery = 1 - exp(-mana_spent / MANA_MASTERY_SCALE)   (0 -> 1, ~63 % after 600 mana, ~92 % after 1500)
MANA_MASTERY_SCALE = 600.0
ADULT_MANA_BONUS = 80.0      # extra max mana for an adult at 100 % mastery
ADULT_SPELL_MULT = 1.5       # adult spells hit harder ...
MASTERY_SPELL_BONUS = 0.4    # ... and up to +40 % more with full mastery
SPIKE_DMG = 14.0
FIRE_DPS = 45.0

# Daylight (Sonnenwiesen, Gleißende Hochebene) and Lichtgewöhnung (sun adaptation):
# every second she spends in sunlight – burning or holding the veil up – trains her body to endure it.
#   adaptation = 1 - exp(-sun_exposure / SUN_ADAPT_SCALE)   (~63 % after 45 s in the light)
DAY_DMG = 12.0               # diffuse daylight burns less than a focused sunbeam
VEIL_DRAIN_DAY = 4.0
SUN_ADAPT_SCALE = 45.0
SUN_ADAPT_DMG = 0.7          # up to -70 % sun damage
SUN_ADAPT_VEIL = 0.5         # up to -50 % veil drain in sunlight
SHRINE_EXPOSURE_RATE = 4.0   # enduring the light at the Sonnenschrein trains 4x faster
SHRINE_DMG = 16.0

# Light / heat
SUN_DMG = 25.0
LAVA_LIGHT_DMG = 40.0
TORCH_DMG = 15.0
VEIL_DRAIN_SUN = 6.0
VEIL_DRAIN_LAVA = 8.0
VEIL_DRAIN_TORCH = 5.0
VEIL_EMPTY_DMG = 18.0
LAVA_HEAT_STAM = 5.0
