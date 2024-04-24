from enum import StrEnum
from typing import Optional, Self

from dnd5e_card_generator.config import COLORS, ICONS, TRANSLATIONS
from dnd5e_card_generator.utils import pascal_case_to_snake_case


class TranslatedStrEnum(StrEnum):
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
        return cls.reversed_translations()[lang].get(s)

    @classmethod
    def to_pattern(cls, lang: str) -> str:
        return (
            r"(?<=[\s\()])(" + r"|".join(cls.translations()[lang].values()) + r")(?=\s)"
        )

    @property
    def color(self) -> str:
        return COLORS[self.config_key()][self.name]

    @property
    def icon(self) -> str:
        return ICONS[self.config_key()][self.name]
