from dataclasses import dataclass, field

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import CharacterClass


@dataclass
class ClassFeature(BaseCardTextFormatter):
    class_name: CharacterClass
    title: str
    text: list[str]
    lang: str
    class_variant: str | None = field(default=None)

    @property
    def text_parts(self) -> list[str]:
        text = self.fix_text_with_subparts(self.text)
        text = self.fix_text_with_bullet_points(text)
        formatters = [
            self.highlight_damage_formula,
            self.highlight_saving_throw,
            self.highlight_italic_words,
            self.highlight_level,
            self.highlight_action_name,
        ]
        return [self.map_string_transformations(part, formatters) for part in text]

    @property
    def subtitle_text(self) -> str:
        parts = [self.class_name.translate(self.lang).capitalize()]
        if self.class_variant:
            parts.extend(["-", self.class_variant])
        return " ".join(parts)

    @property
    def icon(self) -> str:
        return self.class_name.icon

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.title_text,
            self.format_subtitle(self.subtitle_text),
            self.format_header_separator(),
            self.format_card_type(self.class_name.value),
            self.text_parts,
        )
