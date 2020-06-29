import numpy as np

from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dsr_exclue_fraction_bourg_centre_agglomeration(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
        parametres_exclusion = parameters(period).dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion

        # Situées dans une unité urbaine [agglomération]
        # et remplissant au moins une des conditions suivantes :
        # 1° a) Représentant au moins 10 % de la population du département
        #        ou comptant plus de 250 000 habitants ;
        # 1° b) Comptant une commune soit de plus de 100 000 habitants, soit chef-lieu de département ;
        part_max_pop_departement = parametres_exclusion.seuil_part_population_dgf_agglomeration_departement
        pop_max_agglo = parametres_exclusion.seuil_population_dgf_agglomeration
        taille_max_plus_grande_commune_agglo = parametres_exclusion.seuil_population_dgf_maximum_commune_agglomeration

        population_dgf_agglomeration = commune("population_dgf_agglomeration", period)
        population_dgf_maximum_commune_agglomeration = commune("population_dgf_maximum_commune_agglomeration", period)
        chef_lieu_departement_dans_agglomeration = commune("chef_lieu_departement_dans_agglomeration", period)
        part_population_agglomeration_departement = commune("part_population_agglomeration_departement", period)

        return (
            (part_population_agglomeration_departement >= part_max_pop_departement)
            | (population_dgf_agglomeration >= pop_max_agglo)
            | (population_dgf_maximum_commune_agglomeration >= taille_max_plus_grande_commune_agglo)
            | chef_lieu_departement_dans_agglomeration
            )


class dsr_exclue_fraction_bourg_centre_canton(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
        # 2° Situées dans un canton dont la commune chef-lieu compte plus de 10 000 habitants,
        # à l'exception des communes sièges des bureaux centralisateurs ;
        population_dgf_chef_lieu_de_canton = commune("population_dgf_chef_lieu_de_canton", period)
        bureau_centralisateur = commune("bureau_centralisateur", period)
        taille_max_chef_lieu_canton = parameters(period).dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_chef_lieu_de_canton

        return ((population_dgf_chef_lieu_de_canton >= taille_max_chef_lieu_canton)
            * not_(bureau_centralisateur))


class dsr_exclue_fraction_bourg_centre_pfi(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
        # 3° Dont le potentiel financier par habitant (Pfi) est supérieur au double du potentiel
        # financier moyen par habitant (PFi) des communes de moins de 10 000 habitants.
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        ratio_max_potentiel_financier = parameters(period).dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_rapport_pfi_10000

        outre_mer = commune('outre_mer', period)
        potentiel_financier = commune('potentiel_financier', period)
        population_dgf = commune('population_dgf', period)

        taille_max_commune = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        # oui le taille_max_commune est le même que pour le seuil d'éligibilité, notre paramétrisation est ainsi
        communes_moins_10000 = (~outre_mer) * (population_dgf < taille_max_commune)
        pot_fin_10000 = (np.sum(communes_moins_10000 * potentiel_financier)
                / np.sum(communes_moins_10000 * population_dgf))
        return potentiel_financier_par_habitant >= (ratio_max_potentiel_financier * pot_fin_10000)


class dsr_exclue_fraction_bourg_centre_type_1(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Exclusion du bénéfice de la fraction bourg-centre de la DSR pour les \
        communes de taille inférieure au seuil de 10 000 habitants"

    def formula(commune, period, parameters):
        # Sources d'exclusion de l'éligibilité...
        dsr_exclue_fraction_bourg_centre_agglomeration = commune("dsr_exclue_fraction_bourg_centre_agglomeration", period)
        dsr_exclue_fraction_bourg_centre_canton = commune("dsr_exclue_fraction_bourg_centre_canton", period)
        dsr_exclue_fraction_bourg_centre_pfi = commune("dsr_exclue_fraction_bourg_centre_pfi", period)

        return (dsr_exclue_fraction_bourg_centre_agglomeration
            | dsr_exclue_fraction_bourg_centre_canton
            | dsr_exclue_fraction_bourg_centre_pfi)


class dsr_exclue_fraction_bourg_centre_type_2(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Exclusion du bénéfice de la fraction bourg-centre de la DSR pour les \
        communes de taille comprise entre 10000 et 20000 habitants"

    def formula(commune, period, parameters):
        # Sources d'exclusion de l'éligibilité...
        dsr_exclue_fraction_bourg_centre_agglomeration = commune("dsr_exclue_fraction_bourg_centre_agglomeration", period)
        dsr_exclue_fraction_bourg_centre_pfi = commune("dsr_exclue_fraction_bourg_centre_pfi", period)

        return (dsr_exclue_fraction_bourg_centre_agglomeration
            | dsr_exclue_fraction_bourg_centre_pfi)


class dsr_eligible_fraction_bourg_centre_type_1(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Éligibilité à la fraction bourg-centre de la DSR pour les \
        communes de taille inférieure au seuil de 10 000 habitants"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        La première fraction de la dotation de solidarité rurale est attribuée
        aux communes de moins de 10 000 habitants chefs-lieux de canton, ou bureaux
        centralisateurs,ou dont la population représente au moins 15% de la
        population du canton. La qualité de chef-lieu de canton s’apprécie au
        1er janvier 2014, de même que le périmètre cantonal.
    '''

    def formula(commune, period, parameters):
        parametres_dsr = parameters(period).dotation_solidarite_rurale

        population_dgf_plafonnee = commune("population_dgf_plafonnee", period)
        taille_max_commune = parametres_dsr.seuil_nombre_habitants
        taille_eligible = (population_dgf_plafonnee < taille_max_commune)

        part_population_canton = commune("part_population_canton", period)
        seuil_part_population_canton = parametres_dsr.bourg_centre.eligibilite.seuil_part_population_canton
        portion_canton_eligible = (part_population_canton >= seuil_part_population_canton)

        bureau_centralisateur = commune("bureau_centralisateur", period)
        chef_lieu_de_canton = commune("chef_lieu_de_canton", period)

        outre_mer = commune('outre_mer', period)
        preeligible = (~outre_mer) * taille_eligible * (portion_canton_eligible | bureau_centralisateur | chef_lieu_de_canton)
        dsr_exclue_fraction_bourg_centre_type_1 = commune('dsr_exclue_fraction_bourg_centre_type_1', period)

        return preeligible * not_(dsr_exclue_fraction_bourg_centre_type_1)


class dsr_eligible_fraction_bourg_centre_type_2(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "eligibilité à la fraction bourg-centre de la DSR pour les \
        communes de taille comprise entre 10000 et 20000 habitants"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433099&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    documentation = '''
        Bénéficient également de cette fraction [fraction bourg-centre de la DSR dite 1ère fraction] les chefs-lieux d'arrondissement
        au 31 décembre 2014, dont la population est comprise entre 10 000 et
        20 000 habitants, qui n'entrent pas dans les cas prévus aux 1° et 4° ci-dessus.
    '''

    def formula(commune, period, parameters):
        population_dgf_plafonnee = commune("population_dgf_plafonnee", period)
        outre_mer = commune('outre_mer', period)
        chef_lieu_arrondissement = commune("chef_lieu_arrondissement", period)
        dsr_exclue_fraction_bourg_centre_type_2 = commune('dsr_exclue_fraction_bourg_centre_type_2', period)

        taille_max_commune = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        taille_max_chef_lieu_arrondissement = parameters(period).dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_nombre_habitants_chef_lieu
        taille_eligible = (population_dgf_plafonnee >= taille_max_commune) * (population_dgf_plafonnee <= taille_max_chef_lieu_arrondissement)

        preeligible = (~outre_mer) * taille_eligible * chef_lieu_arrondissement

        return preeligible * not_(dsr_exclue_fraction_bourg_centre_type_2)


class dsr_eligible_fraction_bourg_centre(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "eligibilité à la fraction bourg-centre de la DSR"
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433099&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]

    def formula(commune, period, parameters):
        dsr_eligible_fraction_bourg_centre_type_1 = commune("dsr_eligible_fraction_bourg_centre_type_1", period)
        dsr_eligible_fraction_bourg_centre_type_2 = commune("dsr_eligible_fraction_bourg_centre_type_2", period)
        return dsr_eligible_fraction_bourg_centre_type_1 | dsr_eligible_fraction_bourg_centre_type_2


class dsr_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
