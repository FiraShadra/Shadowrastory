"""snowyvillage – a village of humans in the snow (see humans.md).

The humans can meet Shadowra kindly or try to kill her – it depends on what she has become
(her morality) and on whether Fira is with her. Their elder can give her the Herdsegen.
Villager names, looks and lines live in texts.HUMANS; the behaviour in src/humans.py.
What she learns here: see abilities.json.
"""

# name, local x, gender ("f" / "m"), role
HUMANS = (
    ("Mira", 60, "f", "villager"),
    ("Bjarn", 66, "m", "hunter"),
    ("Hanne", 73, "f", "villager"),
    ("Gunnar", 79, "m", "elder"),
    ("Tomas", 88, "m", "hunter"),
    ("Ylva", 94, "f", "villager"),
)
HEARTH = 77                      # local x of the village hearth (warmth)


def build(b, s, g):
    obj_at = b.obj_at
    for hx, size in ((58, 1.0), (69, 0.9), (84, 1.1), (97, 0.95)):
        obj_at("decor", s(hx), g - 1, f"humanhouse_{hx}", decor="humanhouse", size=size)
    obj_at("hearth", s(HEARTH), g - 1, "village_hearth")
    obj_at("altar", s(81), g - 1, "H", stock={"fish": 2, "meat": 2}, locked_humans=True)
    for name, lx, gender, role in HUMANS:
        obj_at("human", s(lx), g - 1, f"human_{name.lower()}", name=name, gender=gender, role=role)
    for lx, kind in ((56, "pine"), (63, "fence"), (75, "lantern_snow"), (86, "fence"), (91, "lantern_snow"),
                     (100, "pine")):
        obj_at("decor", s(lx), g - 1, f"vdecor_snow_{lx}", decor=kind)
