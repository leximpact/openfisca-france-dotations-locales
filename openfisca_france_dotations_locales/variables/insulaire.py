from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class insulaire(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Commune insulaire:\
        Commune insulaire au sens de l'article 2334-22 du CGCL"
    documentation = """
    Une commune insulaire s'entend d'une commune de métropole située sur une île qui,
    n'étant pas reliée au continent par une infrastructure routière, comprend une
    seule commune ou un seul établissement public de coopération intercommunale.
    """
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"
