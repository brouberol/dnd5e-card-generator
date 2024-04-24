import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"
AIDEDD_CLASS_RULES_URL = "https://www.aidedd.org/regles/classes/{class_}"
AIDEDD_FEATS_ITEMS_URL = "https://www.aidedd.org/dnd/dons.php"
AIDEDD_MAGIC_ITEMS_URL = "https://www.aidedd.org/dnd/om.php"
AIDEDD_SPELLS_FILTER_URL = "https://www.aidedd.org/dnd-filters/sorts.php"
SPELLS_BY_TYPE = json.load(open(DATA_DIR / "spell_by_types.json"))
FIVE_E_SHEETS_SPELLS = json.load(open(DATA_DIR / "spells.json"))
