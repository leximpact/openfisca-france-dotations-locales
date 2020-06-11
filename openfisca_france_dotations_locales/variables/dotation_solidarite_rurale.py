from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dotation_solidarite_rurale(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation de solidarité rurale (DSR)"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        return truc


class dsr_fraction_bourg_centre(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR


class dsr_eligible_fraction_perequation(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR

    def formula(commune, period, parameters):
      pf_hab = commune('potentiel_financier_par_habitant', period)
      strate = commune('strate_demographique', period)

      plafond = 2 * (
        + (strate == 1) * 657.114759
        + (strate == 2) * 722.315256
        + (strate == 3) * 785.439563
        + (strate == 4) * 862.218176
        + (strate == 5) * 940.663574
        + (strate == 6) * 1016.450575
        + (strate == 7) * 1073.239296
        + (strate > 7) * 0
        )

      return (pf_hab <= plafond)


class dsr_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
