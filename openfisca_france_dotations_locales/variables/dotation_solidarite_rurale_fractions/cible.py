from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
import numpy as np
from openfisca_france_dotations_locales.variables.base import safe_divide


class indice_synthetique_dsr_cible(Variable):
    value_type = float
    entity = Commune
    label = "Score pour classement DSR fraction cible (indice synthétique)"
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
        poids_pot_fin = parametres_poids.poids_potentiel_financier

        return ((population_dgf < limite_population)
            * (dsr_eligible_fraction_bourg_centre | dsr_eligible_fraction_perequation)
            * (poids_pot_fin * safe_divide(potentiel_financier_par_habitant_strate, potentiel_financier_par_habitant, 0)
            + poids_revenu * safe_divide(revenu_par_habitant_strate, revenu_par_habitant, 0))
            )


class rang_indice_synthetique_dsr_cible(Variable):
    value_type = int
    entity = Commune
    label = "Rang calculé des communes par indice synthétique décroissant de la DSR fraction cible"
    definition_period = YEAR
    reference = [
        'Code général des collectivités territoriales - Article L2334-22-1',
        'https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633',
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
        ]

    def formula(commune, period, parameters):
        indice_synthetique_dsr_cible = commune("indice_synthetique_dsr_cible", period)
        # L'utilisation d'un double argsort renvoie un tableau qui contient
        # la statistique d'ordre (indexée par 0) du tableau d'entrée dans
        # l'ordre croissant (cf par exemple
        # https://www.berkayantmen.com/rank.html).
        # On l'applique sur l'opposé de l'indice synthétique
        # pour obtenir un classement dans l'ordre décroissant.
        # les communes de même indice synthétique auront un rang différent (non spécifié par la loi)
        return (-indice_synthetique_dsr_cible).argsort().argsort() + 1


class dsr_eligible_fraction_cible(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Eligibilité DSR fraction cible"
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


pourcentage_accroissement_dsr_cible = (360_336_634 - 323_780_451) / 90_000_000


class dsr_montant_total_fraction_cible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant disponible pour communes éligibles DSR fraction cible"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula_2013_01(commune, period, parameters):
        montants_an_prochain = commune('dsr_montant_total_fraction_cible', period.offset(1, 'year'))
        accroissement = parameters(period.offset(1, 'year')).dotation_solidarite_rurale.augmentation_montant
        return montants_an_prochain - accroissement * pourcentage_accroissement_dsr_cible

    def formula_2019_01(commune, period, parameters):
        return 323_780_451

    # def formula_2020_01(commune, period, parameters):
    #    return 360_336_634

    # A partir de 2020, formule récursive qui bouge en
    # fonction des pourcentages
    # d'augmentation constatés (en vrai il faudrait défalquer
    # des pourcentages de population d'outre-mer)
    # mais c'est une autre histoire
    # La variation sera égale à pourcentage_accroissement *
    # valeur du paramètre "accroissement" pour cette année là.

    def formula_2020_01(commune, period, parameters):
        montants_an_precedent = commune('dsr_montant_total_fraction_cible', period.last_year)
        accroissement = parameters(period).dotation_solidarite_rurale.augmentation_montant
        return montants_an_precedent + accroissement * pourcentage_accroissement_dsr_cible


class dsr_montant_total_eligibles_fraction_cible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant disponible pour communes éligibles DSR fraction cible"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        dsr_montant_total_fraction_cible = commune('dsr_montant_total_fraction_cible', period)
        dsr_garantie_commune_nouvelle_fraction_cible = commune('dsr_garantie_commune_nouvelle_fraction_cible', period)
        dsr_montant_garantie_non_eligible_fraction_cible = commune('dsr_montant_garantie_non_eligible_fraction_cible', period)
        dsr_eligible_fraction_cible = commune('dsr_eligible_fraction_cible', period)
        montant_total_a_attribuer = dsr_montant_total_fraction_cible - max_(
            (~dsr_eligible_fraction_cible) * dsr_garantie_commune_nouvelle_fraction_cible,  # garantie issue du passé des composantes de la commune nouvelle
            dsr_montant_garantie_non_eligible_fraction_cible
            ).sum()
        return montant_total_a_attribuer


class dsr_montant_total_eligibles_fraction_cible_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction cible - potentiel financier par habitant:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction cible de la DSR au titre du potentiel financier par habitant"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_habitant
        return commune('dsr_montant_total_eligibles_fraction_cible', period) * poids


class dsr_montant_total_eligibles_fraction_cible_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction cible - longueur voirie:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction cible de la DSR au titre de la longueur de voirie"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_longueur_voirie
        return commune('dsr_montant_total_eligibles_fraction_cible', period) * poids


class dsr_montant_total_eligibles_fraction_cible_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction cible - nombre d'enfants:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction cible de la DSR au titre du nombre d'enfants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_enfants
        return commune('dsr_montant_total_eligibles_fraction_cible', period) * poids


class dsr_montant_total_eligibles_fraction_cible_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction cible - potentiel financier par hectare:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction cible de la DSR au titre du potentiel financier par hectare"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_hectare
        return commune('dsr_montant_total_eligibles_fraction_cible', period) * poids


class dsr_score_attribution_cible_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction cible - potentiel financier par habitant:\
        Score d'attribution de la fraction cible de la DSR au titre du potentiel financier par habitant"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """
        1° Pour 30 % de son montant, en fonction de la population
        pondérée par l'écart entre le potentiel financier par habitant de la
        commune et le potentiel financier moyen par habitant des communes
        appartenant au même groupe démographique ainsi que par l'effort fiscal
        plafonné à 1,2 ;"""

    def formula(commune, period, parameters):
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        potentiel_financier_par_habitant_strate = commune('potentiel_financier_par_habitant_moyen', period)
        effort_fiscal = commune('effort_fiscal', period)
        dsr_eligible_fraction_cible = commune("dsr_eligible_fraction_cible", period)
        population_dgf = commune('population_dgf', period)

        plafond_effort_fiscal = parameters(period).dotation_solidarite_rurale.attribution.plafond_effort_fiscal
        facteur_pot_fin = max_(0, 2 - safe_divide(potentiel_financier_par_habitant, potentiel_financier_par_habitant_strate, 2))
        facteur_effort_fiscal = np.minimum(plafond_effort_fiscal, effort_fiscal)

        return dsr_eligible_fraction_cible * population_dgf * facteur_pot_fin * facteur_effort_fiscal


class dsr_score_attribution_cible_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction cible - longueur voirie:\
        Score d'attribution de la fraction cible de la DSR au titre de la voirie"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """
        2° Pour 30 % de son montant, proportionnellement à la longueur
        de la voirie classée dans le domaine public communal ; pour les communes situées
        en zone de montagne ou pour les communes insulaires, la longueur de la voirie est
        doublée. Pour l'application du présent article, une commune insulaire s'entend
        d'une commune de métropole située sur une île qui, n'étant pas reliée au continent
        par une infrastructure routière, comprend une seule commune ou un seul
        établissement public de coopération intercommunale
        """

    def formula(commune, period, parameters):
        longueur_voirie = commune('longueur_voirie', period)
        zone_de_montagne = commune('zone_de_montagne', period)
        dsr_eligible_fraction_cible = commune("dsr_eligible_fraction_cible", period)
        insulaire = commune('insulaire', period)

        return dsr_eligible_fraction_cible * longueur_voirie * where(insulaire | zone_de_montagne, 2, 1)


class dsr_score_attribution_cible_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction cible - enfants:\
        Score d'attribution de la fraction cible de la DSR au titre du nombre d'enfants dans la population"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """
        3° Pour 30 % de son montant, proportionnellement au nombre
        d'enfants de trois à seize ans domiciliés dans la commune, établi lors du dernier
        recensement.
    """

    def formula(commune, period, parameters):
        population_enfants = commune('population_enfants', period)
        dsr_eligible_fraction_cible = commune("dsr_eligible_fraction_cible", period)

        return dsr_eligible_fraction_cible * population_enfants


class dsr_score_attribution_cible_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction cible - potentiel financier par hectare:\
        Score d'attribution de la fraction cible de la DSR au titre du potentiel financier par hectare"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """4° Pour 10 % de son montant au maximum, en fonction de
        l'écart entre le potentiel financier par hectare de la commune et le potentiel
        financier moyen par hectare des communes de moins de 10 000 habitants."""

    def formula(commune, period, parameters):
        potentiel_financier = commune('potentiel_financier', period)
        outre_mer = commune('outre_mer', period)
        potentiel_financier_par_habitant = commune('potentiel_financier_par_hectare', period)
        dsr_eligible_fraction_cible = commune("dsr_eligible_fraction_cible", period)
        population_dgf = commune('population_dgf', period)
        # oui le taille_max_commune est le même que pour le seuil d'éligibilité, notre paramétrisation est ainsi
        taille_max_commune = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        superficie = commune('superficie', period)
        communes_moins_10000 = (~outre_mer) * (population_dgf < taille_max_commune)

        pot_fin_par_hectare_10000 = safe_divide(np.sum(communes_moins_10000 * potentiel_financier), np.sum(communes_moins_10000 * superficie))

        facteur_pot_fin = max_(0, safe_divide((2 * pot_fin_par_hectare_10000 - potentiel_financier_par_habitant), pot_fin_par_hectare_10000, 0))

        return dsr_eligible_fraction_cible * population_dgf * facteur_pot_fin


class dsr_valeur_point_fraction_cible_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction cible - part potentiel financier par habitant"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_cible_part_potentiel_financier_par_habitant", period)
        dsr_score_attribution = commune("dsr_score_attribution_cible_part_potentiel_financier_par_habitant", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_valeur_point_fraction_cible_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction cible - part longueur de voirie"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_cible_part_longueur_voirie", period)
        dsr_score_attribution = commune("dsr_score_attribution_cible_part_longueur_voirie", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_valeur_point_fraction_cible_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction cible - part enfants"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_cible_part_enfants", period)
        dsr_score_attribution = commune("dsr_score_attribution_cible_part_enfants", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_valeur_point_fraction_cible_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction cible - part potentiel financier par hectare"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_cible_part_potentiel_financier_par_hectare", period)
        dsr_score_attribution = commune("dsr_score_attribution_cible_part_potentiel_financier_par_hectare", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_fraction_cible_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
        fraction cible de la DSR au titre du potentiel financier par habitant"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_cible_part_potentiel_financier_par_habitant", period)
        valeur_point = commune("dsr_valeur_point_fraction_cible_part_potentiel_financier_par_habitant", period)
        return scores * valeur_point


class dsr_fraction_cible_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
        fraction cible de la DSR au titre des enfants"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_cible_part_longueur_voirie", period)
        valeur_point = commune("dsr_valeur_point_fraction_cible_part_longueur_voirie", period)
        return scores * valeur_point


class dsr_fraction_cible_part_enfants(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
        fraction cible de la DSR au titre de la longueur de voirie"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_cible_part_enfants", period)
        valeur_point = commune("dsr_valeur_point_fraction_cible_part_enfants", period)
        return scores * valeur_point


class dsr_fraction_cible_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
        fraction cible de la DSR au titre du potentiel financier par hectare"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_cible_part_potentiel_financier_par_hectare", period)
        valeur_point = commune("dsr_valeur_point_fraction_cible_part_potentiel_financier_par_hectare", period)
        return scores * valeur_point


class dsr_montant_hors_garanties_fraction_cible(Variable):
    value_type = float
    entity = Commune
    label = "Valeurs attribuée hors garanties de stabilité aux communes éligibles au titre de la fraction cible de la DSR"
    definition_period = YEAR

    def formula(commune, period, parameters):
        part_potentiel_financier_par_habitant = commune('dsr_fraction_cible_part_potentiel_financier_par_habitant', period)
        part_longueur_voirie = commune('dsr_fraction_cible_part_longueur_voirie', period)
        part_enfants = commune('dsr_fraction_cible_part_enfants', period)
        part_potentiel_financier_par_hectare = commune('dsr_fraction_cible_part_potentiel_financier_par_hectare', period)
        return (part_potentiel_financier_par_habitant
        + part_longueur_voirie
        + part_enfants
        + part_potentiel_financier_par_hectare)


class dsr_garantie_commune_nouvelle_fraction_cible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Garantie commune nouvelle DSR fraction cible:\
        Montant garanti aux communes nouvelles au titre de la fraction cible de la dotation de solidarité rurale"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000041473401&cidTexte=LEGITEXT000006070633"
    documentation = '''Au cours des trois années suivant le 1er janvier de l'année de leur création,
        les communes nouvelles [...] perçoivent des attributions au titre [...] des trois
        fractions de la dotation de solidarité rurale au moins égales aux attributions
        perçues au titre de chacune de ces dotations par les anciennes communes l'année
        précédant la création de la commune nouvelle.'''


class dsr_montant_garantie_non_eligible_fraction_cible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Garantie de sortie DSR fraction cible:\
        Montant garanti aux communes nouvellement inéligibles au titre de la fraction cible de la dotation de solidarité rurale"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"
    documentation = '''Lorsqu'une commune cesse de remplir les conditions requises pour
        bénéficier de cette fraction de la dotation de solidarité rurale, cette
        commune perçoit, à titre de garantie non renouvelable, une attribution
        égale à la moitié de celle qu'elle a perçue l'année précédente.'''

    def formula(commune, period, parameters):
        dsr_eligible_fraction_cible = commune("dsr_eligible_fraction_cible", period)
        montant_an_precedent = commune("dsr_montant_hors_garanties_fraction_cible", period.last_year)
        ratio_garantie = parameters(period).dotation_solidarite_rurale.cible.attribution.ratio_garantie
        return (~dsr_eligible_fraction_cible) * montant_an_precedent * ratio_garantie


class dsr_fraction_cible(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant effectivement attribué DSR fraction-cible:\
        Montant attribué à la commune au titre de la fraction cible de la DSR après garanties de sortie et de commune nouvelle"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000037994647&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        dsr_montant_garantie_non_eligible_fraction_cible = commune("dsr_montant_garantie_non_eligible_fraction_cible", period)
        dsr_garantie_commune_nouvelle_fraction_cible = commune("dsr_garantie_commune_nouvelle_fraction_cible", period)
        dsr_montant_hors_garanties_fraction_cible = commune("dsr_montant_hors_garanties_fraction_cible", period)
        return max_(dsr_montant_garantie_non_eligible_fraction_cible, max_(dsr_garantie_commune_nouvelle_fraction_cible, dsr_montant_hors_garanties_fraction_cible))
