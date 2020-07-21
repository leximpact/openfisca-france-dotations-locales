from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class zrr(Variable):
    value_type = bool
    entity = Commune
    definition_period = ETERNITY
    label = "Commune située en Zone de Revitalisation Rurale (ZRR)"
    reference = [
        "https://www.legifrance.gouv.fr/affichCodeArticle.do?cidTexte=LEGITEXT000006069577&idArticle=LEGIARTI000006306203",
        "https://www.data.gouv.fr/fr/datasets/zones-de-revitalisation-rurale-zrr/"]
