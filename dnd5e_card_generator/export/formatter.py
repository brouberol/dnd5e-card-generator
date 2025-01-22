import re
from dataclasses import dataclass

from dnd5e_card_generator.config import Config
from dnd5e_card_generator.models import Card, DamageDie, DamageFormula, DamageType
from dnd5e_card_generator.utils import (
    damage_type_text,
    game_icon,
    human_readable_class_name,
    pascal_case_to_snake_case,
)


class BaseCardTextFormatter:
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
            return r"(de )?dégâts (de |d')?(?P<damage_type_1>\w+)( ou (de |d')(?P<damage_type_2>\w+))?"
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
        return f"boxes | {recharges} | 1.5"  # 1.5 is in em

    def format_text(self, text: str) -> str:
        return f"text | {text}"

    def format_section(self, section: str) -> str:
        return f"section | {section}"

    def format_property_inline(self, icon: str, text: str) -> str:
        return f"property_inline | {icon} | {text}"

    def format_level(self, level: int) -> str:
        return f"level | {level}"

    def format_spell_school(self, school: str) -> str:
        return f"spell_school | {school}"

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

    def highlight_die_value(self, text) -> str:
        die_value_pattern = r"\dd\d+ " + damage_type_text(self.lang)
        return re.sub(
            die_value_pattern, lambda match: self._strong(match.group(0)), text
        )

    def highlight_damage_formula(self, text: str, lang: str) -> str:
        die_value_pattern = (
            r"(?P<prefix>(one |un )?)(?P<num_die>\d+)?(?P<die_type>d\d+)( (?P<dmg_extra>\+ "
            + self.spell_carac_text(lang)
            + r")| "
            + self.damage_type_text(lang)
            + r")?"
        )
        matches = list(re.finditer(die_value_pattern, text))
        if not matches:
            return text

        for match in matches:
            parts = match.groupdict()
            damage_type_1, damage_type_2 = None, None
            if parts.get("damage_type_1"):
                damage_type_1 = DamageType.from_str(
                    parts["damage_type_1"].rstrip("s"), lang
                )
            if parts.get("damage_type_2"):
                damage_type_2 = DamageType.from_str(
                    parts["damage_type_2"].rstrip("s"), lang
                )

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

    def highlight_saving_throw(self, text: str, lang: str) -> str:
        saving_throw_patterns_by_lang = {
            "fr": [
                r"jet(s)? de sauvegarde de [A-Z]\w+",
                "la moitié de ces dégâts en cas de réussite",
            ],
            "en": [r"\w+ saving throw", "half as much damage on a successful one"],
        }
        for pattern in saving_throw_patterns_by_lang[lang]:
            text = self._highlight(pattern, text)
        return text

    def highlight_italic_words(self, text: str) -> str:
        return re.sub(r"_([^_]+)_", lambda m: self._em(m.group(1)), text)

    def fix_text_with_subparts(self, text: list[str]) -> list[str]:
        text_copy = text.copy()
        for i, part in enumerate(text):
            if part.startswith(". "):
                text_copy[i - 1] = self._strong(text_copy[i - 1]) + part
                text_copy[i] = ""
        return [part for part in text_copy if part]

    def highlight_level(self, text: str) -> str:
        level_pattern_by_lang = {"fr": r"niveau \d+", "en": r"\d+(st|nd|rd|th) level"}
        return self._highlight(level_pattern_by_lang[self.lang], text)

    def format_bullet_point(self, text: str) -> str:
        text = text.replace("• ", "")
        if m := re.match(r"((\w+)\s)+(?=:)", text):
            text = text.replace(m.group(), self._strong(m.group()))
        return self._li(text)

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

    @property
    def color(self) -> str:
        return Config.COLORS[pascal_case_to_snake_case(self.__class__.__name__)]

    def to_card(self) -> dict:
        card = Card(
            color=self.color,
            title=self.format_title_for_card_list(),
            icon=None,
            contents=self.contents_text,
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
        text_parts = [self.highlight_saving_throw(part, self.lang) for part in text]
        text_parts = [self.highlight_italic_words(part) for part in text_parts]
        return text_parts

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
            self.format_title(
                title=self.title,
                icon=Config.ICONS[pascal_case_to_snake_case(self.__class__.__name__)],
            ),
            self.format_spell_school(self.__class__.__name__.lower()),
            self.format_header_separator(),
            self.prerequisite_text,
            self.text_parts,
        )
