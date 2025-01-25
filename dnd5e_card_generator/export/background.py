from dataclasses import dataclass

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.config import Config


@dataclass
class Background(BaseCardTextFormatter):
    title: str
    subtitle: str
    text: list[str]
    lang: str

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.format_title(title=self.title, icon=Config.ICONS["background"]),
            self.format_subtitle(self.subtitle),
            self.format_header_separator(),
            self.format_card_type("background"),
            *[self.format_text(text) for text in self.text],
        )
