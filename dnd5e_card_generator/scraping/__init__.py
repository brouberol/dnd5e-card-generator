from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from dnd5e_card_generator.spell import Spell

from .aidedd import SpellFilter, SpellScraper, scrape_item_details  # noqa


# We override some beautifulsoup machinery to fail fast
class StrictTag(Tag):
    def find(self, *args, **kwargs) -> "StrictTag":
        tag = super(self).find(*args, **kwargs)  # type: ignore
        if not tag:
            raise ValueError("Tag not found")
        return tag

    def find_all(self, *args, **kwargs) -> ResultSet["StrictTag"]:
        rs = super(self).find(*args, **kwargs)  # type: ignore
        if not rs:
            raise ValueError("Tag not found")
        return rs


class StrictBeautifulSoup(BeautifulSoup):
    def find(self, *args, **kwargs) -> StrictTag:
        tag = super(self).find(*args, **kwargs)  # type: ignore
        if not tag:
            raise ValueError("Tag not found")
        return tag


def resolve_spell_filter(spell_filter: str):
    return SpellFilter.from_str(spell_filter).resolve()


def scrape_spell_details(spell: str, lang: str) -> Spell:
    scraper = SpellScraper(spell, lang)
    return scraper.scrape_spell()
