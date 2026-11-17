"""underwater – the caves under the Frostsee (after Fira).

Deep, ice-cold water ('w'). Without Tauchen she floats back up at the hole in the ice; with it she can
swim down – but her breath runs out (air pockets under the ice refill it). At the bottom rests the
Tiefenperle (Tiefenatem: she holds her breath much longer).
What she learns here: see abilities.json.
"""
AREA = (102, 176)                 # local x range under the lake and the north cliff


def build(b):
    from .. import SNOW, SNOW_GROUND
    carve_at, obj_at = b.carve_at, b.obj_at

    def s(lx):
        return SNOW[0] + lx
    g = SNOW_GROUND
    bottom = g + 16                                    # lowest water row
    carve_at(s(AREA[0]), g + 1, s(AREA[1]), bottom, "w")
    carve_at(s(110), g + 6, s(114), bottom, "#")        # rock pillars – swim around and under them
    carve_at(s(132), g + 1, s(135), g + 9, "#")
    carve_at(s(150), g + 1, s(176), g + 5, "#")         # the north cliff's foot reaches into the water
    carve_at(s(150), g + 6, s(153), g + 11, "#")
    carve_at(s(156), g + 13, s(162), bottom, "#")
    carve_at(s(140), g + 1, s(143), g + 2)              # an air pocket under the ice: breathe here
    for i, (lx, dy) in enumerate(((118, 6), (126, 11), (138, 14), (147, 9), (166, 12))):
        obj_at("fish", s(lx), g + dy, f"ice_fish{i}")
    obj_at("crystal", s(129), bottom, "c_deep1")
    obj_at("crystal", s(171), g + 7, "c_deep2")
    obj_at("relic", s(168), bottom, "deep_pearl", relic="deep_breath")
    for lx in (105, 117, 124, 137, 145, 164, 173):
        obj_at("decor", s(lx), bottom, f"kelp_{lx}", decor="kelp")


def zone_at(tx, ty):
    from .. import SNOW, SNOW_GROUND
    lx = tx - SNOW[0]
    if AREA[0] <= lx <= AREA[1] and ty > SNOW_GROUND:
        return "underwater"
    return None
