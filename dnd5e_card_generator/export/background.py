from dataclasses import dataclass

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import Language


@dataclass
class Background(BaseCardTextFormatter):
    title: str
    subtitle: str
    text: list[str]
    lang: Language

    @property
    def text_parts(self) -> list[str]:
        return [self.format_text(text) for text in self.text]

    @property
    def contents_text(self) -> list[str | list[str]]:
        return [
            self.title_text,
            self.format_subtitle(self.subtitle),
            self.format_header_separator(),
            self.format_card_type("background"),
            self.text_parts,
        ]
