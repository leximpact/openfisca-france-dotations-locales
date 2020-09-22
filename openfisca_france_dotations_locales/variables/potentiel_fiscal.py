from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class potentiel_fiscal(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Potentiel fiscal:\
    Potentiel fiscal de la commune (4 taxes)"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000025076225"


class potentiel_fiscal_moyen_national(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Potentiel fiscal par habitant moyen national:\
    potentiel fiscal moyen national utilisé pour le calcul de la Dotation forfaitaire. Attention,\
    c'est pas du tout une moyenne (il y a un facteur logarithmé)"
    reference = ["https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037994287",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=115"]

    def formula_2018(etat, period, parameters):
        return 624.197

    def formula_2019(etat, period, parameters):
        return 631.5677

    def formula_2020(etat, period, parameters):
        return 641.164387
