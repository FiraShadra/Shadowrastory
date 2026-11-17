"""lowrow – the row of high places between the valley and the lava: Aufwindschlucht, Klippe der Stürme,
Ruinen des Lichts and the Gleißende Hochebene.

What she learns here: see abilities.json (Fliegen from the storm dragon, Schattenschleier,
Obsidian-Klauen, Finsternis-Flamme; Lichtgewöhnung at the Sonnenschrein).
"""


def build(b):
    from .. import PLATEAU, PLATEAU_W
    carve, obj, carve_at, obj_at = b.carve, b.obj, b.carve_at, b.obj_at

    # ---------------- Aufwindschlucht ----------------
    carve(119, 0, 150, 45)              # canyon, floor row 46
    carve(123, 20, 125, 45, "U")        # updraft 1
    carve(135, 8, 137, 45, "U")         # updraft 2
    carve(121, 44, 122, 45, "#")        # way back up if she falls
    carve(119, 42, 120, 45, "#")
    obj("skeleton", 130, 45, "sk_canyon1")
    obj("skeleton", 145, 45, "sk_canyon2")
    obj("crystal", 141, 45, "c_canyon")

    # ---------------- Klippe der Stürme ----------------
    carve(151, 0, 166, 17)              # cliff top, ground row 18
    obj("storm", 155, 17, "storm")
    obj("relic", 161, 17, "veil", relic="veil")

    # ---------------- Ruinen des Lichts ----------------
    carve(167, 8, 225, 17)              # ruin halls, floor row 18, roof row 7
    carve(175, 0, 176, 7)
    carve(175, 8, 176, 17, "*")
    obj("relic", 180, 17, "obsidian", relic="obsidian")
    obj("priest", 185, 17, "pr1")
    obj("skeleton", 189, 17, "sk_ruin1")
    carve(192, 8, 192, 17, "C")         # cracked wall
    obj("altar", 196, 17, "A2", stock={"fish": 2, "meat": 3})
    obj("peaceful", 201, 17, "deer3")
    carve(205, 0, 206, 7)
    carve(205, 8, 206, 17, "*")
    obj("relic", 210, 17, "fire", relic="fire")
    obj("priest", 215, 17, "pr2")
    carve(222, 8, 222, 17, "V")         # thorn vines

    # ===================== Gleißende Hochebene (daylight, adult) =====================
    # A blazing plateau between the ruins and the lava sea. No clouds – only old temple roofs and
    # floating rocks give shade. The Sonnenschrein lets her endure the light on purpose.
    def pl(lx):
        return PLATEAU[0] + lx
    carve_at(pl(0), 0, pl(PLATEAU_W - 1), 17)        # open sky, ground row 18 like the ruin floor
    for a, c in ((8, 15), (30, 36), (52, 60)):        # temple roofs on pillars
        carve_at(pl(a), 9, pl(c), 10, "#")
        obj_at("decor", pl(a), 17, f"tpil_{a}", decor="pillar", top=11)
        obj_at("decor", pl(c), 17, f"tpil_{c}", decor="pillar", top=11)
    carve_at(pl(20), 5, pl(24), 6, "#")               # floating rocks
    carve_at(pl(42), 5, pl(46), 6, "#")
    carve_at(pl(44), 16, pl(48), 17, "#")             # a low mound
    obj_at("altar", pl(56), 17, "A6", stock={"meat": 2})
    obj_at("sun_shrine", pl(39), 17, "shrine")
    obj_at("priest", pl(18), 17, "hi_pr1")
    obj_at("priest", pl(51), 17, "hi_pr2")
    obj_at("skull", pl(30), 6, "hi_sk1")
    obj_at("skull", pl(64), 5, "hi_sk2")
    obj_at("sun_intro", pl(1), 17, "sun_intro_plateau", text="plateau")
    for lx, kind in ((4, "stone_day"), (19, "grass_day"), (27, "stone_day"), (41, "grass_day"),
                     (63, "stone_day"), (67, "grass_day")):
        obj_at("decor", pl(lx), 17, f"pdecor_{lx}", decor=kind)
