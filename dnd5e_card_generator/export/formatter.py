import re
from dataclasses import dataclass
from typing import Protocol, Callable

from dnd5e_card_generator.config import Config
from dnd5e_card_generator.models import Card, DamageDie, DamageFormula, DamageType, Action
from dnd5e_card_generator.utils import (
    damage_type_text,
    game_icon,
    human_readable_class_name,
    pascal_case_to_snake_case,
)


class FormatterProtocol(Protocol):
    title: str
    lang: str


class BaseCardTextFormatter(FormatterProtocol):

    @staticmethod
    def map_string_transformations(s: str, functions: list[Callable[[str], str]]) -> str:
        for func in functions:
            s = func(s)
        return s

    def _li(self, text: str) -> str:
        return f"<li>{text}</li>"

    def _em(self, text: str) -> str:
        return f"<em>{text}</em>"

    def _strong(self, text: str) -> str:
        return f"<b>{text}</b>"

    def _highlight(self, pattern: str, text: str) -> str:
        return re.sub(pattern, lambda match: self._strong(match.group(0)), text)

    def format_title_for_card_list(self):
        return f"{human_readable_class_name(self.__class__.__name__).capitalize()} - {self.title}"

    def damage_type_text(self, lang) -> str:
        # 2d8 dégâts de foudre ou de tonnerre
        if lang == "fr":
            return (
                r"(de )?dégâts (de |d')?(?P<damage_type_1>\w+)( ou (de |d')(?P<damage_type_2>\w+))?"
            )
        return r"(?P<damage_type_1>\w+) (or (?P<damage_type_2>\w+) )?damage"

    def spell_carac_text(self, lang: str) -> str:
        if lang == "fr":
            return "le modificateur de votre caractéristique d'incantation"
        return "your spellcasting ability modifier"

    def format_header_separator(self) -> str:
        return "header_separator |"

    def format_fill(self) -> str:
        return "fill |"

    def format_title(self, title: str, icon: str | None = None) -> str:
        parts = ["title", title]
        if icon:
            parts.append(game_icon(icon))
        return " | ".join(parts)

    def format_subtitle(self, subtitle: str) -> str:
        return f"subtitle | {subtitle}"

    def format_boxes(self, recharges: int) -> str:
        return "\n".join(
            [
                f"boxes | {recharges} | 1.5",  # 1.5 is in em
                "text |",  # only here for vertical margin
            ]
        )

    def format_text(self, text: str) -> str:
        return f"text | {text.rstrip()}"

    def format_section(self, section: str) -> str:
        return f"section | {section}"

    def format_property_inline(self, icon: str, text: str) -> str:
        return f"property_inline | {icon} | {text}"

    def format_level(self, level: int) -> str:
        return f"level | {level}"

    def format_spell_school(self, school: str) -> str:
        return f"spell_school | {school}"

    def format_card_type(self, card_type: str) -> str:
        return self.format_spell_school(card_type)

    def assemble_text_contents(self, *parts: list | str) -> list[str]:
        contents = []
        for part in parts:
            if not part:
                continue
            if isinstance(part, list):
                contents.extend(part)
            else:
                contents.append(part)
        return contents

    def fix_text_with_subparts(self, text: list[str]) -> list[str]:
        text_copy = text.copy()
        for i, part in enumerate(text):
            if part.startswith(". "):
                text_copy[i - 1] = self._strong(text_copy[i - 1]) + part
                text_copy[i] = ""
        return [part for part in text_copy if part]

    def fix_text_with_bold(self, text: list[str]) -> list[str]:
        text_copy = text.copy()
        for i, part in enumerate(text):
            if match := re.match(r"\*([\w. ]+)\*", part):
                text_copy[i] = part.replace(
                    match.group(), f"<b>{match.group(1).strip().rstrip('.').strip()}</b>: "
                )
        return text_copy

    def fix_text_with_bullet_points(self, text: list[str]) -> list[str]:
        out = []
        in_ul = False
        for part in text:
            if not part.startswith("• "):
                if in_ul:
                    out[-1] += "</ul>"
                out.append(part)
            elif not out:
                out.append("<ul>" + self.format_bullet_point(part))
            else:
                if not in_ul:
                    in_ul = True
                    out[-1] += "<ul>"
                out[-1] += self.format_bullet_point(part)
        return out

    def highlight_die_value(self, text) -> str:
        die_value_pattern = r"\dd\d+ " + damage_type_text(self.lang)
        return re.sub(die_value_pattern, lambda match: self._strong(match.group(0)), text)

    def highlight_damage_formula(self, text: str) -> str:
        die_value_pattern = (
            r"(?P<prefix>(one |un )?)(?P<num_die>\d+)?(?P<die_type>d\d+)( (?P<dmg_extra>\+ "
            + self.spell_carac_text(self.lang)
            + r")| "
            + self.damage_type_text(self.lang)
            + r")?"
        )
        matches = list(re.finditer(die_value_pattern, text))
        if not matches:
            return text

        for match in matches:
            parts = match.groupdict()
            damage_type_1, damage_type_2 = None, None
            if parts.get("damage_type_1"):
                damage_type_1 = DamageType.from_str(parts["damage_type_1"].rstrip("s"), self.lang)
            if parts.get("damage_type_2"):
                damage_type_2 = DamageType.from_str(parts["damage_type_2"].rstrip("s"), self.lang)

            damage_formula = DamageFormula(
                num_die=int(parts.get("num_die") or 1),
                damage_die=DamageDie.from_str(parts["die_type"]),
                damage_type_1=damage_type_1,
                damage_type_2=damage_type_2,
            )
            text = text.replace(
                match.group(),
                self._strong(damage_formula.render() + (parts.get("dmg_extra") or "")),
            )
        return text

    def highlight_saving_throw(self, text: str) -> str:
        saving_throw_patterns_by_lang = {
            "fr": [
                r"jet(s)? de sauvegarde de [A-Z]\w+",
                "la moitié de ces dégâts en cas de réussite",
            ],
            "en": [r"\w+ saving throw", "half as much damage on a successful one"],
        }
        for pattern in saving_throw_patterns_by_lang[self.lang]:
            text = self._highlight(pattern, text)
        return text

    def highlight_italic_words(self, text: str) -> str:
        return re.sub(r"_([^_]+)_", lambda m: self._em(m.group(1)), text)

    def highlight_action_name(self, text: str) -> str:
        return re.sub(Action.as_pattern(self.lang), lambda m: self._em(m.group(1)), text)

    def highlight_level(self, text: str) -> str:
        level_pattern_by_lang = {"fr": r"niveau \d+", "en": r"\d+(st|nd|rd|th) level"}
        return self._highlight(level_pattern_by_lang[self.lang], text)

    def format_bullet_point(self, text: str) -> str:
        text = text.replace("• ", "")
        if m := re.match(r"((\w+)\s)+(?=:)", text):
            text = text.replace(m.group(), self._strong(m.group()))
        return self._li(text)

    @property
    def color(self) -> str:
        return Config.COLORS[pascal_case_to_snake_case(self.__class__.__name__)]

    @property
    def contents_text(self) -> list[str]:
        return [""]

    @property
    def icon(self) -> str | None:
        return Config.ICONS.get(pascal_case_to_snake_case(self.__class__.__name__))

    @property
    def title_text(self) -> str:
        return self.format_title(
            title=self.title,
            icon=self.icon,
        )

    @property
    def image(self) -> str | None:
        return getattr(self, "image_url", None)

    def to_card(self) -> dict:
        card = Card(
            color=self.color,
            title=self.format_title_for_card_list(),
            icon=self.icon,
            contents=self.contents_text,
            background_image=self.image,
        )
        return card.to_dict()


@dataclass
class TitleDescriptionPrerequisiteFormatter(BaseCardTextFormatter):
    title: str
    prerequesite: str
    text: list[str]
    lang: str

    def render_parts_text(self, text: list[str]) -> list[str]:
        text_parts = self.fix_text_with_subparts(text)
        text_parts = self.fix_text_with_bullet_points(text_parts)
        return [
            self.map_string_transformations(
                part, [self.highlight_saving_throw, self.highlight_italic_words]
            )
            for part in text_parts
        ]

    @property
    def text_parts(self) -> list[str]:
        text_parts = self.render_parts_text(self.text)
        return [self.format_text(text_part) for text_part in text_parts]

    @property
    def prerequisite_text(self) -> str:
        if not self.prerequesite:
            return ""
        return self.format_text(self._strong(self.prerequesite))

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.title_text,
            self.format_card_type(self.__class__.__name__.lower()),
            self.format_header_separator(),
            self.prerequisite_text,
            self.text_parts,
        )
