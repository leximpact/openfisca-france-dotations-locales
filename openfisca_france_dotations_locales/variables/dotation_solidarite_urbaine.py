from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
import numpy as np


class indice_synthetique_dsu(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Indice synthétique DSU:\
indice synthétique pour l'éligibilité à la fraction-cible"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        outre_mer = commune('outre_mer', period)
        potentiel_financier = commune('potentiel_financier', period)
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        nombre_logements = commune('nombre_logements', period)
        nombre_logements_sociaux = commune('nombre_logements_sociaux', period)
        nombre_aides_au_logement = commune('nombre_beneficiaires_aides_au_logement', period)
        revenu = commune('revenu_total', period)
        population_insee = commune('population_insee', period)
        revenu_par_habitant = commune('revenu_par_habitant', period)

        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        ratio_max_pot_fin = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_rapport_potentiel_financier
        poids_pot_fin = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_potentiel_financier
        poids_logements_sociaux = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_logements_sociaux
        poids_aides_au_logement = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_aides_au_logement
        poids_revenu = parameters(period).dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_revenu

        groupe_bas = (~outre_mer) * (seuil_bas <= population_dgf) * (seuil_haut > population_dgf)
        groupe_haut = (~outre_mer) * (seuil_haut <= population_dgf)

        pot_fin_bas = (np.sum(groupe_bas * potentiel_financier)
                / np.sum(groupe_bas * population_dgf)) if np.sum(groupe_bas * population_dgf) > 0 else 0
        pot_fin_haut = (np.sum(groupe_haut * potentiel_financier)
                / np.sum(groupe_haut * population_dgf)) if np.sum(groupe_haut * population_dgf) > 0 else 0

        # Retrait des communes au potentiel financier trop élevé, les communes restantes ont droit à un indice synthétique
        groupe_bas_score_positif = groupe_bas * (potentiel_financier_par_habitant < ratio_max_pot_fin * pot_fin_bas)
        groupe_haut_score_positif = groupe_haut * (potentiel_financier_par_habitant < ratio_max_pot_fin * pot_fin_haut)

        # Calcul des ratios moyens nécessaires au calcul de l'indice synthétique
        part_logements_sociaux_bas = (np.sum(groupe_bas * nombre_logements_sociaux)
                / np.sum(groupe_bas * nombre_logements)) if np.sum(groupe_bas * nombre_logements) > 0 else 0
        part_logements_sociaux_haut = (np.sum(groupe_haut * nombre_logements_sociaux)
                / np.sum(groupe_haut * nombre_logements)) if np.sum(groupe_haut * nombre_logements) > 0 else 0

        part_aides_logement_bas = (np.sum(groupe_bas * nombre_aides_au_logement)
                / np.sum(groupe_bas * nombre_logements)) if np.sum(groupe_bas * nombre_logements) > 0 else 0
        part_aides_logement_haut = (np.sum(groupe_haut * nombre_aides_au_logement)
                / np.sum(groupe_haut * nombre_logements)) if np.sum(groupe_haut * nombre_logements) > 0 else 0

        revenu_moyen_bas = (np.sum(groupe_bas * revenu)
                / np.sum(groupe_bas * population_insee)) if np.sum(groupe_bas * population_insee) > 0 else 0
        revenu_moyen_haut = (np.sum(groupe_haut * revenu)
                / np.sum(groupe_haut * population_insee)) if np.sum(groupe_haut * population_insee) > 0 else 0

        part_logements_sociaux_commune = np.where(nombre_logements > 0, np.divide(nombre_logements_sociaux, nombre_logements), 0)
        part_aides_logement_commune = np.where(nombre_logements > 0, np.divide(nombre_aides_au_logement, nombre_logements), 0)

        indice_synthetique_bas = groupe_bas_score_positif * (
            poids_pot_fin * np.where(potentiel_financier_par_habitant > 0, np.divide(pot_fin_bas, potentiel_financier_par_habitant), 0)
            + poids_logements_sociaux * np.where(part_logements_sociaux_bas > 0, np.divide(part_logements_sociaux_commune, part_logements_sociaux_bas), 0)
            + poids_aides_au_logement * np.where(part_aides_logement_bas > 0, np.divide(part_aides_logement_commune, part_aides_logement_bas), 0)
            + poids_revenu * np.where(revenu_par_habitant > 0, np.divide(revenu_moyen_bas, revenu_par_habitant), 0)
            )

        indice_synthetique_haut = groupe_haut_score_positif * (
            poids_pot_fin * np.where(potentiel_financier_par_habitant > 0, np.divide(pot_fin_haut, potentiel_financier_par_habitant), 0)
            + poids_logements_sociaux * np.where(part_logements_sociaux_haut > 0, np.divide(part_logements_sociaux_commune, part_logements_sociaux_haut), 0)
            + poids_aides_au_logement * np.where(part_aides_logement_haut > 0, np.divide(part_aides_logement_commune, part_aides_logement_haut), 0)
            + poids_revenu * np.where(revenu_par_habitant > 0, np.divide(revenu_moyen_haut, revenu_par_habitant), 0)
            )
        return indice_synthetique_bas + indice_synthetique_haut
