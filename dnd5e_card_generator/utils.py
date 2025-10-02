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


def pascal_case_to_snake_case(pascal_string: str) -> str:
    snake_string = ""
    for i, char in enumerate(pascal_string):
        if char.isupper() and i != 0:
            snake_string += "_"
        snake_string += char.lower()
    return snake_string


def human_readable_class_name(cls_name: str) -> str:
    return pascal_case_to_snake_case(cls_name).replace("_", " ")


def slugify(s: str) -> str:
    return s.lower().replace(" ", "-").replace("/", "-").replace("'", "-")
