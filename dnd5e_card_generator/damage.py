from .translator import TranslatedStrEnum


class DamageType(TranslatedStrEnum):
    acid = "acid"
    bludgeoning = "bludgeoning"
    cold = "cold"
    fire = "fire"
    force = "force"
    lightning = "lightning"
    necrotic = "necrotic"
    piercing = "piercing"
    poison = "poison"
    psychic = "psychic"
    radiant = "radiant"
    slashing = "slashing"
    thunder = "thunder"
    healing = "healing"

    @classmethod
    def fr_translations(self) -> dict:
        return {
            "acid": "acide",
            "bludgeoning": "contondant",
            "cold": "froid",
            "fire": "feu",
            "force": "force",
            "lightning": "éclair",
            "necrotic": "nécrotique",
            "piercing": "perforant",
            "poison": "poison",
            "psychic": "psychique",
            "radiant": "radiant",
            "slashing": "tranchant",
            "thunder": "tonnerre",
            "healing": "soin",
        }

    @property
    def icon(self) -> str:
        damage_to_icon = {
            "acid": "acid",
            "bludgeoning": "hammer-drop",
            "cold": "ice-spear",
            "fire": "fire-ray",
            "force": "mighty-force",
            "lightning": "lightning-tree",
            "necrotic": "burning-skull",
            "piercing": "arrowhead",
            "poison": "poison-bottle",
            "psychic": "psychic-waves",
            "radiant": "sunbeams",
            "slashing": "axe-sword",
            "thunder": "crowned-explosion",
            "healing": "health-potion",
        }
        return damage_to_icon.get(self.value)
