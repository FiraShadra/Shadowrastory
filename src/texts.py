"""All in-game text in one place. This file is the German original (like the story notes);
texts_en.py holds the English version with the same names. set_language() switches between them
at runtime – every module reads texts.X when it needs it, so the switch applies everywhere."""

# zone key -> banner name (the positions live in world.ZONES)
ZONE_NAMES = {
    "nest": "Das Nest",
    "river": "Flusstal",
    "meadow": "Sonnenwiesen",
    "vale": "Tal der Schattensteine",
    "canyon": "Aufwindschlucht",
    "cliff": "Klippe der Stürme",
    "grove": "Elfenhain",
    "ruins": "Ruinen des Lichts",
    "plateau": "Gleißende Hochebene",
    "lava": "Lavameer",
    "summit": "Mafors Gipfel",
    "frostpass": "Frostpass",
    "snowfield": "Schneefelder",
    "icecave": "Eishöhle",
    "snowvillage": "Dorf im Schnee",
    "frozenlake": "Frostsee",
    "underwater": "Unter dem Frostsee",
    "northcliff": "Nordklippe",
}

# ---------------------------------------------------------------------------
# Daylight
# ---------------------------------------------------------------------------
SUN_INTRO = {
    "meadow": [
        ("", "Zum ersten Mal sieht Shadowra den offenen Himmel bei Tag. Das Licht brennt auf ihren Schuppen."),
        ("Hinweis", "Tageslicht verbrennt sie. Versteck dich im Schatten von Bäumen, Felsen und Wolken – "
                    "im Wasser – oder nimm die dunklen Gänge unter der Erde."),
        ("Hinweis", "Jede Sekunde im Licht schmerzt. Aber ihr Körper gewöhnt sich daran. (Lichtgewöhnung)"),
    ],
    "vale": [
        ("", "Hinter den Wiesen öffnet sich ein weites Tal voller Licht. Ganz im Osten ragt eine Felswand auf – "
             "mit einem schwarzen Tor darin."),
        ("", "In alten Drachensagen heißt es: Drei Schattensteine schlafen in diesem Tal. Nur wer sie alle weckt, "
             "dem öffnet sich das Schattentor."),
        ("Hinweis", "Finde die drei Schattensteine: in der Höhle unter dem Hügel, auf der Insel im See und oben auf dem Tafelberg. "
                    "(E am Stein)"),
    ],
    "plateau": [
        ("", "Die Hochebene gleißt im Licht. Kein Baum, keine Wolke. Nur alte Tempeldächer und schwebende Felsen werfen Schatten."),
        ("Hinweis", "Im Licht frisst der Schattenschleier ihr Mana. Je mehr sie sich ans Licht gewöhnt, desto weniger."),
        ("Hinweis", "Ein Sonnenschrein steht mitten im Licht. Wer dort ausharrt, lernt das Licht schneller zu ertragen – "
                    "aber es brennt."),
    ],
}
STONE_NAMES = {"stone_cave": "Höhlenstein", "stone_lake": "Seestein", "stone_mesa": "Gipfelstein"}
STONE_PROMPT = "[E] Schattenstein wecken"
STONE_WAKE = "Shadowra legt ihre Klaue auf den {name}. Violette Runen erwachen.  ({n}/3)"
STONE_AWAKE = "Der {name} ist bereits erwacht."
GATE_OPEN = [
    ("", "Weit im Osten grollt der Fels. Alle drei Schattensteine glühen – und das Schattentor sinkt in die Erde."),
]
GATE_CLOSED = "Das Schattentor ist verschlossen. Drei Schattensteine müssen erwachen ({n}/3)."
BURROW_IN = "In den Erdbau kriechen (dunkler Tunnel)"
BURROW_OUT = "Hinaus ins Licht"
SHRINE_NAME = "Sonnenschrein"
SHRINE_PROMPT = "Ein alter Schrein, golden und heiß. Das Licht hier ist fast unerträglich."
SHRINE_MENU = ["Im Licht ausharren (Lichtgewöhnung)", "Gehen"]
SHRINE_ENDURE = "Shadowra senkt ihren Schleier und hält dem Licht stand. Es brennt – und sie wird stärker."
SHRINE_STOP = "Shadowra taumelt aus dem Licht. Mehr erträgt sie gerade nicht."

START_WARNING = [
    "Shadowra ist kein Werkzeug. Sie ist ein lebendes Wesen.",
    "",
    "Sie wird müde. Sie hat Hunger. Sie muss schlafen.",
    "Ihre Kraft kommt nicht aus dem Nichts.",
    "",
    "Jede Entscheidung, zu der du sie zwingst, formt ihre Seele.",
    "Zwingst du sie zu Taten, die sie verabscheut, oder treibst du sie",
    "zu tief in die Gier, so wird dein Spielstand am Ende",
    "unwiederbringlich GELÖSCHT.",
    "",
    "[Enter] Ich habe verstanden",
]

INTRO = [
    ("", "Tief unter der Erde, in einem Nest aus Wurzeln und Schatten, öffnet eine kleine Drachin die Augen."),
    ("", "Ihr Name ist Shadowra. Sie ist ein Kind der Finsternis – und Licht verbrennt sie."),
    ("", "Hoch über der Welt herrscht der Lichttyrann Mafor. Er hat Fira gefangen genommen, den einzigen, der je zu ihr hielt."),
    ("", "Doch Shadowra ist noch so klein. Erst muss sie wachsen."),
    ("Hinweis", "Am Nest (E) kann sie trinken und schlafen. Schlaf füllt ihr Mana und speichert das Spiel."),
]

STAGE_UP = {
    1: [("", "Im Schlaf streckt sich Shadowras Körper. Ihre Schuppen werden härter, ihre Flügel länger."),
        ("", "Sie ist jetzt eine Jungdrachin. Milch stillt ihren Hunger nicht mehr – sie braucht Fisch."),
        ("Hinweis", "Fang Fische mit den Klauen (J), wenn sie im Wasser schwimmen.")],
    2: [("", "Shadowra erwacht – und der Schatten, den sie wirft, ist gewaltig."),
        ("", "Sie ist eine ausgewachsene Finsternis-Drachin. Ihr Körper verlangt nun nach Fleisch."),
        ("", "Ihre Magie hat sie gelehrt, was ihr Körper nun halten kann: Ihre Zauber treffen härter, "
             "und je öfter sie ihr Mana genutzt hat, desto größer ist ihr Vorrat."),
        ("Hinweis", "Ihre Schwingen sind stark genug. Drücke in der Luft die Leertaste für einen Flügelschlag.")],
}
FLY_NOT_SEEN = ("", "Ihre Schwingen wären stark genug... aber sie weiß noch nicht, wie man richtig fliegt. "
                    "Vielleicht kann sie es irgendwo abschauen.")

BIRDS = [
    ("", "Durch eine Öffnung in der Höhlendecke sieht Shadowra Schattenvögel, die lautlos durch die Dämmerung segeln."),
    ("", "Sie breitet ihre winzigen Flügel aus. Etwas in ihr erwacht."),
    ("Neu", "Shadowra hat das Gleiten verstanden.  (Leertaste in der Luft halten)"),
]
STORM_DRAGON = [
    ("", "Über der Klippe zieht ein gewaltiger Drache durch den Sturm. Jeder Flügelschlag ist ruhig und mächtig."),
    ("", "Shadowra sieht ihm nach, bis er in den Wolken verschwindet. Sie hat verstanden, wie man fliegt."),
]
STORM_DRAGON_YOUNG = ("Neu", "Noch sind ihre Flügel zu schwach. Doch wenn sie ausgewachsen ist, wird sie fliegen können.")
STORM_DRAGON_ADULT = ("Neu", "Shadowra kann jetzt fliegen!  (Leertaste in der Luft: Flügelschlag – kostet viel Ausdauer)")

# (ability names and descriptions live in src/world/<place>/abilities.json – see src/abilities.py)

BLOOD_LEARNED = [
    ("", "Shadowra blutet. Ihr Blick verschwimmt. Und plötzlich ist da ein Instinkt, den sie nie wollte."),
    ("", "Blut. Das Leben anderer könnte ihr Mana und Kraft schenken."),
    ("Neu", "Blut-Sog erlernt (U nahe einem geschwächten oder gefallenen Wesen). Shadowra hasst es."),
    ("Warnung", "Jedes Mal, wenn du sie dazu zwingst, verändert es sie."),
]
BLOOD_MSG = {
    "peaceful": "Shadowra zögert... und beißt zu. Ein leises Wimmern entweicht ihr.",
    "priest": "Das Blut des Priesters brennt in ihrer Kehle. Etwas in ihr will mehr davon.",
    "fish": "Das kalte Blut des Fisches. Es fühlt sich beinahe natürlich an.",
    "elf": "Elfenblut. Es schmeckt nach Mondlicht – und nach Verrat.",
    "human": "Menschenblut. Warm und salzig – und alles in ihr schreit, dass es falsch ist.",
    "greedy": "Sie bräuchte es nicht einmal. Sie tut es trotzdem.",
}

# ---------------------------------------------------------------------------
# Age-dependent text: any entry may be a dict keyed by her age; aged() picks the right one.
# ---------------------------------------------------------------------------
AGE = {0: "hatchling", 1: "juvenile", 2: "adult"}


def aged(entry, stage):
    """Return the variant of a text entry for Shadowra's age (falls back to the nearest younger one)."""
    if isinstance(entry, dict) and set(entry) & set(AGE.values()):
        for s in range(stage, -1, -1):
            if AGE[s] in entry:
                return entry[AGE[s]]
        return next(iter(entry.values()))
    return entry


OWL_NAME = "Alte Eule Morwen"
OWL = {
    "first": {
        "juvenile": [
            (OWL_NAME, "Huu... ein Drachenkind, so weit draußen? Fürchte dich nicht, Kleine."),
            (OWL_NAME, "Im Fluss gibt es Fische genug. Fang sie mit den Klauen, solange sie im Wasser sind."),
            (OWL_NAME, "Östlich liegen die Sonnenwiesen. Bei Tag brennt dort das Licht. Bleib im Schatten der Bäume, "
                       "warte auf die Wolken – oder nimm die alten Gänge unter der Erde."),
            (OWL_NAME, "Dahinter liegt ein weites Tal mit einem schwarzen Tor. Drei alte Steine schlafen dort – "
                       "in einer Höhle, auf einer Insel und hoch oben auf dem Tafelberg."),
            (OWL_NAME, "Und hinter dem Tor die Schlucht. Die warmen Winde dort tragen dich, wenn du nur gleitest."),
            (OWL_NAME, "Und vergiss nie: Schatten ist dein Freund, Licht ist dein Feind."),
        ],
        "adult": [
            (OWL_NAME, "Huu! Bei allen Sternen – eine ausgewachsene Finsternis-Drachin! ...Bitte friss mich nicht."),
            (OWL_NAME, "Du willst mir nichts tun? Na dann... Ich bin Morwen. Ich sitze schon ewig auf diesem Ast."),
            (OWL_NAME, "Östlich liegen die Sonnenwiesen. Das Licht brennt dort bei Tag – sogar eine so Große wie dich."),
            (OWL_NAME, "Und vergiss nie: Schatten ist dein Freund, Licht ist dein Feind."),
        ],
    },
    # when she comes back
    "greet": {
        "juvenile": (OWL_NAME, "Huu, da bist du ja wieder, Kleine. Hast du genug gefressen?"),
        "adult": (OWL_NAME, "Ah, meine große Drachin. Schön, dass du mich nicht vergisst."),
    },
    # she visited as a young dragon and now comes back grown
    "grew": [
        (OWL_NAME, "Oh, hallo, du Große! Du bist zu mir zurückgekommen."),
        (OWL_NAME, "Huu... als du das letzte Mal hier warst, warst du kaum größer als ich. Und jetzt sieh dich an!"),
    ],
    "gift": {
        "juvenile": (OWL_NAME, "Hier, nimm diesen Fisch. Du siehst hungrig aus."),
        "adult": (OWL_NAME, "Ich hätte da einen Fisch... für eine so große Drachin wohl nur ein Happen. Nimm ihn trotzdem."),
    },
    "hint_veil": (OWL_NAME, "Auf der Klippe der Stürme soll ein Schleier aus Finsternis liegen. Ohne ihn kommst du nie über das Lavameer."),
    "hint_fish": (OWL_NAME, "Du bist noch zu klein für das Lavameer. Iss Fisch, schlaf gut – dann wirst du wachsen."),
    "hint_fire": (OWL_NAME, "In den Ruinen ruht ein dunkles Feuer. Hinter brüchigem Stein, sagt man."),
    "hint_general": (OWL_NAME, "Ruh dich aus, wenn du kannst, Kind. Wer nie schläft, verliert irgendwann den Verstand."),
    "afraid": (OWL_NAME, "Bleib... bleib weg von mir. Deine Augen glühen so rot. Was ist nur aus dir geworden?"),
    "afraid_wild": (OWL_NAME, "Bleib weg! Du riechst nach dem Blut der Moosläufer... Was ist nur aus dir geworden?"),
    "afraid_mad": (OWL_NAME, "Mit wem sprichst du da, Kind? Da ist niemand. Da war nie jemand... Bitte, schlaf endlich."),
    "afraid_lust": (OWL_NAME, "Du lächelst, wenn du von Macht sprichst. So hat Mafor auch einmal angefangen."),
    "gone": ("", "Der Ast ist leer. Morwen ist fort – sie hat sich vor dir versteckt."),
}

# ---------------------------------------------------------------------------
# Umarmen – how creatures react to a hug
#   confused (first time) -> warming -> loves (after 3 hugs);  afraid / rejected depend on her soul;
#   cold = elves she refused to help;  again = hugged again too soon (no new points)
# ---------------------------------------------------------------------------
# first hug after she has grown since this creature last saw her (prepended to the normal reaction)
HUG_GREW = {
    "peaceful": {
        "juvenile": "Der Moosläufer schnuppert lange an ihr. Ist das wirklich das kleine Drachenkind von damals?",
        "adult": "Der Moosläufer schaut ganz weit nach oben. Das winzige Drachenkind von damals – jetzt ein Riese.",
    },
    "owl": (OWL_NAME, "Huu! Als du mich das letzte Mal gedrückt hast, warst du noch so klein..."),
    "Sera": ("Sera", "Moment – du bist ja noch größer geworden! Wie viel frisst du eigentlich?"),
    "Erila": ("Erila", "Du bist gewachsen, Kleine... nein, Große. Daran muss ich mich erst gewöhnen."),
}
HUG_MENU = {
    "talk": "Sprechen", "hug": "Umarmen", "nuzzle": "Anschmiegen", "leave": "Gehen", "leave_be": "In Ruhe lassen",
}
HUG_PROMPT = "Was möchte Shadowra tun?"
HUG_NAMES = {"peaceful": "Moosläufer", "owl": "Alte Eule Morwen"}
HUGS = {
    # every entry can be a plain text or a dict by age (hatchling / juvenile / adult)
    "peaceful": {
        "confused": {
            "hatchling": "Der Moosläufer beschnuppert das winzige Drachenkind – und bleibt verwirrt stehen.",
            "juvenile": "Der Moosläufer erstarrt. Er weiß nicht, was diese Drachin von ihm will...",
            "adult": "Der Moosläufer erstarrt unter den riesigen Schwingen. Wird er gefressen – oder umarmt?",
        },
        "warming": {
            "hatchling": "Der Moosläufer stupst das Drachenkind sanft mit der Nase an.",
            "juvenile": "Der Moosläufer zögert – dann lehnt er sich vorsichtig an Shadowra.",
            "adult": "Der Moosläufer lehnt sich an die große Drachin wie an einen warmen Felsen.",
        },
        "loves": {
            "hatchling": "Der Moosläufer legt sich neben das Drachenkind und wärmt es mit seinem Moosfell.",
            "juvenile": "Der Moosläufer drückt sich an sie und brummt zufrieden.",
            "adult": "Der Moosläufer kuschelt sich unter ihre Flügel. Dort fühlt er sich sicher.",
        },
        "afraid": "Der Moosläufer zittert am ganzen Körper, bis sie ihn loslässt.",
        "rejected": "Der Moosläufer reißt sich panisch los und flieht.",
        "again": {
            "hatchling": "Der Moosläufer lässt das Drachenkind auf seinem Rücken dösen.",
            "juvenile": "Der Moosläufer genießt die Umarmung.",
            "adult": "Der Moosläufer verschwindet fast ganz in ihrer Umarmung – und genießt es.",
        },
    },
    "owl": {
        "confused": {
            "juvenile": "Huu?! Was... was tust du da, Kind? ...Oh. Du willst nur kuscheln.",
            "adult": "Huu!! Vorsicht, Große – du zerdrückst mich ja! ...Oh. Du willst nur kuscheln.",
        },
        "warming": {
            "juvenile": "Huhu... na komm her. Deine Schuppen sind ganz warm.",
            "adult": "Huhu... so viel Drache, so viel Wärme. Na komm, aber vorsichtig.",
        },
        "loves": {
            "juvenile": "Meine kleine Drachin! Du hast mir gefehlt.",
            "adult": "Oh, hallo, du Große! Du bist zu mir zurückgekommen. Du hast mir gefehlt.",
        },
        "afraid": {
            "juvenile": "B-bitte... lass mich los. Ich weiß nicht mehr, wer du bist.",
            "adult": "B-bitte... du bist so groß geworden. Und so dunkel. Lass mich los.",
        },
        "rejected": "Huu! Weg von mir!",
        "again": {
            "juvenile": "Huu~ Schon wieder? Na gut.",
            "adult": "Huu~ Schon wieder? Na gut – aber lass mir ein paar Federn.",
        },
    },
    "Sera": {
        "accepts": {          # women accept the first hug (Sera in her own prickly way)
            "juvenile": "He! ...Ach, na komm schon her. Aber erzähl das niemandem.",
            "adult": "Du bist doppelt so groß wie ich – und kuschelst trotzdem? ...Na komm schon her.",
        },
        "confused": {
            "juvenile": "He! Was soll das, Drachin?! ...Na schön. Aber nur kurz.",
            "adult": "He! Du bist doppelt so groß wie ich, Drachin! ...Na schön. Aber nur kurz.",
        },
        "warming": {
            "juvenile": "Du bist ganz schön anhänglich, weißt du das?",
            "adult": "Du bist riesig geworden – und trotzdem so anhänglich.",
        },
        "loves": {
            "juvenile": "Komm her, du Schuppenknäuel.",
            "adult": "Komm her, du großes Schuppenknäuel.",
        },
        "afraid": "Lass das. Ich traue dir nicht.",
        "rejected": "Fass mich nicht an, Bestie!",
        "cold": "Jetzt willst du kuscheln? Nachdem du uns im Stich gelassen hast?",
        "again": "Schon wieder? ...Ich beschwer mich ja gar nicht.",
    },
    "Erila": {
        "accepts": {
            "juvenile": "Oh! Komm her, du Liebe. Du bist ja ganz warm.",
            "adult": "Oh! Komm her... so groß und so warm. Das tut gut.",
        },
        "confused": {
            "juvenile": "Oh! Du bist... überraschend warm.",
            "adult": "Oh! Du bist so groß... und so warm.",
        },
        "warming": {
            "juvenile": "Du suchst Nähe, nicht wahr? Das ist nichts Schlechtes.",
            "adult": "Du bist gewachsen, aber dein Herz ist dasselbe geblieben.",
        },
        "loves": {
            "juvenile": "Ich hab dich auch gern, Kleine.",
            "adult": "Ich hab dich auch gern, Große.",
        },
        "afraid": "Ich... spüre so viel Dunkelheit in dir.",
        "rejected": "Nein... bitte nicht.",
        "cold": "Wir sind dir nichts schuldig. Und du uns auch nicht.",
        "again": "Mhm. Bleib ruhig noch einen Moment.",
    },
}

# ---------------------------------------------------------------------------
# Elfendorf – the villagers. gender "f"/"m" decides how they take her FIRST hug:
#   women accept it warmly ("accepts"), men blush and stammer ("blush").
# ---------------------------------------------------------------------------
VILLAGERS = {
    "Lyria": dict(gender="f", style=dict(hair=(240, 196, 110), cloth=(150, 80, 140), trim=(236, 190, 220),
                                         skin=(240, 220, 204), boots=(90, 50, 80), eyes=(120, 60, 140),
                                         hair_style="long", outfit="dress"),
                  first="Oh! Du bist ja ganz warm! Komm her, du Süße – ich lass dich gar nicht mehr los.",
                  talk=["Die Dorfälteste sagt, Drachen bringen Glück. Ich glaube ihr jetzt.",
                        "Magst du Mondblumen? Ich flechte dir einen Kranz – irgendwann, wenn du stillhältst."]),
    "Naela": dict(gender="f", style=dict(hair=(70, 40, 30), cloth=(60, 120, 120), trim=(170, 230, 210),
                                         skin=(214, 180, 150), boots=(50, 60, 50), eyes=(40, 100, 80),
                                         hair_style="braid", outfit="dress"),
                  first="Hihi, deine Schuppen kitzeln! Na komm, drück mich ruhig fester.",
                  talk=["Ich hüte die Pilze am Teich. Sie leuchten heller, seit du hier warst.",
                        "Sera tut immer so streng. Dabei redet sie den ganzen Tag nur von dir."]),
    "Thessa": dict(gender="f", style=dict(hair=(200, 70, 60), cloth=(180, 130, 60), trim=(250, 220, 140),
                                          skin=(236, 206, 186), boots=(100, 60, 40), eyes=(150, 90, 40),
                                          hair_style="bun", outfit="tunic"),
                   first="Oh, eine Drachenumarmung! Wie schön. Du riechst nach Nacht und Moos.",
                   talk=["Ich backe Nussbrot. Drachen essen sowas nicht, oder? Schade.",
                         "Pass auf dich auf, ja? Da draußen brennt die Sonne."]),
    "Aren": dict(gender="m", style=dict(hair=(60, 50, 44), cloth=(60, 90, 60), trim=(150, 180, 110),
                                        skin=(222, 196, 172), boots=(70, 50, 36), eyes=(60, 90, 60),
                                        hair_style="short", outfit="tunic"),
                 first="H-hey! Ich... äh... *wird bis zu den Ohrenspitzen rot* ...Das war nett. Glaub ich.",
                 talk=["Ich bin Jäger, so wie Sera. Na ja... nicht ganz so gut wie Sera.",
                       "Die Brut kommt immer aus dem Westen. Danke, dass du sie aufgehalten hast."]),
    "Calen": dict(gender="m", style=dict(hair=(226, 226, 236), cloth=(70, 80, 140), trim=(180, 190, 240),
                                         skin=(230, 214, 206), boots=(50, 50, 80), eyes=(90, 110, 190),
                                         hair_style="short", outfit="vest"),
                  first="Oh! Ich... das muss ich in ein Lied... äh... *wird knallrot und vergisst jedes Wort*",
                  talk=["Ich schreibe Lieder. Eins handelt von einer Drachin aus Schatten. Rate mal, von wem.",
                        "Erila ist meine Schwester. Sie mag dich sehr. ...Ich auch. Also, als Freund!"]),
    "Fenrik": dict(gender="m", style=dict(hair=(200, 200, 196), cloth=(96, 70, 50), trim=(200, 170, 110),
                                          skin=(220, 196, 176), boots=(60, 44, 34), eyes=(110, 110, 100),
                                          hair_style="elder", outfit="robe", weapon="staff"),
                   first="Hoho! In meinem Alter... *räuspert sich, die Wangen glühen* ...Danke, Kind. Das tat gut.",
                   talk=["Ich bin Fenrik, der Älteste. Ich habe schon Drachen gesehen, als die Sonne noch freundlich war.",
                         "Du trägst Schatten in dir, Kind – aber kein Dunkel im Herzen. Bewahre das."]),
}
VILLAGE_TALK = {
    "grew": "Bei allen Blättern – bist du etwa die kleine Drachin von damals?",
    "cold": "Du hast Sera und Erila allein kämpfen lassen. Warum sollten wir mit dir reden?",
    "wary": "Danke für deine Hilfe... aber bitte bleib ein Stück weg von den Häusern.",
}
# how villagers react to hugs; first hug depends on gender
VILLAGE_HUGS = {
    "f": {
        "accepts": {"juvenile": "Oh! Na komm her, du Süße. *drückt dich ganz fest*",
                    "adult": "Oh! So eine große Umarmung! Komm her, du Süße."},
        "warming": "Schon wieder kuscheln? Jederzeit, Kleine.",
        "loves": {"juvenile": "Meine Lieblingsdrachin! Komm her!", "adult": "Meine große Lieblingsdrachin! Komm her!"},
        "again": "Mhm... noch ein bisschen länger.",
        "afraid": "B-bitte... nicht so fest. Du machst mir Angst.",
        "rejected": "Nein! Lass mich los!",
        "cold": "Lass das. Nach dem, was du getan hast...",
    },
    "m": {
        "blush": {"juvenile": "Ä-äh... ich... das ist... *wird knallrot* ...Danke?",
                  "adult": "W-wow, du bist... groß. Und warm. Ich... *wird knallrot und starrt auf seine Füße*"},
        "warming": "*räuspert sich* Du schon wieder... Na gut. Aber nur kurz. *wird schon wieder rot*",
        "loves": "Okay, ich geb's zu. Ich mag deine Umarmungen. Sag's bloß nicht Sera.",
        "again": "*hüstel* Ja... ja, ist gut. Ist schön.",
        "afraid": "H-halt! Bitte... du bist mir unheimlich.",
        "rejected": "Weg da! Fass mich nicht an!",
        "cold": "Nein danke. Du hast uns im Stich gelassen.",
    },
}

ALTAR_NAMES = {
    "N": "Das Nest",
    "M": "Mondmilch-Quelle",
    "A1": "Flussaltar",
    "A2": "Schrein der Ruinen",
    "A3": "Schatteninsel",
    "A4": "Letzte Rast",
    "A5": "Felsbogen",
    "A6": "Tempelschatten",
    "A7": "Rast am See",
    "A8": "Höhlenquelle",
    "A9": "Torschatten",
    "E": "Dorfbrunnen der Elfen",
}
FOOD_NAMES = {"milk": "Milch", "fish": "Fisch", "meat": "Fleisch"}
CANT_EAT = {
    "fish": "Ihr Magen verträgt noch keinen Fisch.",
    "meat": "Fleisch ist noch viel zu zäh für sie.",
    "milk": "Milch stillt ihren Hunger nicht mehr.",
}

NO_RETURN_GREED = [
    ("???", "Die Finsternis in dir ist nun zu dicht."),
    ("???", "Deine Taten haben Shadowra korrumpiert. Gehst du weiter, verlierst du alles."),
]
NO_RETURN_CLOSE = [
    ("???", "Du stehst am Rand des Abgrunds. Noch eine grausame Tat, und es gibt keinen Weg zurück."),
]
LAST_REST = ("", "Der Wind trägt Firas Ruf herüber. Mafor wartet hinter dem Kamm.")

BOSS_INTRO = [
    ("Mafor", "Ein Kind der Finsternis wagt es, in mein Licht zu treten?"),
    ("Mafor", "Ich werde dich verbrennen, wie ich alle deinesgleichen verbrannt habe."),
]
BOSS_DEFEATED = [("Mafor", "Mein... Licht... Verschone mich, Drache. Ich flehe dich an.")]
BOSS_CHOICE = ["Verschonen", "Verschlingen"]
BOSS_SPARED = ("", "Shadowra wendet sich ab. Mafor flieht in die Tiefe, ein gebrochener, erloschener Mann.")
BOSS_DEVOURED = ("", "Shadowra verschlingt das letzte Licht des Tyrannen. Eine unbekannte Macht durchströmt sie. Sie genießt es.")

ENDINGS = {
    "light": dict(
        title="Licht in der Finsternis",
        lines=[
            ("Fira", "Shadowra! Du bist gekommen..."),
            ("", "Fira sieht in ihre Augen – und sieht dieselbe sanfte Drachin, die er einst kannte."),
            ("Fira", "Du hast all das überlebt, ohne dich selbst zu verlieren."),
            ("", "Zusammen fliegen sie in die erste Nacht, die wieder ihnen gehört."),
        ],
        footer="KAPITEL 1 – ENDE  ·  Du hast Shadowras Herz bewahrt.",
    ),
    "redemption": dict(
        title="Der Weg zurück",
        lines=[
            ("Fira", "Shadowra...? Du... du bist es, oder?"),
            ("", "Fira weicht einen Schritt zurück. Das Blut an ihren Klauen ist noch nicht getrocknet."),
            ("Fira", "Du hast dich verloren, um mich zu retten."),
            ("Fira", "Dann bringe ich dich jetzt zurück. Egal wie lange es dauert."),
        ],
        footer="KAPITEL 1 – ENDE  ·  Shadowras Weg zur Erlösung beginnt erst.",
    ),
    "madness": dict(
        title="Stimmen im Schatten",
        lines=[
            ("Fira", "Shadowra, ich bin es! Fira!"),
            ("Shadowra", "...die Schatten sagen, du bist nicht echt. Die Schatten lügen nie."),
            ("", "Sie erkennt ihn nicht mehr. Als die Stimmen schreien, schlägt sie zu – und Fira fällt."),
            ("", "Lange sitzt sie neben ihm im Wind. Dann zieht sie allein weiter nach Norden."),
            ("Shadowra", "Irgendwo dort wartet jemand Neues auf mich. Die Schatten haben es versprochen."),
        ],
        footer="KAPITEL 1 – ENDE  ·  Shadowras Verstand ist zerbrochen.",
    ),
    "obsession": dict(
        title="Die neue Tyrannin",
        lines=[
            ("Fira", "Shadowra, lass uns gehen. Es ist vorbei."),
            ("Shadowra", "Vorbei? Es fängt doch gerade erst an."),
            ("", "Sie errichtet ein Reich aus den Knochen ihrer Beute. Mafors Thron ist nun der ihre."),
            ("", "Und Fira? Sie sperrt ihn wieder ein. Nicht aus Hass – sondern weil sie alles besitzen will."),
            ("", "Dann blickt sie nach Norden. Dort gibt es noch so viel, das ihr gehören könnte."),
        ],
        footer="KAPITEL 1 – ENDE  ·  Die Gier nach Macht hat Shadowra verschlungen.",
    ),
    "greed": dict(
        title="",
        lines=[
            ("Fira", "Shadowra...?"),
            ("", "Fira weicht voller Entsetzen zurück. Er sieht keine Drachin mehr. Er sieht eine Bestie."),
            ("Fira", "Bleib weg von mir! Du bist nicht sie. Du bist nicht mehr sie..."),
            ("", "Etwas in Shadowra zerbricht. Leise."),
        ],
        footer="",
    ),
}
# ---------------------------------------------------------------------------
# Credits (main menu)
# ---------------------------------------------------------------------------
CREDITS_HEAD = [
    ("title", "Shadowra's Story"),
    ("sub", "Ein Survival-Metroidvania über eine kleine Finsternis-Drachin"),
    ("gap", ""),
    ("head", "Idee, Geschichte & Welt"),
    ("text", "Shadowras Schöpfer"),
    ("gap", ""),
    ("head", "Programmierung, Figuren & Welt-Bau"),
    ("text", "gemeinsam mit Claude"),
    ("gap", ""),
    ("head", "Grafik-Pakete"),
    ("text", "Multi Platformer Tileset – Shackhal (CC0)"),
    ("text", "Starry Night – Quintino Pixels"),
    ("text", "Wasteland Hintergründe"),
    ("text", "Crimson Fantasy GUI"),
    ("text", "Dungeon Character & Tileset"),
    ("gap", ""),
    ("head", "Schriften"),
    ("text", "Kalnia Glaze – Frida Medrano (OFL)"),
    ("gap", ""),
    ("head", "Engine"),
    ("text", "Python & pygame"),
    ("gap", ""),
]
CREDITS_JOURNEY = "Shadowras Reise bisher"
# captions in the credits replay of her journey
REPLAY_EVENTS = {
    "glide": "Gleiten gelernt",
    "storm": "Den Sturmdrachen gesehen – Fliegen verstanden",
    "relic": "Gefunden: {name}",
    "blood": "Blut-Sog erwacht",
    "grew": "Gewachsen: {name}",
    "stone": "Geweckt: {name}",
    "gate": "Das Schattentor öffnet sich",
    "elves": "Die Elfen gerettet",
    "mafor": "Mafor besiegt",
    "north": "Die Schneelande erreicht",
    "dive": "Tauchen gelernt",
    "gift": "Geschenk: {name}",
}
CREDITS_NO_SAVE = "Ihre Reise hat noch nicht begonnen. Im Nest wartet ein Ei aus Schatten..."
CREDITS_FATE_INTRO = "So könnte ihre Geschichte enden:"
CREDITS_FATES = {
    "start": "Ein kleines Drachenkind. Allein. Ihre Geschichte beginnt erst.",
    "light": "Shadowra und Fira – zusammen in der Nacht, die endlich ihnen gehört.",
    "redemption": "Fira bleibt an ihrer Seite. Noch mit Abstand. Der Weg zurück ist lang.",
    "madness": "Allein. Fira ist gefallen – sie sucht im Norden nach einer neuen Liebe, und die Stimmen begleiten sie.",
    "obsession": "Allein auf Mafors Thron. Alles gehört ihr – und niemand bleibt.",
    "greed": "Allein. Die Gier hat ihr alles genommen.",
    "lost": "Korrumpierte Seele – Durch Gier verloren.",
}
CREDITS_ELVES = "Und im Elfendorf zünden Sera und Erila eine Laterne für sie an."
CREDITS_OWL = "Morwen sitzt auf einem Ast in der Nähe und wacht über sie."
CREDITS_END = "Danke fürs Spielen."
# at the very end she comes close to the camera – if her story is not finished yet, she speaks to the player
CREDITS_CLOSEUP_UNFINISHED = "Hey, warum hörst du jetzt auf? Oder willst du mich einfach mal aus der Nähe sehen, Spieler?"
CREDITS_SKIP = "[Enter / Esc] Zurück   ·   [Leertaste halten] schneller"
GROVE_FATES = {"friends": "hat die Elfen gerettet", "wary": "hat geholfen – die Elfen bleiben vorsichtig",
               "alone": "ließ die Elfen allein kämpfen", "dead": "die Elfen sind gefallen",
               "hostile": "die Elfen fürchten sie"}

GREED_DEATH = "Du bist gestorben – durch deine eigene Gier."
GREED_SLOT = "Korrumpierte Seele – Durch Gier verloren"

DEATH = "Shadowra ist gefallen..."

# ---------------------------------------------------------------------------
# Elfenhain – Sera & Erila
# ---------------------------------------------------------------------------
SERA, ERILA = "Sera", "Erila"
GROVE = {
    "meet_trust": {
        "juvenile": [
            ("", "Zwischen leuchtenden Pilzen stehen zwei Elfen Rücken an Rücken. Aus der Dunkelheit kriechen Schattenwesen auf sie zu."),
            (SERA, "Ein Drache?! ...Nein, warte. Sie ist noch jung. Und ihre Augen sind nicht wie die der anderen."),
            (ERILA, "Kleine Drachin, die Brut des Lichttyrannen jagt uns seit Tagen. Wir halten nicht mehr lange durch."),
            (SERA, "Hilfst du uns? ...Oder gehst du einfach weiter, wie alle anderen?"),
        ],
        "adult": [
            ("", "Zwischen leuchtenden Pilzen stehen zwei Elfen Rücken an Rücken. Aus der Dunkelheit kriechen Schattenwesen auf sie zu."),
            (SERA, "Eine ausgewachsene Drachin?! Erila, hinter mich! ...Nein, warte. Ihre Augen sind nicht wie die der anderen."),
            (ERILA, "Große Drachin, die Brut des Lichttyrannen jagt uns seit Tagen. Wir halten nicht mehr lange durch."),
            (SERA, "Mit Klauen wie deinen wären wir in Sicherheit. Hilfst du uns? ...Oder gehst du einfach weiter?"),
        ],
    },
    "meet_afraid": {
        "juvenile": [
            ("", "Zwei Elfen fahren herum. Ein Pfeil zielt direkt auf Shadowras Kehle."),
            (SERA, "Keinen Schritt näher, Bestie! Ich sehe das Blut an deinen Klauen."),
            (ERILA, "Sera, warte... hinter ihr! Die Brut kommt!"),
        ],
        "adult": [
            ("", "Zwei Elfen fahren herum. Sera spannt den Bogen – ihre Hände zittern vor der riesigen Drachin."),
            (SERA, "Bleib, wo du bist, Bestie! So groß... und Blut an deinen Klauen."),
            (ERILA, "Sera, warte... hinter ihr! Die Brut kommt!"),
        ],
    },
    # she met them as a young dragon and comes back grown
    "grew": [
        (ERILA, "Bei den Sternen – du bist gewachsen! Bald passt du nicht mehr in unseren Hain."),
        (SERA, "Hm. Jetzt sieht man wenigstens, wer uns beschützt hat."),
    ],
    "meet_hostile": [
        ("", "Die Elfen sehen Shadowra – und erstarren."),
        (SERA, "Noch eine Bestie! Erila, lauf! Ich halte sie auf!"),
    ],
    "choice": ["Helfen", "Nicht helfen"],
    "choice_nuzzle": "Bei ihnen bleiben und sich anschmiegen",
    "help": [(SERA, "Dann zeig, was in dir steckt! Erila, bleib hinter uns!")],
    "decline": [(SERA, "...Natürlich. Lauf nur."), (ERILA, "Sera, konzentrier dich. Sie kommen!")],
    "nuzzle": [
        ("", "Shadowra legt die Flügel an und schmiegt ihren Kopf an Erilas Hand. Dann an Seras Schulter."),
        (ERILA, "Oh... sie will nicht kämpfen. Sie will nur bei uns sein."),
        (SERA, "Ihr Schatten legt sich um uns wie ein Mantel... Bleib bei uns, Kleine. Wir beschützen uns gegenseitig."),
        ("Hinweis", "Solange Shadowra nahe bei den Elfen bleibt, schützt ihr Schatten sie. (E bei einer Elfe: anschmiegen)"),
    ],
    "wave": "Welle {n}/{total}: Die Brut greift an!",
    "won_friends": [
        (ERILA, "Es ist vorbei... Wir leben. Dank dir."),
        (SERA, "Ich habe mich in dir geirrt, Drachin. Unser Dorf ist auch deins. Iss, ruh dich aus."),
        (ERILA, "Lass mich deine Wunden heilen. Und nimm diesen Mondtau – er füllt deine Kraft."),
    ],
    "won_nuzzle_extra": [(ERILA, "Du darfst jederzeit wiederkommen. Einfach... um bei uns zu sein.")],
    "won_alone": [
        (SERA, "Wir haben es allein geschafft. Ohne dich."),
        (ERILA, "Geh weiter, Drachin. Hier gibt es nichts für dich."),
    ],
    "won_afraid": [
        (SERA, "...Du hast uns tatsächlich geholfen."),
        (ERILA, "Nimm etwas Heilung. Aber in unser Dorf... dafür vertrauen wir dir noch nicht."),
    ],
    "dead_watched": [("", "Die letzte Elfe fällt. Shadowra hat zugesehen. Das Bild brennt sich in ihren Kopf.")],
    "dead_helped": [("", "Trotz allem – die Elfen sind gefallen. Shadowra bleibt lange bei ihnen liegen.")],
    "talk_friends": {
        "juvenile": [(SERA, "Na, Drachin? Hungrig? Das Dorf steht dir offen."),
                     (ERILA, "Pass auf dich auf da draußen. Wir denken an dich.")],
        "adult": [(SERA, "Na, große Drachin? Pass auf, dass du nicht unsere Häuser umwirfst."),
                  (ERILA, "Das Dorf steht dir offen. Wir sind froh, dich zu sehen – egal wie groß du wirst.")],
    },
    "talk_alone": {
        "juvenile": [(SERA, "Was willst du noch hier?")],
        "adult": [(SERA, "Groß geworden, ja. Aber als wir dich gebraucht haben, warst du nicht da.")],
    },
    "talk_turned": [(SERA, "Du riechst nach Blut. Du bist nicht mehr die, die uns gerettet hat. Geh.")],
    "nuzzle_again": "Shadowra schmiegt sich an {name}. Für einen Moment ist alles still.",
    "camp_locked": "Der Dorfbrunnen der Elfen. Ohne ihre Erlaubnis rührt Shadowra nichts an.",
}

GATE_HINT = ("Die Kante ist noch zu hoch für sie. Erst muss sie wachsen – "
             "{food} trinken und schlafen ({food} {have}/{need}).")

TOASTS = {
    "too_hard": "Der Stein ist zu hart für ihre Krallen.",
    "vines": "Dichte Dornenranken. Feuer könnte sie verbrennen.",
    "exhausted": "Shadowra ist erschöpft...",
    "hungry": "Shadowra hat Hunger. Ihre Ausdauer schwindet.",
    "sleepless": "Shadowra ist übermüdet. Die Schatten flüstern.",
    "crystal": "Schattenkristall gefressen  +Mana",
    "fish_eat": "Fisch gefangen und gefressen",
    "fish_young": "Der Fisch entwischt. Ihr Magen verträgt ihn noch nicht.",
    "meat_eat": "Shadowra frisst. Es schmeckt ihr nicht.",
    "no_mana": "Nicht genug Mana.",
    "no_blood": "Hier gibt es kein Blut zu rauben.",
    "saved": "Spiel gespeichert",
    "no_food": "Hier gibt es nichts mehr, das sie fressen kann.",
    "light_burn": "Das Licht verbrennt sie!",
    "need_glide": "Der Abgrund ist zu breit, um ihn zu überspringen...",
    "growth_ready": "Shadowra ist satt genug, um im Schlaf zu wachsen.",
    "sun_adapt": "Lichtgewöhnung {pct}% – ihre Schuppen halten dem Licht besser stand.",
    "mastery_young":"Manaschulung {pct}% – ihre Magie wird ihr vertrauter. Ausgewachsen wird sie davon zehren.",
    "mastery_adult": "Manaschulung {pct}% – ihr Manavorrat wächst, ihre Magie trifft härter.",
    "cozy_meal": "Shadowra rollt sich gemütlich um ihr Essen.  +Zuneigung",
    "ward": "Am Rastplatz wagt sich nichts an sie heran.",
    "cozy_hint": "Tipp: Stell sie direkt auf das Essen neben dem Altar – dann rollt sie sich gemütlich darum.",
}

# ---------------------------------------------------------------------------
# Kapitel 2 – die Schneelande (after Fira, or without him)
# ---------------------------------------------------------------------------
PASSAGE_LABELS = {"frostpass_in": "Hinab in den Frostpass (Norden)", "frostpass_out": "Hinauf zur Letzten Rast"}
SNOW = {
    "frostpass": [
        ("", "Der Tunnel ist voller Reif. Eiskalter Wind weht von Osten herein – und er riecht nach Schnee."),
    ],
    "arrive": [
        ("", "Hinter dem Frostpass liegt ein Land aus Schnee. Kein Sonnenstrahl dringt durch die Wolken – aber die Kälte beißt."),
        ("Hinweis", "Kälte zehrt an ihrer Ausdauer, und ist die leer, an ihrem Leben. Wärme findet sie an Herdfeuern."),
    ],
    "arrive_fira": ("Fira", "Schnee! Ich habe seit Jahren keinen Schnee gesehen. Bleib dicht bei mir, ja?"),
    "arrive_mad": ("Shadowra", "...die Schatten sagen, im Norden wartet jemand. Jemand Neues."),
    "arrive_caged": ("Shadowra", "Fira wartet in seinem Käfig. Er läuft mir nicht weg. Der Norden schon."),
    "grief": [
        ("", "Am Rand des Schnees bleibt Shadowra stehen. Hinter ihr, hoch über den Wolken, sitzt Fira noch immer in seinem Käfig."),
        ("", "Sie geht trotzdem weiter. Die Trauer legt sich wie Eis auf ihr Herz."),
        ("Hinweis", "Trauer: fast alles fällt ihr schwerer – bis sie Fira befreit."),
    ],
    "cold_hint": "Die Kälte zehrt an ihr. Wärme findet sie am Herdfeuer – oder ihre Schuppen müssen härter werden.",
    "cold_hurt": "Die Kälte frisst sich in ihre Knochen!",
    "warm": "Das Herdfeuer wärmt sie.",
    "otters": [
        ("", "Am Loch im Eis tauchen Otter auf, schütteln sich – und verschwinden wieder in der Tiefe."),
        ("", "Shadowra sieht ihnen lange zu. Sie hält die Luft an. Sie versteht."),
        ("Neu", "Tauchen gelernt.  (S im tiefen Eiswasser halten – der Atem reicht nicht ewig)"),
    ],
    "deep_no_dive": "Das Eiswasser ist zu tief – ihr Körper treibt immer wieder nach oben.",
    "breath_low": "Ihr geht die Luft aus!",
    "melt_hint": "Eine Wand aus klarem Eis. Feuer könnte sie schmelzen.",
    "north": [
        ("", "Hinter der Nordklippe führt ein schmaler Pfad weiter in den Schnee. Was dort wartet, weiß noch niemand."),
        ("", "Fortsetzung folgt..."),
    ],
    "north_fira": ("Fira", "Wohin auch immer dieser Weg führt – wir gehen ihn zusammen."),
    "north_mad": ("Shadowra", "Irgendwo dort draußen wartet jemand, der mich ansieht. Die Schatten haben es versprochen."),
    "ash_wings": ("", "Die Hitze des Lavameers hat ihre Flügel gehärtet."),
    "moon_dew": ("Erila", "Nimm diesen Mondtau mit. Wenn du schläfst, schenkt er dir Kraft."),
}
FIRA_TALK = [
    ("Fira", "Ich dachte, ich sehe den Himmel nie wieder. Und jetzt fliege ich neben dir."),
    ("Fira", "Du bist so groß geworden. Damals warst du kaum mehr als ein Schatten mit Flügeln."),
    ("Fira", "Wenn dir kalt wird, rück näher. Ich bin warm genug für zwei."),
    ("Fira", "Ich weiß nicht, was im Norden wartet. Aber ich habe keine Angst – du bist ja da."),
]
# the humans in the snow (src/humans.py). gender and looks: src/world/snowylands/snowyvillage
HUMANS = {
    "Mira": dict(first="Oh! Du bist ja warm wie ein Ofen! Komm her – ich lass dich gar nicht mehr los.",
                 talk=["Ein Drache, der nicht beißt? Meine Großmutter hätte mir das nie geglaubt.",
                       "Der Winter dauert hier neun Monde. Bleib, solange du willst."]),
    "Bjarn": dict(first="H-he! Ich... äh... *wird unter dem Fellkragen knallrot* ...Pass auf meinen Speer auf.",
                  talk=["Ich jage Schneehasen. Du jagst... was jagst du eigentlich?",
                        "Bleib vom Eis weg, wenn es knackt. Der Frostsee hat schon viele geholt."]),
    "Hanne": dict(first="Hihi, deine Schuppen sind kalt und warm zugleich. Wie geht das?",
                  talk=["Die Otter am Frostsee tauchen bis ganz nach unten. Was sie da wohl finden?",
                        "Ich nähe dir eine Decke. Eine sehr, sehr große Decke."]),
    "Gunnar": dict(first="Hoho! In meinem Alter umarmt mich noch ein Drache... *räuspert sich gerührt* Danke, Kind.",
                   talk=["Ich bin Gunnar, der Älteste. Solange das Herdfeuer brennt, ist dieses Dorf sicher.",
                         "Man sagt, in der Eishöhle schlägt ein Herz aus Frost. Wer es findet, friert nie wieder."]),
    "Tomas": dict(first="W-was... das... *wird so rot, dass der Schnee um ihn fast schmilzt* ...Okay.",
                  talk=["Ich war noch nie hinter der Nordklippe. Niemand war das.",
                        "Wenn du Fisch willst: am Frostsee, durch das Loch im Eis."]),
    "Ylva": dict(first="Oh, wie schön! Eine Drachenumarmung im Schnee. Das erzähle ich allen.",
                 talk=["Die Kinder wollen wissen, ob du Feuer speien kannst. Ich habe gesagt: nur dunkles.",
                       "Komm ans Herdfeuer, wenn dir kalt ist. Für dich ist immer Platz."]),
}
HUMAN_TALK = {
    "wary": "...Bleib bitte da drüben stehen, Drache. Wir wollen keinen Ärger.",
    "hostile": ["Da ist die Bestie! Zu den Speeren!", "Sie hat Blut an den Klauen! Haltet sie auf!",
                "Treibt sie zurück in die Berge!"],
    "fira": "Zwei Drachen... und sie sind freundlich? Das glaubt uns keiner.",
    "elder_gift": [
        ("Gunnar", "Du hast uns nichts getan, obwohl du es gekonnt hättest. Das vergisst ein Dorf nicht."),
        ("Gunnar", "Nimm etwas von der Wärme unseres Herdes mit dir. Sie soll dich draußen im Schnee begleiten."),
    ],
    "locked": "Der Herd der Menschen. Ohne ihr Vertrauen rührt Shadowra nichts an.",
}

# Moral paths: title per tier (index 0 = path not taken / fallback)
PATHS = {
    "gentle": ["Unsicher", "Sanftmütig", "Reines Herz"],
    "wild": ["", "Unruhig", "Wild", "Bestie"],
    "madness": ["", "Übermüdet", "Paranoid", "Wahnsinnig"],
    "lust": ["", "Machthungrig", "Im Machtrausch", "Verschlungen"],
}

# Subpaths: (name, description) – which branch of a path her deeds pushed her down
SUBPATHS = {
    "calm_breath": ("Ruhige Atmung", "Sie atmet ruhig – Rennen und Fliegen strengen sie weniger an."),
    "trusted": ("Vertrauen", "Die Welt vertraut ihr – Nahrung heilt sie besser."),
    "strength": ("Raubtier", "Klauen statt Herz. Beute flieht, Nahrung sättigt nicht – sie will nur jagen."),
    "flight": ("Flügelschlag", "Sie jagt aus der Luft. Ihre Schwingen tragen sie, doch ihr Körper zehrt aus."),
    "sleepless": ("Schlaflos", "Sie findet keinen Schlaf mehr, und die Welt beginnt sie zu belügen."),
    "horror": ("Grauen", "Sie sieht Dinge, die nicht da sind, und ihr Fokus zerreißt."),
    "twisted": ("Zerrissen", "Verfolgt von dem, was sie gesehen und getan hat. Ihr Verstand franst aus."),
    "greedy": ("Gierig", "Sie nimmt mehr, als sie braucht. Nichts macht sie mehr satt."),
    "wanting": ("Besessen", "Sie giert nach der Macht anderer. Körper und Herz zahlen dafür."),
    "overflowing": ("Überfluss", "Mehr Macht, als ihr Körper halten kann – sie sickert aus ihr heraus."),
    "affection": ("Zuneigung", "Sie sucht Nähe – zu Fira und zu allen, die sie an sich heranlassen."),
}

DOOMED_TITLE = "Verloren"

# Effects of the moral paths: (name, description)
EFFECTS = {
    "calm_breath": ("Ruhiger Atem", "Rennen und Fliegen kosten weniger Ausdauer."),
    "deep_rest": ("Tiefe Ruhe", "Ihre Ausdauer kehrt schneller zurück."),
    "trusted": ("Geborgenheit", "Nahrung heilt sie besser."),
    "gentle_presence": ("Sanfte Nähe", "Friedliche Wesen fliehen später vor ihr."),
    "skittish_prey": ("Scheue Beute", "Friedliche Wesen fliehen schon von Weitem."),
    "predator": ("Scharfe Klauen", "Ihre Klauen reißen tiefer."),
    "wild_hunger": ("Wilder Hunger", "Normale Nahrung sättigt sie kaum noch."),
    "hunting_frenzy": ("Jagdrausch", "Noch härtere Hiebe – doch sie kommt kaum zur Ruhe."),
    "hunter_wings": ("Jägerschwingen", "Fliegen und Rennen kosten weniger Ausdauer."),
    "lean_body": ("Ausgezehrt", "Ihre maximale Ausdauer sinkt."),
    "sky_hunger": ("Himmelshunger", "Nahrung sättigt kaum, und Beute flieht noch früher."),
    "shaky_wings": ("Zittrige Schwingen", "Fliegen und Rennen kosten viel mehr Ausdauer."),
    "restless_sleep": ("Unruhiger Schlaf", "Ihre Ausdauer erholt sich langsamer."),
    "hallucinations": ("Wahnbilder", "Sie sieht Dinge, die nicht da sind."),
    "false_rest": ("Trügerischer Schlaf", "Schlaf schenkt ihr nur noch einen Teil ihres Manas."),
    "torn_focus": ("Zerrissener Fokus", "Magie und Schleier fressen mehr Mana."),
    "dread": ("Schreckstarre", "Angst lähmt sie – alles kostet mehr Ausdauer."),
    "fraying_mind": ("Ausfransender Geist", "Magie kostet mehr, Nahrung und Schlaf helfen weniger."),
    "dark_affinity": ("Dunkle Verbundenheit", "Ihre Magie kostet weniger Mana."),
    "greedy_soul": ("Gierige Seele", "Nichts macht sie mehr satt."),
    "insatiable": ("Unersättlich", "Blut gibt ihr mehr, Nahrung noch weniger."),
    "blood_thirst": ("Blutdurst", "Blut schenkt ihr mehr Mana."),
    "restless_heart": ("Rastloses Herz", "Ihr Herz rast – Ausdauer kehrt kaum zurück."),
    "possessed": ("Besessenheit", "Härtere Hiebe, doch ihr Körper verkrampft."),
    "overflow": ("Überfluss", "Sie kann mehr Mana in sich tragen."),
    "leaking_power": ("Sickernde Macht", "Ihr Schleier verbrennt mehr Mana."),
    "bursting_heart": ("Berstendes Herz", "Die Macht zerreißt sie – Ausdauer schwindet."),
    "longing": ("Sehnsucht", "Ihre Magie kostet weniger – sie kämpft für Fira."),
    "devotion": ("Hingabe", "Nahrung heilt sie besser."),
    "grief": ("Trauer", "Sie hat Fira im Käfig zurückgelassen. Fast alles fällt ihr schwerer – bis sie ihn befreit."),
}
# (extra morals like SAffection – with their names, effects and limit lines – live in data/morals.json)

# ---------------------------------------------------------------------------
# Menus, HUD and other interface text
# ---------------------------------------------------------------------------
STAGE_NAMES = ["Schlüpfling", "Jungdrachin", "Finsternis-Drachin"]
SUBTITLE = "Ein Survival-Metroidvania über eine kleine Finsternis-Drachin"
WARN_KEYWORD = "GELÖSCHT"            # the line of START_WARNING that is drawn in red
UI = {
    "new_game": "Neues Spiel", "continue": "Fortsetzen", "controls": "Steuerung", "credits": "Credits",
    "settings": "Einstellungen", "quit": "Beenden",
    "overwrite": "Vorhandenen Spielstand überschreiben?", "yes": "Ja", "no": "Nein",
    "pause": "Pause", "resume": "Weiter", "main_menu": "Hauptmenü",
    "pause_note": "Fortschritt wird nur beim Schlafen gespeichert.",
    "mastery": "Manaschulung {pct}%",
    "mastery_adult": "  ·  Mana +{bonus}  ·  Zauberkraft ×{mult}",
    "mastery_young": "  ·  zahlt sich aus, wenn sie ausgewachsen ist",
    "adaptation": "     Lichtgewöhnung {pct}%",
    "nature": "Shadowras Wesen:  {title}",
    "ways": "Wege:  ",
    "affection_stats": "Zuneigung {a}",
    # credits: her journey
    "abilities": "Fähigkeiten: ",
    "journey_stats": "Manaschulung {m}%   ·   Lichtgewöhnung {a}%",
    "her_nature": "Ihr Wesen: {title}",
    "her_ways": "Ihre Wege: ",
    "stones": "Schattensteine geweckt: {n}/3",
    "grove": "Elfenhain: Shadowra {fate}",
    "hugs": "Umarmungen: {total}   ·   Wesen, die sie lieben: {loved}",
    # endings
    "enter_menu": "[Enter] Hauptmenü",
    "story_goes_on": "Die Geschichte geht weiter – im Norden, in den Schneelanden.",
    "continue_or_menu": "[Enter] Weiterspielen   ·   [Esc] Hauptmenü",
    "save_deleted": "Dein Spielstand wurde gelöscht.",
    # in the game
    "new_item": "Neu: ",
    "rest_food": "Fressen & Trinken  ({food})",
    "rest_empty": "leer",
    "rest_sleep": "Schlafen  (Mana auffüllen, speichern)",
    "rest_leave": "Weiterziehen",
    "rest_prompt": "Shadowra lässt sich nieder. Was soll sie tun?",
    "altar": "Altar",
    "eat_msg": "Shadowra frisst ({food}) und trinkt aus der Quelle.",
    "drink_only": " Sie trinkt nur etwas Wasser.",
    "boss_name": "Mafor, der Lichttyrann",
    "prompt_rest": "[E] Rasten",
    "prompt_eat": "[E] Fressen",
    # settings
    "language": "Sprache",
    "back": "Zurück",
    "settings_hint": "[A / D] ändern   ·   [Enter / Esc] zurück",
    "cheats": "Cheats: {names}",
}
HELP = [
    ("A / D", "Laufen"),
    ("Shift", "Rennen (Ausdauer)"),
    ("Leertaste", "Springen  /  halten: Gleiten  /  in der Luft: Flügelschlag"),
    ("J", "Klauen-Kombo   (S + J in der Luft: Sturzflug)"),
    ("K", "Schwanzpeitsche"),
    ("L", "Finsternis-Geschoss (Mana)"),
    ("I", "Finsternis-Flamme halten (Mana)"),
    ("U", "Blut-Sog (wenn erlernt)"),
    ("Q", "Schattensprung (Ausdauer)"),
    ("E", "Fressen / Rasten / Sprechen"),
    ("Esc", "Pause"),
]
CHEAT_NAMES = {"infinite mana": "Unendlich Mana", "infinite stamina": "Unendlich Ausdauer",
               "infinite health": "Unendlich Leben"}
HELP_NOTES = [
    "Leben heilt nur durch Fressen (Altäre, Beute) oder Blut.",
    "Mana kehrt nur durch Schlaf, Schattenkristalle oder Blut zurück.",
    "Ausdauer erholt sich schnell am Boden – in der Luft nicht.",
]


def replay_caption(stored):
    """Replay milestones are stored language-neutral ("@relic:veil"); older saves hold finished text."""
    if not stored or not stored.startswith("@"):
        return stored
    key, _, ref = stored[1:].partition(":")
    name = ""
    if key in ("relic", "gift"):
        from . import abilities
        name = abilities.name(ref)
    elif key == "grew":
        name = STAGE_NAMES[int(ref)] if ref.isdigit() else ref
    elif key == "stone":
        name = STONE_NAMES.get(ref, ref)
    return REPLAY_EVENTS.get(key, key).format(name=name)


# ---------------------------------------------------------------------------
# Language switch
# ---------------------------------------------------------------------------
LANGUAGES = {"de": "Deutsch", "en": "English"}
LANG = "de"
_GERMAN = None


def _is_text(name):
    return name.isupper() and not name.startswith("_") and name not in ("LANG", "LANGUAGES", "AGE")


def set_language(lang):
    """Swap every text constant of this module for the chosen language (German stays the fallback)."""
    global LANG, _GERMAN
    g = globals()
    if _GERMAN is None:
        _GERMAN = {k: v for k, v in g.items() if _is_text(k)}
    lang = lang if lang in LANGUAGES else "de"
    g.update(_GERMAN)
    if lang == "en":
        from . import texts_en
        g.update({k: v for k, v in vars(texts_en).items() if _is_text(k)})
    LANG = lang
