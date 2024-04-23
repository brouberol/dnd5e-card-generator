import re

from .models import DamageDie, DamageFormula, DamageType


class BaseCardExporter:
    def _li(self, text: str) -> str:
        return f"<li>{text}</li>"

    def _strong(self, text: str) -> str:
        return f"<b>{text}</b>"

    def _highlight(self, pattern: str, text: str) -> str:
        return re.sub(pattern, lambda match: self._strong(match.group(0)), text)

    def _highlight(self, pattern: str, text: str) -> str:
        return re.sub(pattern, lambda match: self._strong(match.group(0)), text)

    def damage_type_text(self, lang) -> str:
        if lang == "fr":
            return r"(de )?dégâts (de |d')?(?P<damage_type>\w+)"
        return r"\w+ damage"

    def highlight_damage_formula(self, text: str, lang: str) -> str:
        die_value_pattern = (
            r"(?P<prefix>(one |un )?)(?P<num_die>\d+)?(?P<die_type>d\d+)( (?P<dmg_extra>\+ "
            + self.spell_carac_text
            + r")| "
            + self.damage_type_text(lang)
            + r")?"
        )
        matches = list(re.finditer(die_value_pattern, text))
        if not matches:
            return text

        for match in matches:
            parts = match.groupdict()
            damage_type = None
            if parts.get("damage_type"):
                damage_type = DamageType.from_str(
                    parts["damage_type"].rstrip("s"), lang
                )

            damage_formula = DamageFormula(
                num_die=int(parts.get("num_die") or 1),
                damage_die=DamageDie.from_str(parts["die_type"]),
                damage_type=damage_type,
            )
            text = text.replace(
                match.group(),
                self._strong(damage_formula.render() + (parts.get("dmg_extra") or "")),
            )
        return text

    def highlight_saving_throw(self, text: str, lang: str) -> str:
        saving_throw_patterns_by_lang = {
            "fr": [
                r"jet de sauvegarde de [A-Z]\w+",
                "la moitié de ces dégâts en cas de réussite",
            ],
            "en": [r"\w+ saving throw", "half as much damage on a successful one"],
        }
        for pattern in saving_throw_patterns_by_lang[lang]:
            text = self._highlight(pattern, text)
        return text

    def fix_text_with_subparts(self, text: list[str]) -> list[str]:
        text_copy = text.copy()
        for i, part in enumerate(text):
            if part.startswith(". "):
                text_copy[i - 1] = self._strong(text_copy[i - 1]) + part
                text_copy[i] = ""
        return [part for part in text_copy if part]

    def format_bullet_point(self, text: str) -> str:
        text = text.replace("• ", "")
        if m := re.match(r"((\w+)\s)+(?=:)", text):
            text = text.replace(m.group(), self._strong(m.group()))
        return self._li(text)

    def fix_text_with_bullet_points(self, text: list[str]) -> list[str]:
        out = []
        in_ul = False
        for part in text:
            if not part.startswith("• "):
                if in_ul:
                    out[-1] += "</ul>"
                out.append(part)
            elif not out:
                out.append("<ul>" + self.format_bullet_point(part))
            else:
                if not in_ul:
                    in_ul = True
                    out[-1] += "<ul>"
                out[-1] += self.format_bullet_point(part)
        return out
