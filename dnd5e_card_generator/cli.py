#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from .color import generate_palette
from .config import Config
from .export import (
    export_class_features_to_cards,
    export_eldricht_invocations_to_cards,
    export_feats_to_cards,
    export_items_to_cards,
    export_spells_to_cards,
    export_ancestry_features_to_cards,
    export_backgrounds_to_cards,
)
from .models import (
    CliClassFeature,
    CliEldrichtInvocation,
    CliFeat,
    CliMagicItem,
    CliSpell,
    CliSpellFilter,
    CliAncestryFeature,
    CliBackground,
)
from .scraping.aidedd import SpellFilter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape spell details from aidedd.org",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--spells",
        nargs="+",
        help=("Space separated <lang>:<spell-slug> items.\nExample: fr:lumiere en:toll-the-dead"),
        required=False,
        default=[],
        type=CliSpell.from_str,
    )
    parser.add_argument(
        "--spell-colors",
        nargs="+",
        help=(
            "Space separated hexadecimal colors associated with spells. If provided, a gradient "
            "palette will be generated from these colors, and associated with each spell level.\n"
            "Example: '#646fe1' '#e16492'"
        ),
        required=False,
        type=str,
    )
    parser.add_argument(
        "--spell-filter",
        help=(
            "Filter resolved to a list of spells, of form <lang>:<class>:<start-lvl>:<end-level>.\n"
            "Example: fr:clerc:0:1"
        ),
        required=False,
        type=CliSpellFilter.from_str,
    )
    parser.add_argument(
        "--include-spell-legend",
        help="Include a card with the legend of spell pictograms",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--items",
        nargs="+",
        help=(
            "Space separated <lang>:<item-slug> items.\n"
            "Example: fr:balai-volant fr:armure-de-vulnerabilite"
        ),
        required=False,
        default=[],
        type=CliMagicItem.from_str,
    )
    parser.add_argument(
        "--feats",
        nargs="+",
        help="Space separated <lang>:<feat-slug> items.\nExample: fr:mage-de-guerre fr:sentinelle",
        required=False,
        default=[],
        type=CliFeat.from_str,
    )
    parser.add_argument(
        "--eldricht-invocations",
        nargs="+",
        help=(
            "Space separated <lang>:<invocation-slug> items.\nExample: fr:arme-de-pacte-amelioree"
        ),
        required=False,
        default=[],
        type=CliEldrichtInvocation.from_str,
    )
    parser.add_argument(
        "--class-features",
        nargs="+",
        help=(
            "Space separated <lang>:<class>:<feature title> items.\n"
            "Example: 'fr:clerc:Conduit divin : renvoi des morts-vivants'"
        ),
        required=False,
        default=[],
        type=CliClassFeature.from_str,
    )
    parser.add_argument(
        "--ancestry-features",
        nargs="+",
        help=(
            "Space separated <lang>:<ancestry>:[sub_ancestry].\n"
            "Examples: 'fr:nain', 'fr:elfe:Elfe Noir"
        ),
        required=False,
        default=[],
        type=CliAncestryFeature.from_str,
    )
    parser.add_argument(
        "--backgrounds",
        nargs="+",
        help="Space separated <lang>:<background>.\nExamples: fr:voyageur",
        required=False,
        default=[],
        type=CliBackground.from_str,
    )
    parser.add_argument(
        "--bypass-cache",
        action="store_true",
        help="Bypass local cache to force the scrapers to issue HTTP requests (default: False)",
        default=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="File to write the card data to",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    cards, spells = [], []

    if args.bypass_cache:
        Config.BYPASS_CACHE = True

    if args.spell_colors:
        Config.COLORS["spell"] = {
            lvl: color for lvl, color in enumerate(generate_palette(args.spell_colors, 10))
        }

    if args.spell_filter:
        spells_str = SpellFilter(**args.spell_filter.to_dict()).resolve()
        spells = list(set(spells_str))
        spells = [CliSpell.from_str(spell_str) for spell_str in spells_str]

    spells = args.spells + spells
    cards.extend(export_spells_to_cards(spells, include_legend=args.include_spell_legend))
    cards.extend(export_items_to_cards(args.items))
    cards.extend(export_feats_to_cards(args.feats))
    cards.extend(export_eldricht_invocations_to_cards(args.eldricht_invocations))
    cards.extend(export_class_features_to_cards(args.class_features))
    cards.extend(export_ancestry_features_to_cards(args.ancestry_features))
    cards.extend(export_backgrounds_to_cards(args.backgrounds))

    cards_json = json.dumps(cards, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as out:
            out.write(cards_json)
    else:
        sys.stdout.write(cards_json)


if __name__ == "__main__":
    main()
