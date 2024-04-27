import concurrent.futures

from dnd5e_card_generator.models import (
    CliClassFeature,
    CliEldrichtInvocation,
    CliFeat,
    CliMagicItem,
    CliSpell,
)
from dnd5e_card_generator.scraping.aidedd import (
    CharacterClassFeatureScraper,
    EldrichInvocationScraper,
    FeatScraper,
    MagicItemScraper,
    SpellScraper,
)

from .spell import SpellLegend


def export_elements_to_cards(elements, ScraperCls, sorting_func):
    if not elements:
        return []

    tasks, models = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for element in elements:
            scraper = ScraperCls(**element.to_dict())
            tasks.append(executor.submit(scraper.scrape))
        for future in concurrent.futures.as_completed(tasks):
            models.append(future.result())
    models = sorted(models, key=sorting_func)
    return [model.to_card() for model in models]


def export_spells_to_cards(
    spell_names: list[CliSpell], include_legend: bool
) -> list[dict]:
    """Scrape Aidedd for the provided spells and export them as cards data.

    If include_legend=True, then a legend card will be generated and added at the end
    of the spell cards.

    """
    cards = export_elements_to_cards(
        elements=spell_names,
        ScraperCls=SpellScraper,
        sorting_func=lambda spell: (spell.level, spell.title),
    )
    if include_legend:
        cards.append(SpellLegend("fr").to_card())
    return cards


def export_items_to_cards(item_names: list[CliMagicItem]) -> list[dict]:
    """Scrape Aidedd for the provided items and export them as cards data."""
    return export_elements_to_cards(
        elements=item_names,
        ScraperCls=MagicItemScraper,
        sorting_func=lambda item: (int(item.rarity), item.title),
    )


def export_feats_to_cards(feat_names: list[CliFeat]) -> list[dict]:
    """Scrape Aidedd for the provided feats and export them as cards data."""
    return export_elements_to_cards(
        elements=feat_names,
        ScraperCls=FeatScraper,
        sorting_func=lambda item: item.title,
    )


def export_class_features_to_cards(class_features: list[CliClassFeature]) -> list[dict]:
    return export_elements_to_cards(
        elements=class_features,
        ScraperCls=CharacterClassFeatureScraper,
        sorting_func=lambda item: (item.class_name, item.title),
    )


def export_eldricht_invocations_to_cards(
    eldricht_invocations: list[CliEldrichtInvocation],
) -> list[dict]:
    return export_elements_to_cards(
        elements=eldricht_invocations,
        ScraperCls=EldrichInvocationScraper,
        sorting_func=lambda item: item.title,
    )
