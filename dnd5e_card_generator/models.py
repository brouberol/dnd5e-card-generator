from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Self

from .translator import TranslatedStrEnum
from .utils import game_icon


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
            "common": "5C4B51",
            "uncommon": "8CBEB2",
            "rare": "BDD684",
            "very_rare": "F3B562",
            "legendary": "F06060",
            "artifact": "9575CD",
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
            "armor": "lamellar",
            "weapon": "shard-sword",
            "ring": "ring",
            "wand": "lunar-wand",
            "wondrous_item": "eclipse-flare",
            "staff": "bo",
            "rod": "flanged-mace",
            "potion": "potion-ball",
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
            "radiant": "sun",
            "slashing": "axe-sword",
            "thunder": "crowned-explosion",
        }
        return damage_to_icon[self.value]

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
    def fr_translations(self) -> dict[str, str]:
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
        return shape_to_icon[self.value]


class SpellType(TranslatedStrEnum):
    aoe = "aoe"
    buff = "buff"
    debuff = "debuff"
    utility = "utility"
    healing = "healing"
    damage = "damage"

    @classmethod
    def fr_translations(self) -> dict[str, str]:
        return {
            "aoe": "zone",
            "buff": "bonus",
            "debuff": "malus",
            "healing": "soins",
            "utility": "utilitaire",
            "damage": "offensif",
        }

    @property
    def icon(self) -> str:
        type_to_icon = {
            "aoe": "fire-ring",
            "buff": "armor-upgrade",
            "debuff": "armor-downgrade",
            "healing": "health-potion",
            "utility": "toolbox",
            "damage": "bloody-sword",
        }
        return type_to_icon[self.value]


class DamageDie(StrEnum):
    d4 = "a"
    d6 = "b"
    d8 = "c"
    d10 = "d"
    d12 = "e"
    d20 = "f"

    def __str__(self):
        return f"<dice>{self.value}</dice>"

    @classmethod
    def from_str(self, s: str) -> Self:
        return getattr(DamageDie, s)


@dataclass
class DamageFormula:
    num_die: int
    damage_die: DamageDie
    damage_type: DamageType | None

    def render(self) -> str:
        dice = f" {self.num_die}{str(self.damage_die)}"
        if self.damage_type and self.damage_type.icon:
            return f"{dice}{game_icon(self.damage_type.icon)}"
        else:
            return dice


@dataclass
class Card:
    color: str
    title: str
    icon: str | None
    contents: list[str]
    count: int = field(default=1)

    def to_dict(self) -> dict:
        return asdict(self)
