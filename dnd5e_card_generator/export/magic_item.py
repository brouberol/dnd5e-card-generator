from dataclasses import dataclass

from dnd5e_card_generator.config import Config
from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import MagicItemKind, MagicItemRarity, Language
from dnd5e_card_generator.utils import game_icon


@dataclass
class MagicItem(BaseCardTextFormatter):
    """This class implements the logic of exporting a magic item data as a card"""

    title: str
    type: MagicItemKind
    rarity: MagicItemRarity
    attunement: bool
    text: list[str]
    lang: Language
    image_url: str
    recharges: int

    @property
    def icon(self):
        return self.type.icon

    @property
    def color(self):
        return self.rarity.color

    @property
    def attunement_text(self) -> str:
        return game_icon(Config.ICONS["magic_item"]["attunement"])

    @property
    def type_text(self) -> str:
        return MagicItemKind.translate(self.type, self.lang).capitalize()

    @property
    def rarity_text(self) -> str:
        return self.rarity.translate(self.lang)

    @property
    def subtitle(self) -> str:
        subtitle = f"{self.type_text}, {self.rarity_text}"
        if self.attunement:
            subtitle += f" {self.attunement_text}"
        return subtitle

    @property
    def recharges_text(self) -> list[str]:
        if not self.recharges:
            return []
        return [
            self.format_fill(),
            self.format_boxes(self.recharges),
            self.format_text(""),  # for a vertical margin
        ]

    @property
    def subtitle_text(self) -> str:
        return self.format_subtitle(self.subtitle)

    @property
    def item_text(self) -> list[str]:
        formatters = [
            self.highlight_die_value,
            self.highlight_saving_throw,
            self.highlight_damage_formula,
            self.format_text,
        ]
        return [self.map_string_transformations(part, formatters) for part in self.text]

    @property
    def contents_text(self) -> list[str | list[str]]:
        return [
            self.title_text,
            self.subtitle_text,
            self.format_header_separator(),
            self.item_text,
            self.recharges_text,
        ]
