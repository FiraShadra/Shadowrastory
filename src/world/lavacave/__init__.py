"""lavacave – the Lavameer (adult flight) and Mafors Gipfel (boss, Fira's cage).

Also the Frostpass: a cold cleft next to the Letzte Rast. It leads down and east, under the boss arena,
into the snowlands. It is open at any time – so Shadowra could even leave without freeing Fira
(her grief then weighs on everything she does).
What she learns here: see abilities.json.
"""


def build(b):
    from .. import X, SNOW, SNOW_GROUND
    carve, obj, carve_at, obj_at = b.carve, b.obj, b.carve_at, b.obj_at

    # ---------------- Lavameer (adult flight) ----------------
    carve(226, 2, 299, 41)
    carve(226, 42, 299, 44, "L")
    # 16-tile gaps that rise: a juvenile's best jump+glide covers ~14, an adult flies.
    carve(242, 15, 246, 44, "#")        # shadow pillar 1 (one row above the ruin floor + margin)
    obj("crystal", 244, 14, "c_lava1")
    carve(259, 15, 269, 44, "#")        # shadow island
    obj("altar", 264, 14, "A3", stock={"meat": 2})
    carve(279, 14, 283, 44, "#")        # shadow pillar 3
    obj("crystal", 281, 13, "c_lava2")
    obj("skull", 252, 9, "skull1")
    obj("skull", 274, 8, "skull2")
    obj("skull", 292, 7, "skull3")

    # ---------------- Mafors Gipfel ----------------
    carve(300, 0, 349, 11)              # summit, floor row 12
    obj("noreturn", 304, 11, "noreturn")
    obj("altar", 308, 11, "A4", stock={"meat": 2})
    obj("boss", 330, 6, "mafor", arena_left=X(314))
    obj("fira", 346, 11, "fira")

    # ---------------- Frostpass (to the snowlands) ----------------
    # E at the cleft beside the Letzte Rast: down into an icy tunnel that runs east under the arena.
    top = SNOW_GROUND - 4                              # tunnel air rows top..SNOW_GROUND-1, floor = snow ground
    carve_at(X(305), top, SNOW[0] + 4, SNOW_GROUND - 1)
    obj("passage", 311, 11, "frostpass_down", to=(X(307), SNOW_GROUND - 1), label="frostpass_in")
    obj("passage", 306, SNOW_GROUND - 1, "frostpass_up", to=(X(310), 11), label="frostpass_out")
    obj_at("snow_intro", X(318), SNOW_GROUND - 1, "snow_intro")
    for lx in (309, 316, 325, 334, 343):               # icicles and frost in the tunnel
        obj("decor", lx, SNOW_GROUND - 1, f"fp_ice_{lx}", decor="icicle", top=top)


def zone_at(tx, ty):
    """The Frostpass lies under the summit (summit columns, below row 20)."""
    from .. import X
    if X(300) <= tx <= X(349) and ty >= 20:
        return "frostpass"
    return None
