"""Save game handling with SQLite – including the deliberate save wipe of the greed ending.

Everything lives in one database file: saves/shadowra.db
Every part of the save has its own readable table, so it can be opened and inspected with any
SQLite viewer (e.g. "DB Browser for SQLite") – or printed with:   python -m src.save

    meta           key/value: checkpoint, world time, last save, "soul_lost" (greed ending), schema version
    player         one row: stage, position, Leben/Mana/Ausdauer, hunger, sleep, Manaschulung, food eaten
    abilities      one row per learned ability
    morality       one row: wild / madness / lust / abhorrent ... plus *readable* columns
                   (corruption, current nature, the ending she is heading for)
    deeds          one row per kind of deed (feeds the moral subpaths)
    moral_values   Shadowra's value of each extra moral (data/morals.json), with its max and level
    moral_defs     copy of the definitions in data/morals.json (refreshed at every game start)
    flags          one row per story flag (birds seen, owl talked, grove outcome, ...)
    picked         crystals and relics already taken
    world_tiles    cracked walls broken / vines burned
    altar_stock    food left at every nest / altar
    hugs           how often she has hugged each creature
    save_history   a log of every save (when, where, stage, corruption) – never wiped by new saves

The rest of the game only uses: has_save(), load(), write(data), wipe_for_greed(), soul_lost(),
clear_soul_lost(). load()/write() use the same dict layout the game has always used.
"""
import json
import os
import sqlite3
import time

from .settings import SAVE_DIR, SAVE_FILE, CORRUPT_FLAG

DB_FILE = os.path.join(SAVE_DIR, "shadowra.db")
SCHEMA_VERSION = 2

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta        (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS player      (id INTEGER PRIMARY KEY CHECK (id = 1),
                                        stage INTEGER, stage_name TEXT, x REAL, y REAL, facing INTEGER,
                                        hp REAL, mana REAL, stamina REAL,
                                        awake_time REAL, hunger_time REAL, mana_spent REAL,
                                        food_milk INTEGER, food_fish INTEGER, food_meat INTEGER,
                                        sun_exposure REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS abilities   (name TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS morality    (id INTEGER PRIMARY KEY CHECK (id = 1),
                                        wild REAL, madness REAL, lust REAL, abhorrent INTEGER,
                                        blood_count INTEGER, boss_choice TEXT,
                                        corruption REAL, nature TEXT, ending_now TEXT);
CREATE TABLE IF NOT EXISTS deeds       (deed TEXT PRIMARY KEY, amount REAL);
CREATE TABLE IF NOT EXISTS flags       (flag TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS picked      (item_id TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS world_tiles (x INTEGER, y INTEGER, change TEXT, PRIMARY KEY (x, y, change));
CREATE TABLE IF NOT EXISTS altar_stock (altar TEXT, food TEXT, amount INTEGER, PRIMARY KEY (altar, food));
CREATE TABLE IF NOT EXISTS hugs        (creature_id TEXT PRIMARY KEY, count INTEGER);
CREATE TABLE IF NOT EXISTS moral_values(moral TEXT PRIMARY KEY, value REAL, max REAL, level TEXT, name TEXT);
CREATE TABLE IF NOT EXISTS moral_defs  (key TEXT PRIMARY KEY, level TEXT, name_de TEXT, name_en TEXT,
                                        description_de TEXT, description_en TEXT, ages TEXT, max INTEGER,
                                        gain TEXT, effects TEXT, limit_line_de TEXT, limit_line_en TEXT,
                                        source TEXT);
CREATE TABLE IF NOT EXISTS journey     (id INTEGER PRIMARY KEY AUTOINCREMENT, x REAL, y REAL, stage INTEGER,
                                        pose TEXT, facing INTEGER, flap REAL, event TEXT);
CREATE TABLE IF NOT EXISTS save_history(id INTEGER PRIMARY KEY AUTOINCREMENT, saved_at TEXT,
                                        checkpoint TEXT, stage_name TEXT, hp REAL, mana REAL,
                                        corruption REAL, nature TEXT);
"""
# tables that make up the current save (save_history and meta are kept separately)
SAVE_TABLES = ("player", "abilities", "morality", "deeds", "flags", "picked", "world_tiles",
               "altar_stock", "hugs", "moral_values")


# ---------------------------------------------------------------------------
# connection
# ---------------------------------------------------------------------------
def _connect():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    con = sqlite3.connect(DB_FILE)
    con.executescript(SCHEMA)
    _upgrade_schema(con)
    _set_meta(con, "schema_version", SCHEMA_VERSION)
    _migrate_old_files(con)
    return con


def _upgrade_schema(con):
    """Add columns that newer versions of the game store (older databases keep working)."""
    cols = {r[1] for r in con.execute("PRAGMA table_info(player)")}
    if "sun_exposure" not in cols:
        con.execute("ALTER TABLE player ADD COLUMN sun_exposure REAL DEFAULT 0")


def _get_meta(con, key, default=None):
    row = con.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def _set_meta(con, key, value):
    con.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, str(value)))


def _migrate_old_files(con):
    """One-time import of the old JSON save / greed flag file, kept as *.bak."""
    if os.path.exists(SAVE_FILE) and con.execute("SELECT COUNT(*) FROM player").fetchone()[0] == 0:
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                _write(con, json.load(f))
            os.replace(SAVE_FILE, SAVE_FILE + ".bak")
        except (OSError, ValueError):
            pass
    if os.path.exists(CORRUPT_FLAG):
        _set_meta(con, "soul_lost", 1)
        try:
            os.replace(CORRUPT_FLAG, CORRUPT_FLAG + ".bak")
        except OSError:
            pass
    con.commit()


# ---------------------------------------------------------------------------
# public API (unchanged for the rest of the game)
# ---------------------------------------------------------------------------
def has_save():
    try:
        with _closing(_connect()) as con:
            return con.execute("SELECT COUNT(*) FROM player").fetchone()[0] > 0
    except sqlite3.Error:
        return False


def load():
    try:
        with _closing(_connect()) as con:
            return _read(con)
    except sqlite3.Error:
        return None


def write(data):
    with _closing(_connect()) as con:
        with con:                                   # one transaction: a save is all-or-nothing
            _write(con, data)


def wipe_for_greed():
    """The greed ending: the save is gone and the menu remembers the lost soul."""
    with _closing(_connect()) as con:
        with con:
            for t in SAVE_TABLES + ("journey",):
                con.execute(f"DELETE FROM {t}")
            con.execute("DELETE FROM meta WHERE key IN ('checkpoint', 'world_time', 'last_save', 'world_version')")
            _set_meta(con, "soul_lost", 1)
            con.execute("INSERT INTO save_history (saved_at, checkpoint, stage_name, nature) VALUES (?, ?, ?, ?)",
                        (_now(), "-", "-", "Korrumpierte Seele – Durch Gier verloren"))


# ---------------------------------------------------------------------------
# journey: Shadowra's recorded path for the credits replay. Only stretches that end in a save are kept
# (a death reloads the last save and throws the unsaved part away) – so the replay has no deaths.
# ---------------------------------------------------------------------------
def append_journey(samples):
    if not samples:
        return
    with _closing(_connect()) as con:
        with con:
            con.executemany("INSERT INTO journey (x, y, stage, pose, facing, flap, event) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            samples)


def load_journey():
    try:
        with _closing(_connect()) as con:
            return con.execute("SELECT x, y, stage, pose, facing, flap, event FROM journey ORDER BY id").fetchall()
    except sqlite3.Error:
        return []


def clear_journey():
    """A new game: new journey, and her story is not finished any more."""
    with _closing(_connect()) as con:
        with con:
            con.execute("DELETE FROM journey")
            con.execute("DELETE FROM meta WHERE key = 'story_finished'")


def sync_moral_defs(defs):
    """Mirror data/morals.json into the table moral_defs (readable in any SQLite viewer)."""
    rows = []
    for d in defs.values():
        j = d.as_json()
        rows.append((d.key, d.level, d.names.get("de"), d.names.get("en"), d.descs.get("de"), d.descs.get("en"),
                     ", ".join(d.ages), d.max, json.dumps(d.gain), json.dumps(j["effects"], ensure_ascii=False),
                     (d.limit_lines or {}).get("de"), (d.limit_lines or {}).get("en"), "data/morals.json"))
    try:
        with _closing(_connect()) as con:
            with con:
                con.execute("DELETE FROM moral_defs")
                con.executemany("INSERT INTO moral_defs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    except sqlite3.Error as e:
        print("[save] could not store moral definitions:", e)


def get_setting(name, default=None):
    """Player settings (e.g. the language) live in the meta table and survive new games and the greed wipe."""
    try:
        with _closing(_connect()) as con:
            return _get_meta(con, f"setting_{name}", default)
    except sqlite3.Error:
        return default


def set_setting(name, value):
    with _closing(_connect()) as con:
        with con:
            _set_meta(con, f"setting_{name}", value)


def mark_story_finished():
    with _closing(_connect()) as con:
        with con:
            _set_meta(con, "story_finished", 1)


def story_finished():
    try:
        with _closing(_connect()) as con:
            return _get_meta(con, "story_finished") == "1"
    except sqlite3.Error:
        return False


def soul_lost():
    try:
        with _closing(_connect()) as con:
            return _get_meta(con, "soul_lost") == "1"
    except sqlite3.Error:
        return False


def clear_soul_lost():
    with _closing(_connect()) as con:
        with con:
            con.execute("DELETE FROM meta WHERE key = 'soul_lost'")


# ---------------------------------------------------------------------------
# dict <-> tables
# ---------------------------------------------------------------------------
def _write(con, data):
    from .morality import Morality
    from .settings import STAGES
    p = data["player"]
    mdata = data.get("morality", {})
    w = data.get("world", {})
    m = Morality(mdata)
    for t in SAVE_TABLES:
        con.execute(f"DELETE FROM {t}")
    food = p.get("food", {})
    con.execute("""INSERT INTO player (id, stage, stage_name, x, y, facing, hp, mana, stamina, awake_time,
                                       hunger_time, mana_spent, food_milk, food_fish, food_meat, sun_exposure)
                   VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (p["stage"], STAGES[p["stage"]]["name"], p["x"], p["y"], p.get("facing", 1),
                 p["hp"], p["mana"], p["stamina"], p.get("awake_time", 0.0), p.get("hunger_time", 0.0),
                 p.get("mana_spent", 0.0), food.get("milk", 0), food.get("fish", 0), food.get("meat", 0),
                 p.get("sun_exposure", 0.0)))
    con.executemany("INSERT INTO abilities VALUES (?)", [(a,) for a in p.get("abilities", [])])
    con.execute("INSERT INTO morality VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (m.wild, m.madness, m.lust, m.abhorrent, m.blood_count, m.boss_choice,
                 m.corruption, m.title(), m.ending()))
    con.executemany("INSERT INTO deeds VALUES (?, ?)", list(m.deeds.items()))
    from . import morals
    defs = morals.load()
    con.executemany("INSERT INTO moral_values VALUES (?, ?, ?, ?, ?)",
                    [(k, v, defs[k].max if k in defs else None, defs[k].level if k in defs else None,
                      defs[k].name if k in defs else k) for k, v in m.values.items()])
    con.executemany("INSERT INTO flags VALUES (?)", [(f,) for f in w.get("flags", [])])
    con.executemany("INSERT INTO picked VALUES (?)", [(i,) for i in w.get("picked", [])])
    con.executemany("INSERT OR IGNORE INTO world_tiles VALUES (?, ?, 'broken')", [tuple(t) for t in w.get("broken", [])])
    con.executemany("INSERT OR IGNORE INTO world_tiles VALUES (?, ?, 'burned')", [tuple(t) for t in w.get("burned", [])])
    con.executemany("INSERT INTO altar_stock VALUES (?, ?, ?)",
                    [(a, f, n) for a, st in w.get("stock", {}).items() for f, n in st.items()])
    con.executemany("INSERT INTO hugs VALUES (?, ?)", list(w.get("hugs", {}).items()))
    _set_meta(con, "checkpoint", data.get("checkpoint", "N"))
    _set_meta(con, "world_version", data.get("world_version", 1))
    _set_meta(con, "world_time", w.get("t", 0.0))
    _set_meta(con, "last_save", _now())
    con.execute("""INSERT INTO save_history (saved_at, checkpoint, stage_name, hp, mana, corruption, nature)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (_now(), data.get("checkpoint", "N"), STAGES[p["stage"]]["name"], p["hp"], p["mana"],
                 m.corruption, m.title()))


def _read(con):
    row = con.execute("""SELECT stage, x, y, facing, hp, mana, stamina, awake_time, hunger_time, mana_spent,
                                food_milk, food_fish, food_meat, sun_exposure FROM player WHERE id = 1""").fetchone()
    if not row:
        return None
    (stage, x, y, facing, hp, mana, stamina, awake, hunger, spent, milk, fish, meat, sun) = row
    player = dict(stage=stage, x=x, y=y, facing=facing, hp=hp, mana=mana, stamina=stamina,
                  awake_time=awake, hunger_time=hunger, mana_spent=spent, sun_exposure=sun or 0.0,
                  food=dict(milk=milk, fish=fish, meat=meat),
                  abilities=[r[0] for r in con.execute("SELECT name FROM abilities ORDER BY name")])
    mrow = con.execute("SELECT wild, madness, lust, abhorrent, blood_count, boss_choice FROM morality").fetchone()
    morality = {}
    if mrow:
        morality = dict(wild=mrow[0], madness=mrow[1], lust=mrow[2], abhorrent=mrow[3],
                        blood_count=mrow[4], boss_choice=mrow[5])
    morality["deeds"] = {d: a for d, a in con.execute("SELECT deed, amount FROM deeds")}
    morality["values"] = {k: v for k, v in con.execute("SELECT moral, value FROM moral_values")}
    stock = {}
    for altar, food, n in con.execute("SELECT altar, food, amount FROM altar_stock"):
        stock.setdefault(altar, {})[food] = n
    world = dict(
        flags=sorted(r[0] for r in con.execute("SELECT flag FROM flags")),
        picked=sorted(r[0] for r in con.execute("SELECT item_id FROM picked")),
        broken=[[x, y] for x, y in con.execute("SELECT x, y FROM world_tiles WHERE change = 'broken'")],
        burned=[[x, y] for x, y in con.execute("SELECT x, y FROM world_tiles WHERE change = 'burned'")],
        stock=stock,
        hugs={c: n for c, n in con.execute("SELECT creature_id, count FROM hugs")},
        t=float(_get_meta(con, "world_time", 0.0)),
    )
    return dict(player=player, morality=morality, checkpoint=_get_meta(con, "checkpoint", "N"), world=world,
                world_version=int(_get_meta(con, "world_version", 1)))


# ---------------------------------------------------------------------------
class _closing:
    def __init__(self, con):
        self.con = con

    def __enter__(self):
        return self.con

    def __exit__(self, *exc):
        self.con.close()


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def describe():
    """Readable overview of the current save (python -m src.save)."""
    lines = [f"Datenbank: {DB_FILE}"]
    with _closing(_connect()) as con:
        for table in ("meta",) + SAVE_TABLES + ("moral_defs",):
            rows = con.execute(f"SELECT * FROM {table}").fetchall()
            cols = [c[1] for c in con.execute(f"PRAGMA table_info({table})")]
            lines.append(f"\n[{table}]  ({len(rows)} Zeilen)")
            for r in rows[:30]:
                lines.append("  " + ", ".join(f"{c}={v}" for c, v in zip(cols, r)))
        hist = con.execute("SELECT saved_at, checkpoint, stage_name, corruption, nature FROM save_history "
                           "ORDER BY id DESC LIMIT 10").fetchall()
        lines.append("\n[save_history]  (letzte 10)")
        lines += [f"  {r[0]}  {r[1]:<4} {r[2]:<20} Korruption={r[3]}  {r[4]}" for r in hist]
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
