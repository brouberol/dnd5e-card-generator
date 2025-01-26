class Config:
    BYPASS_CACHE: bool = False
    COLORS = {
        "class_feature": "indianred",
        "background": "#ff9aac",
        "feat": "#37352b",
        "feat_title": "#d6a44a",
        "eldricht_invocation": "#994094",
        # https://colordesigner.io/color-scheme-builder#5C4B51-8CBEB2-F2EBBF-F3B562-F06060
        "magic_item_rarity": {
            "common": "#5C4B51",
            "uncommon": "#8CBEB2",
            "rare": "#BDD684",
            "very_rare": "#F3B562",
            "legendary": "#F06060",
            "artifact": "#9575CD",
        },
        # https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
        "spell": {
            0: "#277DA1",
            1: "#577590",
            2: "#4D908E",
            3: "#43AA8B",
            4: "#90BE6D",
            5: "#F9C74F",
            6: "#F8961E",
            7: "#F9844A",
            8: "#F3722C",
            9: "#F94144",
        },
        "ancestry_feature": "#458f36de",
    }

    # All of these icons come from https://game-icons.net/
    ICONS = {
        "ancestry_feature": "elf-helmet",
        "background": "fluffy-trefoil",
        "character_class": {
            "artificer": "fire-tail",
            "barbarian": "sharp-axe",
            "bard": "harp",
            "cleric": "thor-hammer",
            "druid": "sickle",
            "monk": "fist",
            "paladin": "knight-banner",
            "ranger": "high-shot",
            "rogue": "knife-thrust",
            "sorcerer": "dragon-breath",
            "warlock": "warlock-eye",
            "warrior": "axe-sword",
            "wizard": "robe",
        },
        "feat": "stars-stack",
        "eldricht_invocation": "cursed-star",
        "magic_item_kind": {
            "armor": "lamellar",
            "weapon": "shard-sword",
            "ring": "ring",
            "wand": "lunar-wand",
            "wondrous_item": "eclipse-flare",
            "staff": "bo",
            "rod": "flanged-mace",
            "potion": "potion-ball",
        },
        "magic_item": {"attunement": "empty-hourglass"},
        "damage_type": {
            "acid": "acid",
            "bludgeoning": "hammer-drop",
            "cold": "ice-spear",
            "fire": "celebration-fire",
            "force": "mighty-force",
            "lightning": "lightning-tree",
            "necrotic": "burning-skull",
            "piercing": "arrowhead",
            "poison": "poison-bottle",
            "psychic": "psychic-waves",
            "radiant": "sun",
            "slashing": "axe-sword",
            "thunder": "crowned-explosion",
        },
        "spell_shape": {
            "circle": "circle",
            "cone": "ringed-beam",
            "cube": "cube",
            "cylinder": "database",
            "hemisphere": "onigori",
            "line": "straight-pipe",
            "radius": "circle",
            "sphere": "glass-ball",
            "square": "square",
            "wall": "brick-wall",
        },
        "spell_type": {
            "aoe": "fire-ring",
            "buff": "armor-upgrade",
            "debuff": "armor-downgrade",
            "healing": "health-potion",
            "utility": "toolbox",
            "damage": "bloody-sword",
        },
        "spell_default": "scroll-unfurled",
        "spell_properties": {
            "casting_time": "ink-swirl",
            "casting_range": "hand",
            "effect_duration": "sands-of-time",
            "casting_components": "drink-me",
            "concentration": "eye-target",
            "ritual": "pentacle",
        },
    }
    # Warn: make sure every translation is lowercased
    TRANSLATIONS = {
        "magic_item_kind": {
            "armor": "armure",
            "potion": "potion",
            "ring": "anneau",
            "rod": "sceptre",
            "staff": "bâton",
            "wand": "baguette",
            "weapon": "arme",
            "wondrous_item": "objet merveilleux",
        },
        "magic_item_rarity": {
            "common": "commun",
            "uncommon": "peu commun",
            "rare": "rare",
            "very_rare": "très rare",
            "legendary": "légendaire",
            "artifact": "artéfact",
        },
        "magic_school": {
            "abjuration": "abjuration",
            "divination": "divination",
            "enchantment": "enchantement",
            "evocation": "évocation",
            "illusion": "illusion",
            "conjuration": "invocation",
            "necromancy": "nécromancie",
            "transmutation": "transmutation",
        },
        "damage_type": {
            "acid": "acide",
            "bludgeoning": "contondant",
            "cold": "froid",
            "fire": "feu",
            "force": "force",
            "lightning": "foudre",
            "necrotic": "nécrotique",
            "piercing": "perforant",
            "poison": "poison",
            "psychic": "psychique",
            "radiant": "radiant",
            "slashing": "tranchant",
            "thunder": "tonnerre",
        },
        "spell_shape": {
            "circle": "cercle",
            "cone": "cône",
            "cube": "cube",
            "cylinder": "cylindre",
            "hemisphere": "hémisphère",
            "line": "ligne",
            "sphere": "sphère",
            "square": "carré",
            "wall": "mur",
            "radius": "rayon",
        },
        "spell_type": {
            "aoe": "zone",
            "buff": "bonus",
            "debuff": "malus",
            "healing": "soins",
            "utility": "utilitaire",
            "damage": "offensif",
        },
        "character_class": {
            "artificer": "artificier",
            "barbarian": "barbare",
            "bard": "barde",
            "cleric": "clerc",
            "druid": "druide",
            "monk": "moine",
            "paladin": "paladin",
            "ranger": "rodeur",
            "rogue": "roublard",
            "sorcerer": "ensorceleur",
            "warlock": "occultiste",
            "warrior": "guerrier",
            "wizard": "magicien",
        },
        "character_ancestry": {
            "dragonborn": "drakéide",
            "dwarf": "nain",
            "elf": "elfe",
            "gnome": "gnome",
            "half_elf": "demi-elfe",
            "half_orc": "demi-orque",
            "halfling": "halfelin",
            "human": "humain",
            "tieflin": "tieflin",
        },
        "creature_size": {
            "tiny": "tp",
            "small": "p",
            "medium": "m",
            "large": "g",
            "huge": "tg",
            "gargantuan": "gig",
        },
        "creature_type": {
            "aberration": "aberration",
            "beast": "bête",
            "celestial": "céleste",
            "construct": "artificiel",
            "dragon": "dragon",
            "elemental": "élémentaire",
            "fey": "fée",
            "fiend": "fiélon",
            "giant": "géant",
            "humanoid": "humanoïde",
            "monstrosity": "monstruosité",
            "ooze": "vase",
            "plant": "plante",
            "undead": "mort-vivant",
        },
    }
