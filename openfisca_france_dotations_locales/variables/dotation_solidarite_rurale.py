from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dotation_solidarite_rurale(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation de solidarité rurale (DSR)"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        dsr_fraction_cible = commune("dsr_fraction_cible", period)
        dsr_fraction_bourg_centre = commune("dsr_fraction_bourg_centre", period)
        dsr_fraction_perequation = commune("dsr_fraction_perequation", period)
        return dsr_fraction_cible + dsr_fraction_bourg_centre + dsr_fraction_perequation
