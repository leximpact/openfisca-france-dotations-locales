from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class longueur_voirie(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Longueur de la voirie de la commune en mètres"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"
