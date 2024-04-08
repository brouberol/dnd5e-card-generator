import re

from bs4 import BeautifulSoup

from .const import AIDEDD_MAGIC_ITEMS_URL, AIDEDD_SPELLS_URL
from .magic_item import MagicItem
from .models import DamageType, ItemType, MagicSchool, Rarity, SpellShape
from .spell import Spell
from .utils import fetch_data


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
        "fr": r"dégâts (de )?(type )?(?P<dmg>\w+)s?",
        "en": r"(?P<dmg>\w+) damage",
    }
    spell_heal_by_lang = {
        "fr": r"récupère [\w\s]+ points de vie",
        "en": r"regains [\w\s]+ hit points",
    }
    effect_duration_by_lang = {"fr": "Durée :", "en": "Duration:"}
    components_by_lang = {"fr": "Composantes :", "en": "Components:"}
    casting_time_by_lang = {"fr": "Temps d'incantation :", "en": "Casting Time:"}
    casting_range_by_lang = {"fr": "Portée :", "en": "Range:"}
    ritual_pattern = r"\((ritual|rituel)\)"
    concentration_pattern = r"concentration, "

    def __init__(self, spell: str, lang: str):
        self.spell = spell
        self.lang = lang
        html = fetch_data(AIDEDD_SPELLS_URL, spell, lang)
        self.soup = BeautifulSoup(html, features="html.parser")
        self.div_content = self.soup.find("div", class_="content")
        if self.div_content is None:
            raise ValueError(f"{spell} not found!")

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
        text = list(self.div_content.find("div", class_="description").strings)
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

    def scrape_casting_range(self) -> str:
        return self._scrape_property("r", list(self.casting_range_by_lang.values()))

    def scrape_casting_time(self) -> str:
        return self._scrape_property("t", list(self.casting_time_by_lang.values()))

    def scrape_effect_duration(self) -> str:
        return self._scrape_property("d", list(self.effect_duration_by_lang.values()))

    def scrape_casting_components(self) -> str:
        return self._scrape_property("c", list(self.components_by_lang.values()))

    def scrape_text(self) -> str:
        return [d.text for d in self.div_content.find_all("div", class_="classe")]

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
        casting_components = self.scrape_casting_components()
        single_letter_casting_components = (
            re.sub(r"\(.+\)", "", casting_components).strip().split(", ")
        )
        verbal = "V" in single_letter_casting_components
        somatic = "S" in single_letter_casting_components
        material = "M" in single_letter_casting_components
        if material:
            if components_text := re.search(r"\(.+\)", casting_components).group():
                paying_components = (
                    components_text
                    if self.paying_components_indicator_by_lang[self.lang]
                    in components_text
                    else ""
                )
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
        elif re.search(self.spell_heal_by_lang[self.lang], search_text):
            damage_type = DamageType.healing
        else:
            damage_type = None

        spell_shape_pattern = SpellShape.to_pattern(self.lang)
        for text in (search_text, casting_range):
            if spell_shape_match := re.search(spell_shape_pattern, text):
                spell_shape = SpellShape.from_str(spell_shape_match.group(), self.lang)
                break
        else:
            spell_shape = None

        return Spell(
            lang=self.lang,
            level=self.scrape_level(),
            title=self.scrape_title(),
            school=MagicSchool.from_str(school_text.lower(), self.lang),
            casting_time=self.scrape_casting_time(),
            casting_range=casting_range,
            somatic=somatic,
            verbal=verbal,
            material=material,
            paying_components=paying_components,
            effect_duration=effect_duration,
            tags=self.scrape_text(),
            text=spell_text,
            upcasting_text=upcasting_text,
            ritual=ritual,
            concentration=concentration,
            damage_type=damage_type,
            shape=spell_shape,
        )


def scrape_spell_details(spell: str, lang: str) -> Spell:
    scraper = SpellScraper(spell, lang)
    return scraper.scrape_spell()


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
        item_type = ItemType.armor
    elif re.match(r"(arme|weapon)", item_type_text.lower()):
        item_type = ItemType.weapon
    else:
        item_type = ItemType.from_str(item_type_text.lower(), lang)

    if attunement_text in item_rarity:
        requires_attunement_pattern = r"\(" + attunement_text + r"([\s\w\,]+)?" + r"\)"
        item_rarity = re.sub(requires_attunement_pattern, "", item_rarity).strip()
        requires_attunement = True
    else:
        requires_attunement = False
    img_elt = soup.find("img")
    image_url = img_elt.attrs["src"] if img_elt else ""
    rarity = Rarity.from_str(item_rarity, lang)
    item_description = list(div_content.find("div", class_="description").strings)
    recharges_match = re.search(r"(\d+) charges", " ".join(item_description))
    recharges = recharges_match.group(1) if recharges_match else ""
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
