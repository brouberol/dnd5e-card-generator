#!/usr/bin/env bash

poetry run dnd5e-card-generator \
    --spell-filter cleric:0:1 \
    --spells fr:boule-de-feu en:toll-the-dead \
    --include-spell-legend \
    --items fr:cape-d-invisibilite fr:anneau-de-regeneration \
    --feats fr:athlete fr:sentinelle \
    --class-features \
        'artificier:Outil de circonstance' \
        'artificier:Élixir expérimental' \
        'barbare:Sens du danger' \
        'barbare:Esprit totem' \
        'barde:Expertise' \
        'barde:Mots cinglants' \
        'clerc:Conduit divin' \
        'clerc:Frappe divine' \
        'druide:Jeunesse éternelle' \
        'druide:Formes du cercle' \
        'ensorceleur:Flexibilité des sorts' \
        'ensorceleur:Ancêtre draconique' \
        'guerrier:Archétype martial' \
        'guerrier:Implacable' \
        'magicien:Maîtrise des sorts' \
        'magicien:Regard hypnotique' \
        'moine:Déplacement aérien' \
        'moine:Tranquillité' \
        'occultiste:Pacte de la chaîne' \
        'occultiste:Défenses captivantes' \
        'paladin:Protection' \
        'paladin:Préceptes de dévotion' \
        'rodeur:Vigilance primitive' \
        'rodeur:Attaques multiples' \
        'roublard:Esprit fuyant' \
        'roublard:Embuscade magique' \
    --output ./test-cards.json
