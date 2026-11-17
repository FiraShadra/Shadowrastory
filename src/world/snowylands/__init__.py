"""snowylands – the Schneelande: the story after Fira (or without her, carrying her grief).

Reached through the Frostpass beside the Letzte Rast. Overcast – no sun burns here, but the cold does:
outside the warmth of a hearth it eats her stamina and then her life (Frostschuppen protect her).

    snowfield    the open Schneefelder (west), the Frostrast
    icecave/     the Eishöhle below the snowfield: ice walls melt in the Finsternis-Flamme; the Frostherz
    snowyvillage/ a village of humans – kind to her, or hunting her, depending on what she has become
    frozenlake   the Frostsee: otters dive through a hole in the ice (Tauchen) – below lies underwater/
    northcliff   the Nordklippe, where the road goes on north (the story continues)

What she learns here: see abilities.json in this folder and in icecave/ and snowyvillage/.
"""
from . import icecave, snowyvillage

# local x ranges (tiles from the start of the snowlands)
ICECAVE = (14, 50)
VILLAGE = (55, 100)
LAKE = (101, 149)
NORTH = (150, 179)
LAKE_HOLE = (122, 125)


def build(b):
    from .. import SNOW, SNOW_GROUND, SNOW_W
    carve_at, obj_at = b.carve_at, b.obj_at

    def s(lx):
        return SNOW[0] + lx
    g = SNOW_GROUND
    carve_at(s(5), 0, s(SNOW_W - 2), g - 1)          # overcast sky over the snowlands, ground row g
    obj_at("snow_arrive", s(6), g - 1, "snow_arrive")       # arrival – with Fira, alone, or in grief

    # ---------------- Schneefelder (west) ----------------
    obj_at("altar", s(10), g - 1, "S1", stock={"fish": 2, "meat": 1})
    carve_at(s(24), g - 3, s(27), g - 1, "#")         # snow-covered boulders (2-3 rows)
    carve_at(s(40), g - 2, s(42), g - 1, "#")
    obj_at("skeleton", s(31), g - 1, "sk_snow1")
    obj_at("skeleton", s(46), g - 1, "sk_snow2")
    for lx, kind in ((7, "pine"), (15, "snowrock"), (19, "pine"), (33, "pine"), (37, "snowrock"),
                     (49, "pine"), (52, "pine")):
        obj_at("decor", s(lx), g - 1, f"sdecor_{lx}", decor=kind)

    icecave.build(b, s, g)
    snowyvillage.build(b, s, g)

    # ---------------- Frostsee (frozen lake) ----------------
    carve_at(s(LAKE[0]), g, s(LAKE[1]), g, "F")       # the ice sheet is the floor
    carve_at(s(LAKE_HOLE[0]), g, s(LAKE_HOLE[1]), g, "w")   # a hole in the ice: the otters' door
    obj_at("otters", s(LAKE_HOLE[0] + 1), g - 1, "otters")
    obj_at("altar", s(108), g - 1, "S3", stock={"fish": 3})
    for lx, kind in ((103, "snowrock"), (113, "reed_frost"), (131, "reed_frost"), (140, "snowrock"),
                     (146, "pine")):
        obj_at("decor", s(lx), g - 1, f"ldecor_{lx}", decor=kind)

    # ---------------- Nordklippe ----------------
    for i, top in enumerate((g - 3, g - 6, g - 9, g - 12)):   # rising steps of 3 rows (an adult climbs them)
        carve_at(s(NORTH[0] + 4 + i * 6), top, s(NORTH[0] + 9 + i * 6), g - 1, "#")
    carve_at(s(NORTH[0] + 28), g - 12, s(SNOW_W - 2), g - 1, "#")
    obj_at("altar", s(NORTH[0] + 22), g - 13, "S4", stock={"meat": 2})
    obj_at("chapter_end", s(SNOW_W - 4), g - 13, "north_road")
    for lx, kind in ((NORTH[0] + 2, "pine"), (NORTH[0] + 15, "snowrock"), (NORTH[0] + 26, "pine")):
        obj_at("decor", s(lx), g - 1 if lx < NORTH[0] + 4 else g - 13, f"ndecor_{lx}", decor=kind)


def zone_at(tx, ty):
    from .. import SNOW, SNOW_GROUND
    lx = tx - SNOW[0]
    if lx < 5:
        return "frostpass"
    if ty > SNOW_GROUND and ICECAVE[0] <= lx <= ICECAVE[1]:
        return "icecave"
    if VILLAGE[0] <= lx <= VILLAGE[1]:
        return "snowvillage"
    if LAKE[0] <= lx <= LAKE[1]:
        return "frozenlake"
    if lx >= NORTH[0]:
        return "northcliff"
    return "snowfield"
