from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class part_population_canton(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Part de la population DGF de la commune dans son canton (tel que défini en 2014)"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        La première fraction de la dotation de solidarité rurale est attribuée
        aux communes de moins de 10000 habitants chefs-lieux de canton, ou bureaux
        centralisateurs,ou dont la population représente au moins 15% de la
        population du canton.La qualité de chef-lieu de canton s’apprécie au
        1er janvier 2014, de même que le périmètre cantonal.
        Attention, vous qui tentez de rendre cette variable calculable, sachez
        que vous allez vivre un enfer que j'ai chiffré à 12 heures de boulot pour
        recalculer une colonne en raison des problèmes induits par :
        - communes fusionnées
        - communes sur plusieurs cantons
        - formule cheloue (allez ça je vous le donne, le numérateur est la
        population DGF plafonnée mais le dénominateur n'est pas plafonné)
    '''


class chef_lieu_de_canton(Variable):
    value_type = bool
    entity = Commune
    definition_period = ETERNITY
    label = "Décrit si la commune est chef-lieu de canton au 1er janvier 2014"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        La première fraction de la dotation de solidarité rurale est attribuée
        aux communes de moins de 10000 habitants chefs-lieux de canton, ou bureaux
        centralisateurs,ou dont la population représente au moins 15% de la
        population du canton.La qualité de chef-lieu de canton s’apprécie au
        1er janvier 2014, de même que le périmètre cantonal.
    '''


class chef_lieu_arrondissement(Variable):
    value_type = bool
    entity = Commune
    definition_period = ETERNITY
    label = "Décrit si la commune est chef-lieu d'arrondissement au 31 décembre 2014"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        Bénéficient également de cette fraction [type 2 de la 1ère fraction DSR, i.e. la fraction bourg-centre] les chefs-lieux d'arrondissement
        au 31 décembre 2014, dont la population est comprise entre 10 000 et
        20 000 habitants
    '''


class bureau_centralisateur(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Décrit si la commune est un bureau centralisateur (nom des chefs-lieux de canton depuis 2015)"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        La première fraction de la dotation de solidarité rurale est attribuée
        aux communes de moins de 10000 habitants chefs-lieux de canton, ou bureaux
        centralisateurs,ou dont la population représente au moins 15% de la
        population du canton.La qualité de chef-lieu de canton s’apprécie au
        1er janvier 2014, de même que le périmètre cantonal.
    '''


class population_dgf_chef_lieu_de_canton(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population DGF de la commune qui était chef lieu de canton au 1er janvier 2014"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        Ne peuvent être éligibles les communes : Situées dans un canton
        dont la commune chef-lieu compte plus de 10 000 habitants, à
        l'exception des communes sièges des bureaux centralisateurs
    '''
