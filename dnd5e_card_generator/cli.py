#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from .export import (
    export_class_features_to_cards,
    export_feats_to_cards,
    export_items_to_cards,
    export_spells_to_cards,
)
from .models import CliClassFeature, CliFeat, CliMagicItem, CliSpell, CliSpellFilter
from .scraping.aidedd import SpellFilter


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
        type=CliSpell.from_str,
    )
    parser.add_argument(
        "--spell-filter",
        help=(
            "Filter resolved to a list of spells, of form <class>:<start-lvl>:<end-level>. "
            "Example: cleric:0:1"
        ),
        required=False,
        type=CliSpellFilter.from_str,
    )
    parser.add_argument(
        "--include-spell-legend",
        help=("Include a card with the legend of spell pictograms"),
        required=False,
        action="store_true",
        default=False,
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
        type=CliMagicItem.from_str,
    )
    parser.add_argument(
        "--feats",
        nargs="+",
        help=(
            "Space separated <lang>:<feat-slug> items. "
            "Example: fr:mage-de-guerre fr:sentinelle"
        ),
        required=False,
        default=[],
        type=CliFeat.from_str,
    )
    parser.add_argument(
        "--class-features",
        nargs="+",
        help=(
            "Space separated <class>:<feature title> items. "
            "Example: 'clerc:Conduit divin : renvoi des morts-vivants'"
        ),
        required=False,
        default=[],
        type=CliClassFeature.from_str,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="File to write scraped spell data to",
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    cards, spells = [], []
    if args.spell_filter:
        spells_str = SpellFilter(**args.spell_filter.to_dict()).resolve()
        spells = list(set(spells_str))
        spells = [CliSpell.from_str(spell_str) for spell_str in spells_str]

    spells = args.spells + spells
    if spells:
        cards.extend(
            export_spells_to_cards(spells, include_legend=args.include_spell_legend)
        )
    if args.items:
        cards.extend(export_items_to_cards(args.items))
    if args.feats:
        cards.extend(export_feats_to_cards(args.feats))
    if args.class_features:
        cards.extend(export_class_features_to_cards(args.class_features))

    with open(args.output, "w") as out:
        json.dump(cards, out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
