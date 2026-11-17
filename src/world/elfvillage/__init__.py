"""elfvillage – the Elfenhain with the Elfendorf (optional, below the cliff and the ruins).

Sera, Erila and six villagers; the monster waves and Shadowra's choice live in src/grove.py.
What she learns here: see abilities.json.
"""


def build(b):
    carve, obj = b.carve, b.obj
    # Entered from the canyon floor (row 46) through a low tunnel. Floor row 46, ceiling row 23,
    # so the cliff top and the ruin floor above (row 18) stay untouched.
    carve(151, 40, 156, 45)             # tunnel from the canyon floor (6 tall: an adult fits)
    carve(157, 24, 224, 45)             # the grove hall
    carve(170, 46, 178, 47, "~")        # moon pond, floor row 48
    for i, fx in enumerate((172, 176)):
        obj("fish", fx, 47, f"grove_fish{i}")
    carve(184, 42, 189, 42, "#")        # floating rock ledges, each step <= 4 tiles for a juvenile
    carve(205, 42, 209, 42, "#")
    carve(195, 38, 200, 38, "#")
    obj("crystal", 197, 37, "c_grove")
    carve(214, 42, 224, 45, "#")        # raised elf camp (4 rows: a juvenile can climb it)
    obj("elf", 216, 41, "sera", name="Sera")
    obj("elf", 220, 41, "erila", name="Erila")
    obj("altar", 223, 41, "E", stock={"fish": 2, "meat": 2}, locked=True)
    obj("grove", 160, 45, "grove_quest")
    # Elfendorf: houses of the village (they hide inside during the attack and come out afterwards)
    for hx, hy, size in ((165, 45, 1.0), (187, 41, 0.85), (198, 37, 0.85), (207, 41, 0.9), (219, 41, 1.15)):
        obj("decor", hx, hy, f"elfhouse_{hx}", decor="elfhouse", size=size)
    for name, hx, hy in (("Lyria", 167, 45), ("Aren", 169, 45), ("Naela", 188, 41), ("Calen", 199, 37),
                         ("Thessa", 206, 41), ("Fenrik", 212, 45)):
        obj("villager", hx, hy, f"vil_{name.lower()}", name=name)
    for (dx, dy, kind) in ((159, 45, "tree"), (166, 45, "bush"), (181, 45, "tree"), (183, 45, "mushroom"),
                           (192, 45, "tree"), (194, 45, "grass"), (202, 45, "mushroom"), (204, 45, "bush"),
                           (211, 45, "tree"), (186, 41, "mushroom"), (199, 37, "grass"), (207, 41, "mushroom"),
                           (215, 41, "lantern"), (222, 41, "lantern"), (172, 45, "lantern"), (190, 41, "lantern"),
                           (201, 37, "lantern"), (210, 45, "lantern"), (168, 45, "stone"),
                           (213, 45, "stone")):
        obj("decor", dx, dy, f"decor_{dx}_{dy}", decor=kind)
