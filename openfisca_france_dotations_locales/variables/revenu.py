import numpy as np

from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
from openfisca_france_dotations_locales.variables.base import safe_divide


class revenu_total(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Revenu imposable total des habitants de la commune"


class revenu_par_habitant_moyen(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Revenu par habitant moyen des communes appartenant à la même strate hors Outre-mer"
    reference = [
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94",
        "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"
        ]
    documentation = '''
    Le cas particulier de l'Article L2334-22-1 du Code général des collectivités territoriales
    dédié à la DSR, fraction cible précise :
    "Le revenu pris en considération est le dernier revenu fiscal de référence connu.
    La population prise en compte est celle issue du dernier recensement de population."
    '''

    def formula(commune, period, parameters):
        revenu = commune('revenu_total', period)
        strate_demographique = commune('strate_demographique', period)
        population_insee = commune('population_insee', period)
        outre_mer = commune('outre_mer', period)

        liste_strates = list(range(1 + int(strate_demographique.max())))
        revenu_par_habitant_moyen_par_strate = np.fromiter(
            (
                (np.sum((~outre_mer) * (strate == strate_demographique) * revenu)
                / np.sum((~outre_mer) * (strate == strate_demographique) * population_insee))
                if np.sum((~outre_mer) * (strate == strate_demographique) * population_insee) > 0.01
                else 0
                for strate in liste_strates
                ),
            dtype = float
            )
        return (~outre_mer) * revenu_par_habitant_moyen_par_strate[strate_demographique]


class revenu_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
        population_insee = commune('population_insee', period)
        return safe_divide(commune('revenu_total', period), population_insee, 0)
