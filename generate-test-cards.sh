#!/usr/bin/env bash

poetry run dnd5e-card-generator \
    --spell-filter cleric:0:1 \
    --spells fr:boule-de-feu en:toll-the-dead \
    --include-spell-legend \
    --items fr:cape-d-invisibilite fr:anneau-de-regeneration \
    --feats fr:athlete fr:sentinelle \
    --class-features \
        'fr:artificier:Outil de circonstance' \
        'fr:artificier:Élixir expérimental' \
        'fr:barbare:Sens du danger' \
        'fr:barbare:Esprit totem' \
        'fr:barde:Expertise' \
        'fr:barde:Mots cinglants' \
        'fr:clerc:Conduit divin' \
        'fr:clerc:Frappe divine' \
        'fr:druide:Jeunesse éternelle' \
        'fr:druide:Formes du cercle' \
        'fr:ensorceleur:Flexibilité des sorts' \
        'fr:ensorceleur:Ancêtre draconique' \
        'fr:guerrier:Archétype martial' \
        'fr:guerrier:Implacable' \
        'fr:magicien:Maîtrise des sorts' \
        'fr:magicien:Regard hypnotique' \
        'fr:moine:Déplacement aérien' \
        'fr:moine:Tranquillité' \
        'fr:occultiste:Pacte de la chaîne' \
        'fr:occultiste:Défenses captivantes' \
        'fr:paladin:Protection' \
        'fr:paladin:Préceptes de dévotion' \
        'fr:rodeur:Vigilance primitive' \
        'fr:rodeur:Attaques multiples' \
        'fr:roublard:Esprit fuyant' \
        'fr:roublard:Embuscade magique' \
    --eldricht-invocations fr:arme-de-pacte-amelioree fr:malefice-accablant \
    --ancestry-features fr:nain 'fr:nain:Nain des collines' \
    --spell-colors '#646fe1' '#e16492' \
    --backgrounds fr:voyageur en:acolyte \
    --output ./test-cards.json
