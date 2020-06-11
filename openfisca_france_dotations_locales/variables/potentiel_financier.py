from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class potentiel_financier(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR


class potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
      return commune('potentiel_financier', period) / commune('population_dgf', period)