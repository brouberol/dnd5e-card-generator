import math
import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Optional, Self

from dnd5e_card_generator.config import COLORS, ICONS, TRANSLATIONS
from dnd5e_card_generator.utils import pascal_case_to_snake_case

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


class CliEldrichtInvocation(CliArg): ...


class CliMonster(CliArg): ...


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


class BaseModel(StrEnum):
    @classmethod
    def config_key(cls):
        return pascal_case_to_snake_case(cls.__name__)

    @classmethod
    def fr_translations(cls) -> dict:
        return TRANSLATIONS[cls.config_key()]

    @classmethod
    def en_translations(cls) -> dict:
        return {str(k): str(v) for k, v in cls._member_map_.items()}

    @classmethod
    def translations(cls) -> dict[str, dict]:
        return {
            "fr": cls.fr_translations(),
            "en": cls.en_translations(),
        }

    @classmethod
    def reverse_lang_translations(cls, lang: str) -> dict[str, Self]:
        return {
            v: getattr(cls, k.replace(" ", "_"))
            for k, v in getattr(cls, f"{lang}_translations")().items()
        }

    @classmethod
    def reversed_fr_translations(cls) -> dict[str, Self]:
        return cls.reverse_lang_translations("fr")

    @classmethod
    def reversed_en_translations(cls) -> dict[str, Self]:
        return cls.reverse_lang_translations("en")

    @classmethod
    def reversed_translations(cls) -> dict[str, dict[str, Self]]:
        return {
            "fr": cls.reversed_fr_translations(),
            "en": cls.reversed_en_translations(),
        }

    def translate(self, lang: str) -> str:  # type: ignore
        return self.translations()[lang][self.name]

    @classmethod
    def from_str(cls, s: str, lang: str) -> Optional[Self]:
        return cls.reversed_translations()[lang].get(s.lower())

    @classmethod
    def pattern_options(cls, lang: str) -> str:
        # We make a pattern with the largest elements first, to avoid partial matches
        vals = sorted(
            cls.translations()[lang].values(),
            key=lambda item: len(item),
            reverse=True,
        )
        return r"(" + r"|".join(vals) + r")"

    @classmethod
    def as_pattern(cls, lang: str) -> str:
        return r"(?<=[\s\()])" + cls.pattern_options(lang) + r"(?=\s)"

    @property
    def color(self) -> str:
        return COLORS[self.config_key()][self.name]

    @property
    def icon(self) -> str:
        return ICONS[self.config_key()][self.name]


class MagicItemRarity(BaseModel):
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


class MagicItemKind(BaseModel):
    """Describes the type of object of a magic item"""

    wondrous_item = "wondrous item"
    ring = "ring"
    weapon = "weapon"
    wand = "wand"
    armor = "armor"
    staff = "staff"
    potion = "potion"
    rod = "rod"


class MagicSchool(BaseModel):
    """List and translate all magic schools"""

    abjuration = "abjuration"
    divination = "divination"
    enchantment = "enchantment"
    conjuration = "conjuration"
    illusion = "illusion"
    evocation = "evocation"
    necromancy = "necromancy"
    transmutation = "transmutation"


class DamageType(BaseModel):
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
    def as_pattern(cls, lang: str) -> str:
        return (
            r"dégâts (de (type )?|d')?("
            + r"|".join(cls.translations()[lang].values())
            + r")s?"
        )


class SpellShape(BaseModel):
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


class SpellType(BaseModel):
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


class CharacterClass(BaseModel):
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
    damage_type_1: DamageType | None
    damage_type_2: DamageType | None

    def render(self) -> str:
        parts = [str(self.num_die), self.damage_die.render()]
        if self.damage_type_1 and self.damage_type_1.icon:
            parts.append(game_icon(self.damage_type_1.icon))
        if self.damage_type_2 and self.damage_type_2.icon:
            parts.extend(["/", game_icon(self.damage_type_2.icon)])
        return " " + "".join(parts)


@dataclass
class Card(BaseDataclass):
    """Wrapper around the data contained in a physical item or spell card"""

    color: str
    title: str
    icon: str | None
    contents: list[str]
    count: int = field(default=1)
    background_image: str | None = field(default=None)


class CreatureSize(BaseModel):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large"
    huge = "huge"
    gargantuan = "gargantuan"

    @classmethod
    def as_pattern(cls, lang: str) -> str:
        if lang == "fr":
            return r"(?<=de taille )" + cls.pattern_options(lang)
        return cls.pattern_options(lang)


@dataclass
class Attribute:
    value: int

    @property
    def modifier(self) -> int:
        return math.floor((self.value - 10) / 2)


@dataclass
class CreatureAttributes:
    charisma: Attribute
    constitution: Attribute
    dexterity: Attribute
    intelligence: Attribute
    strength: Attribute
    wisdom: Attribute


@dataclass
class CreatureSpeed:
    speed: int
    unit: str
    type: str = field(default="base")

    @classmethod
    def from_str(cls, s: str) -> Self:
        match = re.match(r"((?P<type>\w+) )?(?P<speed>\d+) (?P<unit>\w+)", s)
        data = match.groupdict()
        if data["type"] is None:
            data["type"] = "base"
        return CreatureSpeed(**data)


class CreatureType(BaseModel):
    aberration = "aberration"
    beast = "beast"
    celestial = "celestial"
    construct = "construct"
    dragon = "dragon"
    elemental = "elemental"
    fey = "fey"
    fiend = "fiend"
    giant = "giant"
    humanoid = "humanoid"
    monstrosity = "monstrosity"
    ooze = "ooze"
    plant = "plant"
    undead = "undead"


@dataclass
class HitPointsFormula:
    die: DamageDie
    num_die: int
    bonus: int

    @classmethod
    def from_str(cls, s: str) -> Self:
        match = re.match(r"(?P<num_die>\d+)(?P<die>d\d+)\s?\+\s?(?P<bonus>\d+)", s)
        data = match.groupdict()
        data["die"] = DamageDie.from_str(data["die"])
        return HitPointsFormula(**data)
