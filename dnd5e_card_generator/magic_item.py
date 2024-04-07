import re
from dataclasses import dataclass

from .models import ItemType, Rarity
from .utils import damage_type_text, game_icon


@dataclass
class MagicItem:
    title: str
    type: ItemType
    color: str
    rarity: Rarity
    attunement: bool
    text: list[str]
    lang: str
    image_url: str
    recharges: int

    @property
    def icon(self):
        return self.type.icon

    @property
    def attunement_text(self) -> str:
        return game_icon("empty-hourglass")

    @property
    def type_text(self) -> str:
        return ItemType.translate(self.type, self.lang).capitalize()

    @property
    def rarity_text(self) -> str:
        return self.rarity.translate(self.lang)

    def highlight_die_value(self, text) -> str:
        die_value_pattern = r"\dd\d+ " + damage_type_text(self.lang)
        return re.sub(die_value_pattern, lambda match: f"<b>{match.group(0)}</b>", text)

    @property
    def subtitle(self) -> SyntaxWarning:
        subtitle = f"{self.type_text}, {self.rarity_text}"
        if self.attunement:
            subtitle += f" {self.attunement_text}"
        return subtitle

    def to_card(self) -> dict:
        extra_content = []
        if self.recharges:
            extra_content.extend(
                ["fill | ", f"boxes | {self.recharges} | 1.5"]
            )  # 1.5 is in em
        card = {
            "count": 1,
            "color": self.color,
            "title": self.title,
            "icon": self.icon,
            "icon_back": self.icon,
            "contents": [
                f"subtitle | {self.subtitle}",
                "rule",
            ]
            + [
                f"text | {self.highlight_die_value(text_part)}"
                for text_part in self.text
            ]
            + extra_content,
        }
        if self.image_url:
            card["background_image"] = self.image_url
        return card
