from enum import IntEnum, StrEnum
from pathlib import Path

from .const import IMAGES_DIR


class Rarity(IntEnum):
    common = 0
    uncommon = 1
    rare = 2
    very_rare = 3
    legendary = 4
    artifact = 5

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


class ItemType:
    wondrous_item = "wondrous_item"
    ring = "ring"
    weapon = "weapon"
    wand = "wand"
    armor = "armor"
    staff = "staff"
    potion = "potion"
    rod = "rod"

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


class MagicSchool(StrEnum):
    abjuration = "abjuration"
    divination = "divination"
    enchantment = "enchantment"
    conjuration = "conjuration"
    illusion = "illusion"
    evocation = "evocation"
    necromancy = "necromancy"
    transmutation = "transmutation"

    @classmethod
    def from_str(cls, school: str, lang: str) -> "MagicSchool":
        school_by_lang = {
            "fr": {
                "abjuration": MagicSchool.abjuration,
                "divination": MagicSchool.divination,
                "enchantement": MagicSchool.enchantment,
                "évocation": MagicSchool.evocation,
                "illusion": MagicSchool.illusion,
                "invocation": MagicSchool.conjuration,
                "nécromancie": MagicSchool.necromancy,
                "transmutation": MagicSchool.transmutation,
            },
            "en": {
                "abjuration": MagicSchool.abjuration,
                "divination": MagicSchool.divination,
                "enchantment": MagicSchool.enchantment,
                "evocation": MagicSchool.evocation,
                "illusion": MagicSchool.illusion,
                "conjuration": MagicSchool.conjuration,
                "necromancy": MagicSchool.necromancy,
                "transmutation": MagicSchool.transmutation,
            },
        }
        return school_by_lang[lang][school]

    def translate(self) -> str: ...

    @property
    def symbol_file_path(self) -> Path:
        return IMAGES_DIR / f"{self.value}.png"
