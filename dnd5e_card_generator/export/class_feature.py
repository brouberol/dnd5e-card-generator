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
    def text_parts(self) -> str:
        text = self.fix_text_with_subparts(self.text)
        text = self.fix_text_with_bullet_points(text)
        text = [
            self.format_text(self.highlight_italic_words(self.highlight_level(part)))
            for part in text
        ]
        return text

    @property
    def subtitle_text(self) -> str:
        parts = [self.class_name.capitalize()]
        if self.class_variant:
            parts.extend(["-", self.class_variant])
        return " ".join(parts)

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.format_title(title=self.title, icon=self.class_name.icon),
            self.format_subtitle(self.subtitle_text),
            self.format_header_separator(),
            self.format_spell_school("illusion"),
            self.format_header_separator(),
            self.text_parts,
        )
