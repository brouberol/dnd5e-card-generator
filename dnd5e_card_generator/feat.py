from dataclasses import dataclass

from .format import BaseCardTextFormatter
from .models import Card


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
        return [f"text | {text_part}" for text_part in text_parts]

    @property
    def contents_text(self) -> list[str]:
        return [
            f"title | {self.title}",
            "spell_school | illusion",
            "header_separator",
            f"text | {self._strong(self.prerequesite)}",
        ] + self.feat_parts

    def to_card(self) -> dict:
        card = Card(
            title=self.title,
            color="HotPink",
            icon="stars-stack",
            contents=self.contents_text,
        )
        return card.to_dict()
