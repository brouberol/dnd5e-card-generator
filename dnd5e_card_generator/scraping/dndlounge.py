import json

import requests
from bs4 import BeautifulSoup

from dnd5e_card_generator.const import DATA_DIR
from dnd5e_card_generator.models import SpellType


class DndLoungeScraper:
    def parse_html(self, url: str) -> BeautifulSoup:
        resp = requests.get(url)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, features="html.parser")

    def parse_spell_names(self, url: str) -> list[str]:
        soup = self.parse_html(url)
        tbl = soup.find("table")
        return [tr.find("td").text.replace("’", "'") for tr in tbl.find_all("tr")[1:]]

    def scrape_spells_by_spells_type(self) -> dict[str, str]:
        out = {}
        for spell_type in [
            SpellType.aoe,
            SpellType.buff,
            SpellType.debuff,
            SpellType.utility,
            SpellType.healing,
            SpellType.damage,
        ]:
            url = f"https://www.dndlounge.com/{spell_type.name}-spells-5e/"
            spells_of_type = self.parse_spell_names(url)
            for spell in spells_of_type:
                out[spell] = spell_type.value
        return out


def main():
    spells_by_type = DndLoungeScraper().scrape_spells_by_spells_type()
    with open(DATA_DIR / "spell_by_types.json", "w") as f:
        json.dump(spells_by_type, f, indent=2, ensure_ascii=False)
