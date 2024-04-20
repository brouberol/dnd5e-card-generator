import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"
AIDEDD_SPELLS_FILTER_URL = "https://www.aidedd.org/dnd-filters/sorts.php"
AIDEDD_MAGIC_ITEMS_URL = "https://www.aidedd.org/dnd/om.php"
SPELLS_BY_TYPE = json.load(open(DATA_DIR / "spell_by_types.json"))
