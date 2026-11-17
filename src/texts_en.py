"""English version of every in-game text. Same names and structure as texts.py (the German original);
texts.set_language("en") copies these over. Anything missing here falls back to German."""
from . import texts as _de

ZONE_NAMES = {
    "nest": "The Nest",
    "river": "River Valley",
    "meadow": "Sun Meadows",
    "vale": "Vale of Shadowstones",
    "canyon": "Updraft Canyon",
    "cliff": "Cliff of Storms",
    "grove": "Elven Grove",
    "ruins": "Ruins of Light",
    "plateau": "Glaring Highlands",
    "lava": "Lava Sea",
    "summit": "Mafor's Summit",
    "frostpass": "Frost Pass",
    "snowfield": "Snowfields",
    "icecave": "Ice Cave",
    "snowvillage": "Village in the Snow",
    "frozenlake": "Frozen Lake",
    "underwater": "Beneath the Frozen Lake",
    "northcliff": "North Cliff",
}

# ---------------------------------------------------------------------------
# Daylight
# ---------------------------------------------------------------------------
SUN_INTRO = {
    "meadow": [
        ("", "For the first time Shadowra sees the open sky by day. The light burns on her scales."),
        ("Hint", "Daylight burns her. Hide in the shade of trees, rocks and clouds – "
                 "in the water – or take the dark tunnels under the ground."),
        ("Hint", "Every second in the light hurts. But her body gets used to it. (Light tolerance)"),
    ],
    "vale": [
        ("", "Beyond the meadows a wide valley full of light opens up. Far to the east a rock wall rises – "
             "with a black gate in it."),
        ("", "Old dragon tales say: three Shadowstones sleep in this valley. Only one who wakes them all "
             "will see the Shadow Gate open."),
        ("Hint", "Find the three Shadowstones: in the cave under the hill, on the island in the lake and on top of the mesa. "
                 "(E at the stone)"),
    ],
    "plateau": [
        ("", "The highlands glare in the light. No tree, no cloud. Only old temple roofs and floating rocks cast shade."),
        ("Hint", "In the light the Shadow Veil eats her mana. The more she gets used to the light, the less."),
        ("Hint", "A Sun Shrine stands in the middle of the light. Whoever endures it there learns to bear the light faster – "
                 "but it burns."),
    ],
}
STONE_NAMES = {"stone_cave": "Cave Stone", "stone_lake": "Lake Stone", "stone_mesa": "Summit Stone"}
STONE_PROMPT = "[E] Wake the Shadowstone"
STONE_WAKE = "Shadowra lays her claw on the {name}. Violet runes awaken.  ({n}/3)"
STONE_AWAKE = "The {name} is already awake."
GATE_OPEN = [
    ("", "Far to the east the rock rumbles. All three Shadowstones glow – and the Shadow Gate sinks into the earth."),
]
GATE_CLOSED = "The Shadow Gate is sealed. Three Shadowstones must awaken ({n}/3)."
BURROW_IN = "Crawl into the burrow (dark tunnel)"
BURROW_OUT = "Out into the light"
SHRINE_NAME = "Sun Shrine"
SHRINE_PROMPT = "An old shrine, golden and hot. The light here is almost unbearable."
SHRINE_MENU = ["Endure the light (light tolerance)", "Leave"]
SHRINE_ENDURE = "Shadowra lowers her veil and stands up to the light. It burns – and she grows stronger."
SHRINE_STOP = "Shadowra staggers out of the light. She can't bear any more right now."

START_WARNING = [
    "Shadowra is not a tool. She is a living being.",
    "",
    "She gets tired. She gets hungry. She has to sleep.",
    "Her strength does not come from nowhere.",
    "",
    "Every choice you force on her shapes her soul.",
    "If you force her into deeds she loathes, or drive her",
    "too deep into greed, your save will in the end be",
    "irretrievably DELETED.",
    "",
    "[Enter] I understand",
]

INTRO = [
    ("", "Deep under the earth, in a nest of roots and shadows, a little dragoness opens her eyes."),
    ("", "Her name is Shadowra. She is a child of darkness – and light burns her."),
    ("", "High above the world rules Mafor, the Light Tyrant. He has captured Fira, the only one who ever stood by her."),
    ("", "But Shadowra is still so small. First she has to grow."),
    ("Hint", "At the nest (E) she can drink and sleep. Sleep refills her mana and saves the game."),
]

STAGE_UP = {
    1: [("", "In her sleep Shadowra's body stretches. Her scales grow harder, her wings longer."),
        ("", "She is a young dragon now. Milk no longer stills her hunger – she needs fish."),
        ("Hint", "Catch fish with your claws (J) while they swim in the water.")],
    2: [("", "Shadowra wakes – and the shadow she casts is enormous."),
        ("", "She is a fully grown Dark Dragoness. Her body now craves meat."),
        ("", "Her magic has taught her what her body can now hold: her spells hit harder, "
             "and the more often she used her mana, the larger her reserve."),
        ("Hint", "Her wings are strong enough. Press Space in the air for a wingbeat.")],
}
FLY_NOT_SEEN = ("", "Her wings would be strong enough... but she doesn't know yet how to really fly. "
                    "Maybe she can learn it by watching someone.")

BIRDS = [
    ("", "Through an opening in the cave ceiling Shadowra sees shadow birds sailing silently through the dusk."),
    ("", "She spreads her tiny wings. Something inside her awakens."),
    ("New", "Shadowra has understood gliding.  (Hold Space in the air)"),
]
STORM_DRAGON = [
    ("", "Above the cliff a mighty dragon passes through the storm. Every wingbeat is calm and powerful."),
    ("", "Shadowra watches him until he vanishes into the clouds. She has understood how to fly."),
]
STORM_DRAGON_YOUNG = ("New", "Her wings are still too weak. But once she is fully grown, she will be able to fly.")
STORM_DRAGON_ADULT = ("New", "Shadowra can fly now!  (Space in the air: wingbeat – costs a lot of stamina)")


BLOOD_LEARNED = [
    ("", "Shadowra is bleeding. Her vision blurs. And suddenly there is an instinct she never wanted."),
    ("", "Blood. The life of others could give her mana and strength."),
    ("New", "Blood Drain learned (U near a weakened or fallen creature). Shadowra hates it."),
    ("Warning", "Every time you force her to do it, it changes her."),
]
BLOOD_MSG = {
    "peaceful": "Shadowra hesitates... and bites. A quiet whimper escapes her.",
    "priest": "The priest's blood burns in her throat. Something inside her wants more of it.",
    "fish": "The cold blood of the fish. It feels almost natural.",
    "elf": "Elven blood. It tastes of moonlight – and of betrayal.",
    "human": "Human blood. Warm and salty – and everything in her screams that it is wrong.",
    "greedy": "She wouldn't even need it. She does it anyway.",
}

OWL_NAME = "Old Owl Morwen"
OWL = {
    "first": {
        "juvenile": [
            (OWL_NAME, "Hoo... a dragon child, this far out? Don't be afraid, little one."),
            (OWL_NAME, "There are plenty of fish in the river. Catch them with your claws while they're in the water."),
            (OWL_NAME, "To the east lie the Sun Meadows. By day the light burns there. Stay in the shade of the trees, "
                       "wait for the clouds – or take the old tunnels under the ground."),
            (OWL_NAME, "Beyond them lies a wide valley with a black gate. Three old stones sleep there – "
                       "in a cave, on an island and high up on the mesa."),
            (OWL_NAME, "And behind the gate, the canyon. The warm winds there carry you if you just glide."),
            (OWL_NAME, "And never forget: shadow is your friend, light is your enemy."),
        ],
        "adult": [
            (OWL_NAME, "Hoo! By all the stars – a fully grown Dark Dragoness! ...Please don't eat me."),
            (OWL_NAME, "You don't want to hurt me? Well then... I'm Morwen. I've been sitting on this branch forever."),
            (OWL_NAME, "To the east lie the Sun Meadows. The light burns there by day – even one as large as you."),
            (OWL_NAME, "And never forget: shadow is your friend, light is your enemy."),
        ],
    },
    "greet": {
        "juvenile": (OWL_NAME, "Hoo, there you are again, little one. Have you eaten enough?"),
        "adult": (OWL_NAME, "Ah, my big dragoness. How nice that you don't forget me."),
    },
    "grew": [
        (OWL_NAME, "Oh, hello, large one! You came back to me."),
        (OWL_NAME, "Hoo... the last time you were here you were hardly bigger than me. And now look at you!"),
    ],
    "gift": {
        "juvenile": (OWL_NAME, "Here, take this fish. You look hungry."),
        "adult": (OWL_NAME, "I'd have a fish here... probably just a bite for a dragoness this big. Take it anyway."),
    },
    "hint_veil": (OWL_NAME, "They say a veil of darkness lies on the Cliff of Storms. Without it you'll never cross the Lava Sea."),
    "hint_fish": (OWL_NAME, "You're still too small for the Lava Sea. Eat fish, sleep well – then you will grow."),
    "hint_fire": (OWL_NAME, "A dark fire rests in the ruins. Behind brittle stone, they say."),
    "hint_general": (OWL_NAME, "Rest when you can, child. Whoever never sleeps loses their mind sooner or later."),
    "afraid": (OWL_NAME, "Stay... stay away from me. Your eyes glow so red. What has become of you?"),
    "afraid_wild": (OWL_NAME, "Stay away! You smell of moss runner blood... What has become of you?"),
    "afraid_mad": (OWL_NAME, "Who are you talking to, child? There's no one there. There never was... Please, sleep at last."),
    "afraid_lust": (OWL_NAME, "You smile when you speak of power. That's how Mafor started, too."),
    "gone": ("", "The branch is empty. Morwen is gone – she is hiding from you."),
}

# ---------------------------------------------------------------------------
# Hugs
# ---------------------------------------------------------------------------
HUG_GREW = {
    "peaceful": {
        "juvenile": "The moss runner sniffs her for a long time. Is this really the little dragon child from back then?",
        "adult": "The moss runner looks way, way up. The tiny dragon child from back then – a giant now.",
    },
    "owl": (OWL_NAME, "Hoo! The last time you squeezed me you were still so small..."),
    "Sera": ("Sera", "Wait – you've grown even bigger! How much do you actually eat?"),
    "Erila": ("Erila", "You've grown, little one... no, big one. I'll have to get used to that."),
}
HUG_MENU = {
    "talk": "Talk", "hug": "Hug", "nuzzle": "Nuzzle", "leave": "Leave", "leave_be": "Leave alone",
}
HUG_PROMPT = "What does Shadowra want to do?"
HUG_NAMES = {"peaceful": "Moss Runner", "owl": "Old Owl Morwen"}
HUGS = {
    "peaceful": {
        "confused": {
            "hatchling": "The moss runner sniffs the tiny dragon child – and stands there, confused.",
            "juvenile": "The moss runner freezes. It has no idea what this dragoness wants from it...",
            "adult": "The moss runner freezes under the huge wings. Will it be eaten – or hugged?",
        },
        "warming": {
            "hatchling": "The moss runner gently nudges the dragon child with its nose.",
            "juvenile": "The moss runner hesitates – then carefully leans against Shadowra.",
            "adult": "The moss runner leans against the big dragoness like against a warm rock.",
        },
        "loves": {
            "hatchling": "The moss runner lies down next to the dragon child and warms it with its mossy fur.",
            "juvenile": "The moss runner presses itself against her and hums contentedly.",
            "adult": "The moss runner snuggles under her wings. It feels safe there.",
        },
        "afraid": "The moss runner trembles all over until she lets go.",
        "rejected": "The moss runner tears free in panic and flees.",
        "again": {
            "hatchling": "The moss runner lets the dragon child doze on its back.",
            "juvenile": "The moss runner enjoys the hug.",
            "adult": "The moss runner almost disappears in her hug – and enjoys it.",
        },
    },
    "owl": {
        "confused": {
            "juvenile": "Hoo?! What... what are you doing, child? ...Oh. You just want to cuddle.",
            "adult": "Hoo!! Careful, big one – you're squashing me! ...Oh. You just want to cuddle.",
        },
        "warming": {
            "juvenile": "Hoo-hoo... come here then. Your scales are so warm.",
            "adult": "Hoo-hoo... so much dragon, so much warmth. Come on, but gently.",
        },
        "loves": {
            "juvenile": "My little dragoness! I missed you.",
            "adult": "Oh, hello, large one! You came back to me. I missed you.",
        },
        "afraid": {
            "juvenile": "P-please... let me go. I don't know who you are anymore.",
            "adult": "P-please... you've grown so big. And so dark. Let me go.",
        },
        "rejected": "Hoo! Get away from me!",
        "again": {
            "juvenile": "Hoo~ Again? Oh, all right.",
            "adult": "Hoo~ Again? All right – but leave me a few feathers.",
        },
    },
    "Sera": {
        "accepts": {
            "juvenile": "Hey! ...Oh, come here then. But don't tell anyone.",
            "adult": "You're twice my size – and you still want to cuddle? ...Come here then.",
        },
        "confused": {
            "juvenile": "Hey! What's that supposed to be, dragoness?! ...Fine. But only for a moment.",
            "adult": "Hey! You're twice my size, dragoness! ...Fine. But only for a moment.",
        },
        "warming": {
            "juvenile": "You're pretty clingy, you know that?",
            "adult": "You've become huge – and you're still this clingy.",
        },
        "loves": {
            "juvenile": "Come here, you ball of scales.",
            "adult": "Come here, you big ball of scales.",
        },
        "afraid": "Stop that. I don't trust you.",
        "rejected": "Don't touch me, beast!",
        "cold": "Now you want to cuddle? After you left us on our own?",
        "again": "Again? ...Not that I'm complaining.",
    },
    "Erila": {
        "accepts": {
            "juvenile": "Oh! Come here, dear. You're so warm.",
            "adult": "Oh! Come here... so big and so warm. That feels good.",
        },
        "confused": {
            "juvenile": "Oh! You're... surprisingly warm.",
            "adult": "Oh! You're so big... and so warm.",
        },
        "warming": {
            "juvenile": "You're looking for closeness, aren't you? There's nothing wrong with that.",
            "adult": "You've grown, but your heart has stayed the same.",
        },
        "loves": {
            "juvenile": "I'm fond of you too, little one.",
            "adult": "I'm fond of you too, big one.",
        },
        "afraid": "I... sense so much darkness in you.",
        "rejected": "No... please don't.",
        "cold": "We owe you nothing. And you owe us nothing.",
        "again": "Mhm. Stay a moment longer.",
    },
}

# ---------------------------------------------------------------------------
# Elven village – the villagers (looks and gender come from the German file)
# ---------------------------------------------------------------------------
_VILLAGER_TEXT = {
    "Lyria": ("Oh! You're so warm! Come here, sweetie – I'm never letting you go.",
              ["The village elder says dragons bring luck. I believe her now.",
               "Do you like moonflowers? I'll weave you a wreath – someday, when you hold still."]),
    "Naela": ("Hehe, your scales tickle! Come on, squeeze me tighter.",
              ["I tend the mushrooms by the pond. They've glowed brighter since you were here.",
               "Sera always acts so strict. Yet she talks about you all day long."]),
    "Thessa": ("Oh, a dragon hug! How lovely. You smell of night and moss.",
               ["I bake nut bread. Dragons don't eat that, do they? Pity.",
                "Take care of yourself, okay? The sun burns out there."]),
    "Aren": ("H-hey! I... uh... *turns red to the tips of his ears* ...That was nice. I think.",
             ["I'm a hunter, like Sera. Well... not quite as good as Sera.",
              "The brood always comes from the west. Thank you for stopping them."]),
    "Calen": ("Oh! I... I have to put this in a song... uh... *turns bright red and forgets every word*",
              ["I write songs. One is about a dragoness made of shadow. Guess who.",
               "Erila is my sister. She likes you a lot. ...So do I. As a friend, I mean!"]),
    "Fenrik": ("Hoho! At my age... *clears his throat, cheeks glowing* ...Thank you, child. That felt good.",
               ["I am Fenrik, the eldest. I saw dragons back when the sun was still kind.",
                "You carry shadow within you, child – but no darkness in your heart. Keep it that way."]),
}
VILLAGERS = {name: dict(data, first=_VILLAGER_TEXT[name][0], talk=_VILLAGER_TEXT[name][1])
             for name, data in _de.VILLAGERS.items()}
VILLAGE_TALK = {
    "grew": "By all the leaves – are you the little dragoness from back then?",
    "cold": "You let Sera and Erila fight alone. Why should we talk to you?",
    "wary": "Thank you for your help... but please keep some distance from the houses.",
}
VILLAGE_HUGS = {
    "f": {
        "accepts": {"juvenile": "Oh! Come here, sweetie. *hugs you really tight*",
                    "adult": "Oh! Such a big hug! Come here, sweetie."},
        "warming": "Cuddling again? Any time, little one.",
        "loves": {"juvenile": "My favourite dragoness! Come here!", "adult": "My big favourite dragoness! Come here!"},
        "again": "Mhm... just a little longer.",
        "afraid": "P-please... not so tight. You're scaring me.",
        "rejected": "No! Let go of me!",
        "cold": "Stop that. After what you did...",
    },
    "m": {
        "blush": {"juvenile": "Uh-uh... I... this is... *turns bright red* ...Thanks?",
                  "adult": "W-wow, you're... big. And warm. I... *turns bright red and stares at his feet*"},
        "warming": "*clears throat* You again... All right. But only briefly. *blushing again already*",
        "loves": "Okay, I admit it. I like your hugs. Just don't tell Sera.",
        "again": "*coughs* Yes... yes, it's fine. It's nice.",
        "afraid": "S-stop! Please... you scare me.",
        "rejected": "Get away! Don't touch me!",
        "cold": "No thanks. You left us on our own.",
    },
}

ALTAR_NAMES = {
    "N": "The Nest",
    "M": "Moonmilk Spring",
    "A1": "River Altar",
    "A2": "Shrine of the Ruins",
    "A3": "Shadow Isle",
    "A4": "Last Rest",
    "A5": "Rock Arch",
    "A6": "Temple Shade",
    "A7": "Lakeside Rest",
    "A8": "Cave Spring",
    "A9": "Gate Shade",
    "E": "Elven Village Well",
}
FOOD_NAMES = {"milk": "milk", "fish": "fish", "meat": "meat"}
CANT_EAT = {
    "fish": "Her stomach can't handle fish yet.",
    "meat": "Meat is still far too tough for her.",
    "milk": "Milk doesn't still her hunger anymore.",
}

NO_RETURN_GREED = [
    ("???", "The darkness in you is too thick now."),
    ("???", "Your deeds have corrupted Shadowra. If you go on, you will lose everything."),
]
NO_RETURN_CLOSE = [
    ("???", "You stand at the edge of the abyss. One more cruel deed, and there is no way back."),
]
LAST_REST = ("", "The wind carries Fira's call. Mafor waits beyond the ridge.")

BOSS_INTRO = [
    ("Mafor", "A child of darkness dares to step into my light?"),
    ("Mafor", "I will burn you, as I have burned all of your kind."),
]
BOSS_DEFEATED = [("Mafor", "My... light... Spare me, dragon. I beg you.")]
BOSS_CHOICE = ["Spare", "Devour"]
BOSS_SPARED = ("", "Shadowra turns away. Mafor flees into the depths, a broken, extinguished man.")
BOSS_DEVOURED = ("", "Shadowra devours the tyrant's last light. An unknown power flows through her. She enjoys it.")

ENDINGS = {
    "light": dict(
        title="Light in the Darkness",
        lines=[
            ("Fira", "Shadowra! You came..."),
            ("", "Fira looks into her eyes – and sees the same gentle dragoness he once knew."),
            ("Fira", "You survived all of this without losing yourself."),
            ("", "Together they fly into the first night that belongs to them again."),
        ],
        footer="END OF CHAPTER 1  ·  You kept Shadowra's heart.",
    ),
    "redemption": dict(
        title="The Way Back",
        lines=[
            ("Fira", "Shadowra...? It's... it's you, isn't it?"),
            ("", "Fira takes a step back. The blood on her claws hasn't dried yet."),
            ("Fira", "You lost yourself to save me."),
            ("Fira", "Then I'll bring you back now. No matter how long it takes."),
        ],
        footer="END OF CHAPTER 1  ·  Shadowra's path to redemption has only begun.",
    ),
    "madness": dict(
        title="Voices in the Shadow",
        lines=[
            ("Fira", "Shadowra, it's me! Fira!"),
            ("Shadowra", "...the shadows say you're not real. The shadows never lie."),
            ("", "She no longer recognizes him. When the voices scream, she strikes – and Fira falls."),
            ("", "For a long time she sits beside him in the wind. Then she travels north, alone."),
            ("Shadowra", "Somewhere out there someone new is waiting for me. The shadows promised."),
        ],
        footer="END OF CHAPTER 1  ·  Shadowra's mind is broken.",
    ),
    "obsession": dict(
        title="The New Tyrant",
        lines=[
            ("Fira", "Shadowra, let's go. It's over."),
            ("Shadowra", "Over? It's only just beginning."),
            ("", "She builds an empire from the bones of her prey. Mafor's throne is hers now."),
            ("", "And Fira? She locks him up again. Not out of hatred – but because she wants to own everything."),
            ("", "Then she looks north. There is so much more there that could belong to her."),
        ],
        footer="END OF CHAPTER 1  ·  The hunger for power has devoured Shadowra.",
    ),
    "greed": dict(
        title="",
        lines=[
            ("Fira", "Shadowra...?"),
            ("", "Fira backs away in horror. He no longer sees a dragoness. He sees a beast."),
            ("Fira", "Stay away from me! You're not her. You're not her anymore..."),
            ("", "Something inside Shadowra breaks. Quietly."),
        ],
        footer="",
    ),
}
# ---------------------------------------------------------------------------
# Credits (main menu)
# ---------------------------------------------------------------------------
CREDITS_HEAD = [
    ("title", "Shadowra's Story"),
    ("sub", "A survival metroidvania about a little dark dragoness"),
    ("gap", ""),
    ("head", "Idea, Story & World"),
    ("text", "Shadowra's creator"),
    ("gap", ""),
    ("head", "Programming, Characters & World Building"),
    ("text", "together with Claude"),
    ("gap", ""),
    ("head", "Art Packs"),
    ("text", "Multi Platformer Tileset – Shackhal (CC0)"),
    ("text", "Starry Night – Quintino Pixels"),
    ("text", "Wasteland Backgrounds"),
    ("text", "Crimson Fantasy GUI"),
    ("text", "Dungeon Character & Tileset"),
    ("gap", ""),
    ("head", "Fonts"),
    ("text", "Kalnia Glaze – Frida Medrano (OFL)"),
    ("gap", ""),
    ("head", "Engine"),
    ("text", "Python & pygame"),
    ("gap", ""),
]
CREDITS_JOURNEY = "Shadowra's Journey So Far"
REPLAY_EVENTS = {
    "glide": "Learned to glide",
    "storm": "Saw the storm dragon – understood flying",
    "relic": "Found: {name}",
    "blood": "Blood Drain awakened",
    "grew": "Grew up: {name}",
    "stone": "Awakened: {name}",
    "gate": "The Shadow Gate opens",
    "elves": "Saved the elves",
    "mafor": "Mafor defeated",
    "north": "Reached the snowlands",
    "dive": "Learned to dive",
    "gift": "Gift: {name}",
}
CREDITS_NO_SAVE = "Her journey hasn't begun yet. In the nest an egg of shadow is waiting..."
CREDITS_FATE_INTRO = "This is how her story could end:"
CREDITS_FATES = {
    "start": "A little dragon child. Alone. Her story is only beginning.",
    "light": "Shadowra and Fira – together in the night that finally belongs to them.",
    "redemption": "Fira stays by her side. Still keeping his distance. The way back is long.",
    "madness": "Alone. Fira has fallen – she searches the north for a new love, and the voices go with her.",
    "obsession": "Alone on Mafor's throne. Everything belongs to her – and no one stays.",
    "greed": "Alone. Greed has taken everything from her.",
    "lost": "Corrupted Soul – Lost to Greed.",
}
CREDITS_ELVES = "And in the elven village, Sera and Erila light a lantern for her."
CREDITS_OWL = "Morwen sits on a branch nearby and watches over her."
CREDITS_END = "Thank you for playing."
CREDITS_CLOSEUP_UNFINISHED ="Hey, why are you stopping now? Or do you just want to see me up close, player?"
CREDITS_SKIP = "[Enter / Esc] Back   ·   [hold Space] faster"
GROVE_FATES = {"friends": "saved the elves", "wary": "helped – the elves remain cautious",
               "alone": "let the elves fight alone", "dead": "the elves have fallen",
               "hostile": "the elves fear her"}

GREED_DEATH = "You died – through your own greed."
GREED_SLOT = "Corrupted Soul – Lost to Greed"

DEATH = "Shadowra has fallen..."

# ---------------------------------------------------------------------------
# Elven Grove – Sera & Erila
# ---------------------------------------------------------------------------
SERA, ERILA = "Sera", "Erila"
GROVE = {
    "meet_trust": {
        "juvenile": [
            ("", "Among glowing mushrooms two elves stand back to back. Shadow creatures crawl toward them out of the dark."),
            (SERA, "A dragon?! ...No, wait. She's still young. And her eyes aren't like the others'."),
            (ERILA, "Little dragoness, the Light Tyrant's brood has been hunting us for days. We can't hold out much longer."),
            (SERA, "Will you help us? ...Or will you just walk on, like everyone else?"),
        ],
        "adult": [
            ("", "Among glowing mushrooms two elves stand back to back. Shadow creatures crawl toward them out of the dark."),
            (SERA, "A fully grown dragoness?! Erila, behind me! ...No, wait. Her eyes aren't like the others'."),
            (ERILA, "Great dragoness, the Light Tyrant's brood has been hunting us for days. We can't hold out much longer."),
            (SERA, "With claws like yours we'd be safe. Will you help us? ...Or will you just walk on?"),
        ],
    },
    "meet_afraid": {
        "juvenile": [
            ("", "Two elves whirl around. An arrow aims straight at Shadowra's throat."),
            (SERA, "Not one step closer, beast! I can see the blood on your claws."),
            (ERILA, "Sera, wait... behind her! The brood is coming!"),
        ],
        "adult": [
            ("", "Two elves whirl around. Sera draws her bow – her hands tremble before the huge dragoness."),
            (SERA, "Stay where you are, beast! So big... and blood on your claws."),
            (ERILA, "Sera, wait... behind her! The brood is coming!"),
        ],
    },
    "grew": [
        (ERILA, "By the stars – you've grown! Soon you won't fit into our grove anymore."),
        (SERA, "Hm. At least now you can see who protected us."),
    ],
    "meet_hostile": [
        ("", "The elves see Shadowra – and freeze."),
        (SERA, "Another beast! Erila, run! I'll hold her off!"),
    ],
    "choice": ["Help", "Don't help"],
    "choice_nuzzle": "Stay with them and nuzzle up",
    "help": [(SERA, "Then show us what you've got! Erila, stay behind us!")],
    "decline": [(SERA, "...Of course. Just run."), (ERILA, "Sera, focus. They're coming!")],
    "nuzzle": [
        ("", "Shadowra folds her wings and nuzzles her head against Erila's hand. Then against Sera's shoulder."),
        (ERILA, "Oh... she doesn't want to fight. She just wants to be with us."),
        (SERA, "Her shadow wraps around us like a cloak... Stay with us, little one. We'll protect each other."),
        ("Hint", "As long as Shadowra stays close to the elves, her shadow protects them. (E at an elf: nuzzle)"),
    ],
    "wave": "Wave {n}/{total}: The brood attacks!",
    "won_friends": [
        (ERILA, "It's over... We're alive. Thanks to you."),
        (SERA, "I was wrong about you, dragoness. Our village is yours too. Eat, rest."),
        (ERILA, "Let me heal your wounds. And take this moon dew – it restores your strength."),
    ],
    "won_nuzzle_extra": [(ERILA, "You may come back any time. Just... to be with us.")],
    "won_alone": [
        (SERA, "We made it on our own. Without you."),
        (ERILA, "Move on, dragoness. There's nothing here for you."),
    ],
    "won_afraid": [
        (SERA, "...You actually helped us."),
        (ERILA, "Take some healing. But into our village... we don't trust you that much yet."),
    ],
    "dead_watched": [("", "The last elf falls. Shadowra watched. The image burns itself into her mind.")],
    "dead_helped": [("", "Despite everything – the elves have fallen. Shadowra lies beside them for a long time.")],
    "talk_friends": {
        "juvenile": [(SERA, "Well, dragoness? Hungry? The village is open to you."),
                     (ERILA, "Take care of yourself out there. We're thinking of you.")],
        "adult": [(SERA, "Well, big dragoness? Careful you don't knock over our houses."),
                  (ERILA, "The village is open to you. We're glad to see you – no matter how big you get.")],
    },
    "talk_alone": {
        "juvenile": [(SERA, "What do you still want here?")],
        "adult": [(SERA, "You've grown, yes. But when we needed you, you weren't there.")],
    },
    "talk_turned": [(SERA, "You smell of blood. You're no longer the one who saved us. Go.")],
    "nuzzle_again": "Shadowra nuzzles up to {name}. For a moment everything is still.",
    "camp_locked": "The elves' village well. Without their permission Shadowra touches nothing.",
}

GATE_HINT = ("The ledge is still too high for her. First she has to grow – "
             "drink {food} and sleep ({food} {have}/{need}).")

TOASTS = {
    "too_hard": "The stone is too hard for her claws.",
    "vines": "Dense thorn vines. Fire could burn them.",
    "exhausted": "Shadowra is exhausted...",
    "hungry": "Shadowra is hungry. Her stamina is fading.",
    "sleepless": "Shadowra is overtired. The shadows whisper.",
    "crystal": "Shadow crystal eaten  +Mana",
    "fish_eat": "Caught and ate a fish",
    "fish_young": "The fish gets away. Her stomach can't handle it yet.",
    "meat_eat": "Shadowra eats. She doesn't like the taste.",
    "no_mana": "Not enough mana.",
    "no_blood": "There is no blood to take here.",
    "saved": "Game saved",
    "no_food": "There is nothing left here she can eat.",
    "light_burn": "The light burns her!",
    "need_glide": "The chasm is too wide to jump across...",
    "growth_ready": "Shadowra is full enough to grow in her sleep.",
    "sun_adapt": "Light tolerance {pct}% – her scales withstand the light better.",
    "mastery_young": "Mana training {pct}% – her magic feels more familiar. Fully grown, she will draw on it.",
    "mastery_adult": "Mana training {pct}% – her mana reserve grows, her magic hits harder.",
    "cozy_meal": "Shadowra curls up cozily around her food.  +Affection",
    "ward": "At the resting place, nothing dares to come near her.",
    "cozy_hint": "Tip: stand her right on the food next to the altar – then she curls up cozily around it.",
}

# ---------------------------------------------------------------------------
# Chapter 2 – the snowlands
# ---------------------------------------------------------------------------
PASSAGE_LABELS = {"frostpass_in": "Down into the Frost Pass (north)", "frostpass_out": "Up to the Last Rest"}
SNOW = {
    "frostpass": [
        ("", "The tunnel is covered in frost. An ice-cold wind blows in from the east – and it smells of snow."),
    ],
    "arrive": [
        ("", "Beyond the Frost Pass lies a land of snow. No sunbeam gets through the clouds – but the cold bites."),
        ("Hint", "The cold drains her stamina, and once that is gone, her life. She finds warmth at hearth fires."),
    ],
    "arrive_fira": ("Fira", "Snow! I haven't seen snow in years. Stay close to me, okay?"),
    "arrive_mad": ("Shadowra", "...the shadows say someone is waiting in the north. Someone new."),
    "arrive_caged": ("Shadowra", "Fira is waiting in his cage. He won't run away from me. The north will."),
    "grief": [
        ("", "At the edge of the snow Shadowra stops. Behind her, high above the clouds, Fira still sits in his cage."),
        ("", "She goes on anyway. The grief settles on her heart like ice."),
        ("Hint", "Grief: almost everything is harder for her – until she frees Fira."),
    ],
    "cold_hint": "The cold wears her down. She finds warmth at a hearth fire – or her scales must grow harder.",
    "cold_hurt": "The cold eats into her bones!",
    "warm": "The hearth fire warms her.",
    "otters": [
        ("", "At the hole in the ice, otters pop up, shake themselves – and vanish into the depths again."),
        ("", "Shadowra watches them for a long time. She holds her breath. She understands."),
        ("New", "Learned to dive.  (Hold S in deep ice water – her breath doesn't last forever)"),
    ],
    "deep_no_dive": "The ice water is too deep – her body keeps floating back up.",
    "breath_low": "She's running out of air!",
    "melt_hint": "A wall of clear ice. Fire could melt it.",
    "north": [
        ("", "Beyond the North Cliff a narrow path leads on into the snow. Nobody knows yet what waits there."),
        ("", "To be continued..."),
    ],
    "north_fira": ("Fira", "Wherever this path leads – we'll walk it together."),
    "north_mad": ("Shadowra", "Somewhere out there someone is waiting who will look at me. The shadows promised."),
    "ash_wings": ("", "The heat of the Lava Sea has hardened her wings."),
    "moon_dew": ("Erila", "Take this moon dew with you. When you sleep, it will give you strength."),
}
FIRA_TALK = [
    ("Fira", "I thought I'd never see the sky again. And now I'm flying next to you."),
    ("Fira", "You've grown so big. Back then you were hardly more than a shadow with wings."),
    ("Fira", "If you get cold, come closer. I'm warm enough for two."),
    ("Fira", "I don't know what waits in the north. But I'm not afraid – you're here."),
]
HUMANS = {
    "Mira": dict(first="Oh! You're as warm as an oven! Come here – I'm never letting you go.",
                 talk=["A dragon that doesn't bite? My grandmother would never have believed me.",
                       "Winter lasts nine moons here. Stay as long as you like."]),
    "Bjarn": dict(first="H-hey! I... uh... *turns bright red under his fur collar* ...Mind my spear.",
                  talk=["I hunt snow hares. You hunt... what do you actually hunt?",
                        "Stay off the ice when it cracks. The Frozen Lake has taken many."]),
    "Hanne": dict(first="Hehe, your scales are cold and warm at the same time. How does that work?",
                  talk=["The otters at the Frozen Lake dive all the way down. I wonder what they find there.",
                        "I'll sew you a blanket. A very, very big blanket."]),
    "Gunnar": dict(first="Hoho! At my age, hugged by a dragon... *clears his throat, moved* Thank you, child.",
                   talk=["I'm Gunnar, the eldest. As long as the hearth fire burns, this village is safe.",
                         "They say a heart of frost beats in the ice cave. Whoever finds it never freezes again."]),
    "Tomas": dict(first="W-what... that... *turns so red the snow around him nearly melts* ...Okay.",
                  talk=["I've never been beyond the North Cliff. Nobody has.",
                        "If you want fish: at the Frozen Lake, through the hole in the ice."]),
    "Ylva": dict(first="Oh, how lovely! A dragon hug in the snow. I'm telling everyone.",
                 talk=["The children want to know if you can breathe fire. I told them: only dark fire.",
                       "Come to the hearth fire when you're cold. There's always room for you."]),
}
HUMAN_TALK = {
    "wary": "...Please stay over there, dragon. We don't want any trouble.",
    "hostile": ["There's the beast! To the spears!", "She has blood on her claws! Stop her!",
                "Drive her back into the mountains!"],
    "fira": "Two dragons... and they're friendly? Nobody will believe us.",
    "elder_gift": [
        ("Gunnar", "You did us no harm, though you could have. A village doesn't forget that."),
        ("Gunnar", "Take some of our hearth's warmth with you. Let it keep you company out in the snow."),
    ],
    "locked": "The humans' hearth. Without their trust Shadowra touches nothing.",
}

PATHS = {
    "gentle": ["Uncertain", "Gentle", "Pure Heart"],
    "wild": ["", "Restless", "Wild", "Beast"],
    "madness": ["", "Overtired", "Paranoid", "Insane"],
    "lust": ["", "Power-Hungry", "Drunk on Power", "Devoured"],
}

SUBPATHS = {
    "calm_breath": ("Calm Breath", "She breathes calmly – running and flying tire her less."),
    "trusted": ("Trust", "The world trusts her – food heals her better."),
    "strength": ("Predator", "Claws instead of heart. Prey flees, food doesn't satisfy – she only wants to hunt."),
    "flight": ("Wingbeat", "She hunts from the air. Her wings carry her, but her body wastes away."),
    "sleepless": ("Sleepless", "She finds no sleep anymore, and the world begins to lie to her."),
    "horror": ("Dread", "She sees things that aren't there, and her focus tears apart."),
    "twisted": ("Torn", "Haunted by what she has seen and done. Her mind frays."),
    "greedy": ("Greedy", "She takes more than she needs. Nothing fills her anymore."),
    "wanting": ("Obsessed", "She craves the power of others. Body and heart pay for it."),
    "overflowing": ("Overflow", "More power than her body can hold – it seeps out of her."),
    "affection": ("Affection", "She seeks closeness – to Fira and to everyone who lets her near."),
}

DOOMED_TITLE = "Lost"

EFFECTS = {
    "calm_breath": ("Calm Breath", "Running and flying cost less stamina."),
    "deep_rest": ("Deep Rest", "Her stamina returns faster."),
    "trusted": ("Sheltered", "Food heals her better."),
    "gentle_presence": ("Gentle Presence", "Peaceful creatures flee from her later."),
    "skittish_prey": ("Skittish Prey", "Peaceful creatures flee from far away."),
    "predator": ("Sharp Claws", "Her claws tear deeper."),
    "wild_hunger": ("Wild Hunger", "Normal food barely satisfies her."),
    "hunting_frenzy": ("Hunting Frenzy", "Even harder blows – but she hardly gets any rest."),
    "hunter_wings": ("Hunter's Wings", "Flying and running cost less stamina."),
    "lean_body": ("Gaunt", "Her maximum stamina drops."),
    "sky_hunger": ("Sky Hunger", "Food barely satisfies, and prey flees even earlier."),
    "shaky_wings": ("Shaky Wings", "Flying and running cost much more stamina."),
    "restless_sleep": ("Restless Sleep", "Her stamina recovers more slowly."),
    "hallucinations": ("Hallucinations", "She sees things that aren't there."),
    "false_rest": ("False Sleep", "Sleep only gives her part of her mana back."),
    "torn_focus": ("Torn Focus", "Magic and veil eat more mana."),
    "dread": ("Paralysis", "Fear paralyzes her – everything costs more stamina."),
    "fraying_mind": ("Fraying Mind", "Magic costs more, food and sleep help less."),
    "dark_affinity": ("Dark Affinity", "Her magic costs less mana."),
    "greedy_soul": ("Greedy Soul", "Nothing fills her anymore."),
    "insatiable": ("Insatiable", "Blood gives her more, food even less."),
    "blood_thirst": ("Bloodthirst", "Blood gives her more mana."),
    "restless_heart": ("Restless Heart", "Her heart races – stamina barely returns."),
    "possessed": ("Possession", "Harder blows, but her body cramps."),
    "overflow": ("Overflow", "She can carry more mana."),
    "leaking_power": ("Leaking Power", "Her veil burns more mana."),
    "bursting_heart": ("Bursting Heart", "The power tears her apart – stamina fades."),
    "longing": ("Longing", "Her magic costs less – she fights for Fira."),
    "devotion": ("Devotion", "Food heals her better."),
    "grief": ("Grief", "She left Fira behind in his cage. Almost everything is harder for her – until she frees him."),
}

# ---------------------------------------------------------------------------
# Menus, HUD and other interface text
# ---------------------------------------------------------------------------
STAGE_NAMES = ["Hatchling", "Young Dragoness", "Dark Dragoness"]
SUBTITLE = "A survival metroidvania about a little dark dragoness"
WARN_KEYWORD = "DELETED"
UI = {
    "new_game": "New Game", "continue": "Continue", "controls": "Controls", "credits": "Credits",
    "settings": "Settings", "quit": "Quit",
    "overwrite": "Overwrite the existing save?", "yes": "Yes", "no": "No",
    "pause": "Pause", "resume": "Resume", "main_menu": "Main Menu",
    "pause_note": "Progress is only saved when she sleeps.",
    "mastery": "Mana training {pct}%",
    "mastery_adult": "  ·  Mana +{bonus}  ·  Spell power ×{mult}",
    "mastery_young": "  ·  pays off once she is fully grown",
    "adaptation": "     Light tolerance {pct}%",
    "nature": "Shadowra's nature:  {title}",
    "ways": "Paths:  ",
    "affection_stats": "Affection {a}",
    "abilities": "Abilities: ",
    "journey_stats": "Mana training {m}%   ·   Light tolerance {a}%",
    "her_nature": "Her nature: {title}",
    "her_ways": "Her paths: ",
    "stones": "Shadowstones awakened: {n}/3",
    "grove": "Elven Grove: Shadowra {fate}",
    "hugs": "Hugs: {total}   ·   Creatures who love her: {loved}",
    "enter_menu": "[Enter] Main Menu",
    "story_goes_on": "The story goes on – in the north, in the snowlands.",
    "continue_or_menu": "[Enter] Keep playing   ·   [Esc] Main Menu",
    "save_deleted": "Your save has been deleted.",
    "new_item": "New: ",
    "rest_food": "Eat & Drink  ({food})",
    "rest_empty": "empty",
    "rest_sleep": "Sleep  (restore mana, save)",
    "rest_leave": "Move on",
    "rest_prompt": "Shadowra settles down. What should she do?",
    "altar": "Altar",
    "eat_msg": "Shadowra eats ({food}) and drinks from the spring.",
    "drink_only": " She only drinks a little water.",
    "boss_name": "Mafor, the Light Tyrant",
    "prompt_rest": "[E] Rest",
    "prompt_eat": "[E] Eat",
    "language": "Language",
    "back": "Back",
    "settings_hint": "[A / D] change   ·   [Enter / Esc] back",
    "cheats": "Cheats: {names}",
}
HELP = [
    ("A / D", "Walk"),
    ("Shift", "Run (stamina)"),
    ("Space", "Jump  /  hold: glide  /  in the air: wingbeat"),
    ("J", "Claw combo   (S + J in the air: dive)"),
    ("K", "Tail whip"),
    ("L", "Dark bolt (mana)"),
    ("I", "Hold for Dark Flame (mana)"),
    ("U", "Blood Drain (once learned)"),
    ("Q", "Shadow dash (stamina)"),
    ("E", "Eat / Rest / Talk"),
    ("Esc", "Pause"),
]
CHEAT_NAMES = {"infinite mana": "Infinite Mana", "infinite stamina": "Infinite Stamina",
               "infinite health": "Infinite Health"}
HELP_NOTES = [
    "Health only heals by eating (altars, prey) or blood.",
    "Mana only returns through sleep, shadow crystals or blood.",
    "Stamina recovers quickly on the ground – not in the air.",
]
