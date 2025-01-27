from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Optional, Self, cast, Literal, get_args as get_type_args


from dnd5e_card_generator.config import Config
from dnd5e_card_generator.utils import pascal_case_to_snake_case

from .utils import game_icon

Language = Literal["en", "fr"]


def validate_language(lang: str):
    supported_languages = get_type_args(Language)
    if lang not in supported_languages:
        msg = (
            f"Unsupported language {lang}. Only {', '.join(supported_languages[:-1])} "
            f"and {supported_languages[-1]} are supported."
        )
        print(f"ERROR: {msg}")  # The exception is gobbled up by argparse, so we print the message
        raise ValueError(msg)


class BaseDataclass:
    def to_dict(self) -> dict:
        return asdict(self)  # pyright: ignore


@dataclass
class CliArg(BaseDataclass):
    lang: str
    slug: str

    @classmethod
    def from_str(cls, s: str) -> "CliArg":
        lang, slug = s.split(":")
        validate_language(lang)
        return cls(lang=lang, slug=slug)


class CliSpell(CliArg): ...


class CliMagicItem(CliArg): ...


class CliFeat(CliArg): ...


class CliEldrichtInvocation(CliArg): ...


class CliMonster(CliArg): ...


class CliBackground(CliArg): ...


@dataclass
class CliClassFeature(BaseDataclass):
    class_name: str
    title: str
    lang: str

    @classmethod
    def from_str(cls, s: str) -> "CliClassFeature":
        lang, class_name, title = s.split(":", 2)  # The title itself can contain semicolumns
        validate_language(lang)
        return cls(title=title, class_name=class_name, lang=lang)


@dataclass
class CliAncestryFeature(BaseDataclass):
    ancestry: str
    sub_ancestry: str
    lang: str

    @classmethod
    def from_str(cls, s: str) -> "CliAncestryFeature":
        if s.count(":") == 1:
            lang, ancestry = s.split(":")
            sub_ancestry = ""
        else:
            lang, ancestry, sub_ancestry = s.split(":")
        validate_language(lang)
        return cls(ancestry=ancestry, sub_ancestry=sub_ancestry, lang=lang)


@dataclass
class CliSpellFilter(BaseDataclass):
    lang: str
    class_name: str
    min_level: int
    max_level: int

    @classmethod
    def from_str(cls, s: str) -> "CliSpellFilter":
        lang, class_name, min_level, max_level = s.split(":")
        validate_language(lang)
        return cls(
            lang=lang,
            class_name=class_name,
            min_level=int(min_level),
            max_level=int(max_level),
        )


class BaseModel(StrEnum):
    @classmethod
    def config_key(cls):
        return pascal_case_to_snake_case(cls.__name__)

    @classmethod
    def fr_translations(cls) -> dict:
        return Config.TRANSLATIONS[cls.config_key()]

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
    def from_str(cls, s: str, lang: str) -> Self:
        return cls.reversed_translations()[lang][s.lower()]

    @classmethod
    def pattern_options(cls, lang: str) -> list[str]:
        # We make a pattern with the largest elements first, to avoid partial matches
        return sorted(
            cls.translations()[lang].values(),
            key=lambda item: len(item),
            reverse=True,
        )

    @classmethod
    def possible_values_as_pattern(cls, lang: str) -> str:
        vals = cls.pattern_options(lang)
        return r"(" + r"|".join(vals) + r")"

    @classmethod
    def as_pattern(cls, lang: str) -> str:
        return r"(?<=[\s\()])" + cls.possible_values_as_pattern(lang) + r"(?=[\s\.])"

    @property
    def color(self) -> str:
        return Config.COLORS[self.config_key()][self.name]

    @property
    def icon(self) -> str:
        return Config.ICONS[self.config_key()][self.name]


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
        return r"dégâts (de (type )?|d')?(" + r"|".join(cls.translations()[lang].values()) + r")s?"


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
            (name, cast(DamageDie, value))
            for name, value in cls._member_map_.items()
            if value != "d100"
        ]

    @classmethod
    def from_str(cls, s: str) -> Self:
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


class CharacterAncestry(BaseModel):
    dragonborn = "dragonborn"
    dwarf = "dwarf"
    elf = "elf"
    gnome = "gnome"
    half_elf = "half-elf"
    half_orc = "half_orc"
    halfling = "halfling"
    human = "human"
    tieflin = "tieflin"


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


class Action(BaseModel):
    attack = "attack"
    dash = "dash"
    disengage = "disengage"
    dodge = "dodge"
    help = "help"
    hide = "hide"
    ready = "ready"
    search = "search"

    @classmethod
    def pattern_options(cls, lang: str) -> list[str]:
        values = super().pattern_options(lang)
        return [val.capitalize() for val in values]
