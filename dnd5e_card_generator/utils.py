import tempfile
from pathlib import Path

import requests


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


def damage_type_text(lang):
    if lang == "fr":
        return r"(de )?dégâts (de |d')?\w+"
    return r"\w+ damage"


def fetch_data(base_url, slug, lang):
    cached_file = Path(f"/{tempfile.gettempdir()}/{lang}:{slug}.html")
    if cached_file.exists():
        return cached_file.read_text()
    lang_param = "vf" if lang == "fr" else "vo"
    resp = requests.get(base_url, params={lang_param: slug})
    resp.raise_for_status()
    cached_file.write_text(resp.text)
    return resp.text
