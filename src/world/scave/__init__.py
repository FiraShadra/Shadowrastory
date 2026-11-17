"""scave – the dark start caves: Das Nest (hatchling) and the Flusstal (juvenile).

What Shadowra learns here: see abilities.json (Gleiten from the shadow birds, the Blut-Sog instinct).
Original coordinates, shifted with X() by the Builder.
"""


def build(b):
    carve, obj = b.carve, b.obj

    # ---------------- Das Nest (hatchling) ----------------
    carve(1, 36, 3, 39)                 # secret chamber, only a hatchling fits through...
    carve(4, 39, 9, 39)                 # ...this 1-tile tunnel
    obj("crystal", 2, 39, "c_secret")
    carve(10, 30, 43, 39)               # main nest cave, floor row 40
    obj("altar", 13, 39, "N", stock={"milk": 2})
    obj("peaceful", 19, 39, "deer0")    # a Moosläufer living in the nest cave – the hatchling's first friend
    obj("start", 16, 39, "start")
    carve(20, 0, 21, 29)                # ceiling crack -> sunbeam
    carve(20, 30, 21, 39, "*")
    # bird-watching ledge: two 2-tile steps (hatchling can climb 2)
    carve(25, 38, 26, 39, "#")
    carve(27, 36, 30, 39, "#")
    carve(26, 22, 31, 29)               # opening in the ceiling
    obj("birds", 28, 35, "birds")
    carve(33, 0, 34, 29)
    carve(33, 30, 34, 39, "*")
    # glide pit: 8 tiles wide, far side 2 rows lower. Too wide to jump, easy to glide.
    carve(36, 40, 43, 47)
    carve(36, 47, 43, 47, "x")
    carve(44, 30, 56, 41)               # moon spring cave, floor row 42
    obj("altar", 50, 41, "M", stock={"milk": 3})
    obj("crystal", 54, 41, "c_moon")
    # growth gate: 4-tile ledge (only a juvenile can climb it) – tell the hatchling why
    obj("gate_hint", 55, 41, "gate_nest", need_stage=1)
    carve(57, 4, 118, 37)               # sky over the river valley, ground row 38

    # ---------------- Flusstal (juvenile) ----------------
    obj("owl", 66, 37, "owl")
    carve(72, 38, 92, 38)
    carve(72, 39, 92, 43, "~")          # river, floor row 44
    for i, (fx, fy) in enumerate([(76, 42), (80, 41), (84, 42), (88, 41), (78, 40), (86, 40)]):
        obj("fish", fx, fy, f"fish{i}")
    obj("altar", 100, 37, "A1", stock={"fish": 3})
    obj("peaceful", 106, 37, "deer1")
    obj("peaceful", 112, 37, "deer2")
