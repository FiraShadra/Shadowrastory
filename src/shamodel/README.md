# shamodel – Shadowra's modelling kit

Everything to design Shadowra in one folder: the editor, her rig, all her drawn pieces and her design file.
It needs only Python 3 and pygame and does not depend on the rest of the game, so this folder alone can be
copied, zipped or shared.

```
pip install -r requirements.txt
python editor.py                 # the Shadowra Modeler (or from the folder above: python shamodel/editor.py)
python editor.py other.json      # edit another design file
```

## What is inside

| | |
|---|---|
| `editor.py` | the Shadowra Modeler |
| `shadowra_design.json` | her design: sizes, colours, pieces, fine-tuning, extra parts (the game reads this file) |
| `sheets/` | the drawn parts sheets (main sheet, `torso.jpg`, `wings.jpg`) |
| `parts/` | every piece cut out of the sheets (PNG with transparency, plus eye / horn masks) |
| `extract_parts.py` | cuts `sheets/` into `parts/` again (`python extract_parts.py`, after changing a sheet) |
| `rig.py` | the cutout rig: which piece hangs where, joints, poses |
| `render.py` | drawing: the rig, the code-drawn model, the close-up portrait, scales shining in light |
| `design.py` | the design format (load / save / defaults) |
| `lights.py` | light sources the scales react to |
| `exports/` | made by Export: `design.json`, a PNG of every pose for every stage, a sprite sheet, portraits |

## The editor

- **Shape**: sizes (overall, body, head, neck, legs, tail, wings, scale shine, ...).
- **Colours**: body, wings, horns (and more for the code-drawn model); the preview eye colour.
- **Parts**: the model (drawn sheet or drawn in code); which sheet piece fills each slot (head, neck, chest,
  front legs, hind legs, tail, wings) and fine-tuning per piece (move, turn, size).
- **Extras**: your own parts (spike, horn, fin, oval, whisker, gem) on an anchor, dragged in the preview.

Preview: every stage and pose, side view or close-up, a test light following the mouse.
**Save** (Ctrl+S) writes `shadowra_design.json`, **Export** (Ctrl+E) also writes `exports/<name>_<date>/`.
Keys: Ctrl+Z / Ctrl+Y undo / redo, Space animate, F flip, arrows nudge the selected extra part, wheel zooms.
