from dnd5e_card_generator.spell import Spell

from .aidedd import SpellFilter, SpellScraper, scrape_item_details  # noqa


def resolve_spell_filter(spell_filter: int):
    return SpellFilter.from_str(spell_filter).resolve()


def scrape_spell_details(spell: str, lang: str) -> Spell:
    scraper = SpellScraper(spell, lang)
    return scraper.scrape_spell()
