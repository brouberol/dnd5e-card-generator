from dataclasses import dataclass

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.models import Card


@dataclass
class Feat(BaseCardTextFormatter):
    title: str
    prerequesite: str
    text: list[str]
    lang: str

    def render_feat_parts_text(self, text: list[str]) -> list[str]:
        text_parts = self.fix_text_with_subparts(text)
        text_parts = [self.highlight_saving_throw(part, self.lang) for part in text]
        text_parts = [self.highlight_italic_words(part) for part in text_parts]
        text_parts = self.fix_text_with_bullet_points(text_parts)
        return text_parts

    @property
    def feat_parts(self) -> list[str]:
        text_parts = self.render_feat_parts_text(self.text)
        return [self.format_text(text_part) for text_part in text_parts]

    @property
    def prerequisite_text(self) -> str:
        if not self.prerequesite:
            return ""
        return self.format_text(self._strong(self.prerequesite))

    @property
    def contents_text(self) -> list[str]:
        return [
            self.format_title(title=self.title, icon="stars-stack"),
            self.format_spell_school("illusion"),
            self.format_header_separator(),
            self.prerequisite_text,
        ] + self.feat_parts

    def to_card(self) -> dict:
        card = Card(
            title=self.title,
            color="#994094",
            icon=None,
            contents=self.contents_text,
        )
        return card.to_dict()
