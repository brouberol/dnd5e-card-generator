from dnd5e_card_generator.export.formatter import TitleDescriptionPrerequisiteFormatter
from dnd5e_card_generator.config import Config


class Feat(TitleDescriptionPrerequisiteFormatter):
    def format_title(self, *args, **kwargs) -> str:
        title = super().format_title(*args, **kwargs)
        title_tokens = title.split(" | ")
        title_color = Config.COLORS["feat_title"]
        stylized_tokens = [title_tokens[0]] + [
            f'<span style="color:{title_color}">{tok}</span>' for tok in title_tokens[1:]
        ]
        return " | ".join(stylized_tokens)
