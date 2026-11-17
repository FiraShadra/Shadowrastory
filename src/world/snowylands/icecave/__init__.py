"""icecave – the Eishöhle below the Schneefelder.

A shaft in the snow leads down into a hall of blue ice. An ice wall blocks the back of the cave:
only the Finsternis-Flamme melts it. Behind it, frozen in the ice, beats the Frostherz (Frostschuppen).
What she learns here: see abilities.json.
"""


def build(b, s, g):
    carve_at, obj_at = b.carve_at, b.obj_at
    floor = g + 15                                       # cave floor row (air down to floor-1)
    carve_at(s(20), g, s(22), floor - 1)                 # shaft down from the snow
    carve_at(s(14), g + 6, s(50), floor - 1)             # the ice hall
    for i, top in enumerate((floor - 8, floor - 6, floor - 4, floor - 2)):   # ice steps up to the shaft
        carve_at(s(23 + i * 2), top, s(24 + i * 2), floor - 1, "#")
    carve_at(s(36), g + 6, s(37), floor - 1, "I")        # the ice wall – melt it with fire
    obj_at("relic", s(46), floor - 1, "frost_heart", relic="frost_scales")
    obj_at("crystal", s(16), floor - 1, "c_ice1")
    obj_at("crystal", s(42), floor - 1, "c_ice2")
    obj_at("skeleton", s(31), floor - 1, "sk_ice1")
    obj_at("altar", s(17), floor - 1, "S2", stock={"fish": 2})
    for lx in (15, 19, 27, 33, 40, 44, 49):
        obj_at("decor", s(lx), floor - 1, f"ice_{lx}", decor="icicle", top=g + 6)
