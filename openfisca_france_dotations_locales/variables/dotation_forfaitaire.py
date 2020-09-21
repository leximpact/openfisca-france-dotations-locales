from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dotation_forfaitaire(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la dotation forfaitaire (DF)"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"

    def formula_2018(commune, period, parameters):
        dotation_forfaitaire_an_dernier = commune('dotation_forfaitaire', period.offset(1, 'year'))
        part_compensations_part_salaires = commune('part_compensations_part_salaires', period)
        return dotation_forfaitaire_an_dernier + part_compensations_part_salaires


class part_compensations_part_salaires(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Retraitement CPS: \
        retraitement des compensations part salaires (CPS) transférées aux communes (dite part CPS)"
    reference = "https://www.collectivites-locales.gouv.fr/files/files/dgcl_v2/FLAE_circulaires_10_fevrier2016/note_dinformation_2019_dfcom_-_vdef2.pdf"
