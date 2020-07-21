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


class dsr_score_attribution_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score en fonction duquel le montant de la fraction bourg-centre est réparti au sein des communes éligibles"
    documentation = """Extrait du CGCT, Article L2334-21 :
        L'attribution revenant à chaque commune est déterminée en fonction :
        a) De la population prise en compte dans la limite de 10 000 habitants ;
        b) De l'écart entre le potentiel financier moyen par habitant des communes de moins de 10 000 habitants et le potentiel financier par habitant de la commune ;
        c) De l'effort fiscal pris en compte dans la limite de 1,2 ;
        d) D'un coefficient multiplicateur égal à 1,3 pour les communes situées en zones de revitalisation rurale telles que définies à l'article 1465 A du code général des impôts.

        La dotation de solidarité rurale des chefs-lieux d'arrondissement de 10000 à 20 000 habitants
        est répartie selon les mêmes critères que celle des communes de moins de 10 000 habitants,
        en prenant en compte leur population DGF dans la limite de 10 000 habitants.
    """
    reference = [
        'Code général des collectivités territoriales - Article L2334-21',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433099&cidTexte=LEGITEXT000006070633',
        'http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94'
        ]

    def formula(commune, period, parameters):
        population_dgf_plafonnee = commune("population_dgf_plafonnee", period)  # cf. Article L2334-21
        potentiel_financier = commune('potentiel_financier', period)
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        effort_fiscal = commune('effort_fiscal', period)
        zrr = commune('zrr', period)
        dsr_eligible_fraction_bourg_centre = commune("dsr_eligible_fraction_bourg_centre", period)
        outre_mer = commune('outre_mer', period)
        population_dgf = commune('population_dgf', period)

        parameters_dsr = parameters(period).dotation_solidarite_rurale

        plafond_effort_fiscal = parameters_dsr.bourg_centre.attribution.plafond_effort_fiscal
        plafond_population = parameters_dsr.bourg_centre.attribution.plafond_population
        population_attribution = np.minimum(population_dgf_plafonnee, plafond_population)

        coefficient_zrr = parameters_dsr.bourg_centre.attribution.coefficient_zrr

        # oui le taille_max_commune est le même que pour le seuil d'éligibilité, notre paramétrisation est ainsi
        taille_max_commune = parameters_dsr.seuil_nombre_habitants
        communes_moins_10000 = (~outre_mer) * (population_dgf < taille_max_commune)
        pot_fin_10000 = (np.sum(communes_moins_10000 * potentiel_financier)
                / np.sum(communes_moins_10000 * population_dgf))

        facteur_pot_fin = max_(0, 2 - potentiel_financier_par_habitant / pot_fin_10000)
        facteur_zrr = np.where(zrr, coefficient_zrr, 1.0)
        facteur_effort_fiscal = np.minimum(plafond_effort_fiscal, effort_fiscal)

        return dsr_eligible_fraction_bourg_centre * population_attribution * facteur_pot_fin * facteur_effort_fiscal * facteur_zrr


class dsr_montant_total_eligibles_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant disponible pour communes de métropole éligibles DSR fraction bourg-centre"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
    documentation = '''
    2019 : La masse des crédits mis en répartition en métropole au titre de l'année 2019
    s’élève à [5]45 248 126 €. Le montant des garanties versées aux communes
    devenues inéligibles en 2018 (hors communes nouvelles) représente 898 172 €.
    Par ailleurs, 6 165 344 € ont été alloués aux communes nouvelles inéligibles.
    '''

    def formula_2019_01(commune, period, parameters):
        montant_total_a_attribuer = 545_248_126 - 898_172 - 6_165_344
        # montant inscrit dans la note. Pour le transformer en formule il faut
        # que soient implémentés :
        # le montant global de la dgf (fait dans les paramètres)
        # les formules de garanties pour communes nouvellement non éligibles (moyen)
        # les garanties communes nouvelles (chaud)
        # la répartition du montant global vers la DSR (très difficile)
        return montant_total_a_attribuer


class dsr_valeur_point_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction bourg-centre"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_bourg_centre", period)
        dsr_score_attribution_fraction_bourg_centre = commune("dsr_score_attribution_fraction_bourg_centre", period)
        score_total = dsr_score_attribution_fraction_bourg_centre.sum()
        return montant_total_a_attribuer / score_total


class dsr_montant_hors_garanties_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    label = "Valeurs attribuée hors 'garanties de stabilité' aux communes éligibles au titre de la fraction bourg-centre de la DSR"
    definition_period = YEAR
    documentation = '''
    Par garanties de stabilité on entend l'attribution d'un montant aux nouvelles communes
    ou aux communes nouvellement sorties de l'éligibilité.
    '''

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_fraction_bourg_centre", period)
        valeur_point = commune("dsr_valeur_point_fraction_bourg_centre", period)
        return scores * valeur_point


class dsr_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
