import itertools
import re
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional

from dnd5e_card_generator.config import Config
from dnd5e_card_generator.const import SPELLS_BY_TYPE
from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import (
    Card,
    DamageDie,
    DamageType,
    MagicSchool,
    SpellShape,
    SpellType,
)
from dnd5e_card_generator.utils import game_icon, humanize_level, strip_accents


@dataclass
class Spell(BaseCardTextFormatter):
    title: str
    en_title: str
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
    reaction_condition: str

    @property
    def color(self) -> str:
        return Config.COLORS["spell"][self.level]

    @cached_property
    def spell_type(self) -> SpellType | None:
        if _spell_type := SPELLS_BY_TYPE.get(self.en_title):
            return getattr(SpellType, _spell_type)
        return None

    @property
    def spell_casting_components(self) -> str:
        components = []
        if self.verbal:
            components.append("V")
        if self.somatic:
            components.append("S")
        if self.material:
            components.append("M")
        return " ".join(components)

    @property
    def spell_type_icon(self) -> str:
        if spell_type := self.spell_type:
            if spell_type.icon:
                return spell_type.icon
        return Config.ICONS["spell_default"]

    @property
    def subtitle(self) -> str:
        if self.lang == "fr":
            if self.level == 0:
                return f"Tour de magie | {self.school_text}"
            else:
                return f"Niveau {self.level} | {self.school_text}"
        else:
            if self.level == 0:
                return f"Cantrip | {self.school_text}"
            else:
                return f"{humanize_level(self.level)} level | {self.school_text}"

    @property
    def school_text(self) -> str:
        return self.school.translate(self.lang).capitalize()

    @property
    def casting_components_text(self) -> str:
        return "Matériaux" if self.lang == "fr" else "Materials"

    @property
    def upcasting_section_title(self) -> str:
        return "Aux niveaux supérieurs" if self.lang == "fr" else "At higher levels"

    @property
    def reaction_section_title(self) -> str:
        return "Réaction" if self.lang == "fr" else "Reaction"

    @property
    def reaction_condition_text(self) -> str:
        if not self.reaction_condition:
            return ""
        if self.lang == "fr":
            prefix = "Vous lancez ce sort via votre réaction"
        else:
            prefix = "Vous cast this spell using your reaction"
        return "".join((prefix, self.reaction_condition))

    def fix_translation_mistakes(self, text: str) -> str:
        replacements = {"fr": {"de un dé": "d'un dé", " [E]": ""}}
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    def highlight_spell_text(self, text: str) -> str:
        text = self.highlight_damage_formula(text, self.lang)
        text = self.highlight_saving_throw(text, self.lang)
        return text

    def highlight_extra_targets(self, text: str) -> str:
        pattern_by_lang = {
            "fr": r"un(e)? \w+ supplémentaire",
            "en": r"one additional \w+ (?=for)",
        }
        return self._highlight(pattern_by_lang[self.lang], text)

    def shorten_upcasting_text(self) -> str:
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
                text = text.replace(upcasting_match.group(), "").strip()

        # We do this instead of .capitalize() because capitalize does not work
        # well on multi-sentence blocks.
        if text[0].islower():
            text = text[0].upper() + text[1:]
        return text

    def shorten_effect_duration_text(self, text: str) -> str:
        replacements = {"fr": {"Jusqu'à": "", "(voir ci-dessous)": ""}}
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return self.shorten_time_text(text).strip().capitalize()

    def shorten_distance_text(self, text: str) -> str:
        replacements = {
            "fr": {"mètres": "m", "mètre": "m", "Personnelle": "Perso.", "kilom": "km"}
        }
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    def shorten_casting_time_text(self, text: str) -> str:
        replacements = {"fr": {"1 action bonus": "a. bonus", "1 action": "action"}}
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text.capitalize()

    def shorten_time_text(self, text: str) -> str:
        replacements = {
            "fr": {
                "heures": "h",
                "heure": "h",
                "minutes": "min",
                "minute": "min",
                "jours": "j",
                "jour": "j",
                "Instantanée": "Instant.",
                "dissipation ou déclenchement": "Illimitée",
            },
            "en": {
                "hours": "h",
                "hour": "h",
                "minutes": "min",
                "minute": "min",
                "days": "d",
                "day": "d",
                "Instantaneous": "Instant.",
            },
        }
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    def radius_specified_for_circle_or_sphere_shape(self) -> bool:
        return (
            self.shape in (SpellShape.circle, SpellShape.sphere)
            and SpellShape.radius.translate(self.lang) in self.casting_range
        )

    @property
    def casting_range_text(self) -> str:
        if not self.shape:
            return self.casting_range
        shape_name = self.shape.translate(self.lang)
        if (
            shape_name in self.casting_range
            or self.radius_specified_for_circle_or_sphere_shape()
        ):
            return re.sub(r"\([^\)]+\)", "", self.casting_range).strip()
        else:
            return self.casting_range

    def render_spell_parts_text(self, text: list[str]) -> list[str]:
        text_parts = self.fix_text_with_subparts(text)
        text_parts = self.fix_text_with_bullet_points(text_parts)
        # text_parts = [self.highlight_spell_text(part) for part in text_parts]
        text_parts = [self.fix_translation_mistakes(part) for part in text_parts]
        text_parts = [self.highlight_italic_words(part) for part in text_parts]
        return text_parts

    @property
    def spell_parts(self) -> list[str]:
        text_parts = self.render_spell_parts_text(self.text)
        return [self.format_text(text_part) for text_part in text_parts]

    @property
    def casting_shape_text(self) -> str:
        if not self.shape:
            return ""
        shape_name = self.shape.translate(self.lang)
        casting_shape_dimension_pattern = r"(?P<dim>\d+([,\.]\d+)? m\w+)"

        # Sometimes, when a spell shape is a circle or a sphere, the radius is specified
        # but not the shape
        if self.radius_specified_for_circle_or_sphere_shape():
            if casting_shape_dimension_match := re.search(
                casting_shape_dimension_pattern, self.casting_range
            ):
                return casting_shape_dimension_match.group("dim").strip().capitalize()

        for text in [self.casting_range] + self.spell_parts:
            if shape_name not in text:
                continue
            if casting_shape_dimension_match := re.search(
                casting_shape_dimension_pattern, text
            ):
                return casting_shape_dimension_match.group("dim").strip().capitalize()
        return ""

    @property
    def upcasting_parts(self) -> list[str]:
        if not self.upcasting_text:
            return []
        upcasting_text = self.shorten_upcasting_text()
        upcasting_text = self.fix_translation_mistakes(upcasting_text)
        # upcasting_text = self.highlight_spell_text(upcasting_text)
        # upcasting_text = self.highlight_extra_targets(upcasting_text)

        return [
            self.format_section(self.upcasting_section_title),
            self.format_text(upcasting_text),
        ]

    def format_casting_time_property(self) -> str:
        return self.format_property_inline(
            game_icon(Config.ICONS["spell_properties"]["casting_time"]),
            self.shorten_time_text(self.shorten_casting_time_text(self.casting_time)),
        )

    def format_casting_range_property(self) -> str:
        return self.format_property_inline(
            game_icon(Config.ICONS["spell_properties"]["casting_range"]),
            self.shorten_distance_text(self.casting_range_text),
        )

    def format_casting_shape_property(self) -> str:
        return self.format_property_inline(
            game_icon(self.shape.icon),
            self.shorten_distance_text(self.casting_shape_text),
        )

    def format_effect_duration_property(self) -> str:
        return self.format_property_inline(
            game_icon(Config.ICONS["spell_properties"]["effect_duration"]),
            self.shorten_effect_duration_text(self.effect_duration),
        )

    def format_casting_components_property(self) -> str:
        return self.format_property_inline(
            game_icon(Config.ICONS["spell_properties"]["casting_components"]),
            self.spell_casting_components,
        )

    def format_concentration_property(self) -> str:
        return self.format_property_inline(
            game_icon(Config.ICONS["spell_properties"]["concentration"]), "C"
        )

    def format_ritual_property(self) -> str:
        return self.format_property_inline(
            game_icon(Config.ICONS["spell_properties"]["ritual"]), "R"
        )

    @property
    def spell_properties_parts(self) -> list[str]:
        parts = [
            self.format_casting_time_property(),
            self.format_casting_range_property(),
        ]
        if self.shape and self.shape.icon:
            parts.append(self.format_casting_shape_property())
        parts += [
            self.format_effect_duration_property(),
            self.format_casting_components_property(),
        ]
        if self.concentration:
            parts.append(self.format_concentration_property())
        if self.ritual:
            parts.append(self.format_ritual_property())
        return parts

    @property
    def paying_components_parts(self) -> list[str]:
        if not self.paying_components:
            return []
        return [
            self.format_section(self.casting_components_text),
            self.format_text(self.paying_components),
        ]

    @property
    def reaction_condition_parts(self) -> list[str]:
        if not self.reaction_condition:
            return []
        return [
            self.format_section(self.reaction_section_title),
            self.format_text(self.reaction_condition_text),
        ]

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.format_title(title=self.title),
            self.format_subtitle(self.subtitle),
            self.format_level(self.level),
            self.format_spell_school(self.school),
            self.format_header_separator(),
            self.spell_properties_parts,
            self.spell_parts,
            self.upcasting_parts,
            self.paying_components_parts,
            self.reaction_condition_parts,
            self.format_fill(),
            'text | Clerc'
        )


class SpellLegend(BaseCardTextFormatter):
    def __init__(self, lang: str):
        self.lang = lang

    @property
    def title_text(self):
        return "Légende" if self.lang == "fr" else "Legend"

    @property
    def die_section_text(self) -> str:
        return "Dés" if self.lang == "fr" else "Dice"

    @property
    def damage_type_section_text(self) -> str:
        return "Dégâts" if self.lang == "fr" else "Damages"

    @property
    def spell_types_section_text(self) -> str:
        return "Types de sort" if self.lang == "fr" else "Spell types"

    @property
    def spell_shapes_section_text(self) -> str:
        return "Formes de sort" if self.lang == "fr" else "Spell shapes"

    def to_table(self, elements: Any, columns: int) -> list[str]:
        out, properties = [self.format_text("")], []
        for element in elements:
            if not element.icon:
                continue
            properties.append(
                self.format_property_inline(
                    text=element.translate(self.lang).capitalize(),
                    icon=game_icon(element.icon),
                )
            )
        properties = sorted(
            properties, key=lambda line: strip_accents(line.split("|")[1])
        )
        properties += [self.format_property_inline(text="", icon="")] * (
            columns - (len(elements) % (columns))
        )
        for batch in itertools.batched(properties, columns):
            for _property in batch:
                out.append(_property)
            out.append(self.format_fill())
        return out

    @property
    def damage_die_legend(self) -> list[str]:
        out = [self.format_section(self.die_section_text), self.format_text("")]
        for damage_die_batch in itertools.batched(DamageDie.values_with_icons(), 6):
            batch = []
            for damage_die_name, damage_die in damage_die_batch:
                batch.append(
                    self.format_property_inline(
                        text=damage_die_name, icon=damage_die.render()
                    )
                )
            batch.append(self.format_fill())
            out.extend(batch)
        return out

    @property
    def damage_type_legend(self) -> list[str]:
        return [self.format_section(self.damage_type_section_text)] + self.to_table(
            DamageType, columns=4
        )

    @property
    def spell_type_legend(self) -> list[str]:
        return [self.format_section(self.spell_types_section_text)] + self.to_table(
            SpellType, columns=3
        )

    @property
    def spell_shape_legend(self) -> list[str]:
        out = [self.format_section(self.spell_shapes_section_text)]
        shapes = [
            shape
            for shape in SpellShape
            if shape not in (SpellShape.radius, SpellShape.hemisphere)
        ]
        return out + self.to_table(shapes, columns=4)

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.format_title(self.title_text),
            self.format_spell_school("illusion"),
            self.format_header_separator(),
            self.damage_die_legend,
            self.damage_type_legend,
            self.spell_type_legend,
            self.spell_shape_legend,
            self.format_fill(),
        )

    def to_card(self) -> dict:
        card = Card(
            color="LightCoral",
            title=self.title_text,
            icon=None,
            contents=self.contents_text,
        )

        return card.to_dict()
