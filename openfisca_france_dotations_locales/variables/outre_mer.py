from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class outre_mer(Variable):
    value_type = bool
    entity = Commune
    definition_period = ETERNITY
    label = "Caractère ultramarin de la commune"
