from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dotation_forfaitaire(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation forfaitaire (DF)"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"
