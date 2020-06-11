# -*- coding: utf-8 -*-

# This file defines the entities needed by our legislation.
from openfisca_core.entities import build_entity

#Household = build_entity(
#    key = "household",
#    plural = "households",
#    label = u'All the people in a family or group who live together in the same place.',
#    doc = '''
#    Household is an example of a group entity.
#    A group entity contains one or more individual·s.
#    Each individual in a group entity has a role (e.g. parent or children). Some roles can only be held by a limited number of individuals (e.g. a 'first_parent' can only be held by one individual), while others can have an unlimited number of individuals (e.g. 'children').
#
#    Example:
#    Housing variables (e.g. housing_tax') are usually defined for a group entity such as 'Household'.
#
#    Usage:
#    Check the number of individuals of a specific role (e.g. check if there is a 'second_parent' with household.nb_persons(Household.SECOND_PARENT)).
#    Calculate a variable applied to each individual of the group entity (e.g. calculate the 'salary' of each member of the 'Household' with salaries = household.members('salary', period = MONTH); sum_salaries = household.sum(salaries)).
#
#    For more information, see: https://openfisca.org/doc/coding-the-legislation/50_entities.html
#    ''',
#    roles = [
#        {
#            'key': 'parent',
#            'plural': 'parents',
#            'label': u'Parents',
#            'max': 2,
#            'subroles': ['first_parent', 'second_parent'],
#            'doc': u'The one or two adults in charge of the household.'
#            },
#        {
#            'key': 'child',
#            'plural': 'children',
#            'label': u'Child',
#            'doc': u'Other individuals living in the household.'
#            }
#        ]
#    )

Commune = build_entity(
    key = "commune",
    plural = "communes",
    label = "Une commune. L'entité légale la plus réduite à laquelle s'applique la législation de ce moteur de calcul.",
    doc = '''
    TODO
    ''',
    is_person = True,  # entité pivot
    )

entities = [Commune]  # [Household, Commune]
