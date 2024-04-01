#!/usr/bin/env python3

import argparse
import concurrent.futures
import json
import re
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pathlib import Path

import requests
from bs4 import BeautifulSoup, element

AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"
AIDEDD_MAGIC_ITEMS_URL = "https://www.aidedd.org/dnd/om.php"

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


class Rarity(IntEnum):
    common = 0
    uncommon = 1
    rare = 2
    very_rare = 3
    legendary = 4
    artifact = 5


class ItemType:
    wondrous_item = "wondrous_item"
    ring = "ring"
    weapon = "weapon"
    wand = "wand"
    armor = "armor"
    staff = "staff"
    potion = "potion"
    rod = "rod"


ITEM_ICON_BY_TYPE = {
    ItemType.armor: "lamellar",
    ItemType.weapon: "shard-sword",
    ItemType.ring: "ring",
    ItemType.wand: "lunar-wand",
    ItemType.wondrous_item: "eclipse-flare",
    ItemType.staff: "bo",
    ItemType.rod: "flanged-mace",
    ItemType.potion: "potion-ball",
}

# https://coolors.co/palette/003049-d62828-f77f00-fcbf49-eae2b7
MAGIC_ITEM_COLOR_BY_RARITY = {
    Rarity.common: "FFBA08",
    Rarity.uncommon: "F48C06",
    Rarity.rare: "E85D04",
    Rarity.very_rare: "DC2F02",
    Rarity.legendary: "9D0208",
    Rarity.artifact: "370617",
}


class MagicSchool(StrEnum):
    abjuration = "abjuration"
    divination = "divination"
    enchantment = "enchantment"
    conjuration = "conjuration"
    illusion = "illusion"
    evocation = "evocation"
    necromancy = "necromancy"
    transmutation = "transmutation"


def humanize_level(level: int) -> str:
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
    school: MagicSchool
    casting_time: str
    casting_range: str
    casting_components: str
    effect_duration: str
    text: list[str]
    upcasting_text: str
    tags: list[str]
    color: str

    @property
    def subtitle(self) -> str:
        if self.lang == "fr":
            if self.level == 0:
                return f"Tour de magie - {self.school_text}"
            else:
                return f"Niveau {self.level} - {self.school_text}"
        else:
            if self.level == 0:
                return f"{self.school_text} cantrip"
            else:
                return f"{humanize_level(self.level)}-level - {self.school_text}"

    @property
    def school_text(self):
        translations = {
            "fr": {
                MagicSchool.abjuration: "abjuration",
                MagicSchool.divination: "divination",
                MagicSchool.enchantment: "enchantement",
                MagicSchool.evocation: "évocation",
                MagicSchool.illusion: "illusion",
                MagicSchool.conjuration: "invocation",
                MagicSchool.necromancy: "nécromancie",
                MagicSchool.transmutation: "transmutation",
            },
            "en": {
                MagicSchool.abjuration: "abjuration",
                MagicSchool.divination: "divination",
                MagicSchool.enchantment: "enchantment",
                MagicSchool.evocation: "evocation",
                MagicSchool.illusion: "illusion",
                MagicSchool.conjuration: "conjuration",
                MagicSchool.necromancy: "necromancy",
                MagicSchool.transmutation: "transmutation",
            },
        }
        return translations[self.lang][self.school].capitalize()

    @property
    def casting_time_text(self) -> str:
        return "Temps d'invocation" if self.lang == "fr" else "Casting time"

    @property
    def casting_range_text(self) -> str:
        return "Portée" if self.lang == "fr" else "Range"

    @property
    def casting_components_text(self) -> str:
        return "Composants" if self.lang == "fr" else "Compoments"

    @property
    def effect_duration_text(self) -> str:
        return "Durée" if self.lang == "fr" else "Duration"

    @property
    def upcasting_section_title(self) -> str:
        return "Aux niveaux supérieurs" if self.lang == "fr" else "At higher levels"

    @property
    def spell_carac_text(self) -> str:
        if self.lang == "fr":
            return "le modificateur de votre caractéristique d'incantation"
        return "your spellcasting ability modifier"

    def highlight_die_value(self, text) -> str:
        die_value_pattern = r"\dd\d+( \+ " + self.spell_carac_text + ")?"
        return re.sub(die_value_pattern, lambda match: f"<b>{match.group(0)}</b>", text)

    def to_card(self) -> dict:
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
            "background_image": f"https://balthazar-rouberol.com/public/dnd-magic-schools/{str(self.school.value)}.jpg",
        }


@dataclass
class MagicItem:
    title: str
    type: ItemType
    color: str
    rarity: Rarity
    attunement: bool
    text: list[str]
    lang: str
    image_url: str
    recharges: int

    @property
    def icon(self):
        return ITEM_ICON_BY_TYPE[self.type]

    @property
    def attunement_text(self) -> str:
        return "harmonisation nécessaire" if self.lang == "fr" else "requires attunment"

    @property
    def type_text(self) -> str:
        translations = {
            "fr": {
                ItemType.armor: "Armure",
                ItemType.potion: "Potion",
                ItemType.ring: "Anneau",
                ItemType.rod: "Sceptre",
                ItemType.staff: "Bâton",
                ItemType.wand: "Baguette",
                ItemType.weapon: "Arme",
                ItemType.wondrous_item: "Objet merveilleux",
            },
            "en": {
                ItemType.armor: "Armor",
                ItemType.potion: "Potion",
                ItemType.ring: "Ring",
                ItemType.rod: "Rod",
                ItemType.staff: "Staff",
                ItemType.wand: "Wand",
                ItemType.weapon: "Weapon",
                ItemType.wondrous_item: "Wondrous item",
            },
        }
        return translations[self.lang][self.type]

    @property
    def rarity_text(self) -> str:
        translations = {
            "fr": {
                Rarity.common: "commun",
                Rarity.uncommon: "peu commun",
                Rarity.rare: "rare",
                Rarity.very_rare: "très rare",
                Rarity.legendary: "légendaire",
                Rarity.artifact: "artéfact",
            },
            "en": {
                Rarity.common: "common",
                Rarity.uncommon: "uncommun",
                Rarity.rare: "rare",
                Rarity.very_rare: "very rare",
                Rarity.legendary: "legendary",
                Rarity.artifact: "artifact",
            },
        }
        return translations[self.lang][self.rarity]

    @property
    def subtitle(self) -> SyntaxWarning:
        parts = [self.type_text, self.rarity_text]
        if self.attunement:
            parts.append(self.attunement_text)
        return ", ".join(parts)

    def to_card(self) -> dict:
        extra_content = []
        if self.recharges:
            extra_content.extend(['fill | ', f'boxes | {self.recharges} | 1.5']) # 1.5 is in em
        card = {
            "count": 1,
            "color": self.color,
            "title": self.title,
            "icon": self.icon,
            "icon_back": self.icon,
            "contents": [
                f"subtitle | {self.subtitle}",
                "rule",
            ]
            + [f"text | {text_part}" for text_part in self.text] + extra_content
        }
        if self.image_url:
            card["background_image"] = self.image_url
        return card


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape spell details from aidedd.org")
    parser.add_argument(
        "--spells",
        nargs="+",
        help=(
            "Space separated <lang>:<spell-slug> items. "
            "Example: fr:lumiere en:toll-the-dead"
        ),
        required=False,
        default=[],
    )
    parser.add_argument(
        "--items",
        nargs="+",
        help=(
            "Space separated <lang>:<object-slug> items. "
            "Example: fr:balai-volant fr:armure-de-vulnerabilite"
        ),
        required=False,
        default=[],
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="File to write scraped spell data to",
        required=True,
    )
    return parser.parse_args()


def scrape_property(div: element.Tag, classname: str, remove: list[str]) -> str:
    prop = div.find("div", class_=classname).text
    for term in remove:
        prop = prop.replace(term, "")
    return prop.strip()


def scrape_spell_texts(div: element.Tag, lang: str) -> tuple[str, str]:
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


def scrape_spell_details(spell: str, lang: str) -> Spell:
    print(f"Scraping data for spell {spell}")
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
    school_text = (
        div_content.find("div", class_="ecole")
        .text.split(" - ")[1]
        .strip()
        .capitalize()
    )
    school_by_lang = {
        "fr": {
            "abjuration": MagicSchool.abjuration,
            "divination": MagicSchool.divination,
            "enchantement": MagicSchool.enchantment,
            "évocation": MagicSchool.evocation,
            "illusion": MagicSchool.illusion,
            "invocation": MagicSchool.conjuration,
            "nécromancie": MagicSchool.necromancy,
            "transmutation": MagicSchool.transmutation,
        },
        "en": {
            "abjuration": MagicSchool.abjuration,
            "divination": MagicSchool.divination,
            "enchantment": MagicSchool.enchantment,
            "evocation": MagicSchool.evocation,
            "illusion": MagicSchool.illusion,
            "conjuration": MagicSchool.conjuration,
            "necromancy": MagicSchool.necromancy,
            "transmutation": MagicSchool.transmutation,
        },
    }
    spell = Spell(
        lang=lang,
        color="#" + SPELL_COLORS_BY_LEVEL[level],
        level=level,
        title=div_content.find("h1").text.strip(),
        school=school_by_lang[lang][school_text.lower()],
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


def scrape_item_details(item: str, lang: str) -> MagicItem:
    print(f"Scraping data for item {item}")
    attunement_text_by_lang = {
        "fr": "nécessite un lien",
        "en": "requires attunement",
    }
    rarity_text_by_lang = {
        "fr": {
            "commun": Rarity.common,
            "peu commun": Rarity.uncommon,
            "rare": Rarity.rare,
            "très rare": Rarity.very_rare,
            "légendaire": Rarity.legendary,
            "artéfact": Rarity.artifact,
        },
        "en": {
            "commun": Rarity.common,
            "peu commun": Rarity.uncommon,
            "rare": Rarity.rare,
            "très rare": Rarity.very_rare,
            "légendaire": Rarity.legendary,
            "artéfact": Rarity.artifact,
        },
    }
    type_text_by_lang = {
        "fr": {
            "objet merveilleux": ItemType.wondrous_item,
            "anneau": ItemType.ring,
            "baguette": ItemType.wand,
            "armure": ItemType.armor,
            "bâton": ItemType.staff,
            "potion": ItemType.potion,
            "sceptre": ItemType.rod,
        },
        "en": {
            "wondrous item": ItemType.wondrous_item,
            "ring": ItemType.ring,
            "wand": ItemType.wand,
            "armor": ItemType.armor,
            "staff": ItemType.staff,
            "potion": ItemType.potion,
            "rod": ItemType.rod,
        },
    }
    lang_param = "vf" if lang == "fr" else "vo"
    resp = requests.get(AIDEDD_MAGIC_ITEMS_URL, params={lang_param: item})
    resp.raise_for_status()
    attunement_text = attunement_text_by_lang[lang]
    soup = BeautifulSoup(resp.text, features="html.parser")
    div_content = soup.find("div", class_="content")
    item_type_div_text = div_content.find("div", class_="type").text
    item_type_text, _, item_rarity = item_type_div_text.partition(",")
    item_rarity = item_rarity.strip()
    if "Armure" in item_type_text:
        item_type = ItemType.armor
    else:
        item_type = type_text_by_lang[lang][item_type_text.lower()]

    if attunement_text in item_rarity:
        requires_attunement_pattern = r'\(' + attunement_text + r'([\s\w\,]+)?' + r'\)'
        item_rarity = re.sub(requires_attunement_pattern, '', item_rarity).strip()
        requires_attunement = True
    else:
        requires_attunement = False
    img_elt = soup.find("img")
    image_url = img_elt.attrs["src"] if img_elt else ""
    rarity = rarity_text_by_lang[lang][item_rarity]
    color = MAGIC_ITEM_COLOR_BY_RARITY[rarity]
    item_description = list(div_content.find("div", class_="description").strings)
    recharges_match = re.search(r'(\d+) charges', ' '.join(item_description))
    recharges = recharges_match.group(1) if recharges_match else ''
    magic_item = MagicItem(
        title=div_content.find("h1").text.strip(),
        type=item_type,
        attunement=requires_attunement,
        text=item_description,
        rarity=rarity,
        color="#" + color,
        lang=lang,
        image_url=image_url,
        recharges=recharges
    )
    return magic_item


def export_spells_to_cards(spell_names: list[str]) -> list[dict]:
    if not spell_names:
        return []

    tasks, spells = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for spell_name in spell_names:
            lang, spell_name = spell_name.split(":")
            tasks.append(executor.submit(scrape_spell_details, spell_name, lang))
        for future in concurrent.futures.as_completed(tasks):
            spells.append(future.result())
    spells = sorted(spells, key=lambda spell: (spell.level, spell.title))
    cards = [spell.to_card() for spell in spells]
    return cards


def export_items_to_cards(item_names: list[str]) -> list[dict]:
    if not item_names:
        return []

    tasks, items = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for item_name in item_names:
            lang, item_name = item_name.split(":")
            tasks.append(executor.submit(scrape_item_details, item_name, lang))
        for future in concurrent.futures.as_completed(tasks):
            items.append(future.result())
    items = sorted(items, key=lambda item: (item.rarity, item.title))
    cards = [item.to_card() for item in items]
    return cards


def main():
    args = parse_args()
    cards = export_spells_to_cards(args.spells)
    cards += export_items_to_cards(args.items)
    with open(args.output, "w") as out:
        json.dump(cards, out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
