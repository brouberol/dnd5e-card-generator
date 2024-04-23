import concurrent.futures

from .scraping.aidedd import FeatScraper, MagicItemScraper, SpellScraper
from .spell import SpellLegend


def scrape_elements(elements, ScraperCls, sorting_func):
    if not elements:
        return []

    tasks, models = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for element in elements:
            lang, slug = element.split(":")
            scraper = ScraperCls(slug=slug, lang=lang)
            tasks.append(executor.submit(scraper.scrape))
        for future in concurrent.futures.as_completed(tasks):
            models.append(future.result())
    models = sorted(models, key=sorting_func)
    return [model.to_card() for model in models]


def export_spells_to_cards(spell_names: list[str], include_legend: bool) -> list[dict]:
    """Scrape Aidedd for the provided spells and export them as cards data.

    If include_legend=True, then a legend card will be generated and added at the end
    of the spell cards.

    """
    cards = scrape_elements(
        elements=spell_names,
        ScraperCls=SpellScraper,
        sorting_func=lambda spell: (spell.level, spell.title),
    )
    if include_legend:
        cards.append(SpellLegend("fr").to_card())
    return cards


def export_items_to_cards(item_names: list[str]) -> list[dict]:
    """Scrape Aidedd for the provided items and export them as cards data."""
    return scrape_elements(
        elements=item_names,
        ScraperCls=MagicItemScraper,
        sorting_func=lambda item: (int(item.rarity), item.title),
    )


def export_feats_to_cards(feat_names: list[str]) -> list[dict]:
    """Scrape Aidedd for the provided feats and export them as cards data."""
    return scrape_elements(
        elements=feat_names,
        ScraperCls=FeatScraper,
        sorting_func=lambda item: item.title,
    )
