#!/usr/bin/env python3

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup

AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"

# https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
SPELL_COLORS_BY_LEVEL = {
    0: "277DA1",
    1: "577590",
    2: "4D908E",
    3: "43AA8B",
    4: "90BE6D",
    5: "F9C74F",
    6: "F9844A",
    7: "F8961E",
    8: "F3722C",
    9: "F94144",
}


def humanize_level(level):
    if level == 1:
        return "1st"
    elif level == 2:
        return "2nd"
    elif level == 3:
        return "3rd"
    return f"{level}th"


@dataclass
class Spell:
    title: str
    lang: str
    level: int
    school: str
    casting_time: str
    casting_range: str
    casting_components: str
    effect_duration: str
    text: list[str]
    upcasting_text: str
    tags: list[str]
    color: str

    @property
    def subtitle(self):
        if self.lang == "fr":
            if self.level == 0:
                return f"Tour de magie - {self.school}"
            else:
                return f"Niveau {self.level} - {self.school}"
        else:
            if self.level == 0:
                return f"{self.school} cantrip"
            else:
                return f"{humanize_level(self.level)}-level - {self.school}"

    @property
    def casting_time_text(self):
        return "Temps d'invocation" if self.lang == "fr" else "Casting time"

    @property
    def casting_range_text(self):
        return "Portée" if self.lang == "fr" else "Range"

    @property
    def casting_components_text(self):
        return "Composants" if self.lang == "fr" else "Compoments"

    @property
    def effect_duration_text(self):
        return "Durée" if self.lang == "fr" else "Duration"

    @property
    def upcasting_section_title(self):
        return "Aux niveaux supérieurs" if self.lang == "fr" else "At higher levels"

    @property
    def spell_carac_text(self):
        if self.lang == "fr":
            return "le modificateur de votre caractéristique d'incantation"
        return "your spellcasting ability modifier"

    def highlight_die_value(self, text):
        die_value_pattern = r"\dd\d+( \+ " + self.spell_carac_text + ")?"
        return re.sub(die_value_pattern, lambda match: f"<b>{match.group(0)}</b>", text)

    def to_card(self):
        if self.upcasting_text:
            upcasting_parts = [
                "text |",
                f"section | {self.upcasting_section_title}",
                f"text | {self.upcasting_text}",
            ]
        else:
            upcasting_parts = []
        return {
            "count": 1,
            "color": self.color,
            "title": self.title,
            "icon": "magic-swirl",
            "icon_back": "magic-swirl",
            "contents": [
                f"subtitle | {self.subtitle}",
                "rule",
                f"property | {self.casting_time_text}: | {self.casting_time}",
                f"property | {self.casting_range_text}: | {self.casting_range}",
                f"property | {self.casting_components_text}: | {self.casting_components}",
                f"property | {self.effect_duration_text}: | {self.effect_duration}",
                "rule",
            ]
            + [
                f"text | {self.highlight_die_value(text_part)}"
                for text_part in self.text
            ]
            + upcasting_parts,
            "tags": self.tags,
        }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spells", nargs="+")
    parser.add_argument("-o", "--output", type=Path)
    return parser.parse_args()



def scrape_property(div, classname, remove):
    prop = div.find("div", class_=classname).text
    for term in remove:
        prop = prop.replace(term, "")
    return prop.strip()


def scrape_spell_texts(div, lang):
    upcasting_indicator_by_lang = {
        "fr": "Aux niveaux supérieurs",
        "en": "At Higher Levels",
    }
    text = list(div.find("div", class_="description").strings)
    upcasting_indicator = upcasting_indicator_by_lang[lang]
    if upcasting_indicator not in text:
        return text, ""
    upcasting_text_element_index = text.index(upcasting_indicator)
    upcasting_text_parts = text[upcasting_text_element_index + 1 :]
    upcasting_text_parts = [re.sub(r"^\. ", "", part) for part in upcasting_text_parts]
    upcasting_text = "\n".join(upcasting_text_parts)
    text = text[:upcasting_text_element_index]
    return text, upcasting_text


def scrape_spell_details(spell, lang):
    lang_param = "vf" if lang == "fr" else "vo"
    resp = requests.get(AIDEDD_SPELLS_URL, params={lang_param: spell})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, features="html.parser")
    div_content = soup.find("div", class_="content")
    level = int(
        div_content.find("div", class_="ecole")
        .text.split(" - ")[0]
        .replace("niveau", "")
        .replace("level", "")
        .strip()
    )
    text, upcasting_text = scrape_spell_texts(div_content, lang)
    spell = Spell(
        lang=lang,
        color="#" + SPELL_COLORS_BY_LEVEL[level],
        level=level,
        title=div_content.find("h1").text.strip(),
        school=div_content.find("div", class_="ecole")
        .text.split(" - ")[1]
        .strip()
        .capitalize(),
        casting_time=scrape_property(
            div_content, "t", ["Temps d'incantation :", "Casting Time:"]
        ),
        casting_range=scrape_property(div_content, "r", ["Portée :", "Range:"]),
        casting_components=scrape_property(
            div_content, "c", ["Composantes :", "Components:"]
        ),
        effect_duration=scrape_property(div_content, "d", ["Durée :", "Duration:"]),
        tags=[d.text for d in div_content.find_all("div", class_="classe")],
        text=text,
        upcasting_text=upcasting_text,
    )
    return spell


def main():
    args = parse_args()
    spells = []
    for spell in args.spells:
        lang, spell = spell.split(":")
        print(f"Scraping data for {spell}")
        spell_data = scrape_spell_details(spell, lang)
        spells.append(spell_data)
    spells = sorted(spells, key=lambda spell: (spell.level, spell.title))
    cards = [spell.to_card() for spell in spells]
    with open(args.output, "w") as out:
        json.dump(cards, out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
