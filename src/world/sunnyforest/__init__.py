"""sunnyforest – the daylight lands: Sonnenwiesen and Tal der Schattensteine (juvenile).

The sun burns her: shade under canopies, rock arches, ponds, cloud shadows and the dark tunnel.
What she learns here: see abilities.json (Lichtgewöhnung grows in the sun; the Schattensteine).
"""


def build(b):
    from .. import MEADOW, VALE, VALE_W
    carve_at, obj_at = b.carve_at, b.obj_at

    # ======================= Sonnenwiesen (daylight, juvenile) =======================
    # Open sky – the sun burns her. Hide under tree canopies, the rock arch, in the pond, in cloud
    # shadows – or take the dark tunnel below. Ground row 38 like the river; tunnel rows 44-46.
    def m(lx):
        return MEADOW[0] + lx
    carve_at(m(0), 0, m(79), 37)                      # open sky
    carve_at(m(2), 44, m(67), 46)                     # the dark tunnel (3 rows: everyone fits)
    # Erdbau: an earth burrow – press E to crawl into the dark tunnel (and back out). A choice, not a trap.
    obj_at("burrow", m(5), 37, "burrow_top", to=(m(4), 46))
    obj_at("burrow", m(3), 46, "burrow_down", to=(m(6), 37))
    carve_at(m(30), 46, m(34), 46, "#")               # a bump in the tunnel floor
    carve_at(m(62), 41, m(67), 43)                    # higher ceiling before the steps (room to jump)
    carve_at(m(68), 38, m(75), 46)                    # shaft back up, with 2-row steps
    for i, top in enumerate((45, 43, 41, 39)):
        carve_at(m(68 + i * 2), top, m(69 + i * 2), 46, "#")
    for lx in (9, 20, 56):                            # trees: leaf canopies cast shade
        carve_at(m(lx), 29, m(lx + 5), 30, "T")
        obj_at("decor", m(lx + 2), 37, f"trunk_m{lx}", decor="trunk", top=31)
    carve_at(m(34), 30, m(46), 31, "#")               # rock arch over the resting place
    obj_at("decor", m(35), 37, "arch_l", decor="pillar", top=32)
    obj_at("decor", m(45), 37, "arch_r", decor="pillar", top=32)
    obj_at("altar", m(40), 37, "A5", stock={"fish": 2})
    carve_at(m(50), 38, m(54), 40, "~")               # pond: under water she is safe from the sun
    obj_at("fish", m(51), 39, "sun_fish1")
    obj_at("fish", m(53), 40, "sun_fish2")
    obj_at("priest", m(28), 37, "sun_pr1")
    obj_at("priest", m(64), 37, "sun_pr2")
    obj_at("peaceful", m(17), 37, "deer_m1")
    obj_at("peaceful", m(59), 37, "deer_m2")
    obj_at("skeleton", m(22), 46, "sk_tun1")
    obj_at("skeleton", m(48), 46, "sk_tun2")
    obj_at("crystal", m(40), 46, "c_tunnel")
    obj_at("sun_intro", m(1), 37, "sun_intro_meadow", text="meadow")
    for lx, kind in ((5, "flower"), (7, "grass_day"), (16, "bush_day"), (27, "flower"), (31, "grass_day"),
                     (48, "stone_day"), (62, "flower"), (66, "grass_day"), (77, "bush_day")):
        obj_at("decor", m(lx), 37, f"mdecor_{lx}", decor=kind)

    # ================ Tal der Schattensteine (big daylight valley, juvenile) ================
    # A wide sunny valley. The way east is shut by the Schattentor; three Schattensteine in three
    # very different places must be woken first: in a dark cave, on a lake island, on a sunny mesa.
    def v(lx):
        return VALE[0] + lx
    carve_at(v(0), 0, v(104), 37)                     # open sky, ground row 38
    obj_at("sun_intro", v(1), 37, "sun_intro_vale", text="vale")
    for lx in (4, 36, 89):                            # shade trees
        carve_at(v(lx), 29, v(lx + 5), 30, "T")
        obj_at("decor", v(lx + 2), 37, f"trunk_v{lx}", decor="trunk", top=31)
    # 1) the hill with a dark cave – the only way past it (too high to climb)
    carve_at(v(14), 31, v(30), 37, "#")
    carve_at(v(14), 34, v(30), 37)                    # cave passage, 4 rows
    obj_at("shadow_stone", v(22), 37, "stone_cave")
    obj_at("altar", v(17), 37, "A8", stock={"fish": 2})   # a cool spring in the dark – rest out of the sun
    obj_at("skeleton", v(18), 37, "sk_vale1")
    obj_at("skeleton", v(27), 37, "sk_vale2")
    obj_at("peaceful", v(33), 37, "deer_v1")
    obj_at("peaceful", v(42), 37, "deer_v2")
    # 2) the lake with an island – swim or glide; under water the sun can't reach her
    carve_at(v(45), 38, v(62), 42, "~")
    carve_at(v(52), 36, v(55), 42, "#")
    obj_at("shadow_stone", v(53), 35, "stone_lake")
    for i, (fx, fy) in enumerate(((47, 40), (50, 42), (59, 41))):
        obj_at("fish", v(fx), fy, f"vale_fish{i}")
    # resting place under a rock overhang
    carve_at(v(64), 30, v(71), 31, "#")
    obj_at("decor", v(64), 37, "vale_pil_l", decor="pillar", top=32)
    obj_at("decor", v(71), 37, "vale_pil_r", decor="pillar", top=32)
    obj_at("altar", v(67), 37, "A7", stock={"fish": 3})
    # 3) the mesa – a warm updraft carries her up into the full sun
    carve_at(v(73), 12, v(75), 37, "U")
    carve_at(v(76), 26, v(84), 37, "#")
    obj_at("shadow_stone", v(80), 25, "stone_mesa")
    obj_at("skull", v(88), 18, "vale_sk1")            # on the open plain east of the mesa
    obj_at("skull", v(98), 22, "vale_sk2")
    obj_at("priest", v(95), 37, "vale_pr2")
    # the Schattentor in a cliff wall: a closed gate of shadow stone
    carve_at(v(105), 34, v(110), 37)
    carve_at(v(107), 34, v(108), 37, "G")
    obj_at("vale_gate", v(104), 37, "vale_gate")
    obj_at("altar", v(110), 37, "A9", stock={"fish": 2, "meat": 2})   # in the gate's shadow, behind the gate
    carve_at(v(111), 0, v(VALE_W - 1), 37)            # beyond the gate: open sky to the canyon rim
    for lx, kind in ((2, "flower"), (11, "grass_day"), (32, "flower"), (44, "bush_day"), (63, "grass_day"),
                     (86, "flower"), (100, "stone_day"), (113, "grass_day"), (117, "flower")):
        obj_at("decor", v(lx), 37, f"vdecor_{lx}", decor=kind)
