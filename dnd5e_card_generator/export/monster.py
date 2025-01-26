from dataclasses import dataclass

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import (
    CreatureAttributes,
    CreatureSize,
    CreatureSpeed,
    CreatureType,
    HitPointsFormula,
)


@dataclass
class Monster(BaseCardTextFormatter):
    title: str
    lang: str
    type: CreatureType
    size: CreatureSize
    armor_class: str
    hit_points: int
    hit_points_formula: HitPointsFormula
    speeds: list[CreatureSpeed]
    attributes: CreatureAttributes
    saving_throws: list[str]
    skills: list[str]
    damage_resistances: list[str]
    senses: list[str]
    languages: str  # not an int due to 1/8, 1/4, etc
    challenge_rating: str
    features: list[str]
    actions: list[str]
    description: list[str]
    image_url: str

    def to_card(self) -> dict:
        return super().to_card()
