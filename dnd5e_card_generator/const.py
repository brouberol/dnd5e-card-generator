import glob
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / "images"
SYMBOLS_DIR = IMAGES_DIR / "symbols"
BACKGROUNDS_DIR = IMAGES_DIR / "backgrounds"
WATERCOLORS_DIR = IMAGES_DIR / "watercolors"
AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"
AIDEDD_SPELLS_FILTER_URL = "https://www.aidedd.org/dnd-filters/sorts.php"
AIDEDD_MAGIC_ITEMS_URL = "https://www.aidedd.org/dnd/om.php"
NUM_WATERCOLORS = len(glob.glob(f"{WATERCOLORS_DIR}/watercolor*.png"))
