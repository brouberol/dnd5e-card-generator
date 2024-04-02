from pathlib import Path

import glob

IMAGES_DIR = Path(__file__).parent.parent / "images"
AIDEDD_SPELLS_URL = "https://www.aidedd.org/dnd/sorts.php"
AIDEDD_MAGIC_ITEMS_URL = "https://www.aidedd.org/dnd/om.php"
NUM_WATERCOLORS = len(glob.glob(f"{IMAGES_DIR}/watercolor*.png"))
