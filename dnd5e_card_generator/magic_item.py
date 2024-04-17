import re
from dataclasses import dataclass

from .models import MagicItemKind, MagicItemRarity
from .utils import damage_type_text, game_icon


@dataclass
class MagicItem:
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
        return ["fill | ", f"boxes | {self.recharges} | 1.5"]  # 1.5 is in em

    @property
    def subtitle_text(self) -> list[str]:
        return [
            f"subtitle | {self.subtitle}",
            "rule",
        ]

    @property
    def item_text(self) -> list[str]:
        return [
            f"text | {self.highlight_die_value(text_part)}" for text_part in self.text
        ]

    @property
    def contents_text(self) -> list[str]:
        return self.subtitle_text + self.text + self.recharges_text

    def to_card(self) -> dict:
        card = {
            "count": 1,
            "color": self.color,
            "title": self.title,
            "icon": self.icon,
            "icon_back": self.icon,
            "contents": self.contents_text,
        }
        if self.image_url:
            card["background_image"] = self.image_url
        return card
