import re
import tempfile
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional, cast
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from dnd5e_card_generator.config import Config
from dnd5e_card_generator.const import (
    AIDEDD_CLASS_RULES_URL,
    AIDEDD_RACE_RULES_URL,
    AIDEDD_ELDRICHT_INVOCATIONS_URL,
    AIDEDD_FEATS_ITEMS_URL,
    AIDEDD_MAGIC_ITEMS_URL,
    AIDEDD_SPELLS_FILTER_URL,
    AIDEDD_SPELLS_URL,
    AIDEDD_UNEARTHED_ARCANA_URL,
    FIVE_E_SHEETS_SPELLS,
    AIDEDD_BACKGROUND_URL,
)
from dnd5e_card_generator.export.class_feature import ClassFeature
from dnd5e_card_generator.export.ancestry_feature import AncestryFeature
from dnd5e_card_generator.export.eldricht_invocation import EldrichtInvocation
from dnd5e_card_generator.export.feat import Feat
from dnd5e_card_generator.export.magic_item import MagicItem
from dnd5e_card_generator.export.spell import Spell
from dnd5e_card_generator.export.background import Background
from dnd5e_card_generator.models import (
    CharacterClass,
    DamageType,
    MagicItemKind,
    MagicItemRarity,
    MagicSchool,
    SpellShape,
    Language,
)
from dnd5e_card_generator.utils import human_readable_class_name, slugify


class ScrapingError(Exception): ...


@dataclass
class SpellFilter:
    lang: str
    class_name: str
    min_level: int
    max_level: int

    @property
    def class_name_synonyms(self):
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

    def request(self) -> requests.Response:
        resp = requests.post(
            AIDEDD_SPELLS_FILTER_URL,
            headers={
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "Filtre1[]": [self.class_name_synonyms[self.class_name]],
                "nivMin": self.min_level,
                "nivMax": self.max_level,
                "source[]": ["base", "xgte", "tcoe", "ftod"],
                "opt_tcoe": "S",
                "colE": "on",
                "colI": "on",
                "colC": "on",
                "colR": "on",
                "colVO": "on",
                "filtrer": "FILTRER",
            },
        )
        resp.raise_for_status()
        return resp

    def resolve(self) -> list[str]:
        out = []
        resp = self.request()
        soup = BeautifulSoup(resp.text, features="html.parser")
        table = soup.find("table")
        if not table:
            raise ScrapingError("no table found in page")
        table = cast(Tag, table)
        spell_rows = table.find_all("tr") or []
        for spell_row in spell_rows[1:]:  # skip headers
            if self.lang == "fr":
                link = spell_row.find("a")
                query = parse_qs(urlparse(link.attrs["href"]).query)
                out.append(f"{self.lang}:{query['vf'][0]}")
            elif self.lang == "en":
                en_title = cast(Tag, spell_row.find("td", class_="colVO")).text
                en_slug = slugify(en_title)
                out.append(f"{self.lang}:{en_slug}")
        return out


class BaseAideDDScraper:
    model = None
    model_url: str = ""
    tags_to_unwrap_from_description = ["a", "em", "ul", "li", "strong"]

    def __init__(self, slug: str, lang: Language):
        self.slug = slug
        self.lang = lang
        self.soup, self.div_content = self.parse_page()

    @property
    def base_url(self) -> str:
        return self.model_url

    def fetch_data(self):
        cached_file = Path(f"{tempfile.gettempdir()}/{self.lang}:{self.slug}.html")
        if cached_file.exists() and not Config.BYPASS_CACHE:
            return cached_file.read_text()
        lang_param = "vf" if self.lang == "fr" else "vo"
        resp = requests.get(self.base_url, params={lang_param: self.slug})
        resp.raise_for_status()
        cached_file.write_text(resp.text)
        return resp.text

    def parse_page(self) -> tuple[BeautifulSoup, Tag]:
        html = self.fetch_data()
        soup = BeautifulSoup(html, features="html.parser")
        div_content = soup.find("div", class_="col1") or soup.find("div", class_="content")
        if div_content is None:
            raise ScrapingError(f"{self.slug} not found!")
        return soup, cast(Tag, div_content)

    def sanitize_soup(self, soup: BeautifulSoup | Tag) -> BeautifulSoup:
        """Remove formatting tags form soup to avoid whitespace issues when extracting the text content"""
        for tag_type in self.tags_to_unwrap_from_description:
            for tag in soup.find_all(tag_type):
                if tag.name == "li":
                    if tag.string is None:
                        tag.string = tag.text
                    # This will help us later on to re-render the li bullet in the card
                    tag.string = "• " + tag.string
                    continue
                elif tag.name == "em":
                    tag.string = f"_{tag.string}_"
                elif tag.name == "strong":
                    tag.string = f"*{tag.string}*"
                tag.unwrap()

        # Hack, cf https://stackoverflow.com/questions/44679677/get-real-text-with-beautifulsoup-after-unwrap
        string_soup = str(soup)
        new_soup = BeautifulSoup(string_soup, features="html.parser")
        return new_soup

    def _find_in_tag(self, tag: Tag | NavigableString | BeautifulSoup, *args, **kwargs) -> Tag:
        match = tag.find(*args, **kwargs)
        if not match:
            raise ScrapingError(f"No match were found for {args}, {kwargs} ({self.slug})")
        return cast(Tag, match)

    def find_in_content(self, *args, **kwargs):
        return self._find_in_tag(self.div_content, *args, **kwargs)

    def find_in_soup(self, *args, **kwargs):
        return self._find_in_tag(self.soup, *args, **kwargs)

    def scrape_text_block(self, tag: Tag) -> list[str]:
        if tag.name == "table":
            return [str(tag)]
        desc_div = self.sanitize_soup(tag)
        return list(desc_div.strings)

    def scrape_title(self) -> str:
        return self.find_in_soup("h1").text.strip()

    def scrape_en_title(self) -> str:
        if self.lang == "en":
            return self.scrape_title()
        en_link = self.find_in_content("div", class_="trad").find("a")
        if not en_link:
            raise ScrapingError("No english link found")
        en_link = cast(Tag, en_link)
        return en_link.text

    def scrape_description(self) -> list[str]:
        return self.scrape_text_block(self.find_in_content("div", class_="description"))


class BaseItemPageScraper(BaseAideDDScraper):

    def scrape_title(self) -> str:
        return self.find_in_content("h1").text.strip()


class TitleDescriptionPrerequisiteScraper(BaseItemPageScraper):

    def scrape(self):
        print(
            f"Scraping data for {human_readable_class_name(self.model.__name__)} {self.slug}"  # pyright: ignore
        )
        prerequisite_div = self.div_content.find("div", class_="prerequis")
        return self.model(  # pyright: ignore
            title=self.scrape_title(),
            text=self.scrape_description(),
            prerequesite=prerequisite_div.text if prerequisite_div else None,
            lang=self.lang,
        )


class SpellScraper(BaseItemPageScraper):
    model_url = AIDEDD_SPELLS_URL
    # We surround these indicators with underscores as the text appears in italics
    # in the text, and this is our way to signal the card formatter to display this
    # text in italics in the end.
    upcasting_indicator_by_lang = {
        "fr": "_Aux niveaux supérieurs_",
        "en": "_At Higher Levels_",
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

    @cached_property
    def five_e_sheets_spell(self) -> dict:
        return FIVE_E_SHEETS_SPELLS[self.scrape_en_title()]

    def _scrape_property(self, classname: str, remove: list[str]) -> str:
        prop = self.find_in_content("div", class_=classname).text
        for term in remove:
            prop = prop.replace(term, "")
        return prop.strip()

    def scrape_level(self) -> int:
        return int(
            self.find_in_content("div", class_="ecole")
            .text.split(" - ")[0]
            .replace("niveau", "")
            .replace("level", "")
            .strip()
        )

    def scrape_spell_texts(self) -> tuple[list[str], str]:
        upcasting_indicator = self.upcasting_indicator_by_lang[self.lang]
        text = self.scrape_description()
        if upcasting_indicator not in text:
            return text, ""

        upcasting_text_element_index = text.index(upcasting_indicator)
        upcasting_text_parts = text[upcasting_text_element_index + 1 :]
        upcasting_text_parts = [re.sub(r"^\. ", "", part) for part in upcasting_text_parts]
        upcasting_text = "\n".join(upcasting_text_parts)
        text = text[:upcasting_text_element_index]
        return text, upcasting_text

    def scrape_school_text(self) -> str:
        return self.find_in_content("div", class_="ecole").text.split(" - ")[1].strip().capitalize()

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

    def scrape(self) -> Spell:
        print(f"Scraping data for spell {self.slug}")
        spell_text, upcasting_text = self.scrape_spell_texts()
        school_text = self.scrape_school_text()

        if ritual_match := re.search(self.ritual_pattern, school_text):
            school_text = school_text.replace(ritual_match.group(0), "").strip()
            ritual = True
        else:
            ritual = False
        effect_duration = self.scrape_effect_duration()
        if concentration_match := re.search(
            self.concentration_pattern, effect_duration, flags=re.I
        ):
            effect_duration = effect_duration.replace(concentration_match.group(0), "").strip()
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
        paying_components = ""
        if material:
            if components_match := re.search(r"\((.+)\)", casting_components):
                components_text = components_match.group(1)
                paying_components = (
                    components_text.capitalize()
                    if self.paying_components_indicator_by_lang[self.lang] in components_text
                    else ""
                )
                if paying_components and not paying_components.endswith("."):
                    paying_components = f"{paying_components}."

        search_text = "\n".join(spell_text)
        if damage_type_match := re.search(self.spell_damage_by_lang[self.lang], search_text):
            damage_type_str = damage_type_match.group("dmg")
            if damage_type_str.endswith("s"):
                damage_type_str = damage_type_str.rstrip("s")
            try:
                damage_type = DamageType.from_str(damage_type_str, self.lang)
            # sometimes, the text can be confusing and we get something like `former damage`
            # instead of a damage type, like `fire damage`. We just ignore them.
            except KeyError:
                damage_type = None
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


class MagicItemScraper(BaseItemPageScraper):
    model_url = AIDEDD_MAGIC_ITEMS_URL

    attunement_text_by_lang = {
        "fr": "nécessite un lien",
        "en": "requires attunement",
    }

    def scrape(self) -> MagicItem:
        print(f"Scraping data for item {self.slug}")

        attunement_text = self.attunement_text_by_lang[self.lang]
        item_type_div_text = self.find_in_content("div", class_="type").text
        item_type_text, _, item_rarity = item_type_div_text.partition(",")
        item_rarity = item_rarity.strip()
        if re.match(r"(armor|armure)", item_type_text.lower()):
            item_type = MagicItemKind.armor
        elif re.match(r"(arme|weapon)", item_type_text.lower()):
            item_type = MagicItemKind.weapon
        else:
            item_type = MagicItemKind.from_str(item_type_text.lower(), self.lang)

        if attunement_text in item_rarity:
            requires_attunement_pattern = r"\(" + attunement_text + r"([\s\w\,]+)?" + r"\)"
            item_rarity = re.sub(requires_attunement_pattern, "", item_rarity).strip()
            requires_attunement = True
        else:
            requires_attunement = False
        img_elt = cast(Tag | None, self.soup.find("img"))
        image_url = img_elt.attrs["src"] if img_elt else ""
        rarity = MagicItemRarity.from_str(item_rarity, self.lang)
        item_description = list(self.find_in_content("div", class_="description").strings)
        recharges_match = re.search(r"(\d+) charges", " ".join(item_description))
        recharges = int(recharges_match.group(1) if recharges_match else 0)
        magic_item = MagicItem(
            title=self.scrape_title(),
            type=item_type,
            attunement=requires_attunement,
            text=item_description,
            rarity=rarity,
            lang=self.lang,
            image_url=image_url,
            recharges=recharges,
        )
        return magic_item


class FeatScraper(TitleDescriptionPrerequisiteScraper):
    model_url = AIDEDD_FEATS_ITEMS_URL
    model = Feat


class EldrichInvocationScraper(TitleDescriptionPrerequisiteScraper):
    model_url = AIDEDD_ELDRICHT_INVOCATIONS_URL
    model = EldrichtInvocation


class CharacterClassFeatureScraper(BaseAideDDScraper):
    class_variant_indicator = {
        CharacterClass.artificer: "Spécialité",
        CharacterClass.barbarian: "Voie",
        CharacterClass.bard: "Collège",
        CharacterClass.cleric: "Domaine",
        CharacterClass.druid: "Cercle",
        CharacterClass.monk: "Tradition",
        CharacterClass.paladin: "Serment",
        CharacterClass.ranger: "Archétype",
        CharacterClass.rogue: "Archétype",
        CharacterClass.sorcerer: "Origine",
        CharacterClass.warlock: "Patron",
        CharacterClass.warrior: "Archétype",
        CharacterClass.wizard: "Tradition",
    }

    def __init__(self, class_name: str, title: str, lang: Language):
        self.class_name = CharacterClass.from_str(class_name, lang)
        self.title = title
        super().__init__(slug=title, lang=lang)

    @property
    def base_url(self) -> str:
        if self.class_name == CharacterClass.artificer:
            return AIDEDD_UNEARTHED_ARCANA_URL.format(class_=self.class_name.translate(self.lang))
        return AIDEDD_CLASS_RULES_URL[self.lang].format(class_=self.class_name.translate(self.lang))

    def find_feature_section(self) -> Tag:
        for tag in self.soup.find_all(["h3", "h4"]):
            if tag.text == self.title:
                break
        else:
            raise ScrapingError(f"Class feature {self.title} not found")
        return tag

    def scrape_text(self) -> list[str]:
        tag = self.find_feature_section()
        accumulator, found_tag = [], False
        for t in self.soup.find_all():
            if t == tag:
                found_tag = True
                continue
            if t.name == "p" and found_tag:
                accumulator.append(self.sanitize_soup(t))
            elif t.name == "table" and found_tag:
                accumulator.append(t)
            elif t.name in ["h2", "h3", "h4"] and found_tag:
                break
        out = []
        for tag in accumulator:
            out.extend(self.scrape_text_block(tag))
        return out

    def scrape_class_variant(self) -> str | None:
        tag = self.find_feature_section()
        last_seen_h2: Tag | None = None
        last_seen_h3: Tag | None = None
        for t in cast(list[Tag], self.soup.find_all(["h2", "h3", tag.name])):
            if t == tag and last_seen_h2 is not None and last_seen_h3 is not None:
                if last_seen_h2.text.startswith(self.class_variant_indicator[self.class_name]):
                    return last_seen_h3.text
                else:
                    return
            elif t.name == "h2":
                last_seen_h2 = t
            elif t.name == "h3":
                last_seen_h3 = t
        return

    def scrape(self) -> ClassFeature:
        print(f"Scraping data for class feature {self.title}")
        text = self.scrape_text()
        class_variant = self.scrape_class_variant()
        return ClassFeature(
            text=text,
            title=self.title,
            lang=self.lang,
            class_name=self.class_name,
            class_variant=class_variant,
        )


class AncestryFeatureScraper(BaseAideDDScraper):
    model = AncestryFeature
    title_indicator = "Traits"

    def __init__(self, ancestry: str, sub_ancestry: str, lang: Language):
        self.ancestry = ancestry
        self.sub_ancestry = sub_ancestry
        super().__init__(slug=ancestry, lang=lang)

    @property
    def base_url(self) -> str:
        return AIDEDD_RACE_RULES_URL[self.lang].format(ancestry=self.ancestry)

    def find_feature_section(self) -> Tag:
        if self.sub_ancestry:
            for tag in self.soup.find_all(["h4"]):
                if tag.text.endswith(self.sub_ancestry):
                    break
            else:
                raise ScrapingError(f"Ancestry feature {self.sub_ancestry} not found")
        else:
            for tag in self.soup.find_all(["h3", "h4"]):
                if tag.text.endswith(self.title_indicator):
                    break
            else:
                raise ScrapingError(f"Ancestry feature {self.ancestry} not found")
        return tag

    def scrape_text(self) -> list[str]:
        tag = self.find_feature_section()
        accumulator, found_tag = [], False
        for t in self.soup.find_all():
            if t == tag:
                found_tag = True
                continue
            if (
                t.name == "p"
                and found_tag
                and "encadre" not in t.attrs.get("class", {})
                and not t.text.startswith("Sous-race.")
            ):
                accumulator.append(self.sanitize_soup(t))
            elif t.name == "table" and found_tag:
                accumulator.append(t)
            elif t.name in ["h2", "h3", "h4"] and found_tag:
                break
        out = []
        for tag in accumulator:
            out.extend(self.scrape_text_block(tag))

        return out

    def scrape(self) -> AncestryFeature:
        print(f"Scraping data for ancestry feature {self.sub_ancestry or self.ancestry}")
        return AncestryFeature(
            title=self.scrape_title(),
            lang=self.lang,
            sub_ancestry=self.sub_ancestry,
            text=self.scrape_text(),
        )


class BackgroundScraper(BaseAideDDScraper):
    model = Background
    marker = {"fr": "Capacité", "en": "Feature"}

    @property
    def base_url(self) -> str:
        return AIDEDD_BACKGROUND_URL[self.lang].format(background=self.slug)

    def scrape_subtitle(self) -> str:
        marker = self.marker[self.lang]
        for h4 in self.div_content.find_all("h4"):
            if h4.text.startswith(marker):
                return h4.text.replace(marker, "").lstrip(" ").lstrip(":").lstrip(" ")
        return ""

    def scrape_text(self) -> list[str]:
        accumulator = []
        for h4 in self.div_content.find_all("h4"):
            if h4.text.startswith(self.marker[self.lang]):
                for element in h4.find_next_siblings():
                    if element.name == "h4":
                        return accumulator
                    else:
                        accumulator.extend(self.scrape_text_block(element))
        return []

    def scrape(self) -> Background:
        print(f"Scraping data for background {self.slug}")
        return Background(
            title=self.scrape_title(),
            text=self.scrape_text(),
            lang=self.lang,
            subtitle=self.scrape_subtitle(),
        )
