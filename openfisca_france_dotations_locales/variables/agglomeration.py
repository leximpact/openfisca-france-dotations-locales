from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
from openfisca_france_dotations_locales.variables.base import safe_divide


class population_dgf_agglomeration(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population DGF totale de l'agglomération où se situe la commune"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        Ne peuvent être éligibles les communes :
        1° Situées dans une agglomération :
        a) Représentant au moins 10 % de la population du département ou comptant plus de 250 000 habitants ;
        b) Comptant une commune soit de plus de 100 000 habitants, soit chef-lieu de département ;
    '''


class population_dgf_departement_agglomeration(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population DGF totale du département de référence de l'agglomération où se situe la commune"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        N'est pas nécessairement le même département que
        celui où se trouve la commune.
    '''


class part_population_agglomeration_departement(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Part de la population au sens DGF de l'agglomération dans son département"

    def formula(commune, period, parameters):
        population_dgf_agglomeration = commune("population_dgf_agglomeration", period)
        population_dgf_departement_agglomeration = commune("population_dgf_departement_agglomeration", period)
        return safe_divide(population_dgf_agglomeration, population_dgf_departement_agglomeration, 0)


class population_dgf_maximum_commune_agglomeration(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population maximale d'une commune appartenant à l'agglomération de la commune"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]


class chef_lieu_departement_dans_agglomeration(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Décrit si le chef-lieu de département se trouve dans l'agglomération de la commune"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
