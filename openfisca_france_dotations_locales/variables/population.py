from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class strate_demographique(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Strate ou groupe démographique de la commune d'après son nombre d'habitants"
    reference = [
        'Code général des collectivités territoriales - Article L2334-3',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878299&cidTexte=LEGITEXT000006070633'
        ]

    def formula(commune, period, parameters):
        pop = commune('population_dgf', period)

        return (
            + 1 * (pop <= 499)
            + 2 * (499 < pop) * (pop <= 999)
            + 3 * (999 < pop) * (pop <= 1999)
            + 4 * (1999 < pop) * (pop <= 3499)
            + 5 * (3499 < pop) * (pop <= 4999)
            + 6 * (4999 < pop) * (pop <= 7499)
            + 7 * (7499 < pop) * (pop <= 9999)
            + 8 * (9999 < pop) * (pop <= 14999)
            + 9 * (14999 < pop) * (pop <= 19999)
            + 10 * (19999 < pop) * (pop <= 34999)
            + 11 * (34999 < pop) * (pop <= 49999)
            + 12 * (49999 < pop) * (pop <= 74999)
            + 13 * (74999 < pop) * (pop <= 99999)
            + 14 * (99999 < pop) * (pop <= 199999)
            + 15 * (199999 < pop)
            )


class population_insee(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR


class population_dgf(Variable):
    value_type = int
    entity = Commune
    label = "Population au sens DGF de la commune"
    reference = [
        'Code général des collectivités territoriales - Article L2334-2',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633'
        ]
    definition_period = YEAR

#     def formula(commune, period, parameters):
#         insee = commune('population_insee', period)
#         nb_resid_second = commune('nb_residences_secondaires', period)
#         nb_caravanes = commune('nb_caravanes', period)
#         dsu_nm1 = commune('dotation_solidarite_urbaine', period.last_year)
#         pfrac_dsu_nm1 = commune('premiere_fraction_dotation_solidarite_rurale', period.last_year)
#
#         return (
#             + insee
#             + 1 * nb_resid_second
#             + 1 * nb_caravanes
#             + 1 * nb_caravanes * ((dsu_nm1 > 0) + (pfrac_dsu_nm1 > 0))
#             )


class population_dgf_plafonnee(Variable):
    value_type = int
    entity = Commune
    label = "Population au sens DGF de la commune, plafonnée en fonction de la population INSEE"
    reference = [
        'https://www.legifrance.gouv.fr/affichCodeArticle.do;jsessionid=849B2A0736FF63D09762D4F7CE98FC9C.tplgfr31s_2?idArticle=LEGIARTI000036433099&cidTexte=LEGITEXT000006070633',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033878277&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]
    definition_period = YEAR
    documentation = '''
    La population prise en compte est celle définie à l'article L. 2334-21 :
    – plafonnée à 500 habitants pour les communes dont la population issue du dernier recensement est inférieure à 100 habitants ;
    – plafonnée à 1 000 habitants pour les communes dont la population issue du dernier recensement est comprise entre 100 et 499 habitants ;
    – plafonnée à 2 250 habitants pour les communes dont la population issue du dernier recensement est comprise entre 500 et 1 499 habitants.
    Ce plafond s'applique uniquement à la population de la commune concernée et n'intervient pas dans le calcul du potentiel financier par habitant.
    '''

    def formula(commune, period, parameters):
        population_dgf = commune('population_dgf', period)
        population_insee = commune('population_insee', period)
        bareme_plafond_dgf = parameters(period).population.plafond_dgf

        # pour les communes  à la population insee < à la clef, la population dgf est plafonnée à value
        return min_(bareme_plafond_dgf.calc(population_insee), population_dgf)


class population_dgf_majoree(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Population DGF majorée:\
        Population DGF majorée pour le calcul de la dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"
    documentation = '''
        La population de la commune prise en compte au titre de 2019 est celle définie à l'article L. 2334-2
        du présent code majorée de 0,5 habitant supplémentaire par résidence secondaire pour les communes
        dont la population est inférieure à 3 500 habitants, dont le potentiel fiscal par habitant
        est inférieur au potentiel fiscal moyen par habitant des communes appartenant à la même
        strate démographique et dont la part de la majoration au titre des résidences secondaires
        dans la population avant application de la présente disposition est supérieure à 30 %.
        '''


class population_enfants(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombre d'habitants de 3 à 16 ans (selon le dernier recensement)"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"


class population_qpv(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population QPV:\
        Population des quartiers prioritaires de politique de la ville"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"


class population_zfu(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Population ZFU:\
        Population des zones franches urbaines de la commune"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"
