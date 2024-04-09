import base64
import re
from dataclasses import dataclass
from typing import Optional

from .models import DamageType, MagicSchool, SpellShape
from .utils import damage_type_text, game_icon, humanize_level


@dataclass
class Spell:
    title: str
    lang: str
    level: int
    school: MagicSchool
    casting_time: str
    casting_range: str
    effect_duration: str
    verbal: bool
    somatic: bool
    material: bool
    paying_components: str
    concentration: bool
    ritual: bool
    text: list[str]
    upcasting_text: str
    tags: list[str]
    damage_type: Optional[DamageType]
    shape: Optional[SpellShape]

    @property
    def color(self) -> str:
        # https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
        spell_colors_by_level = {
            0: "277DA1",
            1: "577590",
            2: "4D908E",
            3: "43AA8B",
            4: "90BE6D",
            5: "F9C74F",
            6: "F8961E",
            7: "F9844A",
            8: "F3722C",
            9: "F94144",
        }
        return "#" + spell_colors_by_level[self.level]

    @property
    def background_image_base64(self):
        return base64.b64encode(self.school.background_file_path.read_bytes()).decode(
            "utf-8"
        )

    @property
    def spell_casting_extra(self):
        spell_extra = []
        if ritual_text := self.ritual_text:
            spell_extra.append(ritual_text)
        if concentration_text := self.concentration_text:
            spell_extra.append(concentration_text)
        spell_extra_text = " ".join(spell_extra)
        if spell_extra_text:
            spell_extra_text = f"- {spell_extra_text}"
        return spell_extra_text

    @property
    def spell_casting_components(self):
        components = []
        if self.verbal:
            components.append("V")
        if self.somatic:
            components.append("S")
        if self.material:
            components.append("M")
        return " ".join(components)

    @property
    def spell_damage_type_icon(self):
        if not self.damage_type:
            return "scroll-unfurled"
        return self.damage_type.icon

    @property
    def subtitle(self) -> str:
        if self.lang == "fr":
            if self.level == 0:
                return f"Tour de magie - {self.school_text}"
            else:
                return f"Niveau {self.level} - {self.school_text}"
        else:
            if self.level == 0:
                return f"Cantrip - {self.school_text}"
            else:
                return f"{humanize_level(self.level)} level - {self.school_text}"

    @property
    def school_text(self):
        return self.school.translate(self.lang).capitalize()

    @property
    def ritual_text(self):
        return "Rituel" if self.lang == "fr" else "Ritual"

    @property
    def casting_time_text(self) -> str:
        return "Temps d'invocation" if self.lang == "fr" else "Casting time"

    @property
    def casting_range_text(self) -> str:
        return "Portée" if self.lang == "fr" else "Range"

    @property
    def casting_components_text(self) -> str:
        return "Composants" if self.lang == "fr" else "Compoments"

    @property
    def effect_duration_text(self) -> str:
        return "Durée" if self.lang == "fr" else "Duration"

    @property
    def upcasting_section_title(self) -> str:
        return "Aux niveaux supérieurs" if self.lang == "fr" else "At higher levels"

    @property
    def spell_carac_text(self) -> str:
        if self.lang == "fr":
            return "le modificateur de votre caractéristique d'incantation"
        return "your spellcasting ability modifier"

    def _highlight(self, pattern: str, text: str) -> str:
        return re.sub(pattern, lambda match: f"<b>{match.group(0)}</b>", text)

    def fix_translation_mistakes(self, text: str) -> str:
        replacements = {"fr": {"de un dé": "d'un dé"}}
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    def highlight_saving_throw(self, text: str) -> str:
        saving_throw_pattern_by_lang = {
            "fr": r"jet de sauvegarde de \w+",
            "en": r"\w+ saving throw",
        }
        return self._highlight(saving_throw_pattern_by_lang[self.lang], text)

    def highlight_die_value(self, text: str) -> str:
        die_value_pattern = (
            r"\d+d\d+( \+ "
            + self.spell_carac_text
            + r"| "
            + damage_type_text(self.lang)
            + r")?"
        )
        return self._highlight(die_value_pattern, text)

    def highlight_spell_text(self, text: str) -> str:
        text = self.highlight_die_value(text)
        text = self.highlight_saving_throw(text)
        return text

    def shorten_upcasting_text(self) -> tuple[int, str]:
        upcasting_text = {
            "fr": [
                r"(Lorsque|Si) vous lancez ce sort en utilisant un emplacement de sort de niveau \d ou supérieur,",
                r" d'emplacement au-delà du niveau \d",
            ],
            "en": [
                r" When you cast this spell using a spell slot of \d\w+ level or higher,",
                r" for each slot level above \d(st|nd|rd|th)",
            ],
        }
        text = self.upcasting_text[:]
        for pattern in upcasting_text[self.lang]:
            if upcasting_match := re.search(pattern, text):
                text = text.replace(upcasting_match.group(), "").strip().capitalize()
        return text

    def shorten_effect_duration_text(self, text: str) -> str:
        replacements = {"fr": {"Jusqu'à": "≤"}}
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    @property
    def casting_range_text_value(self) -> str:
        parts = []
        if self.shape:
            shape_name = self.shape.translate(self.lang)
            shape_icon = game_icon(self.shape.icon)
            if shape_name in self.casting_range:
                parts.append(self.casting_range.replace(shape_name, shape_icon))
            else:
                parts.extend([self.casting_range, "-", shape_icon])
        else:
            parts = [self.casting_range]
        return " ".join(parts)

    @property
    def spell_parts(self) -> list[str]:
        return [
            f"text | {self.fix_translation_mistakes(self.highlight_spell_text(text_part))}"
            for text_part in self.text
        ]

    @property
    def upcasting_parts(self) -> list[str]:
        if not self.upcasting_text:
            return []
        shortened_upcasting_text = self.shorten_upcasting_text()
        shortened_upcasting_text = self.fix_translation_mistakes(
            shortened_upcasting_text
        )
        shortened_upcasting_text = self.highlight_spell_text(shortened_upcasting_text)

        return [
            f"section | {self.upcasting_section_title}",
            f"text | {shortened_upcasting_text}",
        ]

    @property
    def spell_properties_parts(self) -> list[str]:
        parts = []
        parts.append(f"property_inline | {game_icon('duration')} | {self.casting_time}")
        parts.append(
            f"property_inline | {game_icon('measure-tape')} | {self.casting_range_text_value}"
        )
        parts.append(
            f"property_inline | {game_icon('sands-of-time')} | {self.shorten_effect_duration_text(self.effect_duration)}"
        )
        parts.append(
            f"property_inline | {game_icon('drink-me')} | {self.spell_casting_components}"
        )
        if self.concentration:
            parts.append(f"property_inline | {game_icon('meditation')} | C")
        if self.ritual:
            parts.append(
                f"property_inline | {game_icon('pentacle')} | {self.ritual_text}"
            )
        return parts

    @property
    def paying_components_parts(self) -> list[str]:
        if not self.paying_components:
            return []
        return [
            f"section | {self.casting_components_text}",
            f"text | {self.paying_components}",
        ]

    @property
    def contents_text(self) -> str:
        subtitle_text = f"subtitle | {self.subtitle}"
        level_text = f"level | {self.level}"
        return (
            [subtitle_text, level_text]
            + self.spell_properties_parts
            + self.spell_parts
            + self.upcasting_parts
            + self.paying_components_parts
        )

    def to_card(self) -> dict:
        return {
            "count": 1,
            "color": self.color,
            "title": self.title,
            "icon": self.spell_damage_type_icon,
            "contents": self.contents_text,
            "background_image": f"data:image/png;base64,{self.background_image_base64}",
        }
