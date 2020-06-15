import numpy as np

from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class potentiel_financier(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Potentiel financier de la commune"


class potentiel_financier_par_habitant_moyen(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Potentiel financier par habitant moyen (PFi) des communes appartenant à la même strate"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        strate_demographique = commune('strate_demographique', period)

        potentiel_financier_par_strate = np.fromiter(
            (
                np.sum((strate == strate_demographique) * potentiel_financier_par_habitant)
                for strate in strate_demographique
                ),
            dtype = float
            )

        nombre_commune_par_strate = np.fromiter(
            (
                np.count_nonzero((strate == strate_demographique))
                for strate in strate_demographique
                ),
            dtype = int
            )

        return potentiel_financier_par_strate / nombre_commune_par_strate


class potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
        return commune('potentiel_financier', period) / commune('population_dgf', period)
