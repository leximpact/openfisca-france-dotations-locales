from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class effort_fiscal(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Effort fiscal de la commune"
