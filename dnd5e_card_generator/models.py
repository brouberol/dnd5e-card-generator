from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Optional, Self

from .translator import TranslatedStrEnum
from .utils import game_icon


class MagicItemRarity(TranslatedStrEnum):
    """Describes the rarity of a magic item"""

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


class MagicItemKind(TranslatedStrEnum):
    """Describes the type of object of a magic item"""

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
    """List and translate all magic schools"""

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
    """Translate and assign an icon to all types of damage"""

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
    def from_5esheet_tag(cls, tag: str) -> "DamageType":
        return cls.reversed_en_translations()[tag]

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
    """Translate and assign an icon to all shapes of spells"""

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
    def from_5esheet_tag(cls, tag: str) -> Optional["SpellShape"]:
        mapping = {
            "C": SpellShape.cube,
            "H": SpellShape.hemisphere,
            "L": SpellShape.line,
            "N": SpellShape.cone,
            "Q": SpellShape.square,
            "R": SpellShape.circle,
            "S": SpellShape.sphere,
            "W": SpellShape.wall,
            "Y": SpellShape.cylinder,
        }
        return mapping.get(tag)

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
    """Translate and assign an icon to all types of spells

    A type of spell describes the kind of general effect it has, and could be
    used in the decision process of choosing the right spell for the right
    situation.

    """

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
    """Representation of the different damage die"""

    d4 = "a"
    d6 = "b"
    d8 = "c"
    d10 = "d"
    d12 = "e"
    d20 = "f"
    d100 = "d100"

    def __str__(self):
        if self.value != DamageDie.d100:
            return f"<dice>{self.value}</dice>"
        else:
            return "d100"

    @classmethod
    def values_with_icons(cls) -> list[tuple[str, "DamageDie"]]:
        return [
            (name, value) for name, value in cls._member_map_.items() if value != "d100"
        ]

    @classmethod
    def from_str(self, s: str) -> Self:
        return getattr(DamageDie, s)


@dataclass
class DamageFormula:
    """Representation of a damage formula.

    Ex: 2d10 radiant damages

    """

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
    """Wrapper around the data contained in a physical item or spell card"""

    color: str
    title: str
    icon: str | None
    contents: list[str]
    count: int = field(default=1)

    def to_dict(self) -> dict:
        return asdict(self)
