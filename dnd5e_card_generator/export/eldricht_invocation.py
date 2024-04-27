from dnd5e_card_generator.config import COLORS
from dnd5e_card_generator.export.formatter import TitleDescriptionPrerequisiteFormatter
from dnd5e_card_generator.models import Card


class EldrichtInvocation(TitleDescriptionPrerequisiteFormatter):
    def to_card(self) -> dict:
        card = Card(
            title=self.title,
            color=COLORS["eldricht_invocation"],
            icon=None,
            contents=self.contents_text,
        )
        return card.to_dict()
