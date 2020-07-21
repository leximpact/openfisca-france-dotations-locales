from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class superficie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Superficie de la commune en hectares"
