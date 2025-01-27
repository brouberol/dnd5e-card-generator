from dataclasses import dataclass

from dnd5e_card_generator.export.formatter import BaseCardTextFormatter
from dnd5e_card_generator.utils import human_readable_class_name


@dataclass
class AncestryFeature(BaseCardTextFormatter):
    title: str
    lang: str
    sub_ancestry: str
    text: list[str]

    def format_title_for_card_list(self):
        return (
            f"{human_readable_class_name(self.__class__.__name__).capitalize()} - {self.title_text}"
        )

    @property
    def title_text(self) -> str:
        if self.sub_ancestry:
            return self.sub_ancestry
        return self.title

    @property
    def text_parts(self) -> list[str]:
        text = self.fix_text_with_bold(self.text)
        return [self.format_text(part) for part in text]

    @property
    def contents_text(self) -> list[str]:
        return self.assemble_text_contents(
            self.format_title(self.title_text),
            self.format_card_type("ancestry"),
            self.format_header_separator(),
            self.text_parts,
        )
