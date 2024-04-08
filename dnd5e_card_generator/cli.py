#!/usr/bin/env python3

import argparse
import json
import shutil
import sys
from pathlib import Path

from .cards import export_items_to_cards, export_spells_to_cards
from .scraping import resolve_spell_filter


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
    )
    parser.add_argument(
        "--spell-filter",
        help=(
            "Filter resolved to a list of spells, of form <class>:<start-lvl>:<end-level>. "
            "Example: cleric:0:1"
        ),
        required=False,
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
    if not shutil.which("magick"):
        print(
            "Imagemagick is required. Please install it from your package manager or https://imagemagick.org/script/download.php"
        )
        sys.exit(1)

    args = parse_args()
    spells = args.spells
    if args.spell_filter:
        spells += resolve_spell_filter(args.spell_filter)
        spells = list(set(spells))

    cards = export_spells_to_cards(spells)
    cards += export_items_to_cards(args.items)
    with open(args.output, "w") as out:
        json.dump(cards, out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
