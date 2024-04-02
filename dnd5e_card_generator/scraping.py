from bs4 import element, BeautifulSoup
import re
from .utils import fetch_data
from .const import AIDEDD_MAGIC_ITEMS_URL, AIDEDD_SPELLS_URL
from .spell import Spell
from .magic_item import MagicItem
from .models import MagicSchool, ItemType, Rarity


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
    html = fetch_data(AIDEDD_SPELLS_URL, spell, lang)
    soup = BeautifulSoup(html, features="html.parser")
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
    if ritual_match := re.search(r"\((ritual|rituel)\)", school_text):
        school_text = school_text.replace(ritual_match.group(0), "").strip()
        ritual = True
    else:
        ritual = False
    effect_duration = scrape_property(div_content, "d", ["Durée :", "Duration:"])
    if concentration_match := re.search(r"concentration, ", effect_duration):
        effect_duration = effect_duration.replace(
            concentration_match.group(0), ""
        ).strip()
        concentration = True
    else:
        concentration = False
    casting_components = scrape_property(
        div_content, "c", ["Composantes :", "Components:"]
    )
    single_letter_casting_components = (
        re.sub(r"\(.+\)", "", casting_components).strip().split(", ")
    )
    verbal = "V" in single_letter_casting_components
    somatic = "S" in single_letter_casting_components
    material = "M" in single_letter_casting_components

    paying_components_indicator_by_lang = {
        "fr": "valant au moins",
        "en": "worth at least",
    }
    if material:
        if components_text := re.search(r"\(.+\)", casting_components).group():
            paying_components = (
                components_text
                if paying_components_indicator_by_lang[lang] in components_text
                else ""
            )
    else:
        paying_components = ""
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
        level=level,
        title=div_content.find("h1").text.strip(),
        school=school_by_lang[lang][school_text.lower()],
        casting_time=scrape_property(
            div_content, "t", ["Temps d'incantation :", "Casting Time:"]
        ),
        casting_range=scrape_property(div_content, "r", ["Portée :", "Range:"]),
        somatic=somatic,
        verbal=verbal,
        material=material,
        paying_components=paying_components,
        effect_duration=effect_duration,
        tags=[d.text for d in div_content.find_all("div", class_="classe")],
        text=text,
        upcasting_text=upcasting_text,
        ritual=ritual,
        concentration=concentration,
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
    html = fetch_data(AIDEDD_MAGIC_ITEMS_URL, item, lang)
    attunement_text = attunement_text_by_lang[lang]
    soup = BeautifulSoup(html, features="html.parser")
    div_content = soup.find("div", class_="content")
    item_type_div_text = div_content.find("div", class_="type").text
    item_type_text, _, item_rarity = item_type_div_text.partition(",")
    item_rarity = item_rarity.strip()
    if re.match(r"(armor|armure)", item_type_text.lower()):
        item_type = ItemType.armor
    elif re.match(r"(arme|weapon)", item_type_text.lower()):
        item_type = ItemType.weapon
    else:
        item_type = type_text_by_lang[lang][item_type_text.lower()]

    if attunement_text in item_rarity:
        requires_attunement_pattern = r"\(" + attunement_text + r"([\s\w\,]+)?" + r"\)"
        item_rarity = re.sub(requires_attunement_pattern, "", item_rarity).strip()
        requires_attunement = True
    else:
        requires_attunement = False
    img_elt = soup.find("img")
    image_url = img_elt.attrs["src"] if img_elt else ""
    rarity = rarity_text_by_lang[lang][item_rarity]
    color = rarity.color
    item_description = list(div_content.find("div", class_="description").strings)
    recharges_match = re.search(r"(\d+) charges", " ".join(item_description))
    recharges = recharges_match.group(1) if recharges_match else ""
    magic_item = MagicItem(
        title=div_content.find("h1").text.strip(),
        type=item_type,
        attunement=requires_attunement,
        text=item_description,
        rarity=rarity,
        color="#" + color,
        lang=lang,
        image_url=image_url,
        recharges=recharges,
    )
    return magic_item
