from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class nombre_logements(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombre de logements :\
Nombre total de logements de la commune"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"


class nombre_logements_sociaux(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombre de logements sociaux:\
Nombre de logements sociaux de la commune"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"


class nombre_beneficiaires_aides_au_logement(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombre de bénéficiaires d'aides au logement:\
Nombre de bénéficiaires d'aides au logement de la commune"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"
