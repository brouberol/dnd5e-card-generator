import unicodedata


def humanize_level(level: int) -> str:
    if level == 1:
        return "1st"
    elif level == 2:
        return "2nd"
    elif level == 3:
        return "3rd"
    return f"{level}th"


def game_icon(icon_name: str) -> str:
    return f'<icon name="{icon_name}">'


def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def damage_type_text(lang):
    if lang == "fr":
        return r"(de )?dégâts (de |d')?\w+"
    return r"\w+ damage"
