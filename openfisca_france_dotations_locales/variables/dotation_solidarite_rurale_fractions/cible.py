import pandas as pd

from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class indice_synthetique_dsr_cible(Variable):
    value_type = float
    entity = Commune
    label = "Score pour clasement DSR part cible (indice synthétique)"
    definition_period = YEAR
    reference = [
        'Code général des collectivités territoriales - Article L2334-22-1',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        revenu_par_habitant = commune("revenu_par_habitant", period)
        revenu_par_habitant_strate = commune("revenu_par_habitant_moyen", period)
        potentiel_financier_par_habitant = commune("potentiel_financier_par_habitant", period)
        potentiel_financier_par_habitant_strate = commune("potentiel_financier_par_habitant_moyen", period)
        dsr_eligible_fraction_bourg_centre = commune("dsr_eligible_fraction_bourg_centre", period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)

        limite_population = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        parametres_poids = parameters(period).dotation_solidarite_rurale.cible.eligibilite.indice_synthetique
        poids_revenu = parametres_poids.poids_revenu
        poids_pot_fin = parametres_poids.poids_pot_fin

        return ((population_dgf < limite_population)
            * (dsr_eligible_fraction_bourg_centre | dsr_eligible_fraction_perequation)
            * (
                (poids_pot_fin * potentiel_financier_par_habitant_strate / potentiel_financier_par_habitant
                + poids_revenu * revenu_par_habitant_strate / revenu_par_habitant)
                )
            )


class rang_indice_synthetique_dsr_cible(Variable):
    value_type = int
    entity = Commune
    label = "Rang indice synthétique DSR part cible calculé"
    definition_period = YEAR
    reference = [
        'Code général des collectivités territoriales - Article L2334-22-1',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]

    def formula(commune, period, parameters):
        indice_synthetique_dsr_cible = commune("indice_synthetique_dsr_cible", period)
        rank_indice = pd.DataFrame(indice_synthetique_dsr_cible).rank(method="min", ascending= False)
        rank_indice.columns = ["rang_indice_synthetique"]
        return rank_indice["rang_indice_synthetique"].astype(int).values


class dsr_eligible_fraction_cible(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Eligibilité DSR part-cible"
    reference = [
        'Code général des collectivités territoriales - Article L2334-22-1',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        dsr_eligible_fraction_bourg_centre = commune("dsr_eligible_fraction_bourg_centre", period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        rang_indice_synthetique_dsr_cible = commune("rang_indice_synthetique_dsr_cible", period)

        nb_communes_qualifiees = parameters(period).dotation_solidarite_rurale.cible.eligibilite.seuil_classement
        limite_population = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        # On refait figurer les contraintes d'éligibilité ici pour éviter que des communes
        # soient sélectionnées avec un score de zéro si le nombre de communes sélectionnées
        # devient trop élevé
        return ((population_dgf < limite_population)
            * (dsr_eligible_fraction_bourg_centre | dsr_eligible_fraction_perequation)
            * (rang_indice_synthetique_dsr_cible <= nb_communes_qualifiees))
