from dataclasses import dataclass
import re
from .models import ItemType, Rarity
from .utils import game_icon, damage_type_text


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
        translations = {
            "fr": {
                ItemType.armor: "Armure",
                ItemType.potion: "Potion",
                ItemType.ring: "Anneau",
                ItemType.rod: "Sceptre",
                ItemType.staff: "Bâton",
                ItemType.wand: "Baguette",
                ItemType.weapon: "Arme",
                ItemType.wondrous_item: "Objet merveilleux",
            },
            "en": {
                ItemType.armor: "Armor",
                ItemType.potion: "Potion",
                ItemType.ring: "Ring",
                ItemType.rod: "Rod",
                ItemType.staff: "Staff",
                ItemType.wand: "Wand",
                ItemType.weapon: "Weapon",
                ItemType.wondrous_item: "Wondrous item",
            },
        }
        return translations[self.lang][self.type]

    @property
    def rarity_text(self) -> str:
        translations = {
            "fr": {
                Rarity.common: "commun",
                Rarity.uncommon: "peu commun",
                Rarity.rare: "rare",
                Rarity.very_rare: "très rare",
                Rarity.legendary: "légendaire",
                Rarity.artifact: "artéfact",
            },
            "en": {
                Rarity.common: "common",
                Rarity.uncommon: "uncommun",
                Rarity.rare: "rare",
                Rarity.very_rare: "very rare",
                Rarity.legendary: "legendary",
                Rarity.artifact: "artifact",
            },
        }
        return translations[self.lang][self.rarity]

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
