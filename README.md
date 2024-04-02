# dnd5e-card-generator

Scrape data from https://aidedd.org to generate spell and items cards with https://rpg-cards.vercel.app

## Example

In this example., we'll scrape data for 13 cleric spell cards, in French. As _Toll the dead_ was never translated, we fallback to the english version.

The spell identifier is the one visible in the aidedd URL, Example: `toll-the-dead` from https://www.aidedd.org/dnd/sorts.php?vo=toll-the-dead.

```console
$ dnd5e-cards-generator \
    --spells \
      fr:lumiere \
      en:toll-the-dead \
      fr:stabilisation \
      fr:nappe-de-brouillard \
      fr:vague-tonnante \
      fr:mot-de-guerison \
      fr:soins \
      fr:benediction \
      fr:eclair-tracant \
      fr:bourrasque \
      fr:fracassement \
      fr:aide \
      fr:arme-spirituelle \
    --output bhargrim-cards.json
Scraping data for lumiere
Scraping data for toll-the-dead
Scraping data for stabilisation
Scraping data for nappe-de-brouillard
Scraping data for vague-tonnante
Scraping data for mot-de-guerison
Scraping data for soins
Scraping data for benediction
Scraping data for eclair-tracant
Scraping data for bourrasque
Scraping data for fracassement
Scraping data for aide
Scraping data for arme-spirituelle
$ cat bhargrim-cards.json | jq '.[0]'
{
  "count": 1,
  "color": "#277DA1",
  "title": "Lumière",
  "icon": "magic-swirl",
  "icon_back": "magic-swirl",
  "contents": [
    "subtitle | Tour de magie - Évocation",
    "rule",
    "property | Temps d'invocation: | 1 action",
    "property | Portée: | contact",
    "property | Composants: | V, M (une luciole ou de la mousse phosphorescente)",
    "property | Durée: | 1 heure",
    "rule",
    "text | Vous touchez un objet qui ne dépasse pas 3 mètres dans toutes les dimensions. Jusqu'à la fin du sort, l'objet émet une lumière vive dans un rayon de 6 mètres et une lumière faible sur 6 mètres supplémentaires. La lumière est de la couleur que vous voulez. Couvrir complètement l'objet avec quelque chose d'opaque bloque la lumière. Le sort se termine si vous le lancez de nouveau ou si vous le dissipez par une action.",
    "text | Si vous ciblez un objet tenu ou porté par une créature hostile, cette créature doit réussir un jet de sauvegarde de Dextérité pour éviter le sort."
  ],
  "tags": [
    "Barde",
    "Clerc",
    "Ensorceleur",
    "Magicien"
  ]
}
```

At this point, we can load `bhargrim-cards.json` in https://rpg-cards.vercel.app and export them as we wish.
