from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Optional, Self

from .translator import TranslatedStrEnum
from .utils import game_icon


class BaseDataclass:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CliArg(BaseDataclass):
    lang: str
    slug: str

    @classmethod
    def from_str(cls, s: str) -> "CliArg":
        lang, slug = s.split(":")
        return cls(lang=lang, slug=slug)


class CliSpell(CliArg): ...


class CliMagicItem(CliArg): ...


class CliFeat(CliArg): ...


@dataclass
class CliClassFeature(BaseDataclass):
    class_name: str
    title: str
    lang: str

    @classmethod
    def from_str(cls, s: str) -> "CliClassFeature":
        class_name, _, title = s.partition(":")
        return cls(title=title, class_name=class_name, lang="fr")


@dataclass
class CliSpellFilter(BaseDataclass):
    class_name: str
    min_level: int
    max_level: int

    @classmethod
    def from_str(cls, s: str) -> "CliSpellFilter":
        class_name, min_level, max_level = s.split(":")
        return cls(
            class_name=class_name, min_level=int(min_level), max_level=int(max_level)
        )


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


class MagicItemKind(TranslatedStrEnum):
    """Describes the type of object of a magic item"""

    wondrous_item = "wondrous item"
    ring = "ring"
    weapon = "weapon"
    wand = "wand"
    armor = "armor"
    staff = "staff"
    potion = "potion"
    rod = "rod"


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


class DamageDie(StrEnum):
    """Representation of the different damage die"""

    d4 = "a"
    d6 = "b"
    d8 = "c"
    d10 = "d"
    d12 = "e"
    d20 = "f"
    d100 = "d100"

    def render(self):
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


class CharacterClass(TranslatedStrEnum):
    artificer = "artificer"
    barbarian = "barbarian"
    bard = "bard"
    cleric = "cleric"
    druid = "druid"
    monk = "monk"
    paladin = "paladin"
    ranger = "ranger"
    rogue = "rogue"
    sorcerer = "sorcerer"
    warlock = "warlock"
    warrior = "warrior"
    wizard = "wizard"


@dataclass
class DamageFormula:
    """Representation of a damage formula.

    Ex: 2d10 radiant damages

    """

    num_die: int
    damage_die: DamageDie
    damage_type: DamageType | None

    def render(self) -> str:
        dice = f" {self.num_die}{self.damage_die.render()}"
        if self.damage_type and self.damage_type.icon:
            return f"{dice}{game_icon(self.damage_type.icon)}"
        else:
            return dice


@dataclass
class Card(BaseDataclass):
    """Wrapper around the data contained in a physical item or spell card"""

    color: str
    title: str
    icon: str | None
    contents: list[str]
    count: int = field(default=1)
    background_image: str | None = field(default=None)
