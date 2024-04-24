import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"
AIDEDD_CLASS_RULES_URL = "https://www.aidedd.org/regles/classes/{class_}"
AIDEDD_FEATS_ITEMS_URL = "https://www.aidedd.org/dnd/dons.php"
AIDEDD_MAGIC_ITEMS_URL = "https://www.aidedd.org/dnd/om.php"
AIDEDD_SPELLS_FILTER_URL = "https://www.aidedd.org/dnd-filters/sorts.php"
AIDEDD_UNEARTHED_ARCANA_URL = "https://www.aidedd.org/dnd-5/unearthed-arcana/{class_}"
SPELLS_BY_TYPE = json.load(open(DATA_DIR / "spell_by_types.json"))
FIVE_E_SHEETS_SPELLS = json.load(open(DATA_DIR / "spells.json"))
COLORS = {
    "class_feature": "DarkCyan",
    "feat": "#994094",
    # https://colordesigner.io/color-scheme-builder#5C4B51-8CBEB2-F2EBBF-F3B562-F06060
    "magic_item": {
        "common": "5C4B51",
        "uncommon": "8CBEB2",
        "rare": "BDD684",
        "very_rare": "F3B562",
        "legendary": "F06060",
        "artifact": "9575CD",
    },
    # https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
    "spell": {
        0: "277DA1",
        1: "577590",
        2: "4D908E",
        3: "43AA8B",
        4: "90BE6D",
        5: "F9C74F",
        6: "F8961E",
        7: "F9844A",
        8: "F3722C",
        9: "F94144",
    },
}
