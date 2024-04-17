import base64
import itertools
import json
import re
from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from .const import DATA_DIR
from .models import (
    Card,
    DamageDie,
    DamageFormula,
    DamageType,
    MagicSchool,
    SpellShape,
    SpellType,
)
from .translator import TranslatedStrEnum
from .utils import game_icon, humanize_level, strip_accents


@dataclass
class Spell:
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
    def spell_types(self):
        return json.load(open(DATA_DIR / "spell_by_types.json", "r"))

    @cached_property
    def spell_type(self):
        if spell_type := self.spell_types.get(self.en_title):
            return getattr(SpellType, spell_type)

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
    def spell_type_icon(self):
        if self.spell_type:
            return self.spell_type.icon
        return "scroll-unfurled"

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

    @property
    def spell_carac_text(self) -> str:
        if self.lang == "fr":
            return "le modificateur de votre caractéristique d'incantation"
        return "your spellcasting ability modifier"

    def damage_type_text(self, lang):
        if lang == "fr":
            return r"(de )?dégâts (de |d')?(?P<damage_type>\w+)"
        return r"\w+ damage"

    def _li(self, text: str) -> str:
        return f"<li>{text}</li>"

    def _strong(self, text: str) -> str:
        return f"<b>{text}</b>"

    def _highlight(self, pattern: str, text: str) -> str:
        return re.sub(pattern, lambda match: self._strong(match.group(0)), text)

    def fix_translation_mistakes(self, text: str) -> str:
        replacements = {"fr": {"de un dé": "d'un dé"}}
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    def highlight_saving_throw(self, text: str) -> str:
        saving_throw_patterns_by_lang = {
            "fr": [
                r"jet de sauvegarde de [A-Z]\w+",
                "la moitié de ces dégâts en cas de réussite",
            ],
            "en": [r"\w+ saving throw", "half as much damage on a successful one"],
        }
        for pattern in saving_throw_patterns_by_lang[self.lang]:
            text = self._highlight(pattern, text)
        return text

    def highlight_damage_formula(self, text: str) -> str:
        die_value_pattern = (
            r"(?P<prefix>(one |un )?)(?P<num_die>\d+)?(?P<die_type>d\d+)( (?P<dmg_extra>\+ "
            + self.spell_carac_text
            + r")| "
            + self.damage_type_text(self.lang)
            + r")?"
        )
        matches = list(re.finditer(die_value_pattern, text))
        if not matches:
            return text

        for match in matches:
            parts = match.groupdict()
            damage_formula = DamageFormula(
                num_die=int(parts.get("num_die") or 1),
                damage_die=DamageDie.from_str(parts["die_type"]),
                damage_type=DamageType.from_str(
                    parts["damage_type"].rstrip("s"), self.lang
                )
                if parts.get("damage_type")
                else None,
            )
            text = text.replace(
                match.group(),
                self._strong(damage_formula.render() + (parts.get("dmg_extra") or "")),
            )
        return text

    def highlight_spell_text(self, text: str) -> str:
        text = self.highlight_damage_formula(text)
        text = self.highlight_saving_throw(text)
        return text

    def highlight_extra_targets(self, text: str) -> str:
        pattern_by_lang = {
            "fr": r"un(e)? \w+ supplémentaire",
            "en": r"one additional \w+ (?=for)",
        }
        return self._highlight(pattern_by_lang[self.lang], text)

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
        return self.shorten_time_text(text).capitalize()

    def shorten_distance_text(self, text: str) -> str:
        replacements = {"fr": {"mètres": "m", "mètre": "m", "Personnelle": "Perso."}}
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
                "Instantanée": "Instant.",
            },
            "en": {
                "hours": "h",
                "hour": "h",
                "minutes": "min",
                "minute": "min",
                "Instantaneous": "Instant.",
            },
        }
        for term, replacement in replacements.get(self.lang, {}).items():
            text = text.replace(term, replacement)
        return text

    @property
    def casting_range_text(self) -> str:
        if not self.shape:
            return self.casting_range
        shape_name = self.shape.translate(self.lang)
        if shape_name in self.casting_range:
            return re.sub(r"\([^\)]+\)", "", self.casting_range).strip()
        else:
            return self.casting_range

    def fix_text_with_subparts(self, text: list[str]) -> str:
        text_copy = text.copy()
        for i, part in enumerate(text):
            if part.startswith(". "):
                text_copy[i - 1] = self._strong(text_copy[i - 1]) + part
                text_copy[i] = ""
        return [part for part in text_copy if part]

    def format_bullet_point(self, text: str) -> str:
        text = text.replace("• ", "")
        if m := re.match(r"((\w+)\s)+(?=:)", text):
            text = text.replace(m.group(), self._strong(m.group()))
        return self._li(text)

    def fix_text_with_bullet_points(self, text: list[str]) -> str:
        out = []
        for part in text:
            if not part.startswith("• "):
                out.append(part)
            elif not out:
                out.append(self.format_bullet_point(part))
            else:
                out[-1] += self.format_bullet_point(part)
        return out

    def render_spell_parts_text(self, text: list[str]) -> list[str]:
        text_parts = self.fix_text_with_subparts(text)
        text_parts = self.fix_text_with_bullet_points(text_parts)
        text_parts = [self.highlight_spell_text(part) for part in text_parts]
        text_parts = [self.fix_translation_mistakes(part) for part in text_parts]
        return text_parts

    @property
    def spell_parts(self) -> list[str]:
        text_parts = self.render_spell_parts_text(self.text)
        return [f"text | {text_part}" for text_part in text_parts]

    @property
    def casting_shape_text(self):
        if not self.shape:
            return ""
        shape_name = self.shape.translate(self.lang)
        casting_shape_dimension_pattern = r"(?P<dim>\d+([,\.]\d+)? m\w+)"
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
        upcasting_text = self.highlight_spell_text(upcasting_text)
        upcasting_text = self.highlight_extra_targets(upcasting_text)

        return [
            f"section | {self.upcasting_section_title}",
            f"text | {upcasting_text}",
        ]

    @property
    def spell_properties_parts(self) -> list[str]:
        def property_inline(icon: str, text: str) -> str:
            return f"property_inline | {game_icon(icon)} | {text}"

        parts = [
            property_inline(
                "player-time", self.shorten_casting_time_text(self.casting_time)
            ),
            property_inline(
                "measure-tape", self.shorten_distance_text(self.casting_range_text)
            ),
        ]
        if self.shape:
            parts.append(
                property_inline(
                    self.shape.icon, self.shorten_distance_text(self.casting_shape_text)
                )
            )
        parts += [
            property_inline(
                "sands-of-time", self.shorten_effect_duration_text(self.effect_duration)
            ),
            property_inline("drink-me", self.spell_casting_components),
        ]
        if self.concentration:
            parts.append(f"property_inline | {game_icon('meditation')} | C")
        if self.ritual:
            parts.append(f"property_inline | {game_icon('pentacle')} | R")
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
    def reaction_condition_parts(self) -> list[str]:
        if not self.reaction_condition:
            return []
        return [
            f"section | {self.reaction_section_title}",
            f"text | {self.reaction_condition_text}",
        ]

    @property
    def contents_text(self) -> list[str]:
        subtitle_text = f"subtitle | {self.subtitle}"
        level_text = f"level | {self.level}"
        spell_school_text = f"spell_school | {self.school}"
        title_text = f"title | {self.title}"
        return (
            [title_text, subtitle_text, level_text, spell_school_text]
            + self.spell_properties_parts
            + self.spell_parts
            + self.upcasting_parts
            + self.paying_components_parts
            + self.reaction_condition_parts
        )

    def to_card(self) -> dict:
        card = Card(
            color=self.color,
            title=self.title,
            icon=self.spell_type_icon,
            contents=self.contents_text,
        )
        return card.to_dict()


class SpellLegend:
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

    def to_table(self, elements: list[TranslatedStrEnum], columns: int) -> list[str]:
        out, properties = ["text|"], []
        for element in elements:
            properties.append(
                f"property_inline | {element.translate(self.lang).capitalize()} | {game_icon(element.icon)}"
            )
        properties = sorted(
            properties, key=lambda line: strip_accents(line.split("|")[1])
        )
        properties += ["property_inline | |"] * (columns - (len(elements) % (columns)))
        for batch in itertools.batched(properties, columns):
            for _property in batch:
                out.append(_property)
            out.append("")
        return out

    @property
    def damage_die_legend(self) -> list[str]:
        out = [f"section | {self.die_section_text}", "text|"]
        for damage_die_batch in itertools.batched(DamageDie._member_map_.items(), 6):
            batch = []
            for damage_die_name, damage_die in damage_die_batch:
                batch.append(f"property_inline | {damage_die_name} | {str(damage_die)}")
            batch.append("")
            out.extend(batch)
        return out

    @property
    def damage_type_legend(self) -> list[str]:
        return [f"section | {self.damage_type_section_text}"] + self.to_table(
            DamageType, columns=4
        )

    @property
    def spell_type_legend(self) -> list[str]:
        return [f"section | {self.spell_types_section_text}"] + self.to_table(
            SpellType, columns=3
        )

    @property
    def spell_shape_legend(self) -> list[str]:
        out = [f"section | {self.spell_shapes_section_text}"]
        shapes = [
            shape
            for shape in SpellShape
            if shape not in (SpellShape.radius, SpellShape.hemisphere)
        ]
        return out + self.to_table(shapes, columns=4)

    @property
    def contents_text(self) -> list[str]:
        out = (
            [f"title | {self.title_text}"]
            + ["spell_school | illusion", "text|"]
            + self.damage_die_legend
            + self.damage_type_legend
            + self.spell_type_legend
            + self.spell_shape_legend
            + ["text|"]
        )
        return out

    def to_card(self) -> dict:
        card = Card(
            color="LightCoral",
            title=self.title_text,
            icon=None,
            contents=self.contents_text,
        )

        return card.to_dict()
