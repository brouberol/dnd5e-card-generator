import re
from dataclasses import dataclass
from functools import cached_property
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from dnd5e_card_generator.const import (
    AIDEDD_MAGIC_ITEMS_URL,
    AIDEDD_SPELLS_FILTER_URL,
    AIDEDD_SPELLS_URL,
    FIVE_E_SHEETS_SPELLS,
)
from dnd5e_card_generator.magic_item import MagicItem
from dnd5e_card_generator.models import (
    DamageType,
    MagicItemKind,
    MagicItemRarity,
    MagicSchool,
    SpellShape,
)
from dnd5e_card_generator.spell import Spell
from dnd5e_card_generator.utils import fetch_data


@dataclass
class SpellFilter:
    class_name: str
    min_lvl: int
    max_lvl: int

    @staticmethod
    def class_name_synonyms():
        return {
            "artificer": "a",
            "artificier": "a",
            "bard": "b",
            "barde": "b",
            "cleric": "c",
            "clerc": "c",
            "druid": "d",
            "druide": "d",
            "sorcerer": "s",
            "ensorceleur": "s",
            "wizard": "w",
            "magicien": "w",
            "warlock": "k",
            "occultiste": "k",
            "paladin": "p",
            "ranger": "r",
            "rodeur": "r",
        }

    @classmethod
    def from_str(cls, s: str) -> "SpellFilter":
        class_name, min_lvl, max_lvl = s.split(":")
        resolved_class_name = cls.class_name_synonyms().get(class_name, class_name)
        return SpellFilter(
            class_name=resolved_class_name, min_lvl=int(min_lvl), max_lvl=int(max_lvl)
        )

    def request(self) -> requests.Response:
        resp = requests.post(
            AIDEDD_SPELLS_FILTER_URL,
            headers={
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "Filtre1[]": [self.class_name],
                "nivMin": self.min_lvl,
                "nivMax": self.max_lvl,
                "source[]": ["base", "xgte", "tcoe", "ftod"],
                "opt_tcoe": "S",
                "colE": "on",
                "colI": "on",
                "colC": "on",
                "colR": "on",
                "filtrer": "FILTRER",
            },
        )
        resp.raise_for_status()
        return resp

    def resolve(self) -> list[str]:
        out = []
        resp = self.request()
        soup = BeautifulSoup(resp.text, features="html.parser")
        spell_cells = soup.find("table").find_all("td", class_="item")
        for spell_cell in spell_cells:
            link = spell_cell.find("a")
            query = parse_qs(urlparse(link.attrs["href"]).query)
            out.append(f"fr:{query['vf'][0]}")
        return out


class SpellScraper:
    upcasting_indicator_by_lang = {
        "fr": "Aux niveaux supérieurs",
        "en": "At Higher Levels",
    }
    paying_components_indicator_by_lang = {
        "fr": "valant au moins",
        "en": "worth at least",
    }
    spell_damage_by_lang = {
        "fr": r"dégâts (de |d')?(type )?(?P<dmg>[^\.\sà,]+)s?",
        "en": r"(?P<dmg>\w+) damage",
    }

    effect_duration_by_lang = {"fr": "Durée :", "en": "Duration:"}
    components_by_lang = {"fr": "Composantes :", "en": "Components:"}
    casting_time_by_lang = {"fr": "Temps d'incantation :", "en": "Casting Time:"}
    casting_range_by_lang = {"fr": "Portée :", "en": "Range:"}
    ritual_pattern = r"\((ritual|rituel)\)"
    reaction_pattern = r"\d r[ée]action"
    concentration_pattern = r"concentration, "
    tags_to_unwrap_from_description = ["em", "a"]

    def __init__(self, spell: str, lang: str):
        self.spell = spell
        self.lang = lang
        html = fetch_data(AIDEDD_SPELLS_URL, spell, lang)
        self.soup = BeautifulSoup(html, features="html.parser")
        self.div_content = self.soup.find("div", class_="content")
        if self.div_content is None:
            raise ValueError(f"{spell} not found!")

    def sanitize_soup(self, soup: BeautifulSoup):
        # Remove emphasis and links from the div, to avoid causing whitespace
        # issues when extracting the text content
        for tag in soup.find_all(self.tags_to_unwrap_from_description):
            tag.unwrap()
        # Hack, cf https://stackoverflow.com/questions/44679677/get-real-text-with-beautifulsoup-after-unwrap
        string_soup = str(soup)
        new_soup = BeautifulSoup(string_soup, features="html.parser")
        return new_soup

    @cached_property
    def five_e_sheets_spell(self) -> dict:
        return FIVE_E_SHEETS_SPELLS[self.scrape_en_title()]

    def _scrape_property(self, classname: str, remove: list[str]) -> str:
        prop = self.div_content.find("div", class_=classname).text
        for term in remove:
            prop = prop.replace(term, "")
        return prop.strip()

    def scrape_level(self) -> int:
        return int(
            self.div_content.find("div", class_="ecole")
            .text.split(" - ")[0]
            .replace("niveau", "")
            .replace("level", "")
            .strip()
        )

    def scrape_spell_texts(self) -> tuple[list[str], str]:
        desc_div = self.sanitize_soup(
            self.div_content.find("div", class_="description")
        )
        text = list(desc_div.strings)
        upcasting_indicator = self.upcasting_indicator_by_lang[self.lang]
        if upcasting_indicator not in text:
            return text, ""

        upcasting_text_element_index = text.index(upcasting_indicator)
        upcasting_text_parts = text[upcasting_text_element_index + 1 :]
        upcasting_text_parts = [
            re.sub(r"^\. ", "", part) for part in upcasting_text_parts
        ]
        upcasting_text = "\n".join(upcasting_text_parts)
        text = text[:upcasting_text_element_index]
        return text, upcasting_text

    def scrape_school_text(self) -> str:
        return (
            self.div_content.find("div", class_="ecole")
            .text.split(" - ")[1]
            .strip()
            .capitalize()
        )

    def scrape_title(self) -> str:
        return self.div_content.find("h1").text.strip()

    def scrape_en_title(self) -> str:
        if self.lang == "en":
            return self.scrape_title()
        return self.div_content.find("div", class_="trad").find("a").text

    def scrape_casting_range(self) -> str:
        return self._scrape_property("r", list(self.casting_range_by_lang.values()))

    def scrape_casting_time(self) -> str:
        return self._scrape_property("t", list(self.casting_time_by_lang.values()))

    def scrape_effect_duration(self) -> str:
        return self._scrape_property("d", list(self.effect_duration_by_lang.values()))

    def scrape_casting_components(self) -> str:
        return self._scrape_property("c", list(self.components_by_lang.values()))

    def scrape_text(self) -> list[str]:
        return [d.text for d in self.div_content.find_all("div", class_="classe")]

    def scrape_spell_shape(self) -> Optional[SpellShape]:
        area_tags = self.five_e_sheets_spell.get("area_tags", [])
        area_tags = [tag for tag in area_tags if tag not in ["ST", "MT"]]
        if area_tags:
            # If several shapes are found, we randomly pick the first one
            return SpellShape.from_5esheet_tag(area_tags[0])
        return None

    def scrape_spell(self) -> Spell:
        print(f"Scraping data for spell {self.spell}")
        spell_text, upcasting_text = self.scrape_spell_texts()
        school_text = self.scrape_school_text()

        if ritual_match := re.search(self.ritual_pattern, school_text):
            school_text = school_text.replace(ritual_match.group(0), "").strip()
            ritual = True
        else:
            ritual = False
        effect_duration = self.scrape_effect_duration()
        if concentration_match := re.search(
            self.concentration_pattern, effect_duration
        ):
            effect_duration = effect_duration.replace(
                concentration_match.group(0), ""
            ).strip()
            concentration = True
        else:
            concentration = False

        casting_range = self.scrape_casting_range()
        casting_time = self.scrape_casting_time().capitalize()
        if reaction_match := re.match(self.reaction_pattern, casting_time):
            reaction_condition = casting_time.replace(reaction_match.group(), "")
            casting_time = reaction_match.group()
        else:
            reaction_condition = ""

        casting_components = self.scrape_casting_components()
        single_letter_casting_components = (
            re.sub(r"\(.+\)", "", casting_components).strip().split(", ")
        )
        verbal = "V" in single_letter_casting_components
        somatic = "S" in single_letter_casting_components
        material = "M" in single_letter_casting_components
        if material:
            if components_match := re.search(r"\((.+)\)", casting_components):
                components_text = components_match.group(1)
                paying_components = (
                    components_text.capitalize()
                    if self.paying_components_indicator_by_lang[self.lang]
                    in components_text
                    else ""
                )
                if paying_components and not paying_components.endswith("."):
                    paying_components = f"{paying_components}."
        else:
            paying_components = ""

        search_text = "\n".join(spell_text)
        if damage_type_match := re.search(
            self.spell_damage_by_lang[self.lang], search_text
        ):
            damage_type_str = damage_type_match.group("dmg")
            if damage_type_str.endswith("s"):
                damage_type_str = damage_type_str.rstrip("s")
            damage_type = DamageType.from_str(damage_type_str, self.lang)
        else:
            damage_type = None

        return Spell(
            lang=self.lang,
            level=self.scrape_level(),
            title=self.scrape_title(),
            en_title=self.scrape_en_title(),
            school=MagicSchool.from_str(school_text.lower(), self.lang),
            casting_time=casting_time,
            casting_range=casting_range.capitalize(),
            somatic=somatic,
            verbal=verbal,
            material=material,
            paying_components=paying_components.capitalize(),
            effect_duration=effect_duration.capitalize(),
            tags=self.scrape_text(),
            text=spell_text,
            upcasting_text=upcasting_text,
            ritual=ritual,
            concentration=concentration,
            damage_type=damage_type,
            shape=self.scrape_spell_shape(),
            reaction_condition=reaction_condition,
        )


def scrape_item_details(item: str, lang: str) -> MagicItem:
    print(f"Scraping data for item {item}")
    attunement_text_by_lang = {
        "fr": "nécessite un lien",
        "en": "requires attunement",
    }
    html = fetch_data(AIDEDD_MAGIC_ITEMS_URL, item, lang)
    attunement_text = attunement_text_by_lang[lang]
    soup = BeautifulSoup(html, features="html.parser")
    div_content = soup.find("div", class_="content")
    if div_content is None:
        raise ValueError(f"{item} not found!")

    item_type_div_text = div_content.find("div", class_="type").text
    item_type_text, _, item_rarity = item_type_div_text.partition(",")
    item_rarity = item_rarity.strip()
    if re.match(r"(armor|armure)", item_type_text.lower()):
        item_type = MagicItemKind.armor
    elif re.match(r"(arme|weapon)", item_type_text.lower()):
        item_type = MagicItemKind.weapon
    else:
        item_type = MagicItemKind.from_str(item_type_text.lower(), lang)

    if attunement_text in item_rarity:
        requires_attunement_pattern = r"\(" + attunement_text + r"([\s\w\,]+)?" + r"\)"
        item_rarity = re.sub(requires_attunement_pattern, "", item_rarity).strip()
        requires_attunement = True
    else:
        requires_attunement = False
    img_elt = soup.find("img")
    image_url = img_elt.attrs["src"] if img_elt else ""
    rarity = MagicItemRarity.from_str(item_rarity, lang)
    item_description = list(div_content.find("div", class_="description").strings)
    recharges_match = re.search(r"(\d+) charges", " ".join(item_description))
    recharges = int(recharges_match.group(1) if recharges_match else 0)
    magic_item = MagicItem(
        title=div_content.find("h1").text.strip(),
        type=item_type,
        attunement=requires_attunement,
        text=item_description,
        rarity=rarity,
        color="#" + rarity.color,
        lang=lang,
        image_url=image_url,
        recharges=recharges,
    )
    return magic_item
