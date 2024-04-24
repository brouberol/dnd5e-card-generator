import re
from dataclasses import dataclass

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import Card, MagicItemKind, MagicItemRarity
from dnd5e_card_generator.utils import damage_type_text, game_icon


@dataclass
class MagicItem(BaseCardTextFormatter):
    """This class implements the logic of exporting a magic item data as a card"""

    title: str
    type: MagicItemKind
    color: str
    rarity: MagicItemRarity
    attunement: bool
    text: list[str]
    lang: str
    image_url: str
    recharges: int

    def highlight_die_value(self, text) -> str:
        die_value_pattern = r"\dd\d+ " + damage_type_text(self.lang)
        return re.sub(die_value_pattern, lambda match: f"<b>{match.group(0)}</b>", text)

    @property
    def icon(self):
        return self.type.icon

    @property
    def attunement_text(self) -> str:
        return game_icon("empty-hourglass")

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
        return [self.format_fill(), self.format_boxes(self.recharges)]

    @property
    def title_text(self) -> str:
        return self.format_title(self.title, self.icon)

    @property
    def subtitle_text(self) -> str:
        return self.format_subtitle(self.subtitle)

    @property
    def item_text(self) -> list[str]:
        return [
            self.format_text(self.highlight_die_value(text_part))
            for text_part in self.text
        ]

    @property
    def contents_text(self) -> list[str]:
        return (
            [self.title_text, self.subtitle_text, self.format_header_separator()]
            + self.item_text
            + self.recharges_text
        )

    def to_card(self) -> dict:
        card = Card(
            color=self.color,
            title=self.title,
            icon=self.icon,
            contents=self.contents_text,
            background_image=self.image_url,
        )
        return card.to_dict()
