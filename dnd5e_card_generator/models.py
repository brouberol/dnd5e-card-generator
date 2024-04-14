from enum import StrEnum

from .translator import TranslatedStrEnum


class Rarity(TranslatedStrEnum):
    common = "common"
    uncommon = "uncommon"
    rare = "rare"
    very_rare = "very rare"
    legendary = "legendary"
    artifact = "artifact"

    def __int__(self):
        return {
            "common": 0,
            "uncommon": 1,
            "rare": 2,
            "very_rare": 3,
            "legendary": 4,
            "artifact": 5,
        }[self.name]

    @classmethod
    def fr_translations(self) -> dict:
        return {
            "common": "commun",
            "uncommon": "peu commun",
            "rare": "rare",
            "very_rare": "très rare",
            "legendary": "légendaire",
            "artifact": "artéfact",
        }

    @property
    def color(self) -> str:
        # https://colordesigner.io/color-scheme-builder#5C4B51-8CBEB2-F2EBBF-F3B562-F06060
        colors_by_rarity = {
            Rarity.common: "5C4B51",
            Rarity.uncommon: "8CBEB2",
            Rarity.rare: "BDD684",
            Rarity.very_rare: "F3B562",
            Rarity.legendary: "F06060",
            Rarity.artifact: "9575CD",
        }
        return colors_by_rarity[self.value]


class ItemType(TranslatedStrEnum):
    wondrous_item = "wondrous_item"
    ring = "ring"
    weapon = "weapon"
    wand = "wand"
    armor = "armor"
    staff = "staff"
    potion = "potion"
    rod = "rod"

    @classmethod
    def fr_translations(cls):
        return {
            "armor": "armure",
            "potion": "potion",
            "ring": "anneau",
            "rod": "sceptre",
            "staff": "bâton",
            "wand": "baguette",
            "weapon": "arme",
            "wondrous_item": "objet merveilleux",
        }

    @property
    def icon(self) -> str:
        icon_by_type = {
            ItemType.armor: "lamellar",
            ItemType.weapon: "shard-sword",
            ItemType.ring: "ring",
            ItemType.wand: "lunar-wand",
            ItemType.wondrous_item: "eclipse-flare",
            ItemType.staff: "bo",
            ItemType.rod: "flanged-mace",
            ItemType.potion: "potion-ball",
        }
        return icon_by_type[self.value]


class MagicSchool(TranslatedStrEnum):
    abjuration = "abjuration"
    divination = "divination"
    enchantment = "enchantment"
    conjuration = "conjuration"
    illusion = "illusion"
    evocation = "evocation"
    necromancy = "necromancy"
    transmutation = "transmutation"

    @classmethod
    def fr_translations(cls):
        return {
            "abjuration": "abjuration",
            "divination": "divination",
            "enchantment": "enchantement",
            "evocation": "évocation",
            "illusion": "illusion",
            "conjuration": "invocation",
            "necromancy": "nécromancie",
            "transmutation": "transmutation",
        }


class DamageType(TranslatedStrEnum):
    acid = "acid"
    bludgeoning = "bludgeoning"
    cold = "cold"
    fire = "fire"
    force = "force"
    lightning = "lightning"
    necrotic = "necrotic"
    piercing = "piercing"
    poison = "poison"
    psychic = "psychic"
    radiant = "radiant"
    slashing = "slashing"
    thunder = "thunder"
    healing = "healing"

    @classmethod
    def fr_translations(self) -> dict:
        return {
            "acid": "acide",
            "bludgeoning": "contondant",
            "cold": "froid",
            "fire": "feu",
            "force": "force",
            "lightning": "éclair",
            "necrotic": "nécrotique",
            "piercing": "perforant",
            "poison": "poison",
            "psychic": "psychique",
            "radiant": "radiant",
            "slashing": "tranchant",
            "thunder": "tonnerre",
            "healing": "soin",
        }

    @property
    def icon(self) -> str:
        damage_to_icon = {
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
            "radiant": "sunbeams",
            "slashing": "axe-sword",
            "thunder": "crowned-explosion",
        }
        return damage_to_icon.get(self.value)

    @classmethod
    def to_pattern(cls, lang: str) -> str:
        return (
            r"dégâts (de (type )?|d')?("
            + r"|".join(cls.translations()[lang].values())
            + r")s?"
        )


class SpellShape(TranslatedStrEnum):
    circle = "circle"
    cone = "cone"
    cube = "cube"
    cylinder = "cylinder"
    hemisphere = "hemisphere"
    line = "line"
    radius = "radius"
    sphere = "sphere"
    square = "square"
    wall = "wall"

    @classmethod
    def fr_translations(self) -> dict:
        return {
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
        }

    @property
    def icon(self) -> str:
        shape_to_icon = {
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
        }
        return shape_to_icon.get(self.value)


class SpellType(StrEnum):
    aoe = "aoe"
    buff = "buff"
    debuff = "debuff"
    utility = "utility"
    healing = "healing"

    @property
    def icon(self):
        type_to_icon = {
            "aoe": "fire-ring",
            "buff": "armor-upgrade",
            "debuff": "armor-downgrade",
            "healing": "health-potion",
            "utility": "toolbox",
        }
        return type_to_icon.get(self.value)
