# -*- coding: utf-8 -*-

# This file defines the entities needed by our legislation.
from openfisca_core.entities import build_entity


Commune = build_entity(
    key = "commune",
    plural = "communes",
    label = "Une commune. L'entité légale la plus réduite à laquelle s'applique la législation de ce moteur de calcul.",
    doc = '''
    TODO
    ''',
    is_person = True,  # entité pivot
    )

Etat = build_entity(
    key = "etat",
    plural = "etats",
    label = 'État',
    roles = [
        {
            'key': 'commune',
            'plural': 'communes',
            'label': 'Communes',
            }
        ]
    )

entities = [Etat, Commune]
