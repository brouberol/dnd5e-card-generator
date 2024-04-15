import concurrent.futures

from .scraping import scrape_item_details, scrape_spell_details
from .spell import SpellLegend


def export_spells_to_cards(spell_names: list[str], include_legend: bool) -> list[dict]:
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
    if include_legend:
        cards.append(SpellLegend(lang).to_card())
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
    items = sorted(items, key=lambda item: (int(item.rarity), item.title))
    cards = [item.to_card() for item in items]
    return cards
