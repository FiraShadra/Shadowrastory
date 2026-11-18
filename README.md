# Shadowra's Story

A dark survival-metroidvania about Shadowra, a young darkness dragon. Built with pygame from the design in `storybrainstorming.md`.

## Run

```
pip install -r requirements.txt
python main.py          # normal
python main.py --dev    # dev keys: F1 grow, F2 all abilities, F3 refill bars, F4 +corruption, F5 teleport through zones
```

Saves go to the SQLite database `saves/shadowra.db` (only when Shadowra sleeps at a nest/altar).
Every part of the save has its own table (player, morality, deeds, flags, hugs, save_history, ...), so it
can be opened with any SQLite viewer, e.g. *DB Browser for SQLite*. Quick overview in the terminal:

```
python -m src.save
```

## Building release versions

- **Windows (.exe):** PyInstaller in the project's `.venv` builds `dist/ShadowraS.aplha1.exe` (one file, art and data bundled).
- **Linux (AppImage):** push to `main`/`master` or manually run the **Build Linux AppImage** workflow on GitHub.
  Download `ShadowraS-AppImage` from the completed workflow's **Artifacts** section. It builds on Ubuntu 22.04.
  To build locally on Linux or WSL, run `bash packaging/linux/build_appimage.sh` → `dist/ShadowraS.aplha1-x86_64.AppImage`.

Built games save next to the .exe / .AppImage (`saves/`), or in `%APPDATA%` / `~/.local/share/shadowras-story` if that folder is read-only.
A `data/morals.json` placed next to the built game overrides the bundled one.

## Cheats

`src/controls/xheats.json` – set a cheat to `true` to turn it on, `false` to turn it off:
`"infinite mana"`, `"infinite stamina"`, `"infinite health"` (nothing can kill her, not even lava or drowning).
Read when a game is started or continued; active cheats are shown in the top-right corner.
For the built game, put a `xheats.json` next to the .exe / .AppImage (the bundled one has everything off).

## Adding your own morals (no code needed)

Extra morals live in **`data/morals.json`**. Add an entry to `"morals"` and restart the game; the
`"_doc"` section at the top of the file lists every field, event and stat. Example:

```json
{
  "key": "night_calm",
  "name": {"de": "Nachtruhe", "en": "Night Calm"},
  "description": {"de": "Sie schläft gut und gern.", "en": "She sleeps well and gladly."},
  "level": "basic",
  "ages": ["juvenile", "adult"],
  "max": 5,
  "gain": {"rest": 1},
  "effects": [{"at": 5, "good": true, "name": {"de": "Ausgeruht", "en": "Well Rested"},
               "description": {"de": "Schlaf schenkt mehr Mana.", "en": "Sleep restores more mana."},
               "mods": {"sleep_mana": 1.1}}]
}
```

- `level`: `basic`, or `advanced`. **Advanced morals are hard-limited to 3 points** in this (FSK 12) version, whatever `max` says.
- `ages`: the ages at which the moral can grow (`hatchling`, `juvenile`, `adult`).
- `gain`: which game events raise it (`cozy_meal`, `rest`, `kindness`, `affection`, `hunt_ground`, ...).
- `limit_line` (optional): what Shadowra says to the player, walking up to the camera, when the moral is at its max.
- Mistakes in the file never crash the game: broken entries are skipped and the reason is printed in the terminal (`[morals.json] ...`).

The definitions are copied into the database table `moral_defs` at every start; Shadowra's values are saved
per game in `moral_values` (both visible in DB Browser for SQLite).

## Shadowra Modeler (her design)

```
python model.py               # or: python main.py --editor
```

A tool to reshape Shadowra without touching code. Left side, four tabs:

- **Shape**: sliders for overall size, body, chest, head, snout, eyes, neck, horns (length, thickness, angle, curve),
  legs, tail, wings, spikes, frills, scale size and how strongly the scales shine.
- **Colours**: body, belly, spikes, wings, horns, claws, outline (RGB, brightness, palette; belly and spikes can follow
  the body colour automatically).
- **Parts**: switch body parts on/off (horns, frills, spikes, plates, fangs, wings, tail spade, scales, shine, ...)
  and set how many spikes, spines, frills and toes she has.
- **Extras**: add parts of your own: spike, horn, fin, oval (plate/mark), whisker, gem. Each sits on an anchor
  (head, neck, back, chest, hips, middle or tip of the tail), so it moves with her in every pose. Drag it in the
  preview, or set position, size, length, angle, bend, colour, layer (behind / front / top) and an optional darker
  copy on her far side. Delete removes it.

Right side: live preview at every stage and pose (side view or close-up portrait), an in-game-size inset, and a
test light that follows the mouse (torch, lava, magic, moon), so you can see the scales shine.

**Save** (Ctrl+S) writes `data/shadowra_design.json`; the game uses it from the next start (a copy next to the
built game overrides the bundled one, like `morals.json`). **Export** (Ctrl+E) also saves, then writes
`exports/<name>_<date>/` with `design.json`, a PNG of every pose for every stage, a sprite sheet and the portraits.
Other keys: Ctrl+Z / Ctrl+Y undo / redo, Space animate, F flip, arrow keys nudge the selected extra part,
mouse wheel zooms the preview. Extra parts show in the side view only (not in the front-facing close-up).

## Where things live

| File | What |
|---|---|
| `src/world/` | The map, one folder per place (by biome and area). `__init__.py` holds the shared parts (constants, `X()`, `Builder`, `Level`, zones); each place builds itself in its own `__init__.py`: `scave/` (Nest, Flusstal), `sunnyforest/` (Sonnenwiesen, Tal der Schattensteine), `lowrow/` (Aufwindschlucht, Klippe, Ruinen, Gleißende Hochebene), `elfvillage/`, `lavacave/` (Lavameer, Gipfel, Frostpass), `snowylands/` (+ `icecave/`, `snowyvillage/`), `underwater/`. Gap/ledge sizes are tuned to `settings.py`; use `X()` for hard-coded positions in the original areas. |
| `src/world/<place>/abilities.json` | What Shadowra can learn at that place: name, description, ages, how (watch / relic / gift / instinct / trait). Loaded by `src/abilities.py` – edit names and texts freely. |
| `src/snow.py`, `src/humans.py` | Chapter 2, the snowlands: Frostpass, arrival with Fira / alone / in grief, cold and hearths, diving and breath, the otters, the north road; the humans (kind, wary or hostile depending on her soul). |
| `src/settings.py` | All tuning: growth stages, stamina/mana costs, light damage. |
| `src/texts.py` | Every line of in-game text (German) – edit story here. |
| `src/player.py` | Shadowra: Leben/Mana/Ausdauer, exhaustion, glide → updraft → flight, attacks. |
| `src/morality.py` | Hidden soul state. Deeds are counted in `Morality`; one `MoralPath` subclass per path (Sanftmut, Wildheit, Wahnsinn, Gier) defines its tiers, owl reaction, nest look and ending; each path branches into `SubPath` subclasses (e.g. Raubtier / Flügelschlag) chosen by the *kind* of deeds (`Morality.deeds`), and the active subpath's effects (stat modifiers) apply per tier. |
| `data/morals.json`, `src/morals.py` | Extra morals (e.g. SAffection): definitions in JSON, loaded and validated by `morals.py`, applied in `Morality` (values, age limits, caps, effects, limit lines). |
| `src/closeup.py` | Shadowra walking up to the camera and talking to the player (credits ending, moral limit refusals). |
| `src/play.py` | Gameplay: combat, light & lava, altars (eat/drink/sleep), blood, cutscenes, boss. |
| `src/grove.py` | Elfenhain side area and its Elfendorf: the elves Sera & Erila, six villagers (they hide during the attack and come out afterwards), vampire enemy, the 3 monster waves and Shadowra's choice (help / don't help / nuzzle with Zuneigung). Survival odds tuned in `ARCHER_COOL`, `HEAL`, `Elf.max_hp`. Villager looks, talk and first-hug lines live in `texts.VILLAGERS`. |
| `src/hugs.py` | "Umarmen": the E-menu for creatures, how they react to a hug (her soul + how often she hugged them), kindness/affection points. |
| `src/creatures.py` | Moosläufer, fish, Lichtpriester, skeletons, skulls, owl Morwen, Fira, Mafor. |
| `src/models.py` | High-resolution creature models (Shadowra/Fira, elves, Moosläufer, fish, owl, and the enemies: skeleton, skull, light priest, vampire, Mafor): drawn 3-4x supersampled from smooth curves, then scaled down for anti-aliased edges. |
| `src/tilegen.py` | High-resolution map tiles generated at start-up (4x supersampled): rounded corners, glowing rims, texture, grass, animated water/lava, several variants per shape. |
| `src/scenes.py` | Title, start warning, pause, endings (incl. the greed save wipe). |
