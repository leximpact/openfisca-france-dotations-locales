from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class strate_demographique(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Caractère ultramarin de la commune"

