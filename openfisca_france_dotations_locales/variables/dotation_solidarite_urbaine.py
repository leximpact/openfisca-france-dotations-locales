from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
import numpy as np
from openfisca_france_dotations_locales.variables.base import safe_divide


class indice_synthetique_dsu(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Indice synthétique DSU:\
        indice synthétique pour l'éligibilité à la DSU"
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

        part_logements_sociaux_commune = safe_divide(nombre_logements_sociaux, nombre_logements)
        part_aides_logement_commune = safe_divide(nombre_aides_au_logement, nombre_logements)

        indice_synthetique_bas = groupe_bas_score_positif * (
            poids_pot_fin * safe_divide(pot_fin_bas, potentiel_financier_par_habitant)
            + poids_logements_sociaux * safe_divide(part_logements_sociaux_commune, part_logements_sociaux_bas)
            + poids_aides_au_logement * safe_divide(part_aides_logement_commune, part_aides_logement_bas)
            + poids_revenu * safe_divide(revenu_moyen_bas, revenu_par_habitant)
            )

        indice_synthetique_haut = groupe_haut_score_positif * (
            poids_pot_fin * safe_divide(pot_fin_haut, potentiel_financier_par_habitant)
            + poids_logements_sociaux * safe_divide(part_logements_sociaux_commune, part_logements_sociaux_haut)
            + poids_aides_au_logement * safe_divide(part_aides_logement_commune, part_aides_logement_haut)
            + poids_revenu * safe_divide(revenu_moyen_haut, revenu_par_habitant)
            )
        return indice_synthetique_bas + indice_synthetique_haut


class rang_indice_synthetique_dsu_seuil_haut(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Rang indice synthétique DSU seuil haut:\
        Rang de classement de l'indice synthétique de DSU pour les communes de plus de 10000 habitants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)
        population_dgf = commune('population_dgf', period)
        # L'utilisation d'un double argsort renvoie un tableau qui contient
        # la statistique d'ordre (indexée par 0) du tableau d'entrée dans
        # l'ordre croissant (cf par exemple
        # https://www.berkayantmen.com/rank.html).
        # On l'applique sur l'opposé de l'indice synthétique
        # pour obtenir un classement dans l'ordre décroissant.
        # les communes de même indice synthétique auront un rang différent (non spécifié par la loi)
        score_a_classer = (indice_synthetique_dsu) * (seuil_haut <= population_dgf)
        return (-score_a_classer).argsort().argsort() + 1


class rang_indice_synthetique_dsu_seuil_bas(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Rang indice synthétique DSU seuil bas:\
        Rang de classement de l'indice synthétique de DSU pour les communes de plus de 5000 à 9999 habitants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)
        population_dgf = commune('population_dgf', period)
        # L'utilisation d'un double argsort renvoie un tableau qui contient
        # la statistique d'ordre (indexée par 0) du tableau d'entrée dans
        # l'ordre croissant (cf par exemple
        # https://www.berkayantmen.com/rank.html).
        # On l'applique sur l'opposé de l'indice synthétique
        # pour obtenir un classement dans l'ordre décroissant.
        # les communes de même indice synthétique auront un rang différent (non spécifié par la loi)
        score_a_classer = (indice_synthetique_dsu) * (seuil_haut > population_dgf) * (seuil_bas <= population_dgf)
        return (-score_a_classer).argsort().argsort() + 1


class dsu_nombre_communes_eligibles_seuil_bas(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombres de communes du seuil bas éligible à la DSU:\
        Nombre de communes éligibles à la dsu dans le seuil bas"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        outre_mer = commune('outre_mer', period)

        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        pourcentage_eligible_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.part_eligible_seuil_bas

        nombre_communes_seuil_bas = ((~outre_mer) * (population_dgf >= seuil_bas) * (population_dgf < seuil_haut)).sum()

        return int(nombre_communes_seuil_bas * pourcentage_eligible_bas + 0.99)  # 0.99 pour arrondi supérieur


class dsu_nombre_communes_eligibles_seuil_haut(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Nombres de communes du seuil haut éligible à la DSU:\
        Nombre de communes éligibles à la dsu dans le seuil haut"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        population_dgf = commune("population_dgf", period)
        outre_mer = commune('outre_mer', period)

        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants
        pourcentage_eligible_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.part_eligible_seuil_haut

        nombre_communes_seuil_haut = ((~outre_mer) * (population_dgf >= seuil_haut)).sum()

        return int(nombre_communes_seuil_haut * pourcentage_eligible_haut + 0.99)  # 0.99 pour arrondi supérieur


class dsu_eligible(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "DSU Eligible:\
        Est éligible à la dotation de solidarité urbaine "
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000038834291&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)
        rang_indice_synthetique_dsu_seuil_bas = commune('rang_indice_synthetique_dsu_seuil_bas', period)
        rang_indice_synthetique_dsu_seuil_haut = commune('rang_indice_synthetique_dsu_seuil_haut', period)

        nombre_elig_seuil_bas = commune('dsu_nombre_communes_eligibles_seuil_bas', period)
        nombre_elig_seuil_haut = commune('dsu_nombre_communes_eligibles_seuil_haut', period)
        elig_seuil_bas = (indice_synthetique_dsu > 0) * (rang_indice_synthetique_dsu_seuil_bas <= nombre_elig_seuil_bas)
        elig_seuil_haut = (indice_synthetique_dsu > 0) * (rang_indice_synthetique_dsu_seuil_haut <= nombre_elig_seuil_haut)
        return elig_seuil_bas | elig_seuil_haut


pourcentage_accroissement_dsu = (2_164_552_909 - 2_079_328_714) / 90_000_000


class dsu_montant_total(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant hors garanties:\
        Valeur totale attribuée (hors garanties) aux communes éligibles à la DSU en métropole"
    reference = [
        "https://www.collectivites-locales.gouv.fr/files/files/dgcl_v2/FLAE/Circulaires_2019/note_dinformation_2019_dsu.pdf",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=120"
        ]
    documentation = '''
    En 2019 : La somme effectivement mise en répartition au profit
    des communes de métropole s'élève à 2 164 552 909 €
    (...)
    après prélèvement de la quote-part réservée aux communes des départements
    et collectivités d'outre-mer (126 185 741 €).

    En 2020 : La somme effectivement mise en répartition au profit
    des communes de métropole s'élève à 2 244 240 555 €
    (...)
    après prélèvement de la quote-part réservée aux communes des départements
    et collectivités d’outre-mer (136 498 095 €).
    '''
    # Est un montant fixe pour 2019

    def formula_2019_01(commune, period, parameters):
        montant_total_a_attribuer = 2_164_552_909
        return montant_total_a_attribuer

    # A partir de 2020, formule récursive qui bouge en
    # fonction des pourcentages
    # d'augmentation constatés (en vrai il faudrait défalquer
    # des pourcentages de population d'outre-mer)
    # mais c'est une autre histoire
    # La variation sera égale à pourcentage_accroissement *
    # valeur du paramètre "accroissement" pour cette année là.

    def formula_2020_01(commune, period, parameters):
        montants_an_precedent = commune('dsu_montant_total', period.last_year)
        accroissement = parameters(period).dotation_solidarite_urbaine.augmentation_montant
        return montants_an_precedent + accroissement * pourcentage_accroissement_dsu

    def formula_2013_01(commune, period, parameters):
        montants_an_prochain = commune('dsu_montant_total', period.offset(1, 'year'))
        accroissement = parameters(period.offset(1, 'year')).dotation_solidarite_urbaine.augmentation_montant
        return montants_an_prochain - accroissement * pourcentage_accroissement_dsu


class dsu_montant_garantie_pluriannuelle(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant garanti au titre des années N-2 ou antérieures:\
        Montant de la garantie pluriannuelle touchée par la commune en cas de non-éligibilité"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814534&cidTexte=LEGITEXT000006070633"
    documentation = """Lorsqu'une commune cesse d'être éligible à la dotation à la suite
    d'une baisse de sa population en deçà du seuil minimal fixé au 2° de l'article
    L. 2334-16, elle perçoit, à titre de garantie pour les neufs exercices suivants,
    une attribution calculée en multipliant le montant de dotation perçu la dernière
    année où la commune était éligible par un coefficient égal à 90 % la première
    année et diminuant ensuite d'un dixième chaque année.

    En outre, lorsque, à compter de 2000, une commune, dont l'établissement public de
    coopération intercommunale dont elle est membre a opté deux ans auparavant pour
    l'application du régime fiscal prévu à l'article 1609 nonies C du code général des
    impôts, cesse d'être éligible à la dotation du fait de l'application des 1 et 2 du
    II de l'article L2334-4, elle perçoit, pendant cinq ans, une attribution calculée
    en multipliant le montant de dotation perçu la dernière année où la commune était
    éligible par un coefficient égal à 90 % la première année et diminuant ensuite d'un
    dixième chaque année. """

# Bon OK peut être je dis bien peut-être que je peux :
# prendre montant total à attribuer
# trouver somehow le montant des garanties du futur
# retirer ce montant des garanties
# retirer le montant des dotations spontanées


class dsu_montant_garantie_annuelle(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant garanti au titre de l'année N-1:\
        Montant garanti en cas de non éligibilité pour les communes non éligibles"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814534&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        montant_eligible_an_dernier = commune('dsu_montant_eligible', period.last_year)
        part_garantie = 0.5
        return part_garantie * montant_eligible_an_dernier


class dsu_montant_garantie_non_eligible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU Montant garanti non éligible:\
        Montant de la garantie de DSU versée aux communes non éligibles"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814534&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        dsu_montant_garantie_annuelle = commune('dsu_montant_garantie_annuelle', period)
        dsu_montant_garantie_pluriannuelle = commune('dsu_montant_garantie_pluriannuelle', period)
        dsu_eligible = commune('dsu_eligible', period)
        return (~dsu_eligible) * max_(dsu_montant_garantie_annuelle, dsu_montant_garantie_pluriannuelle)


class dsu_montant_total_eligibles(Variable):
    value_type = float
    entity = Commune  # une valeur unique valable pour la métropole
    definition_period = YEAR
    label = "DSU Montant hors garanties:\
        Valeur totale attribuée (hors garanties) aux communes éligibles à la DSU"
    reference = "https://www.collectivites-locales.gouv.fr/files/files/dgcl_v2/FLAE/Circulaires_2019/note_dinformation_2019_dsu.pdf"

    def formula_2019_01(commune, period, parameters):
        dsu_montant_total = commune('dsu_montant_total', period)
        dsu_montant_garantie_non_eligible = commune('dsu_montant_garantie_non_eligible', period)
        # retrait des montants garantis, le reste est à distribuer entre communes éligibles
        return dsu_montant_total - sum(dsu_montant_garantie_non_eligible)


class dsu_montant_eligible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU au titre de l'éligibilité:\
        Montant total reçu par la commune au titre de son éligibilité à la DSU (incluant part spontanée et augmentation)"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814543&cidTexte=LEGITEXT000006070633"

    # La vraie clef de répartition n'est pas claire : les dotations sont distribuées
    # au prorata du score au sein des 4 sous catégories :
    # - groupe bas (entre 5000 et 9999 habitants DGF) nouvellement éligibles
    # - groupe bas (entre 5000 et 9999 habitants DGF) augmentation pour communes éligibles 2 ans de suite
    # - groupe haut (>= 10000 habitants DGF) nouvellement éligibles
    # - groupe haut (>= 10000 habitants DGF) augmentation pour communes éligibles 2 ans de suite
    # La répartition entre groupe haut et groupe bas se fait "au prorata de leur
    # population dans le total des communes bénéficiaires. "
    # En revanche, la répartition des dotations entre les nouvellement éligibles et toujours
    # éligibles n'est pas claire.
    # Ici, on :
    # Attribue au groupe haut et groupe bas en fonction des populations toujours éligibles
    # Pour la répartition au sein de chaque groupe, on veut que les rapports entre les valeurs de points pour la part spontanées
    # Et pour l'augmentation reflète la part entre la DSU de l'an dernier et l'augmentation.
    # On veut donc :  VP(augmentation) / VP(dotation spontanée) = montant augmentation / montant an dernier
    # Ca correspond grosso modo (mais pas exactement) à la répartition de facto
    def formula_2019_01(commune, period, parameters):
        dsu_montant_total = commune('dsu_montant_total', period)
        dsu_an_precedent = commune('dsu_montant_total', period.last_year)
        montants_an_precedent = commune('dsu_montant_eligible', period.last_year)
        dsu_eligible = commune('dsu_eligible', period)
        total_a_distribuer = commune('dsu_montant_total_eligibles', period)
        rang_indice_synthetique_dsu_seuil_bas = commune('rang_indice_synthetique_dsu_seuil_bas', period)
        rang_indice_synthetique_dsu_seuil_haut = commune('rang_indice_synthetique_dsu_seuil_haut', period)

        nombre_elig_seuil_bas = commune('dsu_nombre_communes_eligibles_seuil_bas', period)
        nombre_elig_seuil_haut = commune('dsu_nombre_communes_eligibles_seuil_haut', period)
        effort_fiscal = commune('effort_fiscal', period)
        population_insee = commune('population_insee', period)
        population_qpv = commune('population_qpv', period)
        population_zfu = commune('population_zfu', period)
        population_dgf = commune('population_dgf', period)
        indice_synthetique_dsu = commune('indice_synthetique_dsu', period)

        facteur_classement_max = parameters(period).dotation_solidarite_urbaine.attribution.facteur_classement_max
        facteur_classement_min = parameters(period).dotation_solidarite_urbaine.attribution.facteur_classement_min
        poids_quartiers_prioritaires_ville = parameters(period).dotation_solidarite_urbaine.attribution.poids_quartiers_prioritaires_ville
        poids_zone_franche_urbaine = parameters(period).dotation_solidarite_urbaine.attribution.poids_zone_franche_urbaine
        plafond_effort_fiscal = parameters(period).dotation_solidarite_urbaine.attribution.plafond_effort_fiscal
        augmentation_max = parameters(period).dotation_solidarite_urbaine.attribution.augmentation_max
        seuil_bas = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants
        seuil_haut = parameters(period).dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants

        pourcentage_augmentation_dsu = dsu_montant_total / dsu_an_precedent - 1

        eligible_groupe_haut = dsu_eligible * (seuil_haut <= population_dgf)
        eligible_groupe_bas = dsu_eligible * (seuil_bas <= population_dgf) * (seuil_haut > population_dgf)
        toujours_eligible_groupe_bas = eligible_groupe_bas * (montants_an_precedent > 0)
        toujours_eligible_groupe_haut = eligible_groupe_haut * (montants_an_precedent > 0)
        nouvellement_eligible_groupe_bas = eligible_groupe_bas * (montants_an_precedent == 0)
        nouvellement_eligible_groupe_haut = eligible_groupe_haut * (montants_an_precedent == 0)
        toujours_eligible = toujours_eligible_groupe_bas | toujours_eligible_groupe_haut
        # Détermination des scores
        facteur_classement_seuil_bas = np.where(rang_indice_synthetique_dsu_seuil_bas <= nombre_elig_seuil_bas, (facteur_classement_min - facteur_classement_max) * safe_divide((rang_indice_synthetique_dsu_seuil_bas - 1), (nombre_elig_seuil_bas - 1), 0) + facteur_classement_max, 0)
        facteur_classement_seuil_haut = np.where(rang_indice_synthetique_dsu_seuil_haut <= nombre_elig_seuil_haut, (facteur_classement_min - facteur_classement_max) * safe_divide((rang_indice_synthetique_dsu_seuil_haut - 1), (nombre_elig_seuil_haut - 1), 0) + facteur_classement_max, 0)
        facteur_classement = facteur_classement_seuil_bas + facteur_classement_seuil_haut
        facteur_effort_fiscal = min_(effort_fiscal, plafond_effort_fiscal)
        facteur_qpv = (1 + np.where(population_insee > 0, poids_quartiers_prioritaires_ville * population_qpv / population_insee, 0))
        facteur_zfu = (1 + np.where(population_insee > 0, poids_zone_franche_urbaine * population_zfu / population_insee, 0))
        score_attribution = indice_synthetique_dsu * population_dgf * facteur_classement * facteur_effort_fiscal * facteur_qpv * facteur_zfu
        score_anciens_eligibles_groupe_haut = (score_attribution * toujours_eligible_groupe_haut)
        score_nouveaux_eligibles_groupe_haut = (score_attribution * nouvellement_eligible_groupe_haut)
        score_anciens_eligibles_groupe_bas = (score_attribution * toujours_eligible_groupe_bas)
        score_nouveaux_eligibles_groupe_bas = (score_attribution * nouvellement_eligible_groupe_bas)
        # clef de répartition groupe haut/groupe bas
        total_pop_eligible_augmentation_groupe_bas = (toujours_eligible_groupe_bas * population_dgf).sum()
        total_pop_eligible_augmentation_groupe_haut = (toujours_eligible_groupe_haut * population_dgf).sum()
        total_pop_eligible_augmentation = total_pop_eligible_augmentation_groupe_haut + total_pop_eligible_augmentation_groupe_bas
        # s'il n'y a pas de population, on répartit selon la population totale des groupes (non spécifié par la loi)
        if not total_pop_eligible_augmentation:
            total_pop_eligible_augmentation_groupe_bas = (eligible_groupe_bas * population_dgf).sum()
            total_pop_eligible_augmentation_groupe_haut = (eligible_groupe_haut * population_dgf).sum()
            total_pop_eligible_augmentation = total_pop_eligible_augmentation_groupe_haut + total_pop_eligible_augmentation_groupe_bas

        part_augmentation_groupe_bas = total_pop_eligible_augmentation_groupe_bas / total_pop_eligible_augmentation
        part_augmentation_groupe_haut = 1 - part_augmentation_groupe_bas
        # clef de répartition : on attribue une valeur des points d'augmentation égale au pourcentage
        # d'augmentation de la DSU
        rapport_valeur_point = pourcentage_augmentation_dsu  # Le rapport valeur point dépend
        # probablement du groupe, mais on ignore les détails de son calcul
        total_points_groupe_bas = (score_anciens_eligibles_groupe_bas * rapport_valeur_point + score_nouveaux_eligibles_groupe_bas).sum()
        total_points_groupe_haut = (score_anciens_eligibles_groupe_haut * rapport_valeur_point + score_nouveaux_eligibles_groupe_haut).sum()
        # Détermination de la valeur du point
        montant_garanti_eligible = (toujours_eligible * montants_an_precedent).sum()
        valeur_point_groupe_bas = (total_a_distribuer - montant_garanti_eligible) * part_augmentation_groupe_bas / total_points_groupe_bas if total_points_groupe_bas else 0
        valeur_point_groupe_haut = (total_a_distribuer - montant_garanti_eligible) * part_augmentation_groupe_haut / total_points_groupe_haut if total_points_groupe_haut else 0
        montant_toujours_eligible_groupe_bas = (min_(valeur_point_groupe_bas * rapport_valeur_point * score_attribution, augmentation_max) + montants_an_precedent) * toujours_eligible_groupe_bas
        montant_toujours_eligible_groupe_haut = (min_(valeur_point_groupe_haut * rapport_valeur_point * score_attribution, augmentation_max) + montants_an_precedent) * toujours_eligible_groupe_haut
        montant_nouvellement_eligible_groupe_bas = valeur_point_groupe_bas * score_attribution * nouvellement_eligible_groupe_bas
        montant_nouvellement_eligible_groupe_haut = valeur_point_groupe_haut * score_attribution * nouvellement_eligible_groupe_haut
        return montant_toujours_eligible_groupe_bas + montant_toujours_eligible_groupe_haut + montant_nouvellement_eligible_groupe_bas + montant_nouvellement_eligible_groupe_haut


class dsu_montant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total versé au titre de la DSU:\
        Montant total versé au titre de la DSU : garanties + montant spontané + augmentation"
    reference = "https://www.legifrance.gouv.fr/affichCode.do?idSectionTA=LEGISCTA000006197674&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        dsu_montant_eligible = commune('dsu_montant_eligible', period)
        dsu_montant_garantie_non_eligible = commune('dsu_montant_garantie_non_eligible', period)
        return dsu_montant_eligible + dsu_montant_garantie_non_eligible


class dsu_part_spontanee(Variable):
    # Cette variable est surtout là parce qu'elle existe dans le fichier de la DGCL en output.
    # Elle représente la partie de la DSU non liée à l'augmentation de la DSU
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU part spontanée:\
        DSU attribution spontanée"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033814543&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        dsu_montant_eligible = commune('dsu_montant_eligible', period)
        montants_an_precedent = commune('dsu_montant_eligible', period.last_year)
        dsu_eligible = commune('dsu_eligible', period)
        return np.where((montants_an_precedent > 0) * dsu_eligible, montants_an_precedent, dsu_montant_eligible)


class dsu_part_augmentation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "DSU augmentation:\
        Acroissement de la DSU"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do;jsessionid=03CB6A1BBD20CCF171C0623A79187071.tplgfr24s_2?idArticle=LEGIARTI000033814522&cidTexte=LEGITEXT000006070633&dateTexte=20200804"

    def formula(commune, period, parameters):
        dsu_montant_eligible = commune('dsu_montant_eligible', period)
        dsu_part_spontanee = commune('dsu_part_spontanee', period)
        return dsu_montant_eligible - dsu_part_spontanee
